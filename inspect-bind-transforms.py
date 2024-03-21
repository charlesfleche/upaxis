#!python

import argparse

from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom, UsdSkel

_ORIGIN = Gf.Vec3d(0, 0, 0)

def main(stage_path: Path) -> None:
    stage = Usd.Stage.Open(str(stage_path))

    for prim in stage.Traverse():
        mesh = UsdGeom.Mesh(prim)
        binding = UsdSkel.BindingAPI(prim)

        if not (mesh and binding):
            continue
        
        cache = UsdGeom.XformCache()

        attr = binding.GetGeomBindTransformAttr()
        if not attr:
            continue

        prim_geom_bind_transform = attr.Get()
        prim_local_to_world_transform = cache.GetLocalToWorldTransform(prim)

        mat = prim_geom_bind_transform * prim_local_to_world_transform

        print(mesh)
        for point in mesh.GetPointsAttr().Get():
            print("Point", point, "->", mat.Transform(point))

        targets = binding.GetSkeletonRel().GetTargets()
        if len(targets) != 1:
            continue

        skel_prim = stage.GetPrimAtPath(targets[0])
        skel = UsdSkel.Skeleton(skel_prim)
        if not skel:
            continue

        prim_local_to_world_transform = cache.GetLocalToWorldTransform(skel_prim)

        print(skel)
        for bind_transform in skel.GetBindTransformsAttr().Get():
            mat = bind_transform * prim_local_to_world_transform
            joint_position = mat.Transform(_ORIGIN)
            print(bind_transform, "->", mat, ", Position", joint_position)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("stage_path", type=Path)

    args = parser.parse_args()

    main(args.stage_path)
