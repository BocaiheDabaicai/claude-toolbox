from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "scripts"),
)

import feature_lint  # noqa: E402


def make_row(**overrides: str) -> dict[str, str]:
    row = {
        "id": "F-001",
        "module": "登录",
        "feature": "管理员登录",
        "description": "邮箱 + 密码登录",
        "priority": "P0",
        "status": "accepted",
        "owner": "张三",
        "acceptance": "正确账号可登录",
        "dependencies": "",
        "notes": "",
        "updated": "2026-11-20",
    }
    row.update(overrides)
    return row


def errors(issues: list[feature_lint.Issue]) -> list[feature_lint.Issue]:
    return [issue for issue in issues if issue.level == "error"]


class FeatureLintTest(unittest.TestCase):
    def test_valid_row(self) -> None:
        issues = feature_lint.lint_rows([make_row()])
        self.assertEqual(errors(issues), [])

    def test_duplicate_id(self) -> None:
        issues = feature_lint.lint_rows(
            [make_row(), make_row(feature="另一个功能")]
        )
        self.assertTrue(any("重复" in issue.message for issue in errors(issues)))

    def test_invalid_status(self) -> None:
        issues = feature_lint.lint_rows([make_row(status="doing")])
        self.assertTrue(any("status" in issue.message for issue in errors(issues)))

    def test_missing_dependency(self) -> None:
        issues = feature_lint.lint_rows([make_row(dependencies="F-999")])
        self.assertTrue(any("依赖不存在" in issue.message for issue in errors(issues)))

    def test_self_dependency(self) -> None:
        issues = feature_lint.lint_rows([make_row(dependencies="F-001")])
        self.assertTrue(any("不能依赖自己" in issue.message for issue in errors(issues)))

    def test_accepted_requires_acceptance(self) -> None:
        issues = feature_lint.lint_rows([make_row(acceptance="")])
        self.assertTrue(any("acceptance" in issue.message for issue in errors(issues)))

    def test_in_progress_requires_owner(self) -> None:
        issues = feature_lint.lint_rows(
            [make_row(status="in-progress", owner="")]
        )
        self.assertTrue(any("owner" in issue.message for issue in errors(issues)))

    def test_summary(self) -> None:
        summary = feature_lint.summarize(
            [
                make_row(),
                make_row(id="F-002", status="idea", priority="P2"),
            ]
        )
        self.assertIn("features: 2", summary)
        self.assertIn("accepted=1", summary)
        self.assertIn("P2=1", summary)

    def test_cli_ok(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "features.csv"
            path.write_text(
                ",".join(feature_lint.REQUIRED_COLUMNS)
                + "\n"
                + "F-001,登录,管理员登录,邮箱登录,P0,accepted,张三,可登录,,,2026-11-20\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(io.StringIO()):
                code = feature_lint.main([str(path), "--strict"])
            self.assertEqual(code, 0)
            self.assertIn("features: 1", output.getvalue())

    def test_cli_bad_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "features.csv"
            path.write_text("id,module\nF-001,登录\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = feature_lint.main([str(path)])
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
