---
type: Policy
title: OKF Federation Project Governance
description: Defines stewardship and the change process for the OKF Federation community proposal.
status: draft
tags: [governance, project]
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
---

# Project governance

## Status and stewardship

OKF Federation is an independent community proposal initially stewarded by
Manaty. Stewardship does not confer ownership of OKF, AGENTS.md, GitOps, or any
other referenced standard or trademark.

The project aims to move to multi-organization maintainership before declaring
version 1.0 stable.

## Changes

All normative changes are proposed through pull requests. A proposal must:

1. state the interoperability problem;
2. explain why existing OKF and Git mechanisms are insufficient;
3. include schema, example, validator, and prior-art updates where relevant;
4. preserve unknown extension fields and progressive adoption; and
5. document backward compatibility.

Material changes should begin as an RFC under `rfcs/`. Editorial corrections
and non-normative clarifications can be proposed directly.

## Decisions

During the `0.x` phase, one Manaty maintainer approval is required. A proposer
must not be the sole approver of a normative change. Before `1.0`, this file
will be revised to identify named maintainers, a voting or consensus process,
appeals, and release signing.

### Maintainer bypass

Repository rules may grant a named maintainer a bypass for continuity. The
bypass is an operational exception, not an alternative decision process.

A bypass:

- MAY be used for editorial or non-normative changes after required CI passes;
- MAY be used to recover from an incident when waiting for the normal review
  path would materially extend the incident;
- MUST include the reason in the pull request record;
- MUST preserve an auditable pull request and passing required checks whenever
  the hosting platform permits it; and
- MUST NOT make the proposer the sole approver of a normative change.

Any use outside these conditions is a governance violation and should be
reviewed after the fact. Repeated incident bypasses should result in a process
or maintainer-coverage change rather than becoming the normal merge path.

## Releases

Releases are tagged. Each release records:

- specification version and commit;
- schema changes;
- conformance changes;
- migration guidance; and
- known interoperability limitations.
