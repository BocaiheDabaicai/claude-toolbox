from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = SKILL_ROOT / "scripts" / "scaffold.py"
LINT = SKILL_ROOT / "scripts" / "feature_lint.py"


class ScaffoldTest(unittest.TestCase):
    def test_scaffold_creates_docs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "demo-project"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCAFFOLD),
                    str(target),
                    "--name",
                    "demo-project",
                    "--title",
                    "演示项目",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            docs = target / "docs"
            for name in (
                "brief.md",
                "features.csv",
                "glossary.md",
                "roadmap.md",
                "acceptance.md",
                "handoff.md",
            ):
                self.assertTrue((docs / name).is_file(), name)

            brief = (docs / "brief.md").read_text(encoding="utf-8")
            self.assertIn("演示项目", brief)
            self.assertNotIn("__PROJECT_TITLE__", brief)

            lint = subprocess.run(
                [sys.executable, str(LINT), str(docs / "features.csv")],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)


if __name__ == "__main__":
    unittest.main()
