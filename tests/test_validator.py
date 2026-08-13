from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate.py"
BUNDLE_VALIDATOR = ROOT / "scripts/validate_bundle.py"
VALID_MANIFEST = ROOT / "examples/minimal/workspace/home/federation.yaml"
WORKSPACE = ROOT / "examples/minimal/workspace"
INVALID_AUTHORITY = ROOT / "conformance/fixtures/invalid-duplicate-authority/federation.yaml"


class ValidatorTests(unittest.TestCase):
    def run_validator(self, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), *(str(argument) for argument in arguments)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_bundle_validator(self, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(BUNDLE_VALIDATOR), *(str(argument) for argument in arguments)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_minimal_federation_is_valid(self) -> None:
        result = self.run_validator(
            VALID_MANIFEST,
            "--workspace",
            WORKSPACE,
            "--today",
            date(2026, 8, 13),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Federation valid", result.stdout)

    def test_duplicate_authority_scope_is_rejected(self) -> None:
        result = self.run_validator(INVALID_AUTHORITY, "--manifest-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AUTHORITY_SCOPE_ID_DUPLICATE", result.stdout)
        self.assertIn("AUTHORITY_SCOPE_CONFLICT", result.stdout)
        self.assertIn("AUTHORITY_MEMBER_UNKNOWN", result.stdout)

    def test_broken_local_link_is_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            shutil.copytree(WORKSPACE, workspace)
            entrypoint = workspace / "service-a" / "index.md"
            entrypoint.write_text(
                entrypoint.read_text(encoding="utf-8")
                + "\n- [Planned documentation](planned.md)\n",
                encoding="utf-8",
            )
            result = self.run_validator(
                workspace / "home" / "federation.yaml",
                "--workspace",
                workspace,
                "--today",
                date(2026, 8, 13),
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("WARNING LINK_BROKEN", result.stdout)

    def test_json_output_has_stable_envelope(self) -> None:
        result = self.run_validator(
            VALID_MANIFEST,
            "--workspace",
            WORKSPACE,
            "--today",
            date(2026, 8, 13),
            "--format",
            "json",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["specification"], "OKF Federation 0.1-draft")
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["errors"], 0)

    def test_member_bundle_can_be_validated_without_a_manifest(self) -> None:
        result = self.run_bundle_validator(
            WORKSPACE / "service-a",
            "--member",
            "service-a",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Bundle valid", result.stdout)

    def test_member_bundle_requires_its_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "knowledge"
            bundle.mkdir()
            result = self.run_bundle_validator(bundle, "--member", "service-a")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MEMBER_ENTRYPOINT_MISSING", result.stdout)

    def test_member_bundle_rejects_a_link_that_escapes_the_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "knowledge"
            shutil.copytree(WORKSPACE / "service-a", bundle)
            (bundle / "details.md").write_text(
                """---
type: Reference
title: Escaping link fixture
description: Exercises the member bundle boundary.
status: draft
generated: { by: process:test, at: 2026-08-13T00:00:00Z }
---

[Outside](../outside.md)
""",
                encoding="utf-8",
            )
            result = self.run_bundle_validator(bundle, "--member", "service-a")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("LINK_ESCAPES_BUNDLE", result.stdout)


if __name__ == "__main__":
    unittest.main()
