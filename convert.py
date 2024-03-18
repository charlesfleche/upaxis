from pxr import Gf, Usd, UsdGeom

def convert_Xformable(x, Tde):
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


def convert_PointBased(pb, Tde):
    def convert(*vec):
        m = Gf.Matrix4d().SetTranslate(Gf.Vec3d(*vec))
        m = Tde * m * Tde.GetInverse()
        return Gf.Transform(m).GetTranslation()

    a = pb.GetPointsAttr()
    assert(a)

    assert(a.Set([convert(vec) for vec in a.Get()]))


def is_compensated(x):
    op = x.GetXformOp(UsdGeom.XformOp.TypeRotateXYZ, opSuffix="compensation")
    return bool(op)


def decompensate(x):
    ops = x.GetOrderedXformOps()
    
    op = x.AddXformOp(UsdGeom.XformOp.TypeRotateXYZ, opSuffix="compensation", isInverseOp=True)
    assert(op)

    ops.insert(0, op)

    assert(x.ClearXformOpOrder())

    a = x.GetXformOpOrderAttr()
    assert(a)

    assert(a.Set([op.GetOpName() for op in ops]))


s = Usd.Stage.Open("yup-src-reference.usda")
s.Export("out-yup-src.usda")

UsdGeom.SetStageUpAxis(s, "Z")

_Rde = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90)  # Rotation DCC to Engine
_Tde = Gf.Matrix4d().SetRotate(_Rde)  # Transformation DCC to Engine

_Identity = Gf.Matrix4d().SetIdentity()

curTde = _Tde

it = iter(Usd.PrimRange.PreAndPostVisit(s.GetPseudoRoot()))

for p in it:
    if p == s.GetPseudoRoot():
        continue

    assert(p)

    if p.GetName() == "Axis":
        continue

    if x := UsdGeom.Xformable(p):
        if is_compensated(x):
            if it.IsPostVisit():
                curTde = _Tde
                continue
            else:
                decompensate(x)
                curTde = _Identity
        convert_Xformable(x, curTde)
    
    if pb := UsdGeom.PointBased(p):
        convert_PointBased(pb, curTde)


s.Export("out-zup-dst.usda")
