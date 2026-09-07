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


class HookEfficiencyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        memory = self.root / ".memory"
        runtime = memory / "runtime"
        wiki = self.root / "docs" / "wiki"
        runtime.mkdir(parents=True)
        wiki.mkdir(parents=True)
        (memory / "MEMORY.md").write_text("# Current\nAgent infra v3\n", encoding="utf-8")
        (memory / "TASKS.md").write_text("# Tasks\n测试 hooks\n", encoding="utf-8")
        (memory / "LEARNING.md").write_text("# Learnings\n", encoding="utf-8")
        (memory / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
        (self.root / "docs" / "ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")
        (wiki / "README.md").write_text("# Wiki\n", encoding="utf-8")
        (memory / "config.json").write_text(
            json.dumps(
                {
                    "version": 3,
                    "retrieval": {"enabled": True, "max_results": 2, "max_chars": 800, "min_token_overlap": 2},
                    "runtime": {
                        "max_record_chars": 4000,
                        "max_observation_chars": 300,
                        "max_file_bytes": 1048576,
                        "dedupe_cache_size": 64,
                    },
                    "promotion": {"build_queue_on_stop": True, "batch_size": 25, "min_queue_confidence": 0.45},
                }
            ),
            encoding="utf-8",
        )
        self.runtime = runtime
        self.env = os.environ.copy()
        self.env["CLAUDE_PROJECT_DIR"] = str(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_hook(self, name: str, payload: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HOOKS / name)],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            env=self.env,
            check=True,
        )

    def test_ordinary_prompt_is_not_persisted_as_candidate(self) -> None:
        self.run_hook("user-prompt.py", {"prompt": "帮我解释一下这段代码", "session_id": "s1"})
        self.assertFalse((self.runtime / "candidates.jsonl").exists())

    def test_high_signal_prompt_is_persisted(self) -> None:
        self.run_hook("user-prompt.py", {"prompt": "最终决定采用 PostgreSQL", "session_id": "s1"})
        text = (self.runtime / "candidates.jsonl").read_text(encoding="utf-8")
        self.assertIn("PostgreSQL", text)

    def test_write_observation_does_not_store_file_content_or_create_candidate(self) -> None:
        secret_body = "very-large-body-" * 100
        self.run_hook(
            "post-tool.py",
            {
                "tool_name": "Write",
                "tool_input": {"file_path": "src/app.py", "content": secret_body},
                "tool_response": {"ok": True},
                "session_id": "s1",
            },
        )
        observation = (self.runtime / "observations.jsonl").read_text(encoding="utf-8")
        self.assertIn("src/app.py", observation)
        self.assertNotIn(secret_body[:50], observation)
        self.assertFalse((self.runtime / "candidates.jsonl").exists())

    def test_pretool_uses_tiered_permission_decisions(self) -> None:
        denied = self.run_hook("pre-tool.py", {"tool_input": {"command": "rm -rf /"}})
        self.assertEqual(json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

        asked = self.run_hook("pre-tool.py", {"tool_input": {"command": "git reset --hard HEAD~1"}})
        self.assertEqual(json.loads(asked.stdout)["hookSpecificOutput"]["permissionDecision"], "ask")

        safe = self.run_hook("pre-tool.py", {"tool_input": {"command": "git status"}})
        self.assertTrue(json.loads(safe.stdout)["continue"])

    def test_stop_builds_queue_incrementally(self) -> None:
        self.run_hook("user-prompt.py", {"prompt": "确认下一步实现登录模块", "session_id": "s1"})
        self.run_hook("stop.py", {"session_id": "s1"})
        first = (self.runtime / "promotion-queue.jsonl").read_text(encoding="utf-8")
        self.run_hook("stop.py", {"session_id": "s1"})
        second = (self.runtime / "promotion-queue.jsonl").read_text(encoding="utf-8")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
