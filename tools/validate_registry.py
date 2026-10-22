#!/usr/bin/env python3
"""Validate the ESML library registry (coordinates, namespaces, digests, deps).

  python3 tools/validate_registry.py                 # read-only check
  python3 tools/validate_registry.py --write-digests # fill sha256 for local packages
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "registry" / "index.tsv"
NAMESPACES = ROOT / "registry" / "namespaces.tsv"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-(?:rc|beta)\.\d+)?$")
GROUP = re.compile(r"^[a-z0-9]+(?:\.[a-z0-9]+)+$")
ARTIFACT = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
COORD = re.compile(r"^([^:\s]+):([^:\s]+):([^:\s]+)$")
STATUS = {"stable", "experimental", "deprecated"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    rows = []
    for i, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != len(header):
            raise SystemExit(f"{path}:{i}: expected {len(header)} columns, got {len(cells)}")
        rows.append(dict(zip(header, cells)))
    return rows


def digest_package(path: Path) -> str:
    h = hashlib.sha256()
    files = sorted(p for p in path.rglob("*") if p.is_file() and ".git" not in p.parts)
    for f in files:
        rel = f.relative_to(path).as_posix()
        h.update(rel.encode("utf-8") + b"\0")
        h.update(f.read_bytes() + b"\0")
    return h.hexdigest()


def coord(row: dict) -> str:
    return f"{row['groupId']}:{row['artifactId']}:{row['version']}"


def parse_coord(text: str) -> tuple[str, str, str] | None:
    m = COORD.match(text)
    return (m.group(1), m.group(2), m.group(3)) if m else None


def validate(write_digests: bool) -> list[str]:
    errors: list[str] = []
    rows = read_tsv(INDEX)
    ns = read_tsv(NAMESPACES)

    seen_coords: dict[str, int] = {}
    for i, row in enumerate(rows, start=2):
        c = coord(row)
        if c in seen_coords:
            errors.append(f"index.tsv:{i}: duplicate coordinate {c}")
        seen_coords[c] = i
        if not GROUP.match(row["groupId"]):
            errors.append(f"index.tsv:{i}: bad groupId {row['groupId']}")
        if not ARTIFACT.match(row["artifactId"]):
            errors.append(f"index.tsv:{i}: bad artifactId {row['artifactId']}")
        if not SEMVER.match(row["version"]):
            errors.append(f"index.tsv:{i}: bad version {row['version']}")
        if row["status"] not in STATUS:
            errors.append(f"index.tsv:{i}: bad status {row['status']}")
        if row["status"] == "deprecated" and row["replacement"] == "-":
            errors.append(f"index.tsv:{i}: deprecated without replacement")

    assigned: dict[str, str] = {}
    for i, row in enumerate(ns, start=2):
        n = row["namespace"]
        if n in assigned:
            errors.append(f"namespaces.tsv:{i}: namespace {n} assigned twice")
        assigned[n] = row["artifactId"]

    for i, row in enumerate(rows, start=2):
        c = coord(row)
        n = row["namespace"]
        if assigned.get(n) != row["artifactId"]:
            errors.append(f"index.tsv:{i}: namespace {n} not assigned to {row['artifactId']}")

        if row["repository"] == "local":
            pkg = ROOT / row["path"]
            meta = pkg / "package.esml"
            if not meta.exists():
                errors.append(f"index.tsv:{i}: missing {meta.relative_to(ROOT)}")
                continue
            try:
                root = ET.parse(meta).getroot()
            except ET.ParseError as e:
                errors.append(f"{meta.relative_to(ROOT)}: XML error {e}")
                continue
            for key in ("groupId", "artifactId", "version"):
                if root.get(key) != row[key]:
                    errors.append(f"{meta.relative_to(ROOT)}: {key} mismatch")
            if root.findtext("namespace") != n:
                errors.append(f"{meta.relative_to(ROOT)}: namespace mismatch")
            for exp in root.findall("./exports/export"):
                ep = pkg / exp.get("path", "")
                if not ep.exists():
                    errors.append(f"{meta.relative_to(ROOT)}: export missing {exp.get('path')}")
                else:
                    try:
                        ET.parse(ep)
                    except ET.ParseError as e:
                        errors.append(f"{ep.relative_to(ROOT)}: XML error {e}")
            digest = digest_package(pkg)
            if write_digests:
                row["sha256"] = digest
            elif row["sha256"] != digest:
                errors.append(f"index.tsv:{i}: digest mismatch for {c}")
        else:
            if row["commit"] == "-" or not re.fullmatch(r"[0-9a-f]{7,40}", row["commit"]):
                errors.append(f"index.tsv:{i}: community package needs a commit")
            if not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
                errors.append(f"index.tsv:{i}: community package needs sha256")

    # Dependencies must exist and must not form a cycle.
    edges: dict[str, list[str]] = {}
    known = set(seen_coords)
    for i, row in enumerate(rows, start=2):
        deps = [] if row["dependencies"] == "-" else row["dependencies"].split(",")
        edges[coord(row)] = deps
        for d in deps:
            if parse_coord(d) is None:
                errors.append(f"index.tsv:{i}: bad dependency {d}")
            elif d not in known:
                errors.append(f"index.tsv:{i}: missing dependency {d}")

    state: dict[str, int] = {}
    def visit(c: str, stack: list[str]) -> None:
        if state.get(c) == 1:
            errors.append("dependency cycle: " + " -> ".join(stack + [c]))
            return
        if state.get(c) == 2:
            return
        state[c] = 1
        for d in edges.get(c, []):
            if d in edges:
                visit(d, stack + [c])
        state[c] = 2
    for c in edges:
        visit(c, [])

    if write_digests:
        header = list(rows[0].keys())
        lines = ["\t".join(header)] + ["\t".join(r[k] for k in header) for r in rows]
        INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-digests", action="store_true")
    args = ap.parse_args()
    errors = validate(args.write_digests)
    if errors:
        for e in errors:
            print("FAIL", e)
        print(f"{len(errors)} error(s)")
        return 1
    rows = read_tsv(INDEX)
    print(f"PASS: {len(rows)} coordinates, {len(read_tsv(NAMESPACES))} namespaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
