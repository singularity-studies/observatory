# Agent Instructions

These instructions apply to the entire repository.

## Scientific integrity

- Do not invent scientific claims, cases, observations, scores, sources, quotations, or empirical data.
- Do not turn missing evidence into an `absent` code. Use `unknown` unless source-backed evidence supports a stronger value.
- Preserve source identity and observation date for every evidence record.
- Keep the mutable Live Registry separate from every Frozen Panel snapshot.
- Treat a bounded improvement-loop function/stage—not a product or technology—as the primary panel unit. Link empirical systems separately.
- Represent transitions, reversals, and human re-entry without assuming that any has occurred.
- Treat labels and operational definitions as versioned instruments, not settled facts.

## Change control

- Do not add, modify, rename, or delete any file inside a Wave that was already locked on the base branch.
- Add corrections outside the locked Wave under a separately versioned amendment path, or to a later Wave; retain the original bytes.
- After Wave 0, change `PROTOCOL.md`, `CODEBOOK.md`, `PANEL.md`, `GOVERNANCE.md`, or schedule/schema instruments only through an explicit version increment and decision record.
- Never silently replace a locked instrument or hash.

## Fail-closed behavior

- Do not describe a Wave as official unless its manifest passes `scripts/validate.py`.
- An official Wave requires resolvable, content-hashed protocol, panel, schema, schedule, governance, Frozen Panel snapshot, Live Registry snapshot, and scientific-record references.
- Validation uncertainty is a failure, not permission to proceed.

## Required checks

Run before proposing changes:

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
```

When the branch may affect existing Wave data, also run:

```bash
python scripts/validate.py --base-ref origin/main
```

Keep implementations small, dependency-free where practical, and auditable in plain text.
