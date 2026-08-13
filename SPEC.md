---
type: Specification
title: OKF Federation Specification
description: Defines discovery, authority, validation, and reconciliation for OKF bundles distributed across Git repositories.
status: draft
tags: [okf, federation, governance, git, agents]
generated: { by: "human:manaty-maintainers", at: "2026-08-13T00:00:00Z" }
sources:
  - id: okf-v0.2
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
    title: Open Knowledge Format v0.2
  - id: agents-md
    resource: https://agents.md/
    title: AGENTS.md
  - id: open-gitops
    resource: https://opengitops.dev/
    title: OpenGitOps principles
---

# OKF Federation Specification

Version: `0.1-draft`

## 1. Conventions

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**,
and **MAY** are to be interpreted as described in RFC 2119 and RFC 8174 when,
and only when, they appear in bold capitals.

This document defines a profile above OKF v0.2. It does not modify OKF
conformance. An implementation claiming OKF Federation conformance also
validates each participating knowledge bundle as OKF v0.2.

## 2. Purpose and scope

An organization often keeps cross-cutting knowledge in one repository and
code-adjacent knowledge in the repositories that implement it. Humans and AI
agents need one way to discover this graph while each fact remains governed at
its canonical source.

OKF Federation standardizes:

- a root knowledge bundle and entry point;
- registration of member bundles in other repositories;
- configurable authority and review policies;
- portable freshness policy built on OKF lifecycle metadata;
- detection and reporting of drift;
- review-gated writes by humans and agents;
- coordination of changes spanning repositories; and
- deterministic handling of authority conflicts.

It does not standardize a search engine, vector database, agent runtime, Git
hosting provider, identity provider, deployment system, or model context
transport.

## 3. Terms

**Federation**
: A root bundle and the registered member bundles it makes discoverable.

**Root bundle**
: The OKF bundle that owns the federation manifest, organization-wide policy,
  and root entry point. `home` is a conventional name, not a requirement.

**Member bundle**
: An OKF bundle registered by the root. It can be the root of a repository or a
  directory within one.

**Workspace**
: A local directory in which the root and some or all member repositories are
  checked out as siblings. A workspace is a runtime arrangement and need not be
  a Git repository.

**Bootstrap adapter**
: A file recognized by an agent host, such as `AGENTS.md` or `CLAUDE.md`, that
  directs the agent to the federation root entry point.

**Canonical scope**
: A class of knowledge for which exactly one registered member has final
  editorial authority.

**Observed state**
: Evidence from code, contracts, infrastructure, runtime systems, tickets, or
  other declared sources against which knowledge can be checked.

**Drift**
: A detectable mismatch within the federation, or between canonical knowledge
  and observed state.

**Reconciler**
: A human or software agent that detects drift and reports it or proposes a
  change. A reconciler is not necessarily authorized to approve that change.

## 4. Design principles

1. **Knowledge stays with its authority.** Detailed facts are maintained once
   at the member that owns them. The root links to them rather than copying
   editable prose.
2. **Git history is the audit trail.** Canonical changes are versioned,
   attributable, reviewable, and reversible.
3. **Agents propose; policy admits.** An agent MAY write a branch or proposal,
   but durable canon changes only through the declared review policy.
4. **Indexes are derived.** Search indexes, graphs, catalogs, and summaries MAY
   accelerate consumption but MUST NOT become a second editable source of
   truth.
5. **Freshness and trust are explicit.** Implementations use OKF `generated`,
   `verified`, `status`, `sources`, and `stale_after`; they do not infer truth
   merely from a recent Git commit.
6. **Conflicts are surfaced.** A reconciler MUST NOT silently choose between
   equal authorities or contradictory canonical claims.
7. **Adoption is progressive.** Legacy members can be registered in an
   advisory mode before all conformance gates become blocking.

## 5. Federation topology

A federation **MUST** have exactly one root bundle. It **MUST** register itself
and **MAY** register any number of member bundles.

A typical local workspace is:

```text
workspace/
├── AGENTS.md               -> read home/index.md
├── CLAUDE.md               -> read home/index.md
├── home/                   # root Git repository and root OKF bundle
│   ├── federation.yaml
│   └── index.md
├── service-a/              # independent Git repository and member bundle
│   └── index.md
└── service-b/
    └── docs/index.md       # bundle may be a repository subdirectory
```

The local layout is not canonical. Repository URI, revision, bundle path, and
entry point in `federation.yaml` identify a member. `workspace_path` is only a
local checkout hint and **MUST NOT** be treated as a globally meaningful ID.

## 6. Federation manifest

The root repository **MUST** contain `federation.yaml` at the root of its OKF
bundle. The manifest **MUST** validate against
[`schemas/federation.schema.json`](schemas/federation.schema.json).

The minimum manifest declares:

```yaml
federation: "0.1"
id: acme-engineering
root: home
members:
  - id: home
    repository: https://github.com/acme/home
    ref: main
    bundle: .
    entrypoint: index.md
    workspace_path: home
    enforcement: required
```

Member IDs **MUST** be unique and stable. Renaming a repository does not by
itself rename a member. A repository can expose more than one bundle, provided
each has a distinct member ID and bundle path.

`ref` identifies the branch or tag whose merged state is canonical. Consumers
working on a proposal MAY read another revision, but **MUST** label it as a
candidate state rather than current canon.

`enforcement` has three modes:

- `required`: all declared gates are blocking;
- `advisory`: violations are reported but do not block federation validity;
- `migrating`: the member is intentionally incomplete and **MUST** declare a
  migration owner and target date.

## 7. Discovery and bootstrap

The root `index.md` **MUST** be a valid OKF bundle index and **MUST** make
organization-wide policy and registered knowledge areas progressively
discoverable.

Each member entry point **MUST**:

- identify the member's purpose and locally canonical knowledge;
- link to relevant root policy; and
- avoid redefining organization-wide rules unless it records an explicitly
  approved exception.

A workspace intended for agent use **MUST** contain at least one supported
bootstrap adapter that directs the agent to the root entry point. It **SHOULD**
provide both `AGENTS.md` and `CLAUDE.md` when those hosts are used.

Bootstrap adapters are routing shims, not knowledge stores. They **SHOULD** be
minimal and **MUST NOT** restate canonical policy. Repository-specific adapter
files MAY add local operating instructions, but durable factual knowledge
SHOULD be placed in the local OKF bundle and linked from the adapter.

## 8. Authority model

Authority is configurable. This specification does not require a particular
organizational chart or Git provider.

The manifest **MUST** define or select:

- roles whose membership can be resolved by an implementation;
- canonical scopes mapping knowledge classes to one member;
- review policies mapping changes to required approvals; and
- a default rule for member-local knowledge.

Resolvers MAY use literal identities, repository maintainers, CODEOWNERS,
hosting-provider teams, or an external identity system. An implementation
**MUST** expose unresolved roles as an error for `required` members and **MUST
NOT** silently replace them with the proposing agent.

The recommended profile is:

- organization maintainers approve root and cross-organization knowledge;
- repository maintainers approve member-local knowledge;
- contract producers approve their contracts;
- generated views have no independent editorial authority; and
- self-approval is forbidden.

Organizations MAY require different counts, roles, or separation of duties.
The example profile in
[`profiles/organization-and-repository-owners.yaml`](profiles/organization-and-repository-owners.yaml)
is informative.

### 8.1 Canonical scopes

Canonical scopes are matched by member, path, and optionally OKF concept type.
The following defaults are recommended:

| Knowledge class | Canonical member |
|---|---|
| Organization policy, portfolio, and cross-system architecture | Root |
| Service implementation and internal architecture | Producer member |
| Database schema and migrations | Schema-owning member |
| OpenAPI, AsyncAPI, and reusable schema contracts | Contract producer |
| Service operations and runbooks | Operating member |
| Generated catalog or search index | No editorial authority; regenerate from sources |

Two canonical-scope rules that assign equal authority to different members for
the same knowledge class are invalid unless one is explicitly more specific.

### 8.2 Review evidence

Approval is evidence from the configured Git workflow, not an OKF `verified`
event. Approval admits a change; `verified` records that knowledge was checked
against its sources. One action MAY produce both events, but implementations
**MUST** keep their meanings distinct.

## 9. Agent write protocol

Implementations **MUST** treat the following capabilities independently:

| Capability | Meaning |
|---|---|
| `read` | Consume canonical knowledge. |
| `report-drift` | Record evidence of a mismatch without changing canon. |
| `propose` | Create a branch, patch, issue, or pull request. |
| `approve` | Admit a proposal into the canonical revision. |

The default policy grants reconcilers `read`, `report-drift`, and `propose`, but
not `approve`.

An agent-generated proposal **MUST** preserve provenance, identify affected
canonical scopes, and include validation results. An agent **MUST NOT** invent a
human `verified.by` identity or approval event. Implementations **SHOULD** scan
proposed knowledge for credentials, personal data, prompt injection, and
untrusted executable instructions before review.

Temporary plans, raw transcripts, chain-of-thought, private tool caches, and
unreviewed observations are not durable organizational knowledge. They **MUST
NOT** become stable canon merely because an agent persisted them. A useful
observation is promoted as an OKF concept with sources through the normal review
policy.

## 10. Freshness and lifecycle

OKF Federation reuses the OKF v0.2 lifecycle fields:

- `generated.at` records the last meaningful content change;
- `verified` records human or process verification against sources;
- `status` distinguishes `draft`, `stable`, and `deprecated`; and
- `stale_after` is the absolute date on which the concept becomes stale.

The manifest MAY define freshness policies by member, path, type, or tag. A
policy can require a trust tier, maximum verification age, or explicit
`stale_after` value. Policy durations are evaluation rules; when a concrete
concept carries `stale_after`, it remains an absolute OKF date.

Implementations **MUST NOT** equate these states:

- stale with false;
- recent with verified;
- machine-confirmed with human-reviewed; or
- deprecated with deleted.

When a meaningful content change invalidates an earlier verification, the
proposal **MUST** remove or replace the obsolete `verified` event. Historical
decisions and incident records SHOULD remain immutable; a later decision links
to and supersedes them rather than rewriting history.

## 11. Validation

A Level 2 validator **MUST** check:

1. manifest schema and unique member IDs;
2. presence and OKF v0.2 conformance of required bundles;
3. member and root entry points;
4. resolvable local and cross-member references required by the profile;
5. one canonical authority for every governed scope;
6. resolvable required roles;
7. freshness policies and stale concepts; and
8. absence of independently editable generated copies.

The core OKF specification tolerates broken links. A federation MAY make a
subset blocking because those links are its discovery and authority graph.
Links declared canonical by the manifest are always blocking for `required`
members.

Validators **MUST** produce machine-readable results with a stable code,
severity, member, path, and human-readable explanation. Severity is one of
`info`, `warning`, or `error`. A validator exits unsuccessfully when any error
applies to a `required` member.

## 12. Drift and reconciliation

Reconcilers distinguish five drift classes:

| Class | Examples |
|---|---|
| `structural` | Invalid YAML, missing OKF type, duplicate ID. |
| `federation` | Missing member, broken canonical link, absent backlink. |
| `governance` | Unresolved owner, insufficient approval, forbidden self-approval. |
| `source` | A declared source changed after the knowledge was verified. |
| `semantic` | Code, contract, runtime evidence, or another canonical claim contradicts the document. |

A reconciler **MUST** preserve the distinction between desired policy and
observed state. Code proving that implementation differs from policy is grounds
for a drift report, not permission to rewrite the policy automatically.

Reconciliation follows this loop:

```text
observe -> validate -> classify drift -> report/propose -> review -> merge -> verify
```

Safe deterministic repairs MAY be automated when policy allows them, for
example regenerating an index. Semantic repairs SHOULD be proposals reviewed by
the relevant authority. Equal-authority contradictions **MUST** stop automatic
reconciliation.

## 13. Multi-repository changes

Git does not provide atomic commits across repositories. An implementation
**MUST NOT** describe a set of independent merges as atomic.

A coordinated change SHOULD be represented by an OKF concept of type
`Federated Change` in the root bundle. It identifies:

- a stable change ID;
- affected members and canonical scopes;
- candidate pull requests or commits;
- dependency and merge order;
- required approvers for each member;
- compatibility or rollback constraints; and
- final reconciliation evidence.

The recommended sequence is:

1. prepare all member proposals;
2. validate their candidate revisions as one prospective federation;
3. obtain each member's required approvals;
4. merge producers before derived catalogs or consumers when compatible;
5. use version coexistence or feature gates for non-atomic transitions;
6. validate the merged federation; and
7. close the federated change only after convergence.

Strict cross-repository atomicity requires a monorepo or an external
transaction coordinator and is outside this specification.

## 14. Conflict resolution

Implementations resolve conflicts in this order:

1. apply the most specific explicit canonical-scope rule;
2. otherwise use the member-local default for code-adjacent knowledge;
3. prefer a canonical source over a generated or cached view;
4. treat observed runtime state as evidence, not automatic authority over
   desired policy; and
5. if two authorities remain equal, report `semantic` or `governance` drift and
   require the configured arbiter.

"Latest commit wins" is not a valid authority rule.

Agent instruction precedence and knowledge authority are separate. A nearby
`AGENTS.md` can control how an agent works in a directory, but it cannot make a
local copy of an organization policy canonical.

## 15. Conformance levels

| Level | Name | Requirements |
|---|---|---|
| 0 | Discovery | Root entry point, manifest, registered members, bootstrap routing. |
| 1 | Authority | Roles, canonical scopes, review policies, conflict rule. |
| 2 | Validation | Automated OKF, federation, ownership, link, and freshness checks. |
| 3 | Reconciliation | Drift reports, proposal workflow, and coordinated change records. |

Claims use the form `OKF Federation 0.1 Level N`. A Level N implementation
**MUST** satisfy every lower level. Because `0.1` is a draft, conformance claims
SHOULD also identify the exact specification commit.

## 16. Security and privacy

Knowledge repositories can contain operationally powerful instructions and are
a prompt-injection and supply-chain boundary.

Implementations **MUST**:

- apply repository access controls before serving knowledge;
- never treat an external member as trusted merely because it is registered;
- keep credentials and secret values outside bundles;
- preserve source and actor attribution;
- prevent an agent from fabricating approval or verification identities; and
- make destructive or externally visible reconciliation subject to explicit
  authorization.

Implementations SHOULD pin third-party members by immutable revision for
sensitive use, scan contributions for secret-like values, and expose whether
retrieved content is canonical, candidate, stale, or unverified.

## 17. Extensibility and compatibility

Organizations MAY add manifest keys under an extension namespace. Consumers
**MUST** preserve unknown keys when round-tripping and SHOULD ignore extensions
they do not understand unless the manifest marks one as required.

MCP servers, software catalogs, search services, and graph databases MAY expose
or index a federation. Their stored state is derived unless the manifest
explicitly registers it as a canonical member.

## 18. Versioning

The specification uses `<major>.<minor>` versions. A minor release adds
backward-compatible optional behavior. A major release may change required
manifest fields or conformance behavior.

Until `1.0`, minor releases MAY contain breaking changes. Draft implementations
SHOULD pin the specification commit and expose it in validation output.
