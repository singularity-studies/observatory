# Domain Universe Normalization Decision Codebook

- Version: `v0.1`
- Status: **PROSPECTIVELY FIXED FOR NORMALIZATION; NOT SCIENTIFICALLY APPROVED**
- Effective normalization batch: **none yet**
- Fixed boundary: `du-boundary-v0.1`

This codebook must be fixed before any Task 105 normalization disposition is
changed from unresolved.

Normalization converts source-classification entries into provisional
coverage strata. It does not determine final Domain eligibility.

This instrument defines rules only. It does not normalize an entry, create a
Domain candidate, approve a scientific decision, identify a governance
authority, establish or lock a Domain Universe, select a Frozen Panel, or
authorize Wave 0.

## 1. Central scientific principle

> Normalization is a topic-preserving translation across source-frame lenses,
> not an opportunity to invent a new ontology.

> Semantic equivalence is not partial overlap.

> Source-frame convergence is evidence of coverage convergence only when the
> normalized loci are substantively coextensive.

The four source frames classify different objects: R&D knowledge domains,
economic activities, technological subject matter, and public or government
functions. Normalization may remove a source-frame role from a label, but it
must preserve every substantive distinction.

Conceptually, “research in X,” “economic activity concerning X,” “technology
concerning X,” and “public function concerning X” may expose a neutral
semantic core X. They may map to one provisional candidate only when the
underlying normalized coverage loci are substantively coextensive. Shared
words are insufficient.

## 2. Frame-role stripping

Frame-role stripping may remove only the classification lens imposed by the
source frame. Removable conceptual wrappers include:

- field of research in ...;
- economic activity of ...;
- patent technological subject matter concerning ...; and
- government expenditure or function concerning ....

It must not remove substantive modifiers. Distinctions such as basic versus
clinical, production versus distribution, road versus building, primary
versus tertiary, medical versus industrial, and hardware versus software
remain substantive unless the official classification context demonstrates
otherwise.

A normalization decision must never broaden an entry merely to make it merge
with another source frame.

## 3. Minimal candidate-generation gate

A source entry may contribute to a provisional Domain candidate only when all
three conditions hold:

1. **Substantive locus.** After permissible frame-role stripping, a coherent
   substantive locus remains.
2. **Topic-preserving translatability.** The locus can be expressed as a
   neutral coverage stratum without adding a material topic, activity,
   technology, institution, or purpose unsupported by the source entry.
3. **Boundary compatibility.** The locus can in principle host
   institutionalized or scalable recurrent sociotechnical improvement
   processes under `du-boundary-v0.1`.

This is a permissive normalization gate, not the six-criterion final Domain
eligibility test. Normalization must not decide final coverage usefulness,
final longitudinal semantic stability, final non-triviality, final
non-duplication, or final panel suitability. Those decisions belong to later
governed stages.

## 4. Out-of-scope rule

Use `normalization_disposition = excluded_out_of_scope` only when the source
category is structurally incompatible with the fixed research-universe
boundary and no topic-preserving transformation can yield a qualifying
recurrent-improvement coverage locus. The threshold is high.

Do not exclude an entry merely because:

- most present-day activity is routine;
- AI is uncommon or weak there;
- humans appear indispensable;
- the area is unfashionable or economically small;
- the area appears unlikely to approach Singularity;
- the source label is broad; or
- the category is residual or labelled “other.”

Broadness, residual status, semantic stability, and weak coverage usefulness
may later cause eligibility failure. They are not automatic normalization
exclusions.

## 5. Equivalence and merge rule

Two or more source entries may map to the same provisional Domain candidate
only when their normalized substantive loci are coextensive for Domain
coverage. All of the following are required:

1. the same substantive object or subject area;
2. materially equivalent inclusion envelopes;
3. materially equivalent exclusion envelopes;
4. neither normalized locus contains an important area absent from the other;
   and
5. differences arise primarily from source-frame lens rather than substantive
   scope.

This is a high-bar equivalence test. The same keyword, topical similarity, a
shared parent category, an enabling relationship, dependency, a part-whole or
general-specific relationship, adjacent value-chain stages, materially
different research and application scopes, or only partially intersecting
technology and industry categories is not sufficient for merging.

## 6. Partial overlap

If two entries overlap materially but are not coextensive, do not merge them.
They remain separate provisional candidates if each independently passes the
minimal candidate-generation gate. A later Domain relation record may
represent their relationship.

> Preserve overlap; do not normalize it away.

Normalization must not force civilization into mutually exclusive bins.

## 7. Disposition semantics

The v0.1 meanings are:

### `candidate_created`

The entry belongs to an in-scope equivalence cluster and is the deterministic
administrative anchor used to create that provisional Domain candidate.

### `merged_into_candidate`

The entry is independently in scope but substantively equivalent to the same
normalized coverage locus represented by that candidate. It remains
scientific provenance for the candidate.

### `excluded_out_of_scope`

The entry fails the strict fixed-boundary normalization gate. It creates no
candidate and has no target candidate ID.

### `excluded_duplicate`

**RESERVED / DISABLED IN NORMALIZATION v0.1.** Do not use this disposition for
valid Task 104 source entries. Substantively equivalent valid entries remain
provenance through `candidate_created` plus `merged_into_candidate`.

`excluded_duplicate` is reserved for a future governed correction mechanism
for genuinely duplicate or erroneous extraction artifacts.

### `unresolved`

Permitted evidence is insufficient for a defensible normalization decision.
Uncertainty is a valid scientific outcome. An unresolved entry cannot silently
become a Domain candidate and must have no target candidate ID.

## 8. Deterministic equivalence-cluster anchor

Scientific meaning must not depend on processing order. Each final equivalence
cluster has exactly one `candidate_created` source entry; every other
equivalent source entry receives `merged_into_candidate`.

Choose the anchor mechanically as the lexicographically smallest tuple
`(source_frame_id, source_entry_id)` among all provenance entries in the
equivalence cluster.

> The anchor has no scientific priority, evidentiary priority, or conceptual
> privilege. It is only a deterministic bookkeeping device.

## 9. Candidate ID assignment

Permanent candidate identity must not derive directly from a vendor, source
frame, or source-entry code. Only after all normalization clusters are
substantively finalized:

1. determine one canonical neutral label for every candidate cluster;
2. sort all clusters first by `canonical_label`, case-insensitively, and then
   by the lexicographically smallest provenance tuple as a deterministic
   tie-breaker; and
3. assign stable identifiers in `du-cand-NNNN` form: `du-cand-0001`,
   `du-cand-0002`, and so on.

Candidate IDs are identifiers, not ranks. Their numbers imply no importance.

## 10. Canonical labels

A candidate `canonical_label` must be a neutral noun phrase describing the
normalized substantive locus. It must avoid source-frame-specific wording
where possible, must not mention AI merely because the research program
concerns AI, must not mention Singularity, and must not imply weakening human
criticality, current automation, or current autonomy. It must not be broader
than the evidence supplied by its provenance cluster.

Prefer stable subject-matter labels over temporary product, organization,
technology-generation, or market labels.

## 11. Candidate record content

Any future Task 105 candidate must use the existing
`schemas/domain-candidate.schema.json` contract and populate:

- `canonical_label`: the neutral normalized locus;
- `scope_definition`: a concise source-neutral definition covering all and
  only the substantively equivalent provenance entries;
- `inclusion_boundary`: recurrent-improvement activity within the locus that
  is potentially covered;
- `exclusion_boundary`: adjacent subject matter and routine activity outside
  the coverage stratum;
- `recurrent_improvement_rationale`: why the locus can in principle contain
  recurrent improvement processes under `du-boundary-v0.1`, without asserting
  that such improvement currently occurs or is AI-led;
- `continuity_rule`: identity follows the substantive locus across changes in
  products, organizations, technologies, institutions, and terminology;
- `overlap_notes`: known or suspected partial overlaps retained for later
  adjudication; and
- `provenance_references`: every cluster entry, identified by exact extraction
  path, extraction SHA-256, and `source_entry_id`.

## 12. Allowed normalization evidence

Task 105 normalization may use only:

1. fixed boundary `du-boundary-v0.1`;
2. this prospective codebook;
3. the official source-entry code and title;
4. first-level parent context recorded in the extraction; and
5. official explanatory notes or lower-level descendants from the same
   registered classification, only when needed to clarify scope.

It must not use current AI benchmark performance, model capabilities, company
announcements, AI adoption rates, AGI/ASI/Singularity predictions, expected
economic value, media attention, current human criticality, or beliefs about
which Domains will change fastest.

If official classification material does not resolve an ambiguity, the entry
remains `unresolved`. Current AI developments cannot resolve taxonomy
ambiguity.

## 13. Blindness to expected AI advancement

> Normalization is blind to expected AI advancement, not blind to source
> semantics.

> No normalization disposition may depend on whether humans are expected to
> remain critical, become less critical, or cease to be critical.

Current human criticality is not a normalization variable.

## 14. Two-pass normalization procedure

### Pass 1 — independent entry interpretation

For every one of the 330 entries, interpret its substantive locus, apply
frame-role stripping, and test minimal boundary compatibility. Do not assign
equivalence merely because another frame has a similar label. Pass 1 must be
completed for all entries before cross-entry clustering begins.

### Pass 2 — cross-entry equivalence clustering

Only after Pass 1 is complete, compare normalized loci, form only
high-confidence equivalence clusters, preserve partial overlaps as separate
candidates, determine deterministic anchors, and assign final candidate IDs.

The two-pass procedure reduces anchoring on whichever source frame happens to
be processed first.

## 15. Fail-closed completion rules

A Task 105 normalization batch is incomplete if:

- any entry lacks an explicit disposition;
- `excluded_duplicate` is used;
- a `candidate_created` or `merged_into_candidate` entry lacks a target
  candidate ID;
- an `excluded_out_of_scope` or `unresolved` entry has a target candidate ID;
- more than one `candidate_created` entry exists in an equivalence cluster;
- a merged entry points to a candidate without reciprocal provenance;
- a candidate omits a normalized provenance entry;
- a merge relies only on keyword similarity or partial overlap; or
- a rationale uses AI capability, expected Singularity proximity, or a
  human-criticality forecast.

Draft normalization work may retain explicit `unresolved` decisions. They
must never be silently resolved.

## 16. Prospective fixation and unchanged scientific state

Version v0.1 is fixed before normalization begins but is not scientifically
approved. No normalization batch is effective. All 330 Task 104 entries remain
`unresolved`, all target candidate lists remain empty, all four source-frame
normalization statuses remain `pending`, and Domain candidate count remains
zero.

Final Domain eligibility rules remain separate. Final scientific review and
governance authority remain unresolved.
