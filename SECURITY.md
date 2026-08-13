---
type: Policy
title: Security Policy
description: Security scope and responsible reporting guidance for OKF Federation.
status: draft
tags: [security, disclosure]
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
---

# Security policy

Do not open a public issue for a vulnerability that could expose credentials,
bypass authority checks, fabricate approval or verification, traverse outside a
validated workspace, or execute untrusted content.

Until a dedicated private reporting address is published, use GitHub's private
security advisory flow for `manaty/okf-federation`.

The reference validator treats bundle content as untrusted input. It must not
execute code found in knowledge documents, follow links outside the selected
workspace for local validation, or print secret values in diagnostics.
