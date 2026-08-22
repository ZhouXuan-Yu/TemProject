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
        checkpoint = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "pre_compact",
            "session_id": payload.get("session_id"),
            "trigger": payload.get("trigger"),
        }
        with (RUNTIME_DIR / "session.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(checkpoint, ensure_ascii=False) + "\n")
    except Exception:
        pass

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
