from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".claude" / "hooks"
STOP_HOOK = HOOKS / "stop.py"
FAILURE_HOOK = HOOKS / "post-tool-failure.py"


class CompletionGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        runtime = self.root / ".memory" / "runtime"
        runtime.mkdir(parents=True)
        (self.root / ".memory" / "config.json").write_text(
            json.dumps(
                {
                    "runtime": {"max_observation_chars": 1600, "max_file_bytes": 1048576},
                    "promotion": {"build_queue_on_stop": False},
                }
            ),
            encoding="utf-8",
        )
        self.runtime = runtime
        self.env = os.environ.copy()
        self.env["CLAUDE_PROJECT_DIR"] = str(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_observations(self, items: list[dict]) -> None:
        path = self.runtime / "observations.jsonl"
        path.write_text(
            "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in items),
            encoding="utf-8",
        )

    def run_hook(self, path: Path, payload: dict) -> dict:
        completed = subprocess.run(
            [sys.executable, str(path)],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            env=self.env,
            check=True,
        )
        return json.loads(completed.stdout)

    def run_stop(self, session_id: str = "s1") -> dict:
        return self.run_hook(STOP_HOOK, {"session_id": session_id})

    def test_code_change_without_verification_is_blocked(self) -> None:
        self.write_observations(
            [{"tool_name": "Edit", "path": "src/app.py", "status": "ok", "session_id": "s1"}]
        )
        result = self.run_stop()
        self.assertEqual(result["decision"], "block")
        self.assertIn("no relevant verification", result["reason"])

    def test_successful_verification_after_change_allows_stop(self) -> None:
        self.write_observations(
            [
                {"tool_name": "Edit", "path": "src/app.py", "status": "ok", "session_id": "s1"},
                {"tool_name": "Bash", "command": "pytest tests/test_app.py", "status": "ok", "session_id": "s1"},
            ]
        )
        result = self.run_stop()
        self.assertTrue(result["continue"])

    def test_failed_verification_blocks_repair_loop(self) -> None:
        self.write_observations(
            [{"tool_name": "Write", "path": "src/app.py", "status": "ok", "session_id": "s1"}]
        )
        self.run_hook(
            FAILURE_HOOK,
            {
                "hook_event_name": "PostToolUseFailure",
                "tool_name": "Bash",
                "tool_input": {"command": "python -m unittest"},
                "error": "FAILED test_login",
                "session_id": "s1",
            },
        )
        result = self.run_stop()
        self.assertEqual(result["decision"], "block")
        self.assertIn("latest verification failed", result["reason"])
        self.assertIn("FAILED test_login", result["reason"])

    def test_failure_hook_accepts_tool_result_fallback(self) -> None:
        self.run_hook(
            FAILURE_HOOK,
            {
                "tool_name": "Bash",
                "tool_input": {"command": "pytest"},
                "tool_result": {"stderr": "1 failed"},
                "session_id": "s1",
            },
        )
        text = (self.runtime / "observations.jsonl").read_text(encoding="utf-8")
        self.assertIn('"status": "error"', text)
        self.assertIn("1 failed", text)

    def test_verification_before_latest_change_does_not_count(self) -> None:
        self.write_observations(
            [
                {"tool_name": "Bash", "command": "npm test", "status": "ok", "session_id": "s1"},
                {"tool_name": "Edit", "path": "src/app.ts", "status": "ok", "session_id": "s1"},
            ]
        )
        result = self.run_stop()
        self.assertEqual(result["decision"], "block")

    def test_documentation_only_change_does_not_require_code_test(self) -> None:
        self.write_observations(
            [{"tool_name": "Edit", "path": "README.md", "status": "ok", "session_id": "s1"}]
        )
        result = self.run_stop()
        self.assertTrue(result["continue"])

    def test_other_session_does_not_affect_current_session(self) -> None:
        self.write_observations(
            [{"tool_name": "Edit", "path": "src/app.py", "status": "ok", "session_id": "other"}]
        )
        result = self.run_stop("s1")
        self.assertTrue(result["continue"])

    def test_settings_include_semantic_and_failure_gates(self) -> None:
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        stop_hooks = settings["hooks"]["Stop"][0]["hooks"]
        prompt_hooks = [item for item in stop_hooks if item.get("type") == "prompt"]
        self.assertEqual(len(prompt_hooks), 1)
        self.assertIn("semantic completion gate", prompt_hooks[0]["prompt"])

        failure = settings["hooks"]["PostToolUseFailure"][0]
        self.assertEqual(failure["matcher"], "Bash")
        self.assertIn("post-tool-failure.py", failure["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
