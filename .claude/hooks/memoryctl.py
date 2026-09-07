#!/usr/bin/env python3

"""On-demand review and health CLI for project Agent memory."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from memory_engine import MEMORY_DIR, PROJECT_DIR, RUNTIME_DIR, load_config
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
        text = str(item.get("text") or "").replace("\n", " ")
        if len(text) > 160:
            text = text[:157] + "..."
        print(
            f"{item.get('candidate_fingerprint')}  {str(item.get('priority')):<6} "
            f"score={item.get('confidence')} conflict={item.get('conflict_status')} "
            f"-> {item.get('proposed_target')}"
        )
        print(f"  {text}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    record = record_review(args.fingerprint, "approve", target=args.target, note=args.note)
    print(f"approved {record['candidate_fingerprint']} -> {record['target']}")
    print("Curated Markdown was not changed. Run `memoryctl.py export` to render a draft.")
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
    return 0


def cmd_export(_: argparse.Namespace) -> int:
    items = approved_items()
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Promotion Application Draft",
        "",
        "> Generated from explicitly approved records. Curated truth has not been modified.",
        "",
    ]
    if not items:
        lines.append("No approved candidates are waiting for application.")
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


def cmd_doctor(_: argparse.Namespace) -> int:
    checks: list[tuple[str, bool, str]] = []
    required = [
        PROJECT_DIR / "CLAUDE.md",
        PROJECT_DIR / ".claude" / "settings.json",
        MEMORY_DIR / "MEMORY.md",
        MEMORY_DIR / "TASKS.md",
        MEMORY_DIR / "DECISIONS.md",
        MEMORY_DIR / "config.json",
    ]
    for path in required:
        checks.append((str(path.relative_to(PROJECT_DIR)), path.exists(), "required file"))

    config = load_config()
    checks.append(("config.version>=3", int(config.get("version", 0)) >= 3, str(config.get("version"))))
    mcp = shutil.which("codebase-memory-mcp")
    checks.append(("codebase-memory-mcp", bool(mcp), mcp or "optional: not on PATH"))

    if RUNTIME_DIR.exists():
        runtime_bytes = sum(p.stat().st_size for p in RUNTIME_DIR.glob("*") if p.is_file())
    else:
        runtime_bytes = 0
    runtime_limit = int((config.get("runtime") or {}).get("max_file_bytes", 1024 * 1024)) * 6
    checks.append(("runtime-size", runtime_bytes <= runtime_limit, f"{runtime_bytes} bytes"))

    failures = 0
    for name, ok, detail in checks:
        status = "PASS" if ok else ("WARN" if name == "codebase-memory-mcp" else "FAIL")
        if status == "FAIL":
            failures += 1
        print(f"[{status}] {name}: {detail}")
    print(f"pending-memory-reviews={len(pending_queue())}")
    print(f"python={sys.version.split()[0]}")
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project Agent memory utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text, func in (
        ("build", "process new memory candidates", cmd_build),
        ("queue", "list pending memory reviews", cmd_queue),
        ("export", "render approved items to a non-authoritative draft", cmd_export),
        ("doctor", "check local Agent infrastructure health", cmd_doctor),
    ):
        item = sub.add_parser(name, help=help_text)
        item.set_defaults(func=func)

    item = sub.add_parser("approve", help="record explicit approval")
    item.add_argument("fingerprint")
    item.add_argument("--target")
    item.add_argument("--note", default="")
    item.set_defaults(func=cmd_approve)

    item = sub.add_parser("reject", help="record rejection")
    item.add_argument("fingerprint")
    item.add_argument("--note", default="")
    item.set_defaults(func=cmd_reject)

    item = sub.add_parser("supersede", help="approve and link to an older record")
    item.add_argument("fingerprint")
    item.add_argument("--supersedes", required=True)
    item.add_argument("--target")
    item.add_argument("--note", default="")
    item.set_defaults(func=cmd_supersede)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
