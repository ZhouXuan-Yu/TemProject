#!/usr/bin/env python3

import json
import sys

from memory_engine import load_config


def main() -> None:
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    try:
        config = load_config()
        promotion = config.get("promotion") if isinstance(config.get("promotion"), dict) else {}
        if promotion.get("build_queue_on_stop", True):
            from promotion_engine import build_review_queue

            build_review_queue(limit=int(promotion.get("batch_size", 25)))
    except Exception:
        pass

    print(json.dumps({"continue": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
