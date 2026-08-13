# Schemas

- Schema bundle version: `0.3.0-draft`
- Status: `DRAFT`

The schema bundle contains contracts for registry units, Frozen Panel snapshots, evidence records, resolved or explicit unresolved observations, and self-contained Wave manifests. `instruments.json` is the machine-readable inventory of current scientific instruments. Every schema declares `x-instrument-version`.

These schemas validate structure and fail-closed release prerequisites. They do not establish the scientific validity of a construct or coding decision.

Before lock, a Wave copies every required schema into its own immutable directory and records the copied bytes and version in `schema_locks`. Historical validation uses those copies, including the copied Wave-manifest schema, even after the top-level bundle advances. A schema change after Wave 0 requires a new version and explicit effective-Wave boundary.
