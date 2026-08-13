#!/usr/bin/env python3
"""Validate one OKF member bundle without requiring a federation manifest."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from validate import Report, validate_bundle


def validate_member_bundle(
    bundle: Path,
    member: str,
    entrypoint: Path,
) -> tuple[Report, int]:
    report = Report()
    resolved_bundle = bundle.resolve()
    if not resolved_bundle.is_dir():
        report.add(
            "MEMBER_BUNDLE_MISSING",
            "error",
            f"Member bundle is not present: {resolved_bundle}",
            member,
        )
        return report, 0

    resolved_entrypoint = (resolved_bundle / entrypoint).resolve()
    try:
        resolved_entrypoint.relative_to(resolved_bundle)
    except ValueError:
        report.add(
            "MEMBER_ENTRYPOINT_ESCAPE",
            "error",
            f"Member entrypoint escapes its bundle: {entrypoint}",
            member,
        )
        return report, 0

    if not resolved_entrypoint.is_file():
        report.add(
            "MEMBER_ENTRYPOINT_MISSING",
            "error",
            f"Member entrypoint is not present: {resolved_entrypoint}",
            member,
        )
        return report, 0

    concepts = validate_bundle({"id": member}, resolved_bundle, report)
    return report, len(concepts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Path to the OKF member bundle")
    parser.add_argument("--member", default="local-member", help="Member ID used in findings")
    parser.add_argument(
        "--entrypoint",
        type=Path,
        default=Path("index.md"),
        help="Entrypoint path relative to the bundle",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    report, concept_count = validate_member_bundle(
        arguments.bundle,
        arguments.member,
        arguments.entrypoint,
    )
    summary = {
        "errors": len(report.errors),
        "warnings": sum(item.severity == "warning" for item in report.findings),
        "info": sum(item.severity == "info" for item in report.findings),
    }

    if arguments.format == "json":
        print(
            json.dumps(
                {
                    "specification": "OKF Federation 0.1-draft",
                    "bundle": str(arguments.bundle.resolve()),
                    "member": arguments.member,
                    "entrypoint": str(arguments.entrypoint),
                    "valid": not report.errors,
                    "concepts": concept_count,
                    "summary": summary,
                    "findings": [asdict(item) for item in report.findings],
                },
                indent=2,
            )
        )
    else:
        for finding in report.findings:
            location = ":".join(part for part in (finding.member, finding.path) if part)
            suffix = f" [{location}]" if location else ""
            print(f"{finding.severity.upper()} {finding.code}{suffix}: {finding.message}")
        state = "valid" if not report.errors else "invalid"
        print(
            f"Bundle {state}: {concept_count} concept(s), {summary['errors']} error(s), "
            f"{summary['warnings']} warning(s), {summary['info']} info finding(s)."
        )

    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
