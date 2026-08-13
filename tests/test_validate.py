from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("observatory_validate", ROOT / "scripts/validate.py")
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)


def complete_locks() -> dict[str, dict[str, str]]:
    lock = {
        "version": "1.0.0",
        "sha256": "a" * 64,
        "locked_at": "2026-01-01T00:00:00Z",
    }
    return {name: dict(lock) for name in VALIDATE.REQUIRED_LOCKS}


class RepositoryValidationTests(unittest.TestCase):
    def test_bootstrap_scaffold_passes(self) -> None:
        self.assertEqual([], VALIDATE.validate_repository(ROOT))

    def test_observation_schema_represents_required_states(self) -> None:
        schema = json.loads((ROOT / "schemas/observation.schema.json").read_text(encoding="utf-8"))
        properties = schema["properties"]
        self.assertIn("unknown", properties["presence_assessment"]["enum"])
        self.assertIn("unknown", properties["human_criticality_state"]["enum"])
        self.assertIn(
            "transition_toward_human_noncriticality",
            properties["event_type"]["enum"],
        )
        self.assertIn("reversal_toward_human_criticality", properties["event_type"]["enum"])
        self.assertIn("human_reentry", properties["event_type"]["enum"])


class WaveGateTests(unittest.TestCase):
    def base_manifest(self) -> dict[str, object]:
        return {
            "wave_id": "wave-0",
            "status": "draft",
            "schema_version": "0.1.0-draft",
            "panel_snapshot": "panel/wave-0.json",
            "registry_snapshot": "registry/wave-0.csv",
            "instrument_locks": {},
        }

    def test_draft_wave_does_not_claim_missing_locks(self) -> None:
        self.assertEqual([], VALIDATE.validate_wave_manifest(self.base_manifest(), "manifest"))

    def test_official_wave_fails_closed_without_locks(self) -> None:
        manifest = self.base_manifest()
        manifest["status"] = "official"
        errors = VALIDATE.validate_wave_manifest(manifest, "manifest")
        for lock_name in VALIDATE.REQUIRED_LOCKS:
            self.assertTrue(any(f"'{lock_name}' lock" in error for error in errors))
        self.assertTrue(any("released_at" in error for error in errors))
        self.assertTrue(any("release_approval" in error for error in errors))

    def test_official_wave_passes_with_complete_locks(self) -> None:
        manifest = self.base_manifest()
        manifest.update(
            {
                "status": "official",
                "instrument_locks": complete_locks(),
                "locked_at": "2026-01-01T00:00:00Z",
                "released_at": "2026-01-02T00:00:00Z",
                "release_approval": "decision-001",
            }
        )
        self.assertEqual([], VALIDATE.validate_wave_manifest(manifest, "manifest"))

    def test_panel_and_registry_snapshots_must_be_distinct(self) -> None:
        manifest = self.base_manifest()
        manifest["registry_snapshot"] = manifest["panel_snapshot"]
        errors = VALIDATE.validate_wave_manifest(manifest, "manifest")
        self.assertTrue(any("must be distinct" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
