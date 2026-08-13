---
okf_version: "0.2"
---

# OKF Federation

## Specification

* [Draft specification](SPEC.md) - Normative requirements for discovery, authority, validation, and reconciliation.
* [Governance](GOVERNANCE.md) - How the proposal evolves and how decisions are reviewed.
* [Roadmap](ROADMAP.md) - Work planned between the initial draft and a stable release.
* [Prior art](PRIOR_ART.md) - Existing standards and systems reused by or adjacent to this proposal.

## Implementer resources

* [Federation manifest schema](schemas/federation.schema.json) - JSON Schema for `federation.yaml`.
* [Default governance profile](profiles/organization-and-repository-owners.yaml) - One organization maintainer for the root and repository maintainers for members.
* [Minimal example](examples/minimal/) - A root bundle, one member bundle, and workspace bootstrap files.
* [Multi-repository changes](examples/multi-repository/) - Coordinating changes that cannot be committed atomically.
* [Conformance](conformance/) - Conformance levels, fixtures, and validation guidance.

## Project

* [Contributing](CONTRIBUTING.md) - How to propose specification and implementation changes.
* [Security](SECURITY.md) - Security considerations and vulnerability reporting.
* [Change log](log.md) - Significant updates to the proposal.
