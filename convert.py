from pxr import Gf, Usd, UsdGeom

s = Usd.Stage.Open("yup-src-reference.usda")
s.Export("out-yup-src.usda")

UsdGeom.SetStageUpAxis(s, "Z")



s.Export("out-zup-dst.usda")
