#!/usr/bin/env python3

import json
import sys

from memory_engine import append_unique, record_candidate, sanitize, utc_now

HIGH_VALUE_TOOLS = {
    "Bash",
    "Write",
    "Edit",
    "MultiEdit",
    "NotebookEdit",
    "mcp__github__create_or_update_file",
}


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    tool_name = str(payload.get("tool_name") or "unknown")
    tool_input = sanitize(payload.get("tool_input") or {})
    tool_response = sanitize(payload.get("tool_response") or {})

    record = {
        "timestamp": utc_now(),
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_response": tool_response,
        "session_id": payload.get("session_id"),
    }
    append_unique(
        "observations.jsonl",
        record,
        [tool_name, tool_input, tool_response],
    )

    if tool_name in HIGH_VALUE_TOOLS:
        record_candidate(
            source="tool_result",
            text=f"Tool: {tool_name}\nInput: {tool_input}\nResult: {tool_response}",
            labels=["implementation_observation"],
            extra={"session_id": payload.get("session_id")},
        )

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
