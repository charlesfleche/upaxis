#!python

import argparse
from pathlib import Path

from pxr import Gf, Tf, Usd, UsdGeom, UsdSkel

Token = str

_MATRIX_IDENTITY = Gf.Matrix4d().SetIdentity()
_MATRIX_ROTATION_POSITIVE_90_DEGREES_AROUND_X = Gf.Rotation(Gf.Vec3d(1, 0, 0), 90)
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

def get_axis_compensation_rotation_transform(src: Token, dst: Token) -> Gf.Matrix4d:
    return _AXIS_COMPENSATION_ROTATION[src, dst]

def get_axis_compensation_scale_transform(src_meters_per_unit: float, dst_meters_per_unit: float) -> Gf.Matrix4d:
    factor = src_meters_per_unit / dst_meters_per_unit
    return Gf.Matrix4d().SetScale(Gf.Vec3d(factor, factor, factor))


def main(src_path: Path, dst_path: Path, dst_up_axis: Token, dst_meters_per_unit: float) -> None:
    stage = Usd.Stage.Open(str(src_path))

    # Axis compensation transform

    src_up_axis = UsdGeom.GetStageUpAxis(stage)
    src_meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)

    s = get_axis_compensation_scale_transform(src_meters_per_unit, dst_meters_per_unit)
    r = get_axis_compensation_rotation_transform(src_up_axis, dst_up_axis)
    axis_compensation_matrix = s * r

    data = stage.GetRootLayer().customLayerData
    data["original_up_axis"] = src_up_axis
    data["original_meters_per_unit"] = src_meters_per_unit
    data["axis_compensation_matrix"] = axis_compensation_matrix
    stage.GetRootLayer().customLayerData = data

    UsdGeom.SetStageMetersPerUnit(stage, dst_meters_per_unit)
    UsdGeom.SetStageUpAxis(stage, dst_up_axis)

    stage.Export(str(dst_path))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--destination-up-axis", "-a", choices=["Y", "y", "Z", "z"], default="Z")
    parser.add_argument("--destination-meters-per-unit", "-u", type=float, default=1.0)

    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)

    args = parser.parse_args()

    main(args.source, args.destination, _AXIS_NAME_TO_TOKEN[args.destination_up_axis.upper()], args.destination_meters_per_unit)
