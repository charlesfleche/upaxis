from pxr import Gf, Usd, UsdGeom

print("test-skel-zup-m.usda")

p0 = Gf.Vec3d(0, 0, 0)
p1 = Gf.Vec3d(.5, 0, 0)
p2 = Gf.Vec3d(0, 0, 1)

GBT = Gf.Transform()
GBT.SetRotation(Gf.Rotation(Gf.Vec3d(0, 1, 0), -90))
GBT.SetTranslation(Gf.Vec3d(0, 0, 1))

GBT = GBT.GetMatrix()
print("GBT", GBT)

b0 = Gf.Matrix4d().SetIdentity()
b1 = Gf.Matrix4d().SetTranslate(Gf.Vec3d(0, 0, 1))

for b in (b0, b1):
    print("joint", b, "->", b * GBT)

print()

print("test-skel-yup-m.usda")

p0 = Gf.Vec3d(0, 0, 0)
p1 = Gf.Vec3d(.5, 0, 0)
p2 = Gf.Vec3d(0, 1, 0)

GBT = Gf.Transform()
GBT.SetRotation(Gf.Rotation(Gf.Vec3d(0, 0, 1), 90))
GBT.SetTranslation(Gf.Vec3d(0, 1, 0))

GBT = GBT.GetMatrix()
print("GBT", GBT)

b0 = Gf.Matrix4d().SetIdentity()
b1 = Gf.Matrix4d().SetTranslate(Gf.Vec3d(0, 1, 0))

for b in (b0, b1):
    print("joint", b, "->", b * GBT)

print()

print("test-skel-yup-dm-compensated_to-zup-m.usda")

C = Gf.Transform()
C.SetScale(Gf.Vec3d(10, 10, 10))
C.SetRotation(Gf.Rotation(Gf.Vec3d(1, 0, 0), -90))
C = C.GetMatrix()

print("C", C)