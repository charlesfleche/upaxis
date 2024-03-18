from pxr import Gf, Usd, UsdGeom

def convert_xformable(x):
    m = x.GetLocalTransformation()

    assert(x.ClearXformOpOrder())

    op = x.AddXformOp(UsdGeom.XformOp.TypeTransform, opSuffix="Tde", isInverseOp=True)
    assert(op)

    op = x.AddXformOp(UsdGeom.XformOp.TypeTransform, opSuffix="src")
    assert(op.Set(m))

    op = x.AddXformOp(UsdGeom.XformOp.TypeTransform, opSuffix="Tde")
    assert(op.Set(Tde))

    # Store the result of the operator stack

    m = x.GetLocalTransformation()
    op = x.AddXformOp(UsdGeom.XformOp.TypeTransform, opSuffix="dst")
    assert(op.Set(m))

    op = x.AddXformOp(UsdGeom.XformOp.TypeTransform, opSuffix="dst", isInverseOp=True)
    assert(op)


s = Usd.Stage.Open("yup-src-reference.usda")
s.Export("out-yup-src.usda")

UsdGeom.SetStageUpAxis(s, "Z")

Rde = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90)  # Rotation DCC to Engine
Tde = Gf.Matrix4d().SetRotate(Rde)  # Transformation DCC to Engine

for p in s.Traverse():
    if p.GetName() == "Axis":
        continue

    if x := UsdGeom.Xformable(p):
        convert_xformable(x)


s.Export("out-zup-dst.usda")
