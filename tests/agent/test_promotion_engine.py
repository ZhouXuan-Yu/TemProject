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

        (memory_dir / "MEMORY.md").write_text("# Current\nDatabase is MySQL.\n", encoding="utf-8")
        (memory_dir / "TASKS.md").write_text("# Tasks\n", encoding="utf-8")
        (memory_dir / "LEARNING.md").write_text("# Learnings\n", encoding="utf-8")
        (memory_dir / "DECISIONS.md").write_text("# Decisions\nADR-001: MySQL\n", encoding="utf-8")
        (root / "docs" / "ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")
        (wiki / "README.md").write_text("# Wiki\n", encoding="utf-8")
        (memory_dir / "config.json").write_text(
            json.dumps({"promotion": {"min_queue_confidence": 0.45}}),
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

        self.root = root
        self.memory_dir = memory_dir
        self.runtime_dir = runtime_dir

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_decision_is_queued_and_curated_truth_is_unchanged(self) -> None:
        before = (self.memory_dir / "DECISIONS.md").read_text(encoding="utf-8")

        added = memory_engine.record_candidate(
            source="user_prompt",
            text="之前不是这样，最终决定数据库统一采用 PostgreSQL，记住这个决定。",
            labels=["correction", "decision"],
        )
        self.assertTrue(added)

        queued = promotion_engine.build_review_queue()
        self.assertEqual(queued, 1)
        items = promotion_engine.pending_queue()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["proposed_target"], ".memory/DECISIONS.md")
        self.assertEqual(items[0]["priority"], "high")
        self.assertEqual(items[0]["conflict_status"], "possible")

        after = (self.memory_dir / "DECISIONS.md").read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_queue_build_is_idempotent(self) -> None:
        memory_engine.record_candidate(
            source="user_prompt",
            text="确认采用 PostgreSQL。",
            labels=["decision"],
        )
        self.assertEqual(promotion_engine.build_review_queue(), 1)
        self.assertEqual(promotion_engine.build_review_queue(), 0)
        self.assertEqual(len(promotion_engine.pending_queue()), 1)

    def test_plain_observation_does_not_enter_review_queue(self) -> None:
        memory_engine.record_candidate(
            source="user_prompt",
            text="今天天气不错。",
            labels=["observation"],
        )
        self.assertEqual(promotion_engine.build_review_queue(), 0)
        self.assertEqual(promotion_engine.pending_queue(), [])

    def test_review_and_supersession_are_audited_without_applying(self) -> None:
        before = (self.memory_dir / "DECISIONS.md").read_text(encoding="utf-8")
        memory_engine.record_candidate(
            source="user_prompt",
            text="最终决定使用 PostgreSQL。",
            labels=["decision"],
        )
        promotion_engine.build_review_queue()
        item = promotion_engine.pending_queue()[0]
        fp = item["candidate_fingerprint"]

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

        audit = (self.runtime_dir / "promotion-decisions.jsonl").read_text(encoding="utf-8")
        self.assertIn("ADR-001", audit)
        self.assertEqual(before, (self.memory_dir / "DECISIONS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
