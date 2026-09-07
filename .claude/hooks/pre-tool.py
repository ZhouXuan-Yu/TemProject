#!/usr/bin/env python3

"""Tiered Bash safety guard: catastrophic commands are denied; recoverable high-risk commands ask."""

import json
import re
import sys

HARD_DENY = [
    (r"(^|\s)rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+/(\s|$)", "Refusing recursive forced deletion of filesystem root."),
    (r"(^|\s)rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+~(/|\s|$)", "Refusing recursive forced deletion of the home directory."),
    (r"\bmkfs(?:\.[a-z0-9]+)?\b", "Refusing filesystem formatting from an Agent hook."),
    (r"\bformat\s+[a-z]:\s*(?:/|$)", "Refusing drive formatting from an Agent hook."),
]

ASK_BEFORE = [
    (r"git\s+reset\s+--hard", "Hard reset can discard uncommitted work."),
    (r"git\s+clean\b[^\n]*-[^\n]*f", "git clean can permanently remove untracked files."),
    (r"git\s+push\b[^\n]*--force(?:-with-lease)?", "Force push rewrites remote history."),
    (r"(^|\s)rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\b", "Recursive forced deletion requires confirmation."),
    (r"\bRemove-Item\b[^\n]*(?:-Recurse[^\n]*-Force|-Force[^\n]*-Recurse)", "Recursive forced PowerShell deletion requires confirmation."),
    (r"\b(?:rmdir|rd)\b[^\n]*/s[^\n]*/q", "Recursive directory deletion requires confirmation."),
    (r"\bdel\b[^\n]*/s[^\n]*/q", "Recursive file deletion requires confirmation."),
    (r"\bDROP\s+(?:TABLE|DATABASE|SCHEMA|USER)\b", "Destructive database DDL requires confirmation."),
    (r"\bTRUNCATE\s+(?:TABLE\s+)?", "Database truncation requires confirmation."),
    (r"\bDELETE\s+FROM\s+[\w.`\"-]+\s*;?\s*$", "DELETE without a visible WHERE clause requires confirmation."),
]


def extract_command(payload: dict) -> str:
    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, dict):
        for key in ("command", "cmd", "script"):
            value = tool_input.get(key)
            if isinstance(value, str):
                return value
    return ""


def decision(kind: str, reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": kind,
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    command = extract_command(payload)
    for pattern, reason in HARD_DENY:
        if re.search(pattern, command, flags=re.IGNORECASE | re.MULTILINE):
            decision("deny", reason)
            return
    for pattern, reason in ASK_BEFORE:
        if re.search(pattern, command, flags=re.IGNORECASE | re.MULTILINE):
            decision("ask", reason)
            return

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
