# Schemas

- Schema bundle version: `0.5.0-draft`
- Status: `DRAFT`

The schema bundle also contains nine contracts for prospectively constructing,
reviewing, and locking a Domain Universe. These cover the boundary, source
frames, domain candidates, deterministic eligibility, relations, proposal,
scientific review, governance decision, and final manifest. The existing
registry, panel-selection, evidence, observation, and Wave contracts remain
separate. `instruments.json` inventories current instruments, and every schema
declares `x-instrument-version`.

Files under `schemas/templates/` are intentionally incomplete, schema-invalid
placeholders. They contain no domain, source frame, candidate, eligibility,
reviewer, authority, panel, or Wave record and must never be treated as data or
approval. A future record enters validation only under its applicable
`domain-universe/` or `selection/` path and after passing its versioned schema
and cross-record integrity checks.

These schemas validate structure and fail-closed release prerequisites. They do not establish the scientific validity of a construct or coding decision.

Before lock, a Wave copies every required schema into its own immutable directory and records the copied bytes and version in `schema_locks`. This includes the seven selection, proposal, review, and governance schemas needed to validate the Frozen Panel's locked selection manifest. Historical validation uses those copies, including the copied Wave-manifest schema, even after the top-level bundle advances. A schema change after Wave 0 requires a new version and explicit effective-Wave boundary.

Domain Universe records use their own exact-byte proposal-review-governance
chain. How a future locked Domain Universe is incorporated into a Wave package
remains unresolved and is not silently inferred by this scaffold.
