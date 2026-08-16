# Normalization Closure Gap Amendment

- Version: v0.1
- Status: POST-D1 VERSIONED AMENDMENT; FIXED BEFORE APPLICATION; NOT SCIENTIFICALLY APPROVED
- Instrument version: 0.5.0-draft
- Effective Wave: none
- Application records created by this task: none

## Timing and purpose

This successor amendment was introduced after Task 105D1 revealed a normalization state not representable by Codebook v0.1. It is fixed before any source entry is reclassified under the new rule.

This rule was not pre-registered before Task 105D1. Task 105D1 remains an immutable historical clarification record, and all eight entries assessed there remain unresolved. This amendment defines a general successor rule prospectively; it does not apply that rule to those entries or to any other source entry.

Post-observation rule development must be versioned and separated from its subsequent application.

## Closure gap

Codebook v0.1 can represent an entry that passes normalization, is outside the registered research universe, or remains unresolved. Task 105D1 exposed a distinct possible state: the source entry can be understood well enough to assess, yet the registered extraction unit has no coherent substantive locus from which a topic-preserving Domain candidate can be materialized, while incompatibility with the research universe has not been established.

Without an explicit successor disposition, that state can only remain unresolved even after the relevant uncertainty has been resolved. This amendment closes that state-space gap without rewriting the historical codebook or any historical assessment.

## Successor disposition

The amendment introduces exactly one successor normalization disposition:

`excluded_non_materializable`

Canonical meaning: the source entry is semantically sufficient for this decision, but at the registered extraction granularity it lacks a coherent substantive locus and cannot be materialized into a topic-preserving Domain candidate; incompatibility with the registered research universe has not been established.

Non-materializable at the registered extraction granularity is not out-of-scope in the underlying world.

Broad is not the same as non-materializable. A broad source entry may still have a coherent substantive locus and support topic-preserving materialization. Breadth alone never satisfies this disposition.

Terminal for this source-entry granularity does not mean terminal for the underlying subject matter. A later, separately governed protocol may examine another source granularity, but that possibility does not alter or reopen a decision made at the registered extraction granularity.

## Conjunctive decision rule

`excluded_non_materializable` is permitted only when all five conditions hold:

1. The predecessor normalization result is `unresolved`.
2. Semantic sufficiency is `true`: the available source meaning is sufficient to decide the remaining materialization question.
3. Coherent substantive locus is `false`: the registered source entry does not identify one coherent substantive locus at its extraction granularity.
4. Topic-preserving materialization possible is `false`: no Domain candidate can be created from that entry without changing its topic or inventing a narrower locus.
5. Research-universe incompatibility established is not `true`: it is either `false` or `null`, so the record does not claim that the underlying subject matter is outside the research universe.

If and only if all five conditions hold, the future closure decision must use `excluded_non_materializable`. Every other combination must remain `unresolved` under this amendment. Candidate contribution must be `none` in either case.

## Decision precedence

The successor closure step follows the historical normalization record and precedes any future disposition overlay or candidate materialization:

```text
immutable predecessor result = unresolved
-> successor normalization-closure assessment
-> excluded_non_materializable only under the five-condition rule
-> otherwise unresolved
-> no candidate contribution from either result
```

The disposition must not be inferred from the label, breadth, residual status, or source-frame family. Each future application requires a separate versioned record that binds its predecessor and source extraction.

## Distinctions

### Unresolved

`unresolved` means that at least one condition needed for closure is not established or that the five-condition terminal rule is not met. Missing evidence remains unknown; `null` is not treated as `false` except where the rule expressly permits either `false` or `null` for research-universe incompatibility.

### Out of scope

`excluded_non_materializable` does not mean `fails_out_of_scope` or `excluded_out_of_scope`. It makes no claim that the underlying activity, function, technology, institution, or human concern lies outside the Domain Universe boundary.

### Final Domain eligibility

This is a normalization disposition at source-entry granularity, not a Domain eligibility decision. It neither establishes Domain separation nor resolves overlap, non-duplication, final eligibility, coverage, selection, or panel membership.

## Future granularity

This amendment does not authorize decomposition, re-extraction, or replacement of any registered source entry. Any future finer-grained treatment requires its own versioned method, provenance, and governance path. Such future work must preserve the historical extraction and closure records rather than silently revising them.

## Change control and non-application state

The amendment and its schema are prospective successor instruments. They are not added to the current Domain Universe lock schema bundle, and the current materialization architecture does not consume them. A later task must separately create and validate any closure decision record before any overlay or candidate workflow can be reconsidered.

During this task:

- normalization-closure decision records remain zero;
- normalization-disposition overlay instances remain zero;
- Domain candidates and assigned stable candidate IDs remain zero; and
- `STABLE_CANDIDATE_ID_ASSIGNMENT_PERMITTED` remains `false`.

No statement in this amendment constitutes scientific approval, governance lock, Domain Universe lock, Frozen Panel selection, or Wave 0 authorization.
