# Normalization Materialization Protocol

- Instrument version: `v0.1`
- Status: `PROSPECTIVELY FIXED FOR MATERIALIZATION; NOT SCIENTIFICALLY APPROVED`
- Effective Wave: none
- Stable candidate ID assignment permitted: `false`

## Purpose

This protocol fixes the provenance architecture that must be used before any
Domain candidate is materialized. It does not create a Domain candidate,
assign a stable candidate ID, establish or lock a Domain Universe, select a
Frozen Panel, or authorize Wave 0.

The governing integrity rule is:

> Historical scientific inputs that have been hash-bound by later stages must
> never be rewritten in place.

This protocol clarifies implementation and provenance only. It does not amend
the prospectively fixed scientific interpretation, equivalence, or
normalization-decision rules in Normalization Decision Codebook v0.1.

## Immutable historical chain

The following artifacts are historical scientific inputs and remain
byte-immutable once a later stage binds their SHA-256:

1. the four registered source-frame records bound by the Task 104 extraction
   records;
2. the four Task 104 extraction records bound by Pass 1;
3. the four Pass 1 records bound by Pass 2A and Pass 2B;
4. the merged Pass 2A record; and
5. the merged Pass 2B record.

The `normalization_disposition` and `target_domain_candidate_ids` fields in the
Task 104 extractions are the historical initialization state captured before
normalization began. Once Pass 1 bound those extraction bytes, these fields
ceased to be mutable current-state fields. Their retained values must not be
rewritten to portray a later decision.

Likewise, `normalization_status` and `normalization_note` in the already
hash-bound source-frame registration records are historical snapshot metadata,
not a live mutable status channel.

## Versioned normalization-disposition overlay

Later authoritative normalization decisions must be recorded in a separate,
versioned normalization-disposition overlay conforming to
`schemas/domain-normalization-disposition-overlay.schema.json`. Future overlay
instances belong under `domain-universe/normalization/dispositions/`; Task
105D0 creates no instance.

Every overlay binds exact path and SHA-256 references to:

- Normalization Decision Codebook v0.1;
- boundary `du-boundary-v0.1`;
- all four immutable Task 104 extraction records;
- all four immutable Pass 1 records;
- the merged Pass 2A record; and
- the merged Pass 2B record.

Each entry identifies the immutable extraction and source entry, its applicable
normalization group when one exists, the later authoritative disposition,
candidate targets if applicable, rationale, and uncertainty. The allowed
dispositions are `candidate_created`, `merged_into_candidate`,
`excluded_out_of_scope`, and `unresolved`. `excluded_duplicate` remains
disabled under Normalization Decision Codebook v0.1.

`candidate_created` and `merged_into_candidate` require exactly one target
candidate ID. `excluded_out_of_scope` and `unresolved` require no target ID.
An overlay may be `partial` while governed work remains incomplete. A
`complete` overlay must cover all 330 source entries exactly once and contain
zero unresolved entries before any Domain Universe lock can be considered.

## Candidate provenance and reciprocity

Original source provenance always identifies the exact immutable Task 104
extraction artifact plus `source_entry_id`. Every future Domain candidate also
binds the exact normalization-disposition overlay record that authoritatively
maps that source entry to the candidate.

Candidate-to-source reciprocity is evaluated through the overlay, not by
changing Task 104 bytes. For every candidate provenance entry, the bound
overlay must contain the same extraction and source-entry identity with a
`candidate_created` or `merged_into_candidate` disposition targeting that
candidate. Every overlay candidate target must reciprocally resolve to a
candidate containing the same immutable extraction and source-entry
provenance.

A locked Domain Universe proposal therefore requires both:

- immutable source provenance through the exact source-frame and Task 104
  extraction hash chain; and
- one complete, hash-bound normalization-disposition overlay with exact
  candidate reciprocity and no unresolved entry.

Automated validation is necessary but does not supply scientific review,
governance authority, or substantive approval.

## Stable candidate ID safety gate

`candidate_materialization_permitted=true` in Pass 2B closes only the two
deferred equivalence questions. It does not by itself authorize stable
sequential candidate-ID assignment while source entries remain unresolved.

The current state contains 322 resolved Pass 1 passes and eight unresolved IPC
residual entries. Therefore:

`stable_candidate_id_assignment_permitted = false`

This value remains false until every one of the 330 source entries has a
governed final normalization path sufficient to freeze the complete
candidate-cluster universe. Task 105D0 assigns no stable candidate ID and
creates no candidate record.

## Change control

This protocol is versioned. A later change must create an explicit successor
version and construction-history record; it must not silently rewrite the
meaning of v0.1 or any already-bound historical artifact.
