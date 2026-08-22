#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
MEMORY_DIR = PROJECT_DIR / ".memory"


def read_file(path: Path, max_chars: int = 12000) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return ""
    if len(text) > max_chars:
        return text[:max_chars] + "\n...[truncated]"
    return text


def main() -> None:
    try:
        _hook_input = json.load(sys.stdin)
    except Exception:
        _hook_input = {}

    memory = read_file(MEMORY_DIR / "MEMORY.md")
    tasks = read_file(MEMORY_DIR / "TASKS.md")

    context = f"""# PROJECT RUNTIME CONTEXT

## Current Project State

{memory}

## Active Tasks

{tasks}

## Runtime Instructions

- Treat MEMORY.md as current state, not immutable truth.
- Treat DECISIONS.md as historical accepted decisions.
- Do not overwrite curated memory because of assumptions.
- Consult relevant wiki and architecture documents before significant changes.
"""

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
