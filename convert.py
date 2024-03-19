from pxr import Gf, Usd, UsdGeom, UsdSkel

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


def convert_Skeleton(sk, Tde):
    if a := sk.GetRestTransformsAttr():
        if ms := a.Get():
            a.Set([Tde * m * Tde.GetInverse() for m in ms])


def is_compensated(x):
    op = x.GetXformOp(UsdGeom.XformOp.TypeRotateXYZ, opSuffix="compensation")
    return bool(op)


def decompensate_Xformable(x):
    ops = x.GetOrderedXformOps()
    
    op = x.AddXformOp(UsdGeom.XformOp.TypeRotateXYZ, opSuffix="compensation", isInverseOp=True)
    assert(op)

    ops.insert(0, op)

    assert(x.ClearXformOpOrder())

    a = x.GetXformOpOrderAttr()
    assert(a)

    assert(a.Set([op.GetOpName() for op in ops]))


def decompensate_SkelBindingAPI(sb, Tde):
    if a := sb.GetGeomBindTransformAttr():
        if m := a.Get():
            a.Set(m * Tde.GetInverse())


def decompensate_Skeleton(sk, Tde):
    if a := sk.GetBindTransformsAttr():
        if ms := a.Get():
            a.Set([m * Tde.GetInverse() for m in ms])


s = Usd.Stage.Open("yup-src-reference.usda")
s.Export("out-yup-src.usda")

UsdGeom.SetStageUpAxis(s, "Z")

_Rde = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90)  # Z-Up to Y-Up
_Tde = Gf.Matrix4d().SetRotate(_Rde)  # Transformation Z-Up to Y-Up

_Identity = Gf.Matrix4d().SetIdentity()

curLocalTde = _Tde
curGlobalTde = _Identity

it = iter(Usd.PrimRange.PreAndPostVisit(s.GetPseudoRoot()))

for p in it:
    if p == s.GetPseudoRoot():
        continue

    assert(p)

    if p.GetName() == "Axis":
        continue

    x = UsdGeom.Xformable(p)
    if x and is_compensated(x):
        if it.IsPostVisit():
            curLocalTde = _Tde
            curGlobalTde = _Identity
        else:
            curLocalTde = _Identity
            curGlobalTde = _Tde

            # For the demo we target an existing xformOp in the Prim, but in
            # practice we'd pass the curGlobalTde
            # decompensate_Xformable(x, curGlobalTde)
            decompensate_Xformable(x)

    if it.IsPostVisit():
        continue

    if x := UsdGeom.Xformable(p):
        convert_Xformable(x, curLocalTde)
    
    if pb := UsdGeom.PointBased(p):
        convert_PointBased(pb, curLocalTde)
    
    if sb := UsdSkel.BindingAPI(p):
        decompensate_SkelBindingAPI(sb, curGlobalTde)

    if sk := UsdSkel.Skeleton(p):
        decompensate_Skeleton(sk, curGlobalTde)
        convert_Skeleton(sk, curLocalTde)


s.Export("out-zup-dst.usda")
