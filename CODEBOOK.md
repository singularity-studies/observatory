# Codebook

- Instrument: Observation Codebook
- Instrument version: `0.1.0-draft`
- Status: `DRAFT`
- Effective Wave: none

This codebook defines representational states only. It contains no coded cases or empirical values.

## General coding rules

1. Code from evidence, never from expectation.
2. Retain conflicting evidence and explain adjudication.
3. Use `unknown` when evidence is missing, inaccessible, ambiguous, or insufficient.
4. Do not infer `absent` from an empty field, unreturned search result, or unavailable source.
5. Record the instrument version used for every coded observation.

## Human-criticality state

`human_criticality_state` represents the supported state for a bounded function at an observation time.

- `human_critical`: evidence supports that a human contribution remains necessary to the defined function.
- `mixed_or_contested`: evidence supports heterogeneous, conditional, or disputed criticality.
- `human_noncritical`: evidence supports that the defined function can continue without a human contribution under the stated boundary conditions.
- `unknown`: the evidence does not support a determination.

These labels do not supply an operational threshold. That threshold remains unresolved for Wave 0 design.

## Presence assessment

`presence_assessment` controls missingness semantics.

- `present`: evidence supports presence within the defined observation scope.
- `absent`: evidence supports absence within a defined opportunity-to-observe.
- `unknown`: absence or presence cannot be supported.

An omitted value is invalid. `unknown` is an explicit scientific state.

## Longitudinal event

`event_type` represents a comparison with an explicitly referenced prior observation.

- `transition_toward_human_noncriticality`
- `reversal_toward_human_criticality`
- `human_reentry`
- `no_supported_change`
- `unknown`

`no_supported_change` requires comparable observations; it is not a substitute for missing data. `human_reentry` may overlap conceptually with reversal, so any future rule for precedence or multi-label coding must be versioned before Wave 0.

## Evidence relation

Each coding record may cite evidence as `supports`, `contradicts`, or `contextualizes`. A final assessment must not erase contradictory records.

## Required observation fields

The machine-readable contract in `schemas/observation.schema.json` requires identifiers, dates, instrument versions, evidence references, current state, presence assessment, and longitudinal event representation. It intentionally contains no numeric score.

## Unresolved before Wave 0

- unit of analysis below or above the case level;
- threshold for necessary human contribution;
- handling of conditional fallback and latent human oversight;
- relationship between reversal and human re-entry;
- reliability and adjudication procedure; and
- whether any ordinal or quantitative measure is scientifically justified.
