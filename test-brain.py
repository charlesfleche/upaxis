import functools

from pxr import Gf

def mult(*mats):
    return functools.reduce(lambda a, b: a * b, mats, I)

def S(v):
    return Gf.Matrix4d().SetScale(Gf.Vec3d(v, 1, 1))

def T(v):
    return Gf.Matrix4d().SetTranslate(Gf.Vec3d(v, 0, 0))

I = Gf.Matrix4d().SetIdentity()

C = S(1/1000)
Ci = C.GetInverse()

C0 = S(10)
C0i = C0.GetInverse()
R0 = T(200)
M0 = mult(C0, R0)

C1 = S(10)
C1i = C1.GetInverse()
R1 = T(30)
M1 = mult(C1, R1)

C2 = S(10)
C2i = C2.GetInverse()
R2 = T(5)
M2 = mult(C2, R2)


print("M0", M0)
print("M1", M1)
print("M2", M2)


M0p = (          C0 * C).GetInverse() * R0 *           C0 * C
M1p = (     C1 * C0 * C).GetInverse() * R1 *      C1 * C0 * C
M2p = (C2 * C1 * C0 * C).GetInverse() * R2 * C2 * C1 * C0 * C

print("M0p", M0p)
print("M1p", M1p)
print("M2p", M2p)

Mp = M2p * M1p * M0p

print("Mp", Mp)
print(Ci * C0i * C1i * C2i * R2 * C2 * C1 * C0 * C)
