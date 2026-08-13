# Observation Protocol

- Instrument: Observation Protocol
- Instrument version: `0.1.0-draft`
- Status: `DRAFT`
- Effective Wave: none

## Purpose

This protocol defines how the Singularity Observatory may conduct cross-domain longitudinal observation of technology and sociotechnical systems. It is infrastructure for asking:

> Where, when, and how does human criticality disappear from civilization's improvement loops?

The question is a research question, not an empirical conclusion. Terms that remain scientifically unsettled must stay explicit and versioned.

## Units and scope

A candidate case is a bounded technology or sociotechnical system proposed in the Live Registry. Admission to a Frozen Panel requires a documented rule, stable identifier, scope statement, and review decision. This draft does not admit any case.

An observation is a source-backed record about a defined case, construct, and observation date. An evidence record is not itself a conclusion. Derived assessments must retain links to every supporting and conflicting evidence record.

## Frozen Panel and Live Registry

The two instruments serve different purposes:

1. The **Live Registry** is mutable and may receive candidates between Waves. Registry membership does not make a candidate part of an official Wave.
2. A **Frozen Panel** is an immutable, versioned snapshot selected for a specified Wave under the rules in `PANEL.md`.
3. Adding a registry candidate never alters a previously frozen panel.
4. Every Wave manifest must identify its panel snapshot separately from its registry snapshot.

## Observation workflow

1. Register a candidate without making an empirical claim.
2. Apply the versioned panel-selection rule.
3. Lock the Wave schedule and required instruments.
4. Collect source metadata and record the observation date.
5. Code only what the evidence supports, including conflicting evidence.
6. Preserve `unknown` when evidence is missing, inaccessible, ambiguous, or out of scope.
7. Validate and lock the Wave package.
8. Publish analysis separately from raw evidence and coded observations.

## Longitudinal representation

The schema and codebook must allow:

- a transition toward reduced human criticality;
- a reversal toward greater human criticality;
- human re-entry after prior reduced criticality;
- no supported determination; and
- conflicting or incomplete evidence.

No transition, reversal, or re-entry is presumed by this protocol.

## Evidence standard

Every evidence record must include a stable identifier, case identifier, source locator, source title, source type, observation date, retrieval timestamp, recorder, and content hash. The record must distinguish what the source states from any coding or interpretation.

Absence may be coded only when the versioned instrument defines an observable opportunity and evidence supports non-occurrence within that scope. Otherwise the value is `unknown`.

## Wave lifecycle

Permitted lifecycle states are `draft`, `locked`, and `official`.

- **Draft:** content may change and must not be represented as official.
- **Locked:** the package is immutable; corrections are append-only amendments or later-Wave records.
- **Official:** all required locks exist, structural validation passes, and the governance authority records release approval.

An official Wave manifest must lock the protocol, Frozen Panel, schema bundle, observation schedule, and governance record by version and SHA-256 digest. The repository validator rejects official status when any required lock is absent or malformed.

## Change policy

Before Wave 0, draft instruments may be revised with normal version control. Once Wave 0 is locked, a protocol change requires:

1. a new instrument version;
2. a dated decision record describing the reason and expected comparability impact;
3. retention of the prior version through Git history and Wave lock hashes; and
4. an explicit effective-Wave boundary.

Silent rewriting is prohibited.

## Unresolved before Wave 0

- operational boundaries of an improvement loop;
- case inclusion and exclusion rules;
- observable criteria for human criticality;
- domain stratification and panel size;
- observation cadence and schedule;
- inter-rater process and disagreement handling;
- amendment and release authority; and
- licensing for data, code, and documentation.
