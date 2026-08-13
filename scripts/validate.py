#!/usr/bin/env python3
"""Fail-closed integrity validation for the Singularity Observatory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse


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
    "data/amendments",
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
    "schemas/registry-unit.schema.json",
    "schemas/panel-snapshot.schema.json",
    "schemas/evidence.schema.json",
    "schemas/observation.schema.json",
    "schemas/wave-manifest.schema.json",
)

REQUIRED_INSTRUMENT_LOCKS = (
    "protocol",
    "codebook",
    "panel",
    "schedule",
    "governance",
    "registry",
)
INSTRUMENT_TITLES = {
    "protocol": "Observation Protocol",
    "codebook": "Observation Codebook",
    "panel": "Frozen Panel Specification",
    "schedule": "Observation Schedule",
    "governance": "Research Governance Framework",
    "registry": "Live Registry Specification",
}
REQUIRED_SCHEMA_LOCKS = (
    "registry_unit",
    "panel_snapshot",
    "evidence",
    "observation",
    "wave_manifest",
)
CURRENT_SCHEMA_PATHS = {
    "registry_unit": "schemas/registry-unit.schema.json",
    "panel_snapshot": "schemas/panel-snapshot.schema.json",
    "evidence": "schemas/evidence.schema.json",
    "observation": "schemas/observation.schema.json",
    "wave_manifest": "schemas/wave-manifest.schema.json",
}

LONGITUDINAL_EVENTS = {
    "transition_toward_human_noncriticality",
    "reversal_toward_human_criticality",
    "human_reentry",
    "no_supported_change",
}

REGISTRY_HEADER = (
    "registry_unit_id",
    "improvement_loop_id",
    "function_id",
    "human_bottleneck_label",
    "status",
    "added_on",
    "provenance_uri",
    "empirical_system_ids",
    "notes",
)

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
VERSION_RE = re.compile(r"Instrument version:\s*`([^`]+)`")
SCHEMA_BUNDLE_VERSION_RE = re.compile(r"Schema bundle version:\s*`([^`]+)`")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _type_matches(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "null":
        return instance is None
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    return False


def _resolve_local_ref(root_schema: dict[str, Any], reference: str) -> Any:
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported schema reference: {reference}")
    current: Any = root_schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[token]
    return current


def _format_matches(value: str, format_name: str) -> bool:
    try:
        if format_name == "date":
            date.fromisoformat(value)
            return True
        if format_name == "date-time":
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return "T" in value and parsed.tzinfo is not None
        if format_name == "uri":
            parsed = urlparse(value)
            return bool(parsed.scheme and (parsed.netloc or parsed.scheme == "urn"))
    except ValueError:
        return False
    return True


def validate_contract(
    instance: Any,
    schema: Any,
    location: str = "$",
    root_schema: dict[str, Any] | None = None,
) -> list[str]:
    """Validate the dependency-free JSON Schema subset used by this repository."""

    if not isinstance(schema, dict):
        return [] if schema is True else [f"{location}: schema rejected value"]
    if root_schema is None:
        root_schema = schema
    if "$ref" in schema:
        try:
            target = _resolve_local_ref(root_schema, schema["$ref"])
        except (KeyError, TypeError, ValueError) as exc:
            return [f"{location}: invalid schema reference: {exc}"]
        return validate_contract(instance, target, location, root_schema)

    errors: list[str] = []
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            errors.extend(validate_contract(instance, subschema, location, root_schema))
    if "anyOf" in schema and not any(
        not validate_contract(instance, subschema, location, root_schema)
        for subschema in schema["anyOf"]
    ):
        errors.append(f"{location}: value does not satisfy any allowed schema")
    if "not" in schema and not validate_contract(instance, schema["not"], location, root_schema):
        errors.append(f"{location}: value matches a prohibited schema")
    if "if" in schema and not validate_contract(instance, schema["if"], location, root_schema):
        errors.extend(validate_contract(instance, schema.get("then", {}), location, root_schema))

    expected_type = schema.get("type")
    if expected_type is not None:
        allowed_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_type_matches(instance, item) for item in allowed_types):
            errors.append(f"{location}: expected type {allowed_types}, got {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{location}: value must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{location}: value is not in the allowed enum")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for field in required:
            if field not in instance:
                errors.append(f"{location}: missing required field '{field}'")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for field in instance:
                if field not in properties:
                    errors.append(f"{location}: unexpected field '{field}'")
        for field, field_schema in properties.items():
            if field in instance:
                errors.extend(
                    validate_contract(instance[field], field_schema, f"{location}.{field}", root_schema)
                )

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{location}: array has fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{location}: array has more than {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in instance]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{location}: array items must be unique")
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(instance):
                errors.extend(
                    validate_contract(item, item_schema, f"{location}[{index}]", root_schema)
                )

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{location}: string is shorter than {schema['minLength']}")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, instance) is None:
            errors.append(f"{location}: string does not match required pattern")
        format_name = schema.get("format")
        if format_name and not _format_matches(instance, format_name):
            errors.append(f"{location}: invalid {format_name}")

    return errors


def resolve_artifact(root: Path, relative: Any, location: str) -> tuple[Path | None, list[str]]:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        return None, [f"{location}: artifact path must be a non-empty POSIX path"]
    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts:
        return None, [f"{location}: artifact path escapes the repository"]
    root_resolved = root.resolve()
    candidate = root.joinpath(*posix.parts).resolve()
    if candidate != root_resolved and root_resolved not in candidate.parents:
        return None, [f"{location}: artifact path escapes the repository"]
    if not candidate.is_file():
        return None, [f"{location}: artifact does not resolve: {relative}"]
    return candidate, []


def validate_artifact_ref(
    root: Path, reference: Any, location: str
) -> tuple[Path | None, list[str]]:
    if not isinstance(reference, dict):
        return None, [f"{location}: artifact reference must be an object"]
    errors: list[str] = []
    digest = reference.get("sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        errors.append(f"{location}: artifact requires a lowercase SHA-256 digest")
    path, path_errors = resolve_artifact(root, reference.get("path"), location)
    errors.extend(path_errors)
    if path is not None and isinstance(digest, str) and SHA256_RE.fullmatch(digest):
        actual = sha256_file(path)
        if actual != digest:
            errors.append(
                f"{location}: SHA-256 mismatch for {reference['path']}; expected {digest}, got {actual}"
            )
    return path, errors


def declared_version(path: Path) -> str | None:
    if path.name == "instruments.json":
        value = read_json(path)
        version = value.get("manifest_version") if isinstance(value, dict) else None
        return version if isinstance(version, str) else None
    if path.name.endswith(".schema.json"):
        value = read_json(path)
        version = value.get("x-instrument-version") if isinstance(value, dict) else None
        return version if isinstance(version, str) else None
    text = path.read_text(encoding="utf-8")
    matcher = SCHEMA_BUNDLE_VERSION_RE if path.as_posix().endswith("schemas/README.md") else VERSION_RE
    match = matcher.search(text)
    return match.group(1) if match else None


def load_instruments(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    path = root / "schemas/instruments.json"
    if not path.is_file():
        return {}, ["missing instrument manifest: schemas/instruments.json"]
    try:
        manifest = read_json(path)
    except json.JSONDecodeError as exc:
        return {}, [f"schemas/instruments.json: invalid JSON: {exc}"]

    errors: list[str] = []
    instruments: dict[str, dict[str, Any]] = {}
    entries = manifest.get("instruments", []) if isinstance(manifest, dict) else []
    if not isinstance(entries, list) or not entries:
        return {}, ["schemas/instruments.json: instruments must be a non-empty list"]

    for index, entry in enumerate(entries):
        location = f"schemas/instruments.json instruments[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{location}: must be an object")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"{location}: missing name")
            continue
        if name in instruments:
            errors.append(f"{location}: duplicate name '{name}'")
            continue
        instruments[name] = entry
        relative = entry.get("path")
        instrument_path, path_errors = resolve_artifact(root, relative, location)
        errors.extend(path_errors)
        version = entry.get("version")
        if not isinstance(version, str) or not version:
            errors.append(f"{location}: missing version")
        if entry.get("status") not in {"draft", "locked", "retired"}:
            errors.append(f"{location}: invalid status")
        if instrument_path is not None:
            try:
                actual_version = declared_version(instrument_path)
            except (json.JSONDecodeError, OSError) as exc:
                errors.append(f"{location}: cannot read declared version: {exc}")
            else:
                if actual_version != version:
                    errors.append(
                        f"{location}: manifest version {version!r} does not match "
                        f"declared version {actual_version!r} in {relative}"
                    )

    schema_bundle = instruments.get("schema_bundle", {}).get("version")
    for relative in SCHEMA_FILES:
        schema_path = root / relative
        if not schema_path.is_file():
            errors.append(f"missing schema: {relative}")
            continue
        try:
            schema = read_json(schema_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        version = schema.get("x-instrument-version") if isinstance(schema, dict) else None
        if version != schema_bundle:
            errors.append(
                f"{relative}: schema version {version!r} does not match bundle {schema_bundle!r}"
            )

    return instruments, errors


def validate_wave_lock(
    root: Path,
    name: str,
    lock: Any,
    location: str,
    wave_directory: PurePosixPath,
    expected_instrument: str | None = None,
) -> tuple[Path | None, str | None, list[str]]:
    """Resolve one immutable, Wave-local instrument or schema snapshot."""

    errors: list[str] = []
    lock_location = f"{location}: lock '{name}'"
    if not isinstance(lock, dict):
        return None, None, [f"{lock_location} must be an object"]
    version = lock.get("version")
    if not isinstance(version, str) or not version:
        errors.append(f"{lock_location} requires a version")
        version = None
    locked_at = lock.get("locked_at")
    if not isinstance(locked_at, str) or not _format_matches(locked_at, "date-time"):
        errors.append(f"{lock_location} requires a valid locked_at date-time")
    artifacts = lock.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        errors.append(f"{lock_location} requires exactly one snapshot artifact")
        return None, version, errors

    artifact = artifacts[0]
    artifact_location = f"{lock_location} artifact[0]"
    relative = artifact.get("path") if isinstance(artifact, dict) else None
    if isinstance(relative, str) and not _is_within(relative, wave_directory):
        errors.append(f"{artifact_location} must be inside its immutable Wave directory")
    path, artifact_errors = validate_artifact_ref(root, artifact, artifact_location)
    errors.extend(artifact_errors)
    if path is not None:
        try:
            artifact_version = declared_version(path)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"{artifact_location}: cannot read declared version: {exc}")
        else:
            if artifact_version != version:
                errors.append(
                    f"{artifact_location}: declared version {artifact_version!r} "
                    f"does not match lock version {version!r}"
                )
        if expected_instrument is not None and not path.name.endswith(".schema.json"):
            text = path.read_text(encoding="utf-8")
            if f"Instrument: {expected_instrument}" not in text:
                errors.append(
                    f"{artifact_location}: snapshot identity does not match {expected_instrument!r}"
                )
    return path, version, errors


def validate_registry_csv(path: Path, schema: dict[str, Any], location: str) -> list[str]:
    errors: list[str] = []
    required_fields = schema.get("required")
    expected_header = (
        tuple(required_fields)
        if isinstance(required_fields, list) and all(isinstance(item, str) for item in required_fields)
        else ()
    )
    if not expected_header:
        return [f"{location}: locked registry schema has no ordered required fields"]
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != expected_header:
            return [f"{location}: Live Registry header does not match the versioned ontology"]
        for line_number, row in enumerate(reader, start=2):
            record: dict[str, Any] = dict(row)
            systems = record.get("empirical_system_ids", "")
            record["empirical_system_ids"] = (
                [item for item in systems.split(";") if item] if isinstance(systems, str) else []
            )
            errors.extend(validate_contract(record, schema, f"{location}:{line_number}"))
    return errors


def _is_within(relative: str, directory: PurePosixPath) -> bool:
    path = PurePosixPath(relative)
    return path == directory or directory in path.parents


def validate_scientific_records(
    root: Path,
    manifest: dict[str, Any],
    location: str,
    wave_directory: PurePosixPath,
    panel_units: dict[str, set[str]],
    schemas: dict[str, dict[str, Any]],
    instrument_versions: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    records = manifest.get("scientific_records", {})
    if not isinstance(records, dict):
        return [f"{location}: scientific_records must be an object"]

    evidence_schema = schemas.get("evidence")
    observation_schema = schemas.get("observation")
    if not isinstance(evidence_schema, dict) or not isinstance(observation_schema, dict):
        return [f"{location}: locked evidence and observation schemas are required"]
    evidence_by_id: dict[str, dict[str, Any]] = {}
    observation_records: list[tuple[dict[str, Any], str]] = []
    covered_units: set[str] = set()

    for kind, schema in (("evidence", evidence_schema), ("observations", observation_schema)):
        references = records.get(kind, [])
        if not isinstance(references, list):
            errors.append(f"{location}: scientific_records.{kind} must be an array")
            continue
        for index, reference in enumerate(references):
            record_location = f"{location}: scientific_records.{kind}[{index}]"
            relative = reference.get("path") if isinstance(reference, dict) else None
            if isinstance(relative, str) and not _is_within(relative, wave_directory):
                errors.append(f"{record_location}: official record must be inside its Wave directory")
            path, artifact_errors = validate_artifact_ref(root, reference, record_location)
            errors.extend(artifact_errors)
            if path is None:
                continue
            try:
                record = read_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{record_location}: invalid JSON: {exc}")
                continue
            contract_name = "evidence" if kind == "evidence" else "observation"
            record_errors = validate_contract(
                record, schema, f"{record_location} {contract_name}"
            )
            errors.extend(record_errors)
            if not isinstance(record, dict):
                continue

            panel_unit_id = record.get("panel_unit_id")
            systems = record.get("empirical_system_ids")
            if panel_unit_id not in panel_units:
                message = f"{record_location}: panel_unit_id is absent from the Frozen Panel"
                errors.append(message)
                record_errors.append(message)
            elif isinstance(systems, list) and not set(systems).issubset(panel_units[panel_unit_id]):
                message = f"{record_location}: empirical system is not linked to the panel unit"
                errors.append(message)
                record_errors.append(message)

            expected_schema_version = schema.get("x-instrument-version")
            if record.get("schema_version") != expected_schema_version:
                message = f"{record_location}: record schema_version does not match its contract"
                errors.append(message)
                record_errors.append(message)

            if kind == "evidence":
                evidence_id = record.get("evidence_id")
                if isinstance(evidence_id, str):
                    if evidence_id in evidence_by_id:
                        errors.append(f"{record_location}: duplicate evidence_id {evidence_id}")
                    evidence_by_id[evidence_id] = record
            else:
                if record.get("protocol_version") != instrument_versions.get("protocol"):
                    message = f"{record_location}: protocol_version mismatch"
                    errors.append(message)
                    record_errors.append(message)
                if record.get("codebook_version") != instrument_versions.get("codebook"):
                    message = f"{record_location}: codebook_version mismatch"
                    errors.append(message)
                    record_errors.append(message)
                observation_records.append((record, record_location))
                if not record_errors and isinstance(panel_unit_id, str):
                    covered_units.add(panel_unit_id)

    observation_ids: set[str] = set()
    for record, record_location in observation_records:
        observation_id = record.get("observation_id")
        if isinstance(observation_id, str):
            if observation_id in observation_ids:
                errors.append(f"{record_location}: duplicate observation_id {observation_id}")
            observation_ids.add(observation_id)
        for evidence_id in record.get("evidence_ids", []):
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                errors.append(f"{record_location}: unresolved evidence_id {evidence_id!r}")
            elif evidence.get("panel_unit_id") != record.get("panel_unit_id"):
                errors.append(f"{record_location}: evidence belongs to a different panel unit")

    for panel_unit_id in sorted(set(panel_units) - covered_units):
        errors.append(
            f"{location}: Frozen Panel unit {panel_unit_id!r} has no valid explicit observation coverage"
        )
    return errors


def validate_wave_manifest(
    manifest: Any,
    location: str,
    root: Path | None = None,
) -> list[str]:
    if not isinstance(manifest, dict):
        return [f"{location}: manifest must be an object"]
    errors: list[str] = []

    status = manifest.get("status")
    if status not in {"draft", "locked", "official"}:
        errors.append(f"{location}: status must be draft, locked, or official")

    if status not in {"locked", "official"}:
        if root is not None:
            wave_schema = read_json(root / CURRENT_SCHEMA_PATHS["wave_manifest"])
            errors.extend(validate_contract(manifest, wave_schema, location))
        else:
            for field in (
                "wave_id",
                "status",
                "schema_version",
                "panel_snapshot",
                "registry_snapshot",
                "instrument_locks",
                "schema_locks",
                "scientific_records",
            ):
                if field not in manifest:
                    errors.append(f"{location}: missing required field '{field}'")
        return errors

    if root is None:
        for field in (
            "wave_id",
            "status",
            "schema_version",
            "panel_snapshot",
            "registry_snapshot",
            "instrument_locks",
            "schema_locks",
            "scientific_records",
        ):
            if field not in manifest:
                errors.append(f"{location}: missing required field '{field}'")
        return errors + [f"{location}: {status} Wave requires repository context for integrity checks"]

    panel_ref = manifest.get("panel_snapshot")
    registry_ref = manifest.get("registry_snapshot")
    panel_path_value = panel_ref.get("path") if isinstance(panel_ref, dict) else None
    registry_path_value = registry_ref.get("path") if isinstance(registry_ref, dict) else None
    if panel_path_value and panel_path_value == registry_path_value:
        errors.append(f"{location}: Frozen Panel and Live Registry snapshots must be distinct")

    wave_directory = PurePosixPath(location).parent
    schema_locks = manifest.get("schema_locks")
    if not isinstance(schema_locks, dict):
        errors.append(f"{location}: schema_locks must be an object")
        schema_locks = {}
    schemas: dict[str, dict[str, Any]] = {}
    schema_versions: dict[str, str] = {}
    for name in REQUIRED_SCHEMA_LOCKS:
        if name not in schema_locks:
            errors.append(f"{location}: {status} Wave is missing '{name}' schema lock")
            continue
        path, version, lock_errors = validate_wave_lock(
            root, f"schema:{name}", schema_locks[name], location, wave_directory
        )
        errors.extend(lock_errors)
        if isinstance(version, str):
            schema_versions[name] = version
        if path is not None:
            try:
                schema = read_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{location}: locked schema '{name}' is invalid JSON: {exc}")
            else:
                if not isinstance(schema, dict):
                    errors.append(f"{location}: locked schema '{name}' must be an object")
                else:
                    schemas[name] = schema
                    expected_name = Path(CURRENT_SCHEMA_PATHS[name]).name
                    schema_id = schema.get("$id")
                    if not isinstance(schema_id, str) or not schema_id.endswith(
                        f"/{expected_name}"
                    ):
                        errors.append(
                            f"{location}: locked schema '{name}' identity does not match {expected_name}"
                        )

    bundle_version = manifest.get("schema_version")
    for name, version in schema_versions.items():
        if version != bundle_version:
            errors.append(
                f"{location}: locked schema '{name}' version {version!r} "
                f"does not match Wave schema_version {bundle_version!r}"
            )

    locked_manifest_schema = schemas.get("wave_manifest")
    if isinstance(locked_manifest_schema, dict):
        errors.extend(validate_contract(manifest, locked_manifest_schema, location))

    locks = manifest.get("instrument_locks")
    if not isinstance(locks, dict):
        errors.append(f"{location}: instrument_locks must be an object")
        locks = {}
    instrument_versions: dict[str, str] = {}
    for name in REQUIRED_INSTRUMENT_LOCKS:
        if name not in locks:
            errors.append(f"{location}: {status} Wave is missing '{name}' lock")
            continue
        _, version, lock_errors = validate_wave_lock(
            root,
            name,
            locks[name],
            location,
            wave_directory,
            INSTRUMENT_TITLES[name],
        )
        errors.extend(lock_errors)
        if isinstance(version, str):
            instrument_versions[name] = version

    panel_path: Path | None = None
    registry_path: Path | None = None
    for name, reference in (("panel_snapshot", panel_ref), ("registry_snapshot", registry_ref)):
        relative = reference.get("path") if isinstance(reference, dict) else None
        if isinstance(relative, str) and not _is_within(relative, wave_directory):
            errors.append(f"{location}: {name} must be inside its immutable Wave directory")
        path, reference_errors = validate_artifact_ref(root, reference, f"{location}: {name}")
        errors.extend(reference_errors)
        if name == "panel_snapshot":
            panel_path = path
        else:
            registry_path = path

    panel_units: dict[str, set[str]] = {}
    if panel_path is not None:
        try:
            panel_snapshot = read_json(panel_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{location}: invalid Frozen Panel snapshot JSON: {exc}")
        else:
            panel_schema = schemas.get("panel_snapshot")
            if isinstance(panel_schema, dict):
                errors.extend(
                    validate_contract(panel_snapshot, panel_schema, f"{location}: panel_snapshot")
                )
            expected_panel_version = instrument_versions.get("panel")
            if isinstance(panel_snapshot, dict) and panel_snapshot.get(
                "instrument_version"
            ) != expected_panel_version:
                errors.append(f"{location}: Frozen Panel snapshot instrument_version mismatch")
            if isinstance(panel_snapshot, dict):
                units = panel_snapshot.get("units", [])
                if not isinstance(units, list) or not units:
                    errors.append(f"{location}: locked or official Frozen Panel must be non-empty")
                    units = []
                for unit in units:
                    if not isinstance(unit, dict):
                        continue
                    unit_id = unit.get("panel_unit_id")
                    systems = unit.get("empirical_system_ids")
                    if isinstance(unit_id, str) and isinstance(systems, list):
                        if unit_id in panel_units:
                            errors.append(f"{location}: duplicate panel_unit_id {unit_id}")
                        panel_units[unit_id] = set(item for item in systems if isinstance(item, str))

    if registry_path is not None:
        registry_schema = schemas.get("registry_unit")
        if isinstance(registry_schema, dict):
            errors.extend(
                validate_registry_csv(
                    registry_path, registry_schema, f"{location}: registry_snapshot"
                )
            )

    errors.extend(
        validate_scientific_records(
            root,
            manifest,
            location,
            wave_directory,
            panel_units,
            schemas,
            instrument_versions,
        )
    )

    if status == "official":
        if not isinstance(manifest.get("released_at"), str) or not manifest["released_at"].strip():
            errors.append(f"{location}: official Wave requires released_at")
        approval = manifest.get("release_approval")
        if not isinstance(approval, str) or not approval.strip():
            errors.append(f"{location}: official Wave requires release_approval")
    return errors


def validate_longitudinal_references(
    root: Path, manifests: list[tuple[dict[str, Any], str]]
) -> list[str]:
    """Resolve prior observations across every locked and official Wave."""

    errors: list[str] = []
    observations: list[tuple[dict[str, Any], str]] = []
    by_id: dict[str, tuple[dict[str, Any], str]] = {}

    for manifest, location in manifests:
        if manifest.get("status") not in {"locked", "official"}:
            continue
        scientific_records = manifest.get("scientific_records", {})
        references = (
            scientific_records.get("observations", [])
            if isinstance(scientific_records, dict)
            else []
        )
        if not isinstance(references, list):
            continue
        for index, reference in enumerate(references):
            record_location = f"{location}: scientific_records.observations[{index}]"
            relative = reference.get("path") if isinstance(reference, dict) else None
            path, path_errors = resolve_artifact(root, relative, record_location)
            if path_errors or path is None:
                continue
            try:
                record = read_json(path)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict):
                continue
            observations.append((record, record_location))
            observation_id = record.get("observation_id")
            if isinstance(observation_id, str):
                if observation_id in by_id:
                    errors.append(
                        f"{record_location}: duplicate cross-Wave observation_id {observation_id!r}"
                    )
                else:
                    by_id[observation_id] = (record, record_location)

    for record, record_location in observations:
        event_type = record.get("event_type")
        prior_id = record.get("prior_observation_id")
        if event_type in LONGITUDINAL_EVENTS and not isinstance(prior_id, str):
            errors.append(f"{record_location}: longitudinal event requires prior_observation_id")
            continue
        if not isinstance(prior_id, str):
            continue
        observation_id = record.get("observation_id")
        if prior_id == observation_id:
            errors.append(f"{record_location}: prior_observation_id is a self-reference")
            continue
        prior_entry = by_id.get(prior_id)
        if prior_entry is None:
            errors.append(f"{record_location}: prior_observation_id {prior_id!r} does not resolve")
            continue
        prior, _ = prior_entry
        if prior.get("panel_unit_id") != record.get("panel_unit_id"):
            errors.append(f"{record_location}: prior observation belongs to a different panel unit")
        prior_time = prior.get("observed_at")
        current_time = record.get("observed_at")
        if not isinstance(prior_time, str) or not isinstance(current_time, str):
            continue
        try:
            prior_datetime = datetime.fromisoformat(prior_time.replace("Z", "+00:00"))
            current_datetime = datetime.fromisoformat(current_time.replace("Z", "+00:00"))
            if prior_datetime > current_datetime:
                errors.append(f"{record_location}: prior_observation_id is a forward reference")
            elif prior_datetime == current_datetime:
                errors.append(
                    f"{record_location}: prior observation must be strictly earlier in observed_at"
                )
        except (TypeError, ValueError):
            errors.append(f"{record_location}: observation dates cannot be ordered")
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
        manifest = json.loads(git(root, "show", f"{base_ref}:{path.as_posix()}"))
        if isinstance(manifest, dict) and manifest.get("status") in {"locked", "official"}:
            locked.add(path.parent)
    return locked


def validate_locked_wave_changes(
    locked_directories: set[PurePosixPath], changes: str
) -> list[str]:
    errors: list[str] = []
    for line in changes.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        affected = [PurePosixPath(value) for value in parts[1:]]
        for wave_dir in locked_directories:
            if any(path == wave_dir or wave_dir in path.parents for path in affected):
                errors.append(
                    f"locked Wave '{wave_dir}' is immutable; change '{line}' is not allowed"
                )
                break
    return errors


def validate_immutable_waves(root: Path, base_ref: str) -> list[str]:
    try:
        locked_directories = locked_wave_directories_at_base(root, base_ref)
        changes = git(root, "diff", "--name-status", base_ref, "--", "data/waves")
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        return [f"cannot verify locked Waves against {base_ref}: {detail}"]
    return validate_locked_wave_changes(locked_directories, changes)


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
        if path.is_file() and declared_version(path) is None:
            errors.append(f"{relative}: missing explicit Instrument version")

    instruments, instrument_errors = load_instruments(root)
    errors.extend(instrument_errors)

    registry_path = root / "registry/live-registry.csv"
    registry_schema_path = root / "schemas/registry-unit.schema.json"
    if not registry_path.is_file():
        errors.append("missing Live Registry: registry/live-registry.csv")
    elif registry_schema_path.is_file():
        errors.extend(
            validate_registry_csv(
                registry_path,
                read_json(registry_schema_path),
                "registry/live-registry.csv",
            )
        )

    evidence_schema_path = root / "schemas/evidence.schema.json"
    if evidence_schema_path.is_file():
        evidence_schema = read_json(evidence_schema_path)
        for path in sorted((root / "evidence").rglob("*.json")):
            relative = path.relative_to(root).as_posix()
            try:
                record = read_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative}: invalid JSON: {exc}")
                continue
            errors.extend(validate_contract(record, evidence_schema, relative))

    waves_root = root / "data/waves"
    manifests: list[tuple[dict[str, Any], str]] = []
    if waves_root.is_dir():
        for manifest_path in sorted(waves_root.glob("*/manifest.json")):
            relative = manifest_path.relative_to(root).as_posix()
            try:
                manifest = read_json(manifest_path)
            except json.JSONDecodeError as exc:
                errors.append(f"{relative}: invalid JSON: {exc}")
                continue
            if isinstance(manifest, dict):
                manifests.append((manifest, relative))
            errors.extend(validate_wave_manifest(manifest, relative, root))
    errors.extend(validate_longitudinal_references(root, manifests))

    if base_ref:
        errors.extend(validate_immutable_waves(root, base_ref))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-ref",
        help="Git ref used to prove byte-immutability of previously locked Waves",
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
    print("Validation passed: scientific contracts and Wave integrity gates are sound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
