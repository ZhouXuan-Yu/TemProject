#!/usr/bin/env python3

import json
import sys

from memory_engine import classify_prompt, is_high_signal, load_config, record_candidate, retrieve


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    if not isinstance(prompt, str):
        prompt = str(prompt)

    labels = classify_prompt(prompt)
    if is_high_signal(labels):
        record_candidate(
            source="user_prompt",
            text=prompt,
            labels=labels,
            extra={"session_id": payload.get("session_id")},
        )

    config = load_config()
    retrieval = config.get("retrieval") if isinstance(config.get("retrieval"), dict) else {}
    recalled = ""
    if retrieval.get("enabled", True):
        try:
            recalled = retrieve(
                prompt,
                limit=int(retrieval.get("max_results", 2)),
                max_chars=int(retrieval.get("max_chars", 2500)),
                min_score=int(retrieval.get("min_token_overlap", 2)),
            )
        except Exception:
            recalled = ""

    if recalled:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    "# Relevant Project Memory\n\n"
                    "Use this reviewed project context only when relevant; current user instructions win on conflict.\n\n"
                    + recalled
                ),
            }
        }
    else:
        output = {"continue": True}

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
