#!/usr/bin/env python3
"""
Prefilter a material database for candidates matching a given IFC material name.

Usage:
    prefilter.py <database.json> <material-name>
        [--db oekobaudat|ICE]
        [--element-types IfcBeam,IfcColumn]
        [--top N]

Pipeline:
  1. If --element-types is given and the database key exists in
     element_categories.json, filter entries to those whose primary
     category starts with one of the allowed prefixes for any of the
     given element types. Cuts ~1800 candidates to ~50-200 immediately.
  2. Score the remaining entries by token-overlap on a haystack of all
     string/number fields.
  3. Return top-N sorted by score.

Token-overlap is deliberately dumb. The matching judgement (DE↔EN,
abbreviations like "stb."→"Stahlbeton"→"reinforced concrete") is the
LLM's job — this script only needs to surface the right candidates.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_SCRIPT_DIR = Path(__file__).resolve().parent

# Per-DB: which field on each entry is the primary category used for
# element-type gating.
_CATEGORY_FIELD = {
    "oekobaudat": "Category",
    "ICE": "Material",
}


def tokenize(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def score(query_tokens: set[str], entry: dict) -> float:
    haystack = " ".join(
        str(v) for v in entry.values() if isinstance(v, (str, int, float))
    )
    entry_tokens = tokenize(haystack)
    if not entry_tokens or not query_tokens:
        return 0.0
    overlap = len(query_tokens & entry_tokens)
    return overlap / (len(query_tokens) ** 0.5 * len(entry_tokens) ** 0.5)


def load_entries(database_path: Path) -> list[dict]:
    data = json.loads(database_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw = data
    else:
        raw = data.get("materials") or data.get("entries") or []
    return [e for e in raw if isinstance(e, dict)]


def allowed_prefixes(element_types: Iterable[str], db: str) -> list[str] | None:
    """Union of category prefixes for the given element types.
    None = no gating (no rule found for any of the requested types)."""
    path = _SCRIPT_DIR / "element_categories.json"
    if not path.exists():
        return None
    table = json.loads(path.read_text(encoding="utf-8"))
    prefixes: list[str] = []
    for t in element_types:
        per_db = table.get(t, {})
        prefixes.extend(per_db.get(db, []))
    # Dedupe, preserve order
    return list(dict.fromkeys(prefixes)) or None


def gate_by_element_type(
    entries: list[dict], db: str, prefixes: list[str]
) -> list[dict]:
    field = _CATEGORY_FIELD.get(db)
    if not field:
        return entries
    lowered = [p.lower() for p in prefixes]

    def keep(entry: dict) -> bool:
        value = entry.get(field)
        if not isinstance(value, str):
            return False
        v = value.lower()
        return any(v.startswith(p) for p in lowered)

    return [e for e in entries if keep(e)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument("material_name")
    parser.add_argument(
        "--db",
        choices=sorted(_CATEGORY_FIELD.keys()),
        help="Database identifier — required when --element-types is given.",
    )
    parser.add_argument(
        "--element-types",
        help="Comma-separated IFC element types this material appears on, "
        "e.g. 'IfcBeam,IfcColumn'. Used to gate candidate categories.",
    )
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    entries = load_entries(args.database)
    gated_count = len(entries)

    if args.element_types:
        if not args.db:
            print(
                "--element-types requires --db <oekobaudat|ICE>",
                file=sys.stderr,
            )
            return 2
        element_types = [t.strip() for t in args.element_types.split(",") if t.strip()]
        prefixes = allowed_prefixes(element_types, args.db)
        if prefixes:
            entries = gate_by_element_type(entries, args.db, prefixes)
            print(
                f"gated {gated_count}→{len(entries)} candidates by "
                f"element types {element_types}",
                file=sys.stderr,
            )

    query = tokenize(args.material_name)
    scored = [{**e, "score": round(score(query, e), 4)} for e in entries]
    scored.sort(key=lambda e: e["score"], reverse=True)
    json.dump(scored[: args.top], sys.stdout, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
