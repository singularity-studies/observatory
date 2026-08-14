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
CURRENT_SELECTION_VERSION = json.loads(
    (ROOT / "schemas/panel-selection-manifest.schema.json").read_text(encoding="utf-8")
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
) -> dict[str, object]:
    return {
        "review_record_id": "test-only-scientific-review",
        "instrument_version": version,
        "review_type": "panel_selection_scientific_review",
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
) -> dict[str, object]:
    return {
        "governance_decision_id": "test-only-governance-decision",
        "instrument_version": version,
        "decision_type": "frozen_panel_lock_authorization",
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

        review_relative = f"{base_relative}/reviews/scientific-review.json"
        write_json(
            self.root / review_relative,
            scientific_review_record(version),
        )
        authority_relative = f"{base_relative}/governance/decision.json"
        write_json(
            self.root / authority_relative,
            governance_decision_record(version),
        )

        manifest: dict[str, object] = {
            "selection_manifest_id": "test-only-selection-manifest",
            "instrument_version": version,
            "status": "locked",
            "selection_protocol": {
                "status": "locked",
                "version": version,
                "artifact": protocol_reference,
            },
            "candidate_universe_snapshot": {
                "snapshot_id": "test-only-candidate-universe",
                "captured_at": "2026-01-01T00:00:00Z",
                "candidate_specifications": candidate_references,
            },
            "eligibility_decisions": eligibility_references,
            "lineage_relations": [],
            "coverage_redundancy_review": {
                "status": "recorded",
                "rationale": "test-only structural coverage fixture",
                "uncertainty": "test-only; no empirical coverage determination",
            },
            "panel_size": {
                "status": "fixed",
                "n": len(selected_ids),
                "rationale": "test-only fixture size; not a proposed panel N",
            },
            "selection_dispositions": selection_dispositions,
            "selected_unit_ids": selected_ids,
            "scientific_review": {
                "status": "complete",
                "review_record": self.reference(review_relative),
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

    def test_selection_is_outcome_blind_and_wave_outcomes_remain_representable(self) -> None:
        panel = (ROOT / "PANEL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
        exact_principle = "Panel selection is outcome-blind with respect to human criticality."
        self.assertIn(exact_principle, panel)
        self.assertIn(exact_principle, protocol)
        self.assertNotIn("baseline_human_criticality", self.candidate_schema["properties"])
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

    def test_complete_temporary_selection_fixture_passes_internal_gate_only(self) -> None:
        errors = self._validate_manifest_change(lambda manifest: None)
        self.assertEqual([], errors)
        source = Path(__file__).read_text(encoding="utf-8")
        self.assertIn(
            "TEMPORARY TEST FIXTURE ONLY; exercises structure and does not record",
            source,
        )

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
