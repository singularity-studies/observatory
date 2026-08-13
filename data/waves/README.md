# Waves

No Wave exists and Wave 0 is not authorized.

Each future Wave uses its own directory with a `manifest.json`. The manifest schema permits `draft`, `locked`, and `official` states. An official Wave fails validation unless protocol, panel, schema, schedule, and governance locks are complete and well formed.

Once a Wave is locked, the complete directory is immutable. Additions, modifications, renames, and deletions are all prohibited. Corrections belong in a separately versioned artifact under `data/amendments/` or in a later Wave. Run `python scripts/validate.py --base-ref origin/main` in pull requests to reject any change inside Waves that were locked on the base branch.
