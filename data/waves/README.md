# Waves

No Wave exists and Wave 0 is not authorized.

Each future Wave uses its own directory with a `manifest.json`. A locked or official directory is a self-contained package: it includes hashed snapshots of the protocol, codebook, panel specification, schedule, governance and registry instruments, plus the registry-unit, panel-snapshot, evidence, observation, and Wave-manifest schemas used by that Wave. Historical validation uses these package-local bytes rather than current top-level instruments.

Locked and official Waves require a non-empty Frozen Panel and explicit observation coverage for every panel unit. An unresolved unit is represented by a schema-valid explicit unknown observation; silent omission fails. Longitudinal prior-observation references are checked across all locked and official Waves.

Once a Wave is locked, the complete directory is immutable. Additions, modifications, renames, and deletions are all prohibited. Corrections belong in a separately versioned artifact under `data/amendments/` or in a later Wave. Run `python scripts/validate.py --base-ref origin/main` in pull requests to reject any change inside Waves that were locked on the base branch.
