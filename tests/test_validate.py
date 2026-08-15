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
NORMALIZATION_SPEC = importlib.util.spec_from_file_location(
    "observatory_normalization_validate", ROOT / "scripts/validate_normalization.py"
)
assert NORMALIZATION_SPEC and NORMALIZATION_SPEC.loader
NORMALIZATION_VALIDATE = importlib.util.module_from_spec(NORMALIZATION_SPEC)
NORMALIZATION_SPEC.loader.exec_module(NORMALIZATION_VALIDATE)

V1 = "1.0.0-test"
V2 = "2.0.0-test"
CURRENT_SELECTION_VERSION = json.loads(
    (ROOT / "schemas/panel-selection-manifest.schema.json").read_text(encoding="utf-8")
)["x-instrument-version"]
CURRENT_DOMAIN_VERSION = json.loads(
    (ROOT / "schemas/domain-universe-manifest.schema.json").read_text(encoding="utf-8")
)["x-instrument-version"]
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
        "domain": "test-only-domain",
        "improvement_loop_id": f"{unit_id}-loop",
        "function_or_stage": f"{unit_id}-function",
        "human_bottleneck_label": "test-only structural label",
        "operational_boundary": "test-only operational boundary",
        "continuity_rule": "test-only continuity rule",
        "boundary_conditions": "test-only structural boundary",
        "empirical_system_ids": [system_id],
    }


def candidate_specification(
    unit_id: str = "test-unit",
    system_id: str = "test-system",
    version: str = CURRENT_SELECTION_VERSION,
) -> dict[str, object]:
    return {
        "candidate_unit_id": unit_id,
        "instrument_version": version,
        "primary_unit_type": "improvement_loop_function_or_stage",
        "domain": "test-only-domain",
        "improvement_loop_id": f"{unit_id}-loop",
        "improvement_loop": "test-only recurrent improvement loop fixture",
        "function_or_stage": f"{unit_id}-function",
        "operational_boundary": "test-only operational boundary",
        "continuity_rule": "test-only continuity rule",
        "boundary_conditions": "test-only structural boundary",
        "empirical_system_ids": [system_id],
    }


def scientific_review_record(
    version: str = CURRENT_SELECTION_VERSION,
    outcome: str = "approved",
    proposal_reference: dict[str, str] | None = None,
    record_id: str = "test-only-scientific-review",
) -> dict[str, object]:
    proposal_reference = proposal_reference or {
        "path": "selection/proposals/test-only-selection-proposal.json",
        "sha256": "0" * 64,
    }
    return {
        "review_record_id": record_id,
        "instrument_version": version,
        "review_type": "panel_selection_scientific_review",
        "selection_proposal": proposal_reference,
        "outcome": outcome,
        "rationale": (
            "TEMPORARY TEST FIXTURE ONLY; exercises structure and does not record "
            "a real scientific review or approval."
        ),
        "responsible_role_id": "test-suite-only-review-role",
        "reviewed_at": "2026-01-01T00:00:00Z",
    }


def governance_decision_record(
    version: str = CURRENT_SELECTION_VERSION,
    outcome: str = "authorized",
    proposal_reference: dict[str, str] | None = None,
    review_reference: dict[str, str] | None = None,
    record_id: str = "test-only-governance-decision",
) -> dict[str, object]:
    proposal_reference = proposal_reference or {
        "path": "selection/proposals/test-only-selection-proposal.json",
        "sha256": "0" * 64,
    }
    review_reference = review_reference or {
        "path": "selection/reviews/test-only-scientific-review.json",
        "sha256": "0" * 64,
    }
    return {
        "governance_decision_id": record_id,
        "instrument_version": version,
        "decision_type": "frozen_panel_lock_authorization",
        "selection_proposal": proposal_reference,
        "scientific_review": review_reference,
        "outcome": outcome,
        "rationale": (
            "TEMPORARY TEST FIXTURE ONLY; exercises structure and does not record "
            "real governance authority or authorization."
        ),
        "responsible_authority_id": "test-suite-only-authority",
        "recorded_at": "2026-01-01T00:00:00Z",
    }


def eligibility_decision(
    candidate_reference: dict[str, str] | None = None,
    unit_id: str = "test-unit",
    version: str = CURRENT_SELECTION_VERSION,
) -> dict[str, object]:
    candidate_reference = candidate_reference or {
        "path": "selection/candidates/test-unit.json",
        "sha256": "0" * 64,
    }
    criterion = {
        "result": "passed",
        "rationale": "test-only structural rationale",
        "uncertainty": "test-only structural uncertainty",
    }
    return {
        "eligibility_decision_id": f"{unit_id}-eligibility",
        "candidate_unit_id": unit_id,
        "instrument_version": version,
        "candidate_specification": candidate_reference,
        "criteria": {name: dict(criterion) for name in VALIDATE.ELIGIBILITY_CRITERIA},
        "decision_status": "eligible",
        "overall_rationale": "test-only structural eligibility fixture",
        "overall_uncertainty": "test-only; no empirical determination",
        "review": {
            "reviewer_status": "unassigned",
            "reviewer_id": None,
            "adjudication_status": "unresolved",
            "adjudicator_id": None,
            "notes": "Temporary structural fixture; reviewer and adjudicator remain unresolved",
        },
    }


def lineage_record(
    retired_id: str = "test-retired-unit",
    successor_id: str = "test-successor-unit",
    version: str = CURRENT_SELECTION_VERSION,
) -> dict[str, object]:
    return {
        "lineage_record_id": f"{retired_id}-lineage",
        "instrument_version": version,
        "retirement_status": "retired",
        "retired_unit": {
            "panel_unit_id": retired_id,
            "primary_unit_type": "improvement_loop_function_or_stage",
            "domain": "test-only-domain",
            "improvement_loop_id": f"{retired_id}-loop",
            "function_or_stage": f"{retired_id}-function",
            "operational_boundary": "test-only boundary",
            "continuity_rule": "test-only continuity rule",
        },
        "retirement": {
            "basis": "function_ceased_to_exist",
            "rationale": "test-only structural retirement fixture",
            "effective_panel_version": "later-test-panel-version",
        },
        "successors": [
            {
                "successor_unit_id": successor_id,
                "relation": "successor",
                "later_panel_version": "later-test-panel-version",
                "rationale": "test-only lineage fixture",
            }
        ],
        "history_note": "Temporary fixture preserves retired identity; no empirical claim",
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

    def selection_schemas(self) -> dict[str, dict[str, object]]:
        return {
            name: json.loads((self.root / relative).read_text(encoding="utf-8"))
            for name, relative in VALIDATE.CURRENT_SCHEMA_PATHS.items()
            if name in VALIDATE.SELECTION_RECORD_PATHS
        }

    def create_locked_selection(
        self,
        base_relative: str = "selection",
        units: list[dict[str, object]] | None = None,
        version: str = CURRENT_SELECTION_VERSION,
        protocol_reference: dict[str, str] | None = None,
    ) -> tuple[dict[str, object], dict[str, str]]:
        units = units if units is not None else [panel_unit()]
        if protocol_reference is None:
            protocol_relative = f"{base_relative}/protocol.md"
            text = (self.root / "PANEL.md").read_text(encoding="utf-8")
            text = re.sub(
                r"Instrument version:\s*`[^`]+`",
                f"Instrument version: `{version}`",
                text,
                count=1,
            )
            protocol_path = self.root / protocol_relative
            protocol_path.parent.mkdir(parents=True, exist_ok=True)
            protocol_path.write_text(text, encoding="utf-8")
            protocol_reference = self.reference(protocol_relative)

        candidate_references: list[dict[str, str]] = []
        eligibility_references: list[dict[str, str]] = []
        selection_dispositions: list[dict[str, str]] = []
        selected_ids: list[str] = []
        for unit in units:
            unit_id = str(unit["panel_unit_id"])
            systems = unit.get("empirical_system_ids", [])
            system_id = str(systems[0]) if systems else "test-system"
            candidate_relative = f"{base_relative}/candidates/{unit_id}.json"
            write_json(
                self.root / candidate_relative,
                candidate_specification(unit_id, system_id, version),
            )
            candidate_reference = self.reference(candidate_relative)
            candidate_references.append(candidate_reference)

            decision_relative = f"{base_relative}/eligibility/{unit_id}.json"
            write_json(
                self.root / decision_relative,
                eligibility_decision(candidate_reference, unit_id, version),
            )
            eligibility_references.append(self.reference(decision_relative))
            selection_dispositions.append(
                {
                    "candidate_unit_id": unit_id,
                    "disposition": "selected",
                    "rationale": "test-only structural selection fixture",
                    "uncertainty": "test-only; no empirical determination",
                }
            )
            selected_ids.append(unit_id)

        selection_protocol = {
            "status": "locked",
            "version": version,
            "artifact": protocol_reference,
        }
        candidate_universe_snapshot = {
            "snapshot_id": "test-only-candidate-universe",
            "captured_at": "2026-01-01T00:00:00Z",
            "candidate_specifications": candidate_references,
        }
        coverage_redundancy_review = {
            "status": "recorded",
            "rationale": (
                "TEMPORARY TEST FIXTURE ONLY; no real selection or approval."
            ),
            "uncertainty": "test-only; no empirical coverage determination",
        }
        panel_size = {
            "status": "fixed",
            "n": len(selected_ids),
            "rationale": "test-only fixture size; not a proposed panel N",
        }
        proposal = {
            "proposal_id": "test-only-selection-proposal",
            "instrument_version": version,
            "proposal_type": "frozen_panel_selection",
            "selection_protocol": selection_protocol,
            "candidate_universe_snapshot": candidate_universe_snapshot,
            "eligibility_decisions": eligibility_references,
            "lineage_relations": [],
            "coverage_redundancy_review": coverage_redundancy_review,
            "panel_size": panel_size,
            "selection_dispositions": selection_dispositions,
            "selected_unit_ids": selected_ids,
            "created_at": "2026-01-01T00:00:00Z",
        }
        proposal_relative = f"{base_relative}/proposals/test-only-selection-proposal.json"
        write_json(self.root / proposal_relative, proposal)
        proposal_reference = self.reference(proposal_relative)

        review_relative = f"{base_relative}/reviews/test-only-scientific-review.json"
        write_json(
            self.root / review_relative,
            scientific_review_record(version, proposal_reference=proposal_reference),
        )
        review_reference = self.reference(review_relative)
        authority_relative = (
            f"{base_relative}/governance/test-only-governance-decision.json"
        )
        write_json(
            self.root / authority_relative,
            governance_decision_record(
                version,
                proposal_reference=proposal_reference,
                review_reference=review_reference,
            ),
        )

        manifest: dict[str, object] = {
            "selection_manifest_id": "test-only-selection-manifest",
            "instrument_version": version,
            "status": "locked",
            "selection_proposal": proposal_reference,
            "selection_protocol": selection_protocol,
            "candidate_universe_snapshot": candidate_universe_snapshot,
            "eligibility_decisions": eligibility_references,
            "lineage_relations": [],
            "coverage_redundancy_review": coverage_redundancy_review,
            "panel_size": panel_size,
            "selection_dispositions": selection_dispositions,
            "selected_unit_ids": selected_ids,
            "scientific_review": {
                "status": "complete",
                "review_record": review_reference,
            },
            "governance_authority": {
                "status": "recorded",
                "authority_id": "test-suite-only-authority",
                "decision_record": self.reference(authority_relative),
            },
            "locked_at": "2026-01-01T00:00:00Z",
        }
        manifest_relative = f"{base_relative}/manifest.json"
        write_json(self.root / manifest_relative, manifest)
        return manifest, self.reference(manifest_relative)

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

        selection_manifest, selection_reference = self.create_locked_selection(
            f"data/waves/{wave}/selection",
            units,
            version,
            instrument_locks["panel"]["artifacts"][0],
        )

        candidate_references = selection_manifest["candidate_universe_snapshot"][
            "candidate_specifications"
        ]
        frozen_units = []
        for unit, candidate_reference in zip(units, candidate_references, strict=True):
            frozen_unit = dict(unit)
            frozen_unit["candidate_specification"] = candidate_reference
            frozen_units.append(frozen_unit)

        panel_relative = f"data/waves/{wave}/panel.json"
        write_json(
            self.root / panel_relative,
            {
                "snapshot_id": f"{wave}-test-panel",
                "instrument_version": version,
                "status": "frozen",
                "selection_manifest": selection_reference,
                "units": frozen_units,
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

        for path in (self.root / "domain-universe").rglob("*.json"):
            if "normalization" in path.relative_to(self.root / "domain-universe").parts:
                # Pass 1 records are version-bound scientific-stage artifacts,
                # not current instruments advanced by this Wave isolation fixture.
                continue
            record = json.loads(path.read_text(encoding="utf-8"))
            if "instrument_version" in record:
                record["instrument_version"] = V2
                write_json(path, record)


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


class FrozenPanelSelectionProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate_schema = json.loads(
            (ROOT / "schemas/candidate-unit.schema.json").read_text(encoding="utf-8")
        )
        self.eligibility_schema = json.loads(
            (ROOT / "schemas/eligibility-decision.schema.json").read_text(encoding="utf-8")
        )
        self.lineage_schema = json.loads(
            (ROOT / "schemas/panel-lineage.schema.json").read_text(encoding="utf-8")
        )

    def test_product_or_model_as_primary_unit_is_rejected(self) -> None:
        for prohibited_type in ("product", "ai_model"):
            record = candidate_specification()
            record["primary_unit_type"] = prohibited_type
            errors = VALIDATE.validate_candidate_unit(
                record, self.candidate_schema, f"test {prohibited_type}"
            )
            self.assertTrue(errors)

    def test_missing_continuity_rule_fails(self) -> None:
        record = candidate_specification()
        del record["continuity_rule"]
        errors = VALIDATE.validate_candidate_unit(record, self.candidate_schema, "test candidate")
        self.assertTrue(any("continuity_rule" in error for error in errors))

    def test_baseline_status_is_not_a_selection_variable(self) -> None:
        panel = (ROOT / "PANEL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        exact_principle = "Baseline human-criticality status is not a selection variable."
        timing_principle = (
            "Baseline human-criticality is first coded after panel lock as a "
            "Wave-observation outcome."
        )
        self.assertIn(exact_principle, panel)
        self.assertIn(exact_principle, protocol)
        self.assertIn(timing_principle, panel.replace("\n", " "))
        self.assertIn(timing_principle, protocol)
        self.assertNotIn("outcome-blind", panel.lower())
        self.assertNotIn("outcome-blind", protocol.lower())
        self.assertNotIn("outcome-blind", agents.lower())
        self.assertNotIn("baseline_human_criticality", self.candidate_schema["properties"])
        self.assertNotIn(
            "baseline_human_criticality", json.dumps(self.eligibility_schema)
        )
        record = candidate_specification()
        record["baseline_human_criticality"] = "unknown"
        self.assertTrue(
            VALIDATE.validate_candidate_unit(record, self.candidate_schema, "test outcome leak")
        )
        observation_schema = json.loads(
            (ROOT / "schemas/observation.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {
                "human_critical",
                "mixed_or_contested",
                "human_noncritical",
                "unknown",
            },
            set(
                observation_schema["properties"]["provisional_human_criticality_summary"][
                    "enum"
                ]
            ),
        )

    def test_anti_selection_bias_and_panel_size_remain_explicit(self) -> None:
        panel = (ROOT / "PANEL.md").read_text(encoding="utf-8")
        self.assertIn(
            "Do not optimize the Frozen Panel for excitement. Optimize it for re-observability.",
            panel,
        )
        self.assertIn("Panel size remains unresolved", panel)
        self.assertNotIn("final N is 50", panel)

    def test_templates_are_fail_closed_non_records(self) -> None:
        contracts = {
            "candidate-unit.template.json": self.candidate_schema,
            "eligibility-decision.template.json": self.eligibility_schema,
            "panel-lineage.template.json": self.lineage_schema,
            "panel-selection-manifest.template.json": json.loads(
                (ROOT / "schemas/panel-selection-manifest.schema.json").read_text(
                    encoding="utf-8"
                )
            ),
            "panel-selection-proposal.template.json": json.loads(
                (ROOT / "schemas/panel-selection-proposal.schema.json").read_text(
                    encoding="utf-8"
                )
            ),
            "panel-selection-review.template.json": json.loads(
                (ROOT / "schemas/panel-selection-review.schema.json").read_text(
                    encoding="utf-8"
                )
            ),
            "panel-lock-governance-decision.template.json": json.loads(
                (ROOT / "schemas/panel-lock-governance-decision.schema.json").read_text(
                    encoding="utf-8"
                )
            ),
        }
        for filename, schema in contracts.items():
            template = json.loads(
                (ROOT / "schemas/templates" / filename).read_text(encoding="utf-8")
            )
            self.assertTrue(template["_template_notice"].startswith("INTENTIONALLY INVALID"))
            self.assertTrue(VALIDATE.validate_contract(template, schema, f"template {filename}"))

    def test_unresolved_criterion_cannot_produce_eligible_status(self) -> None:
        record = eligibility_decision()
        record["criteria"]["re_observability"]["result"] = "unresolved"
        errors = VALIDATE.validate_contract(record, self.eligibility_schema, "test eligibility")
        self.assertTrue(errors)

    def test_failed_criterion_cannot_produce_eligible_status(self) -> None:
        record = eligibility_decision()
        record["criteria"]["non_redundancy"]["result"] = "failed"
        errors = VALIDATE.validate_contract(record, self.eligibility_schema, "test eligibility")
        self.assertTrue(errors)

    def test_all_eight_eligibility_criteria_are_required(self) -> None:
        record = eligibility_decision()
        del record["criteria"]["evidence_traceability"]
        errors = VALIDATE.validate_contract(record, self.eligibility_schema, "test eligibility")
        self.assertTrue(any("evidence_traceability" in error for error in errors))
        self.assertEqual(8, len(VALIDATE.ELIGIBILITY_CRITERIA))

    def test_retired_unit_is_not_deleted_from_lineage_history(self) -> None:
        record = lineage_record()
        del record["retired_unit"]
        errors = VALIDATE.validate_lineage_record(record, self.lineage_schema, "test lineage")
        self.assertTrue(any("retired_unit" in error for error in errors))

    def test_replacement_cannot_reuse_retired_unit_id(self) -> None:
        record = lineage_record(successor_id="test-retired-unit")
        errors = VALIDATE.validate_lineage_record(record, self.lineage_schema, "test lineage")
        self.assertTrue(any("cannot reuse retired panel_unit_id" in error for error in errors))

    def _validate_manifest_change(self, mutate) -> list[str]:
        repository = TemporaryRepository()
        try:
            manifest, _ = repository.create_locked_selection()
            mutate(manifest)
            _, errors = VALIDATE.validate_selection_manifest(
                repository.root,
                manifest,
                "test selection manifest",
                repository.selection_schemas(),
                PurePosixPath("selection"),
                CURRENT_SELECTION_VERSION,
            )
            return errors
        finally:
            repository.close()

    def _validate_manifest_repository_change(
        self,
        mutate,
        units: list[dict[str, object]] | None = None,
    ) -> list[str]:
        repository = TemporaryRepository()
        try:
            manifest, _ = repository.create_locked_selection(units=units)
            mutate(repository, manifest)
            _, errors = VALIDATE.validate_selection_manifest(
                repository.root,
                manifest,
                "test selection manifest",
                repository.selection_schemas(),
                PurePosixPath("selection"),
                CURRENT_SELECTION_VERSION,
            )
            return errors
        finally:
            repository.close()

    def _eligibility_errors(self, mutate) -> list[str]:
        repository = TemporaryRepository()
        try:
            candidate_relative = "selection/candidates/test-unit.json"
            write_json(repository.root / candidate_relative, candidate_specification())
            record = eligibility_decision(repository.reference(candidate_relative))
            mutate(record)
            return VALIDATE.validate_eligibility_decision(
                repository.root,
                record,
                "test eligibility",
                self.eligibility_schema,
                self.candidate_schema,
                CURRENT_SELECTION_VERSION,
                PurePosixPath("selection"),
            )
        finally:
            repository.close()

    def _create_alternate_proposal(
        self,
        repository: TemporaryRepository,
        manifest: dict[str, object],
    ) -> dict[str, str]:
        original_reference = manifest["selection_proposal"]
        proposal = json.loads(
            (repository.root / original_reference["path"]).read_text(encoding="utf-8")
        )
        proposal["proposal_id"] = "test-only-selection-proposal-b"
        proposal["created_at"] = "2026-01-01T00:00:01Z"
        relative = "selection/proposals/test-only-selection-proposal-b.json"
        write_json(repository.root / relative, proposal)
        return repository.reference(relative)

    def _create_review_for_proposal(
        self,
        repository: TemporaryRepository,
        proposal_reference: dict[str, str],
        record_id: str,
    ) -> dict[str, str]:
        relative = f"selection/reviews/{record_id}.json"
        write_json(
            repository.root / relative,
            scientific_review_record(
                proposal_reference=proposal_reference,
                record_id=record_id,
            ),
        )
        return repository.reference(relative)

    def test_complete_temporary_selection_fixture_passes_internal_gate_only(self) -> None:
        repository = TemporaryRepository()
        try:
            manifest, _ = repository.create_locked_selection()
            _, errors = VALIDATE.validate_selection_manifest(
                repository.root,
                manifest,
                "test selection manifest",
                repository.selection_schemas(),
                PurePosixPath("selection"),
                CURRENT_SELECTION_VERSION,
            )
            self.assertEqual([], errors)
            for reference in (
                manifest["selection_proposal"],
                manifest["scientific_review"]["review_record"],
                manifest["governance_authority"]["decision_record"],
            ):
                fixture_text = (repository.root / reference["path"]).read_text(
                    encoding="utf-8"
                )
                self.assertIn("TEMPORARY TEST FIXTURE ONLY", fixture_text)
            self.assertIn(
                "no real selection or approval",
                (repository.root / manifest["selection_proposal"]["path"]).read_text(
                    encoding="utf-8"
                ),
            )
            self.assertIn(
                "does not record a real scientific review or approval",
                (repository.root / manifest["scientific_review"]["review_record"]["path"])
                .read_text(encoding="utf-8"),
            )
            self.assertIn(
                "does not record real governance authority or authorization",
                (repository.root / manifest["governance_authority"]["decision_record"]["path"])
                .read_text(encoding="utf-8"),
            )
        finally:
            repository.close()

    def test_every_universe_member_requires_exactly_one_decision(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            manifest["eligibility_decisions"].pop()

        errors = self._validate_manifest_repository_change(
            mutate,
            [panel_unit("test-unit-1"), panel_unit("test-unit-2")],
        )
        self.assertTrue(any("requires exactly one eligibility decision" in error for error in errors))

    def test_duplicate_eligibility_decision_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            manifest["eligibility_decisions"].append(manifest["eligibility_decisions"][0])

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("duplicate eligibility_decision_id" in error for error in errors))

    def test_decision_outside_candidate_universe_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            candidate_relative = "selection/candidates/outside-unit.json"
            write_json(
                repository.root / candidate_relative,
                candidate_specification("outside-unit"),
            )
            decision_relative = "selection/eligibility/outside-unit.json"
            write_json(
                repository.root / decision_relative,
                eligibility_decision(
                    repository.reference(candidate_relative),
                    "outside-unit",
                ),
            )
            manifest["eligibility_decisions"].append(repository.reference(decision_relative))

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("refer outside candidate universe" in error for error in errors))

    def test_all_passed_deterministically_requires_eligible(self) -> None:
        errors = self._eligibility_errors(
            lambda record: record.__setitem__("decision_status", "ineligible")
        )
        self.assertTrue(any("deterministically be 'eligible'" in error for error in errors))

    def test_any_failed_deterministically_produces_ineligible(self) -> None:
        def mutate(record: dict[str, object]) -> None:
            record["criteria"]["non_redundancy"]["result"] = "failed"
            record["decision_status"] = "ineligible"

        self.assertEqual([], self._eligibility_errors(mutate))

    def test_unresolved_without_failure_deterministically_produces_unresolved(self) -> None:
        def mutate(record: dict[str, object]) -> None:
            record["criteria"]["re_observability"]["result"] = "unresolved"
            record["decision_status"] = "unresolved"

        self.assertEqual([], self._eligibility_errors(mutate))

    def test_every_eligible_candidate_requires_selection_disposition(self) -> None:
        errors = self._validate_manifest_change(
            lambda manifest: manifest["selection_dispositions"].clear()
        )
        self.assertTrue(any("lack selection disposition" in error for error in errors))

    def test_not_selected_requires_rationale_and_uncertainty(self) -> None:
        def mutate(manifest: dict[str, object]) -> None:
            disposition = manifest["selection_dispositions"][0]
            disposition["disposition"] = "not_selected"
            disposition["rationale"] = ""
            disposition["uncertainty"] = ""
            manifest["selected_unit_ids"] = []
            manifest["panel_size"]["n"] = 1

        errors = self._validate_manifest_change(mutate)
        self.assertTrue(any("not_selected requires rationale and uncertainty" in error for error in errors))

    def test_selected_ids_must_exactly_equal_selected_dispositions(self) -> None:
        errors = self._validate_manifest_change(
            lambda manifest: manifest["selected_unit_ids"].clear()
        )
        self.assertTrue(any("exactly equal selected dispositions" in error for error in errors))

    def test_selection_manifest_cannot_lock_without_fixed_panel_size(self) -> None:
        def mutate(manifest: dict[str, object]) -> None:
            manifest["panel_size"] = {
                "status": "unresolved",
                "n": None,
                "rationale": "not prospectively fixed",
            }

        errors = self._validate_manifest_change(mutate)
        self.assertTrue(any("prospectively fixed panel size" in error for error in errors))

    def test_selection_manifest_cannot_lock_without_coverage_review(self) -> None:
        def mutate(manifest: dict[str, object]) -> None:
            manifest["coverage_redundancy_review"] = {
                "status": "unresolved",
                "rationale": "",
                "uncertainty": "unresolved",
            }

        errors = self._validate_manifest_change(mutate)
        self.assertTrue(any("coverage/redundancy review" in error for error in errors))

    def test_empty_candidate_universe_cannot_lock_panel(self) -> None:
        def mutate(manifest: dict[str, object]) -> None:
            manifest["candidate_universe_snapshot"]["candidate_specifications"] = []

        errors = self._validate_manifest_change(mutate)
        self.assertTrue(any("empty candidate universe" in error for error in errors))

    def test_selected_unit_requires_complete_eligibility_record(self) -> None:
        def mutate(manifest: dict[str, object]) -> None:
            manifest["eligibility_decisions"] = []

        errors = self._validate_manifest_change(mutate)
        self.assertTrue(any("requires exactly one eligibility decision" in error for error in errors))

    def test_locked_selection_requires_protocol_and_governance_records(self) -> None:
        def mutate(manifest: dict[str, object]) -> None:
            manifest["selection_protocol"]["status"] = "draft"
            manifest["governance_authority"] = {
                "status": "unresolved",
                "authority_id": None,
                "decision_record": None,
            }

        errors = self._validate_manifest_change(mutate)
        self.assertTrue(any("locked protocol" in error for error in errors))
        self.assertTrue(any("governance authority" in error for error in errors))

    def test_review_for_proposal_a_cannot_approve_proposal_b(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            manifest["selection_proposal"] = self._create_alternate_proposal(
                repository, manifest
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(
            any("scientific review does not bind the exact selection proposal" in error for error in errors)
        )

    def test_manifest_selection_content_must_match_exact_proposal(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            manifest["coverage_redundancy_review"]["rationale"] = (
                "different temporary manifest-only rationale"
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(
            any("must exactly match the hash-bound selection proposal" in error for error in errors)
        )

    def test_wrong_selection_proposal_record_identity_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["selection_proposal"]
            proposal = json.loads(
                (repository.root / reference["path"]).read_text(encoding="utf-8")
            )
            proposal["proposal_id"] = "wrong-proposal-identity"
            write_json(repository.root / reference["path"], proposal)
            manifest["selection_proposal"] = repository.reference(reference["path"])

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("proposal_id must exactly match" in error for error in errors))

    def test_governance_for_proposal_a_cannot_authorize_proposal_b(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            proposal_b = self._create_alternate_proposal(repository, manifest)
            review_b = self._create_review_for_proposal(
                repository,
                proposal_b,
                "test-only-scientific-review-b",
            )
            manifest["selection_proposal"] = proposal_b
            manifest["scientific_review"]["review_record"] = review_b

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(
            any("governance decision does not bind the exact selection proposal" in error for error in errors)
        )

    def test_governance_referencing_different_scientific_review_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            alternate_review = self._create_review_for_proposal(
                repository,
                manifest["selection_proposal"],
                "test-only-scientific-review-b",
            )
            governance_reference = manifest["governance_authority"]["decision_record"]
            governance = json.loads(
                (repository.root / governance_reference["path"]).read_text(encoding="utf-8")
            )
            governance["scientific_review"] = alternate_review
            write_json(repository.root / governance_reference["path"], governance)
            manifest["governance_authority"]["decision_record"] = repository.reference(
                governance_reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(
            any("governance decision does not bind the exact scientific review" in error for error in errors)
        )

    def test_tampered_selection_proposal_fails_sha_binding(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            proposal_reference = manifest["selection_proposal"]
            proposal = json.loads(
                (repository.root / proposal_reference["path"]).read_text(encoding="utf-8")
            )
            proposal["created_at"] = "2026-01-01T00:00:02Z"
            write_json(repository.root / proposal_reference["path"], proposal)

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_tampered_review_binding_fails_governance_authorization(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            review_reference = manifest["scientific_review"]["review_record"]
            review = json.loads(
                (repository.root / review_reference["path"]).read_text(encoding="utf-8")
            )
            review["rationale"] = (
                "TEMPORARY TEST FIXTURE ONLY; changed test rationale and no real approval."
            )
            write_json(repository.root / review_reference["path"], review)
            manifest["scientific_review"]["review_record"] = repository.reference(
                review_reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(
            any("governance decision does not bind the exact scientific review" in error for error in errors)
        )

    def test_wrong_scientific_review_record_identity_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["scientific_review"]["review_record"]
            review = json.loads(
                (repository.root / reference["path"]).read_text(encoding="utf-8")
            )
            review["review_record_id"] = "wrong-review-identity"
            write_json(repository.root / reference["path"], review)
            manifest["scientific_review"]["review_record"] = repository.reference(
                reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("review_record_id must exactly match" in error for error in errors))

    def test_wrong_governance_record_identity_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["governance_authority"]["decision_record"]
            decision = json.loads(
                (repository.root / reference["path"]).read_text(encoding="utf-8")
            )
            decision["governance_decision_id"] = "wrong-governance-identity"
            write_json(repository.root / reference["path"], decision)
            manifest["governance_authority"]["decision_record"] = repository.reference(
                reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(
            any("governance_decision_id must exactly match" in error for error in errors)
        )

    def test_replayed_review_outside_canonical_directory_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            review_reference = manifest["scientific_review"]["review_record"]
            review = json.loads(
                (repository.root / review_reference["path"]).read_text(encoding="utf-8")
            )
            replay_relative = "selection/replayed/test-only-scientific-review.json"
            write_json(repository.root / replay_relative, review)
            replay_reference = repository.reference(replay_relative)
            manifest["scientific_review"]["review_record"] = replay_reference

            governance_reference = manifest["governance_authority"]["decision_record"]
            governance = json.loads(
                (repository.root / governance_reference["path"]).read_text(encoding="utf-8")
            )
            governance["scientific_review"] = replay_reference
            write_json(repository.root / governance_reference["path"], governance)
            manifest["governance_authority"]["decision_record"] = repository.reference(
                governance_reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("record must be inside selection/reviews/" in error for error in errors))

    def test_arbitrary_text_cannot_satisfy_scientific_review(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["scientific_review"]["review_record"]
            path = repository.root / reference["path"]
            path.write_text("approved", encoding="utf-8")
            manifest["scientific_review"]["review_record"] = repository.reference(
                reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("invalid JSON" in error for error in errors))

    def test_rejected_scientific_review_cannot_lock_panel(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["scientific_review"]["review_record"]
            write_json(
                repository.root / reference["path"],
                scientific_review_record(outcome="rejected"),
            )
            manifest["scientific_review"]["review_record"] = repository.reference(
                reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("explicitly approved scientific review" in error for error in errors))

    def test_scientific_review_wrong_type_or_version_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["scientific_review"]["review_record"]
            record = scientific_review_record(version="wrong-version")
            record["review_type"] = "frozen_panel_lock_authorization"
            write_json(repository.root / reference["path"], record)
            manifest["scientific_review"]["review_record"] = repository.reference(
                reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("review_type" in error for error in errors))
        self.assertTrue(any("scientific review instrument_version mismatch" in error for error in errors))

    def test_tampered_scientific_review_fails_sha_binding(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["scientific_review"]["review_record"]
            record = json.loads((repository.root / reference["path"]).read_text(encoding="utf-8"))
            record["rationale"] = "tampered test fixture"
            write_json(repository.root / reference["path"], record)

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_unauthorized_governance_decision_cannot_lock_panel(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["governance_authority"]["decision_record"]
            write_json(
                repository.root / reference["path"],
                governance_decision_record(outcome="unauthorized"),
            )
            manifest["governance_authority"]["decision_record"] = repository.reference(
                reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("explicitly authorized governance decision" in error for error in errors))

    def test_governance_wrong_identity_or_version_fails(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["governance_authority"]["decision_record"]
            record = governance_decision_record(version="wrong-version")
            record["decision_type"] = "panel_selection_scientific_review"
            record["responsible_authority_id"] = "different-test-authority"
            write_json(repository.root / reference["path"], record)
            manifest["governance_authority"]["decision_record"] = repository.reference(
                reference["path"]
            )

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("decision_type" in error for error in errors))
        self.assertTrue(any("governance decision instrument_version mismatch" in error for error in errors))
        self.assertTrue(any("governance authority identity mismatch" in error for error in errors))

    def test_tampered_governance_decision_fails_sha_binding(self) -> None:
        def mutate(repository: TemporaryRepository, manifest: dict[str, object]) -> None:
            reference = manifest["governance_authority"]["decision_record"]
            record = json.loads((repository.root / reference["path"]).read_text(encoding="utf-8"))
            record["rationale"] = "tampered test fixture"
            write_json(repository.root / reference["path"], record)

        errors = self._validate_manifest_repository_change(mutate)
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_initial_repository_remains_pre_wave_zero_without_candidates(self) -> None:
        self.assertEqual([], list((ROOT / "selection").rglob("*.json")))
        self.assertEqual([ROOT / "data/waves/README.md"], list((ROOT / "data/waves").rglob("*")))
        registry_lines = (ROOT / "registry/live-registry.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(1, len(registry_lines))
        panel = (ROOT / "PANEL.md").read_text(encoding="utf-8")
        self.assertIn("No candidate units have been recorded", panel)
        self.assertIn("Panel size remains unresolved", panel)


class TemporaryDomainRepository(TemporaryRepository):
    """Temporary structural Domain Universe fixtures; never scientific records."""

    def domain_schemas(self) -> dict[str, dict[str, object]]:
        return {
            name: json.loads((self.root / relative).read_text(encoding="utf-8"))
            for name, relative in VALIDATE.DOMAIN_SCHEMA_PATHS.items()
        }

    def create_locked_domain_universe(self) -> dict[str, object]:
        version = CURRENT_DOMAIN_VERSION
        boundary = {
            "boundary_specification_id": "test-only-boundary",
            "instrument_version": version,
            "status": "fixed",
            "domain_definition": (
                "A domain is a relatively stable locus of recurrent improvement activity, "
                "defined for coverage and sampling rather than as an exclusive ontological category."
            ),
            "coverage_question": (
                "What parts of civilization's recurrent improvement activity could our "
                "Frozen Panel systematically miss?"
            ),
            "in_scope": {
                "recurrent_improvement_activity": "TEMPORARY TEST FIXTURE ONLY; no real boundary.",
                "later_cycle_change": "TEMPORARY TEST FIXTURE ONLY; no real boundary.",
                "human_criticality_investigability": "TEMPORARY TEST FIXTURE ONLY; no real boundary.",
            },
            "research_universe_distinctions": {
                key: "TEMPORARY TEST FIXTURE ONLY; no substantive distinction."
                for key in (
                    "all_human_activity",
                    "all_economic_sectors",
                    "all_ai_applications",
                    "all_occupations",
                    "all_tasks",
                    "generic_automation",
                )
            },
            "rationale": "TEMPORARY TEST FIXTURE ONLY; not a real universe boundary.",
            "fixed_at": "2026-01-01T00:00:00Z",
        }
        boundary_relative = "domain-universe/boundaries/test-only-boundary.json"
        write_json(self.root / boundary_relative, boundary)

        frame_references: list[dict[str, str]] = []
        for index, family in enumerate(("scientific_research", "economic_activity"), 1):
            frame_id = f"test-only-frame-{index}"
            frame = {
                "source_frame_id": frame_id,
                "instrument_version": version,
                "canonical_name": f"Temporary source frame {index}",
                "classification_family": family,
                "source_identity": "TEMPORARY TEST FIXTURE ONLY; no real source selected.",
                "source_version_or_date": "test-only-version",
                "source_uri": f"urn:test:{frame_id}",
                "source_lineage_id": f"test-only-lineage-{index}",
                "independence_group": f"test-only-independent-group-{index}",
                "independence_basis": (
                    "TEMPORARY TEST FIXTURE ONLY; structurally distinct lineage for validation."
                ),
                "audit_note": "TEMPORARY TEST FIXTURE ONLY; independently auditable structure only.",
                "registered_at": "2026-01-01T00:00:00Z",
                "normalization_status": "complete",
                "normalization_note": "TEMPORARY TEST FIXTURE ONLY; no real normalization.",
            }
            relative = f"domain-universe/source-frames/{frame_id}.json"
            write_json(self.root / relative, frame)
            frame_references.append(self.reference(relative))

        domain_ids = ("test-only-domain-a", "test-only-domain-b")
        extraction_references: list[dict[str, str]] = []
        for index, (frame_reference, domain_id) in enumerate(
            zip(frame_references, domain_ids), 1
        ):
            extraction_id = f"test-only-extraction-{index}"
            extraction = {
                "extraction_id": extraction_id,
                "instrument_version": version,
                "source_frame": frame_reference,
                "extraction_scope": "TEMPORARY TEST FIXTURE ONLY; no real extraction scope.",
                "traversal_or_selection_rule": (
                    "TEMPORARY TEST FIXTURE ONLY; no real traversal or selection."
                ),
                "extraction_status": "complete",
                "extracted_entries": [
                    {
                        "source_entry_id": f"test-only-entry-{index}",
                        "source_entry_reference": "urn:test:source-entry",
                        "source_entry_descriptor": (
                            "TEMPORARY TEST FIXTURE ONLY; no real source descriptor."
                        ),
                        "normalization_disposition": "candidate_created",
                        "target_domain_candidate_ids": [domain_id],
                        "rationale": (
                            "TEMPORARY TEST FIXTURE ONLY; no scientific normalization."
                        ),
                    }
                ],
                "rationale": "TEMPORARY TEST FIXTURE ONLY; no real extraction rationale.",
                "uncertainty": "TEMPORARY TEST FIXTURE ONLY; unresolved scientifically.",
                "recorded_at": "2026-01-01T00:00:00Z",
            }
            relative = f"domain-universe/extractions/{extraction_id}.json"
            write_json(self.root / relative, extraction)
            extraction_references.append(self.reference(relative))

        candidate_references: list[dict[str, str]] = []
        eligibility_references: list[dict[str, str]] = []
        for index, domain_id in enumerate(domain_ids, 1):
            candidate = {
                "domain_candidate_id": domain_id,
                "instrument_version": version,
                "primary_unit_type": "coverage_stratum",
                "canonical_label": f"Temporary domain {index}",
                "scope_definition": "TEMPORARY TEST FIXTURE ONLY; no real domain scope.",
                "inclusion_boundary": "TEMPORARY TEST FIXTURE ONLY; no real inclusion boundary.",
                "exclusion_boundary": "TEMPORARY TEST FIXTURE ONLY; no real exclusion boundary.",
                "recurrent_improvement_rationale": "TEMPORARY TEST FIXTURE ONLY; no empirical claim.",
                "continuity_rule": "TEMPORARY TEST FIXTURE ONLY; no real continuity determination.",
                "overlap_notes": "TEMPORARY TEST FIXTURE ONLY; overlap not empirically assessed.",
                "provenance_references": [
                    {
                        "source_extraction": extraction_references[index - 1],
                        "source_entry_id": f"test-only-entry-{index}",
                    }
                ],
            }
            candidate_relative = f"domain-universe/candidates/{domain_id}.json"
            write_json(self.root / candidate_relative, candidate)
            candidate_reference = self.reference(candidate_relative)
            candidate_references.append(candidate_reference)

            criterion = {
                "result": "passed",
                "rationale": "TEMPORARY TEST FIXTURE ONLY; no scientific determination.",
                "uncertainty": "TEMPORARY TEST FIXTURE ONLY; no empirical assessment.",
            }
            decision_id = f"{domain_id}-eligibility"
            decision = {
                "domain_eligibility_decision_id": decision_id,
                "domain_candidate_id": domain_id,
                "instrument_version": version,
                "domain_candidate": candidate_reference,
                "criteria": {
                    name: dict(criterion) for name in VALIDATE.DOMAIN_ELIGIBILITY_CRITERIA
                },
                "decision_status": "eligible",
                "overall_rationale": "TEMPORARY TEST FIXTURE ONLY; no real eligibility decision.",
                "overall_uncertainty": "TEMPORARY TEST FIXTURE ONLY; no empirical assessment.",
            }
            decision_relative = f"domain-universe/eligibility/{decision_id}.json"
            write_json(self.root / decision_relative, decision)
            eligibility_references.append(self.reference(decision_relative))

        audit_answer = {
            "finding": "TEMPORARY TEST FIXTURE ONLY; no coverage finding.",
            "uncertainty": "TEMPORARY TEST FIXTURE ONLY; unresolved scientifically.",
        }
        proposal = {
            "domain_universe_proposal_id": "test-only-domain-universe-proposal",
            "instrument_version": version,
            "proposal_type": "domain_universe",
            "universe_boundary": self.reference(boundary_relative),
            "source_frames": frame_references,
            "source_extractions": extraction_references,
            "domain_candidates": candidate_references,
            "eligibility_decisions": eligibility_references,
            "domain_relations": [],
            "overlap_duplication_review": {
                "status": "complete",
                "candidate_pair_assessments": [
                    {
                        "left_domain_candidate_id": domain_ids[0],
                        "right_domain_candidate_id": domain_ids[1],
                        "assessment": "distinct",
                        "relation_ids": [],
                        "rationale": "TEMPORARY TEST FIXTURE ONLY; no empirical distinction.",
                    }
                ],
                "rationale": "TEMPORARY TEST FIXTURE ONLY; no real overlap review.",
                "uncertainty": "TEMPORARY TEST FIXTURE ONLY; unresolved scientifically.",
            },
            "coverage_audit": {
                "audit_version": version,
                "status": "complete",
                "represented_activity": dict(audit_answer),
                "potentially_missing_activity": dict(audit_answer),
                "heavy_overlap": dict(audit_answer),
                "single_frame_dependence": dict(audit_answer),
                "unstable_or_technology_specific": dict(audit_answer),
                "fashionable_ai_privilege": dict(audit_answer),
                "overall_rationale": "TEMPORARY TEST FIXTURE ONLY; no real coverage conclusion.",
                "overall_uncertainty": "TEMPORARY TEST FIXTURE ONLY; unresolved scientifically.",
            },
            "domain_dispositions": [
                {
                    "domain_candidate_id": domain_id,
                    "disposition": "included",
                    "rationale": "TEMPORARY TEST FIXTURE ONLY; no real inclusion.",
                    "uncertainty": "TEMPORARY TEST FIXTURE ONLY; no empirical assessment.",
                }
                for domain_id in domain_ids
            ],
            "included_domain_candidate_ids": list(domain_ids),
            "created_at": "2026-01-01T00:00:00Z",
        }
        proposal_relative = "domain-universe/proposals/test-only-domain-universe-proposal.json"
        write_json(self.root / proposal_relative, proposal)
        proposal_reference = self.reference(proposal_relative)

        review = {
            "domain_universe_review_id": "test-only-domain-universe-review",
            "instrument_version": version,
            "review_type": "domain_universe_scientific_review",
            "domain_universe_proposal": proposal_reference,
            "outcome": "approved",
            "rationale": "TEMPORARY TEST FIXTURE ONLY; no real review or approval.",
            "responsible_role_id": "test-suite-only-review-role",
            "reviewed_at": "2026-01-01T00:00:00Z",
        }
        review_relative = "domain-universe/reviews/test-only-domain-universe-review.json"
        write_json(self.root / review_relative, review)
        review_reference = self.reference(review_relative)

        governance = {
            "domain_universe_governance_decision_id": "test-only-domain-universe-governance",
            "instrument_version": version,
            "decision_type": "domain_universe_lock_authorization",
            "domain_universe_proposal": proposal_reference,
            "scientific_review": review_reference,
            "outcome": "authorized",
            "rationale": "TEMPORARY TEST FIXTURE ONLY; no real authority or authorization.",
            "responsible_authority_id": "test-suite-only-authority",
            "recorded_at": "2026-01-01T00:00:00Z",
        }
        governance_relative = "domain-universe/governance/test-only-domain-universe-governance.json"
        write_json(self.root / governance_relative, governance)

        return {
            "domain_universe_manifest_id": "test-only-domain-universe-manifest",
            "instrument_version": version,
            "status": "locked",
            "domain_universe_proposal": proposal_reference,
            "scientific_review": {"status": "complete", "review_record": review_reference},
            "governance_authority": {
                "status": "recorded",
                "authority_id": "test-suite-only-authority",
                "decision_record": self.reference(governance_relative),
            },
            "locked_at": "2026-01-01T00:00:00Z",
        }

    def rewrite_chain(self, manifest: dict[str, object], mutate_proposal=None, mutate_review=None, mutate_governance=None) -> None:
        proposal_reference = manifest["domain_universe_proposal"]
        proposal_path = self.root / proposal_reference["path"]
        proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
        if mutate_proposal is not None:
            mutate_proposal(proposal)
        write_json(proposal_path, proposal)
        proposal_reference = self.reference(proposal_reference["path"])
        manifest["domain_universe_proposal"] = proposal_reference

        review_reference = manifest["scientific_review"]["review_record"]
        review_path = self.root / review_reference["path"]
        review = json.loads(review_path.read_text(encoding="utf-8"))
        review["domain_universe_proposal"] = proposal_reference
        if mutate_review is not None:
            mutate_review(review)
        write_json(review_path, review)
        review_reference = self.reference(review_reference["path"])
        manifest["scientific_review"]["review_record"] = review_reference

        governance_reference = manifest["governance_authority"]["decision_record"]
        governance_path = self.root / governance_reference["path"]
        governance = json.loads(governance_path.read_text(encoding="utf-8"))
        governance["domain_universe_proposal"] = proposal_reference
        governance["scientific_review"] = review_reference
        if mutate_governance is not None:
            mutate_governance(governance)
        write_json(governance_path, governance)
        manifest["governance_authority"]["decision_record"] = self.reference(
            governance_reference["path"]
        )


class DomainUniverseProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = TemporaryDomainRepository()
        self.schemas = self.repository.domain_schemas()

    def tearDown(self) -> None:
        self.repository.close()

    def validate(self, manifest: dict[str, object]) -> list[str]:
        _, errors = VALIDATE.validate_domain_universe_manifest(
            self.repository.root,
            manifest,
            "test Domain Universe manifest",
            self.schemas,
        )
        return errors

    def set_pair_relation(
        self,
        manifest: dict[str, object],
        relation_type: str,
        resolution_status: str,
        assessment: str,
        relation_id: str,
    ) -> None:
        def mutate(proposal: dict[str, object]) -> None:
            relation = {
                "domain_relation_id": relation_id,
                "instrument_version": CURRENT_DOMAIN_VERSION,
                "subject_domain_candidate_id": "test-only-domain-a",
                "relation_type": relation_type,
                "object_domain_candidate_id": "test-only-domain-b",
                "resolution_status": resolution_status,
                "rationale": (
                    "TEMPORARY TEST FIXTURE ONLY; no real relation determination."
                ),
            }
            relative = f"domain-universe/relations/{relation_id}.json"
            write_json(self.repository.root / relative, relation)
            proposal["domain_relations"] = [self.repository.reference(relative)]
            proposal["overlap_duplication_review"]["candidate_pair_assessments"][0].update(
                {"assessment": assessment, "relation_ids": [relation_id]}
            )

        self.repository.rewrite_chain(manifest, mutate)

    def make_duplicate_candidate_ineligible(
        self, manifest: dict[str, object], decision_index: int = 1
    ) -> str:
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        decision_reference = proposal["eligibility_decisions"][decision_index]
        decision_path = self.repository.root / decision_reference["path"]
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        candidate_id = decision["domain_candidate_id"]
        decision["criteria"]["non_duplication"]["result"] = "failed"
        decision["decision_status"] = "ineligible"
        write_json(decision_path, decision)
        replacement = self.repository.reference(decision_reference["path"])

        def mutate(current: dict[str, object]) -> None:
            current["eligibility_decisions"][decision_index] = replacement
            current["domain_dispositions"] = [
                item
                for item in current["domain_dispositions"]
                if item["domain_candidate_id"] != candidate_id
            ]
            current["included_domain_candidate_ids"] = [
                item
                for item in current["included_domain_candidate_ids"]
                if item != candidate_id
            ]

        self.repository.rewrite_chain(manifest, mutate)
        return candidate_id

    def test_complete_temporary_chain_passes_internal_gate_only(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.assertEqual([], self.validate(manifest))
        for reference in (
            manifest["domain_universe_proposal"],
            manifest["scientific_review"]["review_record"],
            manifest["governance_authority"]["decision_record"],
        ):
            self.assertIn(
                "TEMPORARY TEST FIXTURE ONLY",
                (self.repository.root / reference["path"]).read_text(encoding="utf-8"),
            )

    def test_product_company_or_model_cannot_be_domain_unit(self) -> None:
        schema = self.schemas["candidate"]
        manifest = self.repository.create_locked_domain_universe()
        reference = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )["domain_candidates"][0]
        record = json.loads((self.repository.root / reference["path"]).read_text(encoding="utf-8"))
        for prohibited in ("product", "company", "model"):
            record["primary_unit_type"] = prohibited
            self.assertTrue(VALIDATE.validate_contract(record, schema, f"test {prohibited}"))

    def test_missing_inclusion_or_exclusion_boundary_fails(self) -> None:
        schema = self.schemas["candidate"]
        manifest = self.repository.create_locked_domain_universe()
        reference = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(encoding="utf-8")
        )["domain_candidates"][0]
        record = json.loads((self.repository.root / reference["path"]).read_text(encoding="utf-8"))
        for field in ("inclusion_boundary", "exclusion_boundary"):
            changed = dict(record)
            del changed[field]
            self.assertTrue(any(field in error for error in VALIDATE.validate_contract(changed, schema, "test boundary")))

    def test_one_source_frame_cannot_lock_universe(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest, lambda proposal: proposal["source_frames"].pop()
        )
        self.assertTrue(any("at least two source frames" in error for error in self.validate(manifest)))

    def test_unfixed_boundary_cannot_lock_universe(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(encoding="utf-8")
        )
        boundary_reference = proposal["universe_boundary"]
        boundary_path = self.repository.root / boundary_reference["path"]
        boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
        boundary.update({"status": "draft", "fixed_at": None})
        write_json(boundary_path, boundary)
        replacement = self.repository.reference(boundary_reference["path"])
        self.repository.rewrite_chain(
            manifest, lambda current: current.update({"universe_boundary": replacement})
        )
        self.assertTrue(any("boundary must be prospectively fixed" in error for error in self.validate(manifest)))

    def test_two_frames_with_same_independence_group_cannot_lock(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(encoding="utf-8")
        )
        frame_reference = proposal["source_frames"][1]
        frame_path = self.repository.root / frame_reference["path"]
        frame = json.loads(frame_path.read_text(encoding="utf-8"))
        frame["independence_group"] = "test-only-independent-group-1"
        write_json(frame_path, frame)
        replacement = self.repository.reference(frame_reference["path"])
        self.repository.rewrite_chain(
            manifest, lambda current: current["source_frames"].__setitem__(1, replacement)
        )
        self.assertTrue(any("at least two source frames" in error for error in self.validate(manifest)))

    def test_same_source_registered_twice_under_different_frame_ids_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        first = json.loads(
            (self.repository.root / proposal["source_frames"][0]["path"]).read_text(
                encoding="utf-8"
            )
        )
        second_reference = proposal["source_frames"][1]
        second_path = self.repository.root / second_reference["path"]
        second = json.loads(second_path.read_text(encoding="utf-8"))
        for field in ("source_identity", "source_version_or_date", "source_uri"):
            second[field] = first[field]
        write_json(second_path, second)
        replacement = self.repository.reference(second_reference["path"])
        self.repository.rewrite_chain(
            manifest,
            lambda current: current["source_frames"].__setitem__(1, replacement),
        )
        self.assertTrue(
            any("duplicate source identity/version/URI" in error for error in self.validate(manifest))
        )

    def test_exact_duplicate_source_frame_artifact_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest,
            lambda proposal: proposal["source_frames"].append(proposal["source_frames"][0]),
        )
        self.assertTrue(
            any("exact duplicate source-frame artifact" in error for error in self.validate(manifest))
        )

    def test_different_independence_group_labels_do_not_override_same_lineage(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        first = json.loads(
            (self.repository.root / proposal["source_frames"][0]["path"]).read_text(
                encoding="utf-8"
            )
        )
        second_reference = proposal["source_frames"][1]
        second_path = self.repository.root / second_reference["path"]
        second = json.loads(second_path.read_text(encoding="utf-8"))
        self.assertNotEqual(first["independence_group"], second["independence_group"])
        second["source_lineage_id"] = first["source_lineage_id"]
        write_json(second_path, second)
        replacement = self.repository.reference(second_reference["path"])
        self.repository.rewrite_chain(
            manifest,
            lambda current: current["source_frames"].__setitem__(1, replacement),
        )
        self.assertTrue(
            any("distinct independence groups and source lineages" in error for error in self.validate(manifest))
        )

    def test_two_distinct_temporary_source_lineages_pass_structural_gate(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        lineages = {
            json.loads(
                (self.repository.root / reference["path"]).read_text(encoding="utf-8")
            )["source_lineage_id"]
            for reference in proposal["source_frames"]
        }
        self.assertEqual(2, len(lineages))
        self.assertEqual([], self.validate(manifest))

    def test_source_frame_requires_reviewable_independence_basis(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["source_frames"][0]
        frame = json.loads(
            (self.repository.root / reference["path"]).read_text(encoding="utf-8")
        )
        del frame["independence_basis"]
        errors = VALIDATE.validate_contract(frame, self.schemas["source_frame"], "test frame")
        self.assertTrue(any("independence_basis" in error for error in errors))

    def test_missing_extraction_for_registered_frame_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest, lambda proposal: proposal["source_extractions"].pop()
        )
        self.assertTrue(
            any(
                "every registered source frame requires exactly one complete extraction" in error
                for error in self.validate(manifest)
            )
        )

    def test_duplicate_extraction_for_registered_frame_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest,
            lambda proposal: proposal["source_extractions"].append(
                proposal["source_extractions"][0]
            ),
        )
        self.assertTrue(
            any(
                "every registered source frame requires exactly one complete extraction" in error
                for error in self.validate(manifest)
            )
        )

    def test_incomplete_extraction_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["source_extractions"][0]
        path = self.repository.root / reference["path"]
        extraction = json.loads(path.read_text(encoding="utf-8"))
        extraction["extraction_status"] = "pending"
        write_json(path, extraction)
        replacement = self.repository.reference(reference["path"])
        self.repository.rewrite_chain(
            manifest,
            lambda current: current["source_extractions"].__setitem__(0, replacement),
        )
        self.assertTrue(
            any("source extraction must be complete" in error for error in self.validate(manifest))
        )

    def test_extraction_must_bind_exact_registered_source_frame(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["source_extractions"][0]
        path = self.repository.root / reference["path"]
        extraction = json.loads(path.read_text(encoding="utf-8"))
        extraction["source_frame"]["sha256"] = "0" * 64
        write_json(path, extraction)
        replacement = self.repository.reference(reference["path"])
        self.repository.rewrite_chain(
            manifest,
            lambda current: current["source_extractions"].__setitem__(0, replacement),
        )
        self.assertTrue(
            any("must bind an exact registered source frame" in error for error in self.validate(manifest))
        )

    def test_duplicate_source_entry_id_within_frame_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["source_extractions"][0]
        path = self.repository.root / reference["path"]
        extraction = json.loads(path.read_text(encoding="utf-8"))
        extraction["extracted_entries"].append(dict(extraction["extracted_entries"][0]))
        write_json(path, extraction)
        replacement = self.repository.reference(reference["path"])
        self.repository.rewrite_chain(
            manifest,
            lambda current: current["source_extractions"].__setitem__(0, replacement),
        )
        self.assertTrue(
            any("duplicate source_entry_id" in error for error in self.validate(manifest))
        )

    def test_unresolved_extraction_entry_fails_closed(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["source_extractions"][0]
        path = self.repository.root / reference["path"]
        extraction = json.loads(path.read_text(encoding="utf-8"))
        entry = extraction["extracted_entries"][0]
        entry["normalization_disposition"] = "unresolved"
        entry["target_domain_candidate_ids"] = []
        write_json(path, extraction)
        replacement = self.repository.reference(reference["path"])
        self.repository.rewrite_chain(
            manifest,
            lambda current: current["source_extractions"].__setitem__(0, replacement),
        )
        self.assertTrue(
            any("unresolved extraction entry" in error for error in self.validate(manifest))
        )

    def test_free_text_alone_cannot_satisfy_candidate_provenance(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["domain_candidates"][0]
        candidate = json.loads(
            (self.repository.root / reference["path"]).read_text(encoding="utf-8")
        )
        candidate["provenance_references"] = [
            {
                "source_frame_id": "test-only-frame-1",
                "source_entry_reference": "arbitrary free text",
            }
        ]
        errors = VALIDATE.validate_contract(candidate, self.schemas["candidate"], "test candidate")
        self.assertTrue(any("source_extraction" in error for error in errors))

    def test_extraction_target_outside_candidate_universe_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["source_extractions"][0]
        path = self.repository.root / reference["path"]
        extraction = json.loads(path.read_text(encoding="utf-8"))
        extraction["extracted_entries"][0]["target_domain_candidate_ids"] = [
            "test-only-domain-outside-universe"
        ]
        write_json(path, extraction)
        replacement = self.repository.reference(reference["path"])
        self.repository.rewrite_chain(
            manifest,
            lambda current: current["source_extractions"].__setitem__(0, replacement),
        )
        self.assertTrue(
            any("is outside candidate universe" in error for error in self.validate(manifest))
        )

    def test_candidate_and_extraction_provenance_must_be_reciprocal(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        candidate_reference = proposal["domain_candidates"][0]
        candidate_path = self.repository.root / candidate_reference["path"]
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        candidate["provenance_references"][0]["source_entry_id"] = "missing-entry"
        write_json(candidate_path, candidate)
        new_candidate_reference = self.repository.reference(candidate_reference["path"])
        decision_reference = proposal["eligibility_decisions"][0]
        decision_path = self.repository.root / decision_reference["path"]
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        decision["domain_candidate"] = new_candidate_reference
        write_json(decision_path, decision)
        new_decision_reference = self.repository.reference(decision_reference["path"])

        def mutate(current: dict[str, object]) -> None:
            current["domain_candidates"][0] = new_candidate_reference
            current["eligibility_decisions"][0] = new_decision_reference

        self.repository.rewrite_chain(manifest, mutate)
        errors = self.validate(manifest)
        self.assertTrue(any("source_entry_id does not resolve" in error for error in errors))
        self.assertTrue(any("entry-to-candidate provenance is not reciprocal" in error for error in errors))

    def test_two_lineage_distinct_extractions_must_be_non_empty(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["source_extractions"][1]
        path = self.repository.root / reference["path"]
        extraction = json.loads(path.read_text(encoding="utf-8"))
        extraction["extracted_entries"] = []
        write_json(path, extraction)
        replacement = self.repository.reference(reference["path"])
        self.repository.rewrite_chain(
            manifest,
            lambda current: current["source_extractions"].__setitem__(1, replacement),
        )
        self.assertTrue(
            any("distinct source lineages must contribute non-empty" in error for error in self.validate(manifest))
        )

    def test_tampered_extraction_fails_sha_binding(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        reference = proposal["source_extractions"][0]
        path = self.repository.root / reference["path"]
        extraction = json.loads(path.read_text(encoding="utf-8"))
        extraction["rationale"] = "tampered temporary extraction fixture"
        write_json(path, extraction)
        self.assertTrue(any("SHA-256 mismatch" in error for error in self.validate(manifest)))

    def test_unnormalized_source_frame_cannot_lock(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(encoding="utf-8")
        )
        frame_reference = proposal["source_frames"][0]
        frame_path = self.repository.root / frame_reference["path"]
        frame = json.loads(frame_path.read_text(encoding="utf-8"))
        frame["normalization_status"] = "pending"
        write_json(frame_path, frame)
        replacement = self.repository.reference(frame_reference["path"])
        self.repository.rewrite_chain(
            manifest, lambda current: current["source_frames"].__setitem__(0, replacement)
        )
        self.assertTrue(any("must be normalized before lock" in error for error in self.validate(manifest)))

    def test_one_frame_cannot_define_all_candidate_provenance(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(encoding="utf-8")
        )
        candidate_reference = proposal["domain_candidates"][1]
        candidate_path = self.repository.root / candidate_reference["path"]
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        candidate["provenance_references"][0] = {
            "source_extraction": proposal["source_extractions"][0],
            "source_entry_id": "test-only-entry-1",
        }
        write_json(candidate_path, candidate)
        new_candidate_reference = self.repository.reference(candidate_reference["path"])

        decision_reference = proposal["eligibility_decisions"][1]
        decision_path = self.repository.root / decision_reference["path"]
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        decision["domain_candidate"] = new_candidate_reference
        write_json(decision_path, decision)
        new_decision_reference = self.repository.reference(decision_reference["path"])

        def mutate(current: dict[str, object]) -> None:
            current["domain_candidates"][1] = new_candidate_reference
            current["eligibility_decisions"][1] = new_decision_reference

        self.repository.rewrite_chain(manifest, mutate)
        self.assertTrue(any("no single source frame may define" in error for error in self.validate(manifest)))

    def test_duplicate_domain_without_resolution_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest,
            lambda proposal: proposal["overlap_duplication_review"]["candidate_pair_assessments"][0].update(
                {"assessment": "duplicate_unresolved"}
            ),
        )
        self.assertTrue(any("unresolved duplicate domain" in error for error in self.validate(manifest)))

    def test_documented_overlap_does_not_invalidate_domain(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            relation = {
                "domain_relation_id": "test-only-overlap",
                "instrument_version": CURRENT_DOMAIN_VERSION,
                "subject_domain_candidate_id": "test-only-domain-a",
                "relation_type": "overlaps_with",
                "object_domain_candidate_id": "test-only-domain-b",
                "resolution_status": "documented",
                "rationale": "TEMPORARY TEST FIXTURE ONLY; no empirical overlap claim.",
            }
            relative = "domain-universe/relations/test-only-overlap.json"
            write_json(self.repository.root / relative, relation)
            proposal["domain_relations"] = [self.repository.reference(relative)]
            proposal["overlap_duplication_review"]["candidate_pair_assessments"][0].update(
                {"assessment": "overlap_documented", "relation_ids": ["test-only-overlap"]}
            )

        self.repository.rewrite_chain(manifest, mutate)
        self.assertEqual([], self.validate(manifest))

    def test_depends_on_alone_cannot_support_overlap_documented(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            relation = {
                "domain_relation_id": "test-only-dependency",
                "instrument_version": CURRENT_DOMAIN_VERSION,
                "subject_domain_candidate_id": "test-only-domain-a",
                "relation_type": "depends_on",
                "object_domain_candidate_id": "test-only-domain-b",
                "resolution_status": "documented",
                "rationale": "TEMPORARY TEST FIXTURE ONLY; no empirical dependency claim.",
            }
            relative = "domain-universe/relations/test-only-dependency.json"
            write_json(self.repository.root / relative, relation)
            proposal["domain_relations"] = [self.repository.reference(relative)]
            proposal["overlap_duplication_review"]["candidate_pair_assessments"][0].update(
                {
                    "assessment": "overlap_documented",
                    "relation_ids": ["test-only-dependency"],
                }
            )

        self.repository.rewrite_chain(manifest, mutate)
        self.assertTrue(
            any("depends_on alone is insufficient" in error for error in self.validate(manifest))
        )

    def test_distinct_pair_may_record_depends_on_without_implying_overlap(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            relation = {
                "domain_relation_id": "test-only-distinct-dependency",
                "instrument_version": CURRENT_DOMAIN_VERSION,
                "subject_domain_candidate_id": "test-only-domain-a",
                "relation_type": "depends_on",
                "object_domain_candidate_id": "test-only-domain-b",
                "resolution_status": "documented",
                "rationale": "TEMPORARY TEST FIXTURE ONLY; no empirical dependency claim.",
            }
            relative = "domain-universe/relations/test-only-distinct-dependency.json"
            write_json(self.repository.root / relative, relation)
            proposal["domain_relations"] = [self.repository.reference(relative)]
            proposal["overlap_duplication_review"]["candidate_pair_assessments"][0][
                "relation_ids"
            ] = ["test-only-distinct-dependency"]

        self.repository.rewrite_chain(manifest, mutate)
        self.assertEqual([], self.validate(manifest))

    def test_distinct_pair_cannot_cite_overlap_relation(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            relation = {
                "domain_relation_id": "test-only-contradictory-overlap",
                "instrument_version": CURRENT_DOMAIN_VERSION,
                "subject_domain_candidate_id": "test-only-domain-a",
                "relation_type": "overlaps_with",
                "object_domain_candidate_id": "test-only-domain-b",
                "resolution_status": "documented",
                "rationale": "TEMPORARY TEST FIXTURE ONLY; intentionally contradictory.",
            }
            relative = "domain-universe/relations/test-only-contradictory-overlap.json"
            write_json(self.repository.root / relative, relation)
            proposal["domain_relations"] = [self.repository.reference(relative)]
            proposal["overlap_duplication_review"]["candidate_pair_assessments"][0][
                "relation_ids"
            ] = ["test-only-contradictory-overlap"]

        self.repository.rewrite_chain(manifest, mutate)
        self.assertTrue(
            any("distinct pair may only cite depends_on" in error for error in self.validate(manifest))
        )

    def test_orphan_relation_record_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            relation = {
                "domain_relation_id": "test-only-orphan-relation",
                "instrument_version": CURRENT_DOMAIN_VERSION,
                "subject_domain_candidate_id": "test-only-domain-a",
                "relation_type": "depends_on",
                "object_domain_candidate_id": "test-only-domain-b",
                "resolution_status": "documented",
                "rationale": "TEMPORARY TEST FIXTURE ONLY; intentionally orphaned.",
            }
            relative = "domain-universe/relations/test-only-orphan-relation.json"
            write_json(self.repository.root / relative, relation)
            proposal["domain_relations"] = [self.repository.reference(relative)]

        self.repository.rewrite_chain(manifest, mutate)
        self.assertTrue(any("orphan relation IDs" in error for error in self.validate(manifest)))

    def test_relation_endpoints_must_match_assessed_pair(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            relation = {
                "domain_relation_id": "test-only-wrong-endpoints",
                "instrument_version": CURRENT_DOMAIN_VERSION,
                "subject_domain_candidate_id": "test-only-domain-a",
                "relation_type": "overlaps_with",
                "object_domain_candidate_id": "test-only-domain-outside-universe",
                "resolution_status": "documented",
                "rationale": "TEMPORARY TEST FIXTURE ONLY; intentionally mismatched.",
            }
            relative = "domain-universe/relations/test-only-wrong-endpoints.json"
            write_json(self.repository.root / relative, relation)
            proposal["domain_relations"] = [self.repository.reference(relative)]
            proposal["overlap_duplication_review"]["candidate_pair_assessments"][0].update(
                {
                    "assessment": "overlap_documented",
                    "relation_ids": ["test-only-wrong-endpoints"],
                }
            )

        self.repository.rewrite_chain(manifest, mutate)
        self.assertTrue(
            any("relation endpoints do not match assessed pair" in error for error in self.validate(manifest))
        )

    def test_duplicate_relation_ids_fail(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            relation = {
                "domain_relation_id": "test-only-duplicate-relation-id",
                "instrument_version": CURRENT_DOMAIN_VERSION,
                "subject_domain_candidate_id": "test-only-domain-a",
                "relation_type": "overlaps_with",
                "object_domain_candidate_id": "test-only-domain-b",
                "resolution_status": "documented",
                "rationale": "TEMPORARY TEST FIXTURE ONLY; duplicated reference.",
            }
            relative = "domain-universe/relations/test-only-duplicate-relation-id.json"
            write_json(self.repository.root / relative, relation)
            reference = self.repository.reference(relative)
            proposal["domain_relations"] = [reference, reference]
            proposal["overlap_duplication_review"]["candidate_pair_assessments"][0].update(
                {
                    "assessment": "overlap_documented",
                    "relation_ids": ["test-only-duplicate-relation-id"],
                }
            )

        self.repository.rewrite_chain(manifest, mutate)
        self.assertTrue(
            any("duplicate domain_relation_id" in error for error in self.validate(manifest))
        )

    def test_duplicate_resolved_with_both_candidates_eligible_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.set_pair_relation(
            manifest,
            "substantively_duplicates",
            "resolved",
            "duplicate_resolved",
            "test-only-both-eligible-duplicate",
        )

        def retain_only_first(current: dict[str, object]) -> None:
            current["domain_dispositions"][1]["disposition"] = "excluded"
            current["included_domain_candidate_ids"] = ["test-only-domain-a"]

        self.repository.rewrite_chain(manifest, retain_only_first)
        self.assertTrue(
            any(
                "duplicate_resolved requires at least one pair member" in error
                for error in self.validate(manifest)
            )
        )

    def test_duplicate_resolved_with_both_candidates_included_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.set_pair_relation(
            manifest,
            "substantively_duplicates",
            "resolved",
            "duplicate_resolved",
            "test-only-both-included-duplicate",
        )
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(2, len(proposal["included_domain_candidate_ids"]))
        self.assertTrue(
            any(
                "duplicate_resolved requires at least one pair member" in error
                for error in self.validate(manifest)
            )
        )

    def test_duplicate_resolved_passes_when_one_duplicate_is_ineligible(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.set_pair_relation(
            manifest,
            "substantively_duplicates",
            "resolved",
            "duplicate_resolved",
            "test-only-coherent-resolved-duplicate",
        )
        removed_candidate_id = self.make_duplicate_candidate_ineligible(manifest)
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(
                encoding="utf-8"
            )
        )
        removed_reference = proposal["eligibility_decisions"][1]
        removed_decision = json.loads(
            (self.repository.root / removed_reference["path"]).read_text(encoding="utf-8")
        )
        retained_reference = proposal["eligibility_decisions"][0]
        retained_decision = json.loads(
            (self.repository.root / retained_reference["path"]).read_text(encoding="utf-8")
        )
        self.assertEqual("failed", removed_decision["criteria"]["non_duplication"]["result"])
        self.assertEqual("ineligible", removed_decision["decision_status"])
        self.assertNotIn(removed_candidate_id, proposal["included_domain_candidate_ids"])
        self.assertEqual("eligible", retained_decision["decision_status"])
        self.assertIn("test-only-domain-a", proposal["included_domain_candidate_ids"])
        self.assertEqual([], self.validate(manifest))

    def test_revised_nonduplicate_pair_uses_distinct_or_overlap_documented(self) -> None:
        distinct_manifest = self.repository.create_locked_domain_universe()
        distinct_proposal = json.loads(
            (
                self.repository.root
                / distinct_manifest["domain_universe_proposal"]["path"]
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            "distinct",
            distinct_proposal["overlap_duplication_review"]["candidate_pair_assessments"][0][
                "assessment"
            ],
        )
        self.assertEqual([], self.validate(distinct_manifest))

        overlap_manifest = self.repository.create_locked_domain_universe()
        self.set_pair_relation(
            overlap_manifest,
            "overlaps_with",
            "documented",
            "overlap_documented",
            "test-only-revised-overlap",
        )
        self.assertEqual([], self.validate(overlap_manifest))

    def test_unresolved_overlaps_with_cannot_support_overlap_documented(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.set_pair_relation(
            manifest,
            "overlaps_with",
            "unresolved",
            "overlap_documented",
            "test-only-unresolved-overlap",
        )
        self.assertTrue(
            any("unresolved domain relation" in error for error in self.validate(manifest))
        )

    def test_unresolved_depends_on_cannot_support_distinct(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.set_pair_relation(
            manifest,
            "depends_on",
            "unresolved",
            "distinct",
            "test-only-unresolved-dependency",
        )
        self.assertTrue(
            any("unresolved domain relation" in error for error in self.validate(manifest))
        )

    def test_unresolved_substantive_duplicate_continues_to_fail(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.set_pair_relation(
            manifest,
            "substantively_duplicates",
            "unresolved",
            "duplicate_resolved",
            "test-only-unresolved-substantive-duplicate",
        )
        errors = self.validate(manifest)
        self.assertTrue(any("unresolved domain relation" in error for error in errors))
        self.assertTrue(any("duplicate domain relation must be explicitly resolved" in error for error in errors))

    def test_unresolved_relation_records_of_every_type_fail_lock(self) -> None:
        assessments = {
            "overlaps_with": "overlap_documented",
            "contains": "overlap_documented",
            "contained_by": "overlap_documented",
            "cross_cutting_with": "overlap_documented",
            "depends_on": "distinct",
            "substantively_duplicates": "duplicate_resolved",
        }
        for relation_type, assessment in assessments.items():
            with self.subTest(relation_type=relation_type):
                manifest = self.repository.create_locked_domain_universe()
                self.set_pair_relation(
                    manifest,
                    relation_type,
                    "unresolved",
                    assessment,
                    f"test-only-unresolved-{relation_type.replace('_', '-')}",
                )
                self.assertTrue(
                    any("unresolved domain relation" in error for error in self.validate(manifest))
                )

    def test_missing_eligibility_decision_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest, lambda proposal: proposal["eligibility_decisions"].pop()
        )
        self.assertTrue(any("requires exactly one eligibility decision" in error for error in self.validate(manifest)))

    def test_failed_or_unresolved_criterion_cannot_produce_eligible(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(encoding="utf-8")
        )
        reference = proposal["eligibility_decisions"][0]
        record = json.loads((self.repository.root / reference["path"]).read_text(encoding="utf-8"))
        for result, expected in (("failed", "ineligible"), ("unresolved", "unresolved")):
            changed = json.loads(json.dumps(record))
            changed["criteria"]["coverage_usefulness"]["result"] = result
            changed["decision_status"] = "eligible"
            errors = VALIDATE.validate_domain_eligibility_decision(
                self.repository.root,
                changed,
                "test eligibility",
                self.schemas["eligibility"],
                self.schemas["candidate"],
            )
            self.assertTrue(any(f"deterministically be '{expected}'" in error for error in errors))

    def test_domain_inclusion_cannot_depend_on_human_criticality_forecast(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        proposal = json.loads(
            (self.repository.root / manifest["domain_universe_proposal"]["path"]).read_text(encoding="utf-8")
        )
        reference = proposal["domain_candidates"][0]
        record = json.loads((self.repository.root / reference["path"]).read_text(encoding="utf-8"))
        record["human_criticality_forecast"] = "weaken"
        self.assertTrue(VALIDATE.validate_contract(record, self.schemas["candidate"], "test forecast"))
        protocol = (ROOT / "DOMAIN_UNIVERSE.md").read_text(encoding="utf-8")
        self.assertIn("Domain inclusion must not depend on an expectation that human criticality", protocol)

    def test_duplication_adjudication_precedes_final_eligibility_in_protocol(self) -> None:
        protocol = (ROOT / "DOMAIN_UNIVERSE.md").read_text(encoding="utf-8")
        adjudication = protocol.index("-> Overlap / Duplication Adjudication")
        eligibility = protocol.index("-> Final Domain Eligibility")
        self.assertLess(adjudication, eligibility)

    def test_excluded_eligible_domain_requires_rationale(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            proposal["domain_dispositions"][0].update(
                {"disposition": "excluded", "rationale": "", "uncertainty": ""}
            )
            proposal["included_domain_candidate_ids"] = ["test-only-domain-b"]

        self.repository.rewrite_chain(manifest, mutate)
        self.assertTrue(any("excluded eligible domain requires rationale" in error for error in self.validate(manifest)))

    def test_incomplete_coverage_audit_cannot_lock(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest, lambda proposal: proposal["coverage_audit"].update({"status": "incomplete"})
        )
        self.assertTrue(any("coverage audit must be complete" in error for error in self.validate(manifest)))

    def test_coverage_audit_version_mismatch_cannot_lock(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest,
            lambda proposal: proposal["coverage_audit"].update(
                {"audit_version": "wrong-test-version"}
            ),
        )
        self.assertTrue(
            any("coverage audit version must match" in error for error in self.validate(manifest))
        )

    def test_proposal_review_governance_mismatch_fails(self) -> None:
        manifest = self.repository.create_locked_domain_universe()
        self.repository.rewrite_chain(
            manifest,
            mutate_review=lambda review: review.update(
                {"domain_universe_proposal": manifest["scientific_review"]["review_record"]}
            ),
        )
        self.assertTrue(any("scientific review must bind the exact" in error for error in self.validate(manifest)))

    def test_tampered_proposal_review_or_governance_fails(self) -> None:
        for role, wrapper in (
            ("proposal", None),
            ("review", "scientific_review"),
            ("governance", "governance_authority"),
        ):
            repository = TemporaryDomainRepository()
            try:
                manifest = repository.create_locked_domain_universe()
                reference = (
                    manifest["domain_universe_proposal"]
                    if wrapper is None
                    else manifest[wrapper]["review_record" if wrapper == "scientific_review" else "decision_record"]
                )
                path = repository.root / reference["path"]
                record = json.loads(path.read_text(encoding="utf-8"))
                record[next(key for key in record if key.endswith("_at"))] = "2026-01-02T00:00:00Z"
                write_json(path, record)
                _, errors = VALIDATE.validate_domain_universe_manifest(
                    repository.root,
                    manifest,
                    f"test tampered {role}",
                    repository.domain_schemas(),
                )
                self.assertTrue(any("SHA-256 mismatch" in error for error in errors))
            finally:
                repository.close()

    def test_empty_domain_universe_cannot_lock(self) -> None:
        manifest = self.repository.create_locked_domain_universe()

        def mutate(proposal: dict[str, object]) -> None:
            proposal["domain_candidates"] = []
            proposal["eligibility_decisions"] = []
            proposal["domain_dispositions"] = []
            proposal["included_domain_candidate_ids"] = []
            proposal["overlap_duplication_review"]["candidate_pair_assessments"] = []

        self.repository.rewrite_chain(manifest, mutate)
        errors = self.validate(manifest)
        self.assertTrue(any("candidate universe must be non-empty" in error for error in errors))
        self.assertTrue(any("must include at least one eligible domain" in error for error in errors))

    def test_domain_universe_templates_remain_invalid_non_records(self) -> None:
        for name, schema in self.schemas.items():
            filename = {
                "boundary": "domain-universe-boundary.template.json",
                "source_frame": "domain-source-frame.template.json",
                "extraction": "domain-source-extraction.template.json",
                "candidate": "domain-candidate.template.json",
                "eligibility": "domain-eligibility-decision.template.json",
                "relation": "domain-relation.template.json",
                "proposal": "domain-universe-proposal.template.json",
                "review": "domain-universe-review.template.json",
                "governance": "domain-universe-governance-decision.template.json",
                "manifest": "domain-universe-manifest.template.json",
            }[name]
            template = json.loads((ROOT / "schemas/templates" / filename).read_text(encoding="utf-8"))
            self.assertTrue(VALIDATE.validate_contract(template, schema, f"template {filename}"))

    def test_repository_has_exact_prospectively_fixed_boundary(self) -> None:
        boundary_paths = list((ROOT / "domain-universe/boundaries").glob("*.json"))
        self.assertEqual([ROOT / "domain-universe/boundaries/du-boundary-v0.1.json"], boundary_paths)
        boundary = json.loads(boundary_paths[0].read_text(encoding="utf-8"))
        self.assertEqual([], VALIDATE.validate_contract(boundary, self.schemas["boundary"], "actual boundary"))
        self.assertEqual("du-boundary-v0.1", boundary["boundary_specification_id"])
        self.assertEqual("fixed", boundary["status"])
        self.assertEqual(
            {
                "recurrent_improvement_activity": "Institutionalized or scalable recurrent sociotechnical processes in which outputs, evaluations, or experience from one cycle can be used to modify subsequent-cycle performance or the structures that enable it. 'Improvement' is procedural here and does not imply that the resulting change is socially, ethically, economically, or technically beneficial.",
                "later_cycle_change": "The process must be capable of altering at least one of the knowledge, designs, policies, systems, capabilities, practices, or infrastructures that govern or enable a subsequent cycle.",
                "human_criticality_investigability": "It must be meaningful in principle to investigate whether, where, and under what boundary conditions human participation remains necessary on the critical path of the recurrent improvement process, without presupposing that human criticality will weaken.",
            },
            boundary["in_scope"],
        )
        self.assertEqual(
            {
                "all_human_activity": "Human activity is not included merely because learning, adaptation, or change occurs. The activity must form part of an institutionalized or scalable recurrent sociotechnical improvement process.",
                "all_economic_sectors": "Economic-sector membership is not sufficient for inclusion. Routine production or service delivery is outside the research universe unless it participates in a qualifying recurrent improvement process.",
                "all_ai_applications": "Use of AI is not sufficient for inclusion. An AI application is relevant only when it participates in a qualifying recurrent improvement process.",
                "all_occupations": "Occupation labels are not Domain units. Occupational activity is relevant only insofar as it instantiates a qualifying recurrent improvement process.",
                "all_tasks": "Isolated tasks are outside the research universe unless their outputs, evaluations, or experience feed into a subsequent improvement cycle.",
                "generic_automation": "Automation that merely substitutes for or accelerates execution is not sufficient. It must participate in a recurrent process capable of modifying later-cycle knowledge, designs, policies, systems, capabilities, practices, or infrastructures.",
            },
            boundary["research_universe_distinctions"],
        )
        self.assertEqual(
            "This boundary defines a sampling universe for civilization-scale recurrent improvement while excluding generic activity, routine execution, and AI use per se. 'Institutionalized or scalable' includes formal organizations and institutions as well as reproducible or propagating processes such as scientific communities, open-source communities, markets, and decentralized networks; it excludes purely private one-off self-improvement. Fixing this boundary is prospective for Domain candidate construction only. It does not establish or lock a Domain Universe, imply that a Singularity will occur, or authorize Wave 0.",
            boundary["rationale"],
        )

    def test_repository_has_exact_four_pending_source_frame_registrations(self) -> None:
        frame_paths = sorted((ROOT / "domain-universe/source-frames").glob("*.json"))
        expected_extractions = {
            "oecd-ford-frascati-2015": "domain-universe/extractions/oecd-ford-frascati-2015-second-level.json",
            "un-cofog-1999": "domain-universe/extractions/un-cofog-1999-group.json",
            "un-isic-rev5": "domain-universe/extractions/un-isic-rev5-division.json",
            "wipo-ipc-2026-01": "domain-universe/extractions/wipo-ipc-2026-01-class.json",
        }
        expected = {
            "oecd-ford-frascati-2015": (
                "oecd-frascati-ford", "research-knowledge-domain", "scientific_research",
                "https://www.oecd.org/en/publications/frascati-manual-2015_9789264239012-en.html",
            ),
            "un-cofog-1999": (
                "un-cofog", "public-purpose", "public_institutional_function",
                "https://unstats.un.org/unsd/classifications/Econ",
            ),
            "un-isic-rev5": (
                "un-isic", "economic-activity", "economic_activity",
                "https://unstats.un.org/unsd/classifications/Econ/ISIC.cshtml",
            ),
            "wipo-ipc-2026-01": (
                "wipo-ipc", "technology-domain", "engineering_technology",
                "https://www.wipo.int/classifications/data/ipc/ITSupport_and_download_area/20260101/MasterFiles/",
            ),
        }
        self.assertEqual([f"{frame_id}.json" for frame_id in sorted(expected)], [path.name for path in frame_paths])
        frames = [json.loads(path.read_text(encoding="utf-8")) for path in frame_paths]
        for path, frame in zip(frame_paths, frames):
            self.assertEqual([], VALIDATE.validate_contract(frame, self.schemas["source_frame"], str(path)))
            self.assertEqual(path.stem, frame["source_frame_id"])
            self.assertEqual(expected[path.stem], (
                frame["source_lineage_id"], frame["independence_group"],
                frame["classification_family"], frame["source_uri"],
            ))
            self.assertEqual("pending", frame["normalization_status"])
            self.assertIn("Exhaustive Task 104 source extraction is complete", frame["normalization_note"])
            self.assertIn(expected_extractions[path.stem], frame["normalization_note"])
            self.assertIn("normalization and candidate generation have not begun", frame["normalization_note"].lower())
        self.assertEqual(4, len({frame["source_lineage_id"] for frame in frames}))
        self.assertEqual(4, len({frame["independence_group"] for frame in frames}))
        self.assertEqual(1, len({frame["registered_at"] for frame in frames}))
        boundary = json.loads(
            (ROOT / "domain-universe/boundaries/du-boundary-v0.1.json").read_text(encoding="utf-8")
        )
        self.assertEqual({boundary["fixed_at"]}, {frame["registered_at"] for frame in frames})

    def test_repository_has_exact_four_complete_hash_bound_extractions(self) -> None:
        expected = {
            "oecd-ford-frascati-2015-second-level.json": (
                "domain-universe/source-frames/oecd-ford-frascati-2015.json", 42,
            ),
            "un-cofog-1999-group.json": (
                "domain-universe/source-frames/un-cofog-1999.json", 69,
            ),
            "un-isic-rev5-division.json": (
                "domain-universe/source-frames/un-isic-rev5.json", 87,
            ),
            "wipo-ipc-2026-01-class.json": (
                "domain-universe/source-frames/wipo-ipc-2026-01.json", 132,
            ),
        }
        extraction_paths = sorted((ROOT / "domain-universe/extractions").glob("*.json"))
        self.assertEqual(sorted(expected), [path.name for path in extraction_paths])
        total_entries = 0
        for path in extraction_paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            frame_path, expected_count = expected[path.name]
            self.assertEqual([], VALIDATE.validate_contract(record, self.schemas["extraction"], str(path)))
            self.assertEqual(path.stem, record["extraction_id"])
            self.assertEqual("complete", record["extraction_status"])
            self.assertEqual(frame_path, record["source_frame"]["path"])
            # Scientific JSON is canonicalized to LF in .gitattributes. Normalize
            # a pre-existing Windows checkout before hashing the repository bytes.
            frame_bytes = (ROOT / frame_path).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(hashlib.sha256(frame_bytes).hexdigest(), record["source_frame"]["sha256"])
            self.assertEqual(expected_count, len(record["extracted_entries"]))
            self.assertIn(f"Expected entry count: {expected_count}", record["extraction_scope"])
            self.assertIn(f"Observed entry count: {expected_count}", record["extraction_scope"])
            self.assertIn("Official source retrieval URL: https://", record["rationale"])
            self.assertRegex(record["rationale"], r"Retrieved at: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
            self.assertRegex(record["rationale"], r"SHA-256[^:]*: [a-f0-9]{64}")
            total_entries += len(record["extracted_entries"])
        self.assertEqual(330, total_entries)

    def test_real_extraction_entries_are_unique_unresolved_source_categories(self) -> None:
        patterns = {
            "oecd-ford-frascati-2015-second-level.json": (
                r"ford-[1-6]\.\d{1,2}", r"FORD 2015 / [1-6] .+ / [1-6]\.\d{1,2}",
            ),
            "un-isic-rev5-division.json": (
                r"isic-\d{2}", r"ISIC Rev\.5 / Section [A-V] .+ / Division \d{2}",
            ),
            "wipo-ipc-2026-01-class.json": (
                r"ipc-[A-H]\d{2}", r"IPC 2026\.01 / Section [A-H] .+ / Class [A-H]\d{2}",
            ),
            "un-cofog-1999-group.json": (
                r"cofog-\d{2}\.\d", r"COFOG 1999 / Division \d{2} .+ / Group \d{2}\.\d",
            ),
        }
        all_ids: list[str] = []
        for filename, (id_pattern, reference_pattern) in patterns.items():
            record = json.loads((ROOT / "domain-universe/extractions" / filename).read_text(encoding="utf-8"))
            entries = record["extracted_entries"]
            ids = [entry["source_entry_id"] for entry in entries]
            self.assertEqual(len(ids), len(set(ids)))
            all_ids.extend(ids)
            for entry in entries:
                self.assertRegex(entry["source_entry_id"], rf"^{id_pattern}$")
                self.assertRegex(entry["source_entry_reference"], rf"^{reference_pattern}$")
                self.assertTrue(entry["source_entry_descriptor"].strip())
                self.assertEqual("unresolved", entry["normalization_disposition"])
                self.assertEqual([], entry["target_domain_candidate_ids"])
                self.assertIn("Domain normalization and candidate generation are deferred", entry["rationale"])
        self.assertEqual(330, len(all_ids))
        self.assertEqual(330, len(set(all_ids)))

    def test_repository_extraction_state_has_no_normalization_or_downstream_records(self) -> None:
        for directory in (
            "candidates", "eligibility", "relations", "proposals", "reviews",
            "governance", "manifests",
        ):
            self.assertEqual([], list((ROOT / "domain-universe" / directory).glob("*.json")))
        self.assertEqual([], list((ROOT / "selection").rglob("*.json")))
        self.assertEqual([ROOT / "data/waves/README.md"], list((ROOT / "data/waves").rglob("*")))
        registry_lines = (ROOT / "registry/live-registry.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(1, len(registry_lines))
        current_state = (ROOT / "domain-universe/README.md").read_text(encoding="utf-8")
        self.assertIn("330 source categories", current_state)
        self.assertIn("not Domains", current_state)
        self.assertIn("candidate generation has not begun", current_state)
        self.assertIn("Pass 2A high-precision equivalence grouping", current_state)
        self.assertIn("included or locked Domain", current_state)
        self.assertIn("The Domain Universe is not established or locked", current_state)
        self.assertIn("Wave 0 remains unauthorized", current_state.replace("\n", " "))

    def test_normalization_codebook_v0_1_is_prospectively_fixed(self) -> None:
        path = ROOT / "domain-universe/NORMALIZATION_CODEBOOK.md"
        self.assertTrue(path.is_file())
        codebook = path.read_text(encoding="utf-8")
        self.assertIn("# Domain Universe Normalization Decision Codebook", codebook)
        self.assertIn("Version: `v0.1`", codebook)
        self.assertIn(
            "PROSPECTIVELY FIXED FOR NORMALIZATION; NOT SCIENTIFICALLY APPROVED",
            codebook,
        )
        self.assertIn("Effective normalization batch: **none yet**", codebook)
        for phrase in (
            "Normalization is a topic-preserving translation",
            "Semantic equivalence is not partial overlap.",
            "Preserve overlap; do not normalize it away.",
            "Normalization is blind to expected AI advancement",
        ):
            self.assertIn(phrase, codebook)
        self.assertIn("RESERVED / DISABLED IN NORMALIZATION v0.1", codebook)
        self.assertIn("(source_frame_id, source_entry_id)", codebook)
        self.assertIn("no scientific priority, evidentiary priority, or conceptual", codebook)
        self.assertIn("Pass 1 — independent entry interpretation", codebook)
        self.assertIn("Pass 2 — cross-entry equivalence clustering", codebook)
        self.assertIn("du-cand-NNNN", codebook)
        self.assertIn("du-cand-0001", codebook)

    def test_codebook_fixation_does_not_start_normalization(self) -> None:
        extraction_paths = sorted((ROOT / "domain-universe/extractions").glob("*.json"))
        entries = []
        for path in extraction_paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            entries.extend(record["extracted_entries"])
        self.assertEqual(4, len(extraction_paths))
        self.assertEqual(330, len(entries))
        self.assertEqual(330, sum(
            entry["normalization_disposition"] == "unresolved" for entry in entries
        ))
        self.assertTrue(all(entry["target_domain_candidate_ids"] == [] for entry in entries))

        frames = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "domain-universe/source-frames").glob("*.json"))
        ]
        self.assertEqual(4, len(frames))
        self.assertTrue(all(frame["normalization_status"] == "pending" for frame in frames))
        for directory in (
            "candidates", "eligibility", "relations", "proposals", "reviews",
            "governance", "manifests",
        ):
            self.assertEqual([], list((ROOT / "domain-universe" / directory).glob("*.json")))
        self.assertEqual([], list((ROOT / "selection").rglob("*.json")))
        self.assertEqual([ROOT / "data/waves/README.md"], list((ROOT / "data/waves").rglob("*")))


class DomainNormalizationPass1Tests(unittest.TestCase):
    EXPECTED = {
        "oecd-ford-frascati-2015-pass1.json": (
            "domain-universe/extractions/oecd-ford-frascati-2015-second-level.json", 42,
        ),
        "un-isic-rev5-pass1.json": (
            "domain-universe/extractions/un-isic-rev5-division.json", 87,
        ),
        "wipo-ipc-2026-01-pass1.json": (
            "domain-universe/extractions/wipo-ipc-2026-01-class.json", 132,
        ),
        "un-cofog-1999-pass1.json": (
            "domain-universe/extractions/un-cofog-1999-group.json", 69,
        ),
    }

    def setUp(self) -> None:
        self.schema = json.loads(
            (ROOT / "schemas/domain-normalization-pass1.schema.json").read_text(encoding="utf-8")
        )

    def _record(self, filename: str) -> dict[str, object]:
        return json.loads(
            (ROOT / "domain-universe/normalization/pass1" / filename).read_text(encoding="utf-8")
        )

    def _temporary_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for relative in (
            "schemas/domain-normalization-pass1.schema.json",
            "domain-universe/NORMALIZATION_CODEBOOK.md",
            "domain-universe/boundaries/du-boundary-v0.1.json",
        ):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        for relative in (
            "domain-universe/extractions",
            "domain-universe/normalization/pass1",
        ):
            shutil.copytree(ROOT / relative, root / relative)
        return temporary, root

    def test_exact_four_pass1_records_bind_exact_artifacts_and_counts(self) -> None:
        paths = sorted((ROOT / "domain-universe/normalization/pass1").glob("*.json"))
        self.assertEqual(sorted(self.EXPECTED), [path.name for path in paths])
        total = 0
        for path in paths:
            extraction_relative, expected_count = self.EXPECTED[path.name]
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual([], VALIDATE.validate_contract(record, self.schema, str(path)))
            self.assertEqual(path.stem, record["pass1_record_id"])
            self.assertEqual("0.5.0-draft", record["instrument_version"])
            self.assertEqual("independent_entry_interpretation", record["procedure"])
            self.assertEqual("complete", record["status"])
            self.assertEqual([], record["clarification_sources"])
            self.assertEqual(expected_count, len(record["interpretations"]))
            for field, relative in (
                ("normalization_codebook", "domain-universe/NORMALIZATION_CODEBOOK.md"),
                ("universe_boundary", "domain-universe/boundaries/du-boundary-v0.1.json"),
                ("source_extraction", extraction_relative),
            ):
                self.assertEqual(relative, record[field]["path"])
                self.assertEqual(
                    NORMALIZATION_VALIDATE.canonical_lf_sha256(ROOT / relative),
                    record[field]["sha256"],
                )
            total += len(record["interpretations"])
        self.assertEqual(330, total)

    def test_every_extracted_entry_has_one_exact_complete_interpretation(self) -> None:
        required = {
            "frame_role_stripping", "normalized_substantive_locus",
            "minimal_gate_result", "evidence_basis", "clarification_source_ids",
            "rationale", "uncertainty",
        }
        prohibited = {
            "related_source_entry_ids", "equivalent_source_entry_ids", "cluster_id",
            "target_candidate_id", "candidate_id", "overlap_relation", "merge_target",
            "similarity_score",
        }
        for filename, (extraction_relative, _) in self.EXPECTED.items():
            record = self._record(filename)
            extraction = json.loads((ROOT / extraction_relative).read_text(encoding="utf-8"))
            extracted = {entry["source_entry_id"]: entry for entry in extraction["extracted_entries"]}
            interpretations = record["interpretations"]
            self.assertEqual(len(interpretations), len({item["source_entry_id"] for item in interpretations}))
            self.assertEqual(set(extracted), {item["source_entry_id"] for item in interpretations})
            for item in interpretations:
                source = extracted[item["source_entry_id"]]
                self.assertEqual(source["source_entry_reference"], item["source_entry_reference"])
                self.assertEqual(source["source_entry_descriptor"], item["source_entry_descriptor"])
                self.assertTrue(required.issubset(item))
                self.assertTrue(prohibited.isdisjoint(item))

    def test_pass1_distribution_is_audited_without_target(self) -> None:
        expected = {
            "oecd-ford-frascati-2015-pass1.json": (42, 0, 0),
            "un-isic-rev5-pass1.json": (87, 0, 0),
            "wipo-ipc-2026-01-pass1.json": (124, 0, 8),
            "un-cofog-1999-pass1.json": (69, 0, 0),
        }
        totals = {"passes": 0, "fails_out_of_scope": 0, "unresolved": 0}
        for filename, expected_counts in expected.items():
            record = self._record(filename)
            counts = {
                result: sum(
                    item["minimal_gate_result"] == result for item in record["interpretations"]
                )
                for result in totals
            }
            self.assertEqual(expected_counts, tuple(counts[result] for result in totals))
            for result, count in counts.items():
                totals[result] += count
        self.assertEqual({"passes": 322, "fails_out_of_scope": 0, "unresolved": 8}, totals)
        summary = (ROOT / "domain-universe/normalization/PASS1_SUMMARY.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("**322** | **0** | **8** | **330**", summary)
        self.assertIn("Clarification-source use count: **0**", summary)
        self.assertIn("There is no acceptable target distribution", summary)
        self.assertIn("No cross-entry equivalence comparison occurred", summary)
        self.assertIn("No equivalence cluster", summary)

    def test_passes_and_evidence_conditionals_fail_closed(self) -> None:
        record = self._record("oecd-ford-frascati-2015-pass1.json")
        interpretation = record["interpretations"][0]
        mutations = (
            {"normalized_substantive_locus": None},
            {
                "frame_role_stripping": {"action": "unresolved", "note": "test only"},
                "minimal_gate_result": "passes",
            },
            {"clarification_source_ids": ["test-source"]},
            {
                "evidence_basis": "official_same_classification_clarification",
                "clarification_source_ids": [],
            },
        )
        for mutation in mutations:
            changed = json.loads(json.dumps(record))
            changed["interpretations"][0].update(mutation)
            self.assertTrue(VALIDATE.validate_contract(changed, self.schema, str(mutation)))
        self.assertEqual("passes", interpretation["minimal_gate_result"])

    def test_schema_rejects_candidate_cluster_and_cross_entry_fields(self) -> None:
        record = self._record("oecd-ford-frascati-2015-pass1.json")
        for field in (
            "related_source_entry_ids", "equivalent_source_entry_ids", "cluster_id",
            "target_candidate_id", "candidate_id", "overlap_relation", "merge_target",
            "similarity_score",
        ):
            changed = json.loads(json.dumps(record))
            changed["interpretations"][0][field] = "prohibited-test-value"
            errors = VALIDATE.validate_contract(changed, self.schema, field)
            self.assertTrue(any(f"unexpected field '{field}'" in error for error in errors))

    def test_normalization_validator_rejects_tamper_omission_and_copy_mismatch(self) -> None:
        def validate_mutation(mutate) -> list[str]:
            temporary, root = self._temporary_fixture()
            try:
                path = root / "domain-universe/normalization/pass1/oecd-ford-frascati-2015-pass1.json"
                record = json.loads(path.read_text(encoding="utf-8"))
                mutate(record)
                write_json(path, record)
                return NORMALIZATION_VALIDATE.validate_normalization_repository(
                    root, VALIDATE.validate_contract
                )
            finally:
                temporary.cleanup()

        errors = validate_mutation(
            lambda record: record["source_extraction"].update({"sha256": "0" * 64})
        )
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

        errors = validate_mutation(lambda record: record["interpretations"].pop())
        self.assertTrue(any("expected 42 interpretations" in error for error in errors))
        self.assertTrue(any("interpretation IDs must exactly match" in error for error in errors))

        errors = validate_mutation(
            lambda record: record["interpretations"][0].update(
                {"source_entry_descriptor": "tampered test descriptor"}
            )
        )
        self.assertTrue(any("source_entry_descriptor mismatch" in error for error in errors))

    def test_task104_and_all_downstream_scientific_state_remain_unchanged(self) -> None:
        entries = []
        for path in sorted((ROOT / "domain-universe/extractions").glob("*.json")):
            entries.extend(json.loads(path.read_text(encoding="utf-8"))["extracted_entries"])
        self.assertEqual(330, len(entries))
        self.assertTrue(all(item["normalization_disposition"] == "unresolved" for item in entries))
        self.assertTrue(all(item["target_domain_candidate_ids"] == [] for item in entries))
        frames = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "domain-universe/source-frames").glob("*.json"))
        ]
        self.assertEqual(4, len(frames))
        self.assertTrue(all(frame["normalization_status"] == "pending" for frame in frames))
        for directory in (
            "candidates", "eligibility", "relations", "proposals", "reviews",
            "governance", "manifests",
        ):
            self.assertEqual([], list((ROOT / "domain-universe" / directory).glob("*.json")))
        self.assertEqual([], list((ROOT / "selection").rglob("*.json")))
        self.assertEqual([ROOT / "data/waves/README.md"], list((ROOT / "data/waves").rglob("*")))
        self.assertEqual(
            1,
            len((ROOT / "registry/live-registry.csv").read_text(encoding="utf-8").splitlines()),
        )


class DomainNormalizationPass2ATests(unittest.TestCase):
    PATH = ROOT / "domain-universe/normalization/pass2a/equivalence-groups-v0.1.json"

    def setUp(self) -> None:
        self.schema = json.loads(
            (ROOT / "schemas/domain-normalization-pass2a.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.record = json.loads(self.PATH.read_text(encoding="utf-8"))
        self.pass1_index, self.record_hashes, errors = (
            NORMALIZATION_VALIDATE.build_pass1_index(ROOT)
        )
        self.assertEqual([], errors)

    def _errors(self, record: dict[str, object]) -> list[str]:
        return VALIDATE.validate_contract(record, self.schema, "test-pass2a") + (
            NORMALIZATION_VALIDATE.validate_pass2a_record(
                record, self.pass1_index, self.record_hashes, "test-pass2a"
            )
        )

    @staticmethod
    def _synthetic_clique() -> tuple[dict[tuple[str, str], dict[str, object]], dict[str, object]]:
        keys = [("test-frame", f"test-entry-{letter}") for letter in "abc"]
        record_ref = {"path": "test/pass1.json", "sha256": "0" * 64}
        index = {
            key: {
                "record_path": record_ref["path"],
                "record_sha256": record_ref["sha256"],
                "minimal_gate_result": "passes",
                "normalized_substantive_locus": "test-only structural locus",
            }
            for key in keys
        }

        def locator(key: tuple[str, str]) -> dict[str, str]:
            return {"source_frame_id": key[0], "source_entry_id": key[1]}

        members = [
            {
                **locator(key),
                "pass1_record": record_ref,
                "normalized_substantive_locus": "test-only structural locus",
            }
            for key in keys
        ]
        assertions = []
        for left_index in range(len(keys)):
            for right_index in range(left_index + 1, len(keys)):
                assertions.append(
                    {
                        "left_member": locator(keys[left_index]),
                        "right_member": locator(keys[right_index]),
                        "same_substantive_locus": True,
                        "equivalent_inclusion_envelope": True,
                        "equivalent_exclusion_envelope": True,
                        "no_material_scope_asymmetry": True,
                        "lens_difference_only": True,
                        "rationale": "test-only complete-clique fixture",
                        "uncertainty": "structural validation only; no scientific claim",
                    }
                )
        group = {
            "normalization_group_id": NORMALIZATION_VALIDATE.group_id_for_members(keys),
            "group_kind": "coextensive_equivalence",
            "members": members,
            "deterministic_anchor": locator(min(keys)),
            "group_locus_statement": "test-only structural locus",
            "pairwise_equivalence_assertions": assertions,
            "rationale": "test-only complete-clique fixture",
            "uncertainty": "structural validation only; no scientific claim",
        }
        return index, group

    def test_schema_and_exact_single_artifact_exist(self) -> None:
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", self.schema["$schema"])
        self.assertEqual("0.5.0-draft", self.schema["x-instrument-version"])
        self.assertEqual(
            [self.PATH],
            list((ROOT / "domain-universe/normalization/pass2a").glob("*.json")),
        )
        self.assertEqual([], VALIDATE.validate_contract(self.record, self.schema, str(self.PATH)))

    def test_exact_codebook_boundary_and_immutable_pass1_hashes_resolve(self) -> None:
        for field, relative in (
            ("normalization_codebook", "domain-universe/NORMALIZATION_CODEBOOK.md"),
            ("universe_boundary", "domain-universe/boundaries/du-boundary-v0.1.json"),
        ):
            self.assertEqual(relative, self.record[field]["path"])
            self.assertEqual(
                NORMALIZATION_VALIDATE.canonical_lf_sha256(ROOT / relative),
                self.record[field]["sha256"],
            )
        self.assertEqual(self.record_hashes, {
            item["path"]: item["sha256"] for item in self.record["pass1_records"]
        })
        self.assertEqual(
            set(NORMALIZATION_VALIDATE.EXPECTED_PASS1_SHA256.values()),
            set(self.record_hashes.values()),
        )

    def test_tampered_pass1_bytes_fail_immutable_input_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(
                ROOT / "domain-universe/normalization/pass1",
                root / "domain-universe/normalization/pass1",
            )
            path = root / (
                "domain-universe/normalization/pass1/"
                "oecd-ford-frascati-2015-pass1.json"
            )
            changed = json.loads(path.read_text(encoding="utf-8"))
            changed["interpretations"][0]["uncertainty"] += " test-only tamper"
            write_json(path, changed)
            _, _, errors = NORMALIZATION_VALIDATE.build_pass1_index(root)
        self.assertTrue(any("immutable Pass 1 bytes changed" in error for error in errors))

    def test_partition_accounts_for_322_passes_and_eight_unresolved_once(self) -> None:
        grouped = [
            (member["source_frame_id"], member["source_entry_id"])
            for group in self.record["groups"]
            for member in group["members"]
        ]
        excluded = [
            (item["source_frame_id"], item["source_entry_id"])
            for item in self.record["excluded_from_grouping"]
        ]
        self.assertEqual(322, len(grouped))
        self.assertEqual(322, len(set(grouped)))
        self.assertEqual(8, len(excluded))
        self.assertEqual(8, len(set(excluded)))
        self.assertEqual(NORMALIZATION_VALIDATE.EXPECTED_UNRESOLVED, set(excluded))
        self.assertEqual(330, len(grouped) + len(excluded))

    def test_repository_group_ids_anchors_and_kind_rules_are_deterministic(self) -> None:
        kinds = {"singleton": 0, "coextensive_equivalence": 0}
        for index, group in enumerate(self.record["groups"]):
            keys = [
                (member["source_frame_id"], member["source_entry_id"])
                for member in group["members"]
            ]
            self.assertEqual(
                NORMALIZATION_VALIDATE.group_id_for_members(keys),
                group["normalization_group_id"],
            )
            self.assertEqual(
                {"source_frame_id": min(keys)[0], "source_entry_id": min(keys)[1]},
                group["deterministic_anchor"],
            )
            errors, _ = NORMALIZATION_VALIDATE.validate_group_structure(
                group, self.pass1_index, f"group[{index}]"
            )
            self.assertEqual([], errors)
            kinds[group["group_kind"]] += 1
        self.assertEqual({"singleton": 322, "coextensive_equivalence": 0}, kinds)

    def test_complete_three_member_pairwise_clique_passes_structural_gate(self) -> None:
        index, group = self._synthetic_clique()
        errors, _ = NORMALIZATION_VALIDATE.validate_group_structure(
            group, index, "test-only-group"
        )
        self.assertEqual([], errors)

    def test_removing_one_required_pairwise_assertion_fails(self) -> None:
        index, group = self._synthetic_clique()
        group["pairwise_equivalence_assertions"].pop()
        errors, _ = NORMALIZATION_VALIDATE.validate_group_structure(
            group, index, "test-only-group"
        )
        self.assertTrue(any("complete equivalence clique" in error for error in errors))

    def test_one_false_equivalence_criterion_fails(self) -> None:
        index, group = self._synthetic_clique()
        group["pairwise_equivalence_assertions"][0]["lens_difference_only"] = False
        errors, _ = NORMALIZATION_VALIDATE.validate_group_structure(
            group, index, "test-only-group"
        )
        self.assertTrue(any("lens_difference_only must be true" in error for error in errors))

    def test_transitive_chain_without_endpoint_pair_fails(self) -> None:
        index, group = self._synthetic_clique()
        assertions = group["pairwise_equivalence_assertions"]
        group["pairwise_equivalence_assertions"] = [assertions[0], assertions[2]]
        errors, _ = NORMALIZATION_VALIDATE.validate_group_structure(
            group, index, "test-only-transitive-chain"
        )
        self.assertTrue(any("complete equivalence clique" in error for error in errors))

    def test_unresolved_member_omitted_pass_and_duplicate_pass_all_fail(self) -> None:
        unresolved = json.loads(json.dumps(self.record))
        excluded = unresolved["excluded_from_grouping"][0]
        key = excluded["source_frame_id"], excluded["source_entry_id"]
        group = unresolved["groups"][0]
        group["members"] = [{
            "source_frame_id": key[0],
            "pass1_record": excluded["pass1_record"],
            "source_entry_id": key[1],
            "normalized_substantive_locus": self.pass1_index[key][
                "normalized_substantive_locus"
            ],
        }]
        group["normalization_group_id"] = NORMALIZATION_VALIDATE.group_id_for_members([key])
        group["deterministic_anchor"] = {
            "source_frame_id": key[0], "source_entry_id": key[1]
        }
        group["group_locus_statement"] = "test-only invalid unresolved grouping"
        self.assertTrue(any("only Pass 1 passes" in error for error in self._errors(unresolved)))

        omitted = json.loads(json.dumps(self.record))
        omitted["groups"].pop()
        self.assertTrue(any("partition every Pass 1 pass" in error for error in self._errors(omitted)))

        duplicated = json.loads(json.dumps(self.record))
        duplicated["groups"].append(json.loads(json.dumps(duplicated["groups"][0])))
        duplicate_errors = self._errors(duplicated)
        self.assertTrue(any("multiple groups" in error for error in duplicate_errors))

    def test_deferred_equivalence_pair_cannot_already_be_merged(self) -> None:
        changed = json.loads(json.dumps(self.record))
        deferred = changed["deferred_equivalence_questions"][0]
        left = (
            deferred["left_member"]["source_frame_id"],
            deferred["left_member"]["source_entry_id"],
        )
        right = (
            deferred["right_member"]["source_frame_id"],
            deferred["right_member"]["source_entry_id"],
        )
        selected = []
        retained = []
        for group in changed["groups"]:
            key = (
                group["members"][0]["source_frame_id"],
                group["members"][0]["source_entry_id"],
            )
            if key in (left, right):
                selected.append(group["members"][0])
            else:
                retained.append(group)
        # Structural negative fixture only; this is not a scientific equivalence assertion.
        merged = {
            "normalization_group_id": NORMALIZATION_VALIDATE.group_id_for_members([left, right]),
            "group_kind": "coextensive_equivalence",
            "members": selected,
            "deterministic_anchor": deferred["left_member"],
            "group_locus_statement": selected[0]["normalized_substantive_locus"],
            "pairwise_equivalence_assertions": [{
                "left_member": deferred["left_member"],
                "right_member": deferred["right_member"],
                "same_substantive_locus": True,
                "equivalent_inclusion_envelope": True,
                "equivalent_exclusion_envelope": True,
                "no_material_scope_asymmetry": True,
                "lens_difference_only": True,
                "rationale": "test-only invalid deferred-and-merged fixture",
                "uncertainty": "structural validation only; no scientific claim",
            }],
            "rationale": "test-only invalid deferred-and-merged fixture",
            "uncertainty": "structural validation only; no scientific claim",
        }
        changed["groups"] = retained + [merged]
        self.assertTrue(any("deferred pair is already merged" in error for error in self._errors(changed)))

    def test_no_candidate_or_downstream_state_is_created(self) -> None:
        serialized = json.dumps(self.record)
        self.assertNotIn("du-cand-", serialized)
        self.assertEqual(
            [],
            NORMALIZATION_VALIDATE.find_prohibited_pass2a_content(
                self.record, "repository-pass2a"
            ),
        )
        self.assertEqual(
            [],
            NORMALIZATION_VALIDATE.find_prohibited_pass2a_content(
                self.schema, "pass2a-schema"
            ),
        )
        entries = []
        for path in sorted((ROOT / "domain-universe/extractions").glob("*.json")):
            entries.extend(json.loads(path.read_text(encoding="utf-8"))["extracted_entries"])
        self.assertEqual(330, sum(item["normalization_disposition"] == "unresolved" for item in entries))
        self.assertEqual(330, sum(item["target_domain_candidate_ids"] == [] for item in entries))
        frames = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "domain-universe/source-frames").glob("*.json"))
        ]
        self.assertEqual(4, sum(frame["normalization_status"] == "pending" for frame in frames))
        for directory in (
            "candidates", "eligibility", "relations", "proposals", "reviews",
            "governance", "manifests",
        ):
            self.assertEqual([], list((ROOT / "domain-universe" / directory).glob("*.json")))
        self.assertEqual([], list((ROOT / "selection").rglob("*.json")))
        self.assertEqual([ROOT / "data/waves/README.md"], list((ROOT / "data/waves").rglob("*")))
        self.assertEqual(1, len((ROOT / "registry/live-registry.csv").read_text(encoding="utf-8").splitlines()))


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

        # The remaining mutation isolates historical Wave self-containment.
        # Pass 1 is already validated above and has its own immutability tests;
        # it is not part of this fixture's synthetic current-v2 migration.
        shutil.rmtree(self.repository.root / "domain-universe/normalization")
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

    def test_frozen_panel_requires_hash_bound_selection_manifest(self) -> None:
        manifest = self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        panel_relative = manifest["panel_snapshot"]["path"]
        panel_path = self.repository.root / panel_relative
        snapshot = json.loads(panel_path.read_text(encoding="utf-8"))
        del snapshot["selection_manifest"]
        write_json(panel_path, snapshot)
        manifest["panel_snapshot"] = self.repository.reference(panel_relative)
        self.repository.save_manifest("wave-0", manifest)
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("selection_manifest" in error for error in errors))

    def test_same_panel_id_with_altered_semantic_identity_fails(self) -> None:
        manifest = self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        panel_relative = manifest["panel_snapshot"]["path"]
        panel_path = self.repository.root / panel_relative
        snapshot = json.loads(panel_path.read_text(encoding="utf-8"))
        snapshot["units"][0]["operational_boundary"] = "altered test-only boundary"
        snapshot["units"][0]["continuity_rule"] = "altered test-only continuity rule"
        write_json(panel_path, snapshot)
        manifest["panel_snapshot"] = self.repository.reference(panel_relative)
        self.repository.save_manifest("wave-0", manifest)
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("semantic identity field 'operational_boundary'" in error for error in errors))
        self.assertTrue(any("semantic identity field 'continuity_rule'" in error for error in errors))

    def test_frozen_panel_must_preserve_exact_candidate_path_and_hash(self) -> None:
        manifest = self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        panel_relative = manifest["panel_snapshot"]["path"]
        panel_path = self.repository.root / panel_relative
        snapshot = json.loads(panel_path.read_text(encoding="utf-8"))
        snapshot["units"][0]["candidate_specification"]["sha256"] = "a" * 64
        write_json(panel_path, snapshot)
        manifest["panel_snapshot"] = self.repository.reference(panel_relative)
        self.repository.save_manifest("wave-0", manifest)
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("exact candidate specification path and SHA-256 binding" in error for error in errors))

    def test_tampered_candidate_specification_fails_sha_binding(self) -> None:
        self.repository.create_wave(
            "wave-0", [panel_unit()], [unresolved_observation()]
        )
        selection_path = self.repository.root / "data/waves/wave-0/selection/manifest.json"
        selection = json.loads(selection_path.read_text(encoding="utf-8"))
        candidate_reference = selection["candidate_universe_snapshot"][
            "candidate_specifications"
        ][0]
        candidate_path = self.repository.root / candidate_reference["path"]
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        candidate["operational_boundary"] = "tampered test-only boundary"
        write_json(candidate_path, candidate)
        errors = VALIDATE.validate_repository(self.repository.root)
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

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
