# Singularity Observatory

Open research infrastructure for **Observational Singularity Studies** (シンギュラリティ観測学).

## Scientific position

- Umbrella field: **Singularity Studies**
- Empirical field: **Empirical Singularity Studies**
- This repository: **Observational Singularity Studies**
- Core perspective: technology and sociotechnical systems
- Core instrument: **Singularity Observatory**
- Core method: cross-domain longitudinal observation
- Core question:

  > Where, when, and how does human criticality disappear from civilization's improvement loops?

The repository supplies research instruments and provenance controls. It does not currently contain empirical observations, cases, scores, findings, or scientific claims.

## Current status

The scaffold is **pre-Wave 0**. Every scientific instrument is a draft. No official Wave is authorized until the protocol, frozen panel, schema bundle, observation schedule, and governance record have each been versioned and locked.

## Repository map

- [`PROTOCOL.md`](PROTOCOL.md): observation design and Wave lifecycle
- [`CODEBOOK.md`](CODEBOOK.md): state and event representations
- [`PANEL.md`](PANEL.md): Frozen Panel definition and freeze procedure
- [`registry/`](registry/): mutable Live Registry, distinct from the Frozen Panel
- [`evidence/`](evidence/): source-traceable evidence records
- [`data/waves/`](data/waves/): append-only Wave packages after lock
- [`schemas/`](schemas/): versioned machine-readable contracts
- [`scripts/validate.py`](scripts/validate.py): fail-closed structural validation
- [`GOVERNANCE.md`](GOVERNANCE.md): authority, locking, and change control

## Validate

The validator uses only the Python standard library.

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
```

For a pull request that may touch existing Wave data, compare against the base branch:

```bash
python scripts/validate.py --base-ref origin/main
```

## Integrity rules

Unknown remains unknown. Missing evidence is not evidence of absence. Transition, reversal, and human re-entry are first-class representable events. Locked Wave data is append-only, and protocol changes after Wave 0 require a new instrument version rather than an in-place rewrite.

See [`LICENSING.md`](LICENSING.md) before reusing content. No project-wide license has yet been selected.
