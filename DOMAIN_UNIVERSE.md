# Domain Universe Construction Protocol

- Instrument: Domain Universe Construction Protocol
- Instrument version: `0.5.0-draft`
- Status: `DRAFT`
- Effective Wave: none

## Purpose and scientific position

> A domain is a relatively stable locus of recurrent improvement activity,
> defined for coverage and sampling rather than as an exclusive ontological
> category.

A Domain is a coverage stratum for constructing an auditable sampling frame.
It is not a claim that civilization is naturally, exhaustively, or exclusively
divided into those categories. The protocol asks:

> What parts of civilization's recurrent improvement activity could our Frozen
> Panel systematically miss?

The goal is coverage, not a metaphysical taxonomy. Construction has begun with
one prospectively fixed boundary, four registered source frames, and exhaustive
second-level extraction of 330 official source categories. These source
categories are not Domains. Normalization has not begun, every normalization
disposition remains unresolved, and no Domain, candidate, eligibility decision,
proposal, review, authority, or lock has been created.

## Universe boundary

Before candidate generation, a versioned boundary specification must be fixed
prospectively. It must explain how the research universe treats:

- recurrent improvement activity;
- processes capable of changing knowledge, designs, policies, systems,
  capabilities, practices, or infrastructures used in later cycles; and
- sociotechnical activity in which human criticality can meaningfully be
  investigated.

It must also distinguish this research universe from all human activity, all
economic sectors, all AI applications, all occupations, all tasks, and generic
automation. Boundary `du-boundary-v0.1` is now fixed prospectively for Domain
candidate generation. Fixing it does not establish or lock a Domain Universe.

## Domain unit and eligibility

A future candidate domain records a stable identifier, canonical label, scope,
inclusion and exclusion boundaries, recurrent-improvement rationale,
continuity rule, overlap notes, provenance references, and instrument version.
Products, companies, models, occupations, and deployments are not Domain units.

Eligibility v1 is conjunctive and has no exception mechanism:

1. **Improvement relevance:** recurrent improvement activity relevant to the
   Observatory is present.
2. **Coverage usefulness:** a distinct stratum reduces a meaningful sampling
   blind spot.
3. **Boundary expressibility:** inclusion and exclusion boundaries are explicit.
4. **Longitudinal semantic stability:** meaning can persist across changes in
   firms, products, technologies, and terminology.
5. **Non-triviality:** the unit is not merely one product, company, model,
   occupation, or deployment.
6. **Non-duplication:** it is not substantively identical to another domain
   under the stated boundaries.

All passed yields `eligible`; any failed yields `ineligible`; otherwise any
unresolved yields `unresolved`. Overlap/duplication adjudication occurs before
the final eligibility decision so that the `non_duplication` criterion records
the adjudicated result rather than an earlier assumption.

## Overlap and relations

Domains need not be mutually exclusive. Versioned relations may record
`overlaps_with`, `contains`, `contained_by`, `depends_on`,
`cross_cutting_with`, or a substantively duplicate relation requiring explicit
resolution. Every unordered candidate pair must receive exactly one
overlap/duplication assessment before lock. Documented overlap is permissible;
an undocumented or unresolved duplicate is not. No relation with
`resolution_status: unresolved` may enter a locked Domain Universe, regardless
of relation type. `overlaps_with`, `contains`, `contained_by`,
`cross_cutting_with`, and `depends_on` must be `documented` or `resolved`;
`substantively_duplicates` must be `resolved`.

For v1, `duplicate_resolved` means the final pair remains substantively
duplicate and the duplicate has been removed from the eligible universe. At
least one pair member must therefore record `non_duplication: failed` and the
deterministic status `ineligible`; that candidate receives no eligible-domain
disposition. The retained member may remain eligible and included. If revised
boundaries make the candidates non-duplicate, the final assessment is
`distinct` or `overlap_documented`, not `duplicate_resolved`.

## Multi-frame construction

No single person or source classification may define the Domain Universe.
Future candidate generation must use at least two independently identified
source frames from distinct source lineages. Each frame records its identity,
classification family, version/date, auditable source reference,
`source_lineage_id`, independence group, an explicit `independence_basis`, and
registration date. A lineage identifies the underlying classification origin,
not a file or edition. Exact duplicate identity/version/URI registrations do
not count twice, even when their frame IDs or independence-group labels differ.
Potential frame families include scientific/research, economic/activity,
engineering/technology, public-sector or institutional-function, and other
defensible structured classifications. The registered frames are OECD FORD
(Frascati Manual 2015), UN ISIC Revision 5, WIPO IPC 2026.01, and UN COFOG
1999. Their prospectively specified second levels have been exhaustively
extracted; normalization and candidate generation have not begun.

Machine validation cannot substantively prove intellectual independence. It
can require reviewable provenance and block obvious duplication or relabeling;
scientific review remains responsible for assessing the stated independence
basis.

## Extraction and normalization ledger

Every source frame in a locked proposal has exactly one complete, versioned
extraction record under `domain-universe/extractions/`. The record is bound to
the exact source-frame path and SHA-256, states the extraction scope and
prospective traversal or selection rule, and records every traversed source
entry's disposition. It may use stable identifiers and short descriptors; no
copyrighted source document must be copied into this repository.

Entry dispositions are `candidate_created`, `merged_into_candidate`,
`excluded_out_of_scope`, `excluded_duplicate`, or `unresolved`. Source-entry
IDs are unique within a frame, and unresolved entries fail closed. Every
candidate provenance reference identifies an exact extraction artifact and
concrete entry ID. Candidate-to-entry and entry-to-candidate references must
agree. This ledger prevents a free-text reference from concealing silent
cherry-picking or omitted normalization decisions. At least two structurally
independent source lineages must contribute non-empty extracted-entry sets.

The Task 104 ledgers contain 42 FORD second-level fields, 87 ISIC Rev.5
Divisions, 132 IPC 2026.01 Classes, and 69 COFOG 1999 Groups: 330 source
categories in total. First-level categories are retained only as parent
context. Every entry remains `unresolved` with no target candidate. Extraction
completeness does not establish scope, duplication, eligibility, a Domain, or a
Domain Universe.

Normalization Codebook v0.1 is now prospectively fixed in
`domain-universe/NORMALIZATION_CODEBOOK.md`, before any normalization
disposition changes. The codebook defines topic-preserving interpretation,
high-bar equivalence, partial-overlap preservation, deterministic anchors, and
the two-pass procedure. It is not scientifically approved, normalization has
not begun, all 330 entries remain untouched and `unresolved`, and the Domain
candidate count remains zero. Final Domain eligibility remains a separate
governed stage.

## Construction pipeline

```text
Universe Boundary
-> Source-Frame Registration
-> Raw Source-Entry Extraction
-> Normalization Ledger
-> Domain Candidates
-> Overlap / Duplication Adjudication
-> Final Domain Eligibility
-> Coverage Audit
-> Domain Universe Proposal
-> Scientific Review
-> Governance Lock
```

## Coverage audit

The versioned audit must document, without a numerical coverage score:

- represented recurrent improvement activity;
- potentially missing recurrent improvement activity;
- heavily overlapping domains;
- domains represented through only one source frame;
- unstable or overly technology-specific domains; and
- possible privilege given to currently fashionable AI areas.

Coverage dimensions and weighting remain unresolved.

## Anti-bias rules

> Do not construct the Domain Universe around where AI appears most advanced.

> Domain inclusion must not depend on an expectation that human criticality
> will weaken.

A domain remains eligible even if humans appear likely to remain critical
indefinitely. Current AI capability and expected Singularity proximity are not
domain-selection variables.

## Fail-closed lock

A lock requires a fixed boundary, at least two source frames with distinct
lineages and reviewable independence bases, exactly one complete extraction
ledger per frame, at least two lineage-distinct non-empty extractions,
reciprocal entry-level candidate provenance, a non-empty candidate universe,
exactly one deterministic eligibility decision per candidate, semantically
consistent and exhaustive relation/pair accounting, complete pairwise
overlap/duplication review, complete coverage audit, explicit disposition of
every eligible candidate, a non-empty included set containing only eligible
candidates, and rationale plus uncertainty for every excluded eligible
candidate.

Every relation in the proposal must be cited by exactly one assessment for its
endpoint pair. `overlap_documented` requires an overlap, containment, or
cross-cutting relation; `depends_on` alone does not establish overlap.
`duplicate_resolved` requires a resolved `substantively_duplicates` relation.
Orphan, repeated, contradictory, endpoint-mismatched, and unresolved relation
records fail closed.

A `duplicate_resolved` pair also requires at least one candidate to fail the
conjunctive `non_duplication` criterion and become ineligible. Two substantively
duplicate candidates cannot both survive as eligible or included domains.

The complete pre-approval state, including every extraction ledger, is an
immutable proposal bound by path and SHA-256. Scientific review must explicitly
approve that exact proposal.
Governance must explicitly authorize the same proposal and exact approving
review. Proposal, review, and governance IDs match their filename stems and use
canonical record directories. The final manifest references this non-circular
chain and creates no authority by itself.

## Unresolved scientific decisions

Domain names, domain count, source-entry normalization outcomes, weights, panel
quotas, final Frozen Panel size, improvement-loop stage taxonomy, final
Singularity measurement dimensions, scientific approval of the normalization
codebook, and final Domain Universe governance authority remain unresolved. No
Domain Universe is established or locked, the Frozen Panel remains unselected,
and Wave 0 remains unauthorized.
