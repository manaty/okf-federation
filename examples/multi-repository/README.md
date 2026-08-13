---
type: Reference
title: Multi-repository Change Example
description: Explains the example coordination record for a non-atomic federated change.
status: stable
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
---

# Multi-repository change example

[`change.md`](change.md) illustrates a root-owned coordination record. It does
not make independent Git merges atomic. Each listed repository still applies
its own review policy, and the change closes only after post-merge federation
validation succeeds.
