---
type: Reference
title: Minimal Federation Example
description: Explains the smallest root-and-member OKF Federation workspace.
status: stable
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
---

# Minimal federation example

This example models a workspace containing a root `home` repository and one
producer-owned service repository.

```text
workspace/
├── AGENTS.md
├── CLAUDE.md
├── home/
│   ├── federation.yaml
│   ├── index.md
│   └── org/development-process.md
└── service-a/
    ├── index.md
    └── architecture/index.md
```

The example paths stand in for independent Git checkouts. Validate it from the
project root:

```bash
python3 scripts/validate.py examples/minimal/workspace/home/federation.yaml \
  --workspace examples/minimal/workspace --today 2026-08-13
```

The explicit date keeps this historical fixture deterministic. Real
federations omit `--today` and evaluate freshness against the current date.
