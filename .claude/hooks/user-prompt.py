#!/usr/bin/env python3

import json
import sys

from memory_engine import classify_prompt, record_candidate, retrieve


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    if not isinstance(prompt, str):
        prompt = str(prompt)

    labels = classify_prompt(prompt)
    record_candidate(
        source="user_prompt",
        text=prompt,
        labels=labels,
        extra={"session_id": payload.get("session_id")},
    )

    recalled = retrieve(prompt)
    if recalled:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    "# Relevant Project Memory\n\n"
                    "The following content was retrieved from curated project memory. "
                    "Use it as context, but prefer explicit current user instructions if they conflict.\n\n"
                    + recalled
                ),
            }
        }
    else:
        output = {"continue": True}

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
