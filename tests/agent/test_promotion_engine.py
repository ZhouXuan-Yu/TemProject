from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "hooks"
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

import memory_engine  # noqa: E402
import promotion_engine  # noqa: E402


class PromotionEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        memory_dir = root / ".memory"
        runtime_dir = memory_dir / "runtime"
        archive_dir = memory_dir / "archive"
        wiki = root / "docs" / "wiki"
        wiki.mkdir(parents=True)
        runtime_dir.mkdir(parents=True)
        archive_dir.mkdir(parents=True)

        (memory_dir / "MEMORY.md").write_text("# Current\n数据库当前采用 MySQL。\n", encoding="utf-8")
        (memory_dir / "TASKS.md").write_text("# Tasks\n", encoding="utf-8")
        (memory_dir / "LEARNING.md").write_text("# Learnings\n", encoding="utf-8")
        (memory_dir / "DECISIONS.md").write_text("# Decisions\nADR-001: 数据库采用 MySQL。\n", encoding="utf-8")
        (root / "docs" / "ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")
        (wiki / "README.md").write_text("# Wiki\n", encoding="utf-8")
        (memory_dir / "config.json").write_text(
            json.dumps(
                {
                    "version": 3,
                    "runtime": {"dedupe_cache_size": 64, "max_file_bytes": 1048576},
                    "retrieval": {"max_results": 2, "max_chars": 1800, "min_token_overlap": 1},
                    "promotion": {"min_queue_confidence": 0.45, "batch_size": 25},
                }
            ),
            encoding="utf-8",
        )

        memory_engine.PROJECT_DIR = root
        memory_engine.MEMORY_DIR = memory_dir
        memory_engine.RUNTIME_DIR = runtime_dir
        memory_engine.ARCHIVE_DIR = archive_dir
        memory_engine.CURATED_FILES = [
            memory_dir / "MEMORY.md",
            memory_dir / "TASKS.md",
            memory_dir / "LEARNING.md",
            memory_dir / "DECISIONS.md",
            root / "docs" / "ARCHITECTURE.md",
            wiki / "README.md",
        ]

        promotion_engine.MEMORY_DIR = memory_dir
        promotion_engine.RUNTIME_DIR = runtime_dir
        promotion_engine.CANDIDATES_PATH = runtime_dir / "candidates.jsonl"
        promotion_engine.QUEUE_PATH = runtime_dir / "promotion-queue.jsonl"
        promotion_engine.STATE_PATH = runtime_dir / "promotion-state.json"
        promotion_engine.DECISIONS_PATH = runtime_dir / "promotion-decisions.jsonl"

        self.memory_dir = memory_dir
        self.runtime_dir = runtime_dir

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_decision_is_queued_without_mutating_curated_truth(self) -> None:
        before = (self.memory_dir / "DECISIONS.md").read_text(encoding="utf-8")
        self.assertTrue(
            memory_engine.record_candidate(
                source="user_prompt",
                text="之前不是这样，最终决定数据库统一采用 PostgreSQL，记住这个决定。",
                labels=["correction", "decision"],
            )
        )
        self.assertEqual(promotion_engine.build_review_queue(), 1)
        item = promotion_engine.pending_queue()[0]
        self.assertEqual(item["proposed_target"], ".memory/DECISIONS.md")
        self.assertEqual(item["priority"], "high")
        self.assertEqual(item["conflict_status"], "possible")
        self.assertEqual(before, (self.memory_dir / "DECISIONS.md").read_text(encoding="utf-8"))

    def test_incremental_cursor_processes_only_new_lines(self) -> None:
        memory_engine.record_candidate("user_prompt", "确认采用 PostgreSQL。", ["decision"])
        self.assertEqual(promotion_engine.build_review_queue(), 1)
        self.assertEqual(promotion_engine.build_review_queue(), 0)

        memory_engine.record_candidate("user_prompt", "下一步实现数据库迁移。", ["task"])
        self.assertEqual(promotion_engine.build_review_queue(), 1)
        self.assertEqual(len(promotion_engine.pending_queue()), 2)

    def test_plain_observation_does_not_enter_queue(self) -> None:
        memory_engine.record_candidate("user_prompt", "今天天气不错。", ["observation"])
        self.assertEqual(promotion_engine.build_review_queue(), 0)
        self.assertEqual(promotion_engine.pending_queue(), [])

    def test_correction_without_category_routes_to_current_memory(self) -> None:
        memory_engine.record_candidate("user_prompt", "不对，之前说过的状态需要纠正，记住。", ["correction"])
        self.assertEqual(promotion_engine.build_review_queue(), 1)
        self.assertEqual(promotion_engine.pending_queue()[0]["proposed_target"], ".memory/MEMORY.md")

    def test_review_and_supersession_are_audited_without_applying(self) -> None:
        before = (self.memory_dir / "DECISIONS.md").read_text(encoding="utf-8")
        memory_engine.record_candidate("user_prompt", "最终决定使用 PostgreSQL。", ["decision"])
        promotion_engine.build_review_queue()
        fp = promotion_engine.pending_queue()[0]["candidate_fingerprint"]
        review = promotion_engine.record_review(
            fp,
            "supersede",
            target=".memory/DECISIONS.md",
            note="confirmed in architecture review",
            supersedes="ADR-001",
        )
        self.assertEqual(review["supersedes"], "ADR-001")
        self.assertFalse(review["applied_to_curated"])
        self.assertEqual(promotion_engine.pending_queue(), [])
        self.assertIn("ADR-001", (self.runtime_dir / "promotion-decisions.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(before, (self.memory_dir / "DECISIONS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
