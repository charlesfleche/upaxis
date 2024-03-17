# USD axis conversion test

## Goals

- Animators author in DCC that are Y-Up
- But animation tracks are difficult to convert to other Up-Axis
- So we want to author skinning / animation in Z-Up
- Hence we need to compensate by the inverse of Z-Up -> Y-Up transform somewhere when working in the DCC...
- ...and compensate by the inverse of the inverse when exporting to the Engine

## Files

- [zup-reference.usda](zup-reference.usda) the scene as it should be in the Engine editor, Z-Up
- [yup-src.usda](yup-src.usda) the scene as it should be edited in the DCC:
  - Coordinate system is Y-Up
  - But skinning / animation is done in Z-Up so it is edited in the Engine coordinate system