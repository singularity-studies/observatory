# Singularity Observatory

Open research infrastructure for **Observational Singularity Studies** (シンギュラリティ観測学).

## Scientific position

- Umbrella field: **Singularity Studies**
- Empirical field: **Empirical Singularity Studies**
- This repository: **Observational Singularity Studies**
- Core perspective: technology and sociotechnical systems
- Core instrument: **Singularity Observatory**
- Core method: cross-domain longitudinal observation
- Primary panel unit: a bounded function or stage in a civilization improvement loop, framed as a potential **Human Bottleneck**
- Core question:

  > How does human criticality change across civilization’s improvement loops, and where—if anywhere—does it cease to be necessary?

The repository supplies research instruments and provenance controls. It does not currently contain empirical observations, cases, scores, findings, or scientific claims.

Technologies, products, organizations, and deployments are not normally the primary panel unit. They are empirical systems that may instantiate or supply evidence about a panel unit, and multiple empirical systems may be linked to the same improvement-loop function.

## Current status

The scaffold is **pre-Wave 0**. Every scientific instrument is a draft. Domain
Universe construction is in progress: prospective boundary `du-boundary-v0.1`
is fixed for candidate generation and four source frames are registered, but
no extraction, normalization, candidate, eligibility decision, proposal,
scientific approval, governance lock, or Domain exists. The Domain Universe is
not established or locked, final governance authority remains unresolved, and
no official Wave is authorized until the protocol, coverage frame, frozen
panel, schema bundle, observation schedule, and governance record have each
been versioned and locked.

## Repository map

- [`PROTOCOL.md`](PROTOCOL.md): observation design and Wave lifecycle
- [`CODEBOOK.md`](CODEBOOK.md): state and event representations
- [`PANEL.md`](PANEL.md): improvement-loop/function-centered Frozen Panel definition
- [`DOMAIN_UNIVERSE.md`](DOMAIN_UNIVERSE.md): auditable coverage-frame construction protocol
- [`domain-universe/`](domain-universe/): prospective boundary and source-frame registrations, with downstream construction records absent
- [`registry/`](registry/): mutable Live Registry, distinct from the Frozen Panel
- [`evidence/`](evidence/): source-traceable evidence records
- [`data/waves/`](data/waves/): immutable Wave packages after lock
- [`data/amendments/`](data/amendments/): separately versioned post-lock corrections
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

Unknown remains unknown. Missing evidence is not evidence of absence. Persistence, transition, reversal, and human re-entry are equally admissible outcomes. Locked Wave packages are byte-immutable and self-contained with their own instrument and schema snapshots; historical validation never substitutes current versions. Every panel unit requires explicit coverage, including an unresolved observation when no determination is supportable. Post-lock corrections live outside the package as versioned amendments.

See [`LICENSING.md`](LICENSING.md) before reusing content. No project-wide license has yet been selected.
