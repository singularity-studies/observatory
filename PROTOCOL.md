# Observation Protocol

- Instrument: Observation Protocol
- Instrument version: `0.2.0-draft`
- Status: `DRAFT`
- Effective Wave: none

## Purpose

This protocol defines how the Singularity Observatory may conduct cross-domain longitudinal observation of improvement-loop functions and their empirical sociotechnical instantiations. It is infrastructure for asking:

> How does human criticality change across civilization’s improvement loops, and where—if anywhere—does it cease to be necessary?

The question is a research question, not an empirical conclusion. Persistence, transition, reversal, and human re-entry are equally valid possible outcomes. Terms that remain scientifically unsettled must stay explicit and versioned.

## Units and scope

A candidate **panel unit** is a bounded function or stage within a defined civilization improvement loop. It is framed as a potential **Human Bottleneck**: a location at which human contribution may or may not remain critical. The framing identifies a question for observation, not a claim that a bottleneck exists or will disappear.

Technologies, products, organizations, deployments, and other sociotechnical systems are normally empirical instantiations or evidence contexts rather than primary panel units. A panel unit may link to multiple empirical systems, and an empirical system may be relevant to multiple functions when those relationships are explicit.

Admission to a Frozen Panel requires a documented rule, stable panel-unit identifier, improvement-loop boundary, function/stage definition, Human-Bottleneck hypothesis, scope statement, and review decision. This draft admits no panel unit.

An observation is a source-backed record about a defined panel unit, one or more linked empirical systems, a construct, and an observation date. An evidence record is not itself a conclusion. Derived assessments must retain links to every supporting and conflicting evidence record.

## Frozen Panel and Live Registry

The two instruments serve different purposes:

1. The **Live Registry** is mutable and may receive candidate improvement-loop functions between Waves. Registry membership does not make a candidate a Frozen Panel unit.
2. A **Frozen Panel** is an immutable, versioned snapshot selected for a specified Wave under the rules in `PANEL.md`.
3. Adding a registry unit or linking another empirical system never alters a previously frozen panel.
4. Every Wave manifest must identify its panel snapshot separately from its registry snapshot.

## Observation workflow

1. Register a candidate function/stage and its improvement-loop boundary without making an empirical claim.
2. Apply the versioned panel-selection rule.
3. Lock the Wave schedule and required instruments.
4. Collect source metadata and record the observation date.
5. Code only what the evidence supports, including conflicting evidence.
6. Preserve `unknown` when evidence is missing, inaccessible, ambiguous, or out of scope.
7. Validate and lock the Wave package.
8. Publish analysis separately from raw evidence and coded observations.

## Longitudinal representation

The schema and codebook must allow:

- persistence of human criticality;
- a transition toward reduced human criticality;
- a reversal toward greater human criticality;
- human re-entry after prior reduced criticality;
- no supported determination; and
- conflicting or incomplete evidence.

No persistence, transition, reversal, disappearance, or re-entry is presumed by this protocol.

## Evidence standard

Every evidence record must include a stable identifier, panel-unit identifier, linked empirical-system identifiers, source locator, source title, source type, observation date, retrieval timestamp, recorder, and content hash. The record must distinguish what the source states from any coding or interpretation.

Absence may be coded only when the versioned instrument defines an observable opportunity and evidence supports non-occurrence within that scope. Otherwise the value is `unknown`.

## Wave lifecycle

Permitted lifecycle states are `draft`, `locked`, and `official`.

- **Draft:** content may change and must not be represented as official.
- **Locked:** every byte in the Wave directory is immutable; corrections use separately versioned artifacts in `data/amendments/` or a later Wave.
- **Official:** all required locks exist, structural validation passes, and the governance authority records release approval.

An official Wave manifest must lock the protocol, Frozen Panel specification, schema bundle, observation schedule, and governance record by version plus repository-relative artifact paths and SHA-256 digests. It must also reference separately hashed Frozen Panel and Live Registry snapshots. The repository validator resolves every reference, recomputes every digest, checks version consistency, and rejects official status when any required artifact or relation is invalid.

## Change policy

Before Wave 0, draft instruments may be revised with normal version control. Once Wave 0 is locked, a protocol change requires:

1. a new instrument version;
2. a dated decision record describing the reason and expected comparability impact;
3. retention of the prior version through Git history and Wave lock hashes; and
4. an explicit effective-Wave boundary.

Silent rewriting is prohibited.

## Unresolved before Wave 0

- operational boundaries of an improvement loop and its functions/stages;
- panel-unit inclusion and exclusion rules;
- observable criteria for human criticality;
- the multidimensional measurement model and its relation to any provisional categorical summary;
- domain stratification and panel size;
- observation cadence and schedule;
- inter-rater process and disagreement handling;
- amendment and release authority; and
- licensing for data, code, and documentation.
