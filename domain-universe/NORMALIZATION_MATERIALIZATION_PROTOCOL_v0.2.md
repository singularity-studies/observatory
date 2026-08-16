# Normalization Materialization Protocol v0.2

- Version: `v0.2`
- Instrument version: `0.5.0-draft`
- Status: `POST-CLOSURE SUCCESSOR MATERIALIZATION PROTOCOL; FIXED BEFORE MATERIALIZATION; NOT SCIENTIFICALLY APPROVED`
- Effective Wave: `none`
- Bound completion record: `domain-universe/normalization/completion/normalization-completion-v0.1.json`

## Purpose and succession

This protocol fixes the post-closure contract that a future Task 106 must use
to materialize the normalization state. It creates no normalization overlay,
Domain candidate, stable candidate ID, Domain Universe lock, Frozen Panel, or
Wave authorization.

`NORMALIZATION_MATERIALIZATION_PROTOCOL.md` v0.1 remains immutable historical
architecture. The Task 105D3 closure application introduced eight terminal
`excluded_non_materializable` decisions through the already-fixed Task 105D2
rule. This v0.2 successor extends future current-state materialization so that
the terminal successor state can be represented without rewriting Task 104,
Pass 1, Pass 2A, Pass 2B, D1, D2, or D3.

This protocol is bound conceptually to `normalization-completion-v0.1`, which
records the complete and disjoint 322-group plus eight-terminal-entry
partition. That record is administrative closure bookkeeping, not a new
scientific classification or approval.

## Canonical labels and future stable-ID order

Task 105D4 administratively designates the already-fixed Pass 2A
`group_locus_statement` as the canonical label for future candidate
materialization. It makes no new normalization judgment.

For every candidate-bearing group, future ordering uses exactly:

1. `canonical_label.casefold()` over the exact Unicode label string;
2. `deterministic_anchor.source_frame_id`; and
3. `deterministic_anchor.source_entry_id`.

The completion record stores only the digest of that order. It contains no
group-to-`du-cand-*` mapping and assigns no stable identifier.

## Future complete overlay

A future complete v0.2 overlay must contain exactly one entry for each of the
330 source-entry identities and must contain zero `unresolved` dispositions.

For members of the 322 Pass 2A candidate-bearing groups, the only applicable
future dispositions are:

- `candidate_created` for the deterministic group anchor; and
- `merged_into_candidate` for any other member of the same group.

For the exact eight D3 terminal identities, the required future disposition
is:

- `excluded_non_materializable`.

`excluded_duplicate` remains disabled. `excluded_out_of_scope` remains a
structurally representable disposition but is not the result of the immutable
Task 105 chain and cannot replace any of the 322 grouped or eight terminal
identities in a complete overlay.

Candidate-bearing dispositions require exactly one candidate target, a
non-null Pass 2A normalization group ID, and a null successor closure-decision
entry ID. `excluded_non_materializable` requires zero candidate targets, a
null normalization group ID, and the exact non-null D3 closure-decision entry
ID.

## Lock-path boundary

Task 105 ends before candidate materialization. Therefore D4 does not update
the locked Domain Universe overlay consumption in `scripts/validate.py`.
Task 106, which has not started, must instantiate the v0.2 overlay, materialize
candidates, assign stable IDs, and separately connect the v0.2 overlay to the
Domain Universe lock validator.

The absence of v0.2 lock consumption in D4 is an explicit phase boundary, not
permission to use the v0.1 lock path for successor materialization.

## Permission boundary

`STABLE_CANDIDATE_ID_ASSIGNMENT_PERMITTED = true` means only that the complete
candidate-cluster universe, exact inherited labels, and deterministic future
ordering are sufficiently frozen to permit Task 106 to assign IDs. It does not
mean any ID or candidate has been assigned or created.

The current state must remain:

```text
NORMALIZATION_OVERLAY_INSTANCE = 0
DOMAIN_CANDIDATES = 0
ASSIGNED_STABLE_CANDIDATE_IDS = 0
DOMAIN_UNIVERSE_LOCKED = false
FROZEN_PANEL_SELECTED = false
WAVE_0_AUTHORIZED = false
```

## Change control

This protocol was fixed before any v0.2 overlay instance or candidate
materialization. Later changes require an explicit successor version and may
not rewrite v0.1, v0.2, the completion manifest, or any immutable historical
normalization artifact.
