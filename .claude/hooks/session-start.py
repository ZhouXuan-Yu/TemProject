#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
MEMORY_DIR = PROJECT_DIR / ".memory"


def read_file(path: Path, max_chars: int) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return ""
    return text if len(text) <= max_chars else text[:max_chars] + "\n...[truncated]"


def main() -> None:
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    memory = read_file(MEMORY_DIR / "MEMORY.md", 3200)
    tasks = read_file(MEMORY_DIR / "TASKS.md", 2200)
    context = (
        "# PROJECT RUNTIME CONTEXT\n\n"
        "## Current State\n\n" + memory + "\n\n"
        "## Active Work\n\n" + tasks + "\n\n"
        "Use curated project records as context. Current user instructions and current source code take precedence on conflict."
    )
    print(
        json.dumps(
            {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
