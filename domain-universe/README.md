# Domain Universe records

Domain Universe construction is in progress. This namespace contains one
prospectively fixed boundary specification, `du-boundary-v0.1`, and exactly
four registered source frames: OECD FORD (Frascati Manual 2015), UN ISIC
Revision 5, WIPO IPC 2026.01, and UN COFOG 1999.

Exhaustive Task 104 second-level extraction is complete: 42 FORD fields, 87
ISIC Rev.5 Divisions, 132 IPC 2026.01 Classes, and 69 COFOG 1999 Groups, for
330 source categories in four extraction ledgers. The entries are source
classification categories, not Domains. Every normalization disposition is
intentionally `unresolved`; Pass 1, Pass 2A, and Pass 2B have not changed those
dispositions, and candidate generation has not begun.

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

`NORMALIZATION_MATERIALIZATION_PROTOCOL.md` v0.1 now prospectively fixes the
materialization provenance architecture, pending scientific review. Task 104
dispositions and targets, and the bound source-frame status metadata, remain
immutable historical snapshots. Future authoritative disposition state belongs
in a separately versioned overlay under `normalization/dispositions/`, and
future candidates must bind that overlay while retaining exact Task 104
extraction provenance. No overlay instance exists. Because eight source entries
remain unresolved, stable candidate-ID assignment is not permitted.

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
