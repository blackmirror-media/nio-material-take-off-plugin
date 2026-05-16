---
description: Validate an IFC file for take-off readiness (schema, materials, quantities, proxy elements)
argument-hint: <ifc-path>
---

Run `ifc-check` on `$1`.

Use the `ifc-check` skill: invoke `mto check $1`, summarise the warnings to the
user, and end with a verdict on whether the model is ready for
`/material-takeoff`.

If `$1` is empty, ask the user for the IFC path.
