# Waves

No Wave exists and Wave 0 is not authorized.

Each future Wave uses its own directory with a `manifest.json`. The manifest schema permits `draft`, `locked`, and `official` states. An official Wave fails validation unless protocol, panel, schema, schedule, and governance locks are complete and well formed.

Once a Wave is locked, its existing files are immutable. Corrections are append-only amendments or later-Wave records. Run `python scripts/validate.py --base-ref origin/main` in pull requests to reject modification or deletion inside Waves that were locked on the base branch.
