from pxr import Gf

o = Gf.Vec3d(0, 0, 0)

x1 = Gf.Vec3d(1, 0, 0)
y1 = Gf.Vec3d(0, 1, 0)
z1 = Gf.Vec3d(0, 0, 1)

Ryz = Gf.Rotation(x1, 90)
Tyz = Gf.Matrix4d().SetIdentity().SetRotate(Ryz)
Tzy = Tyz.GetInverse()

print("Tyz", Tyz)
for v in (x1, y1, z1):
    print(v)
    print(Tyz.Transform(v))

    mv = Gf.Matrix4d().SetIdentity().SetTranslate(v)
    print((mv * Tyz).Transform(o))
    print()

print("#\n")

p0 = Gf.Vec3d(0, 0, 1)
p1 = Gf.Vec3d(.5, 0, 1)
p2 = Gf.Vec3d(0, 0, 2)

print("Tzy", Tzy)
for v in (p0, p1, p2):
    print(v)
    print(Tzy.Transform(v))
    print()

print("#\n")

bb = Gf.Matrix4d(
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
	0.0, 0.0, 1.0, 0.0,
	0.0, 0.0, 1.0, 1.0
)

bt = Gf.Matrix4d(
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
	0.0, 0.0, 1.0, 0.0,
	0.0, 0.0, 2.0, 1.0
)

for m in (bb, bt):
    print(m)
    print(m * Tzy)
    print(m * Tzy * Tyz)
