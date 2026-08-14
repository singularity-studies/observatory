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

The goal is coverage, not a metaphysical taxonomy. No domain, source frame,
extraction, candidate, review, authority, or lock is created by this draft.

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
automation. This scaffold does not settle the substantive boundary.

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
unresolved yields `unresolved`.

## Overlap and relations

Domains need not be mutually exclusive. Versioned relations may record
`overlaps_with`, `contains`, `contained_by`, `depends_on`,
`cross_cutting_with`, or a substantively duplicate relation requiring explicit
resolution. Every unordered candidate pair must receive exactly one
overlap/duplication assessment before lock. Documented overlap is permissible;
an undocumented or unresolved duplicate is not.

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
defensible structured classifications. This task chooses or fetches none.

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

## Construction pipeline

```text
Universe Boundary
-> Source-Frame Registration
-> Raw Source-Entry Extraction
-> Normalization Ledger
-> Domain Candidates
-> Domain Eligibility
-> Overlap / Duplication Review
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

The complete pre-approval state, including every extraction ledger, is an
immutable proposal bound by path and SHA-256. Scientific review must explicitly
approve that exact proposal.
Governance must explicitly authorize the same proposal and exact approving
review. Proposal, review, and governance IDs match their filename stems and use
canonical record directories. The final manifest references this non-circular
chain and creates no authority by itself.

## Unresolved scientific decisions

Actual boundary content, source frames, domain names, domain count, weights,
panel quotas, final Frozen Panel size, improvement-loop stage taxonomy, and
final Singularity measurement dimensions remain unresolved.
