#!/usr/bin/env python3
"""Resolve ESML library coordinates to a dependency closure.

  python3 tools/resolve.py cn.ai4energy.esml:esml-thermal:0.1.0
  python3 tools/resolve.py --bom bom/esml-bom-0.1.0.esml
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_index() -> dict[str, dict[str, str]]:
    lines = (ROOT / "registry" / "index.tsv").read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    out = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        row = dict(zip(header, line.split("\t")))
        out[f"{row['groupId']}:{row['artifactId']}:{row['version']}"] = row
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("coordinates", nargs="*")
    ap.add_argument("--bom")
    args = ap.parse_args()

    roots = list(args.coordinates)
    if args.bom:
        for p in ET.parse(args.bom).getroot().findall("./packages/package"):
            roots.append(p.get("coordinate", ""))
    if not roots:
        ap.error("give coordinates or --bom")

    index = read_index()
    order: list[str] = []
    seen: set[str] = set()
    q = deque(roots)
    while q:
        c = q.popleft()
        if c in seen:
            continue
        if c not in index:
            print(f"FAIL missing coordinate {c}")
            return 1
        seen.add(c)
        order.append(c)
        deps = index[c]["dependencies"]
        if deps != "-":
            q.extend(deps.split(","))

    by_artifact: dict[tuple[str, str], str] = {}
    for c in order:
        row = index[c]
        key = (row["groupId"], row["artifactId"])
        if key in by_artifact and by_artifact[key] != c:
            print(f"FAIL conflict: {key[0]}:{key[1]} -> {by_artifact[key]} vs {c}")
            return 1
        by_artifact[key] = c

    for c in sorted(order):
        row = index[c]
        loc = row["path"] if row["repository"] == "local" else f"{row['repository']}@{row['commit']}"
        print(f"{c}\t{row['namespace']}\t{loc}")
    print(f"{len(order)} package(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
