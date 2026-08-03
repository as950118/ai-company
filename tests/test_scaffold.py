"""Smoke tests for the company-os-cli scaffolder.

Run with: python3 -m unittest discover -s tests -v
Works whether the package is `pip install -e .`-ed or not (src/ is added
to sys.path below), but does require `typer` for the CLI-level tests
(it's a mandatory runtime dependency of the package anyway).
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from company_os_cli.scaffold import ScaffoldError, scaffold  # noqa: E402

TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
IGNORE_LEFTOVER = {"{{TITLE}}", "{{NNNN}}"}


def _find_leftovers(root: Path) -> list[str]:
    leftovers: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in TOKEN_RE.findall(text):
            if token not in IGNORE_LEFTOVER:
                leftovers.append(f"{path.relative_to(root)}: {token}")
    return leftovers


class ScaffoldFunctionTests(unittest.TestCase):
    """Exercise company_os_cli.scaffold.scaffold() directly."""

    def test_scaffold_creates_expected_layout(self) -> None:
        out_dir = self._tmp_dir()
        result = scaffold(
            name="Acme Agent Co",
            product="Acme Task Hub",
            slug="acme-task-hub",
            out=out_dir,
        )

        self.assertEqual(result.leftover, [])
        self.assertTrue((out_dir / "README.md").is_file())
        self.assertFalse((out_dir / "TEMPLATE_README.md").exists())

        self.assertTrue((out_dir / "projects" / "acme-task-hub").is_dir())
        self.assertFalse((out_dir / "projects" / "_starter").exists())

        for expected in [
            "company/vision.md",
            "roles/pm.md",
            "agents/frontend.yaml",
            "agents/devops.yaml",
            "agents/technical-writer.yaml",
            "skills/write-architecture.md",
            "workflows/create-feature.md",
            "langgraph/feature-graph.md",
            "runtime/pyproject.toml",
        ]:
            self.assertTrue((out_dir / expected).is_file(), msg=f"missing {expected}")

    def test_scaffold_resolves_all_placeholders(self) -> None:
        out_dir = self._tmp_dir()
        scaffold(name="Acme Agent Co", product="Acme Task Hub", out=out_dir)

        leftovers = _find_leftovers(out_dir)
        self.assertEqual(leftovers, [], msg="Unresolved placeholders:\n" + "\n".join(leftovers))

    def test_refuses_non_empty_dir_without_force(self) -> None:
        out_dir = self._tmp_dir()
        (out_dir / "keep.txt").write_text("existing file")

        with self.assertRaises(ScaffoldError):
            scaffold(name="Acme", product="Acme App", out=out_dir)

    def test_force_allows_non_empty_dir(self) -> None:
        out_dir = self._tmp_dir()
        (out_dir / "keep.txt").write_text("existing file")

        result = scaffold(name="Acme", product="Acme App", out=out_dir, force=True)
        self.assertTrue((out_dir / "keep.txt").exists())
        self.assertTrue((out_dir / "README.md").exists())
        self.assertEqual(result.leftover, [])

    def _tmp_dir(self) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="company-os-test-"))
        self.addCleanup(self._cleanup, tmp)
        return tmp

    @staticmethod
    def _cleanup(path: Path) -> None:
        import shutil

        shutil.rmtree(path, ignore_errors=True)


class CliSmokeTests(unittest.TestCase):
    """Exercise the installed `company-os` console entry via `python -m`."""

    def _run_cli(self, *args: str) -> subprocess.CompletedProcess:
        import os

        env = {**os.environ, "PYTHONPATH": str(SRC_ROOT)}
        return subprocess.run(
            [sys.executable, "-m", "company_os_cli.cli", *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_version_flag(self) -> None:
        result = self._run_cli("--version")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("company-os-cli", result.stdout)

    def test_init_end_to_end(self) -> None:
        out_dir = Path(tempfile.mkdtemp(prefix="company-os-cli-test-"))
        try:
            result = self._run_cli(
                "init",
                "--name",
                "Acme Agent Co",
                "--product",
                "Acme Task Hub",
                "--slug",
                "acme-task-hub",
                "--out",
                str(out_dir),
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue((out_dir / "company" / "vision.md").is_file())
            self.assertIn("Scaffolded Company OS", result.stdout)
        finally:
            import shutil

            shutil.rmtree(out_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
