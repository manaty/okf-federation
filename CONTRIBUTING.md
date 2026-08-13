---
type: Process
title: Contributing to OKF Federation
description: Contribution workflow for specification, schema, examples, and validator changes.
status: draft
tags: [contributing, governance]
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
---

# Contributing

1. Read [`index.md`](index.md), [`SPEC.md`](SPEC.md), and
   [`GOVERNANCE.md`](GOVERNANCE.md).
2. Open an issue for a material normative change or add an RFC under `rfcs/`.
3. Keep specification, schema, examples, and validation behavior aligned.
4. Add a conformance fixture for behavior that a validator must accept or
   reject.
5. Run:

   ```bash
   python3 -m pip install -r requirements-dev.txt
   python3 scripts/validate.py examples/minimal/workspace/home/federation.yaml \
     --workspace examples/minimal/workspace --today 2026-08-13
   python3 scripts/validate_bundle.py examples/minimal/workspace/service-a \
     --member service-a
   python3 -m unittest discover -s tests -v
   ```

Pull requests and review discussions are written in English. Contributions
must not contain credentials, private organizational data, or copied material
without a compatible license.
