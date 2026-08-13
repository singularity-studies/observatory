# Governance

- Instrument: Research Governance Framework
- Instrument version: `0.1.0-draft`
- Status: `DRAFT`
- Effective Wave: none

## Principles

- Scientific records are auditable from source to release.
- Unknown and disagreement remain visible.
- No person may silently rewrite a locked instrument or Wave.
- Release authority is separate from data entry where practicable.
- Governance decisions are versioned, dated, and reviewable.

## Roles to assign before Wave 0

- protocol steward;
- panel custodian;
- evidence and provenance reviewer;
- Wave release approver;
- repository maintainer; and
- conflict-of-interest reviewer.

No individuals are assigned by this scaffold.

## Lock authority

An official Wave requires recorded approval for protocol, panel, schema, schedule, and governance locks. Each approval must identify the instrument version, SHA-256 digest, approver, timestamp, and effective Wave. Self-approval and quorum rules remain unresolved and must be settled before Wave 0.

## Change control

After Wave 0, scientific instrument changes require a new version and an entry in `docs/DECISIONS.md` or a successor decision log. The record must state the rationale, effective Wave, migration plan, and expected effect on longitudinal comparability.

Locked data is append-only. Corrections use an amendment record that identifies the superseded record without deleting it. Source withdrawals, access loss, and disputed interpretations remain visible.

## Release gate

The automated validator is necessary but not sufficient for release. Governance approval is also required. Conversely, governance approval cannot override a failed structural validation: the system fails closed.

## Security and privacy

This repository is scoped to technology and sociotechnical observation. It does not authorize human-subject research or collection of private personal data. Any future expansion that may involve human participants or sensitive personal information requires separate ethical, legal, and governance review before collection.

## Unresolved before Wave 0

- named role assignments and succession;
- quorum and independence rules;
- conflict-of-interest process;
- embargo and incident response procedures;
- human-subject boundary tests; and
- appeal and correction adjudication.
