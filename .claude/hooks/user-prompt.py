#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
RUNTIME_DIR = PROJECT_DIR / ".memory" / "runtime"
CORRECTION_HINTS = ["不对", "不是", "我说过", "记住", "以后不要", "应该是", "之前说过"]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    if not isinstance(prompt, str):
        prompt = str(prompt)

    if prompt and any(hint in prompt for hint in CORRECTION_HINTS):
        try:
            RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "potential_correction",
                "prompt": prompt[:4000],
            }
            with (RUNTIME_DIR / "corrections.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            pass

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
