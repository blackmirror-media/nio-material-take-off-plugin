---
name: ifc-check
description: Validate an IFC building model for take-off readiness. Checks schema version (IFC4 recommended), presence of materials, exported BaseQuantities, and IfcBuildingElementProxy elements. Trigger when the user provides an .ifc file and asks whether it's usable, valid, ready for take-off, or what's wrong with it — without yet asking for a take-off itself.
---

# IFC Check

Cheap preflight on an IFC model. Runs in seconds, no matching, no LCA. Tells the
user whether `/material-takeoff` will produce a usable result and, if not, what
to fix.

## Inputs

- An IFC file path (required)

## Workflow

### Phase 0 — Register

Same as the `material-takeoff` skill: tell the binary who is using the plugin
so we can track adoption. Take-off is *not* gated by this.

1. Resolve the user's email from Claude's `userEmail` context (ask once if
   missing).
2. Run `<binary> register --email <userEmail>`. Best-effort; ignore failures.
3. Run `<binary> status` to learn `runCount`.
4. Show the welcome banner (`runCount == 1`) or one-line footer
   (`runCount > 1`) — same wording as the `material-takeoff` skill.

Continue to the actual check below regardless of telemetry outcome. Users can
opt out with `NIO_NO_TELEMETRY=1`.

### Phase 1 — Check

1. Resolve the binary via the fetch-binary script (auto-detects platform
   and downloads on first use):
   - macOS / Linux: `binary=$(bash ${CLAUDE_PLUGIN_ROOT}/skills/material-takeoff/scripts/fetch-binary.sh)`
   - Windows: `$binary = & "$env:CLAUDE_PLUGIN_ROOT/skills/material-takeoff/scripts/fetch-binary.ps1"`

   Supported: `darwin-arm64`, `darwin-x64`, `linux-arm64`, `linux-x64`, `win-x64`.

2. Run `<binary> check <ifc-path>`. The binary emits `{ warnings: [...] }` on
   stdout. Absence of a code = check passed.
3. Render the response using the **exact format below**. Show **all four checks
   ** every time — green ✅ when the code is *not* in the warnings list, red ⚠️
   when it is.
4. Match the user's chat language (English, German, Hungarian, etc.). Translate
   the descriptions but keep the codes and URLs verbatim.
5. Do NOT print the GUID list by default — say "ask me for the affected GUIDs if
   you want to double-check" and only print them if the user asks in a
   follow-up.

## Known checks

| Code                  | Short description                     | Help article                                                   |
|-----------------------|---------------------------------------|----------------------------------------------------------------|
| `ifc.schema.not_ifc4` | IFC version is IFC4                   | https://nio.energy/help/ifc-export-version (TODO: confirm URL) |
| `material.missing`    | All elements have a material assigned | https://nio.energy/help/ifc-materials (TODO: confirm URL)      |
| `quantity.missing`    | BaseQuantities are exported           | https://nio.energy/help/ifc-basequantities (TODO: confirm URL) |
| `element.proxy`       | No IfcBuildingElementProxy elements   | https://nio.energy/help/ifc-proxy-elements (TODO: confirm URL) |
| `units.unknown`       | All quantities use recognized units   | https://nio.energy/help/ifc-units (TODO: confirm URL)          |

When a new code appears in `IfcValidator.cs`, add a row here.

## Required response format

```
I checked **<filename>**.

<verdict line — see below>

| | Check | Result |
|---|---|---|
| <icon> | IFC version | <IFC4 / Ifc2X3 — older than IFC4> |
| <icon> | Materials assigned | <all N elements / N of M missing> |
| <icon> | BaseQuantities exported | <all N elements / N of M missing> |
| <icon> | No proxy elements | <none found / N IfcBuildingElementProxy elements> |

<per-failing-check: one line with help link>
- ⚠️ <Check name>: <one-sentence guidance>. See [help article](<url>).

Ask me for the affected GUIDs if you want to double-check which elements are involved.

<call to action>
```

**Icons:** ✅ for pass, ⚠️ for fail, ❌ for `error`-level fail.

**Verdict line (top of response):**

- All four ✅ → `**Model is ready for take-off.** Run \`
  /material-takeoff <path>\` to produce the workbook.`
- Any ⚠️ →
  `**Model has issues — the take-off will be incomplete.** Affected elements will be skipped and their embodied carbon will be missing from the result.`
- Any ❌ → `**Model can't be processed.** Fix the issues below and re-export.`

**Call to action (bottom):**

- All ✅ → repeat the `/material-takeoff` invitation
- Any ⚠️/❌ → "Fix the items above and re-run `/ifc-check`, or proceed with
  `/material-takeoff <path>` knowing the result will be limited."

## Example — partial failure (English)

> I checked **wall_window_2x3.ifc**.
>
> **Model has issues — the take-off will be incomplete.** Affected elements will
> be skipped and their embodied carbon will be missing from the result.
>
> | | Check | Result |
> |---|---|---|
> | ⚠️ | IFC version | Ifc2X3 — older than IFC4 |
> | ⚠️ | Materials assigned | 2 of 3 elements missing |
> | ⚠️ | BaseQuantities exported | 2 of 3 elements missing |
> | ✅ | No proxy elements | none found |
>
> - ⚠️ **IFC version:** Re-export from your CAD tool with IFC4 selected.
    See [help article](https://nio.energy/help/ifc-export-version).
> - ⚠️ **Materials assigned:** Some elements have no material. In Revit, check
    the Material parameter on the family type.
    See [help article](https://nio.energy/help/ifc-materials).
> - ⚠️ **BaseQuantities exported:** Enable "Export base quantities" in the IFC
    export settings.
    See [help article](https://nio.energy/help/ifc-basequantities).
>
> Ask me for the affected GUIDs if you want to double-check which elements are
> involved.
>
> Fix the items above and re-run `/ifc-check wall_window_2x3.ifc`, or proceed
> with `/material-takeoff wall_window_2x3.ifc` knowing the result will be
> limited.

## Example — all green (English)

> I checked **sample_hall_4.ifc**.
>
> **Model is ready for take-off.** Run `/material-takeoff sample_hall_4.ifc` to
> produce the workbook.
>
> | | Check | Result |
> |---|---|---|
> | ✅ | IFC version | IFC4 |
> | ✅ | Materials assigned | all 108 elements |
> | ✅ | BaseQuantities exported | all 108 elements |
> | ✅ | No proxy elements | none found |

## Notes

- Binary shared with `material-takeoff` skill.
- Help URLs above are placeholders (`TODO: confirm URL`) — replace with real
  article URLs as they're published.
