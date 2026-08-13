---
type: Reference
title: Conformance
description: Describes progressive OKF Federation conformance and current validator coverage.
status: draft
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
---

# Conformance

Conformance is progressive:

| Level | Required capability |
|---|---|
| 0 | Discovery |
| 1 | Authority |
| 2 | Validation |
| 3 | Reconciliation |

The reference validator currently exercises Level 0 and a structural subset of
Level 1 and Level 2. It checks the manifest schema, unique IDs, member presence,
OKF structure, bootstrap routing, local links, declared roles, and basic
freshness rules.

Hosting-provider approval evidence, semantic drift detection, and prospective
multi-PR validation remain planned for `0.2` and `0.3`.
