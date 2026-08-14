# Frozen Panel

- Instrument: Frozen Panel Specification
- Instrument version: `0.3.0-draft`
- Status: `DRAFT`
- Effective Wave: none

## Current panel

No panel units are included. No Frozen Panel has been approved or locked.

## Primary ontology

The primary panel unit is a bounded function or stage within a defined civilization improvement loop, framed as a potential Human Bottleneck. The unit definition must identify the loop, the function/stage, its boundary conditions, and the human contribution under investigation.

Technologies, products, organizations, and deployments are empirical systems linked to panel units. They do not become primary panel units merely because they are observable. A panel unit may link to multiple empirical systems so that the function can be followed across implementations and time.

## Separation from the Live Registry

The Live Registry in `registry/` is a mutable inventory of candidate improvement-loop functions. This document and any future panel snapshot are controlled Wave instruments. Registry additions and empirical-system link changes do not change a Frozen Panel.

## Freeze procedure

Before a panel may be used by an official Wave:

1. version and lock inclusion and exclusion criteria;
2. record the registry snapshot used for selection;
3. document every included and excluded panel-unit decision without inventing missing facts;
4. assign immutable panel-unit identifiers;
5. review conflicts of interest and scope coverage;
6. serialize selected functions/stages and their empirical-system links into a versioned panel snapshot;
7. compute its SHA-256 digest; and
8. reference that version and digest from the Wave manifest.

A locked or official Wave cannot use an empty Frozen Panel. Every frozen panel unit must have explicit observation coverage in that Wave; inability to determine a state is recorded as a version-valid unresolved observation, never as omission.

After lock, the panel snapshot is immutable. A later addition or removal requires a new panel version and a new Wave boundary.

## Unresolved before Wave 0

- panel-unit eligibility and improvement-loop boundary rules;
- domains and stratification;
- panel size and replacement rules;
- treatment of related or nested functions and shared empirical systems; and
- decision authority for panel freeze.
