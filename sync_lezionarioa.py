#!/usr/bin/env python3
"""
Sync the Basque lectionary (Lezionarioa_CL.json) from the calendarioliturgico
skill into tools/lecturasdeldia/data/.

The authoritative builder is tools/pipeline/leccionario/build_lezionarioa.py;
the skill's data/ folder is its publishing point. We commit a copy here so
the GitHub Pages build is self-contained.

Guard: refuse to overwrite if the destination's meta.last_built is *newer*
than the source — that situation means a fix was applied locally and not yet
fed back into the skill, and overwriting would erase it.

Usage:
  python sync_lezionarioa.py            # do the sync
  python sync_lezionarioa.py --check    # report drift only, no copy
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent.parent / ".claude" / "skills" / "calendarioliturgico" / "data" / "Lezionarioa_CL.json"
DEST = ROOT / "data" / "Lezionarioa_CL.json"


def _meta(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("meta", {})


def main(check_only: bool = False) -> int:
    if not SOURCE.exists():
        print(f"ERROR: source missing: {SOURCE}", file=sys.stderr)
        return 1

    src_meta = _meta(SOURCE)
    dst_meta = _meta(DEST)

    src_built = src_meta.get("last_built", "")
    dst_built = dst_meta.get("last_built", "")
    src_cov = src_meta.get("coverage_pct_calendar_texto", "?")
    dst_cov = dst_meta.get("coverage_pct_calendar_texto", "?")

    print(f"source: {SOURCE}")
    print(f"  last_built={src_built}  coverage={src_cov}%")
    print(f"dest:   {DEST}")
    print(f"  last_built={dst_built}  coverage={dst_cov}%")

    if dst_built and src_built and dst_built < src_built:
        print(f"  -> source newer ({src_built} > {dst_built}), sync will refresh")
    elif dst_built and src_built and dst_built > src_built:
        print(f"  [BLOCKED] destination newer than source ({dst_built} > {src_built}).")
        print("    Refusing to overwrite -- check that local fixes are pushed back to the skill.")
        return 2
    elif dst_built == src_built:
        print("  -> identical last_built; nothing to do (still copies bytes)")

    if check_only:
        return 0

    shutil.copy2(SOURCE, DEST)
    print(f"copied {SOURCE.name} → {DEST}")
    return 0


if __name__ == "__main__":
    check = "--check" in sys.argv[1:]
    sys.exit(main(check_only=check))
