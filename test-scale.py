from pxr import Gf

O = Gf.Vec3d(0, 0, 0)
I = Gf.Matrix4d().SetIdentity()

Tde = Gf.Matrix4d().SetScale(Gf.Vec3d(1/1000, 1, 1))
T = Tde
Ti = T.GetInverse()

M0 = Gf.Matrix4d().SetScale(Gf.Vec3d(10, 1, 1))
C0 = M0
R0 = I

M1 = Gf.Matrix4d().SetScale(Gf.Vec3d(100, 1, 1))
C1 = M1
R1 = I

M2 = Gf.Matrix4d().SetTranslate(Gf.Vec3d(2, 0, 0))
C2 = I
R2 = M2

Mge = Ti * M2 * M1 * M0 * T
Pe = Mge.Transform(O)

print(Pe)  # Should be x == 2


Mge = Ti * R2 * C2 * T * Ti * R1 * C1 * T * Ti * R0 * C0 * T
Pe = Mge.Transform(O)

print(Pe)  # Should be x == 2
