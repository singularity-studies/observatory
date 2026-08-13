from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("observatory_validate", ROOT / "scripts/validate.py")
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class TemporaryOfficialWave:
    """Build an empty, structural gate fixture outside the repository."""

    def __init__(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "observatory"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        self.wave_directory = self.root / "data/waves/test-wave"
        self.wave_directory.mkdir(parents=True)
        self.panel_path = self.wave_directory / "panel.json"
        self.registry_path = self.wave_directory / "registry.csv"
        write_json(
            self.panel_path,
            {
                "snapshot_id": "test-empty-panel",
                "instrument_version": "0.2.0-draft",
                "status": "frozen",
                "units": [],
            },
        )
        self.registry_path.write_text(
            ",".join(VALIDATE.REGISTRY_HEADER) + "\n",
            encoding="utf-8",
        )
        self.instruments, errors = VALIDATE.load_instruments(self.root)
        if errors:
            raise AssertionError(errors)
        self.manifest = self._manifest()

    def close(self) -> None:
        self.temporary_directory.cleanup()

    def reference(self, relative: str) -> dict[str, str]:
        return {
            "path": relative,
            "sha256": VALIDATE.sha256_file(self.root / relative),
        }

    def _locks(self) -> dict[str, object]:
        locks: dict[str, object] = {}
        for name in VALIDATE.REQUIRED_LOCKS:
            instrument = self.instruments[VALIDATE.LOCK_INSTRUMENTS[name]]
            locks[name] = {
                "version": instrument["version"],
                "locked_at": "2026-01-01T00:00:00Z",
                "artifacts": [
                    self.reference(relative)
                    for relative in sorted(VALIDATE.REQUIRED_LOCK_ARTIFACTS[name])
                ],
            }
        return locks

    def _manifest(self) -> dict[str, object]:
        return {
            "wave_id": "test-wave",
            "status": "official",
            "schema_version": self.instruments["schema_bundle"]["version"],
            "panel_snapshot": self.reference("data/waves/test-wave/panel.json"),
            "registry_snapshot": self.reference("data/waves/test-wave/registry.csv"),
            "instrument_locks": self._locks(),
            "scientific_records": {"evidence": [], "observations": []},
            "locked_at": "2026-01-01T00:00:00Z",
            "released_at": "2026-01-02T00:00:00Z",
            "release_approval": "test-only-approval",
        }

    def save_manifest(self) -> None:
        write_json(self.wave_directory / "manifest.json", self.manifest)


class RepositoryValidationTests(unittest.TestCase):
    def test_bootstrap_scaffold_passes(self) -> None:
        self.assertEqual([], VALIDATE.validate_repository(ROOT))

    def test_primary_ontology_is_function_and_human_bottleneck_centered(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        panel = (ROOT / "PANEL.md").read_text(encoding="utf-8")
        registry_header = (ROOT / "registry/live-registry.csv").read_text(
            encoding="utf-8"
        ).splitlines()[0]
        for text in (readme, protocol, panel):
            self.assertIn("improvement-loop", text)
            self.assertIn("Human Bottleneck", text)
            self.assertIn("multiple empirical systems", text)
        self.assertEqual(",".join(VALIDATE.REGISTRY_HEADER), registry_header)

    def test_core_question_is_neutral_and_longitudinal_outcomes_are_symmetric(self) -> None:
        question = (
            "How does human criticality change across civilization’s improvement loops, "
            "and where—if anywhere—does it cease to be necessary?"
        )
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn(question, protocol)
        for outcome in ("persistence", "transition", "reversal", "human re-entry"):
            self.assertIn(outcome, protocol.lower())

    def test_measurement_remains_provisional_without_a_fixed_vector(self) -> None:
        codebook = (ROOT / "CODEBOOK.md").read_text(encoding="utf-8")
        schema = json.loads(
            (ROOT / "schemas/observation.schema.json").read_text(encoding="utf-8")
        )
        properties = schema["properties"]
        self.assertIn("provisional_human_criticality_summary", properties)
        self.assertIn("human_participation_presence", properties)
        self.assertNotIn("human_criticality_state", properties)
        self.assertNotIn("presence_assessment", properties)
        for candidate in (
            "capability",
            "loop closure",
            "verification dependence",
            "authority delegation",
            "recursive gain",
            "human dependence",
        ):
            self.assertIn(candidate, codebook)
        self.assertIn("not a fixed vector", codebook)
        self.assertNotIn("[C,L,V,A,R,H]", codebook.replace(" ", ""))

    def test_invalid_scientific_record_is_rejected_by_contract(self) -> None:
        schema = json.loads(
            (ROOT / "schemas/evidence.schema.json").read_text(encoding="utf-8")
        )
        errors = VALIDATE.validate_contract({}, schema, "test evidence")
        self.assertTrue(any("missing required field 'evidence_id'" in error for error in errors))


class OfficialWaveGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = TemporaryOfficialWave()

    def tearDown(self) -> None:
        self.fixture.close()

    def errors(self) -> list[str]:
        self.fixture.save_manifest()
        return VALIDATE.validate_repository(self.fixture.root)

    def test_empty_official_fixture_passes_all_gates(self) -> None:
        self.assertEqual([], self.errors())

    def test_official_wave_without_every_required_lock_is_rejected(self) -> None:
        del self.fixture.manifest["instrument_locks"]["governance"]
        errors = self.errors()
        self.assertTrue(any("missing 'governance' lock" in error for error in errors))

    def test_wave_schema_version_must_match_bundle(self) -> None:
        self.fixture.manifest["schema_version"] = "test-mismatch"
        errors = self.errors()
        self.assertTrue(any("Wave schema_version does not match" in error for error in errors))

    def test_panel_and_registry_snapshots_must_be_distinct(self) -> None:
        self.fixture.manifest["registry_snapshot"] = self.fixture.manifest["panel_snapshot"]
        errors = self.errors()
        self.assertTrue(any("snapshots must be distinct" in error for error in errors))

    def test_fake_well_formed_hash_is_rejected(self) -> None:
        protocol_lock = self.fixture.manifest["instrument_locks"]["protocol"]
        protocol_lock["artifacts"][0]["sha256"] = "a" * 64
        errors = self.errors()
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_unresolved_snapshot_reference_is_rejected(self) -> None:
        self.fixture.manifest["panel_snapshot"] = {
            "path": "data/waves/test-wave/missing-panel.json",
            "sha256": "a" * 64,
        }
        errors = self.errors()
        self.assertTrue(any("artifact does not resolve" in error for error in errors))

    def test_modified_snapshot_hash_is_rejected(self) -> None:
        self.fixture.manifest["panel_snapshot"]["sha256"] = "b" * 64
        errors = self.errors()
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_snapshot_must_be_inside_immutable_wave_directory(self) -> None:
        self.fixture.manifest["panel_snapshot"] = self.fixture.reference("PANEL.md")
        errors = self.errors()
        self.assertTrue(any("must be inside its immutable Wave directory" in error for error in errors))

    def test_instrument_manifest_version_mismatch_is_rejected(self) -> None:
        path = self.fixture.root / "schemas/instruments.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["instruments"][0]["version"] = "test-mismatch"
        write_json(path, manifest)
        errors = self.errors()
        self.assertTrue(any("manifest version 'test-mismatch'" in error for error in errors))

    def test_invalid_record_referenced_by_official_wave_is_rejected(self) -> None:
        relative = "data/waves/test-wave/evidence/invalid.json"
        write_json(self.fixture.root / relative, {})
        self.fixture.manifest["scientific_records"]["evidence"] = [
            self.fixture.reference(relative)
        ]
        errors = self.errors()
        self.assertTrue(any("missing required field 'evidence_id'" in error for error in errors))

    def test_record_versions_and_evidence_references_must_resolve(self) -> None:
        relative = "data/waves/test-wave/observations/invalid-version.json"
        write_json(
            self.fixture.root / relative,
            {
                "protocol_version": "test-wrong-version",
                "codebook_version": "0.2.0-draft",
                "schema_version": "test-wrong-version",
                "evidence_ids": ["test-missing-evidence"],
            },
        )
        self.fixture.manifest["scientific_records"]["observations"] = [
            self.fixture.reference(relative)
        ]
        errors = self.errors()
        self.assertTrue(any("record schema_version does not match" in error for error in errors))
        self.assertTrue(any("protocol_version mismatch" in error for error in errors))
        self.assertTrue(any("unresolved evidence_id" in error for error in errors))

    def test_panel_snapshot_instrument_version_must_match(self) -> None:
        panel = json.loads(self.fixture.panel_path.read_text(encoding="utf-8"))
        panel["instrument_version"] = "test-mismatch"
        write_json(self.fixture.panel_path, panel)
        self.fixture.manifest["panel_snapshot"] = self.fixture.reference(
            "data/waves/test-wave/panel.json"
        )
        errors = self.errors()
        self.assertTrue(any("Frozen Panel snapshot instrument_version mismatch" in error for error in errors))


class LockedWaveImmutabilityTests(unittest.TestCase):
    def test_every_change_type_inside_locked_wave_is_rejected(self) -> None:
        locked = {PurePosixPath("data/waves/wave-0")}
        changes = {
            "addition": "A\tdata/waves/wave-0/new.json",
            "modification": "M\tdata/waves/wave-0/manifest.json",
            "deletion": "D\tdata/waves/wave-0/old.json",
            "rename": (
                "R100\tdata/waves/wave-0/old.json\t"
                "data/waves/wave-0/renamed.json"
            ),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                errors = VALIDATE.validate_locked_wave_changes(locked, change)
                self.assertTrue(any("is immutable" in error for error in errors))

    def test_change_outside_locked_wave_is_allowed(self) -> None:
        locked = {PurePosixPath("data/waves/wave-0")}
        self.assertEqual(
            [],
            VALIDATE.validate_locked_wave_changes(
                locked, "A\tdata/amendments/wave-0/test-only.json"
            ),
        )


if __name__ == "__main__":
    unittest.main()
