# Frozen Panel selection records

This directory is reserved for future versioned candidate specifications,
eligibility decisions, lineage records, panel-selection proposals and
manifests, scientific reviews, and governance decisions.

It currently contains no candidate, eligibility, disposition, lineage,
proposal, review, authority, approval, or lock record. The Live Registry
remains separately mutable under `registry/`; locked Wave packages remain
separately immutable under `data/waves/`.

Future records use these locations:

- `selection/candidates/`
- `selection/eligibility/`
- `selection/lineage/`
- `selection/manifests/`
- `selection/proposals/`
- `selection/reviews/`
- `selection/governance/`

No record subdirectory or record is created until a real, governed selection
process begins. JSON placed under those paths is fail-closed by
`scripts/validate.py`.
