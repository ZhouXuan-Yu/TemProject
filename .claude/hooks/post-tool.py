#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
RUNTIME_DIR = PROJECT_DIR / ".memory" / "runtime"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    try:
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_name": payload.get("tool_name"),
            "tool_input": payload.get("tool_input"),
            "tool_response": payload.get("tool_response"),
        }
        with (RUNTIME_DIR / "observations.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
