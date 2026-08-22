#!/usr/bin/env python3

import json
import re
import sys

DANGEROUS_PATTERNS = [
    (r"(^|\s)rm\s+-rf\s+/(\s|$)", "Refusing recursive deletion of filesystem root."),
    (r"(^|\s)rm\s+-rf\s+~(/|\s|$)", "Refusing recursive deletion of the home directory."),
    (r"git\s+reset\s+--hard", "Destructive git reset requires explicit approval."),
    (r"git\s+push\b[^\n]*--force(?:-with-lease)?", "Force push requires explicit approval."),
    (r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b", "Destructive database operation requires explicit approval."),
    (r"\bTRUNCATE\s+(TABLE\s+)?", "Database truncation requires explicit approval."),
]


def extract_command(payload: dict) -> str:
    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, dict):
        for key in ("command", "cmd", "script"):
            value = tool_input.get(key)
            if isinstance(value, str):
                return value
    return ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    command = extract_command(payload)
    for pattern, reason in DANGEROUS_PATTERNS:
        if re.search(pattern, command, flags=re.IGNORECASE | re.MULTILINE):
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
            print(json.dumps(output, ensure_ascii=False))
            return

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
