---
type: Study
title: Prior Art and Differentiation
description: Compares OKF Federation with adjacent knowledge, memory, catalog, instruction, and reconciliation systems.
status: draft
tags: [prior-art, okf, memory, catalogs, gitops]
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
sources:
  - { id: okf, resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md, title: Open Knowledge Format v0.2 }
  - { id: agents, resource: https://agents.md/, title: AGENTS.md }
  - { id: gitops, resource: https://opengitops.dev/, title: OpenGitOps }
  - { id: backstage, resource: https://backstage.io/docs/features/software-catalog/, title: Backstage Software Catalog }
  - { id: amp, resource: https://github.com/agentmemoryprotocol/agentmemoryprotocol, title: Agent Memory Protocol }
  - { id: akbp, resource: https://github.com/rohitg00/akbp, title: Agent Knowledge Base Protocol }
  - { id: noema, resource: https://github.com/Fail-Safe/Noema, title: Noema }
  - { id: openwiki, resource: https://github.com/langchain-ai/openwiki, title: OpenWiki }
  - { id: brain-harness, resource: https://github.com/starmynd-org/infinite-brain-harness, title: Infinite Brain Harness }
  - { id: gitmem, resource: https://gitmem.ai/, title: GitMem }
---

# Prior art and differentiation

Reviewed: 2026-08-13. This is an engineering landscape review, not a trademark
or legal opinion.

## What already exists

| Project or standard | What it already solves | What OKF Federation reuses or leaves to it |
|---|---|---|
| OKF v0.2 | Markdown knowledge bundles, provenance, trust, lifecycle, freshness, and attested computations. | Required document format. This proposal does not define another memory-node format. |
| AGENTS.md | A predictable, tool-neutral instruction file with directory precedence. | Bootstrap routing. Knowledge authority remains separate from instruction precedence. |
| OpenGitOps | Declarative, versioned state pulled and continuously reconciled by software agents. | Inspiration for the observation and reconciliation loop, adapted to review-gated knowledge. |
| Backstage Catalog and TechDocs | Git-backed component metadata, ownership, discovery, and docs close to code. | Catalogs are compatible derived views; no Backstage deployment is required. |
| Agent Memory Protocol | Portable Git-friendly agent memory nodes, daily notes, lifecycle, and conflict concepts. | Personal or agent memory is adjacent; organizational canon continues to use OKF. |
| Agent Knowledge Base Protocol | Evidence-backed claims, reviewed durable writes, cited retrieval, and lifecycle. | Its approval boundary informs the agent write protocol. This proposal focuses on authority across repositories. |
| Noema | Typed local memory, peer federation, source locks, divergence records, and MCP access. | Demonstrates conflict-preserving federation; this proposal uses Git PR governance rather than a peer event protocol. |
| OpenWiki | Agent-maintained OKF wikis and generated AGENTS.md/CLAUDE.md routing. | A potential producer implementation; this proposal governs a federation of outputs. |
| Infinite Brain Harness | A root workspace, sibling repositories, registry, shared canon, and agent adapters. | Closest topology. This proposal narrows the idea to an interoperable OKF governance profile rather than a business operating system. |
| GitMem | Persistent institutional memory for coding agents through MCP and `.gitmem/`. | Direct name collision with the earlier working name; OKF Federation uses a distinct name and scope. |

## Specific gap

The components above cover most individual mechanisms. The remaining
interoperability gap is a small contract answering these questions across Git
repositories:

1. Where does every agent begin discovery?
2. Which repositories participate, and at which canonical revisions?
3. Which member has authority for each class of knowledge?
4. Which human or machine roles may propose and approve changes?
5. How is OKF freshness policy enforced consistently across members?
6. How are structural, federation, governance, source, and semantic drift
   distinguished?
7. How are non-atomic multi-repository changes coordinated and verified?

OKF Federation should remain focused on this gap. Adding a proprietary memory
store, retrieval engine, agent runtime, or graph model would duplicate existing
work and weaken interoperability.
