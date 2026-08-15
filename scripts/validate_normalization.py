#!/usr/bin/env python3
"""Fail-closed validation for prospective Domain normalization artifacts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable


PASS1_SCHEMA_PATH = "schemas/domain-normalization-pass1.schema.json"
PASS1_DIRECTORY = "domain-universe/normalization/pass1"
CODEBOOK_PATH = "domain-universe/NORMALIZATION_CODEBOOK.md"
BOUNDARY_PATH = "domain-universe/boundaries/du-boundary-v0.1.json"
EXPECTED_PASS1: dict[str, tuple[str, str, int]] = {
    "oecd-ford-frascati-2015-pass1.json": (
        "domain-universe/extractions/oecd-ford-frascati-2015-second-level.json",
        "oecd-ford-frascati-2015",
        42,
    ),
    "un-isic-rev5-pass1.json": (
        "domain-universe/extractions/un-isic-rev5-division.json",
        "un-isic-rev5",
        87,
    ),
    "wipo-ipc-2026-01-pass1.json": (
        "domain-universe/extractions/wipo-ipc-2026-01-class.json",
        "wipo-ipc-2026-01",
        132,
    ),
    "un-cofog-1999-pass1.json": (
        "domain-universe/extractions/un-cofog-1999-group.json",
        "un-cofog-1999",
        69,
    ),
}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_lf_sha256(path: Path) -> str:
    """Hash canonical LF repository bytes independent of checkout conversion."""

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate_artifact(
    root: Path,
    reference: Any,
    expected_path: str,
    location: str,
) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    if not isinstance(reference, dict):
        return None, [f"{location}: artifact reference must be an object"]
    if reference.get("path") != expected_path:
        errors.append(f"{location}: path must equal {expected_path}")
    path = root / expected_path
    if not path.is_file():
        errors.append(f"{location}: referenced artifact does not exist: {expected_path}")
        return None, errors
    actual = canonical_lf_sha256(path)
    if reference.get("sha256") != actual:
        errors.append(f"{location}: SHA-256 mismatch for {expected_path}")
    return path, errors


def validate_normalization_repository(
    root: Path,
    validate_contract: Callable[[Any, Any, str], list[str]],
) -> list[str]:
    """Validate Pass 1 records without adding them to Domain lock schemas."""

    errors: list[str] = []
    directory = root / PASS1_DIRECTORY
    records = sorted(directory.glob("*.json")) if directory.is_dir() else []
    if not records:
        return errors

    expected_names = set(EXPECTED_PASS1)
    actual_names = {path.name for path in records}
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        errors.append(
            f"{PASS1_DIRECTORY}: expected exactly four Pass 1 files; "
            f"missing={missing}, extra={extra}"
        )

    schema_path = root / PASS1_SCHEMA_PATH
    if not schema_path.is_file():
        return errors + [f"{PASS1_SCHEMA_PATH}: required when Pass 1 records exist"]
    try:
        schema = read_json(schema_path)
    except json.JSONDecodeError as exc:
        return errors + [f"{PASS1_SCHEMA_PATH}: invalid JSON: {exc}"]

    bound_extractions: set[str] = set()
    total_interpretations = 0
    for path in records:
        location = path.relative_to(root).as_posix()
        expected = EXPECTED_PASS1.get(path.name)
        if expected is None:
            continue
        extraction_relative, source_frame_id, expected_count = expected
        try:
            record = read_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{location}: invalid JSON: {exc}")
            continue
        errors.extend(validate_contract(record, schema, location))
        if not isinstance(record, dict):
            continue

        if record.get("pass1_record_id") != path.stem:
            errors.append(f"{location}: pass1_record_id must match filename stem")
        if record.get("instrument_version") != "0.5.0-draft":
            errors.append(f"{location}: instrument_version mismatch")
        if record.get("procedure") != "independent_entry_interpretation":
            errors.append(f"{location}: procedure mismatch")
        if record.get("status") != "complete":
            errors.append(f"{location}: status must be complete")

        _, artifact_errors = validate_artifact(
            root,
            record.get("normalization_codebook"),
            CODEBOOK_PATH,
            f"{location}: normalization_codebook",
        )
        errors.extend(artifact_errors)
        _, artifact_errors = validate_artifact(
            root,
            record.get("universe_boundary"),
            BOUNDARY_PATH,
            f"{location}: universe_boundary",
        )
        errors.extend(artifact_errors)
        extraction_path, artifact_errors = validate_artifact(
            root,
            record.get("source_extraction"),
            extraction_relative,
            f"{location}: source_extraction",
        )
        errors.extend(artifact_errors)
        if extraction_relative in bound_extractions:
            errors.append(f"{location}: duplicate Pass 1 record for {extraction_relative}")
        bound_extractions.add(extraction_relative)
        if extraction_path is None:
            continue

        try:
            extraction = read_json(extraction_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{location}: bound extraction is invalid JSON: {exc}")
            continue
        extracted_entries = extraction.get("extracted_entries", [])
        extraction_by_id = {
            entry.get("source_entry_id"): entry
            for entry in extracted_entries
            if isinstance(entry, dict) and isinstance(entry.get("source_entry_id"), str)
        }
        interpretations = record.get("interpretations", [])
        if not isinstance(interpretations, list):
            continue
        total_interpretations += len(interpretations)
        if len(interpretations) != expected_count:
            errors.append(
                f"{location}: expected {expected_count} interpretations, "
                f"found {len(interpretations)}"
            )
        interpretation_ids = [
            item.get("source_entry_id")
            for item in interpretations
            if isinstance(item, dict)
        ]
        if len(interpretation_ids) != len(set(interpretation_ids)):
            errors.append(f"{location}: duplicate Pass 1 interpretation")
        if set(interpretation_ids) != set(extraction_by_id):
            missing = sorted(set(extraction_by_id) - set(interpretation_ids))
            extra = sorted(set(interpretation_ids) - set(extraction_by_id))
            errors.append(
                f"{location}: interpretation IDs must exactly match extraction; "
                f"missing={missing}, extra={extra}"
            )

        clarification_sources = record.get("clarification_sources", [])
        clarification_by_id: dict[str, dict[str, Any]] = {}
        if isinstance(clarification_sources, list):
            for source in clarification_sources:
                if not isinstance(source, dict):
                    continue
                clarification_id = source.get("clarification_source_id")
                if isinstance(clarification_id, str):
                    if clarification_id in clarification_by_id:
                        errors.append(f"{location}: duplicate clarification_source_id")
                    clarification_by_id[clarification_id] = source
                if source.get("source_frame_id") != source_frame_id:
                    errors.append(
                        f"{location}: clarification source belongs to a different source frame"
                    )

        for index, interpretation in enumerate(interpretations):
            item_location = f"{location}: interpretations[{index}]"
            if not isinstance(interpretation, dict):
                continue
            source_entry_id = interpretation.get("source_entry_id")
            extracted = extraction_by_id.get(source_entry_id)
            if extracted is None:
                continue
            if interpretation.get("source_entry_reference") != extracted.get(
                "source_entry_reference"
            ):
                errors.append(f"{item_location}: source_entry_reference mismatch")
            if interpretation.get("source_entry_descriptor") != extracted.get(
                "source_entry_descriptor"
            ):
                errors.append(f"{item_location}: source_entry_descriptor mismatch")
            if (
                interpretation.get("minimal_gate_result") == "passes"
                and not str(interpretation.get("normalized_substantive_locus") or "").strip()
            ):
                errors.append(f"{item_location}: passes requires a substantive locus")
            stripping = interpretation.get("frame_role_stripping")
            if (
                isinstance(stripping, dict)
                and stripping.get("action") == "unresolved"
                and interpretation.get("minimal_gate_result") != "unresolved"
            ):
                errors.append(
                    f"{item_location}: unresolved frame-role stripping requires unresolved gate"
                )
            clarification_ids = interpretation.get("clarification_source_ids", [])
            if not isinstance(clarification_ids, list):
                continue
            if interpretation.get("evidence_basis") == "title_and_parent_only" and clarification_ids:
                errors.append(
                    f"{item_location}: title_and_parent_only forbids clarification sources"
                )
            if (
                interpretation.get("evidence_basis")
                == "official_same_classification_clarification"
                and not clarification_ids
            ):
                errors.append(
                    f"{item_location}: official clarification requires a source ID"
                )
            for clarification_id in clarification_ids:
                if clarification_id not in clarification_by_id:
                    errors.append(
                        f"{item_location}: unresolved clarification_source_id "
                        f"{clarification_id!r}"
                    )

    expected_extractions = {value[0] for value in EXPECTED_PASS1.values()}
    if bound_extractions != expected_extractions:
        errors.append(f"{PASS1_DIRECTORY}: Pass 1 must bind each extraction exactly once")
    if total_interpretations != 330:
        errors.append(
            f"{PASS1_DIRECTORY}: expected 330 interpretations across all records, "
            f"found {total_interpretations}"
        )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    validator_path = root / "scripts/validate.py"
    spec = importlib.util.spec_from_file_location("observatory_validate", validator_path)
    if spec is None or spec.loader is None:
        print("Validation failed: cannot load scripts/validate.py")
        return 1
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors = validate_normalization_repository(root, module.validate_contract)
    if errors:
        print("Normalization validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Normalization validation passed: Pass 1 contracts are sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
