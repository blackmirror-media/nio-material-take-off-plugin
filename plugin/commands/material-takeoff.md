---
description: Extract materials from an IFC file, match against oekobaudat/ICE, produce an Excel take-off
argument-hint: <ifc-path> [output-path]
---

Run a material take-off on the IFC file at `$1`.

Use the `material-takeoff` skill to:

1. Extract elements, materials, and quantities from the IFC via the bundled
   binary
2. Match each distinct material against the oekobaudat and ICE databases
3. Produce an Excel workbook at `$2` (default: alongside the input IFC) with the
   take-off, matched materials, and
   embodied carbon per element

If `$1` is empty, ask the user for the IFC path.
