#!/usr/bin/env python3
"""Reference structural validator for OKF Federation 0.1-draft."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable
from urllib.parse import unquote, urlparse

from jsonschema import Draft202012Validator, FormatChecker
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = PROJECT_ROOT / "schemas/federation.schema.json"
RESERVED_MARKDOWN = {"index.md", "log.md"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
ISO_LOG_HEADING = re.compile(r"^## \d{4}-\d{2}-\d{2}$", re.MULTILINE)
DURATION_DAYS = re.compile(r"^([1-9][0-9]*)d$")


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    member: str | None = None
    path: str | None = None


class Report:
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def add(
        self,
        code: str,
        severity: str,
        message: str,
        member: str | None = None,
        path: str | None = None,
    ) -> None:
        self.findings.append(Finding(code, severity, message, member, path))

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "error"]

    def as_json(self, manifest: Path) -> dict[str, Any]:
        return {
            "specification": "OKF Federation 0.1-draft",
            "manifest": str(manifest),
            "valid": not self.errors,
            "summary": {
                "errors": len(self.errors),
                "warnings": sum(item.severity == "warning" for item in self.findings),
                "info": sum(item.severity == "info" for item in self.findings),
            },
            "findings": [asdict(item) for item in self.findings],
        }


@dataclass(frozen=True)
class Concept:
    member: str
    path: Path
    relative: Path
    metadata: dict[str, Any]
    text: str


def load_yaml_mapping(path: Path, report: Report, code: str) -> dict[str, Any] | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exception:
        report.add(code, "error", f"Cannot parse YAML: {exception}", path=str(path))
        return None
    if not isinstance(value, dict):
        report.add(code, "error", "YAML document must be a mapping", path=str(path))
        return None
    return value


def validate_schema(manifest: dict[str, Any], schema_path: Path, report: Report) -> None:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        report.add("SCHEMA_UNAVAILABLE", "error", f"Cannot read schema: {exception}", path=str(schema_path))
        return

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        report.add("MANIFEST_SCHEMA", "error", f"{location}: {error.message}")


def duplicate_values(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_manifest_semantics(manifest: dict[str, Any], report: Report) -> None:
    members = manifest.get("members")
    if not isinstance(members, list):
        return

    member_ids = [member.get("id") for member in members if isinstance(member, dict) and isinstance(member.get("id"), str)]
    for duplicate in sorted(duplicate_values(member_ids)):
        report.add("MEMBER_ID_DUPLICATE", "error", f"Member ID is declared more than once: {duplicate}")

    root = manifest.get("root")
    if isinstance(root, str) and root not in member_ids:
        report.add("ROOT_MEMBER_UNKNOWN", "error", f"Root member is not registered: {root}")

    roles = manifest.get("roles") if isinstance(manifest.get("roles"), dict) else {}
    authority = manifest.get("authority") if isinstance(manifest.get("authority"), dict) else {}
    scopes = authority.get("canonical_scopes") if isinstance(authority.get("canonical_scopes"), list) else []
    scope_ids = [scope.get("id") for scope in scopes if isinstance(scope, dict) and isinstance(scope.get("id"), str)]
    for duplicate in sorted(duplicate_values(scope_ids)):
        report.add(
            "AUTHORITY_SCOPE_ID_DUPLICATE",
            "error",
            f"Canonical scope ID is declared more than once: {duplicate}",
        )

    for scope in scopes:
        if not isinstance(scope, dict):
            continue
        owner = scope.get("member")
        if isinstance(owner, str) and owner not in member_ids and owner != "$matched-member":
            report.add(
                "AUTHORITY_MEMBER_UNKNOWN",
                "error",
                f"Canonical scope {scope.get('id', '<unknown>')} names an unknown member: {owner}",
            )

    selectors: dict[tuple[tuple[str, ...], tuple[str, ...]], dict[str, Any]] = {}
    for scope in scopes:
        if not isinstance(scope, dict):
            continue
        paths = scope.get("paths") if isinstance(scope.get("paths"), list) else []
        types = scope.get("types") if isinstance(scope.get("types"), list) else []
        selector = (tuple(sorted(str(value) for value in paths)), tuple(sorted(str(value) for value in types)))
        previous = selectors.get(selector)
        if previous is not None and previous.get("member") != scope.get("member"):
            report.add(
                "AUTHORITY_SCOPE_CONFLICT",
                "error",
                (
                    f"Canonical scopes {previous.get('id', '<unknown>')} and "
                    f"{scope.get('id', '<unknown>')} assign the same selector to different members"
                ),
            )
        else:
            selectors[selector] = scope

    arbiter = authority.get("arbiter_role")
    if isinstance(arbiter, str) and arbiter not in roles:
        report.add("ARBITER_ROLE_UNKNOWN", "error", f"Arbiter role is not declared: {arbiter}")

    review = manifest.get("review_policies") if isinstance(manifest.get("review_policies"), dict) else {}
    rules = review.get("rules") if isinstance(review.get("rules"), list) else []
    rule_ids = [rule.get("id") for rule in rules if isinstance(rule, dict) and isinstance(rule.get("id"), str)]
    for duplicate in sorted(duplicate_values(rule_ids)):
        report.add("REVIEW_RULE_ID_DUPLICATE", "error", f"Review rule ID is declared more than once: {duplicate}")
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        for approval in rule.get("approvals", []):
            if isinstance(approval, dict) and isinstance(approval.get("role"), str) and approval["role"] not in roles:
                report.add(
                    "REVIEW_ROLE_UNKNOWN",
                    "error",
                    f"Review rule {rule.get('id', '<unknown>')} names an unknown role: {approval['role']}",
                )


def parse_frontmatter(path: Path, text: str, member: str, report: Report) -> dict[str, Any] | None:
    if not text.startswith("---\n"):
        report.add("OKF_FRONTMATTER_MISSING", "error", "Concept has no YAML frontmatter", member, str(path))
        return None
    parts = text.split("---", 2)
    if len(parts) != 3:
        report.add("OKF_FRONTMATTER_INVALID", "error", "Concept frontmatter is not closed", member, str(path))
        return None
    try:
        metadata = yaml.safe_load(parts[1])
    except yaml.YAMLError as exception:
        report.add("OKF_FRONTMATTER_INVALID", "error", f"Invalid YAML frontmatter: {exception}", member, str(path))
        return None
    if not isinstance(metadata, dict):
        report.add("OKF_FRONTMATTER_INVALID", "error", "Concept frontmatter must be a mapping", member, str(path))
        return None
    if not isinstance(metadata.get("type"), str) or not metadata["type"].strip():
        report.add("OKF_TYPE_MISSING", "error", "Concept has no non-empty type", member, str(path))
    return metadata


def link_target(source: Path, bundle: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or target.startswith("#"):
        return None
    clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not clean:
        return None
    candidate = bundle / clean.lstrip("/") if clean.startswith("/") else source.parent / clean
    return candidate


def validate_local_links(path: Path, text: str, bundle: Path, member: str, report: Report) -> None:
    bundle_resolved = bundle.resolve()
    for raw_target in MARKDOWN_LINK.findall(text):
        target = link_target(path, bundle, raw_target)
        if target is None:
            continue
        resolved = target.resolve()
        try:
            resolved.relative_to(bundle_resolved)
        except ValueError:
            report.add(
                "LINK_ESCAPES_BUNDLE",
                "error",
                f"Local link escapes the member bundle: {raw_target}",
                member,
                str(path.relative_to(bundle)),
            )
            continue
        if resolved.is_dir():
            resolved = resolved / "index.md"
        if not resolved.exists():
            report.add(
                "LINK_BROKEN",
                "warning",
                f"Local link target does not exist: {raw_target}",
                member,
                str(path.relative_to(bundle)),
            )


def validate_bundle(member: dict[str, Any], bundle: Path, report: Report) -> list[Concept]:
    member_id = str(member.get("id", "<unknown>"))
    concepts: list[Concept] = []
    for path in sorted(bundle.rglob("*.md")):
        if ".git" in path.parts:
            continue
        relative = path.relative_to(bundle)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exception:
            report.add("MARKDOWN_UNREADABLE", "error", str(exception), member_id, str(relative))
            continue
        if path.name in RESERVED_MARKDOWN:
            if path.name == "log.md" and not ISO_LOG_HEADING.search(text):
                report.add("OKF_LOG_DATE_MISSING", "error", "log.md has no ISO date heading", member_id, str(relative))
        else:
            metadata = parse_frontmatter(relative, text, member_id, report)
            if metadata is not None:
                concepts.append(Concept(member_id, path, relative, metadata, text))
        validate_local_links(path, text, bundle, member_id, report)
    return concepts


def parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def trust_tier(verified: Any) -> tuple[int, datetime | None]:
    events = verified if isinstance(verified, list) else [verified] if isinstance(verified, dict) else []
    tier = 0
    latest: datetime | None = None
    for event in events:
        if not isinstance(event, dict):
            continue
        actor = event.get("by")
        if isinstance(actor, str):
            tier = max(tier, 2 if actor.startswith("human:") else 1)
        timestamp = parse_datetime(event.get("at"))
        if timestamp is not None and (latest is None or timestamp > latest):
            latest = timestamp
    return tier, latest


def concept_matches(concept: Concept, match: dict[str, Any]) -> bool:
    members = match.get("members")
    if isinstance(members, list) and concept.member not in members and "*" not in members:
        return False
    types = match.get("types")
    if isinstance(types, list) and concept.metadata.get("type") not in types:
        return False
    tags = match.get("tags")
    concept_tags = concept.metadata.get("tags") if isinstance(concept.metadata.get("tags"), list) else []
    if isinstance(tags, list) and not set(tags).intersection(concept_tags):
        return False
    paths = match.get("paths")
    if isinstance(paths, list):
        from fnmatch import fnmatch

        if not any(fnmatch(str(concept.relative), pattern) for pattern in paths):
            return False
    return True


def validate_freshness(manifest: dict[str, Any], concepts: list[Concept], report: Report, today: date) -> None:
    policies = manifest.get("freshness_policies")
    if not isinstance(policies, list):
        return
    trust_names = {"unverified": 0, "machine-confirmed": 1, "human-reviewed": 2}
    for policy in policies:
        if not isinstance(policy, dict) or not isinstance(policy.get("match"), dict):
            continue
        for concept in concepts:
            if not concept_matches(concept, policy["match"]):
                continue
            severity = policy.get("stale_severity", "warning")
            stale_after = parse_date(concept.metadata.get("stale_after"))
            if policy.get("require_stale_after") and stale_after is None:
                report.add(
                    "FRESHNESS_STALE_AFTER_MISSING",
                    severity,
                    f"Freshness policy {policy.get('id')} requires stale_after",
                    concept.member,
                    str(concept.relative),
                )
            if stale_after is not None and today >= stale_after:
                report.add(
                    "FRESHNESS_STALE",
                    severity,
                    f"Concept became stale on {stale_after.isoformat()}",
                    concept.member,
                    str(concept.relative),
                )
            tier, latest = trust_tier(concept.metadata.get("verified"))
            required_tier = trust_names.get(policy.get("minimum_trust", "unverified"), 0)
            if tier < required_tier:
                report.add(
                    "FRESHNESS_TRUST_INSUFFICIENT",
                    severity,
                    f"Freshness policy {policy.get('id')} requires {policy.get('minimum_trust')}",
                    concept.member,
                    str(concept.relative),
                )
            duration = policy.get("maximum_verification_age")
            match = DURATION_DAYS.match(duration) if isinstance(duration, str) else None
            if match:
                if latest is None or latest.date() + timedelta(days=int(match.group(1))) <= today:
                    report.add(
                        "FRESHNESS_VERIFICATION_OLD",
                        severity,
                        f"Freshness policy {policy.get('id')} requires verification within {duration}",
                        concept.member,
                        str(concept.relative),
                    )


def safe_child(workspace: Path, relative: str, report: Report, member: str) -> Path | None:
    target = (workspace / relative).resolve()
    try:
        target.relative_to(workspace.resolve())
    except ValueError:
        report.add("WORKSPACE_PATH_ESCAPE", "error", f"workspace_path escapes the workspace: {relative}", member)
        return None
    return target


def validate_workspace(
    manifest: dict[str, Any], manifest_path: Path, workspace: Path, report: Report, today: date
) -> None:
    root_id = manifest.get("root")
    members = manifest.get("members") if isinstance(manifest.get("members"), list) else []
    concepts: list[Concept] = []

    root_member = next((member for member in members if isinstance(member, dict) and member.get("id") == root_id), None)
    root_entry_hint: str | None = None
    if isinstance(root_member, dict):
        root_workspace_path = root_member.get("workspace_path")
        if isinstance(root_workspace_path, str) and isinstance(root_member.get("entrypoint"), str):
            root_entry_hint = (Path(root_workspace_path) / root_member["entrypoint"]).as_posix()

    adapters = [workspace / "AGENTS.md", workspace / "CLAUDE.md"]
    present_adapters = [path for path in adapters if path.is_file()]
    if not present_adapters:
        report.add("BOOTSTRAP_MISSING", "error", "Workspace has neither AGENTS.md nor CLAUDE.md")
    elif root_entry_hint and not any(root_entry_hint in path.read_text(encoding="utf-8") for path in present_adapters):
        report.add("BOOTSTRAP_ROOT_MISSING", "error", f"No bootstrap adapter directs agents to {root_entry_hint}")

    for member in members:
        if not isinstance(member, dict) or not isinstance(member.get("id"), str):
            continue
        member_id = member["id"]
        checkout_hint = member.get("workspace_path")
        if not isinstance(checkout_hint, str):
            severity = "error" if member.get("enforcement") == "required" else "warning"
            report.add("MEMBER_WORKSPACE_PATH_MISSING", severity, "No workspace_path is available for local validation", member_id)
            continue
        checkout = safe_child(workspace, checkout_hint, report, member_id)
        if checkout is None:
            continue
        bundle_value = member.get("bundle")
        entrypoint_value = member.get("entrypoint")
        if not isinstance(bundle_value, str) or not isinstance(entrypoint_value, str):
            continue
        bundle = safe_child(checkout, bundle_value, report, member_id)
        if bundle is None or not bundle.is_dir():
            severity = "error" if member.get("enforcement") == "required" else "warning"
            report.add("MEMBER_BUNDLE_MISSING", severity, f"Member bundle is not present: {bundle}", member_id)
            continue
        entrypoint = (bundle / entrypoint_value).resolve()
        try:
            entrypoint.relative_to(bundle.resolve())
        except ValueError:
            report.add("MEMBER_ENTRYPOINT_ESCAPE", "error", "Member entrypoint escapes its bundle", member_id)
            continue
        if not entrypoint.is_file():
            severity = "error" if member.get("enforcement") == "required" else "warning"
            report.add("MEMBER_ENTRYPOINT_MISSING", severity, f"Member entrypoint is not present: {entrypoint}", member_id)
            continue
        concepts.extend(validate_bundle(member, bundle, report))

    validate_freshness(manifest, concepts, report, today)


def validate(
    manifest_path: Path,
    schema_path: Path,
    workspace: Path | None,
    manifest_only: bool,
    today: date,
) -> Report:
    report = Report()
    manifest = load_yaml_mapping(manifest_path, report, "MANIFEST_YAML")
    if manifest is None:
        return report
    validate_schema(manifest, schema_path, report)
    validate_manifest_semantics(manifest, report)
    if not manifest_only and workspace is not None and not report.errors:
        validate_workspace(manifest, manifest_path, workspace, report, today)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to federation.yaml")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Federation JSON Schema")
    parser.add_argument("--workspace", type=Path, help="Workspace containing member checkouts")
    parser.add_argument("--manifest-only", action="store_true", help="Skip workspace and bundle validation")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(), help="Evaluation date (YYYY-MM-DD)")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    manifest_path = arguments.manifest.resolve()
    workspace = arguments.workspace.resolve() if arguments.workspace else None
    if not arguments.manifest_only and workspace is None:
        workspace = manifest_path.parent.parent
    report = validate(manifest_path, arguments.schema.resolve(), workspace, arguments.manifest_only, arguments.today)

    if arguments.format == "json":
        print(json.dumps(report.as_json(manifest_path), indent=2))
    else:
        for finding in report.findings:
            location = ":".join(part for part in (finding.member, finding.path) if part)
            suffix = f" [{location}]" if location else ""
            print(f"{finding.severity.upper()} {finding.code}{suffix}: {finding.message}")
        summary = report.as_json(manifest_path)["summary"]
        state = "valid" if not report.errors else "invalid"
        print(
            f"Federation {state}: {summary['errors']} error(s), "
            f"{summary['warnings']} warning(s), {summary['info']} info finding(s)."
        )
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
