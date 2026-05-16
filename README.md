# nio Material Take-Off

Claude Code plugin that turns an IFC building model into an Excel material
take-off with embodied carbon, matched against the ÖKOBAUDAT environmental
database. Powered by the Claude LLM for semantic material matching (
abbreviations, German↔English, structural intent), with deterministic xBIM-based
IFC parsing and LCA arithmetic underneath.

## Install

You need [Claude Code](https://docs.anthropic.com/claude-code) installed first:

```bash
npm install -g @anthropic-ai/claude-code
```

Then open Claude Code in any terminal:

```bash
claude
```

And inside the Claude Code session, add the marketplace and install the plugin:

```
/plugin marketplace add blackmirror-media/nio-material-take-off@feature/claude-plugin
/plugin install material-takeoff@nio
```

> The `@feature/claude-plugin` suffix points at the active development branch.
> Once the plugin reaches v1 on `develop`, you can drop the suffix. Pinning a
> specific binary release: `@bin-v0.1.0-alpha.1`.

On first use, the plugin downloads a platform-specific binary (~80 MB) from
GitHub Releases. macOS and Windows x64 supported; Linux is intentionally out of
scope.

## Use

```
/ifc-check path/to/model.ifc
```

Preflight: validates IFC schema version, presence of materials, exported
quantities, and proxy elements. Returns a ✅/⚠️ table telling you whether the
model is ready for a take-off.

```
/material-takeoff path/to/model.ifc
```

Full pipeline:

1. Extract elements, materials, and quantities from the IFC
2. Match each distinct material against ÖKOBAUDAT, gated by element type
3. Compute density-derived weights and embodied + whole-life carbon per group
4. Write an Excel workbook (5 sheets: Summary, Materials, Building Elements,
   Matches, Warnings)

## What's in the box

- `src/MaterialTakeOff/` — the .NET binary (`mto`). Subcommands: `check`,
  `extract`, `build-model`, `register`, `status`.
- `plugin/skills/material-takeoff/` — the take-off skill, the Python renderer,
  ÖKOBAUDAT + ICE database snapshots.
- `plugin/skills/ifc-check/` — the preflight skill.
- `.claude-plugin/marketplace.json` — the marketplace manifest.

## Beta + telemetry

The plugin is in **public beta**. Take-offs run for free; in return the plugin
phones home with usage data so we know who's using it and how the matcher is
performing.

On first run `mto` writes `~/.nio/usage.json` (your device fingerprint plus
the email Claude Code already knows) and pings our Confluent Cloud event
stream. Every subsequent run sends a heartbeat keyed by device fingerprint
only — no email after registration.

What we collect:

- **Device usage**: registration once, then a heartbeat per run with the
  command, run count, take-off result counts, error codes, phase durations.
  Never file paths or IFC body content.
- **Material matching**: per take-off, the raw material names found in the
  IFC, what we matched them to in oekobaudat, and the confidence — this is
  the feedback loop that improves matching for everyone.

Opt out: `export NIO_NO_TELEMETRY=1`. The take-off still works.

## Licence

Proprietary. Commercial licence required for any use — see [LICENSE](LICENSE).
Read access to this repository is not a use licence.

Contact <hello@nio.energy> for a commercial licence.

ÖKOBAUDAT data is bundled under CC BY 4.0; the ICE database is bundled for
reference only and must not be used in commercial deliverables without a
separate licence from Circular Ecology.
See [plugin/skills/material-takeoff/databases/LICENSE.md](plugin/skills/material-takeoff/databases/LICENSE.md).

## Company

**blackmirror media GmbH** — Cobenzlgasse 79, 1190 Wien, Austria · FN 475645 d,
Handelsgericht Wien · VAT:
ATU72557958 · <https://blackmirror.at> · <https://www.linkedin.com/company/blackmirror-media>
