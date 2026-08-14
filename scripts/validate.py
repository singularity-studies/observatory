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
    "selection",
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
    "schemas/candidate-unit.schema.json",
    "schemas/eligibility-decision.schema.json",
    "schemas/panel-lineage.schema.json",
    "schemas/panel-selection-manifest.schema.json",
    "schemas/panel-selection-review.schema.json",
    "schemas/panel-lock-governance-decision.schema.json",
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
    "candidate_unit",
    "eligibility_decision",
    "panel_lineage",
    "panel_selection_manifest",
    "panel_selection_review",
    "panel_lock_governance_decision",
    "wave_manifest",
)
CURRENT_SCHEMA_PATHS = {
    "registry_unit": "schemas/registry-unit.schema.json",
    "panel_snapshot": "schemas/panel-snapshot.schema.json",
    "evidence": "schemas/evidence.schema.json",
    "observation": "schemas/observation.schema.json",
    "candidate_unit": "schemas/candidate-unit.schema.json",
    "eligibility_decision": "schemas/eligibility-decision.schema.json",
    "panel_lineage": "schemas/panel-lineage.schema.json",
    "panel_selection_manifest": "schemas/panel-selection-manifest.schema.json",
    "panel_selection_review": "schemas/panel-selection-review.schema.json",
    "panel_lock_governance_decision": "schemas/panel-lock-governance-decision.schema.json",
    "wave_manifest": "schemas/wave-manifest.schema.json",
}

ELIGIBILITY_CRITERIA = (
    "improvement_loop_relevance",
    "functional_boundedness",
    "human_criticality_interrogability",
    "longitudinal_identity_stability",
    "re_observability",
    "evidence_traceability",
    "boundary_condition_expressibility",
    "non_redundancy",
)

SELECTION_RECORD_PATHS = {
    "candidate_unit": "selection/candidates",
    "eligibility_decision": "selection/eligibility",
    "panel_lineage": "selection/lineage",
    "panel_selection_manifest": "selection/manifests",
    "panel_selection_review": "selection/reviews",
    "panel_lock_governance_decision": "selection/governance",
}

CANDIDATE_IDENTITY_FIELDS = (
    "domain",
    "improvement_loop_id",
    "function_or_stage",
    "operational_boundary",
    "continuity_rule",
    "boundary_conditions",
)

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

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{location}: value is below minimum {schema['minimum']}")

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


def _load_json_artifact(
    root: Path,
    reference: Any,
    location: str,
    container: PurePosixPath | None = None,
) -> tuple[Any | None, Path | None, list[str]]:
    errors: list[str] = []
    relative = reference.get("path") if isinstance(reference, dict) else None
    if container is not None and isinstance(relative, str) and not _is_within(relative, container):
        errors.append(f"{location}: selection artifact must be inside {container.as_posix()}/")
    path, artifact_errors = validate_artifact_ref(root, reference, location)
    errors.extend(artifact_errors)
    if path is None:
        return None, None, errors
    try:
        record = read_json(path)
    except json.JSONDecodeError as exc:
        errors.append(f"{location}: invalid JSON: {exc}")
        return None, path, errors
    return record, path, errors


def validate_candidate_unit(
    record: Any,
    schema: dict[str, Any],
    location: str,
    expected_version: str | None = None,
) -> list[str]:
    errors = validate_contract(record, schema, location)
    if not isinstance(record, dict):
        return errors
    schema_version = schema.get("x-instrument-version")
    required_version = expected_version or schema_version
    if record.get("instrument_version") != required_version:
        errors.append(f"{location}: candidate instrument_version mismatch")
    return errors


def validate_eligibility_decision(
    root: Path,
    record: Any,
    location: str,
    eligibility_schema: dict[str, Any],
    candidate_schema: dict[str, Any],
    expected_version: str | None = None,
    container: PurePosixPath | None = None,
) -> list[str]:
    errors = validate_contract(record, eligibility_schema, location)
    if not isinstance(record, dict):
        return errors

    required_version = expected_version or eligibility_schema.get("x-instrument-version")
    if record.get("instrument_version") != required_version:
        errors.append(f"{location}: eligibility instrument_version mismatch")

    criteria = record.get("criteria")
    results = {
        name: criteria.get(name, {}).get("result")
        for name in ELIGIBILITY_CRITERIA
        if isinstance(criteria, dict) and isinstance(criteria.get(name), dict)
    }
    if set(results) == set(ELIGIBILITY_CRITERIA) and all(
        results[name] in {"passed", "failed", "unresolved"} for name in ELIGIBILITY_CRITERIA
    ):
        if any(result == "failed" for result in results.values()):
            expected_status = "ineligible"
        elif any(result == "unresolved" for result in results.values()):
            expected_status = "unresolved"
        else:
            expected_status = "eligible"
        if record.get("decision_status") != expected_status:
            errors.append(
                f"{location}: decision_status must deterministically be {expected_status!r}"
            )

    review = record.get("review")
    if isinstance(review, dict):
        reviewer_status = review.get("reviewer_status")
        reviewer_id = review.get("reviewer_id")
        if reviewer_status == "unassigned" and reviewer_id is not None:
            errors.append(f"{location}: unassigned reviewer_id must remain null")
        if reviewer_status == "assigned" and not (
            isinstance(reviewer_id, str) and reviewer_id.strip()
        ):
            errors.append(f"{location}: assigned reviewer requires reviewer_id")
        adjudication_status = review.get("adjudication_status")
        adjudicator_id = review.get("adjudicator_id")
        if adjudication_status in {"unresolved", "not_required"} and adjudicator_id is not None:
            errors.append(f"{location}: unresolved or unnecessary adjudicator_id must remain null")
        if adjudication_status == "complete" and not (
            isinstance(adjudicator_id, str) and adjudicator_id.strip()
        ):
            errors.append(f"{location}: complete adjudication requires adjudicator_id")

    candidate, _, reference_errors = _load_json_artifact(
        root,
        record.get("candidate_specification"),
        f"{location}: candidate_specification",
        container,
    )
    errors.extend(reference_errors)
    if candidate is not None:
        errors.extend(
            validate_candidate_unit(
                candidate,
                candidate_schema,
                f"{location}: candidate_specification",
                required_version,
            )
        )
        if isinstance(candidate, dict) and candidate.get("candidate_unit_id") != record.get(
            "candidate_unit_id"
        ):
            errors.append(f"{location}: eligibility candidate identity mismatch")
    return errors


def validate_lineage_record(
    record: Any,
    schema: dict[str, Any],
    location: str,
    expected_version: str | None = None,
) -> list[str]:
    errors = validate_contract(record, schema, location)
    if not isinstance(record, dict):
        return errors
    required_version = expected_version or schema.get("x-instrument-version")
    if record.get("instrument_version") != required_version:
        errors.append(f"{location}: lineage instrument_version mismatch")
    retired = record.get("retired_unit")
    retired_id = retired.get("panel_unit_id") if isinstance(retired, dict) else None
    successors = record.get("successors")
    if isinstance(successors, list) and isinstance(retired_id, str):
        for index, successor in enumerate(successors):
            if isinstance(successor, dict) and successor.get("successor_unit_id") == retired_id:
                errors.append(
                    f"{location}: successors[{index}] cannot reuse retired panel_unit_id {retired_id!r}"
                )
    return errors


def validate_scientific_review_record(
    record: Any,
    schema: dict[str, Any],
    location: str,
    expected_version: str | None = None,
) -> list[str]:
    errors = validate_contract(record, schema, location)
    if not isinstance(record, dict):
        return errors
    required_version = expected_version or schema.get("x-instrument-version")
    if record.get("instrument_version") != required_version:
        errors.append(f"{location}: scientific review instrument_version mismatch")
    return errors


def validate_governance_decision_record(
    record: Any,
    schema: dict[str, Any],
    location: str,
    expected_version: str | None = None,
) -> list[str]:
    errors = validate_contract(record, schema, location)
    if not isinstance(record, dict):
        return errors
    required_version = expected_version or schema.get("x-instrument-version")
    if record.get("instrument_version") != required_version:
        errors.append(f"{location}: governance decision instrument_version mismatch")
    return errors


def _validate_plain_artifact(
    root: Path,
    reference: Any,
    location: str,
    container: PurePosixPath | None,
) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    relative = reference.get("path") if isinstance(reference, dict) else None
    if container is not None and isinstance(relative, str) and not _is_within(relative, container):
        errors.append(f"{location}: selection artifact must be inside {container.as_posix()}/")
    path, artifact_errors = validate_artifact_ref(root, reference, location)
    errors.extend(artifact_errors)
    if path is not None and path.stat().st_size == 0:
        errors.append(f"{location}: referenced record must not be empty")
    return path, errors


def validate_selection_manifest(
    root: Path,
    manifest: Any,
    location: str,
    schemas: dict[str, dict[str, Any]],
    container: PurePosixPath | None = None,
    expected_protocol_version: str | None = None,
) -> tuple[dict[str, tuple[dict[str, Any], dict[str, Any]]], list[str]]:
    schema = schemas.get("panel_selection_manifest")
    candidate_schema = schemas.get("candidate_unit")
    eligibility_schema = schemas.get("eligibility_decision")
    lineage_schema = schemas.get("panel_lineage")
    review_schema = schemas.get("panel_selection_review")
    governance_schema = schemas.get("panel_lock_governance_decision")
    if not all(
        isinstance(item, dict)
        for item in (
            schema,
            candidate_schema,
            eligibility_schema,
            lineage_schema,
            review_schema,
            governance_schema,
        )
    ):
        return {}, [f"{location}: complete selection schema bundle is required"]

    errors = validate_contract(manifest, schema, location)
    if not isinstance(manifest, dict):
        return {}, errors

    instrument_version = manifest.get("instrument_version")
    if instrument_version != schema.get("x-instrument-version"):
        errors.append(f"{location}: selection manifest instrument_version mismatch")
    selected_values = manifest.get("selected_unit_ids")
    selected_ids = {
        item for item in selected_values if isinstance(item, str)
    } if isinstance(selected_values, list) else set()

    if manifest.get("status") != "locked":
        return {}, errors

    protocol = manifest.get("selection_protocol")
    if not isinstance(protocol, dict) or protocol.get("status") != "locked":
        errors.append(f"{location}: locked selection requires a locked protocol version")
    else:
        protocol_version = protocol.get("version")
        if protocol_version != instrument_version:
            errors.append(f"{location}: selection protocol version mismatch")
        if expected_protocol_version is not None and protocol_version != expected_protocol_version:
            errors.append(f"{location}: selection protocol does not match Frozen Panel version")
        protocol_path, protocol_errors = _validate_plain_artifact(
            root,
            protocol.get("artifact"),
            f"{location}: selection_protocol",
            container,
        )
        errors.extend(protocol_errors)
        if protocol_path is not None:
            if declared_version(protocol_path) != protocol_version:
                errors.append(f"{location}: selection protocol artifact version mismatch")
            text = protocol_path.read_text(encoding="utf-8")
            if "Instrument: Frozen Panel Specification" not in text:
                errors.append(f"{location}: selection protocol artifact identity mismatch")

    universe = manifest.get("candidate_universe_snapshot")
    candidate_references = universe.get("candidate_specifications") if isinstance(universe, dict) else None
    if not isinstance(universe, dict) or not isinstance(universe.get("snapshot_id"), str):
        errors.append(f"{location}: locked selection requires candidate universe snapshot identity")
    if not isinstance(candidate_references, list) or not candidate_references:
        errors.append(f"{location}: empty candidate universe cannot lock a Frozen Panel")
        candidate_references = []

    candidates: dict[str, dict[str, Any]] = {}
    candidate_references_by_id: dict[str, dict[str, Any]] = {}
    for index, reference in enumerate(candidate_references):
        record_location = f"{location}: candidate_universe_snapshot[{index}]"
        candidate, _, artifact_errors = _load_json_artifact(
            root, reference, record_location, container
        )
        errors.extend(artifact_errors)
        if candidate is None:
            continue
        candidate_errors = validate_candidate_unit(
            candidate, candidate_schema, record_location, instrument_version
        )
        errors.extend(candidate_errors)
        if isinstance(candidate, dict):
            candidate_id = candidate.get("candidate_unit_id")
            if isinstance(candidate_id, str):
                if candidate_id in candidates:
                    errors.append(f"{record_location}: duplicate candidate_unit_id {candidate_id}")
                candidates[candidate_id] = candidate
                if isinstance(reference, dict):
                    candidate_references_by_id[candidate_id] = reference

    eligibility_by_candidate: dict[str, list[dict[str, Any]]] = {}
    eligibility_ids: set[str] = set()
    decisions = manifest.get("eligibility_decisions")
    if not isinstance(decisions, list):
        errors.append(f"{location}: eligibility_decisions must be an array")
        decisions = []
    for index, reference in enumerate(decisions):
        record_location = f"{location}: eligibility_decisions[{index}]"
        decision, _, artifact_errors = _load_json_artifact(
            root, reference, record_location, container
        )
        errors.extend(artifact_errors)
        if decision is None:
            continue
        decision_errors = validate_eligibility_decision(
            root,
            decision,
            record_location,
            eligibility_schema,
            candidate_schema,
            instrument_version,
            container,
        )
        errors.extend(decision_errors)
        if isinstance(decision, dict):
            decision_id = decision.get("eligibility_decision_id")
            if isinstance(decision_id, str):
                if decision_id in eligibility_ids:
                    errors.append(f"{record_location}: duplicate eligibility_decision_id {decision_id}")
                eligibility_ids.add(decision_id)
            candidate_id = decision.get("candidate_unit_id")
            if isinstance(candidate_id, str):
                eligibility_by_candidate.setdefault(candidate_id, []).append(decision)
                universe_reference = candidate_references_by_id.get(candidate_id)
                if universe_reference is not None and decision.get(
                    "candidate_specification"
                ) != universe_reference:
                    errors.append(
                        f"{record_location}: eligibility decision must bind the exact candidate-universe specification"
                    )

    for candidate_id in sorted(candidates):
        count = len(eligibility_by_candidate.get(candidate_id, []))
        if count != 1:
            errors.append(
                f"{location}: candidate-universe member {candidate_id!r} requires exactly one eligibility decision"
            )
    outside_decisions = set(eligibility_by_candidate) - set(candidates)
    if outside_decisions:
        errors.append(
            f"{location}: eligibility decisions refer outside candidate universe: {sorted(outside_decisions)}"
        )

    lineage_references = manifest.get("lineage_relations")
    if not isinstance(lineage_references, list):
        errors.append(f"{location}: lineage_relations must be an array")
        lineage_references = []
    for index, reference in enumerate(lineage_references):
        record_location = f"{location}: lineage_relations[{index}]"
        lineage, _, artifact_errors = _load_json_artifact(
            root, reference, record_location, container
        )
        errors.extend(artifact_errors)
        if lineage is not None:
            errors.extend(
                validate_lineage_record(
                    lineage, lineage_schema, record_location, instrument_version
                )
            )

    eligible_ids = {
        candidate_id
        for candidate_id in candidates
        if len(eligibility_by_candidate.get(candidate_id, [])) == 1
        and eligibility_by_candidate[candidate_id][0].get("decision_status") == "eligible"
    }
    dispositions = manifest.get("selection_dispositions")
    if not isinstance(dispositions, list):
        errors.append(f"{location}: selection_dispositions must be an array")
        dispositions = []
    disposition_by_candidate: dict[str, dict[str, Any]] = {}
    for index, disposition in enumerate(dispositions):
        disposition_location = f"{location}: selection_dispositions[{index}]"
        if not isinstance(disposition, dict):
            continue
        candidate_id = disposition.get("candidate_unit_id")
        if not isinstance(candidate_id, str):
            continue
        if candidate_id in disposition_by_candidate:
            errors.append(f"{disposition_location}: duplicate selection disposition")
        disposition_by_candidate[candidate_id] = disposition
        if disposition.get("disposition") == "not_selected" and not all(
            isinstance(disposition.get(field), str) and disposition[field].strip()
            for field in ("rationale", "uncertainty")
        ):
            errors.append(
                f"{disposition_location}: not_selected requires rationale and uncertainty"
            )

    if set(disposition_by_candidate) != eligible_ids:
        missing = sorted(eligible_ids - set(disposition_by_candidate))
        outside = sorted(set(disposition_by_candidate) - eligible_ids)
        if missing:
            errors.append(f"{location}: eligible candidates lack selection disposition: {missing}")
        if outside:
            errors.append(f"{location}: selection dispositions refer to non-eligible candidates: {outside}")

    disposition_selected_ids = {
        candidate_id
        for candidate_id, disposition in disposition_by_candidate.items()
        if disposition.get("disposition") == "selected"
    }
    if selected_ids != disposition_selected_ids:
        errors.append(
            f"{location}: selected_unit_ids must exactly equal selected dispositions"
        )
    if not selected_ids:
        errors.append(f"{location}: locked selection requires a non-empty selected set")

    coverage = manifest.get("coverage_redundancy_review")
    if not isinstance(coverage, dict) or coverage.get("status") != "recorded":
        errors.append(f"{location}: locked selection requires recorded coverage/redundancy review")
    elif not all(
        isinstance(coverage.get(field), str) and coverage[field].strip()
        for field in ("rationale", "uncertainty")
    ):
        errors.append(f"{location}: coverage/redundancy review requires rationale and uncertainty")

    panel_size = manifest.get("panel_size")
    n = panel_size.get("n") if isinstance(panel_size, dict) else None
    if not isinstance(panel_size, dict) or panel_size.get("status") != "fixed":
        errors.append(f"{location}: locked selection requires prospectively fixed panel size")
    elif not isinstance(n, int) or isinstance(n, bool) or n < 1:
        errors.append(f"{location}: fixed panel size must be a positive integer")
    elif n != len(selected_ids):
        errors.append(f"{location}: fixed panel size does not match selected unit count")
    if isinstance(panel_size, dict) and not (
        isinstance(panel_size.get("rationale"), str) and panel_size["rationale"].strip()
    ):
        errors.append(f"{location}: panel size requires prospective rationale")

    scientific_review = manifest.get("scientific_review")
    if not isinstance(scientific_review, dict) or scientific_review.get("status") != "complete":
        errors.append(f"{location}: locked selection requires completed scientific review")
    else:
        review_record, _, review_errors = _load_json_artifact(
            root,
            scientific_review.get("review_record"),
            f"{location}: scientific_review",
            container,
        )
        errors.extend(review_errors)
        if review_record is not None:
            errors.extend(
                validate_scientific_review_record(
                    review_record,
                    review_schema,
                    f"{location}: scientific_review",
                    instrument_version,
                )
            )
            if not isinstance(review_record, dict) or review_record.get("outcome") != "approved":
                errors.append(
                    f"{location}: locked selection requires explicitly approved scientific review"
                )

    governance = manifest.get("governance_authority")
    if not isinstance(governance, dict) or governance.get("status") != "recorded":
        errors.append(f"{location}: locked selection requires recorded governance authority")
    else:
        authority_id = governance.get("authority_id")
        if not isinstance(authority_id, str) or not authority_id.strip():
            errors.append(f"{location}: governance authority_id is required")
        governance_record, _, governance_errors = _load_json_artifact(
            root,
            governance.get("decision_record"),
            f"{location}: governance_authority",
            container,
        )
        errors.extend(governance_errors)
        if governance_record is not None:
            errors.extend(
                validate_governance_decision_record(
                    governance_record,
                    governance_schema,
                    f"{location}: governance_authority",
                    instrument_version,
                )
            )
            if not isinstance(governance_record, dict) or governance_record.get(
                "outcome"
            ) != "authorized":
                errors.append(
                    f"{location}: locked selection requires explicitly authorized governance decision"
                )
            if isinstance(governance_record, dict) and governance_record.get(
                "responsible_authority_id"
            ) != authority_id:
                errors.append(f"{location}: governance authority identity mismatch")

    selected_bindings = {
        candidate_id: (candidates[candidate_id], candidate_references_by_id[candidate_id])
        for candidate_id in selected_ids
        if candidate_id in candidates and candidate_id in candidate_references_by_id
    }
    return selected_bindings, errors


def validate_selection_repository(root: Path) -> list[str]:
    errors: list[str] = []
    schemas: dict[str, dict[str, Any]] = {}
    for name in SELECTION_RECORD_PATHS:
        path = root / CURRENT_SCHEMA_PATHS[name]
        if not path.is_file():
            continue
        try:
            schema = read_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: invalid JSON: {exc}")
            continue
        if isinstance(schema, dict):
            schemas[name] = schema

    for name, relative_directory in SELECTION_RECORD_PATHS.items():
        directory = root / relative_directory
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            location = path.relative_to(root).as_posix()
            try:
                record = read_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{location}: invalid JSON: {exc}")
                continue
            if name == "candidate_unit" and name in schemas:
                errors.extend(validate_candidate_unit(record, schemas[name], location))
            elif name == "eligibility_decision" and all(
                item in schemas for item in ("eligibility_decision", "candidate_unit")
            ):
                errors.extend(
                    validate_eligibility_decision(
                        root,
                        record,
                        location,
                        schemas["eligibility_decision"],
                        schemas["candidate_unit"],
                        container=PurePosixPath("selection"),
                    )
                )
            elif name == "panel_lineage" and name in schemas:
                errors.extend(validate_lineage_record(record, schemas[name], location))
            elif name == "panel_selection_review" and name in schemas:
                errors.extend(
                    validate_scientific_review_record(record, schemas[name], location)
                )
            elif name == "panel_lock_governance_decision" and name in schemas:
                errors.extend(
                    validate_governance_decision_record(record, schemas[name], location)
                )
            elif name == "panel_selection_manifest":
                _, manifest_errors = validate_selection_manifest(
                    root,
                    record,
                    location,
                    schemas,
                    container=PurePosixPath("selection"),
                )
                errors.extend(manifest_errors)
    return errors


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

                selection_reference = panel_snapshot.get("selection_manifest")
                selection_manifest, _, selection_reference_errors = _load_json_artifact(
                    root,
                    selection_reference,
                    f"{location}: panel_snapshot selection_manifest",
                    wave_directory,
                )
                errors.extend(selection_reference_errors)
                if selection_manifest is not None:
                    selected_bindings, selection_errors = validate_selection_manifest(
                        root,
                        selection_manifest,
                        f"{location}: panel_snapshot selection_manifest",
                        schemas,
                        wave_directory,
                        expected_panel_version,
                    )
                    errors.extend(selection_errors)
                    if set(selected_bindings) != set(panel_units):
                        errors.append(
                            f"{location}: Frozen Panel units must exactly match the locked selection manifest"
                        )
                    for unit in units:
                        if not isinstance(unit, dict):
                            continue
                        unit_id = unit.get("panel_unit_id")
                        binding = selected_bindings.get(unit_id)
                        if binding is None:
                            continue
                        candidate, candidate_reference = binding
                        if unit.get("candidate_specification") != candidate_reference:
                            errors.append(
                                f"{location}: Frozen Panel unit {unit_id!r} must preserve "
                                "the exact candidate specification path and SHA-256 binding"
                            )
                        for field in CANDIDATE_IDENTITY_FIELDS:
                            if unit.get(field) != candidate.get(field):
                                errors.append(
                                    f"{location}: Frozen Panel unit {unit_id!r} changes "
                                    f"candidate semantic identity field {field!r}"
                                )

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
    errors.extend(validate_selection_repository(root))

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
