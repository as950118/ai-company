"""Smoke tests for scaffold.py.

Run with: python3 -m unittest discover -s tests -v
(no third-party dependencies required)
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = REPO_ROOT / "scaffold.py"
TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
IGNORE_LEFTOVER = {"{{TITLE}}", "{{NNNN}}"}


def run_scaffold(out_dir: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCAFFOLD),
            "--name",
            "Acme Agent Co",
            "--product",
            "Acme Task Hub",
            "--slug",
            "acme-task-hub",
            "--out",
            str(out_dir),
            *extra_args,
        ],
        capture_output=True,
        text=True,
    )


class ScaffoldTests(unittest.TestCase):
    def test_scaffold_creates_expected_layout(self) -> None:
        with_tmp = self._tmp_dir()
        result = run_scaffold(with_tmp)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        self.assertTrue((with_tmp / "README.md").is_file())
        self.assertFalse((with_tmp / "TEMPLATE_README.md").exists())
        self.assertFalse((with_tmp / "scaffold.py").exists())
        self.assertFalse((with_tmp / "PLACEHOLDERS.md").exists())

        self.assertTrue((with_tmp / "projects" / "acme-task-hub").is_dir())
        self.assertFalse((with_tmp / "projects" / "_starter").exists())

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
            self.assertTrue((with_tmp / expected).is_file(), msg=f"missing {expected}")

    def test_scaffold_resolves_all_placeholders(self) -> None:
        out_dir = self._tmp_dir()
        result = run_scaffold(out_dir)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        leftovers: list[str] = []
        for path in out_dir.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in TOKEN_RE.findall(text):
                if token not in IGNORE_LEFTOVER:
                    leftovers.append(f"{path.relative_to(out_dir)}: {token}")

        self.assertEqual(leftovers, [], msg="Unresolved placeholders:\n" + "\n".join(leftovers))

    def test_refuses_non_empty_dir_without_force(self) -> None:
        out_dir = self._tmp_dir()
        (out_dir / "keep.txt").write_text("existing file")

        result = run_scaffold(out_dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to write", result.stderr)

    def _tmp_dir(self) -> Path:
        import tempfile

        tmp = Path(tempfile.mkdtemp(prefix="company-os-test-"))
        self.addCleanup(self._cleanup, tmp)
        return tmp

    @staticmethod
    def _cleanup(path: Path) -> None:
        import shutil

        shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
