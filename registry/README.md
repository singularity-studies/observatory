# Live Registry

- Instrument: Live Registry Specification
- Instrument version: `0.1.0-draft`
- Status: `DRAFT`

The Live Registry is a mutable inventory of candidate cases. It is not a Frozen Panel and must never be used as one by implication.

`live-registry.csv` currently contains only its header. Adding a candidate records a proposal, not an empirical observation or an inclusion decision. Every row requires a stable registry identifier, label, registry status, addition date, and provenance locator.

Permitted draft statuses are `candidate`, `under_review`, `eligible`, `ineligible`, and `withdrawn`. Eligibility criteria remain unresolved and must be versioned before any status beyond `candidate` is used.

A Wave must record both the registry snapshot used during selection and the separately frozen panel snapshot.
