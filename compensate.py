#!python

import argparse
from pathlib import Path

from pxr import Gf, Tf, Usd, UsdGeom, UsdSkel

Token = str

_VECTOR_ORIGIN = Gf.Vec3d(0, 0, 0)

_MATRIX_IDENTITY = Gf.Matrix4d().SetIdentity()
_MATRIX_ROTATION_POSITIVE_90_DEGREES_AROUND_X = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), 90))
_MATRIX_ROTATION_NEGATIVE_90_DEGREES_AROUND_X = _MATRIX_ROTATION_POSITIVE_90_DEGREES_AROUND_X.GetInverse()

_AXIS_NAME_TO_TOKEN = {
    "Y": UsdGeom.Tokens.y,
    "Z": UsdGeom.Tokens.z,
}

_AXIS_COMPENSATION_ROTATION = {
    (UsdGeom.Tokens.y, UsdGeom.Tokens.y): _MATRIX_IDENTITY,                               # From Y-Up to Y-Up
    (UsdGeom.Tokens.y, UsdGeom.Tokens.z): _MATRIX_ROTATION_POSITIVE_90_DEGREES_AROUND_X,  # From Y-Up to Z-Up
    (UsdGeom.Tokens.z, UsdGeom.Tokens.y): _MATRIX_ROTATION_NEGATIVE_90_DEGREES_AROUND_X,  # From Z-Up to Y-Up
    (UsdGeom.Tokens.z, UsdGeom.Tokens.z): _MATRIX_IDENTITY,                               # From Z-Up to Z-Up
}

class Compensator:
    def __init__(self):
        self._compensation_matrix = Gf.Matrix4d().SetIdentity()
        self._compensation_matrices = []
    
    def __call__(self, mat: Gf.Matrix4d) -> Gf.Matrix4d:
        return self._compensation_matrix.GetInverse() * mat * self._compensation_matrix

    def push_compensation_matrix(self, mat: Gf.Matrix4d) -> None:
        mat = Gf.Matrix4d(mat)  # Ensure mat is copied, just not referenced
        self._compensation_matrix *= mat
        self._compensation_matrices.append(mat)

    def pop_compensation_matrix(self) -> None:
        mat = self._compensation_matrices.pop()
        self._compensation_matrix *= mat.GetInverse()

def compensate_xformable(xformable: UsdGeom.Xformable, compensate: Compensator) -> None:
    mat = xformable.GetLocalTransformation()
    op = xformable.MakeMatrixXform()
    op.Set(compensate(mat))


def compensate_pointbased(point_based: UsdGeom.PointBased, compensate: Compensator) -> None:
    def compensate_vector(*vec):
        mat = Gf.Matrix4d().SetTranslate(Gf.Vec3d(*vec))
        mat = compensate(mat)
        return mat.Transform(_VECTOR_ORIGIN)

    points = point_based.GetPointsAttr()
    points.Set([compensate_vector(vec) for vec in points.Get()])


def get_axis_compensation_rotation_transform(src: Token, dst: Token) -> Gf.Matrix4d:
    return _AXIS_COMPENSATION_ROTATION[src, dst]


def get_axis_compensation_scale_transform(src_meters_per_unit: float, dst_meters_per_unit: float) -> Gf.Matrix4d:
    factor = src_meters_per_unit / dst_meters_per_unit
    return Gf.Matrix4d().SetScale(Gf.Vec3d(factor, factor, factor))


def get_xformable_compensation_matrix(xformable: UsdGeom.Xformable) -> Gf.Matrix4d:
    op = xformable.GetXformOp(UsdGeom.XformOp.TypeTransform, opSuffix="compensation")
    return op.GetOpTransform(Usd.TimeCode()) if op else Gf.Matrix4d().SetIdentity()


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

            if prim.IsPseudoRoot():
                compensate.push_compensation_matrix(axis_compensation_matrix)
            
            if xformable := UsdGeom.Xformable(prim):
                mat = get_xformable_compensation_matrix(xformable)
                compensate.push_compensation_matrix(mat)

                compensate_xformable(xformable, compensate)
            
            if point_based := UsdGeom.PointBased(prim):
                compensate_pointbased(point_based, compensate)


        # Leaving a Prim
        
        else:
            # Only PseudoRoot and Xformable push compensation transforms

            if prim.IsPseudoRoot() or UsdGeom.Xformable(prim):
                compensate.pop_compensation_matrix()

    # The list of compensation matrices should be empty

    assert(not compensate._compensation_matrices)

    # All done

    stage.Export(str(dst_path))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--destination-up-axis", "-a", choices=["Y", "y", "Z", "z"], default="Z")
    parser.add_argument("--destination-meters-per-unit", "-u", type=float, default=1.0)

    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)

    args = parser.parse_args()

    main(args.source, args.destination, _AXIS_NAME_TO_TOKEN[args.destination_up_axis.upper()], args.destination_meters_per_unit)
