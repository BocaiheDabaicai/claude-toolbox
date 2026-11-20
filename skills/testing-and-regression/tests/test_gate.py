from __future__ import annotations

import io
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "scripts"),
)

import gate  # noqa: E402


def write_config(directory: Path, checks: str) -> Path:
    path = directory / "gate.toml"
    path.write_text(
        f"""
[project]
name = "test-project"
report = "docs/report.md"

{checks}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return path


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        status = 200 if self.path == "/ok" else 503
        self.send_response(status)
        self.end_headers()
        self.wfile.write(b"ok" if status == 200 else b"down")

    def log_message(self, *args) -> None:
        return None


class GateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_command_pass_and_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ok_script = root / "ok.py"
            ok_script.write_text("print('ok')\n", encoding="utf-8")
            fail_script = root / "fail.py"
            fail_script.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
            config = write_config(
                root,
                f"""
[[checks]]
name = "ok"
type = "command"
command = '{sys.executable} "{ok_script}"'

[[checks]]
name = "fail"
type = "command"
command = '{sys.executable} "{fail_script}"'
""",
            )
            loaded = gate.load_config(config)
            results = gate.run_gate(loaded)
            self.assertEqual([item.passed for item in results], [True, False])

    def test_http_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = write_config(
                root,
                f"""
[[checks]]
name = "ok"
type = "http"
url = "{self.base_url}/ok"
expect_status = 200

[[checks]]
name = "down"
type = "http"
url = "{self.base_url}/down"
expect_status = 200
""",
            )
            loaded = gate.load_config(config)
            results = gate.run_gate(loaded)
            self.assertEqual([item.passed for item in results], [True, False])

    def test_file_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            present = root / "present.txt"
            present.write_text("ok", encoding="utf-8")
            config = write_config(
                root,
                f"""
[[checks]]
name = "present"
type = "file"
path = "{present.as_posix()}"

[[checks]]
name = "missing"
type = "file"
path = "{(root / 'missing.txt').as_posix()}"
""",
            )
            loaded = gate.load_config(config)
            results = gate.run_gate(loaded)
            self.assertEqual([item.passed for item in results], [True, False])

    def test_dry_run_does_not_execute(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = write_config(
                root,
                """
[[checks]]
name = "would-fail"
type = "command"
command = "exit 1"
""",
            )
            loaded = gate.load_config(config)
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(io.StringIO()):
                code = gate.main(
                    [
                        "--config",
                        str(config),
                        "--dry-run",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("[DRY]", output.getvalue())

    def test_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = write_config(
                root,
                f"""
[[checks]]
name = "ok"
type = "http"
url = "{self.base_url}/ok"
""",
            )
            loaded = gate.load_config(config)
            results = gate.run_gate(loaded)
            report = gate.format_report(loaded, results)
            self.assertIn("回归门禁报告", report)
            self.assertIn("PASS", report)

    def test_missing_env(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = write_config(
                root,
                """
[[checks]]
name = "env"
type = "http"
url = "${MISSING_GATE_URL}"
""",
            )
            with self.assertRaises(gate.GateError):
                gate.load_config(config)

    def test_cli_list(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = write_config(
                root,
                f"""
[[checks]]
name = "ok"
type = "http"
url = "{self.base_url}/ok"
""",
            )
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(io.StringIO()):
                code = gate.main(["--config", str(config), "--list"])
            self.assertEqual(code, 0)
            self.assertIn("http", output.getvalue())


if __name__ == "__main__":
    unittest.main()
