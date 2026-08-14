# Schemas

- Schema bundle version: `0.4.0-draft`
- Status: `DRAFT`

The schema bundle contains contracts for registry units, candidate unit specifications, eligibility decisions, panel lineage, panel-selection manifests, Frozen Panel snapshots, evidence records, resolved or explicit unresolved observations, and self-contained Wave manifests. `instruments.json` is the machine-readable inventory of current scientific instruments. Every schema declares `x-instrument-version`.

Files under `schemas/templates/` are intentionally incomplete, schema-invalid placeholders. They contain no candidate, eligibility, reviewer, authority, panel, or Wave record and must never be treated as scientific data or approval. A future record becomes eligible for repository validation only after it is placed under the applicable `selection/` path and independently passes its versioned schema and cross-record integrity checks.

These schemas validate structure and fail-closed release prerequisites. They do not establish the scientific validity of a construct or coding decision.

Before lock, a Wave copies every required schema into its own immutable directory and records the copied bytes and version in `schema_locks`. This includes the four selection schemas needed to validate the Frozen Panel's locked selection manifest. Historical validation uses those copies, including the copied Wave-manifest schema, even after the top-level bundle advances. A schema change after Wave 0 requires a new version and explicit effective-Wave boundary.
