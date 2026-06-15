#!/usr/bin/env python3
"""Validate a protoAgent bundle manifest (ADR 0040/0049) — structure + pin sanity, no host.

Checks:
  • the manifest parses; `id` / `name` / `description` are present
  • each member is `builtin: true` OR has `id` + `url` + `ref`
  • every member line is ON ONE LINE in the inline `- { ... }` form (so the pin-bump
    rewriter can find it) — the count of inline member lines must equal len(plugins)
  • `enabled` ⊆ the member ids
  • `archetype` (if present) has label / icon / blurb
  • every tag-pinned member's tag actually EXISTS at its repo (git ls-remote; a network
    error is a soft warning, a genuinely-missing tag is a hard failure)

Usage:  python3 scripts/validate_bundle.py [protoagent.bundle.yaml] [--no-net]
Exit 0 if valid, 1 otherwise.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

_MEMBER_LINE = re.compile(
    r"^\s*-\s*\{\s*id:\s*[\w-]+\s*,\s*(?:builtin:\s*true|url:\s*\S+?\s*,\s*ref:\s*\S+?)\s*\}\s*$"
)
_SEMVER_TAG = re.compile(r"^v?\d+\.\d+\.\d+$")


def _tag_exists(url: str, tag: str) -> bool | None:
    try:
        out = subprocess.run(
            ["git", "ls-remote", "--tags", url, tag],
            check=True, capture_output=True, text=True, timeout=30,
        ).stdout
        return bool(out.strip())
    except (subprocess.SubprocessError, OSError):
        return None  # network/tooling error → soft (can't prove either way)


def main(path_str: str, net: bool = True) -> int:
    path = Path(path_str)
    errs: list[str] = []
    warns: list[str] = []
    text = path.read_text(encoding="utf-8")
    m = yaml.safe_load(text)

    for field in ("id", "name", "description"):
        if not (isinstance(m, dict) and str(m.get(field, "")).strip()):
            errs.append(f"missing/empty `{field}`")

    plugins = m.get("plugins") if isinstance(m, dict) else None
    member_ids: list[str] = []
    if not isinstance(plugins, list) or not plugins:
        errs.append("`plugins` must be a non-empty list")
        plugins = []
    for p in plugins:
        if not isinstance(p, dict) or not p.get("id"):
            errs.append(f"member missing id: {p!r}")
            continue
        member_ids.append(p["id"])
        if not p.get("builtin") and not (p.get("url") and p.get("ref")):
            errs.append(f"member {p['id']}: needs `builtin: true` or both `url` + `ref`")

    # every member must be on one line (the pin-bump rewriter is line-based)
    inline = sum(1 for ln in text.splitlines() if _MEMBER_LINE.match(ln))
    if inline != len(plugins):
        errs.append(f"{len(plugins)} members but {inline} inline `- {{ ... }}` lines — keep each member on ONE line")

    enabled = m.get("enabled", []) if isinstance(m, dict) else []
    for e in enabled:
        if e not in member_ids:
            errs.append(f"`enabled` lists {e!r}, which is not a member")

    arch = m.get("archetype") if isinstance(m, dict) else None
    if arch is not None:
        for field in ("label", "icon", "blurb"):
            if not str(arch.get(field, "")).strip():
                errs.append(f"archetype missing `{field}`")

    if net:
        for p in plugins:
            ref = str(p.get("ref", ""))
            if p.get("url") and _SEMVER_TAG.match(ref):
                ok = _tag_exists(p["url"], ref)
                if ok is False:
                    errs.append(f"member {p['id']}: tag {ref} not found at {p['url']}")
                elif ok is None:
                    warns.append(f"member {p['id']}: could not reach {p['url']} to confirm {ref}")

    for w in warns:
        print(f"warn: {w}")
    if errs:
        for e in errs:
            print(f"FAIL: {e}")
        return 1
    label = (arch or {}).get("label", m.get("name"))
    print(f"OK: {m.get('id')} — {len(member_ids)} members ({', '.join(member_ids)}), archetype {label!r}.")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    no_net = "--no-net" in sys.argv
    sys.exit(main(args[0] if args else "protoagent.bundle.yaml", net=not no_net))
