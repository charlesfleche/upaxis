#!python

import argparse
import logging

from pathlib import Path

from pxr import Gf, Usd, UsdGeom, UsdSkel

Token = str

_VECTOR_ORIGIN = Gf.Vec3d(0, 0, 0)

_MATRIX_IDENTITY = Gf.Matrix4d().SetIdentity()
_MATRIX_ROTATION_POSITIVE_90_DEGREES_AROUND_X = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), 90))
_MATRIX_ROTATION_NEGATIVE_90_DEGREES_AROUND_X = _MATRIX_ROTATION_POSITIVE_90_DEGREES_AROUND_X.GetInverse()

_AXIS_COMPENSATION_ROTATION = {
    (UsdGeom.Tokens.y, UsdGeom.Tokens.y): _MATRIX_IDENTITY,                               # From Y-Up to Y-Up
    (UsdGeom.Tokens.y, UsdGeom.Tokens.z): _MATRIX_ROTATION_POSITIVE_90_DEGREES_AROUND_X,  # From Y-Up to Z-Up
    (UsdGeom.Tokens.z, UsdGeom.Tokens.y): _MATRIX_ROTATION_NEGATIVE_90_DEGREES_AROUND_X,  # From Z-Up to Y-Up
    (UsdGeom.Tokens.z, UsdGeom.Tokens.z): _MATRIX_IDENTITY,                               # From Z-Up to Z-Up
}


def _compensate_matrix(compensation_matrix: Gf.Matrix4d, matrix_to_compensate: Gf.Matrix4d) -> Gf.Matrix4d:
    ret = compensation_matrix.GetInverse() * matrix_to_compensate * compensation_matrix
    logging.debug("compensating matrix from\n%r\nto\n%r", matrix_to_compensate, ret)
    return ret


class Compensator:
    def __init__(self):
        self._compensation_matrix = Gf.Matrix4d().SetIdentity()
        self._compensation_matrices = []


    def compensate_global_matrix(self, mat: Gf.Matrix4d) -> Gf.Matrix4d:
        global_compensation_matrix = self._compensation_matrices[0]
        return _compensate_matrix(global_compensation_matrix, mat)
        

    def compensate_local_matrix(self, mat: Gf.Matrix4d) -> Gf.Matrix4d:
        return _compensate_matrix(self._compensation_matrix, mat)


    def compensate_local_vector(self, vec: Gf.Vec3d) -> Gf.Vec3d:
        mat = Gf.Matrix4d().SetTranslate(vec)
        mat = self.compensate_local_matrix(mat)
        return mat.Transform(_VECTOR_ORIGIN)


    def push_compensation_matrix(self, mat: Gf.Matrix4d) -> None:
        mat = Gf.Matrix4d(mat)  # Ensure mat is copied, just not referenced
        self._compensation_matrix *= mat
        self._compensation_matrices.append(mat)

        logging.debug("pushing compensation matrix\r%r\nnew compensation matrix\n%r", mat, self._compensation_matrix)


    def pop_compensation_matrix(self) -> None:
        mat = self._compensation_matrices.pop()

        logging.debug("%r", mat)

        self._compensation_matrix *= mat.GetInverse()

        logging.debug("popping compensation matrix\n%r\nnew compensation matrix\n%r", mat, self._compensation_matrix)


def compensate_xformable(xformable: UsdGeom.Xformable, compensator: Compensator) -> None:
    mat = get_xformable_payload_matrix(xformable)
    op = xformable.MakeMatrixXform()
    op.Set(compensator.compensate_local_matrix(mat))


def compensate_pointbased(point_based: UsdGeom.PointBased, compensator: Compensator) -> None:
    points = point_based.GetPointsAttr()
    points.Set([compensator.compensate_local_vector(Gf.Vec3d(*vec)) for vec in points.Get()])


def compensate_skel_binding_api(skel_binding_api: UsdSkel.BindingAPI, compensator: Compensator) -> None:
    return
    if attr := skel_binding_api.GetGeomBindTransformAttr():
        if mat := attr.Get():
            attr.Set(compensator.compensate_global_matrix(mat))


def compensate_skeleton(skeleton: UsdSkel.Skeleton, compensator: Compensator) -> None:
    if attr := skeleton.GetRestTransformsAttr():
        attr.Set([compensator.compensate_local_matrix(mat) for mat in attr.Get()])
    return
    if attr := skeleton.GetBindTransformsAttr():
        attr.Set([compensator.compensate_global_matrix(mat) for mat in attr.Get()])


def get_axis_compensation_rotation_transform(src: Token, dst: Token) -> Gf.Matrix4d:
    return _AXIS_COMPENSATION_ROTATION[src, dst]


def get_axis_compensation_scale_transform(src_meters_per_unit: float, dst_meters_per_unit: float) -> Gf.Matrix4d:
    factor = src_meters_per_unit / dst_meters_per_unit
    return Gf.Matrix4d().SetScale(Gf.Vec3d(factor, factor, factor))


def get_xformable_compensation_matrix(xformable: UsdGeom.Xformable) -> Gf.Matrix4d:
    op = xformable.GetXformOp(UsdGeom.XformOp.TypeTransform, opSuffix="compensation")
    return op.GetOpTransform(Usd.TimeCode()) if op else Gf.Matrix4d().SetIdentity()


def get_xformable_payload_matrix(xformable: UsdGeom.Xformable) -> Gf.Matrix4d:
    full_mat = xformable.GetLocalTransformation()
    compensation_mat = get_xformable_compensation_matrix(xformable)
    return full_mat * compensation_mat.GetInverse()


def prim_is_marked_as_excluded_from_compensation(prim: Usd.Prim) -> bool:
    return prim.GetName().endswith("_ExcludedFromCompensation")


def main(src_path: Path, dst_path: Path, dst_up_axis: Token, dst_meters_per_unit: float) -> None:
    stage = Usd.Stage.Open(str(src_path))

    # Axis compensation transform

    src_up_axis = UsdGeom.GetStageUpAxis(stage)
    src_meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)

    s = get_axis_compensation_scale_transform(src_meters_per_unit, dst_meters_per_unit)
    r = get_axis_compensation_rotation_transform(src_up_axis, dst_up_axis)
    axis_compensation_matrix = s * r

    UsdGeom.SetStageMetersPerUnit(stage, dst_meters_per_unit)
    UsdGeom.SetStageUpAxis(stage, dst_up_axis)

    data = stage.GetRootLayer().customLayerData
    data["original_up_axis"] = src_up_axis
    data["original_meters_per_unit"] = src_meters_per_unit
    data["axis_compensation_matrix"] = axis_compensation_matrix
    stage.GetRootLayer().customLayerData = data

    # Traverse the Stage and compensate objects

    compensate = Compensator()

    prims_iterator = iter(Usd.PrimRange.PreAndPostVisit(stage.GetPseudoRoot()))
    for prim in prims_iterator:
        if prim_is_marked_as_excluded_from_compensation(prim):
            continue

        # Entering a Prim

        if not prims_iterator.IsPostVisit():

            logging.debug("entering %s", prim)

            if prim.IsPseudoRoot():
                compensate.push_compensation_matrix(axis_compensation_matrix)
            
            if xformable := UsdGeom.Xformable(prim):
                mat = get_xformable_compensation_matrix(xformable)
                compensate.push_compensation_matrix(mat)

                compensate_xformable(xformable, compensate)
            
            if point_based := UsdGeom.PointBased(prim):
                compensate_pointbased(point_based, compensate)

            if skel_binding_api := UsdSkel.BindingAPI(prim):
                compensate_skel_binding_api(skel_binding_api, compensate)
            
            if skeleton := UsdSkel.Skeleton(prim):
                compensate_skeleton(skeleton, compensate)

        # Leaving a Prim
        
        else:
            logging.debug("leaving %s", prim)

            # Only PseudoRoot and Xformable push compensation transforms

            if prim.IsPseudoRoot() or UsdGeom.Xformable(prim):
                compensate.pop_compensation_matrix()

    # The list of compensation matrices should be empty

    assert(not compensate._compensation_matrices)

    # All done

    stage.Export(str(dst_path))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--debug", "-d", action="store_true", default=False)
    parser.add_argument("--destination-up-axis", "-a", choices=[UsdGeom.Tokens.y, UsdGeom.Tokens.z], default=UsdGeom.Tokens.z)
    parser.add_argument("--destination-meters-per-unit", "-u", type=float, default=1.0)

    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    main(args.source, args.destination, args.destination_up_axis, args.destination_meters_per_unit)
