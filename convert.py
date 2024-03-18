from pxr import Usd

s = Usd.Stage.Open("zup-dst.usda")

s.Save()
