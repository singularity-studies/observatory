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
categories are not Domains. Pass 1 interpretation, Pass 2A conservative
equivalence grouping, and Pass 2B adjudication of the two deferred pairs are
complete pending scientific review. Every extraction normalization disposition
remains unresolved, and none of these stages creates a Domain, candidate,
eligibility decision, proposal, review, authority, or lock.

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
continuity rule, overlap notes, provenance references, the exact
normalization-disposition overlay record, and instrument version. Products,
companies, models, occupations, and deployments are not Domain units.

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
The `normalization_status` and `normalization_note` values in the four
already-bound registrations are historical snapshot metadata, not a mutable
current-state channel.
Potential frame families include scientific/research, economic/activity,
engineering/technology, public-sector or institutional-function, and other
defensible structured classifications. The registered frames are OECD FORD
(Frascati Manual 2015), UN ISIC Revision 5, WIPO IPC 2026.01, and UN COFOG
1999. Their prospectively specified second levels have been exhaustively
extracted. Pass 1 interpretation, Pass 2A equivalence grouping, and Pass 2B
adjudication of the two deferred pairs are complete pending scientific review;
candidate generation has not begun.

Machine validation cannot substantively prove intellectual independence. It
can require reviewable provenance and block obvious duplication or relabeling;
scientific review remains responsible for assessing the stated independence
basis.

## Extraction and normalization ledger

Every source frame in a locked proposal has exactly one complete, versioned
extraction record under `domain-universe/extractions/`. The record is bound to
the exact source-frame path and SHA-256 and states the extraction scope and
prospective traversal or selection rule. It may use stable identifiers and
short descriptors; no copyrighted source document must be copied into this
repository.

The Task 104 `normalization_disposition` and `target_domain_candidate_ids`
fields are historical initialization state. Pass 1 subsequently bound the
exact extraction bytes, so those fields are not mutable current-state fields.
Later authoritative dispositions live in a separate versioned overlay under
the architecture fixed by
`domain-universe/NORMALIZATION_MATERIALIZATION_PROTOCOL.md`. The overlay binds
the exact codebook, boundary, four Task 104 extractions, four Pass 1 records,
Pass 2A, and Pass 2B. `candidate_created` and `merged_into_candidate` require
one target; `excluded_out_of_scope` and `unresolved` require none;
`excluded_duplicate` remains disabled under Codebook v0.1.

Source-entry IDs remain unique within a frame, and unresolved overlay entries
fail closed. Every candidate provenance reference identifies an exact
immutable Task 104 extraction and concrete entry ID, while the candidate also
binds the authoritative overlay record. Candidate-to-entry and
entry-to-candidate reciprocity is checked through that overlay, never by
rewriting the extraction. This architecture prevents a free-text reference
from concealing silent cherry-picking or omitted normalization decisions. At
least two structurally independent source lineages must contribute non-empty
extracted-entry sets.

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
the two-pass procedure. It is not scientifically approved. Normalization had
not begun at the point of fixation, and all 330 entries were untouched and
`unresolved`. Those Task 104 dispositions remain unchanged after Pass 1, and
the Domain candidate count remains zero. Final Domain eligibility remains a
separate governed stage.

Task 105B Pass 1 independent interpretation is complete pending scientific
review. Exactly 330 separate interpretations now exist under
`domain-universe/normalization/pass1/`, each bound to the fixed codebook,
boundary, and its immutable Task 104 extraction. Pass 1 used no cross-entry
equivalence comparison and created no cluster or candidate. The Task 104
dispositions remain `unresolved`, their candidate targets remain empty, and
Pass 2A high-precision equivalence grouping is now complete pending scientific
review. All 322 passed interpretations appear exactly once in 322 conservative
singleton groups; the eight unresolved IPC residual classes remain outside
grouping. No pair was merged because the permitted Pass 1 evidence did not
affirm all five coextensiveness conditions. This is not evidence that the
groups are disjoint, non-overlapping, independent, finally non-duplicate, or
eligible. Two same-wording cross-frame comparisons remained explicit deferred
questions at Pass 2A. Pass 2B independently constructed each member's
official-source envelope and closed both as
`not_coextensive_for_normalization`: FORD classifies R&D subject-matter fields,
whereas the corresponding ISIC divisions classify construction or education
economic activity with materially different inclusion and exclusion envelopes.
The decision is normalization-specific and does not establish disjointness, no
overlap, final non-duplication, Domain separation, or eligibility. The Pass 2A
singleton partition needs no revision, so later candidate materialization is
structurally permitted but has not begun. No candidate ID or candidate record
exists, extraction dispositions remain untouched, and final Domain eligibility
has not begun. At that historical stage, Pass 1, Pass 2A, and Pass 2B did not
complete normalization.

Pass 2B's `candidate_materialization_permitted=true` closed only its two
deferred equivalence questions. It did not by itself authorize stable
sequential candidate-ID assignment while eight IPC residual entries remained
unresolved. The historical gate therefore remained false until the later D3
successor decisions and D4 completion record provided all 330 entries with a
governed final normalization path. No overlay instance, candidate ID, or
candidate record was created at Pass 2B.

Task 105D1 is an immutable successor clarification of the eight historical
Pass 1 unresolved IPC residual judgments. Official WIPO IPC 2026.01 scheme and
Guide material establishes the section-relative residual mechanism but does
not, for any of A99 through H99, establish a positive coherent Domain coverage
locus. All eight therefore remain `unresolved`; residual status alone neither
passed nor excluded an entry. The original Pass 1, Pass 2A, and Pass 2B bytes
remain unchanged. No successor grouping, overlay, candidate materialization,
stable ID assignment, eligibility decision, scientific approval, or lock
occurred, and `stable_candidate_id_assignment_permitted = false` remains in
force.

Task 105D2 prospectively defines a successor normalization-closure rule after
Task 105D1 exposed a state-space gap in Codebook v0.1. The versioned
`NORMALIZATION_CLOSURE_AMENDMENT.md` introduces only
`excluded_non_materializable`: a source entry may receive that disposition in
a later, separate record only when it is semantically sufficient, has no
coherent substantive locus at the registered extraction granularity, cannot
support topic-preserving materialization, and is not established as
incompatible with the research universe. This rule was not pre-registered
before D1 and does not reclassify A99-H99 or any other entry. Non-materializable
at one registered granularity is neither out-of-scope in the underlying world
nor a final Domain eligibility decision. The current materialization
architecture does not yet consume this successor instrument. Closure decision
records, overlays, candidates, and stable candidate IDs remained zero during
D2, and the stable-ID gate remained false.

Task 105D3 is the first application of the merged D2 closure amendment. It
uses only the frozen D1 predecessor evidence and creates exactly one successor
record for A99-H99. Each entry was assessed independently. In all eight cases,
D1 was semantically sufficient to distinguish the negative residual place
from the absence of a positive candidate locus; the inherited coherent-locus
judgment remained false; one candidate could not be materialized without an
unsupported narrowing, subset selection, false unity, or section-title
substitution; and no strict research-universe incompatibility was established.
The fixed rule therefore produced eight `excluded_non_materializable` and zero
`unresolved` decisions. This was the application result, not a target
distribution. D1 and D2 remain byte-unchanged, and no new evidence,
normalization group, overlay, candidate, or stable candidate ID was introduced.
Although the summary-level closure and gate-reassessment questions closed,
`stable_candidate_id_assignment_permitted = false` remained in force during
D3 until a separate successor materialization architecture was fixed.

Task 105D4 closes Task 105 at the normalization boundary without making a new
scientific classification. The immutable Pass 2A groups and D3 terminal
decisions form an exact, disjoint partition of all 330 source entries: 322
candidate-bearing groups plus eight terminal `excluded_non_materializable`
entries, with zero effective unresolved entries. Each exact Pass 2A
`group_locus_statement` is administratively designated as the canonical label
for its future group; no label is rewritten or synthesized. Unicode
`casefold()` plus the existing deterministic anchor freezes future stable-ID
ordering by digest without assigning an ID.

The versioned v0.2 successor materialization protocol and overlay schema are
fixed before use. `stable_candidate_id_assignment_permitted = true` now means
only that Task 106 may assign IDs from this frozen shape and order. Task 106
has not started: overlay instances, Domain candidates, and assigned stable IDs
remain zero. `scripts/validate.py` deliberately continues to implement the
historical v0.1 lock path until Task 106 creates and connects a v0.2 overlay.

## Construction pipeline

```text
Universe Boundary
-> Source-Frame Registration
-> Raw Source-Entry Extraction
-> Normalization Ledger
-> Successor Normalization Closure (separate versioned application, if needed)
-> Normalization Completion and Successor Contract
-> Normalization Disposition Overlay
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
lineages and reviewable independence bases, exactly one immutable complete
extraction ledger per frame, at least two lineage-distinct non-empty
extractions, one complete hash-bound normalization-disposition overlay covering
all source entries with no unresolved entry, reciprocal overlay-based
entry-level candidate provenance, a non-empty candidate universe,
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

Domain candidate specifications, final Domain eligibility outcomes, domain
count, weights, panel quotas, final Frozen Panel size, improvement-loop stage taxonomy, final
Singularity measurement dimensions, scientific approval of the normalization
codebook, and final Domain Universe governance authority remain unresolved. No
Domain Universe is established or locked, the Frozen Panel remains unselected,
and Wave 0 remains unauthorized.
