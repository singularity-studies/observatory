# Schemas

- Schema bundle version: `0.5.0-draft`
- Status: `DRAFT`

The schema bundle also contains eleven contracts for prospectively constructing,
reviewing, and locking a Domain Universe. These cover the boundary, source
frames, immutable source-entry extraction, the versioned normalization-
disposition overlay, domain candidates, deterministic eligibility, relations,
proposal, scientific review, governance decision, and final manifest. The existing
registry, panel-selection, evidence, observation, and Wave contracts remain
separate. `instruments.json` inventories current instruments, and every schema
declares `x-instrument-version`.

Files under `schemas/templates/` are intentionally incomplete, schema-invalid
placeholders. They contain no domain, source frame, extraction, candidate,
eligibility, reviewer, authority, panel, or Wave record and must never be
treated as data or approval. A future record enters validation only under its
applicable `domain-universe/` or `selection/` path and after passing its
versioned schema and cross-record integrity checks.

`domain-normalization-disposition-overlay.schema.json` is the immutable v0.1
prospective contract; there is no overlay instance. It binds the historical
normalization input chain and separates later authoritative dispositions from
immutable Task 104 bytes.

`domain-normalization-completion.schema.json` validates the single Task 105D4
completion manifest. `domain-normalization-disposition-overlay-v0.2.schema.json`
is its post-closure prospective successor and can represent the exact D3
`excluded_non_materializable` state. D4 creates no v0.2 overlay instance. The
v0.2 schema is intentionally not connected to the locked Domain Universe path;
Task 106 must instantiate and connect it separately. The amended Domain
candidate contract continues to require an exact overlay-record reference in
addition to immutable extraction-entry provenance.

These schemas validate structure and fail-closed release prerequisites. They do not establish the scientific validity of a construct or coding decision.

Before lock, a Wave copies every required schema into its own immutable directory and records the copied bytes and version in `schema_locks`. This includes the seven selection, proposal, review, and governance schemas needed to validate the Frozen Panel's locked selection manifest. Historical validation uses those copies, including the copied Wave-manifest schema, even after the top-level bundle advances. A schema change after Wave 0 requires a new version and explicit effective-Wave boundary.

Domain Universe records use their own exact-byte proposal-review-governance
chain. How a future locked Domain Universe is incorporated into a Wave package
remains unresolved and is not silently inferred by this scaffold.
