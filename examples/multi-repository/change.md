---
type: Federated Change
title: Introduce Service A events v2
description: Coordinates the producer contract, consumer migration, and root catalog update for a versioned event change.
status: draft
tags: [federated-change, contracts]
generated: { by: "human:example-author", at: "2026-08-13T00:00:00Z" }
change_id: fc-service-a-events-v2
members:
  - id: service-a
    role: producer
    candidate: https://github.com/acme/service-a/pull/42
  - id: service-b
    role: consumer
    candidate: https://github.com/acme/service-b/pull/17
  - id: home
    role: derived-catalog
    candidate: https://github.com/acme/home/pull/9
merge_order: [service-a, service-b, home]
compatibility: v1 and v2 coexist until every registered consumer has migrated
---

# Introduce Service A events v2

## Gate

All candidate revisions must validate together before the first merge. Service
A publishes v2 while retaining v1. Service B then migrates, and `home` updates
its derived catalog last.

## Completion evidence

The coordinator records the merged commit for each member and attaches the
post-merge federation validation result before marking this concept stable.
