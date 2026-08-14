# Codebook

- Instrument: Observation Codebook
- Instrument version: `0.3.0-draft`
- Status: `DRAFT`
- Effective Wave: none

This codebook defines representational states only. It contains no coded cases or empirical values.

## General coding rules

1. Code from evidence, never from expectation.
2. Retain conflicting evidence and explain adjudication.
3. Use `unknown` when evidence is missing, inaccessible, ambiguous, or insufficient.
4. Do not infer `absent` from an empty field, unreturned search result, or unavailable source.
5. Record the instrument version used for every coded observation.

## Provisional human-criticality summary

`provisional_human_criticality_summary` is a provisional categorical summary for a bounded improvement-loop function at an observation time.

- `human_critical`: evidence supports that a human contribution remains necessary to the defined function.
- `mixed_or_contested`: evidence supports heterogeneous, conditional, or disputed criticality.
- `human_noncritical`: evidence supports that the defined function can continue without a human contribution under the stated boundary conditions.
- `unknown`: the evidence does not support a determination.

These labels do not supply an operational threshold and are not the full measurement model. Wave 0 construct validation must preserve room for multidimensional analysis of capability, loop closure, verification dependence, authority delegation, recursive gain, and human dependence, among other candidates. This list is exploratory, is not a fixed vector, and does not establish final dimensions, notation, aggregation, or scoring.

## Human-participation presence

`human_participation_presence` refers only to whether human participation is evidenced within the bounded function during the stated observation scope. It does not determine whether that participation is necessary, critical, authoritative, effective, or merely nominal.

- `present`: evidence supports presence within the defined observation scope.
- `absent`: evidence supports absence within a defined opportunity-to-observe.
- `unknown`: absence or presence cannot be supported.

An omitted value is invalid. `unknown` is an explicit scientific state. Presence must not be used as a proxy for criticality.

## Longitudinal event

`event_type` represents a comparison with an explicitly referenced prior observation.

- `transition_toward_human_noncriticality`
- `reversal_toward_human_criticality`
- `human_reentry`
- `no_supported_change`
- `unknown`

`no_supported_change` requires comparable observations; it is not a substitute for missing data. `human_reentry` may overlap conceptually with reversal, so any future rule for precedence or multi-label coding must be versioned before Wave 0.

## Resolution status

`resolution_status` distinguishes an evidence-supported coded observation from explicit unresolved coverage.

- `resolved`: the observation cites at least one evidence record and may use only values permitted by the versioned codebook.
- `unresolved`: no determination is supported for the scheduled panel unit. Evidence references are empty, the provisional summary, participation presence, and event type are all `unknown`, and a non-empty uncertainty note explains why resolution was not possible.

An unresolved record is coverage, not evidence of absence and not a scientific finding. It prevents silent omission without forcing a score, replication rule, or final multidimensional model.

## Evidence relation

Each coding record may cite evidence as `supports`, `contradicts`, or `contextualizes`. A final assessment must not erase contradictory records.

## Required observation fields

The machine-readable contract in `schemas/observation.schema.json` requires panel-unit and empirical-system identifiers, dates, instrument versions, resolution status, evidence references, a provisional summary, human-participation presence, and longitudinal event representation. It intentionally contains no multidimensional fields, aggregation rule, or numeric score.

## Unresolved before Wave 0

- boundaries and nesting of improvement-loop functions;
- threshold for necessary human contribution;
- candidate dimensions, their observability, and whether they can be combined;
- handling of conditional fallback and latent human oversight;
- relationship between reversal and human re-entry;
- reliability and adjudication procedure; and
- whether any ordinal or quantitative measure is scientifically justified.
