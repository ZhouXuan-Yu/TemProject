#!/usr/bin/env python3

"""Capture only bounded, state-changing tool observations.

This hook intentionally does not create long-term memory candidates. User/agent
reviewed state belongs in curated memory; tool telemetry remains runtime evidence.
"""

import json
import sys
from typing import Any

from memory_engine import append_record, load_config, sanitize


def _path_from_input(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    for key in ("file_path", "path", "notebook_path"):
        item = value.get(key)
        if isinstance(item, str):
            return item
    return ""


def _summarize(tool_name: str, tool_input: Any, tool_response: Any) -> dict[str, Any]:
    config = load_config()
    runtime = config.get("runtime") if isinstance(config.get("runtime"), dict) else {}
    max_chars = int(runtime.get("max_observation_chars", 1600))

    result: dict[str, Any] = {"tool_name": tool_name}
    if tool_name == "Bash" and isinstance(tool_input, dict):
        command = tool_input.get("command") or tool_input.get("cmd") or tool_input.get("script") or ""
        result["command"] = sanitize(command, max_chars=min(1000, max_chars))
    else:
        path = _path_from_input(tool_input)
        if path:
            result["path"] = sanitize(path, max_chars=500)

    response_text = sanitize(tool_response or {}, max_chars=max_chars)
    lowered = response_text.lower()
    result["status"] = "error" if any(token in lowered for token in ("error", "failed", "exception", "traceback")) else "ok"
    if result["status"] == "error":
        result["error_summary"] = response_text
    return result


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    tool_name = str(payload.get("tool_name") or "unknown")
    observation = _summarize(tool_name, payload.get("tool_input") or {}, payload.get("tool_response") or {})
    observation["session_id"] = payload.get("session_id")
    append_record("observations.jsonl", observation)

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
