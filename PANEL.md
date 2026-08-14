# Frozen Panel

- Instrument: Frozen Panel Specification
- Instrument version: `0.5.0-draft`
- Status: `DRAFT`
- Effective Wave: none

## Current panel

No candidate units have been recorded. No Frozen Panel has been approved or
locked, and no panel size has been selected.

The prospective coverage frame is governed separately by
`DOMAIN_UNIVERSE.md`. No domain stratum, quota, or panel membership follows
automatically from that instrument.

## Improvement loops and the primary observation unit

An improvement loop is a recurrent process in which outputs or evaluations
from one cycle are used to alter the knowledge, design, policy, system, or
capability that governs a subsequent cycle.

The Observatory is not a generic task-automation tracker. Its primary panel
unit is a bounded function or stage within a recurring civilizational
improvement loop. Each candidate unit must state its conceptual identity as:

```text
Domain
→ Improvement Loop
→ Function/Stage
→ Operational Boundary
→ Continuity Rule
```

The continuity rule states what must remain stable for the unit to retain its
identity across time, even when empirical systems change. Products, companies,
AI models, organizations, and deployments are not primary panel units. They may
later be linked as empirical-system instantiations or evidence sources.

## Eligibility criteria

A candidate must satisfy every criterion below:

1. **Improvement-loop relevance:** the unit occupies a function or stage in a
   recurrent improvement loop as defined above.
2. **Functional boundedness:** the function or stage has a stated operational
   boundary that distinguishes it from adjacent work.
3. **Human-criticality interrogability:** evidence could, in principle,
   support inquiry into whether and how human contribution is critical.
4. **Longitudinal identity stability:** a continuity rule makes the unit
   identifiable across time without tying it to one product or organization.
5. **Re-observability:** the unit can prospectively be revisited under a
   versioned observation schedule.
6. **Evidence traceability:** future observations can retain source identity
   and observation date.
7. **Boundary-condition expressibility:** conditions under which the unit or
   an inference would cease to apply can be stated.
8. **Non-redundancy:** the unit is not merely a duplicate of another candidate
   under the applicable boundaries and continuity rules.

For selection protocol v1, `failed`, missing, or `unresolved` on any criterion
prevents an `eligible` decision. No exception mechanism exists.

**Baseline human-criticality status is not a selection variable.** No baseline
human-criticality classification is required by the candidate specification,
eligibility decision, or selection disposition. **Baseline human-criticality
is first coded after panel lock as a Wave-observation outcome.**
`human_critical`, `mixed_or_contested`, `human_noncritical`, and `unknown`
remain admissible Wave-observation states. They are observational outcomes,
not candidate-selection inputs, targets, or forecasts.

## Anti-selection-bias rule

Do not select a candidate because it:

- appears likely to lose human criticality soon;
- seems close to AGI or ASI;
- is fashionable or heavily covered in AI news;
- is promoted by a vendor;
- appears especially futuristic or dramatic; or
- already appears human-noncritical.

> **Do not optimize the Frozen Panel for excitement. Optimize it for re-observability.**

Selection must not presuppose persistence, disappearance, reversal, human
re-entry, or any other direction of future transition.

## Selection pipeline

```text
Live Candidate Registry
→ Eligibility Screen
→ Coverage / Redundancy Review
→ Frozen Panel Candidate Set
→ Scientific Review
→ LOCK
```

The Live Registry remains mutable. Registry membership is not eligibility or
panel inclusion. A locked Frozen Panel is immutable within its applicable Wave
and instrument version.

## Panel size

Panel size remains unresolved. The final `N` must be fixed prospectively only
after domain-universe construction, candidate-universe construction,
eligibility screening, coverage analysis, and operational workload analysis.
A future comparison may evaluate candidate sizes such as 30, 40, 50, or 60;
this instrument does not select any of them.

## Retirement and lineage

A unit is never removed because it becomes boring, stable, human-critical,
human-noncritical, reversed, or inconvenient. `RETIRED` is permitted only when
the underlying improvement-loop function ceases to exist, loses coherent
semantic identity, or becomes structurally non-observable under the applicable
versioned rules.

Retirement preserves the retired unit's identity and history. It does not
automatically create a replacement. Any successor or replacement receives its
own identifier and an explicit lineage relation in a later panel version. A
successor may not reuse the retired unit identifier. Prior Waves are never
retroactively rewritten.

## Machine-readable records

Versioned schemas define candidate unit specifications, eligibility decisions,
lineage/retirement relations, panel-selection proposals and manifests,
scientific reviews, and panel-lock governance decisions. Eligibility records
preserve every criterion result, rationale, uncertainty, instrument version,
and unresolved reviewer/adjudication fields when roles are unassigned.
Scientific review and governance authority require structured, versioned,
hash-bound records with an explicit permitting outcome. The immutable proposal
contains the complete pre-approval selection state. A scientific review binds
to its exact path and SHA-256; governance binds to that same proposal and exact
approving review. Nothing in this chain hashes the final manifest, so the
binding is non-circular. Structured proposal, review, and governance IDs must
equal their repository filename stems. Templates under `schemas/templates/`
are intentionally incomplete and are not candidate or approval records.

Every candidate in a frozen candidate universe receives exactly one
deterministic eligibility decision. Every eligible candidate then receives
exactly one explicit `selected` or `not_selected` disposition. A non-selection
rationale and uncertainty note are mandatory, and selected identifiers must
exactly equal the `selected` dispositions. An eligible candidate cannot
silently disappear between screening and panel lock.

Future selection records belong under `selection/` and remain distinct from
the mutable registry and immutable Wave observations.

## Fail-closed lock procedure

A Frozen Panel must not be locked until all of the following resolve and pass:

1. the selection protocol version is locked and bound to exact bytes;
2. a non-empty candidate-universe snapshot is referenced;
3. every candidate has exactly one deterministic criterion-by-criterion
   eligibility decision, with no outside or duplicate decision;
4. every eligible candidate has an explicit selection disposition;
5. a coverage and redundancy review is recorded;
6. panel size `N` has been prospectively fixed and matches the selected set;
7. the complete pre-approval selection state is preserved as a versioned,
   hash-bound proposal;
8. an approving scientific-review record binds that exact proposal, and an
   authorizing governance-decision record binds the same proposal and exact
   review; all three records are schema-valid, version-compatible, and have IDs
   matching their filename stems;
9. the panel snapshot binds every unit to the exact selected candidate
   specification and preserves its semantic identity;
10. the panel snapshot references the locked selection manifest by path and
   SHA-256; and
11. the selection manifest, its records, and its schemas are preserved inside
   the immutable Wave package.

No lock, authority, exception, candidate universe, or approval is created by
this draft scaffold.

## Separation from the Live Registry

The Live Registry in `registry/` is a mutable inventory of candidate
improvement-loop functions. This document, future selection manifests, and
future panel snapshots are separately controlled instruments. Registry changes
never alter a Frozen Panel.

A locked or official Wave cannot use an empty Frozen Panel. Every frozen panel
unit must have explicit observation coverage in that Wave; inability to
determine a state is recorded as a version-valid unresolved observation, never
as omission.

After lock, the panel snapshot is immutable. A later addition, retirement,
successor, or replacement requires a new panel version and later Wave boundary.

## Unresolved before Wave 0

- domain-universe construction and coverage dimensions;
- candidate-universe construction and provenance procedure;
- panel size and workload model;
- treatment of related or nested functions and shared empirical systems;
- reviewer, adjudicator, and governance roles;
- conflict-of-interest process and scientific review procedure; and
- effective dates and authority for any future protocol exception mechanism.
