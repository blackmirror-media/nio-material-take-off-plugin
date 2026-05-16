# Material Take-Off — Claude Code plugin

Turn an IFC building model into an Excel material take-off with matched
environmental data (oekobaudat, ICE) and
embodied carbon.

## Install

```
/plugin marketplace add nio-energy/nio-material-take-off
/plugin install material-takeoff
```

## Use

```
/material-takeoff path/to/model.ifc
```

Optional second argument sets the output xlsx path.

## Layout

```
plugin/
├── .claude-plugin/plugin.json        # manifest
├── commands/material-takeoff.md      # /material-takeoff slash command
└── skills/material-takeoff/
    ├── SKILL.md                      # workflow (extract → match → build-model → xlsx)
    ├── bin/<platform>/mto            # IFC extractor (built from src/MaterialTakeOff/)
    ├── databases/                    # oekobaudat + ICE snapshots
    └── scripts/
        ├── prefilter.py              # top-N candidate filter for matching
        ├── models.py                 # pydantic models mirroring CompleteModel
        └── build-xlsx.py             # uv-launched renderer
```

Supported platforms: macOS arm64, macOS x64, Windows x64.

## Building the binary

```
./plugin/build-binaries.sh
```

Runs `dotnet publish` for all supported runtimes and drops the binaries into
`plugin/skills/material-takeoff/bin/<platform>/`.
