# Frozen Panel

- Instrument: Frozen Panel Specification
- Instrument version: `0.1.0-draft`
- Status: `DRAFT`
- Effective Wave: none

## Current panel

No cases are included. No Frozen Panel has been approved or locked.

## Separation from the Live Registry

The Live Registry in `registry/` is a mutable candidate inventory. This document and any future panel snapshot are controlled Wave instruments. Registry additions do not change a Frozen Panel.

## Freeze procedure

Before a panel may be used by an official Wave:

1. version and lock inclusion and exclusion criteria;
2. record the registry snapshot used for selection;
3. document every included and excluded candidate decision without inventing missing facts;
4. assign immutable case identifiers;
5. review conflicts of interest and scope coverage;
6. serialize the selected cases into a versioned panel snapshot;
7. compute its SHA-256 digest; and
8. reference that version and digest from the Wave manifest.

After lock, the panel snapshot is immutable. A later addition or removal requires a new panel version and a new Wave boundary.

## Unresolved before Wave 0

- candidate eligibility;
- domains and stratification;
- panel size and replacement rules;
- treatment of related or nested systems; and
- decision authority for panel freeze.
