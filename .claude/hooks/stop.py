#!/usr/bin/env python3

"""Stop-time completion gate.

Memory promotion stays fail-open. Code-changing work, however, must have
verification evidence after the latest code edit before Claude is allowed to
stop. A semantic Stop prompt in settings.json performs the second acceptance
layer against the user's requested outcome.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from memory_engine import load_config

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
RUNTIME_DIR = PROJECT_DIR / ".memory" / "runtime"

STATE_CHANGING_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
DOC_ONLY_SUFFIXES = {".md", ".mdx", ".txt", ".rst", ".adoc"}

VERIFICATION_PATTERNS = [
    r"\bpytest\b",
    r"python(?:3)?\s+-m\s+unittest\b",
    r"\bunittest\b",
    r"\b(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:test|lint|build|check|typecheck)\b",
    r"\bnpx\s+(?:tsc|eslint|vitest|jest)\b",
    r"\b(?:ruff|mypy|pyright)\b",
    r"\btsc\b",
    r"\bgo\s+test\b",
    r"\bcargo\s+(?:test|check|clippy)\b",
    r"\b(?:mvn|mvnw)\b[^\n]*(?:test|verify|package)\b",
    r"\b(?:gradle|gradlew)\b[^\n]*(?:test|check|build)\b",
    r"\bdotnet\s+(?:test|build)\b",
    r"\bphpunit\b",
    r"\bcomposer\s+(?:test|check)\b",
    r"\bgit\s+diff\s+--check\b",
    r"python(?:3)?\s+-m\s+compileall\b",
]

VERIFICATION_RE = re.compile("|".join(f"(?:{p})" for p in VERIFICATION_PATTERNS), re.IGNORECASE)


def _load_session_observations(session_id: str | None) -> list[dict[str, Any]]:
    path = RUNTIME_DIR / "observations.jsonl"
    if not path.exists():
        return []

    items: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-500:]
    except Exception:
        return []

    for line in lines:
        try:
            item = json.loads(line)
        except Exception:
            continue
        if session_id and item.get("session_id") != session_id:
            continue
        if isinstance(item, dict):
            items.append(item)
    return items


def _path_requires_verification(path: str) -> bool:
    if not path:
        return True
    normalized = path.lower().split("?", 1)[0]
    return Path(normalized).suffix not in DOC_ONLY_SUFFIXES


def _verification_command(command: str) -> bool:
    return bool(VERIFICATION_RE.search(command or ""))


def _completion_failure(session_id: str | None) -> str | None:
    observations = _load_session_observations(session_id)
    if not observations:
        return None

    last_change = -1
    changed_paths: list[str] = []

    for idx, item in enumerate(observations):
        if item.get("tool_name") not in STATE_CHANGING_TOOLS:
            continue
        path = str(item.get("path") or "")
        if _path_requires_verification(path):
            last_change = idx
            if path:
                changed_paths.append(path)

    if last_change < 0:
        return None

    verifications: list[dict[str, Any]] = []
    for item in observations[last_change + 1 :]:
        if item.get("tool_name") != "Bash":
            continue
        command = str(item.get("command") or "")
        if _verification_command(command):
            verifications.append(item)

    scope = ", ".join(changed_paths[-4:]) or "code files"

    if not verifications:
        return (
            f"Acceptance gate: {scope} changed, but no relevant verification was run after the latest edit. "
            "Run the smallest relevant test/build/lint/typecheck/smoke check, inspect the result, "
            "fix any failure, then attempt to finish again."
        )

    last = verifications[-1]
    if last.get("status") == "error":
        command = str(last.get("command") or "verification command")
        error = str(last.get("error_summary") or "")[:800]
        return (
            f"Acceptance gate: the latest verification failed: {command}. "
            f"Fix the failure and rerun verification before finishing. {error}"
        )

    return None


def _run_promotion() -> None:
    try:
        config = load_config()
        promotion = config.get("promotion") if isinstance(config.get("promotion"), dict) else {}
        if promotion.get("build_queue_on_stop", True):
            from promotion_engine import build_review_queue

            build_review_queue(limit=int(promotion.get("batch_size", 25)))
    except Exception:
        pass


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    _run_promotion()

    reason = _completion_failure(payload.get("session_id"))
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
        return

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
