#!/usr/bin/env python3
"""Fail-closed structural validation for the Singularity Observatory."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


REQUIRED_TOP_FILES = (
    "README.md",
    "AGENTS.md",
    "PROTOCOL.md",
    "CODEBOOK.md",
    "PANEL.md",
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "LICENSING.md",
    "CITATION.cff",
)

REQUIRED_DIRECTORIES = (
    "registry",
    "cases",
    "evidence",
    "data/waves",
    "schemas",
    "analysis",
    "scripts",
    "tests",
    "docs",
)

VERSIONED_TEXT_INSTRUMENTS = (
    "PROTOCOL.md",
    "CODEBOOK.md",
    "PANEL.md",
    "GOVERNANCE.md",
    "docs/SCHEDULE.md",
    "registry/README.md",
)

SCHEMA_FILES = (
    "schemas/evidence.schema.json",
    "schemas/observation.schema.json",
    "schemas/wave-manifest.schema.json",
)

REQUIRED_LOCKS = ("protocol", "panel", "schema", "schedule", "governance")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
VERSION_RE = re.compile(r"Instrument version:\s*`([^`]+)`")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_lock(name: str, lock: Any, location: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(lock, dict):
        return [f"{location}: lock '{name}' must be an object"]
    if not isinstance(lock.get("version"), str) or not lock["version"].strip():
        errors.append(f"{location}: lock '{name}' requires a non-empty version")
    digest = lock.get("sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        errors.append(f"{location}: lock '{name}' requires a lowercase SHA-256 digest")
    if not isinstance(lock.get("locked_at"), str) or not lock["locked_at"].strip():
        errors.append(f"{location}: lock '{name}' requires locked_at")
    return errors


def validate_wave_manifest(manifest: Any, location: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return [f"{location}: manifest must be an object"]

    required = (
        "wave_id",
        "status",
        "schema_version",
        "panel_snapshot",
        "registry_snapshot",
        "instrument_locks",
    )
    for field in required:
        if field not in manifest:
            errors.append(f"{location}: missing required field '{field}'")

    status = manifest.get("status")
    if status not in {"draft", "locked", "official"}:
        errors.append(f"{location}: status must be draft, locked, or official")

    panel_snapshot = manifest.get("panel_snapshot")
    registry_snapshot = manifest.get("registry_snapshot")
    if panel_snapshot and registry_snapshot and panel_snapshot == registry_snapshot:
        errors.append(f"{location}: Frozen Panel and Live Registry snapshots must be distinct")

    locks = manifest.get("instrument_locks")
    if not isinstance(locks, dict):
        errors.append(f"{location}: instrument_locks must be an object")
        locks = {}

    if status in {"locked", "official"}:
        if not isinstance(manifest.get("locked_at"), str) or not manifest["locked_at"].strip():
            errors.append(f"{location}: {status} Wave requires locked_at")
        for name in REQUIRED_LOCKS:
            if name not in locks:
                errors.append(f"{location}: {status} Wave is missing '{name}' lock")
            else:
                errors.extend(validate_lock(name, locks[name], location))

    if status == "official":
        if not isinstance(manifest.get("released_at"), str) or not manifest["released_at"].strip():
            errors.append(f"{location}: official Wave requires released_at")
        approval = manifest.get("release_approval")
        if not isinstance(approval, str) or not approval.strip():
            errors.append(f"{location}: official Wave requires release_approval")

    return errors


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def locked_wave_directories_at_base(root: Path, base_ref: str) -> set[PurePosixPath]:
    paths = git(root, "ls-tree", "-r", "--name-only", base_ref, "--", "data/waves")
    locked: set[PurePosixPath] = set()
    for raw_path in paths.splitlines():
        path = PurePosixPath(raw_path.strip())
        if path.name != "manifest.json":
            continue
        try:
            manifest = json.loads(git(root, "show", f"{base_ref}:{path.as_posix()}"))
        except (json.JSONDecodeError, subprocess.CalledProcessError):
            continue
        if isinstance(manifest, dict) and manifest.get("status") in {"locked", "official"}:
            locked.add(path.parent)
    return locked


def validate_append_only(root: Path, base_ref: str) -> list[str]:
    errors: list[str] = []
    try:
        locked_directories = locked_wave_directories_at_base(root, base_ref)
        changes = git(root, "diff", "--name-status", base_ref, "--", "data/waves")
    except subprocess.CalledProcessError as exc:
        return [f"cannot compare locked Waves with {base_ref}: {exc.stderr.strip()}"]

    for line in changes.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        affected = [PurePosixPath(value) for value in parts[1:]]
        for wave_dir in locked_directories:
            if any(path == wave_dir or wave_dir in path.parents for path in affected):
                if not status.startswith("A"):
                    errors.append(
                        f"locked Wave '{wave_dir}' is append-only; change '{line}' is not allowed"
                    )
                break
    return errors


def validate_repository(root: Path, base_ref: str | None = None) -> list[str]:
    errors: list[str] = []

    for relative in REQUIRED_TOP_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required top-level file: {relative}")
    for relative in REQUIRED_DIRECTORIES:
        if not (root / relative).is_dir():
            errors.append(f"missing required directory: {relative}/")

    for relative in VERSIONED_TEXT_INSTRUMENTS:
        path = root / relative
        if not path.is_file():
            continue
        if not VERSION_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"{relative}: missing explicit Instrument version")

    for relative in SCHEMA_FILES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing schema: {relative}")
            continue
        try:
            schema = read_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        version = schema.get("x-instrument-version") if isinstance(schema, dict) else None
        if not isinstance(version, str) or not version.strip():
            errors.append(f"{relative}: missing x-instrument-version")

    instrument_manifest_path = root / "schemas/instruments.json"
    if not instrument_manifest_path.is_file():
        errors.append("missing instrument manifest: schemas/instruments.json")
    else:
        try:
            instrument_manifest = read_json(instrument_manifest_path)
        except json.JSONDecodeError as exc:
            errors.append(f"schemas/instruments.json: invalid JSON: {exc}")
        else:
            instruments = instrument_manifest.get("instruments", [])
            if not isinstance(instruments, list) or not instruments:
                errors.append("schemas/instruments.json: instruments must be a non-empty list")
            else:
                names: set[str] = set()
                for index, instrument in enumerate(instruments):
                    location = f"schemas/instruments.json instruments[{index}]"
                    if not isinstance(instrument, dict):
                        errors.append(f"{location}: must be an object")
                        continue
                    name = instrument.get("name")
                    if not isinstance(name, str) or not name.strip():
                        errors.append(f"{location}: missing name")
                    elif name in names:
                        errors.append(f"{location}: duplicate name '{name}'")
                    else:
                        names.add(name)
                    path_value = instrument.get("path")
                    if not isinstance(path_value, str) or not (root / path_value).is_file():
                        errors.append(f"{location}: instrument path does not exist")
                    if not isinstance(instrument.get("version"), str) or not instrument["version"].strip():
                        errors.append(f"{location}: missing version")
                    if instrument.get("status") not in {"draft", "locked", "retired"}:
                        errors.append(f"{location}: invalid status")

    registry = root / "registry/live-registry.csv"
    if not registry.is_file():
        errors.append("missing Live Registry: registry/live-registry.csv")
    panel = root / "PANEL.md"
    if registry.resolve() == panel.resolve():
        errors.append("Frozen Panel and Live Registry must be distinct files")

    waves_root = root / "data/waves"
    if waves_root.is_dir():
        for manifest_path in sorted(waves_root.glob("*/manifest.json")):
            relative = manifest_path.relative_to(root).as_posix()
            try:
                manifest = read_json(manifest_path)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative}: invalid JSON: {exc}")
                continue
            errors.extend(validate_wave_manifest(manifest, relative))

    if base_ref:
        errors.extend(validate_append_only(root, base_ref))

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-ref",
        help="Git ref used to enforce append-only behavior for previously locked Waves",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = validate_repository(root, args.base_ref)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed: scaffold and Wave gates are structurally sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
