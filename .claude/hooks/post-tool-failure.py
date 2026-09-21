#!/usr/bin/env python3

"""Capture failed Bash executions as bounded runtime evidence.

Claude Code routes non-zero Bash executions through PostToolUseFailure rather
than PostToolUse. This hook makes failed verification visible to the
deterministic Stop completion gate. It is deliberately fail-open.
"""

import json
import sys

from memory_engine import append_record, load_config, sanitize


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    try:
        config = load_config()
        runtime = config.get("runtime") if isinstance(config.get("runtime"), dict) else {}
        max_chars = int(runtime.get("max_observation_chars", 1600))

        tool_input = payload.get("tool_input") or {}
        command = ""
        if isinstance(tool_input, dict):
            command = tool_input.get("command") or tool_input.get("cmd") or tool_input.get("script") or ""

        error = payload.get("error")
        if error is None:
            error = payload.get("tool_response")
        if error is None:
            error = payload.get("tool_result")
        if error is None:
            error = "tool execution failed"

        append_record(
            "observations.jsonl",
            {
                "tool_name": str(payload.get("tool_name") or "Bash"),
                "command": sanitize(command, max_chars=min(1000, max_chars)),
                "status": "error",
                "error_summary": sanitize(error, max_chars=max_chars),
                "session_id": payload.get("session_id"),
            },
        )
    except Exception:
        pass

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
