---
name: material-takeoff
description: Extract building materials and quantities from an IFC (Industry Foundation Classes) file, match them against environmental databases (oekobaudat, ICE), and produce an Excel take-off with embodied carbon per element. Trigger when the user provides an .ifc file and asks for a material take-off, bill of materials, embodied carbon, LCA, or environmental impact analysis of a building model.
---

# Material Take-Off

End-to-end workflow that turns an IFC building model into an Excel take-off with
matched environmental data.

## Inputs

- An IFC file path (required)
- Optional output path for the Excel workbook (default: same directory as the
  IFC, `<ifc-stem>-takeoff.xlsx`)

## Prerequisites

The renderer uses [uv](https://docs.astral.sh/uv/) to run Python with declared
dependencies. If `uv` is missing, point the user at
`https://docs.astral.sh/uv/getting-started/installation/` and stop.

## Workflow

### Phase 0 — Register

Before anything else, register this device against the user's email and emit a
heartbeat. This is how we know who uses the plugin. The take-off still runs if
this step fails — never block on it.

1. Resolve the user's email. Claude Code exposes it as `userEmail` in the
   session context. If that's missing, ask the user once and remember it for
   the rest of the conversation.
2. Pick the platform binary as in Phase 1 below.
3. Generate a `runId` (any UUID — `uuidgen` on macOS/Linux,
   `[guid]::NewGuid()` in PowerShell). Use this same `runId` for the
   `--run-id` arg in Phase 3.
4. Run `<binary> register --email <userEmail>` — JSON stdout shape:
   `{ "fingerprint": "…", "runCount": N, "registered": true|false }`.
5. Run `<binary> status` — JSON stdout includes `runCount`.
6. Show the user:
   - If `runCount == 1`:
     > 👋 Welcome to **nio Material Take-Off** — public beta. Thanks for
     > trying it! We've registered this device against `<email>` so we can
     > keep you in the loop on the upcoming activation flow.
   - If `runCount > 1`:
     > nio MTO · public beta · run #N
7. Continue to Phase 1.

The user can opt out of telemetry by setting `NIO_NO_TELEMETRY=1` in their
environment. The `register` and `status` calls still succeed; they just don't
ping the server.

### Phase 1 — Extract

The bundled `mto` binary parses the IFC and emits an `ExtractionResult` JSON to
stdout: project info, every element with raw quantities, the list of distinct
material names, and a `Warnings` array.

1. Resolve the binary. The plugin ships a `fetch-binary` script that picks
   the right platform automatically and downloads from GitHub Releases on
   first use. Use it rather than hard-coding paths:

   - macOS / Linux: `binary=$(bash ${CLAUDE_PLUGIN_ROOT}/skills/material-takeoff/scripts/fetch-binary.sh)`
   - Windows PowerShell: `$binary = & "$env:CLAUDE_PLUGIN_ROOT/skills/material-takeoff/scripts/fetch-binary.ps1"`

   Supported platforms: `darwin-arm64`, `darwin-x64`, `linux-arm64`,
   `linux-x64`, `win-x64`.

2. Run `<binary> extract <ifc-path> > /tmp/mto-extract.json`. On non-zero exit,
   surface stderr to the user and stop.
3. Parse the JSON. Shape:
   ```
   { Project,
     Elements,
     DistinctMaterials: [{ Name, ElementTypes: [string] }],
     Warnings: [{Code, Level, Message, Context}] }
   ```
4. **Always surface warnings to the user before proceeding.** They flag issues
   that materially affect the take-off:

- `ifc.schema.not_ifc4` — model isn't IFC4. Take-off may be incomplete.
- `material.missing` — N elements have no material. Their rows in the Building
  Elements sheet will be blank.
- `quantity.missing` — N elements have no exported BaseQuantities. They can't
  contribute to volumes/areas.
- `element.proxy` — IfcBuildingElementProxy present. Geometry not classified
  into structural types.

5. If `fetch-binary` exits with "Unsupported platform", tell the user the
   plugin doesn't support this platform yet — do NOT fall back to another
   tool.

### Phase 2 — Match

Each entry in `DistinctMaterials` carries `Name` and `ElementTypes` (the IFC
element types this material appears on). Use both — the element type drastically
narrows what categories are plausible (an IfcBeam never wants a "Roofing
membrane" match).

For each material, in two steps:

**2a. Expand and clarify the name.** IFC material names are often abbreviated,
multilingual, or internal codes ("stb." → Stahlbeton → reinforced concrete; "WD"
on an IfcWall layer → Wärmedämmung / thermal insulation). Use the `ElementTypes`
as context. Write your expanded interpretation alongside the original name —
this is your audit trail and what you'll feed the prefilter.

**2b. Prefilter, then pick.** For each database:

- `${CLAUDE_PLUGIN_ROOT}/skills/material-takeoff/databases/oekobaudat-en.json` (
  `--db oekobaudat`)
- `${CLAUDE_PLUGIN_ROOT}/skills/material-takeoff/databases/ICE.json` (
  `--db ICE`)

Call the prefilter with the expanded name and the element types:

```
python3 scripts/prefilter.py <database> "<expanded-name>" \
    --db <oekobaudat|ICE> \
    --element-types IfcBeam,IfcColumn \
    --top 20
```

The prefilter:

- Filters DB candidates by category compatibility with the element types (uses
  `scripts/element_categories.json`)
- Then scores by token overlap on the reduced set
- Logs the candidate-count reduction to stderr

This typically cuts ~1800 oekobaudat entries to 50–200 *before* scoring. Pick
the best match from the returned top-20 using judgment (concrete-grade
equivalences, structural vs decorative variants, regulatory conformity). If no
candidate is plausible, leave the match empty.

Produce a `matches.json` file at `/tmp/mto-matches.json` with this shape:

```json
{
  "Matches": [
    {
      "IfcMaterialName": "Normalbeton C35/37",
      "Okobaudat": { /* full database row */ },
      "Confidence": "high",
      "Rationale": "C35/37 grade matches directly; structural concrete on IfcSlab"
    },
    { "IfcMaterialName": "Unknown Material X", "Okobaudat": null, "Confidence": "none", "Rationale": "No plausible candidate in oekobaudat or ICE" }
  ]
}
```

Each `Okobaudat` object must include
`Uuid, Name, Category, EmbodiedCarbon, WholeLifeCarbon, CarbonUnit, Conformity, CountryCode, Url, Quantities { ReferenceQuantity, ReferenceUnit, Density?, ArealDensity?, ... }`.
Copy the matched row verbatim from the database — don't paraphrase.

`Confidence` is one of `"high" | "medium" | "low" | "none"`. `Rationale` is a
one-sentence explanation of *why* this candidate was chosen (or why nothing
matched). Both appear in the Matches sheet of the workbook — the audit trail the
user reviews after the fact.

Do all materials before moving on. Don't ask the user to confirm each match;
produce the full draft and let them review in the Excel.

### Phase 3 — Build complete model

Run the binary's second pass to enrich the extraction with the matches and
compute aggregated weights + LCA. Pass the `runId` you generated in Phase 0
so the per-material match events get linked to the rest of this run's
telemetry:

```
<binary> build-model /tmp/mto-extract.json /tmp/mto-matches.json \
  --run-id <runId> --database oekobaudat \
  > /tmp/mto-complete.json
```

The output is a `CompleteModel` JSON containing the project, every element with
matched ökobaudat and per-quantity LCA, plus a `MaterialGroups` array with
aggregated quantities and LCA per distinct material.

### Phase 4 — Render Excel

Hand the complete model to the renderer:

```
uv run ${CLAUDE_PLUGIN_ROOT}/skills/material-takeoff/scripts/build-xlsx.py \
  /tmp/mto-complete.json <output-path>
```

The renderer validates the JSON with pydantic before writing — any schema drift
between the binary and the renderer fails loud with a field path, not a silent
bad workbook.

Report the output path to the user. If any warnings fired in Phase 1, restate
them so the user knows what's *not* in the workbook.

## Notes for future maintainers

- The `mto` binary lives at `src/MaterialTakeOff/`. Build with
  `./plugin/build-binaries.sh` from the repo root.
- Pydantic models are in `scripts/models.py` and mirror the .NET record types
  via PascalCase aliases. Any field added on the .NET side that the renderer
  needs must be added to `models.py` too.
- Bundled databases are snapshots. A future `update-databases` command will
  refresh them from upstream.
