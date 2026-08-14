# Live Registry

- Instrument: Live Registry Specification
- Instrument version: `0.3.0-draft`
- Status: `DRAFT`

The Live Registry is a mutable inventory of candidate improvement-loop functions or stages framed as potential Human Bottlenecks. It is not a product inventory, a Frozen Panel, or evidence that any bottleneck exists.

`live-registry.csv` currently contains only its header. Adding a candidate records a proposal, not an empirical observation or an inclusion decision. Every row requires stable registry, improvement-loop, and function identifiers; a provisional Human-Bottleneck label; registry status; addition date; provenance locator; and an optional delimiter-separated list of empirical-system identifiers. Multiple empirical systems may link to one registry unit.

Permitted draft statuses are `candidate`, `under_review`, `eligible`, `ineligible`, and `withdrawn`. Eligibility criteria remain unresolved and must be versioned before any status beyond `candidate` is used.

A Wave must record both the registry snapshot used during selection and the separately frozen panel snapshot. Both references must resolve to immutable artifacts with verified SHA-256 digests. A locked or official Wave also preserves this specification and the registry-unit schema inside its own immutable package so later registry versions cannot alter historical validation.
