# USD axis conversion test

## Goals

- Animators author in DCC that are Y-Up
- But animation tracks are difficult to convert to other Up-Axis
- So we want to author skinning / animation in Z-Up
- Hence we need to compensate by the inverse of Z-Up -> Y-Up transform somewhere when working in the DCC...
- ...and compensate by the inverse of the inverse when exporting to the Engine

## Files

In all scene a tetrahedron at the base of the origin (`Ox`, `oY` and `oZ` edges are of size = 1) represents the coordinate system:
- coordinates along x are red
- coordinates along y are green
- coordinates along z are blue

- [`zup-reference.usda`](zup-reference.usda) the scene as it should be in the Engine editor, Z-Up
- [`yup-src.usda`](yup-src.usda) the scene as it should be edited in the DCC:
  - Coordinate system is Y-Up
  - But skinning / animation is done in Z-Up so it is edited in the Engine coordinate system
  - The Axis Compensation matrix `xformOp:rotateXYZ:compensation` (Y-Up to Z-Up) is added to the root object `SkelRoot`
- [`zup-dst.usda`](zup-dst.usda) the scene as export from DCC then imported to the Engine
  - It sublayers `yup-src.usda` to simulate an export from DCC
  - The Axis Compensation matrix is reverted by applying its inverse `!invert!xformOp:rotateXYZ:compensation`
  - The stage up axis is simply set to Z

The `offset-*` versions of those files introduces a few extra transformations:

## Solution

d = DCC
e = Engine

g = global matrix

M = matrix
P = other matrix local to M

Mdg = Md0 * Md1 * ... * Mdn
Mdg = Ted * Me0 * Me1 * ... * Men
Mdg = Ted * Meg

Meg = Tde * Mdg * Tde-1
Meg = Tde * [Ted * Meg] * Tde-1
Meg = Tde * [Ted * Me0 * Me1 * ... * Men] * Tde-1
Meg = Tde * [Ted * Me0] * Me1 * ... * Men * Tde-1
Meg = Tde * Ted-1 * [Ted * Me0] * Me1 * ... * Men * Tde-1
Meg = Tde * Me0 * Me1 * ... * Men * Tde-1
Meg =  Me0 * Me1 * ... * Men  # if Tde == Identity

In practice:
  - Compensate
    - Local matrices marqued as ALREADY_COMPENSATED then don't compensate descendant matrices
      - Entity Xform
  - Global matrices
    - Mesh GeomBindTransforms
    - Skeleton bindTransforms
