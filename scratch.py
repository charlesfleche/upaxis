from pxr import Gf, Usd, UsdGeom

s = Usd.Stage.Open("test-compensation_skeleton.usda")

p = s.GetPrimAtPath("/SkelRoot_CompensatedZToYDecimetersToMeters")
c = UsdGeom.XformCache()
print(c.GetLocalToWorldTransform(p))
print(c.GetParentToWorldTransform(p))
m, _ = c.GetLocalTransformation(p)
print(m)

print()

p = s.GetPrimAtPath("/SkelRoot_CompensatedZToYDecimetersToMeters/Skeleton")
c = UsdGeom.XformCache()
print(c.GetLocalToWorldTransform(p))
print(c.GetParentToWorldTransform(p))
m, _ = c.GetLocalTransformation(p)
print(m)


L = c.GetLocalToWorldTransform(p)

print()

O = Gf.Vec3d(0, 0, 0)

r = Gf.Rotation(Gf.Vec3d(0, 1, 0), -90)
t = Gf.Vec3d( 0, 0, 1)

p0 = Gf.Vec3d( 0, 0, 0)
p1 = Gf.Vec3d(.5, 0, 0)
p2 = Gf.Vec3d( 0, 0, 1)

GBT = Gf.Transform()
GBT.SetRotation(r)
GBT.SetTranslation(t)

print("GBT ->", GBT.GetMatrix())
print()

for p in (p0, p1, p2):
    print(p, "->", GBT.GetMatrix().Transform(p))

print()

b0 = Gf.Transform()
b0.SetTranslation(p0)
b0 = b0.GetMatrix()

b1 = Gf.Transform()
b1.SetTranslation(p2)
b1 = b1.GetMatrix()

for bt in (b0, b1):
    m = bt * GBT.GetMatrix()
    print(bt, "->", m, "->", m.Transform(O))
