from pxr import Gf, Usd, UsdGeom

def convert_Xformable(x):
    m = x.GetLocalTransformation()
    assert(m)

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


def convert_PointBased(pb):
    def convert(*vec):
        m = Gf.Matrix4d().SetTranslate(Gf.Vec3d(*vec))
        m = Tde * m * Tde.GetInverse()
        return Gf.Transform(m).GetTranslation()

    a = pb.GetPointsAttr()
    assert(a)

    assert(a.Set([convert(vec) for vec in a.Get()]))


s = Usd.Stage.Open("yup-src-reference.usda")
s.Export("out-yup-src.usda")

UsdGeom.SetStageUpAxis(s, "Z")

Rde = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90)  # Rotation DCC to Engine
Tde = Gf.Matrix4d().SetRotate(Rde)  # Transformation DCC to Engine

for p in s.Traverse():
    if p.GetName() == "Axis":
        continue

    if x := UsdGeom.Xformable(p):
        convert_Xformable(x)
    
    if pb := UsdGeom.PointBased(p):
        convert_PointBased(pb)


s.Export("out-zup-dst.usda")
