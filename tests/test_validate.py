from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("observatory_validate", ROOT / "scripts/validate.py")
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)

V1 = "1.0.0-test"
V2 = "2.0.0-test"
INSTRUMENT_SOURCES = {
    "protocol": "PROTOCOL.md",
    "codebook": "CODEBOOK.md",
    "panel": "PANEL.md",
    "schedule": "docs/SCHEDULE.md",
    "governance": "GOVERNANCE.md",
    "registry": "registry/README.md",
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def panel_unit(unit_id: str = "test-unit", system_id: str = "test-system") -> dict[str, object]:
    return {
        "panel_unit_id": unit_id,
        "improvement_loop_id": f"{unit_id}-loop",
        "function_id": f"{unit_id}-function",
        "human_bottleneck_label": "test-only structural label",
        "boundary_conditions": "test-only structural boundary",
        "empirical_system_ids": [system_id],
    }


def unresolved_observation(
    observation_id: str = "test-observation",
    unit_id: str = "test-unit",
    system_id: str = "test-system",
    observed_at: str = "2026-01-01T00:00:00Z",
) -> dict[str, object]:
    return {
        "observation_id": observation_id,
        "panel_unit_id": unit_id,
        "empirical_system_ids": [system_id],
        "observed_at": observed_at,
        "protocol_version": V1,
        "codebook_version": V1,
        "schema_version": V1,
        "resolution_status": "unresolved",
        "evidence_ids": [],
        "provisional_human_criticality_summary": "unknown",
        "human_participation_presence": "unknown",
        "event_type": "unknown",
        "uncertainty_note": "test-only unresolved structural fixture",
    }


def structural_evidence(
    evidence_id: str,
    unit_id: str,
    system_id: str,
    observed_at: str,
) -> dict[str, object]:
    fixture_bytes = b"test-only structural fixture; no empirical assertion"
    return {
        "evidence_id": evidence_id,
        "schema_version": V1,
        "panel_unit_id": unit_id,
        "empirical_system_ids": [system_id],
        "source_uri": f"urn:test:{evidence_id}",
        "source_title": "Test-only structural fixture",
        "source_type": "other",
        "observed_at": observed_at,
        "retrieved_at": observed_at,
        "recorded_by": "test-suite",
        "content_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "relation": "contextualizes",
        "source_statement": "No empirical assertion; structural validation fixture only.",
        "interpretation": "",
    }


def longitudinal_observation(
    observation_id: str,
    prior_id: str,
    evidence_id: str,
    unit_id: str = "test-unit",
    system_id: str = "test-system",
    observed_at: str = "2026-02-01T00:00:00Z",
) -> dict[str, object]:
    return {
        "observation_id": observation_id,
        "panel_unit_id": unit_id,
        "empirical_system_ids": [system_id],
        "observed_at": observed_at,
        "protocol_version": V1,
        "codebook_version": V1,
        "schema_version": V1,
        "resolution_status": "resolved",
        "evidence_ids": [evidence_id],
        "provisional_human_criticality_summary": "unknown",
        "human_participation_presence": "unknown",
        "event_type": "no_supported_change",
        "prior_observation_id": prior_id,
        "uncertainty_note": "test-only longitudinal structural fixture",
    }


class TemporaryRepository:
    """Create only temporary structural fixtures; never repository scientific data."""

    def __init__(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "observatory"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )

    def close(self) -> None:
        self.temporary_directory.cleanup()

    def reference(self, relative: str) -> dict[str, str]:
        return {
            "path": relative,
            "sha256": VALIDATE.sha256_file(self.root / relative),
        }

    def _snapshot_instruments(self, wave: str, version: str) -> dict[str, object]:
        locks: dict[str, object] = {}
        for role, source_relative in INSTRUMENT_SOURCES.items():
            text = (self.root / source_relative).read_text(encoding="utf-8")
            text = re.sub(
                r"Instrument version:\s*`[^`]+`",
                f"Instrument version: `{version}`",
                text,
                count=1,
            )
            relative = f"data/waves/{wave}/instruments/{role}.md"
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            locks[role] = {
                "version": version,
                "locked_at": "2026-01-01T00:00:00Z",
                "artifacts": [self.reference(relative)],
            }
        return locks

    def _snapshot_schemas(self, wave: str, version: str) -> dict[str, object]:
        locks: dict[str, object] = {}
        for role, source_relative in VALIDATE.CURRENT_SCHEMA_PATHS.items():
            schema = json.loads((self.root / source_relative).read_text(encoding="utf-8"))
            schema["x-instrument-version"] = version
            relative = f"data/waves/{wave}/schemas/{Path(source_relative).name}"
            write_json(self.root / relative, schema)
            locks[role] = {
                "version": version,
                "locked_at": "2026-01-01T00:00:00Z",
                "artifacts": [self.reference(relative)],
            }
        return locks

    def create_wave(
        self,
        wave: str,
        units: list[dict[str, object]],
        observations: list[dict[str, object]],
        evidence: list[dict[str, object]] | None = None,
        version: str = V1,
    ) -> dict[str, object]:
        evidence = evidence or []
        wave_directory = self.root / f"data/waves/{wave}"
        wave_directory.mkdir(parents=True, exist_ok=True)
        instrument_locks = self._snapshot_instruments(wave, version)
        schema_locks = self._snapshot_schemas(wave, version)

        panel_relative = f"data/waves/{wave}/panel.json"
        write_json(
            self.root / panel_relative,
            {
                "snapshot_id": f"{wave}-test-panel",
                "instrument_version": version,
                "status": "frozen",
                "units": units,
            },
        )
        registry_relative = f"data/waves/{wave}/registry.csv"
        (self.root / registry_relative).write_text(
            ",".join(VALIDATE.REGISTRY_HEADER) + "\n", encoding="utf-8"
        )

        evidence_refs = []
        for index, record in enumerate(evidence):
            relative = f"data/waves/{wave}/evidence/evidence-{index}.json"
            write_json(self.root / relative, record)
            evidence_refs.append(self.reference(relative))
        observation_refs = []
        for index, record in enumerate(observations):
            relative = f"data/waves/{wave}/observations/observation-{index}.json"
            write_json(self.root / relative, record)
            observation_refs.append(self.reference(relative))

        manifest: dict[str, object] = {
            "wave_id": wave,
            "status": "official",
            "schema_version": version,
            "panel_snapshot": self.reference(panel_relative),
            "registry_snapshot": self.reference(registry_relative),
            "instrument_locks": instrument_locks,
            "schema_locks": schema_locks,
            "scientific_records": {
                "evidence": evidence_refs,
                "observations": observation_refs,
            },
            "locked_at": "2026-01-01T00:00:00Z",
            "released_at": "2026-01-02T00:00:00Z",
            "release_approval": "test-only-approval",
        }
        write_json(wave_directory / "manifest.json", manifest)
        return manifest

    def save_manifest(self, wave: str, manifest: dict[str, object]) -> None:
        write_json(self.root / f"data/waves/{wave}/manifest.json", manifest)

    def advance_current_to_v2(self) -> None:
        for relative in VALIDATE.VERSIONED_TEXT_INSTRUMENTS:
            path = self.root / relative
            text = path.read_text(encoding="utf-8")
            text = re.sub(
                r"Instrument version:\s*`[^`]+`",
                f"Instrument version: `{V2}`",
                text,
                count=1,
            )
            path.write_text(text, encoding="utf-8")

        schema_readme = self.root / "schemas/README.md"
        text = schema_readme.read_text(encoding="utf-8")
        text = re.sub(
            r"Schema bundle version:\s*`[^`]+`",
            f"Schema bundle version: `{V2}`",
            text,
            count=1,
        )
        schema_readme.write_text(text, encoding="utf-8")

        for relative in VALIDATE.SCHEMA_FILES:
            path = self.root / relative
            schema = json.loads(path.read_text(encoding="utf-8"))
            schema["x-instrument-version"] = V2
            if relative.endswith("observation.schema.json"):
                schema["required"].append("v2_only_observation_field")
                schema["properties"]["v2_only_observation_field"] = {"type": "string"}
            if relative.endswith("wave-manifest.schema.json"):
                schema["required"].append("v2_only_manifest_field")
                schema["properties"]["v2_only_manifest_field"] = {"type": "string"}
            write_json(path, schema)

        path = self.root / "schemas/instruments.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["manifest_version"] = V2
        for instrument in manifest["instruments"]:
            instrument["version"] = V2
        write_json(path, manifest)


class RepositoryContractTests(unittest.TestCase):
    def test_bootstrap_scaffold_passes(self) -> None:
        self.assertEqual([], VALIDATE.validate_repository(ROOT))

    def test_ontology_and_measurement_boundaries_remain_intact(self) -> None:
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        codebook = (ROOT / "CODEBOOK.md").read_text(encoding="utf-8")
        self.assertIn("improvement-loop", protocol)
        self.assertIn("Human Bottleneck", protocol)
        self.assertIn("not a fixed vector", codebook)
        self.assertNotIn("[C,L,V,A,R,H]", codebook.replace(" ", ""))

    def test_unresolved_contract_is_explicit_and_evidence_free(self) -> None:
        schema = json.loads(
            (ROOT / "schemas/observation.schema.json").read_text(encoding="utf-8")
        )
        record = unresolved_observation()
        record["schema_version"] = schema["x-instrument-version"]
        record["protocol_version"] = "not-checked-by-contract"
        record["codebook_version"] = "not-checked-by-contract"
        self.assertEqual([], VALIDATE.validate_contract(record, schema, "test unresolved"))


class HistoricalSelfContainmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = TemporaryRepository()

    def tearDown(self) -> None:
        self.repository.close()

    def test_wave_v1_survives_current_instruments_and_schemas_advancing_to_v2(self) -> None:
        self.repository.create_wave(
            "wave-0",
            [panel_unit()],
            [unresolved_observation()],
        )
        self.assertEqual([], VALIDATE.validate_repository(self.repository.root))

        self.repository.advance_current_to_v2()
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertEqual([], errors)

    def test_locked_schema_snapshot_hash_must_be_real(self) -> None:
        manifest = self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        manifest["schema_locks"]["observation"]["artifacts"][0]["sha256"] = "a" * 64
        self.repository.save_manifest("wave-0", manifest)
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_instrument_snapshot_must_be_inside_wave(self) -> None:
        manifest = self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        manifest["instrument_locks"]["protocol"]["artifacts"] = [
            self.repository.reference("PROTOCOL.md")
        ]
        self.repository.save_manifest("wave-0", manifest)
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("must be inside its immutable Wave directory" in error for error in errors))

    def test_instrument_snapshot_role_identity_must_match(self) -> None:
        manifest = self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        manifest["instrument_locks"]["protocol"]["artifacts"] = manifest[
            "instrument_locks"
        ]["codebook"]["artifacts"]
        self.repository.save_manifest("wave-0", manifest)
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("snapshot identity does not match" in error for error in errors))

    def test_schema_snapshot_role_identity_must_match(self) -> None:
        manifest = self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        manifest["schema_locks"]["observation"]["artifacts"] = manifest["schema_locks"][
            "evidence"
        ]["artifacts"]
        self.repository.save_manifest("wave-0", manifest)
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("schema 'observation' identity" in error for error in errors))


class OfficialCompletenessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = TemporaryRepository()

    def tearDown(self) -> None:
        self.repository.close()

    def test_empty_official_panel_fails(self) -> None:
        self.repository.create_wave("wave-0", [], [])
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("Frozen Panel must be non-empty" in error for error in errors))

    def test_omitted_panel_unit_fails_coverage(self) -> None:
        self.repository.create_wave(
            "wave-0",
            [panel_unit("test-unit-1", "test-system-1"), panel_unit("test-unit-2", "test-system-2")],
            [unresolved_observation("test-observation-1", "test-unit-1", "test-system-1")],
        )
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(
            any("'test-unit-2' has no valid explicit observation coverage" in error for error in errors)
        )

    def test_explicit_unresolved_observation_satisfies_coverage(self) -> None:
        self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        self.assertEqual([], VALIDATE.validate_repository(self.repository.root))


class LongitudinalReferentialIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = TemporaryRepository()

    def tearDown(self) -> None:
        self.repository.close()

    def create_pair(
        self,
        prior: dict[str, object],
        current: dict[str, object],
        prior_unit: dict[str, object] | None = None,
        current_unit: dict[str, object] | None = None,
    ) -> list[str]:
        prior_unit = prior_unit or panel_unit()
        current_unit = current_unit or panel_unit()
        self.repository.create_wave("wave-0", [prior_unit], [prior])
        evidence_id = current["evidence_ids"][0]
        evidence = structural_evidence(
            evidence_id,
            current["panel_unit_id"],
            current["empirical_system_ids"][0],
            current["observed_at"],
        )
        self.repository.create_wave("wave-1", [current_unit], [current], [evidence])
        return VALIDATE.validate_repository(self.repository.root)

    def test_valid_cross_wave_prior_reference_passes(self) -> None:
        errors = self.create_pair(
            unresolved_observation("observation-v1", observed_at="2026-01-01T00:00:00Z"),
            longitudinal_observation("observation-v2", "observation-v1", "evidence-v2"),
        )
        self.assertEqual([], errors)

    def test_missing_prior_reference_fails(self) -> None:
        errors = self.create_pair(
            unresolved_observation("observation-v1"),
            longitudinal_observation("observation-v2", "missing-observation", "evidence-v2"),
        )
        self.assertTrue(any("does not resolve" in error for error in errors))

    def test_prior_from_different_panel_unit_fails(self) -> None:
        prior = unresolved_observation(
            "observation-v1", "test-unit-1", "test-system-1"
        )
        current = longitudinal_observation(
            "observation-v2",
            "observation-v1",
            "evidence-v2",
            "test-unit-2",
            "test-system-2",
        )
        errors = self.create_pair(
            prior,
            current,
            panel_unit("test-unit-1", "test-system-1"),
            panel_unit("test-unit-2", "test-system-2"),
        )
        self.assertTrue(any("different panel unit" in error for error in errors))

    def test_self_reference_fails(self) -> None:
        current = longitudinal_observation(
            "observation-v2", "observation-v2", "evidence-v2"
        )
        errors = self.create_pair(unresolved_observation("observation-v1"), current)
        self.assertTrue(any("self-reference" in error for error in errors))

    def test_forward_reference_fails(self) -> None:
        errors = self.create_pair(
            unresolved_observation("observation-v1", observed_at="2026-03-01T00:00:00Z"),
            longitudinal_observation(
                "observation-v2",
                "observation-v1",
                "evidence-v2",
                observed_at="2026-02-01T00:00:00Z",
            ),
        )
        self.assertTrue(any("forward reference" in error for error in errors))

    def test_same_time_prior_fails_strict_ordering(self) -> None:
        timestamp = "2026-02-01T00:00:00Z"
        errors = self.create_pair(
            unresolved_observation("observation-v1", observed_at=timestamp),
            longitudinal_observation(
                "observation-v2",
                "observation-v1",
                "evidence-v2",
                observed_at=timestamp,
            ),
        )
        self.assertTrue(any("strictly earlier" in error for error in errors))


class LockedWaveImmutabilityTests(unittest.TestCase):
    def test_add_modify_delete_and_rename_inside_locked_wave_fail(self) -> None:
        locked = {PurePosixPath("data/waves/wave-0")}
        changes = (
            "A\tdata/waves/wave-0/new.json\n"
            "M\tdata/waves/wave-0/manifest.json\n"
            "D\tdata/waves/wave-0/old.json\n"
            "R100\tdata/waves/wave-0/old.json\tdata/waves/wave-0/renamed.json"
        )
        errors = VALIDATE.validate_locked_wave_changes(locked, changes)
        self.assertEqual(4, len(errors))


if __name__ == "__main__":
    unittest.main()
