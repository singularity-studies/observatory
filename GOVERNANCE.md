# Governance

- Instrument: Research Governance Framework
- Instrument version: `0.3.0-draft`
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

An official Wave requires recorded approval for the protocol, codebook, panel, schedule, governance, registry, and validation-schema snapshots sealed into its directory. Each approval must identify the role, version, SHA-256 digest, approver, timestamp, and effective Wave. Self-approval and quorum rules remain unresolved and must be settled before Wave 0.

## Change control

After Wave 0, scientific instrument changes require a new version and an entry in `docs/DECISIONS.md` or a successor decision log. The record must state the rationale, effective Wave, migration plan, and expected effect on longitudinal comparability.

A locked Wave directory is byte-immutable: no addition, modification, rename, or deletion is allowed. Corrections use a separately versioned artifact under `data/amendments/` that identifies the affected Wave and superseded record without altering the original package. Source withdrawals, access loss, and disputed interpretations remain visible.

The locked directory must contain content-hashed snapshots of every scientific instrument and schema needed to interpret and revalidate the Wave. Later top-level versions cannot be substituted during historical validation. Release authority must also verify a non-empty panel, explicit coverage of every panel unit, and resolvable longitudinal references before lock or release.

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
