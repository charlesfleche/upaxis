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

# print("C", C)

p0 = Gf.Vec3d(0, 0, 0)
p1 = Gf.Vec3d(.5, 0, 0)
p2 = Gf.Vec3d(0, 0, 1)

GBT = Gf.Transform()

s = Gf.Vec3d(10, 10, 10)
rzy = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90)
rxy = Gf.Rotation(Gf.Vec3d(0, 0, 1), 90)
rxz = Gf.Rotation(Gf.Vec3d(0, 1, 0), -90)
t = Gf.Vec3d(1, 0, 0)

# GBT.SetScale(s)
# GBT.SetTranslation(t)
# GBT.SetPivotPosition(-t)
#GBT.SetPivotOrientation(rxz)
# GBT.SetRotation(rzy * rxy)
# GBT = GBT.GetMatrix()

S = Gf.Matrix4d().SetScale(s)
R = Gf.Matrix4d().SetRotate(rzy * rxy)
T = Gf.Matrix4d().SetTranslate(t)

GBT = T * R * S

print("GBT", GBT)
for p in (p0, p1, p2):
    print(p, "->", GBT.Transform(p))

print()

C = Gf.Transform()
C.SetScale(Gf.Vec3d(1/10, 1/10, 1/10))
C.SetRotation(Gf.Rotation(Gf.Vec3d(1, 0, 0), 90))
C = C.GetMatrix()
Ci = C.GetInverse()

print("C", C)

print("C-1 * GBT * C", Ci * GBT * C)

for p in (p0, p1, p2):
    m = Ci * GBT * C
    print(p, "->", m.Transform(p))

# b0 = Gf.Matrix4d().SetIdentity()
# b1 = Gf.Matrix4d().SetTranslate(Gf.Vec3d(0, 0, 1))

# for b in (b0, b1):
#     print(b, "->", b * GBT)

# print("")


print()

# t = Gf.Transform()
# t.SetRotate(Gf.Rotation())


print()

C0 = Gf.Transform()
C0.SetScale(Gf.Vec3d(1/10, 1/10, 1/10))
C0.SetRotation(Gf.Rotation(Gf.Vec3d(1, 0, 0), 90))
C0 = C0.GetMatrix()
C0i = C0.GetInverse()

C1 = C0i
C1i = C1.GetInverse()

p0 = Gf.Vec3d(  0, 10, 0)
p1 = Gf.Vec3d(  0, 15, 0)
p2 = Gf.Vec3d(-10, 10, 0)

for p in (p0, p1, p2):
    print(p, "-> C0 ->", C0.Transform(p))
print()

B = Gf.Matrix4d(
      0, 10,   0, 0,
      0,  0, -10, 0,
    -10,  0,   0, 0,
      0, 10,   0, 1
)

p0 = Gf.Vec3d(0,   0, 0)
p1 = Gf.Vec3d(0.5, 0, 0)
p2 = Gf.Vec3d(0,   0, 1)

for p in (p0, p1, p2):
    print(p, "-> B ->", B.Transform(p))
print()

Bp = B * C1i

for p in (p0, p1, p2):
    print(p, "-> Bp ->", Bp.Transform(p))
print()
