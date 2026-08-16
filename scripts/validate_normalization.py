#!/usr/bin/env python3
"""Fail-closed validation for prospective Domain normalization artifacts."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


PASS1_SCHEMA_PATH = "schemas/domain-normalization-pass1.schema.json"
PASS1_DIRECTORY = "domain-universe/normalization/pass1"
PASS2A_SCHEMA_PATH = "schemas/domain-normalization-pass2a.schema.json"
PASS2A_DIRECTORY = "domain-universe/normalization/pass2a"
PASS2A_PATH = f"{PASS2A_DIRECTORY}/equivalence-groups-v0.1.json"
PASS2B_SCHEMA_PATH = "schemas/domain-normalization-pass2b.schema.json"
PASS2B_DIRECTORY = "domain-universe/normalization/pass2b"
PASS2B_PATH = f"{PASS2B_DIRECTORY}/deferred-equivalence-adjudication-v0.1.json"
RESIDUAL_SCHEMA_PATH = "schemas/domain-normalization-residual-clarification.schema.json"
RESIDUAL_DIRECTORY = "domain-universe/normalization/residuals"
RESIDUAL_PATH = f"{RESIDUAL_DIRECTORY}/ipc-residual-clarification-v0.1.json"
CLOSURE_AMENDMENT_PATH = "domain-universe/NORMALIZATION_CLOSURE_AMENDMENT.md"
CLOSURE_SCHEMA_PATH = "schemas/domain-normalization-closure-decision.schema.json"
CLOSURE_DIRECTORY = "domain-universe/normalization/closure"
CLOSURE_PATH = f"{CLOSURE_DIRECTORY}/ipc-residual-closure-v0.1.json"
MATERIALIZATION_PROTOCOL_PATH = (
    "domain-universe/NORMALIZATION_MATERIALIZATION_PROTOCOL.md"
)
OVERLAY_SCHEMA_PATH = "schemas/domain-normalization-disposition-overlay.schema.json"
OVERLAY_DIRECTORY = "domain-universe/normalization/dispositions"
CANDIDATE_SCHEMA_PATH = "schemas/domain-candidate.schema.json"
COMPLETION_SCHEMA_PATH = "schemas/domain-normalization-completion.schema.json"
COMPLETION_DIRECTORY = "domain-universe/normalization/completion"
COMPLETION_PATH = f"{COMPLETION_DIRECTORY}/normalization-completion-v0.1.json"
SUCCESSOR_MATERIALIZATION_PROTOCOL_PATH = (
    "domain-universe/NORMALIZATION_MATERIALIZATION_PROTOCOL_v0.2.md"
)
SUCCESSOR_OVERLAY_SCHEMA_PATH = (
    "schemas/domain-normalization-disposition-overlay-v0.2.schema.json"
)
CODEBOOK_PATH = "domain-universe/NORMALIZATION_CODEBOOK.md"
BOUNDARY_PATH = "domain-universe/boundaries/du-boundary-v0.1.json"
EXPECTED_PASS2A_SHA256 = "e830a1cf566888badc31776ad263077208dae458d5f9e53f0783a5bdd778c822"
EXPECTED_PASS2B_SHA256 = "4ec539b016e35cd7ec6f0545160d662a508472e4b664e843e8a7a1d8c227d012"
EXPECTED_MATERIALIZATION_PROTOCOL_SHA256 = (
    "1d10310c5c2c3337e6cb87596f46b981ce55a3e5ae46b4fb385644e8ebac97a4"
)
EXPECTED_CODEBOOK_SHA256 = "bc0f2d62c8b6219911b759e8a69332021cb471167a9e3fdbc6a4b5b8918b69e4"
EXPECTED_RESIDUAL_SHA256 = "610e36a5776bacd423fed1d926ee13c32f2eff2c98a9f4a523abc6bed59b083a"
EXPECTED_CLOSURE_AMENDMENT_SHA256 = (
    "edc324516ffe98888e0621f1d47ff019b6ca33c7d7ebc9266f32613b3e7a6570"
)
EXPECTED_CLOSURE_SCHEMA_SHA256 = (
    "3fec41de4f93eebe4632c2f5bfab28450e74f281581a6b3744dbb509143893cb"
)
EXPECTED_CLOSURE_SHA256 = (
    "4df98da8522b17957acc49a34a160740a52487905f5b709af104c34a61269c81"
)
EXPECTED_BOUNDARY_SHA256 = "d60ac188138cfc638b53ccfa05635e5d65372586d57553ff55fa7895040a6581"
EXPECTED_OVERLAY_SCHEMA_SHA256 = (
    "1dc14aac93d6b0b529fbe8a8258c9f14d8c551222f73b6a796eb52fbf2370f64"
)
EXPECTED_COMPLETION_SCHEMA_SHA256 = (
    "3981024a36ae5d351559329ba5bfc782cec5c7a8d16572280fb76c2861bc09da"
)
EXPECTED_COMPLETION_SHA256 = (
    "6e86b856966ae352aaf8777a2e0389954294b51ef5a98a6c228109b56c763643"
)
EXPECTED_SUCCESSOR_MATERIALIZATION_PROTOCOL_SHA256 = (
    "cd34e1147970e6353cecf64eb710a4a596674005116bb30db839b5e267bdae4a"
)
EXPECTED_SUCCESSOR_OVERLAY_SCHEMA_SHA256 = (
    "5d7a11e304b714f79f9edbf3fc4ca692652d53000fa46e84a4d4f3d63a3915e7"
)
EXPECTED_CANDIDATE_UNIVERSE_SHAPE_SHA256 = (
    "4449c3b488af822ed6e6e42a17138d2dd7ef25a8c7f3dbecf6cb1325e828528c"
)
EXPECTED_CANDIDATE_ID_ORDER_SHA256 = (
    "62e674888a47027ff3bd30a9c48cdebc12a503f1e2a07581864427128d3ba4ab"
)
STABLE_CANDIDATE_ID_ASSIGNMENT_PERMITTED = True
EXPECTED_EXTRACTION_SHA256 = {
    "domain-universe/extractions/oecd-ford-frascati-2015-second-level.json":
        "eb376d7c4da77078cdfdc9772daf166eb3bf6e11a973df0241b1fb782128b6e4",
    "domain-universe/extractions/un-cofog-1999-group.json":
        "0b5061f4a1029fe28e1ccb5a1c3f5563371e876f983bb6b6365883b7c875e3dd",
    "domain-universe/extractions/un-isic-rev5-division.json":
        "569b5ac552ffdf0f5fcf993e8918181a9005c2c9d6e4b19c701126d3b1f2b9b9",
    "domain-universe/extractions/wipo-ipc-2026-01-class.json":
        "e8cf7903547eb245a2e4447b1221aa73df541c1da4a748e5127a232a87efe33c",
}
EXPECTED_SOURCE_FRAME_SHA256 = {
    "domain-universe/source-frames/oecd-ford-frascati-2015.json":
        "472c821fa78861e446222dd22730a08974573d3cac50fd7ee9865a58f9d9d348",
    "domain-universe/source-frames/un-cofog-1999.json":
        "1148106a005d2701e6f6142e55260c2979db25f98574f2c8ec1eca26da768d82",
    "domain-universe/source-frames/un-isic-rev5.json":
        "6e30b6fa28c8dcf3a3e06a1ca630e6ea9346b3c56ec5501fc442e0f13d94afea",
    "domain-universe/source-frames/wipo-ipc-2026-01.json":
        "815729fe39b8c422b7151a64d1c64b0526926c9c0906cbf08e129a7336561dc8",
}
PASS2B_CRITERIA = (
    "same_substantive_locus",
    "equivalent_inclusion_envelope",
    "equivalent_exclusion_envelope",
    "no_material_scope_asymmetry",
    "lens_difference_only",
)
EXPECTED_PASS2B_ADJUDICATIONS = {
    "civil-engineering-ford-isic": (
        ("oecd-ford-frascati-2015", "ford-2.1", "ng-73a29d43db0bb8be"),
        ("un-isic-rev5", "isic-42", "ng-e0e507e25b84e9a4"),
    ),
    "education-ford-isic": (
        ("oecd-ford-frascati-2015", "ford-5.3", "ng-d0e631acf950ddad"),
        ("un-isic-rev5", "isic-85", "ng-35c79c5f079afbd3"),
    ),
}
EXPECTED_PASS2B_SOURCES = {
    "oecd-frascati-2015-official-pdf": {
        "source_frame_id": "oecd-ford-frascati-2015",
        "source_uri": (
            "https://www.oecd.org/content/dam/oecd/en/publications/reports/2015/10/"
            "frascati-manual-2015_g1g57dcb/9789264239012-en.pdf"
        ),
        "sha256": "98e19466a97c2c63e2d8070fe66de7ac8ad18db253429d979349f8a2e72f3775",
    },
    "un-isic-rev5-explanatory-notes-2024-03-11": {
        "source_frame_id": "un-isic-rev5",
        "source_uri": (
            "https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/"
            "ISIC5_Exp_Notes_11Mar2024.pdf"
        ),
        "sha256": "b9ef4ac00d3b1736a5d7068e437babaa0105dd02ad70a86c11c9905878271ae8",
    },
}
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
EXPECTED_PASS1_SHA256 = {
    "oecd-ford-frascati-2015-pass1.json":
        "d62c8f899b3b966381cdd693adcb1e9bf89cd6210474b8d30a4550889fb5612d",
    "un-cofog-1999-pass1.json":
        "e95466d6e82c20f4d0f082e914509c080ebb962182c09fce20faad0786f226cc",
    "un-isic-rev5-pass1.json":
        "7b02e4a2864076700c2d1d26910ef2b591e7771007d4819670f8c30a70d82cb3",
    "wipo-ipc-2026-01-pass1.json":
        "8ca43b8888fe64d5f96c663dead2a2e37b8da9f687af1ee42188c21926723a9a",
}
EXPECTED_UNRESOLVED = {
    ("wipo-ipc-2026-01", f"ipc-{section}99")
    for section in "ABCDEFGH"
}
EXPECTED_RESIDUAL_SECTIONS = {
    "A": "HUMAN NECESSITIES",
    "B": "PERFORMING OPERATIONS; TRANSPORTING",
    "C": "CHEMISTRY; METALLURGY",
    "D": "TEXTILES; PAPER",
    "E": "FIXED CONSTRUCTIONS",
    "F": "MECHANICAL ENGINEERING; LIGHTING; HEATING; WEAPONS; BLASTING",
    "G": "PHYSICS",
    "H": "ELECTRICITY",
}
EXPECTED_RESIDUAL_SOURCES = {
    "wipo-ipc-2026-01-scheme-package": {
        "source_frame_id": "wipo-ipc-2026-01",
        "source_uri": (
            "https://www.wipo.int/classifications/data/ipc/"
            "ITSupport_and_download_area/20260101/MasterFiles/"
            "ipc_scheme_20260101.zip"
        ),
        "sha256": "22977dd19b2061d155b4d48558b495192418bafca8147ea15eea2e05019e4849",
    },
    "wipo-guide-ipc-2026-official-pdf": {
        "source_frame_id": "wipo-ipc-2026-01",
        "source_uri": (
            "https://tind.wipo.int/record/60169/files/"
            "wipo-guide-ipc-2026-en-guide-to-the-international-patent-"
            "classification-2026.pdf?register_download=0"
        ),
        "sha256": "3a85807f469dc19004fc9d152f33f44627528934519f7cd08248885771bdfdb3",
    },
}
RESIDUAL_GATE_FIELDS = (
    "coherent_substantive_locus",
    "topic_preserving_translatability",
    "boundary_compatibility",
)
PROHIBITED_RESIDUAL_FIELDS = {
    "candidate_id",
    "domain_candidate_id",
    "target_candidate_id",
    "target_domain_candidate_id",
    "normalization_group_id",
    "equivalence_relation",
    "equivalent_source_entry_ids",
    "related_source_entry_ids",
    "cross_entry_comparison",
}
EXPECTED_CLOSURE_DECISIONS = {
    f"ipc-{section}99-closure": (
        "wipo-ipc-2026-01",
        f"ipc-{section}99",
        f"ipc-{section}99-residual-clarification",
    )
    for section in "ABCDEFGH"
}
PROHIBITED_CLOSURE_FIELDS = {
    "candidate_id",
    "domain_candidate_id",
    "target_candidate_id",
    "target_domain_candidate_id",
    "target_domain_candidate_ids",
    "normalization_group_id",
    "equivalence_relation",
    "equivalent_source_entry_ids",
    "related_source_entry_ids",
    "clarification_sources",
    "clarification_source_ids",
    "external_evidence",
    "evidence",
    "evidence_ids",
    "source_uri",
    "source_reference",
    "sources",
}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_lf_sha256(path: Path) -> str:
    """Hash canonical LF repository bytes independent of checkout conversion."""

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def parse_timezone_aware_datetime(
    value: Any,
    location: str,
) -> tuple[datetime | None, list[str]]:
    """Parse an ISO timestamp and reject missing or naive timezone metadata."""

    if not isinstance(value, str):
        return None, [f"{location}: must be an ISO 8601 string"]
    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None, [f"{location}: invalid ISO 8601 datetime"]
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None, [f"{location}: timezone-aware datetime is required"]
    return parsed, []


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
        if (root / PASS2A_DIRECTORY).exists():
            errors.append(f"{PASS2A_DIRECTORY}: Pass 2A requires the exact Pass 1 records")
        if (root / PASS2B_DIRECTORY).exists():
            errors.append(f"{PASS2B_DIRECTORY}: Pass 2B requires the exact Pass 1 records")
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
    errors.extend(validate_pass2a_repository(root, validate_contract))
    errors.extend(validate_pass2b_repository(root, validate_contract))
    errors.extend(validate_residual_clarification_repository(root, validate_contract))
    errors.extend(validate_materialization_architecture(root))
    errors.extend(validate_closure_gap_architecture(root, validate_contract))
    errors.extend(validate_normalization_completion(root, validate_contract))
    return errors


Pass1Key = tuple[str, str]


def pass1_record_path(filename: str) -> str:
    return f"{PASS1_DIRECTORY}/{filename}"


def group_id_for_members(members: list[Pass1Key]) -> str:
    tokens = sorted(f"{source_frame_id}|{source_entry_id}" for source_frame_id, source_entry_id in members)
    digest = hashlib.sha256("\n".join(tokens).encode("utf-8")).hexdigest()[:16]
    return f"ng-{digest}"


def locator_key(value: Any) -> Pass1Key | None:
    if not isinstance(value, dict):
        return None
    source_frame_id = value.get("source_frame_id")
    source_entry_id = value.get("source_entry_id")
    if not isinstance(source_frame_id, str) or not isinstance(source_entry_id, str):
        return None
    return source_frame_id, source_entry_id


def build_pass1_index(root: Path) -> tuple[dict[Pass1Key, dict[str, Any]], dict[str, str], list[str]]:
    index: dict[Pass1Key, dict[str, Any]] = {}
    record_hashes: dict[str, str] = {}
    errors: list[str] = []
    for filename, (_, source_frame_id, _) in EXPECTED_PASS1.items():
        relative = pass1_record_path(filename)
        path = root / relative
        if not path.is_file():
            errors.append(f"{PASS2A_PATH}: required Pass 1 record is missing: {relative}")
            continue
        try:
            record = read_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{PASS2A_PATH}: invalid bound Pass 1 JSON {relative}: {exc}")
            continue
        record_hashes[relative] = canonical_lf_sha256(path)
        if record_hashes[relative] != EXPECTED_PASS1_SHA256[filename]:
            errors.append(f"{PASS2A_PATH}: immutable Pass 1 bytes changed: {relative}")
        for interpretation in record.get("interpretations", []):
            if not isinstance(interpretation, dict):
                continue
            source_entry_id = interpretation.get("source_entry_id")
            if not isinstance(source_entry_id, str):
                continue
            key = source_frame_id, source_entry_id
            if key in index:
                errors.append(f"{PASS2A_PATH}: duplicate Pass 1 identity {key!r}")
                continue
            index[key] = {
                "record_path": relative,
                "record_sha256": record_hashes[relative],
                "minimal_gate_result": interpretation.get("minimal_gate_result"),
                "normalized_substantive_locus": interpretation.get(
                    "normalized_substantive_locus"
                ),
            }
    return index, record_hashes, errors


def validate_bound_pass1_reference(
    reference: Any,
    expected: dict[str, Any],
    location: str,
) -> list[str]:
    if not isinstance(reference, dict):
        return [f"{location}: pass1_record must be an artifact reference"]
    errors: list[str] = []
    if reference.get("path") != expected["record_path"]:
        errors.append(f"{location}: pass1_record path does not match the member identity")
    if reference.get("sha256") != expected["record_sha256"]:
        errors.append(f"{location}: pass1_record SHA-256 mismatch")
    return errors


def validate_group_structure(
    group: Any,
    pass1_index: dict[Pass1Key, dict[str, Any]],
    location: str,
) -> tuple[list[str], list[Pass1Key]]:
    errors: list[str] = []
    if not isinstance(group, dict):
        return [f"{location}: group must be an object"], []
    members = group.get("members", [])
    if not isinstance(members, list):
        return [f"{location}: members must be an array"], []

    member_keys: list[Pass1Key] = []
    for index, member in enumerate(members):
        member_location = f"{location}: members[{index}]"
        key = locator_key(member)
        if key is None:
            errors.append(f"{member_location}: member identity is invalid")
            continue
        member_keys.append(key)
        expected = pass1_index.get(key)
        if expected is None:
            errors.append(f"{member_location}: member does not resolve to Pass 1")
            continue
        errors.extend(
            validate_bound_pass1_reference(member.get("pass1_record"), expected, member_location)
        )
        if expected["minimal_gate_result"] != "passes":
            errors.append(f"{member_location}: only Pass 1 passes may be grouped")
        if member.get("normalized_substantive_locus") != expected[
            "normalized_substantive_locus"
        ]:
            errors.append(f"{member_location}: normalized_substantive_locus mismatch")

    if len(member_keys) != len(set(member_keys)):
        errors.append(f"{location}: a member appears more than once in the group")
    if member_keys:
        expected_id = group_id_for_members(member_keys)
        if group.get("normalization_group_id") != expected_id:
            errors.append(f"{location}: normalization_group_id does not match deterministic hash")
        anchor_key = min(member_keys)
        if locator_key(group.get("deterministic_anchor")) != anchor_key:
            errors.append(f"{location}: deterministic_anchor is not the lexicographic minimum")

    assertions = group.get("pairwise_equivalence_assertions", [])
    if not isinstance(assertions, list):
        assertions = []
    group_kind = group.get("group_kind")
    if group_kind == "singleton":
        if len(member_keys) != 1:
            errors.append(f"{location}: singleton must contain exactly one member")
        if assertions:
            errors.append(f"{location}: singleton must contain zero pairwise assertions")
        if member_keys:
            expected = pass1_index.get(member_keys[0])
            if expected and group.get("group_locus_statement") != expected[
                "normalized_substantive_locus"
            ]:
                errors.append(f"{location}: singleton locus must equal its Pass 1 locus")
    elif group_kind == "coextensive_equivalence":
        if len(member_keys) < 2:
            errors.append(f"{location}: coextensive_equivalence requires at least two members")
        expected_pairs = {
            frozenset((left, right))
            for left, right in itertools.combinations(set(member_keys), 2)
        }
        actual_pairs: list[frozenset[Pass1Key]] = []
        criteria = (
            "same_substantive_locus",
            "equivalent_inclusion_envelope",
            "equivalent_exclusion_envelope",
            "no_material_scope_asymmetry",
            "lens_difference_only",
        )
        for assertion_index, assertion in enumerate(assertions):
            assertion_location = (
                f"{location}: pairwise_equivalence_assertions[{assertion_index}]"
            )
            if not isinstance(assertion, dict):
                errors.append(f"{assertion_location}: assertion must be an object")
                continue
            left = locator_key(assertion.get("left_member"))
            right = locator_key(assertion.get("right_member"))
            if left is None or right is None or left == right:
                errors.append(f"{assertion_location}: assertion pair is invalid")
                continue
            pair = frozenset((left, right))
            actual_pairs.append(pair)
            if left not in set(member_keys) or right not in set(member_keys):
                errors.append(f"{assertion_location}: assertion references a non-member")
            for criterion in criteria:
                if assertion.get(criterion) is not True:
                    errors.append(f"{assertion_location}: {criterion} must be true")
        if len(actual_pairs) != len(set(actual_pairs)):
            errors.append(f"{location}: duplicate unordered pairwise assertion")
        if set(actual_pairs) != expected_pairs:
            errors.append(
                f"{location}: pairwise assertions must form a complete equivalence clique"
            )
    else:
        errors.append(f"{location}: unrecognized group_kind")
    return errors, member_keys


def find_prohibited_pass2a_content(value: Any, location: str) -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if "candidate" in key.lower():
                errors.append(f"{location}: prohibited candidate field {key!r}")
            errors.extend(find_prohibited_pass2a_content(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(find_prohibited_pass2a_content(child, f"{location}[{index}]"))
    elif isinstance(value, str) and "du-cand-" in value.lower():
        errors.append(f"{location}: prohibited Domain candidate identifier")
    return errors


def validate_pass2a_record(
    record: Any,
    pass1_index: dict[Pass1Key, dict[str, Any]],
    record_hashes: dict[str, str],
    location: str = PASS2A_PATH,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{location}: Pass 2A record must be an object"]
    if record.get("pass2a_record_id") != "equivalence-groups-v0.1":
        errors.append(f"{location}: pass2a_record_id mismatch")
    if record.get("instrument_version") != "0.5.0-draft":
        errors.append(f"{location}: instrument_version mismatch")
    if record.get("procedure") != "high_precision_equivalence_grouping":
        errors.append(f"{location}: procedure mismatch")
    if record.get("status") != "complete":
        errors.append(f"{location}: status must be complete")
    errors.extend(find_prohibited_pass2a_content(record, location))

    references = record.get("pass1_records", [])
    if not isinstance(references, list):
        references = []
    reference_paths = [
        reference.get("path")
        for reference in references
        if isinstance(reference, dict)
    ]
    if len(reference_paths) != len(set(reference_paths)):
        errors.append(f"{location}: duplicate Pass 1 artifact binding")
    if set(reference_paths) != set(record_hashes):
        errors.append(f"{location}: must bind the exact four Pass 1 records")
    for reference in references:
        if not isinstance(reference, dict):
            errors.append(f"{location}: pass1_records entry must be an artifact reference")
            continue
        path = reference.get("path")
        if path in record_hashes and reference.get("sha256") != record_hashes[path]:
            errors.append(f"{location}: Pass 1 SHA-256 mismatch for {path}")

    groups = record.get("groups", [])
    if not isinstance(groups, list):
        groups = []
    all_grouped: list[Pass1Key] = []
    group_ids: list[str] = []
    group_for_member: dict[Pass1Key, tuple[str, str]] = {}
    for index, group in enumerate(groups):
        group_location = f"{location}: groups[{index}]"
        group_errors, member_keys = validate_group_structure(
            group, pass1_index, group_location
        )
        errors.extend(group_errors)
        all_grouped.extend(member_keys)
        if isinstance(group, dict):
            group_id = group.get("normalization_group_id")
            if isinstance(group_id, str):
                group_ids.append(group_id)
            for key in member_keys:
                group_for_member[key] = (str(group_id), str(group.get("group_kind")))
    if len(group_ids) != len(set(group_ids)):
        errors.append(f"{location}: duplicate normalization_group_id")

    expected_passes = {
        key
        for key, value in pass1_index.items()
        if value.get("minimal_gate_result") == "passes"
    }
    if len(all_grouped) != len(set(all_grouped)):
        errors.append(f"{location}: a passed interpretation appears in multiple groups")
    grouped_set = set(all_grouped)
    if grouped_set != expected_passes:
        missing = sorted(expected_passes - grouped_set)
        extra = sorted(grouped_set - expected_passes)
        errors.append(
            f"{location}: groups must partition every Pass 1 pass exactly once; "
            f"missing={missing}, extra={extra}"
        )
    if len(all_grouped) != 322:
        errors.append(f"{location}: expected exactly 322 grouped members")

    excluded = record.get("excluded_from_grouping", [])
    if not isinstance(excluded, list):
        excluded = []
    excluded_keys: list[Pass1Key] = []
    for index, item in enumerate(excluded):
        item_location = f"{location}: excluded_from_grouping[{index}]"
        key = locator_key(item)
        if key is None:
            errors.append(f"{item_location}: excluded identity is invalid")
            continue
        excluded_keys.append(key)
        expected = pass1_index.get(key)
        if expected is None:
            errors.append(f"{item_location}: excluded identity does not resolve to Pass 1")
            continue
        errors.extend(
            validate_bound_pass1_reference(item.get("pass1_record"), expected, item_location)
        )
        result = expected.get("minimal_gate_result")
        expected_reason = {
            "unresolved": "pass1_unresolved",
            "fails_out_of_scope": "pass1_fails_out_of_scope",
        }.get(result)
        if expected_reason is None:
            errors.append(f"{item_location}: a Pass 1 pass cannot be excluded")
        elif item.get("reason") != expected_reason:
            errors.append(f"{item_location}: exclusion reason does not match Pass 1")
    expected_excluded = set(pass1_index) - expected_passes
    if len(excluded_keys) != len(set(excluded_keys)):
        errors.append(f"{location}: duplicate excluded Pass 1 identity")
    if set(excluded_keys) != expected_excluded:
        errors.append(f"{location}: excluded entries must account for every non-pass exactly once")
    if len(excluded_keys) != 8 or set(excluded_keys) != EXPECTED_UNRESOLVED:
        errors.append(f"{location}: expected exactly the eight unresolved IPC A99-H99 entries")

    deferred = record.get("deferred_equivalence_questions", [])
    if not isinstance(deferred, list):
        deferred = []
    deferred_pairs: list[frozenset[Pass1Key]] = []
    for index, item in enumerate(deferred):
        item_location = f"{location}: deferred_equivalence_questions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_location}: deferred question must be an object")
            continue
        left = locator_key(item.get("left_member"))
        right = locator_key(item.get("right_member"))
        if left is None or right is None or left == right:
            errors.append(f"{item_location}: deferred pair is invalid")
            continue
        pair = frozenset((left, right))
        deferred_pairs.append(pair)
        for key in (left, right):
            if key not in expected_passes:
                errors.append(f"{item_location}: deferred member must resolve to a Pass 1 pass")
        left_group = group_for_member.get(left)
        right_group = group_for_member.get(right)
        if (
            left_group is not None
            and left_group == right_group
            and left_group[1] == "coextensive_equivalence"
        ):
            errors.append(f"{item_location}: deferred pair is already merged")
    if len(deferred_pairs) != len(set(deferred_pairs)):
        errors.append(f"{location}: duplicate deferred equivalence pair")
    return errors


def validate_pass2a_repository(
    root: Path,
    validate_contract: Callable[[Any, Any, str], list[str]],
) -> list[str]:
    directory = root / PASS2A_DIRECTORY
    if not directory.exists():
        return []
    errors: list[str] = []
    files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    expected_file = root / PASS2A_PATH
    if files != [expected_file]:
        errors.append(f"{PASS2A_DIRECTORY}: expected exactly equivalence-groups-v0.1.json")
    if not expected_file.is_file():
        return errors

    schema_path = root / PASS2A_SCHEMA_PATH
    if not schema_path.is_file():
        return errors + [f"{PASS2A_SCHEMA_PATH}: required when Pass 2A exists"]
    try:
        schema = read_json(schema_path)
        record = read_json(expected_file)
    except json.JSONDecodeError as exc:
        return errors + [f"{PASS2A_PATH}: invalid JSON: {exc}"]
    if schema.get("x-instrument-version") != "0.5.0-draft":
        errors.append(f"{PASS2A_SCHEMA_PATH}: x-instrument-version mismatch")
    errors.extend(find_prohibited_pass2a_content(schema, PASS2A_SCHEMA_PATH))
    errors.extend(validate_contract(record, schema, PASS2A_PATH))

    _, artifact_errors = validate_artifact(
        root,
        record.get("normalization_codebook"),
        CODEBOOK_PATH,
        f"{PASS2A_PATH}: normalization_codebook",
    )
    errors.extend(artifact_errors)
    _, artifact_errors = validate_artifact(
        root,
        record.get("universe_boundary"),
        BOUNDARY_PATH,
        f"{PASS2A_PATH}: universe_boundary",
    )
    errors.extend(artifact_errors)

    pass1_index, record_hashes, index_errors = build_pass1_index(root)
    errors.extend(index_errors)
    errors.extend(validate_pass2a_record(record, pass1_index, record_hashes))
    return errors


def pass2a_group_index(record: Any) -> dict[Pass1Key, tuple[str, str]]:
    """Map every Pass 2A member to its immutable group identity and kind."""

    result: dict[Pass1Key, tuple[str, str]] = {}
    if not isinstance(record, dict):
        return result
    for group in record.get("groups", []):
        if not isinstance(group, dict):
            continue
        group_id = group.get("normalization_group_id")
        group_kind = group.get("group_kind")
        for member in group.get("members", []):
            key = locator_key(member)
            if key is not None and isinstance(group_id, str) and isinstance(group_kind, str):
                result[key] = group_id, group_kind
    return result


def find_prohibited_pass2b_content(value: Any, location: str) -> list[str]:
    """Reject candidate identifiers without rejecting the permission status field."""

    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            errors.extend(find_prohibited_pass2b_content(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(find_prohibited_pass2b_content(child, f"{location}[{index}]"))
    elif isinstance(value, str) and "du-cand-" in value.lower():
        errors.append(f"{location}: prohibited Domain candidate identifier")
    return errors


def validate_pass2b_outcome(adjudication: Any, location: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(adjudication, dict):
        return [f"{location}: adjudication must be an object"]
    criteria = adjudication.get("criteria")
    if not isinstance(criteria, dict):
        return [f"{location}: criteria must be an object"]
    values: list[bool | None] = []
    for criterion in PASS2B_CRITERIA:
        value = criteria.get(criterion)
        if value is not True and value is not False and value is not None:
            errors.append(f"{location}: {criterion} must be true, false, or null")
        values.append(value)
    outcome = adjudication.get("outcome")
    if outcome == "coextensive":
        if not all(value is True for value in values):
            errors.append(f"{location}: coextensive requires all five criteria true")
    elif outcome == "not_coextensive_for_normalization":
        if not any(value is False for value in values):
            errors.append(
                f"{location}: not_coextensive_for_normalization requires a false criterion"
            )
    elif outcome == "unresolved":
        if any(value is False for value in values) or not any(value is None for value in values):
            errors.append(
                f"{location}: unresolved requires no false criterion and at least one null"
            )
    else:
        errors.append(f"{location}: unrecognized outcome")
    return errors


def validate_pass2b_record(
    record: Any,
    pass1_index: dict[Pass1Key, dict[str, Any]],
    record_hashes: dict[str, str],
    pass2a_record: Any,
    pass2a_sha256: str,
    location: str = PASS2B_PATH,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{location}: Pass 2B record must be an object"]
    if record.get("pass2b_record_id") != "deferred-equivalence-adjudication-v0.1":
        errors.append(f"{location}: pass2b_record_id mismatch")
    if record.get("instrument_version") != "0.5.0-draft":
        errors.append(f"{location}: instrument_version mismatch")
    if record.get("procedure") != "deferred_equivalence_adjudication":
        errors.append(f"{location}: procedure mismatch")
    if record.get("status") != "complete":
        errors.append(f"{location}: status must be complete")
    errors.extend(find_prohibited_pass2b_content(record, location))

    if pass2a_sha256 != EXPECTED_PASS2A_SHA256:
        errors.append(f"{location}: immutable Pass 2A bytes changed")
    pass2a_reference = record.get("pass2a_record")
    if not isinstance(pass2a_reference, dict):
        errors.append(f"{location}: pass2a_record must be an artifact reference")
    else:
        if pass2a_reference.get("path") != PASS2A_PATH:
            errors.append(f"{location}: pass2a_record path mismatch")
        if pass2a_reference.get("sha256") != pass2a_sha256:
            errors.append(f"{location}: Pass 2A SHA-256 mismatch")

    relevant_paths = {
        pass1_record_path("oecd-ford-frascati-2015-pass1.json"),
        pass1_record_path("un-isic-rev5-pass1.json"),
    }
    references = record.get("pass1_records", [])
    if not isinstance(references, list):
        references = []
    paths = [item.get("path") for item in references if isinstance(item, dict)]
    if len(paths) != len(set(paths)) or set(paths) != relevant_paths:
        errors.append(f"{location}: must bind exactly the relevant FORD and ISIC Pass 1 records")
    for reference in references:
        if not isinstance(reference, dict):
            errors.append(f"{location}: pass1_records entry must be an artifact reference")
            continue
        path = reference.get("path")
        if path in relevant_paths and reference.get("sha256") != record_hashes.get(path):
            errors.append(f"{location}: Pass 1 SHA-256 mismatch for {path}")

    sources = record.get("clarification_sources", [])
    if not isinstance(sources, list):
        sources = []
    sources_by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        source_location = f"{location}: clarification_sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{source_location}: clarification source must be an object")
            continue
        source_id = source.get("clarification_source_id")
        if not isinstance(source_id, str) or source_id in sources_by_id:
            errors.append(f"{source_location}: clarification_source_id is invalid or duplicate")
            continue
        sources_by_id[source_id] = source
        expected_source = EXPECTED_PASS2B_SOURCES.get(source_id)
        if expected_source is None:
            errors.append(f"{source_location}: clarification source is outside permitted lineage")
            continue
        for field in ("source_frame_id", "source_uri", "sha256"):
            if source.get(field) != expected_source[field]:
                errors.append(f"{source_location}: {field} does not match official provenance")
    if set(sources_by_id) != set(EXPECTED_PASS2B_SOURCES):
        errors.append(f"{location}: exact two official clarification sources are required")

    group_index = pass2a_group_index(pass2a_record)
    deferred = pass2a_record.get("deferred_equivalence_questions", []) if isinstance(
        pass2a_record, dict
    ) else []
    deferred_pairs = {
        frozenset((left, right))
        for item in deferred
        if isinstance(item, dict)
        for left, right in [(locator_key(item.get("left_member")), locator_key(item.get("right_member")))]
        if left is not None and right is not None and left != right
    }
    expected_pairs = {
        frozenset(((left[0], left[1]), (right[0], right[1])))
        for left, right in EXPECTED_PASS2B_ADJUDICATIONS.values()
    }
    if deferred_pairs != expected_pairs:
        errors.append(f"{location}: merged Pass 2A does not contain the exact deferred pairs")

    adjudications = record.get("adjudications", [])
    if not isinstance(adjudications, list):
        adjudications = []
    ids: list[str] = []
    actual_pairs: list[frozenset[Pass1Key]] = []
    outcomes: list[str] = []
    for index, adjudication in enumerate(adjudications):
        item_location = f"{location}: adjudications[{index}]"
        if not isinstance(adjudication, dict):
            errors.append(f"{item_location}: adjudication must be an object")
            continue
        adjudication_id = adjudication.get("adjudication_id")
        if isinstance(adjudication_id, str):
            ids.append(adjudication_id)
        expected_pair = EXPECTED_PASS2B_ADJUDICATIONS.get(str(adjudication_id))
        left = locator_key(adjudication.get("left_member"))
        right = locator_key(adjudication.get("right_member"))
        if left is None or right is None or left == right:
            errors.append(f"{item_location}: member pair is invalid")
            continue
        pair = frozenset((left, right))
        actual_pairs.append(pair)
        if expected_pair is None or pair != frozenset(
            ((expected_pair[0][0], expected_pair[0][1]), (expected_pair[1][0], expected_pair[1][1]))
        ):
            errors.append(f"{item_location}: adjudication ID and deferred pair mismatch")

        for side, key, envelope_field in (
            ("left", left, "left_envelope"),
            ("right", right, "right_envelope"),
        ):
            member = adjudication.get(f"{side}_member")
            member_location = f"{item_location}: {side}_member"
            expected_member = pass1_index.get(key)
            if expected_member is None:
                errors.append(f"{member_location}: member does not resolve to Pass 1")
                continue
            if expected_member.get("minimal_gate_result") != "passes":
                errors.append(f"{member_location}: member must be a Pass 1 pass")
            errors.extend(
                validate_bound_pass1_reference(
                    member.get("pass1_record") if isinstance(member, dict) else None,
                    expected_member,
                    member_location,
                )
            )
            actual_group = group_index.get(key)
            if actual_group is None or actual_group[1] != "singleton":
                errors.append(f"{member_location}: member must resolve to a Pass 2A singleton")
            elif not isinstance(member, dict) or member.get("pass2a_group_id") != actual_group[0]:
                errors.append(f"{member_location}: pass2a_group_id mismatch")
            envelope = adjudication.get(envelope_field)
            if not isinstance(envelope, dict):
                errors.append(f"{item_location}: {envelope_field} must be an object")
                continue
            if envelope.get("substantive_locus") != expected_member.get(
                "normalized_substantive_locus"
            ):
                errors.append(f"{item_location}: {envelope_field} changes the Pass 1 locus")
            evidence_ids = envelope.get("evidence_source_ids", [])
            if not isinstance(evidence_ids, list) or not evidence_ids:
                errors.append(f"{item_location}: {envelope_field} requires evidence sources")
                continue
            for source_id in evidence_ids:
                source = sources_by_id.get(source_id)
                if source is None:
                    errors.append(f"{item_location}: unresolved clarification source {source_id!r}")
                elif source.get("source_frame_id") != key[0]:
                    errors.append(
                        f"{item_location}: {envelope_field} uses another classification lineage"
                    )
        errors.extend(validate_pass2b_outcome(adjudication, item_location))
        outcome = adjudication.get("outcome")
        if isinstance(outcome, str):
            outcomes.append(outcome)

    if len(ids) != len(set(ids)) or set(ids) != set(EXPECTED_PASS2B_ADJUDICATIONS):
        errors.append(f"{location}: exactly the two required adjudication IDs are required")
    if len(actual_pairs) != len(set(actual_pairs)) or set(actual_pairs) != expected_pairs:
        errors.append(f"{location}: adjudications must exactly close the two deferred pairs")

    all_closed = len(outcomes) == 2 and all(outcome != "unresolved" for outcome in outcomes)
    revision_required = len(outcomes) == 2 and any(outcome == "coextensive" for outcome in outcomes)
    materialization_permitted = all_closed and not revision_required
    for field, expected in (
        ("all_deferred_questions_closed", all_closed),
        ("grouping_revision_required", revision_required),
        ("candidate_materialization_permitted", materialization_permitted),
    ):
        if record.get(field) is not expected:
            errors.append(f"{location}: {field} does not match adjudication outcomes")
    return errors


def validate_pass2b_repository(
    root: Path,
    validate_contract: Callable[[Any, Any, str], list[str]],
) -> list[str]:
    directory = root / PASS2B_DIRECTORY
    if not directory.exists():
        return []
    errors: list[str] = []
    files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    expected_file = root / PASS2B_PATH
    if files != [expected_file]:
        errors.append(
            f"{PASS2B_DIRECTORY}: expected exactly deferred-equivalence-adjudication-v0.1.json"
        )
    if not expected_file.is_file():
        return errors
    schema_path = root / PASS2B_SCHEMA_PATH
    if not schema_path.is_file():
        return errors + [f"{PASS2B_SCHEMA_PATH}: required when Pass 2B exists"]
    pass2a_path = root / PASS2A_PATH
    if not pass2a_path.is_file():
        return errors + [f"{PASS2B_PATH}: exact Pass 2A record is required"]
    try:
        schema = read_json(schema_path)
        record = read_json(expected_file)
        pass2a_record = read_json(pass2a_path)
    except json.JSONDecodeError as exc:
        return errors + [f"{PASS2B_PATH}: invalid JSON dependency: {exc}"]
    if schema.get("x-instrument-version") != "0.5.0-draft":
        errors.append(f"{PASS2B_SCHEMA_PATH}: x-instrument-version mismatch")
    errors.extend(find_prohibited_pass2b_content(schema, PASS2B_SCHEMA_PATH))
    errors.extend(validate_contract(record, schema, PASS2B_PATH))
    for field, expected_path in (
        ("normalization_codebook", CODEBOOK_PATH),
        ("universe_boundary", BOUNDARY_PATH),
    ):
        _, artifact_errors = validate_artifact(
            root, record.get(field), expected_path, f"{PASS2B_PATH}: {field}"
        )
        errors.extend(artifact_errors)
    pass1_index, record_hashes, index_errors = build_pass1_index(root)
    errors.extend(index_errors)
    errors.extend(
        validate_pass2b_record(
            record,
            pass1_index,
            record_hashes,
            pass2a_record,
            canonical_lf_sha256(pass2a_path),
        )
    )
    candidate_files = list((root / "domain-universe/candidates").glob("*.json"))
    if candidate_files:
        errors.append(f"{PASS2B_PATH}: Pass 2B requires zero Domain candidate records")
    return errors


def find_prohibited_residual_content(value: Any, location: str) -> list[str]:
    """Keep the successor clarification independent of grouping and candidates."""

    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in PROHIBITED_RESIDUAL_FIELDS:
                errors.append(f"{location}: prohibited residual-clarification field {key!r}")
            errors.extend(
                find_prohibited_residual_content(child, f"{location}.{key}")
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(
                find_prohibited_residual_content(child, f"{location}[{index}]")
            )
    elif isinstance(value, str) and re.search(
        r"\bdu-cand-[0-9]{4}\b", value, re.IGNORECASE
    ):
        errors.append(f"{location}: prohibited Domain candidate identifier")
    return errors


def validate_residual_clarification_record(
    record: Any,
    pass1_index: dict[Pass1Key, dict[str, Any]],
    pass2a_record: Any,
    location: str = RESIDUAL_PATH,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{location}: residual clarification must be an object"]
    if record.get("residual_clarification_id") != "ipc-residual-clarification-v0.1":
        errors.append(f"{location}: residual_clarification_id mismatch")
    if record.get("instrument_version") != "0.5.0-draft":
        errors.append(f"{location}: instrument_version mismatch")
    if record.get("procedure") != "independent_ipc_residual_clarification":
        errors.append(f"{location}: procedure mismatch")
    if record.get("status") != "complete":
        errors.append(f"{location}: status must be complete")
    errors.extend(find_prohibited_residual_content(record, location))

    expected_bindings = {
        "normalization_codebook": (CODEBOOK_PATH, EXPECTED_CODEBOOK_SHA256),
        "universe_boundary": (BOUNDARY_PATH, EXPECTED_BOUNDARY_SHA256),
        "source_extraction": (
            "domain-universe/extractions/wipo-ipc-2026-01-class.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/wipo-ipc-2026-01-class.json"
            ],
        ),
        "original_pass1_record": (
            pass1_record_path("wipo-ipc-2026-01-pass1.json"),
            EXPECTED_PASS1_SHA256["wipo-ipc-2026-01-pass1.json"],
        ),
        "pass2a_record": (PASS2A_PATH, EXPECTED_PASS2A_SHA256),
    }
    for field, (expected_path, expected_sha256) in expected_bindings.items():
        reference = record.get(field)
        if not isinstance(reference, dict):
            errors.append(f"{location}: {field} must be an artifact reference")
            continue
        if reference.get("path") != expected_path:
            errors.append(f"{location}: {field} path must bind exact historical artifact")
        if reference.get("sha256") != expected_sha256:
            errors.append(f"{location}: {field} SHA-256 must bind exact historical bytes")

    grouped: set[Pass1Key] = set()
    excluded: set[Pass1Key] = set()
    if not isinstance(pass2a_record, dict):
        errors.append(f"{location}: exact Pass 2A record is invalid")
    else:
        for group in pass2a_record.get("groups", []):
            if not isinstance(group, dict):
                continue
            for member in group.get("members", []):
                key = locator_key(member)
                if key is not None:
                    grouped.add(key)
        for item in pass2a_record.get("excluded_from_grouping", []):
            key = locator_key(item)
            if key is not None:
                excluded.add(key)

    sources = record.get("clarification_sources", [])
    if not isinstance(sources, list):
        sources = []
    sources_by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        source_location = f"{location}: clarification_sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{source_location}: source must be an object")
            continue
        source_id = source.get("clarification_source_id")
        if not isinstance(source_id, str):
            errors.append(f"{source_location}: clarification_source_id is invalid")
            continue
        if source_id in sources_by_id:
            errors.append(f"{source_location}: duplicate clarification_source_id")
        sources_by_id[source_id] = source
        expected = EXPECTED_RESIDUAL_SOURCES.get(source_id)
        if expected is None:
            errors.append(f"{source_location}: source is outside the WIPO IPC lineage")
            continue
        for field in ("source_frame_id", "source_uri", "sha256"):
            if source.get(field) != expected[field]:
                errors.append(f"{source_location}: {field} does not match official source")
    if set(sources_by_id) != set(EXPECTED_RESIDUAL_SOURCES):
        errors.append(f"{location}: exactly the two required WIPO sources are required")

    assessments = record.get("assessments", [])
    if not isinstance(assessments, list):
        assessments = []
    assessment_ids: list[str] = []
    assessed_keys: list[Pass1Key] = []
    results: list[str] = []
    expected_source_ids = set(EXPECTED_RESIDUAL_SOURCES)
    official_title = "SUBJECT MATTER NOT OTHERWISE PROVIDED FOR IN THIS SECTION"

    for index, assessment in enumerate(assessments):
        item_location = f"{location}: assessments[{index}]"
        if not isinstance(assessment, dict):
            errors.append(f"{item_location}: assessment must be an object")
            continue
        assessment_id = assessment.get("assessment_id")
        if isinstance(assessment_id, str):
            assessment_ids.append(assessment_id)
        key = locator_key(assessment)
        if key is None:
            errors.append(f"{item_location}: source-entry identity is invalid")
            continue
        assessed_keys.append(key)
        source_frame_id, source_entry_id = key
        match = re.fullmatch(r"ipc-([A-H])99", source_entry_id)
        if source_frame_id != "wipo-ipc-2026-01" or match is None:
            errors.append(f"{item_location}: only exact IPC A99-H99 residuals may be assessed")
            continue
        section = match.group(1)
        expected_id = f"ipc-{section}99-residual-clarification"
        if assessment_id != expected_id:
            errors.append(f"{item_location}: assessment_id does not match source entry")
        expected_pass1 = pass1_index.get(key)
        if expected_pass1 is None:
            errors.append(f"{item_location}: source entry does not resolve to Pass 1")
        elif expected_pass1.get("minimal_gate_result") != "unresolved":
            errors.append(f"{item_location}: source entry was not unresolved in Pass 1")
        if key not in excluded:
            errors.append(f"{item_location}: source entry is not Pass 2A excluded_from_grouping")
        if key in grouped:
            errors.append(f"{item_location}: a Pass 2A grouped member cannot be reassessed here")

        expected_symbols = {
            "section_symbol": section,
            "section_title": EXPECTED_RESIDUAL_SECTIONS[section],
            "class_symbol": f"{section}99",
            "subclass_symbol": f"{section}99Z",
            "main_group_symbol": f"{section}99Z 99/00",
            "official_residual_title": official_title,
        }
        for field, expected in expected_symbols.items():
            if assessment.get(field) != expected:
                errors.append(f"{item_location}: {field} does not match IPC 2026.01")

        source_ids = assessment.get("clarification_source_ids", [])
        if not isinstance(source_ids, list) or set(source_ids) != expected_source_ids:
            errors.append(f"{item_location}: both exact WIPO clarification sources are required")
        elif len(source_ids) != len(set(source_ids)):
            errors.append(f"{item_location}: duplicate clarification source reference")

        gate = assessment.get("gate")
        if not isinstance(gate, dict):
            errors.append(f"{item_location}: gate must be an object")
            continue
        values = tuple(gate.get(field) for field in RESIDUAL_GATE_FIELDS)
        if any(value not in (True, False, None) for value in values):
            errors.append(f"{item_location}: gate values must be true, false, or null")
            continue
        if values == (True, True, True):
            expected_result = "passes"
        elif values == (True, True, False):
            expected_result = "fails_out_of_scope"
        else:
            expected_result = "unresolved"
        result = assessment.get("minimal_gate_result")
        if result != expected_result:
            errors.append(
                f"{item_location}: minimal_gate_result does not match exact three-gate logic"
            )
        if isinstance(result, str):
            results.append(result)
        locus = assessment.get("normalized_substantive_locus")
        if result == "passes" and (not isinstance(locus, str) or not locus.strip()):
            errors.append(f"{item_location}: passes requires a non-empty normalized locus")

    expected_ids = {
        f"ipc-{section}99-residual-clarification" for section in "ABCDEFGH"
    }
    if len(assessment_ids) != len(set(assessment_ids)) or set(assessment_ids) != expected_ids:
        errors.append(f"{location}: exactly the eight required assessment IDs are required")
    if len(assessed_keys) != len(set(assessed_keys)) or set(assessed_keys) != EXPECTED_UNRESOLVED:
        errors.append(f"{location}: assessments must exactly cover IPC A99-H99 once")

    counts = {
        result: sum(value == result for value in results)
        for result in ("passes", "fails_out_of_scope", "unresolved")
    }
    aggregate = record.get("aggregate")
    if not isinstance(aggregate, dict):
        errors.append(f"{location}: aggregate must be an object")
    else:
        expected_aggregate = {
            "assessed_residuals": len(results),
            **counts,
            "all_residual_questions_closed": counts["unresolved"] == 0,
            "successor_grouping_required": counts["passes"] > 0,
            "stable_candidate_id_gate_reassessment_ready": counts["unresolved"] == 0,
        }
        for field, expected in expected_aggregate.items():
            if aggregate.get(field) != expected:
                errors.append(f"{location}: aggregate {field} does not match assessments")
    return errors


def validate_residual_clarification_repository(
    root: Path,
    validate_contract: Callable[[Any, Any, str], list[str]],
) -> list[str]:
    directory = root / RESIDUAL_DIRECTORY
    if not directory.exists():
        return []
    errors: list[str] = []
    files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    expected_file = root / RESIDUAL_PATH
    if files != [expected_file]:
        errors.append(
            f"{RESIDUAL_DIRECTORY}: expected exactly ipc-residual-clarification-v0.1.json"
        )
    if not expected_file.is_file():
        return errors
    schema_path = root / RESIDUAL_SCHEMA_PATH
    if not schema_path.is_file():
        return errors + [f"{RESIDUAL_SCHEMA_PATH}: required when Task 105D1 exists"]
    pass2a_path = root / PASS2A_PATH
    if not pass2a_path.is_file():
        return errors + [f"{RESIDUAL_PATH}: exact Pass 2A record is required"]
    try:
        schema = read_json(schema_path)
        record = read_json(expected_file)
        pass2a_record = read_json(pass2a_path)
    except json.JSONDecodeError as exc:
        return errors + [f"{RESIDUAL_PATH}: invalid JSON dependency: {exc}"]
    if schema.get("x-instrument-version") != "0.5.0-draft":
        errors.append(f"{RESIDUAL_SCHEMA_PATH}: x-instrument-version mismatch")
    errors.extend(find_prohibited_residual_content(schema, RESIDUAL_SCHEMA_PATH))
    errors.extend(validate_contract(record, schema, RESIDUAL_PATH))

    bindings = {
        "normalization_codebook": CODEBOOK_PATH,
        "universe_boundary": BOUNDARY_PATH,
        "source_extraction": (
            "domain-universe/extractions/wipo-ipc-2026-01-class.json"
        ),
        "original_pass1_record": pass1_record_path(
            "wipo-ipc-2026-01-pass1.json"
        ),
        "pass2a_record": PASS2A_PATH,
    }
    for field, expected_path in bindings.items():
        _, artifact_errors = validate_artifact(
            root, record.get(field), expected_path, f"{RESIDUAL_PATH}: {field}"
        )
        errors.extend(artifact_errors)

    pass1_index, _, index_errors = build_pass1_index(root)
    errors.extend(index_errors)
    errors.extend(
        validate_residual_clarification_record(
            record, pass1_index, pass2a_record, RESIDUAL_PATH
        )
    )
    return errors


def validate_fixed_bytes(
    root: Path,
    relative: str,
    expected_sha256: str,
    label: str,
) -> list[str]:
    path = root / relative
    if not path.is_file():
        return [f"{label}: immutable artifact is missing: {relative}"]
    if canonical_lf_sha256(path) != expected_sha256:
        return [f"{label}: immutable bytes changed: {relative}"]
    return []


def schema_const_reference(
    schema: dict[str, Any],
    definition: str,
) -> tuple[str | None, str | None]:
    definitions = schema.get("$defs", {})
    if not isinstance(definitions, dict):
        return None, None
    value = definitions.get(definition, {})
    if not isinstance(value, dict):
        return None, None
    properties = value.get("properties")
    if not isinstance(properties, dict):
        all_of = value.get("allOf", [])
        for item in all_of if isinstance(all_of, list) else []:
            if isinstance(item, dict) and isinstance(item.get("properties"), dict):
                properties = item["properties"]
                break
    if not isinstance(properties, dict):
        return None, None
    path_schema = properties.get("path")
    sha_schema = properties.get("sha256")
    path = path_schema.get("const") if isinstance(path_schema, dict) else None
    digest = sha_schema.get("const") if isinstance(sha_schema, dict) else None
    return path, digest


def find_prohibited_closure_content(value: Any, location: str) -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for field, item in value.items():
            field_location = f"{location}.{field}"
            if field in PROHIBITED_CLOSURE_FIELDS:
                errors.append(f"{field_location}: prohibited closure-application field")
            errors.extend(find_prohibited_closure_content(item, field_location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(find_prohibited_closure_content(item, f"{location}[{index}]"))
    return errors


def validate_closure_gap_architecture(
    root: Path,
    validate_contract: Callable[[Any, Any, str], list[str]],
) -> list[str]:
    """Validate the fixed D2 contract and its exact first D3 application."""

    errors: list[str] = []
    errors.extend(
        validate_fixed_bytes(
            root,
            CLOSURE_AMENDMENT_PATH,
            EXPECTED_CLOSURE_AMENDMENT_SHA256,
            "normalization closure gap amendment",
        )
    )
    errors.extend(
        validate_fixed_bytes(
            root,
            CLOSURE_SCHEMA_PATH,
            EXPECTED_CLOSURE_SCHEMA_SHA256,
            "Task 105D2 closure-decision schema",
        )
    )
    amendment_path = root / CLOSURE_AMENDMENT_PATH
    if amendment_path.is_file():
        amendment = amendment_path.read_text(encoding="utf-8")
        required_lines = (
            "# Normalization Closure Gap Amendment",
            "- Version: v0.1",
            "- Status: POST-D1 VERSIONED AMENDMENT; FIXED BEFORE APPLICATION; "
            "NOT SCIENTIFICALLY APPROVED",
            "- Effective Wave: none",
            "This successor amendment was introduced after Task 105D1 revealed a "
            "normalization state not representable by Codebook v0.1. It is fixed "
            "before any source entry is reclassified under the new rule.",
            "Post-observation rule development must be versioned and separated "
            "from its subsequent application.",
            "Non-materializable at the registered extraction granularity is not "
            "out-of-scope in the underlying world.",
            "Broad is not the same as non-materializable.",
            "Terminal for this source-entry granularity does not mean terminal "
            "for the underlying subject matter.",
        )
        for required in required_lines:
            if required not in amendment:
                errors.append(
                    f"{CLOSURE_AMENDMENT_PATH}: missing fixed disclosure {required!r}"
                )

    schema_path = root / CLOSURE_SCHEMA_PATH
    schema: dict[str, Any] = {}
    if not schema_path.is_file():
        errors.append(f"{CLOSURE_SCHEMA_PATH}: frozen closure schema is required")
    else:
        try:
            value = read_json(schema_path)
            if isinstance(value, dict):
                schema = value
            else:
                errors.append(f"{CLOSURE_SCHEMA_PATH}: schema must be an object")
        except json.JSONDecodeError as exc:
            errors.append(f"{CLOSURE_SCHEMA_PATH}: invalid JSON: {exc}")

    if schema:
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{CLOSURE_SCHEMA_PATH}: Draft 2020-12 is required")
        if schema.get("x-instrument-version") != "0.5.0-draft":
            errors.append(f"{CLOSURE_SCHEMA_PATH}: x-instrument-version mismatch")
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        if properties.get("procedure") != {"const": "successor_normalization_closure"}:
            errors.append(f"{CLOSURE_SCHEMA_PATH}: procedure must be fixed")
        if properties.get("status") != {"const": "complete"}:
            errors.append(f"{CLOSURE_SCHEMA_PATH}: status must be fixed")
        expected_bindings = {
            "closure_amendment": (
                CLOSURE_AMENDMENT_PATH,
                EXPECTED_CLOSURE_AMENDMENT_SHA256,
            ),
            "normalization_codebook": (CODEBOOK_PATH, EXPECTED_CODEBOOK_SHA256),
        }
        for definition, expected in expected_bindings.items():
            if schema_const_reference(schema, definition) != expected:
                errors.append(
                    f"{CLOSURE_SCHEMA_PATH}: {definition} must bind exact immutable bytes"
                )
        definitions = schema.get("$defs", {})
        decision = definitions.get("decision", {}) if isinstance(definitions, dict) else {}
        decision_properties = (
            decision.get("properties", {}) if isinstance(decision, dict) else {}
        )
        disposition = (
            decision_properties.get("final_normalization_disposition", {})
            if isinstance(decision_properties, dict)
            else {}
        )
        if not isinstance(disposition, dict) or disposition.get("enum") != [
            "excluded_non_materializable",
            "unresolved",
        ]:
            errors.append(
                f"{CLOSURE_SCHEMA_PATH}: exact successor disposition enum is required"
            )

    validator_path = root / "scripts/validate.py"
    if validator_path.is_file():
        validator_source = validator_path.read_text(encoding="utf-8")
        domain_paths_start = validator_source.find("DOMAIN_SCHEMA_PATHS = {")
        domain_paths_end = validator_source.find("\n}", domain_paths_start)
        if (
            domain_paths_start < 0
            or domain_paths_end < 0
            or Path(CLOSURE_SCHEMA_PATH).name
            in validator_source[domain_paths_start:domain_paths_end]
        ):
            errors.append(
                f"{CLOSURE_SCHEMA_PATH}: successor schema must not enter DOMAIN_SCHEMA_PATHS"
            )

    closure_directory = root / CLOSURE_DIRECTORY
    closure_files = (
        sorted(closure_directory.rglob("*.json"))
        if closure_directory.exists()
        else []
    )
    expected_file = root / CLOSURE_PATH
    if closure_files != [expected_file]:
        errors.append(
            f"{CLOSURE_DIRECTORY}: expected exactly ipc-residual-closure-v0.1.json"
        )

    record: dict[str, Any] = {}
    d1_record: dict[str, Any] = {}
    if expected_file.is_file():
        try:
            value = read_json(expected_file)
            if isinstance(value, dict):
                record = value
            else:
                errors.append(f"{CLOSURE_PATH}: closure record must be an object")
        except json.JSONDecodeError as exc:
            errors.append(f"{CLOSURE_PATH}: invalid JSON: {exc}")
    if (root / RESIDUAL_PATH).is_file():
        try:
            value = read_json(root / RESIDUAL_PATH)
            if isinstance(value, dict):
                d1_record = value
        except json.JSONDecodeError as exc:
            errors.append(f"{RESIDUAL_PATH}: invalid JSON: {exc}")

    if record and schema:
        errors.extend(validate_contract(record, schema, CLOSURE_PATH))
    if record:
        if record.get("normalization_closure_decision_id") != "ipc-residual-closure-v0.1":
            errors.append(f"{CLOSURE_PATH}: normalization_closure_decision_id mismatch")
        if record.get("instrument_version") != "0.5.0-draft":
            errors.append(f"{CLOSURE_PATH}: instrument_version mismatch")
        if record.get("procedure") != "successor_normalization_closure":
            errors.append(f"{CLOSURE_PATH}: procedure mismatch")
        if record.get("status") != "complete":
            errors.append(f"{CLOSURE_PATH}: status must be complete")
        for field, expected_path in (
            ("closure_amendment", CLOSURE_AMENDMENT_PATH),
            ("normalization_codebook", CODEBOOK_PATH),
            ("predecessor_record", RESIDUAL_PATH),
        ):
            _, artifact_errors = validate_artifact(
                root, record.get(field), expected_path, f"{CLOSURE_PATH}: {field}"
            )
            errors.extend(artifact_errors)
        errors.extend(find_prohibited_closure_content(record, CLOSURE_PATH))

        d1_assessments = d1_record.get("assessments", [])
        d1_by_id = {
            item.get("assessment_id"): item
            for item in d1_assessments
            if isinstance(item, dict) and isinstance(item.get("assessment_id"), str)
        } if isinstance(d1_assessments, list) else {}
        decisions = record.get("decisions", [])
        if not isinstance(decisions, list):
            decisions = []
        if len(decisions) != 8:
            errors.append(f"{CLOSURE_PATH}: exactly eight closure decisions are required")
        decision_ids = [
            item.get("closure_decision_entry_id")
            for item in decisions
            if isinstance(item, dict)
        ]
        if set(decision_ids) != set(EXPECTED_CLOSURE_DECISIONS):
            errors.append(f"{CLOSURE_PATH}: closure decision IDs must exactly match A99-H99")
        if len(decision_ids) != len(set(decision_ids)):
            errors.append(f"{CLOSURE_PATH}: duplicate closure decision ID")
        source_entries: list[Any] = []
        predecessor_ids: list[Any] = []
        rationales: list[Any] = []
        for index, item in enumerate(decisions):
            location = f"{CLOSURE_PATH}: decisions[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{location}: decision must be an object")
                continue
            decision_id = item.get("closure_decision_entry_id")
            source_entry_id = item.get("source_entry_id")
            predecessor_id = item.get("predecessor_assessment_id")
            source_entries.append(source_entry_id)
            predecessor_ids.append(predecessor_id)
            rationales.append(item.get("rationale"))
            expected_identity = EXPECTED_CLOSURE_DECISIONS.get(decision_id)
            if expected_identity is None:
                errors.append(f"{location}: unknown closure decision identity")
                continue
            expected_frame, expected_entry, expected_predecessor = expected_identity
            if item.get("source_frame_id") != expected_frame:
                errors.append(f"{location}: source_frame_id is not reciprocal with D1")
            if source_entry_id != expected_entry:
                errors.append(f"{location}: source_entry_id is not reciprocal with D1")
            if predecessor_id != expected_predecessor:
                errors.append(
                    f"{location}: predecessor_assessment_id is not reciprocal with D1"
                )
            if item.get("predecessor_result") != "unresolved":
                errors.append(f"{location}: predecessor_result must remain unresolved")
            _, artifact_errors = validate_artifact(
                root,
                item.get("source_extraction"),
                "domain-universe/extractions/wipo-ipc-2026-01-class.json",
                f"{location}: source_extraction",
            )
            errors.extend(artifact_errors)
            predecessor = d1_by_id.get(expected_predecessor)
            if not isinstance(predecessor, dict):
                errors.append(f"{location}: predecessor assessment does not exist")
                continue
            if (
                predecessor.get("assessment_id") != predecessor_id
                or predecessor.get("source_frame_id") != item.get("source_frame_id")
                or predecessor.get("source_entry_id") != source_entry_id
            ):
                errors.append(f"{location}: D1 predecessor linkage is not reciprocal")
            if predecessor.get("minimal_gate_result") != "unresolved":
                errors.append(f"{location}: D1 predecessor result must remain unresolved")
            gate = predecessor.get("gate", {})
            d1_coherence = gate.get("coherent_substantive_locus") if isinstance(gate, dict) else None
            if item.get("coherent_substantive_locus") != d1_coherence:
                errors.append(
                    f"{location}: coherent_substantive_locus must equal the D1 judgment"
                )
            section_token = expected_entry.removeprefix("ipc-")
            rationale = item.get("rationale")
            if not isinstance(rationale, str) or section_token not in rationale:
                errors.append(f"{location}: rationale must preserve section-specific identity")

        if len(source_entries) != len(set(source_entries)):
            errors.append(f"{CLOSURE_PATH}: duplicate source entry")
        if len(predecessor_ids) != len(set(predecessor_ids)):
            errors.append(f"{CLOSURE_PATH}: duplicate predecessor assessment")
        if len(rationales) != len(set(rationales)):
            errors.append(f"{CLOSURE_PATH}: each decision requires an independent rationale")

        counts = {
            "decision_count": len(decisions),
            "excluded_non_materializable": sum(
                isinstance(item, dict)
                and item.get("final_normalization_disposition")
                == "excluded_non_materializable"
                for item in decisions
            ),
            "unresolved": sum(
                isinstance(item, dict)
                and item.get("final_normalization_disposition") == "unresolved"
                for item in decisions
            ),
            "candidate_contributions": sum(
                isinstance(item, dict) and item.get("candidate_contribution") != "none"
                for item in decisions
            ),
        }
        aggregate = record.get("aggregate", {})
        if not isinstance(aggregate, dict):
            errors.append(f"{CLOSURE_PATH}: aggregate must be an object")
        else:
            for field, expected in counts.items():
                if aggregate.get(field) != expected:
                    errors.append(f"{CLOSURE_PATH}: aggregate {field} does not match decisions")

    overlay_directory = root / OVERLAY_DIRECTORY
    overlay_files = (
        sorted(overlay_directory.rglob("*.json")) if overlay_directory.exists() else []
    )
    if overlay_files:
        errors.append("normalization closure application: Task 105D3 must create no overlay")
    candidate_files = sorted((root / "domain-universe/candidates").rglob("*.json"))
    if candidate_files:
        errors.append("normalization closure application: Domain candidate count must remain zero")
    applied_roots = (
        "domain-universe",
        "selection",
        "registry",
        "cases",
        "evidence",
        "data",
    )
    for relative_root in applied_roots:
        directory = root / relative_root
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.json")):
            relative = path.relative_to(root).as_posix()
            if (
                relative != CLOSURE_PATH
                and "excluded_non_materializable" in path.read_text(encoding="utf-8")
            ):
                errors.append(
                    "normalization closure application: successor disposition leaked into "
                    f"{relative}"
                )
    return errors


def validate_materialization_architecture(root: Path) -> list[str]:
    """Keep current scientific inputs immutable until a later governed overlay task."""

    errors: list[str] = []
    errors.extend(
        validate_fixed_bytes(
            root,
            MATERIALIZATION_PROTOCOL_PATH,
            EXPECTED_MATERIALIZATION_PROTOCOL_SHA256,
            "normalization materialization protocol",
        )
    )
    errors.extend(
        validate_fixed_bytes(
            root,
            OVERLAY_SCHEMA_PATH,
            EXPECTED_OVERLAY_SCHEMA_SHA256,
            "historical v0.1 normalization overlay schema",
        )
    )
    errors.extend(
        validate_fixed_bytes(
            root, CODEBOOK_PATH, EXPECTED_CODEBOOK_SHA256, "Normalization Codebook v0.1"
        )
    )
    errors.extend(
        validate_fixed_bytes(
            root,
            RESIDUAL_PATH,
            EXPECTED_RESIDUAL_SHA256,
            "Task 105D1 residual clarification",
        )
    )
    errors.extend(
        validate_fixed_bytes(
            root, BOUNDARY_PATH, EXPECTED_BOUNDARY_SHA256, "Domain Universe boundary"
        )
    )

    pass1_total = 0
    pass1_unresolved = 0
    seen_extractions: set[str] = set()
    seen_source_frames: set[str] = set()
    for filename, (extraction_relative, _, _) in EXPECTED_PASS1.items():
        pass1_relative = pass1_record_path(filename)
        errors.extend(
            validate_fixed_bytes(
                root,
                pass1_relative,
                EXPECTED_PASS1_SHA256[filename],
                "Pass 1",
            )
        )
        pass1_path = root / pass1_relative
        if not pass1_path.is_file():
            continue
        try:
            pass1 = read_json(pass1_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{pass1_relative}: invalid immutable Pass 1 JSON: {exc}")
            continue
        interpretations = pass1.get("interpretations", []) if isinstance(pass1, dict) else []
        if isinstance(interpretations, list):
            pass1_total += len(interpretations)
            pass1_unresolved += sum(
                isinstance(item, dict) and item.get("minimal_gate_result") == "unresolved"
                for item in interpretations
            )
        extraction_reference = pass1.get("source_extraction") if isinstance(pass1, dict) else None
        if not isinstance(extraction_reference, dict):
            errors.append(f"{pass1_relative}: immutable extraction binding is missing")
            continue
        if extraction_reference.get("path") != extraction_relative:
            errors.append(f"{pass1_relative}: immutable extraction path changed")
        expected_extraction_sha = EXPECTED_EXTRACTION_SHA256.get(extraction_relative)
        if extraction_reference.get("sha256") != expected_extraction_sha:
            errors.append(f"{pass1_relative}: immutable extraction SHA-256 binding changed")
        if expected_extraction_sha is None:
            errors.append(f"{pass1_relative}: extraction is outside the fixed Task 104 set")
            continue
        seen_extractions.add(extraction_relative)
        errors.extend(
            validate_fixed_bytes(
                root, extraction_relative, expected_extraction_sha, "Task 104 extraction"
            )
        )
        extraction_path = root / extraction_relative
        if not extraction_path.is_file():
            continue
        try:
            extraction = read_json(extraction_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{extraction_relative}: invalid immutable extraction JSON: {exc}")
            continue
        frame_reference = extraction.get("source_frame") if isinstance(extraction, dict) else None
        if not isinstance(frame_reference, dict):
            errors.append(f"{extraction_relative}: immutable source-frame binding is missing")
            continue
        frame_relative = frame_reference.get("path")
        if not isinstance(frame_relative, str):
            errors.append(f"{extraction_relative}: immutable source-frame path is invalid")
            continue
        expected_frame_sha = EXPECTED_SOURCE_FRAME_SHA256.get(frame_relative)
        if expected_frame_sha is None:
            errors.append(f"{extraction_relative}: source frame is outside the fixed Task 104 set")
            continue
        seen_source_frames.add(frame_relative)
        if frame_reference.get("sha256") != expected_frame_sha:
            errors.append(f"{extraction_relative}: immutable source-frame SHA-256 binding changed")
        errors.extend(
            validate_fixed_bytes(
                root, frame_relative, expected_frame_sha, "registered source frame"
            )
        )

    if seen_extractions != set(EXPECTED_EXTRACTION_SHA256):
        errors.append("materialization architecture: exact four Task 104 extractions are required")
    if seen_source_frames != set(EXPECTED_SOURCE_FRAME_SHA256):
        errors.append("materialization architecture: exact four source frames are required")
    errors.extend(
        validate_fixed_bytes(root, PASS2A_PATH, EXPECTED_PASS2A_SHA256, "Pass 2A")
    )
    errors.extend(
        validate_fixed_bytes(root, PASS2B_PATH, EXPECTED_PASS2B_SHA256, "Pass 2B")
    )

    overlay_schema_path = root / OVERLAY_SCHEMA_PATH
    candidate_schema_path = root / CANDIDATE_SCHEMA_PATH
    try:
        overlay_schema = read_json(overlay_schema_path)
    except FileNotFoundError:
        errors.append(f"{OVERLAY_SCHEMA_PATH}: prospective overlay schema is required")
        overlay_schema = {}
    except json.JSONDecodeError as exc:
        errors.append(f"{OVERLAY_SCHEMA_PATH}: invalid JSON: {exc}")
        overlay_schema = {}
    if not isinstance(overlay_schema, dict):
        errors.append(f"{OVERLAY_SCHEMA_PATH}: schema root must be an object")
        overlay_schema = {}
    try:
        candidate_schema = read_json(candidate_schema_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"{CANDIDATE_SCHEMA_PATH}: cannot load amended candidate schema: {exc}")
        candidate_schema = {}
    if not isinstance(candidate_schema, dict):
        errors.append(f"{CANDIDATE_SCHEMA_PATH}: schema root must be an object")
        candidate_schema = {}

    if overlay_schema.get("x-instrument-version") != "0.5.0-draft":
        errors.append(f"{OVERLAY_SCHEMA_PATH}: x-instrument-version mismatch")
    required_candidate_fields = candidate_schema.get("required", [])
    candidate_properties = candidate_schema.get("properties", {})
    if "normalization_disposition_record" not in required_candidate_fields:
        errors.append(
            f"{CANDIDATE_SCHEMA_PATH}: normalization_disposition_record must be required"
        )
    if not isinstance(candidate_properties, dict) or candidate_properties.get(
        "normalization_disposition_record"
    ) != {"$ref": "#/$defs/artifact"}:
        errors.append(
            f"{CANDIDATE_SCHEMA_PATH}: normalization_disposition_record must be an artifact"
        )

    exact_schema_bindings = {
        "materialization_protocol": (
            MATERIALIZATION_PROTOCOL_PATH,
            EXPECTED_MATERIALIZATION_PROTOCOL_SHA256,
        ),
        "normalization_codebook": (CODEBOOK_PATH, EXPECTED_CODEBOOK_SHA256),
        "universe_boundary": (BOUNDARY_PATH, EXPECTED_BOUNDARY_SHA256),
        "ford_extraction": (
            "domain-universe/extractions/oecd-ford-frascati-2015-second-level.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/oecd-ford-frascati-2015-second-level.json"
            ],
        ),
        "isic_extraction": (
            "domain-universe/extractions/un-isic-rev5-division.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/un-isic-rev5-division.json"
            ],
        ),
        "ipc_extraction": (
            "domain-universe/extractions/wipo-ipc-2026-01-class.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/wipo-ipc-2026-01-class.json"
            ],
        ),
        "cofog_extraction": (
            "domain-universe/extractions/un-cofog-1999-group.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/un-cofog-1999-group.json"
            ],
        ),
        "ford_pass1": (
            pass1_record_path("oecd-ford-frascati-2015-pass1.json"),
            EXPECTED_PASS1_SHA256["oecd-ford-frascati-2015-pass1.json"],
        ),
        "isic_pass1": (
            pass1_record_path("un-isic-rev5-pass1.json"),
            EXPECTED_PASS1_SHA256["un-isic-rev5-pass1.json"],
        ),
        "ipc_pass1": (
            pass1_record_path("wipo-ipc-2026-01-pass1.json"),
            EXPECTED_PASS1_SHA256["wipo-ipc-2026-01-pass1.json"],
        ),
        "cofog_pass1": (
            pass1_record_path("un-cofog-1999-pass1.json"),
            EXPECTED_PASS1_SHA256["un-cofog-1999-pass1.json"],
        ),
        "pass2a_record": (PASS2A_PATH, EXPECTED_PASS2A_SHA256),
        "pass2b_record": (PASS2B_PATH, EXPECTED_PASS2B_SHA256),
    }
    for definition, expected in exact_schema_bindings.items():
        if schema_const_reference(overlay_schema, definition) != expected:
            errors.append(
                f"{OVERLAY_SCHEMA_PATH}: {definition} must bind exact immutable bytes"
            )

    candidate_files = sorted((root / "domain-universe/candidates").rglob("*.json"))
    if candidate_files:
        errors.append("materialization architecture: Domain candidate count must remain zero")
    overlay_directory = root / OVERLAY_DIRECTORY
    overlay_files = sorted(overlay_directory.rglob("*.json")) if overlay_directory.exists() else []
    if overlay_files:
        errors.append("materialization architecture: Task 105D0 must create no overlay instance")
    candidate_id_pattern = re.compile(r"\bdu-cand-[0-9]{4}\b", re.IGNORECASE)
    for path in sorted((root / "domain-universe").rglob("*.json")):
        if candidate_id_pattern.search(path.read_text(encoding="utf-8")):
            errors.append(
                f"materialization architecture: assigned candidate identifier found in "
                f"{path.relative_to(root).as_posix()}"
            )

    if pass1_total != 330 or pass1_unresolved != 8:
        errors.append(
            "historical Pass 1 state must remain 330 entries with eight unresolved"
        )
    return errors


def canonical_json_sha256(value: Any) -> str:
    """Hash canonical UTF-8 JSON used by the Task 105D4 completion record."""

    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def completion_group_state(
    groups: Any,
) -> tuple[str, str, set[Pass1Key], list[str]]:
    """Derive the exact inherited labels, shape digest, and future ID order."""

    errors: list[str] = []
    if not isinstance(groups, list):
        return "", "", set(), [f"{PASS2A_PATH}: groups must be an array"]

    shape: list[dict[str, Any]] = []
    order_rows: list[tuple[str, str, str, str]] = []
    grouped: list[Pass1Key] = []
    for index, group in enumerate(groups):
        location = f"{PASS2A_PATH}: groups[{index}]"
        if not isinstance(group, dict):
            errors.append(f"{location}: group must be an object")
            continue
        group_id = group.get("normalization_group_id")
        label = group.get("group_locus_statement")
        anchor = group.get("deterministic_anchor")
        if not isinstance(group_id, str):
            errors.append(f"{location}: normalization_group_id must be a string")
            continue
        if not isinstance(label, str) or not label:
            errors.append(f"{location}: group_locus_statement must be non-empty")
            continue
        anchor_key = locator_key(anchor)
        if anchor_key is None:
            errors.append(f"{location}: deterministic anchor is invalid")
            continue

        members = group.get("members", [])
        if not isinstance(members, list):
            errors.append(f"{location}: members must be an array")
            continue
        member_identities: list[dict[str, str]] = []
        for member_index, member in enumerate(members):
            member_key = locator_key(member)
            if member_key is None:
                errors.append(
                    f"{location}: members[{member_index}] identity is invalid"
                )
                continue
            grouped.append(member_key)
            member_identities.append(
                {
                    "source_frame_id": member_key[0],
                    "source_entry_id": member_key[1],
                }
            )
        member_identities.sort(
            key=lambda item: (item["source_frame_id"], item["source_entry_id"])
        )
        shape.append(
            {
                "normalization_group_id": group_id,
                "canonical_label": label,
                "deterministic_anchor": {
                    "source_frame_id": anchor_key[0],
                    "source_entry_id": anchor_key[1],
                },
                "member_source_entry_identities": member_identities,
            }
        )
        order_rows.append((label.casefold(), anchor_key[0], anchor_key[1], group_id))

    shape.sort(key=lambda item: item["normalization_group_id"])
    order_keys = [row[:3] for row in order_rows]
    if len(order_keys) != len(set(order_keys)):
        errors.append("normalization completion: future candidate-ID order key is not unique")
    order_rows.sort(key=lambda row: row[:3])
    ordered_group_ids = [row[3] for row in order_rows]
    if len(grouped) != len(set(grouped)):
        errors.append("normalization completion: grouped source identity is duplicated")
    return (
        canonical_json_sha256(shape),
        canonical_json_sha256(ordered_group_ids),
        set(grouped),
        errors,
    )


def validate_normalization_completion(
    root: Path,
    validate_contract: Callable[[Any, Any, str], list[str]],
) -> list[str]:
    """Fail closed on Task 105 completion without performing Task 106."""

    errors: list[str] = []
    immutable_inputs = {
        CODEBOOK_PATH: EXPECTED_CODEBOOK_SHA256,
        BOUNDARY_PATH: EXPECTED_BOUNDARY_SHA256,
        PASS2A_PATH: EXPECTED_PASS2A_SHA256,
        PASS2B_PATH: EXPECTED_PASS2B_SHA256,
        RESIDUAL_PATH: EXPECTED_RESIDUAL_SHA256,
        CLOSURE_AMENDMENT_PATH: EXPECTED_CLOSURE_AMENDMENT_SHA256,
        CLOSURE_SCHEMA_PATH: EXPECTED_CLOSURE_SCHEMA_SHA256,
        CLOSURE_PATH: EXPECTED_CLOSURE_SHA256,
        MATERIALIZATION_PROTOCOL_PATH: EXPECTED_MATERIALIZATION_PROTOCOL_SHA256,
        OVERLAY_SCHEMA_PATH: EXPECTED_OVERLAY_SCHEMA_SHA256,
    }
    immutable_inputs.update(EXPECTED_EXTRACTION_SHA256)
    immutable_inputs.update(
        {
            pass1_record_path(filename): digest
            for filename, digest in EXPECTED_PASS1_SHA256.items()
        }
    )
    for relative, digest in immutable_inputs.items():
        errors.extend(
            validate_fixed_bytes(root, relative, digest, "Task 105 immutable history")
        )

    completion_directory = root / COMPLETION_DIRECTORY
    completion_files = (
        sorted(completion_directory.rglob("*.json"))
        if completion_directory.exists()
        else []
    )
    expected_completion_path = root / COMPLETION_PATH
    if completion_files != [expected_completion_path]:
        errors.append(
            f"{COMPLETION_DIRECTORY}: expected exactly normalization-completion-v0.1.json"
        )
    errors.extend(
        validate_fixed_bytes(
            root,
            COMPLETION_PATH,
            EXPECTED_COMPLETION_SHA256,
            "normalization completion manifest",
        )
    )

    schema: dict[str, Any] = {}
    record: dict[str, Any] = {}
    schema_path = root / COMPLETION_SCHEMA_PATH
    errors.extend(
        validate_fixed_bytes(
            root,
            COMPLETION_SCHEMA_PATH,
            EXPECTED_COMPLETION_SCHEMA_SHA256,
            "normalization completion schema",
        )
    )
    if schema_path.is_file():
        try:
            value = read_json(schema_path)
            if isinstance(value, dict):
                schema = value
            else:
                errors.append(f"{COMPLETION_SCHEMA_PATH}: schema root must be an object")
        except json.JSONDecodeError as exc:
            errors.append(f"{COMPLETION_SCHEMA_PATH}: invalid JSON: {exc}")
    if expected_completion_path.is_file():
        try:
            value = read_json(expected_completion_path)
            if isinstance(value, dict):
                record = value
            else:
                errors.append(f"{COMPLETION_PATH}: record must be an object")
        except json.JSONDecodeError as exc:
            errors.append(f"{COMPLETION_PATH}: invalid JSON: {exc}")

    if schema.get("x-instrument-version") != "0.5.0-draft":
        errors.append(f"{COMPLETION_SCHEMA_PATH}: x-instrument-version mismatch")
    if record and schema:
        errors.extend(validate_contract(record, schema, COMPLETION_PATH))

    single_bindings = {
        "normalization_codebook": CODEBOOK_PATH,
        "universe_boundary": BOUNDARY_PATH,
        "pass2a_record": PASS2A_PATH,
        "pass2b_record": PASS2B_PATH,
        "residual_clarification": RESIDUAL_PATH,
        "closure_amendment": CLOSURE_AMENDMENT_PATH,
        "closure_decision_schema": CLOSURE_SCHEMA_PATH,
        "closure_application": CLOSURE_PATH,
    }
    for field, relative in single_bindings.items():
        _, artifact_errors = validate_artifact(
            root, record.get(field), relative, f"{COMPLETION_PATH}: {field}"
        )
        errors.extend(artifact_errors)

    for field, expected_paths in (
        ("source_extractions", set(EXPECTED_EXTRACTION_SHA256)),
        (
            "pass1_records",
            {pass1_record_path(filename) for filename in EXPECTED_PASS1},
        ),
    ):
        references = record.get(field, [])
        if not isinstance(references, list):
            errors.append(f"{COMPLETION_PATH}: {field} must be an array")
            continue
        paths = [
            item.get("path") for item in references if isinstance(item, dict)
        ]
        if len(paths) != len(set(paths)) or set(paths) != expected_paths:
            errors.append(f"{COMPLETION_PATH}: {field} must bind the exact artifact set")
        for index, reference in enumerate(references):
            if not isinstance(reference, dict):
                errors.append(f"{COMPLETION_PATH}: {field}[{index}] must be an artifact")
                continue
            relative = reference.get("path")
            if isinstance(relative, str) and relative in expected_paths:
                _, artifact_errors = validate_artifact(
                    root,
                    reference,
                    relative,
                    f"{COMPLETION_PATH}: {field}[{index}]",
                )
                errors.extend(artifact_errors)

    pass1_index, _, pass1_errors = build_pass1_index(root)
    errors.extend(pass1_errors)
    pass2a: dict[str, Any] = {}
    closure: dict[str, Any] = {}
    try:
        value = read_json(root / PASS2A_PATH)
        if isinstance(value, dict):
            pass2a = value
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"{PASS2A_PATH}: cannot derive completion state: {exc}")
    try:
        value = read_json(root / CLOSURE_PATH)
        if isinstance(value, dict):
            closure = value
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"{CLOSURE_PATH}: cannot derive completion state: {exc}")

    completion_time, timestamp_errors = parse_timezone_aware_datetime(
        record.get("recorded_at"),
        f"{COMPLETION_PATH}: recorded_at",
    )
    errors.extend(timestamp_errors)
    closure_time, timestamp_errors = parse_timezone_aware_datetime(
        closure.get("recorded_at"),
        f"{CLOSURE_PATH}: recorded_at",
    )
    errors.extend(timestamp_errors)
    if (
        completion_time is not None
        and closure_time is not None
        and completion_time <= closure_time
    ):
        errors.append(
            f"{COMPLETION_PATH}: recorded_at must be strictly later than "
            f"{CLOSURE_PATH}: recorded_at"
        )

    shape_digest, order_digest, grouped, group_errors = completion_group_state(
        pass2a.get("groups", [])
    )
    errors.extend(group_errors)
    groups = pass2a.get("groups", [])
    group_count = len(groups) if isinstance(groups, list) else 0
    decisions = closure.get("decisions", [])
    if not isinstance(decisions, list):
        decisions = []
    terminal: set[Pass1Key] = set()
    unresolved = 0
    for item in decisions:
        if not isinstance(item, dict):
            continue
        key = locator_key(item)
        if item.get("final_normalization_disposition") == "excluded_non_materializable":
            if key is not None:
                terminal.add(key)
        elif item.get("final_normalization_disposition") == "unresolved":
            unresolved += 1

    all_pass1 = set(pass1_index)
    if grouped & terminal:
        errors.append("normalization completion: grouped and terminal identities overlap")
    if grouped | terminal != all_pass1:
        missing = sorted(all_pass1 - grouped - terminal)
        extra = sorted((grouped | terminal) - all_pass1)
        errors.append(
            "normalization completion: grouped and terminal identities must exactly "
            f"partition all Pass 1 identities; missing={missing}, extra={extra}"
        )
    if group_count != 322 or len(grouped) != 322:
        errors.append("normalization completion: exactly 322 candidate-bearing groups and entries required")
    if len(terminal) != 8:
        errors.append("normalization completion: exactly eight terminal source entries required")
    expected_terminal = set(EXPECTED_UNRESOLVED)
    if terminal != expected_terminal:
        errors.append("normalization completion: terminal identities must exactly equal IPC A99-H99")
    effective_unresolved = unresolved + len(all_pass1 - grouped - terminal)
    if effective_unresolved != 0:
        errors.append("normalization completion: effective unresolved source entries must be zero")

    expected_state = {
        "normalization_completion_id": "normalization-completion-v0.1",
        "instrument_version": "0.5.0-draft",
        "status": "complete",
        "source_entry_total": 330,
        "candidate_bearing_group_count": group_count,
        "candidate_bearing_source_entry_count": len(grouped),
        "terminal_non_candidate_entry_count": len(terminal),
        "effective_unresolved_source_entry_count": effective_unresolved,
        "candidate_canonical_label_source": "pass2a_group_locus_statement",
        "candidate_universe_shape_sha256": shape_digest,
        "candidate_id_order_sha256": order_digest,
        "stable_candidate_id_assignment_permitted": True,
        "domain_candidate_count": 0,
        "assigned_stable_candidate_id_count": 0,
        "normalization_overlay_instance_count": 0,
    }
    for field, expected in expected_state.items():
        if record.get(field) != expected:
            errors.append(f"{COMPLETION_PATH}: {field} mismatch")
    if shape_digest != EXPECTED_CANDIDATE_UNIVERSE_SHAPE_SHA256:
        errors.append("normalization completion: candidate-universe shape digest changed")
    if order_digest != EXPECTED_CANDIDATE_ID_ORDER_SHA256:
        errors.append("normalization completion: candidate-ID order digest changed")

    if not STABLE_CANDIDATE_ID_ASSIGNMENT_PERMITTED:
        errors.append("normalization completion: stable candidate ID permission must be true")
    candidate_files = sorted((root / "domain-universe/candidates").rglob("*.json"))
    if candidate_files:
        errors.append("normalization completion: Domain candidate count must remain zero")
    overlay_directory = root / OVERLAY_DIRECTORY
    overlay_files = (
        sorted(overlay_directory.rglob("*.json")) if overlay_directory.exists() else []
    )
    if overlay_files:
        errors.append("normalization completion: overlay instance count must remain zero")
    candidate_id_pattern = re.compile(r"\bdu-cand-[0-9]{4}\b", re.IGNORECASE)
    for path in sorted((root / "domain-universe").rglob("*.json")):
        if candidate_id_pattern.search(path.read_text(encoding="utf-8")):
            errors.append(
                "normalization completion: assigned stable candidate identifier found in "
                f"{path.relative_to(root).as_posix()}"
            )

    errors.extend(
        validate_fixed_bytes(
            root,
            SUCCESSOR_MATERIALIZATION_PROTOCOL_PATH,
            EXPECTED_SUCCESSOR_MATERIALIZATION_PROTOCOL_SHA256,
            "successor materialization protocol v0.2",
        )
    )
    errors.extend(
        validate_fixed_bytes(
            root,
            SUCCESSOR_OVERLAY_SCHEMA_PATH,
            EXPECTED_SUCCESSOR_OVERLAY_SCHEMA_SHA256,
            "successor normalization overlay schema v0.2",
        )
    )
    protocol_path = root / SUCCESSOR_MATERIALIZATION_PROTOCOL_PATH
    if protocol_path.is_file():
        protocol = protocol_path.read_text(encoding="utf-8")
        required_protocol_text = (
            "POST-CLOSURE SUCCESSOR MATERIALIZATION PROTOCOL; FIXED BEFORE MATERIALIZATION; NOT SCIENTIFICALLY APPROVED",
            "normalization-completion-v0.1",
            "excluded_non_materializable",
            "Task 106, which has not started",
            "does not update",
        )
        for required in required_protocol_text:
            if required not in protocol:
                errors.append(
                    f"{SUCCESSOR_MATERIALIZATION_PROTOCOL_PATH}: missing {required!r}"
                )

    successor_schema: dict[str, Any] = {}
    try:
        value = read_json(root / SUCCESSOR_OVERLAY_SCHEMA_PATH)
        if isinstance(value, dict):
            successor_schema = value
        else:
            errors.append(f"{SUCCESSOR_OVERLAY_SCHEMA_PATH}: schema root must be an object")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"{SUCCESSOR_OVERLAY_SCHEMA_PATH}: cannot load schema: {exc}")
    if successor_schema.get("x-instrument-version") != "0.5.0-draft":
        errors.append(f"{SUCCESSOR_OVERLAY_SCHEMA_PATH}: x-instrument-version mismatch")

    successor_bindings = {
        "materialization_protocol": (
            SUCCESSOR_MATERIALIZATION_PROTOCOL_PATH,
            EXPECTED_SUCCESSOR_MATERIALIZATION_PROTOCOL_SHA256,
        ),
        "normalization_completion": (COMPLETION_PATH, EXPECTED_COMPLETION_SHA256),
        "normalization_codebook": (CODEBOOK_PATH, EXPECTED_CODEBOOK_SHA256),
        "universe_boundary": (BOUNDARY_PATH, EXPECTED_BOUNDARY_SHA256),
        "ford_extraction": (
            "domain-universe/extractions/oecd-ford-frascati-2015-second-level.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/oecd-ford-frascati-2015-second-level.json"
            ],
        ),
        "isic_extraction": (
            "domain-universe/extractions/un-isic-rev5-division.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/un-isic-rev5-division.json"
            ],
        ),
        "ipc_extraction": (
            "domain-universe/extractions/wipo-ipc-2026-01-class.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/wipo-ipc-2026-01-class.json"
            ],
        ),
        "cofog_extraction": (
            "domain-universe/extractions/un-cofog-1999-group.json",
            EXPECTED_EXTRACTION_SHA256[
                "domain-universe/extractions/un-cofog-1999-group.json"
            ],
        ),
        "ford_pass1": (
            pass1_record_path("oecd-ford-frascati-2015-pass1.json"),
            EXPECTED_PASS1_SHA256["oecd-ford-frascati-2015-pass1.json"],
        ),
        "isic_pass1": (
            pass1_record_path("un-isic-rev5-pass1.json"),
            EXPECTED_PASS1_SHA256["un-isic-rev5-pass1.json"],
        ),
        "ipc_pass1": (
            pass1_record_path("wipo-ipc-2026-01-pass1.json"),
            EXPECTED_PASS1_SHA256["wipo-ipc-2026-01-pass1.json"],
        ),
        "cofog_pass1": (
            pass1_record_path("un-cofog-1999-pass1.json"),
            EXPECTED_PASS1_SHA256["un-cofog-1999-pass1.json"],
        ),
        "pass2a_record": (PASS2A_PATH, EXPECTED_PASS2A_SHA256),
        "pass2b_record": (PASS2B_PATH, EXPECTED_PASS2B_SHA256),
        "residual_clarification": (RESIDUAL_PATH, EXPECTED_RESIDUAL_SHA256),
        "closure_amendment": (
            CLOSURE_AMENDMENT_PATH,
            EXPECTED_CLOSURE_AMENDMENT_SHA256,
        ),
        "closure_application": (CLOSURE_PATH, EXPECTED_CLOSURE_SHA256),
    }
    for definition, expected in successor_bindings.items():
        if schema_const_reference(successor_schema, definition) != expected:
            errors.append(
                f"{SUCCESSOR_OVERLAY_SCHEMA_PATH}: {definition} must bind exact bytes"
            )
    disposition = (
        successor_schema.get("$defs", {})
        .get("disposition_entry", {})
        .get("properties", {})
        .get("normalization_disposition", {})
    )
    expected_dispositions = {
        "candidate_created",
        "merged_into_candidate",
        "excluded_out_of_scope",
        "excluded_non_materializable",
        "unresolved",
    }
    if set(disposition.get("enum", [])) != expected_dispositions:
        errors.append(f"{SUCCESSOR_OVERLAY_SCHEMA_PATH}: disposition enum mismatch")
    if "excluded_duplicate" in json.dumps(successor_schema):
        errors.append(f"{SUCCESSOR_OVERLAY_SCHEMA_PATH}: excluded_duplicate must remain disabled")

    validator_path = root / "scripts/validate.py"
    if validator_path.is_file():
        source = validator_path.read_text(encoding="utf-8")
        domain_paths_start = source.find("DOMAIN_SCHEMA_PATHS = {")
        domain_paths_end = source.find("\n}", domain_paths_start)
        if (
            domain_paths_start < 0
            or domain_paths_end < 0
            or Path(SUCCESSOR_OVERLAY_SCHEMA_PATH).name
            in source[domain_paths_start:domain_paths_end]
        ):
            errors.append(
                "Task 105D4: successor overlay schema must not enter the Domain lock path"
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
    print(
        "Normalization validation passed: Pass 1, Pass 2A, Pass 2B, the IPC "
        "residual successor clarification, the immutable materialization "
        "architecture, the fixed closure-gap amendment, and its exact first "
        "IPC residual application are sound; Task 105 normalization completion "
        "and the uninstantiated v0.2 successor contract are fixed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
