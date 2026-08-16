# Domain Universe records

Domain Universe construction is in progress. This namespace contains one
prospectively fixed boundary specification, `du-boundary-v0.1`, and exactly
four registered source frames: OECD FORD (Frascati Manual 2015), UN ISIC
Revision 5, WIPO IPC 2026.01, and UN COFOG 1999.

Exhaustive Task 104 second-level extraction is complete: 42 FORD fields, 87
ISIC Rev.5 Divisions, 132 IPC 2026.01 Classes, and 69 COFOG 1999 Groups, for
330 source categories in four extraction ledgers. The entries are source
classification categories, not Domains. Every immutable Task 104
normalization disposition remains historically `unresolved`; later Pass 1,
Pass 2A, Pass 2B, and successor records do not rewrite those fields. Current
effective state is derived through the versioned successor chain, and
candidate generation has not begun.

`NORMALIZATION_CODEBOOK.md` v0.1 is prospectively fixed for normalization but
is not scientifically approved. It fixes the decision rules before any of the
330 entries can change disposition. It was fixed before Pass 1 execution; the
Task 104 entries remain untouched and `unresolved`, and the candidate count
remains zero. Final Domain eligibility rules remain separate, and final
governance authority remains unresolved.

Task 105B has completed Pass 1 independent interpretation for all 330 entries,
pending scientific review. The four records under `normalization/pass1/` bind
the exact codebook, boundary, and Task 104 extractions. No cross-entry
equivalence comparison or clustering occurred during Pass 1. Task 104
dispositions and candidate targets remain untouched, and Domain candidate
count remains zero. Pass 1 completion does not mean normalization completion.

Task 105C Pass 2A high-precision equivalence grouping is complete pending
scientific review. The 322 Pass 1 passes are partitioned exactly once into 322
conservative singleton groups. No pair met all five affirmative
coextensiveness conditions on the permitted evidence; this does not establish
disjointness or non-overlap. The eight unresolved IPC residual classes remain
outside grouping, and two same-wording cross-frame comparisons are deferred.
No candidate ID or candidate record exists, Task 104 dispositions remain
untouched, and final eligibility has not begun.

Task 105C2 Pass 2B deferred-equivalence adjudication is complete pending
scientific review. Official same-classification clarification closed both
Pass 2A deferred pairs as `not_coextensive_for_normalization`: their shared
topic labels do not make the FORD R&D-content envelopes coextensive with the
ISIC economic-activity envelopes. This normalization-specific result does not
establish no overlap, final non-duplication, Domain separation, or eligibility.
The Pass 2A singleton grouping requires no revision, and candidate
materialization is structurally permitted for a later governed task; no
candidate has been created here.

Task 105D1 independently clarified the eight historical Pass 1 unresolved IPC
residual classes using only the official WIPO IPC 2026.01 scheme and 2026
Guide. Each X99Z place has a valid section-relative residual meaning, but that
negative classification envelope does not itself establish a positive
coherent Domain coverage locus. All eight results remain `unresolved`. The
successor record under `normalization/residuals/` does not rewrite Pass 1,
Pass 2A, or Pass 2B and performs no equivalence clustering.

`NORMALIZATION_CLOSURE_AMENDMENT.md` v0.1 is a post-D1, versioned successor
rule fixed before any application. D1 revealed a normalization state that
Codebook v0.1 could not represent; the amendment defines the general
`excluded_non_materializable` disposition without rewriting D1 or applying it
to A99-H99 or any other entry. The disposition is about the registered
source-entry granularity, not whether the underlying subject matter is outside
the research universe. No closure decision record existed during D2, and the
current materialization architecture does not yet consume the successor schema.

Task 105D3 is the first application of that already-merged rule. The exact
record under `normalization/closure/` applies it independently to the eight D1
residual assessments using no new scientific evidence. The resulting
distribution is eight `excluded_non_materializable` and zero `unresolved`;
this is an application outcome, not a target. D1, the D2 amendment, and the D2
schema remain immutable. No normalization group, overlay, Domain candidate, or
stable candidate ID was created. Summary-level reassessment readiness became
true, but the stable-ID gate remained false during D3 pending a separately
versioned successor materialization architecture.

`NORMALIZATION_MATERIALIZATION_PROTOCOL.md` v0.1 now prospectively fixes the
materialization provenance architecture, pending scientific review. Task 104
dispositions and targets, and the bound source-frame status metadata, remain
immutable historical snapshots. Future authoritative disposition state belongs
in a separately versioned overlay under `normalization/dispositions/`, and
future candidates must bind that overlay while retaining exact Task 104
extraction provenance. No overlay instance exists. This v0.1 protocol remains
the immutable historical architecture and does not consume the later D3
successor state.

Task 105D4 records normalization completion under
`normalization/completion/normalization-completion-v0.1.json` and fixes
`NORMALIZATION_MATERIALIZATION_PROTOCOL_v0.2.md` plus its prospective v0.2
overlay schema. The immutable final partition is 322 candidate-bearing Pass 2A
groups plus eight D3 terminal non-candidate entries, exhausting all 330 source
identities with zero effective unresolved entries. Canonical labels are the
exact existing Pass 2A `group_locus_statement` values; no new label or
scientific judgment was introduced. The future ID order is digest-frozen using
Unicode `casefold()` and each fixed deterministic anchor.

The current stable-ID assignment gate is true only as permission for the
not-started Task 106. No overlay, candidate, or `du-cand-*` identifier exists.
The actual Domain lock implementation remains on its historical v0.1
consumption path until Task 106 instantiates and connects the v0.2 overlay.

There is no Domain candidate, eligibility decision, relation, proposal,
scientific review, governance decision, manifest, included or locked Domain,
approval, or lock. The Domain Universe is not established or locked, final
governance authority remains unresolved, Frozen Panel selection has not begun,
and Wave 0 remains unauthorized.

Records use these canonical locations:

- `domain-universe/boundaries/`
- `domain-universe/source-frames/`
- `domain-universe/extractions/`
- `domain-universe/normalization/pass1/`
- `domain-universe/normalization/pass2a/`
- `domain-universe/normalization/pass2b/`
- `domain-universe/normalization/residuals/`
- `domain-universe/normalization/closure/` (exact D3 successor application)
- `domain-universe/normalization/completion/` (exact D4 completion manifest)
- `domain-universe/normalization/dispositions/` (future versioned overlays;
  currently absent)
- `domain-universe/candidates/`
- `domain-universe/eligibility/`
- `domain-universe/relations/`
- `domain-universe/proposals/`
- `domain-universe/reviews/`
- `domain-universe/governance/`
- `domain-universe/manifests/`

Templates under `schemas/templates/` are intentionally invalid non-records.
Creating directories or JSON files here does not itself establish eligibility,
approval, authority, or a locked Domain Universe.
