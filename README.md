# nio Material Take-Off

Claude Code plugin that turns an IFC building model into an Excel material
take-off with embodied carbon, matched against the ÖKOBAUDAT environmental
database. Powered by the Claude LLM for semantic material matching (
abbreviations, German↔English, structural intent).

## Install

### In Claude Code

```bash
npm install -g @anthropic-ai/claude-code   # if not installed yet
claude                                     # open a session in any terminal
```

Inside the session:

```
/plugin marketplace add blackmirror-media/nio-material-take-off-plugin
/plugin install material-takeoff@nio
```

### In Claude Cowork

Two ways:

1. **Add by URL** — in the Plugins UI, "Add plugin" → paste
   `https://github.com/blackmirror-media/nio-material-take-off-plugin`.
2. **Drag-and-drop** — download `material-takeoff.plugin` from the
   [latest release](https://github.com/blackmirror-media/nio-material-take-off-plugin/releases)
   and drop it onto the Cowork window.

After installing, open the plugin's "···" menu and turn on **Sync
automatically** so Cowork tracks new commits on the default branch.
Otherwise you'll be stuck on the version you first installed.

When a new commit lands, Cowork shows an **Update** button on the plugin's
settings card — click it to apply. Auto-sync notices the new version;
applying it still takes one click.

### On first run

The plugin downloads a platform-specific binary (~80 MB) from GitHub Releases.
**Supported: macOS (Apple Silicon + Intel) and Windows x64.** Linux is not a
supported target.

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

