---
type: Reference
title: OKF Federation
description: Overview and quick start for the OKF Federation community proposal.
status: draft
tags: [okf, federation, governance]
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
---

# OKF Federation

OKF Federation is a community proposal for governing organizational knowledge
that is distributed across multiple Git repositories and represented as
[Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
bundles.

OKF defines the portable knowledge documents. OKF Federation defines how an
organization discovers those bundles, assigns authority, reviews changes,
checks freshness, and reconciles drift without copying every fact into one
repository.

> [!IMPORTANT]
> This project is an independent community proposal. It is not an official
> Google, Open Knowledge Format, CNCF, or Linux Foundation specification.

## Status

Version `0.1-draft` is open for review. The draft focuses on four progressive
conformance levels:

1. **Discovery** — one root entry point and a registry of member bundles.
2. **Authority** — configurable roles, canonical scopes, and review policies.
3. **Validation** — structural, federation, ownership, and freshness checks.
4. **Reconciliation** — drift reporting and coordinated multi-repository
   changes.

## Start here

- [Knowledge entry point](index.md)
- [Draft specification](SPEC.md)
- [Minimal example](examples/minimal/README.md)
- [Prior art and differentiation](PRIOR_ART.md)
- [Project governance](GOVERNANCE.md)

Validate the examples locally:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate.py federation.yaml --workspace .
python3 scripts/validate.py examples/minimal/workspace/home/federation.yaml \
  --workspace examples/minimal/workspace --today 2026-08-13
python3 scripts/validate_bundle.py examples/minimal/workspace/service-a \
  --member service-a
python3 -m unittest discover -s tests -v
```

Member repositories can run `validate_bundle.py` in their own CI without
checking out the root manifest or exposing a private federation registry. This
is a structural bundle gate; federation authority, ownership, cross-member
references, and freshness remain root-validator responsibilities.

## License

Code and schemas are licensed under Apache-2.0. Specification and documentation
text are made available under Apache-2.0 as part of this repository.
