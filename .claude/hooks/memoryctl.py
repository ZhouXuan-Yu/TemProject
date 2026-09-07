#!/usr/bin/env python3

"""Small CLI for reviewing promotion candidates.

Approval is deliberately separate from application. This tool records review
intent and can render a draft, but never edits curated Markdown automatically.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from memory_engine import RUNTIME_DIR
from promotion_engine import approved_items, build_review_queue, pending_queue, record_review

DRAFT_PATH = RUNTIME_DIR / "promotion-draft.md"


def cmd_build(_: argparse.Namespace) -> int:
    added = build_review_queue()
    print(f"queued={added} pending={len(pending_queue())}")
    return 0


def cmd_queue(_: argparse.Namespace) -> int:
    items = pending_queue()
    if not items:
        print("No pending promotion candidates.")
        return 0
    for item in items:
        fp = str(item.get("candidate_fingerprint"))
        target = str(item.get("proposed_target"))
        priority = str(item.get("priority"))
        score = item.get("confidence")
        conflict = str(item.get("conflict_status"))
        text = str(item.get("text") or "").replace("\n", " ")
        if len(text) > 180:
            text = text[:177] + "..."
        print(f"{fp}  {priority:<6} score={score} conflict={conflict} -> {target}")
        print(f"  {text}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    record = record_review(args.fingerprint, "approve", target=args.target, note=args.note)
    print(f"approved {record['candidate_fingerprint']} -> {record['target']}")
    print("Curated Markdown was NOT changed. Run `memoryctl.py export` to render an application draft.")
    return 0


def cmd_reject(args: argparse.Namespace) -> int:
    record_review(args.fingerprint, "reject", note=args.note)
    print(f"rejected {args.fingerprint}")
    return 0


def cmd_supersede(args: argparse.Namespace) -> int:
    record = record_review(
        args.fingerprint,
        "supersede",
        target=args.target,
        note=args.note,
        supersedes=args.supersedes,
    )
    print(f"approved {record['candidate_fingerprint']} as superseding {record['supersedes']}")
    print("Curated Markdown was NOT changed; the supersession relationship is preserved in the review audit log.")
    return 0


def cmd_export(_: argparse.Namespace) -> int:
    items = approved_items()
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Promotion Application Draft",
        "",
        "> Generated from explicitly approved promotion records.",
        "> This is a draft only; curated project truth has not been modified.",
        "",
    ]
    if not items:
        lines.append("No approved candidates are waiting for explicit application.")
    else:
        for item, decision in items:
            lines.extend(
                [
                    f"## {item.get('candidate_fingerprint')}",
                    "",
                    f"- Target: `{decision.get('target') or item.get('proposed_target')}`",
                    f"- Action: `{decision.get('action')}`",
                    f"- Confidence: `{item.get('confidence')}`",
                    f"- Conflict: `{item.get('conflict_status')}`",
                    f"- Supersedes: `{decision.get('supersedes') or ''}`",
                    f"- Review note: {decision.get('note') or ''}",
                    "",
                    "### Candidate",
                    "",
                    str(item.get("text") or ""),
                    "",
                    "### Related curated context",
                    "",
                    str(item.get("related_context") or "(none)"),
                    "",
                ]
            )
    DRAFT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(DRAFT_PATH)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review candidate project memories")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="build/rebuild derived promotion queue from new candidates")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("queue", help="list pending candidates")
    p.set_defaults(func=cmd_queue)

    p = sub.add_parser("approve", help="record explicit approval without editing curated Markdown")
    p.add_argument("fingerprint")
    p.add_argument("--target")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("reject", help="record rejection")
    p.add_argument("fingerprint")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_reject)

    p = sub.add_parser("supersede", help="approve a candidate and link it to an older record")
    p.add_argument("fingerprint")
    p.add_argument("--supersedes", required=True, help="older ADR/record identifier, e.g. ADR-003")
    p.add_argument("--target")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_supersede)

    p = sub.add_parser("export", help="render approved candidates to a non-authoritative Markdown draft")
    p.set_defaults(func=cmd_export)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
