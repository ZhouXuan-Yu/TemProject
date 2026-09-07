#!/usr/bin/env python3

"""Build a reviewed promotion queue from append-oriented runtime memory events.

Design goals:
- raw candidates remain non-authoritative
- queue generation is deterministic and idempotent
- scoring is triage only, never authority
- possible conflicts are marked, never auto-resolved
- curated Markdown is never modified by this module
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from memory_engine import MEMORY_DIR, RUNTIME_DIR, retrieve, sanitize, utc_now

CANDIDATES_PATH = RUNTIME_DIR / "candidates.jsonl"
QUEUE_PATH = RUNTIME_DIR / "promotion-queue.jsonl"
STATE_PATH = RUNTIME_DIR / "promotion-state.json"
DECISIONS_PATH = RUNTIME_DIR / "promotion-decisions.jsonl"

TARGET_BY_LABEL = {
    "decision": ".memory/DECISIONS.md",
    "task": ".memory/TASKS.md",
    "knowledge": "docs/wiki/",
    "implementation_observation": ".memory/MEMORY.md",
}


def load_config() -> dict[str, Any]:
    path = MEMORY_DIR / "config.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    value = json.loads(line)
                except Exception:
                    continue
                if isinstance(value, dict):
                    rows.append(value)
    except Exception:
        return []
    return rows


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def _load_state() -> dict[str, Any]:
    try:
        value = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            value.setdefault("processed", [])
            return value
    except Exception:
        pass
    return {"processed": []}


def _save_state(state: dict[str, Any]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    processed = state.get("processed", [])
    if not isinstance(processed, list):
        processed = []
    # Bound derived state. Raw candidates remain in their append-oriented log.
    state["processed"] = processed[-10000:]
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _labels(candidate: dict[str, Any]) -> list[str]:
    raw = candidate.get("labels") or []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return []


def proposed_target(labels: list[str]) -> str | None:
    # Correction is a signal about importance, not a storage destination.
    for label in ("decision", "knowledge", "task", "implementation_observation"):
        if label in labels:
            return TARGET_BY_LABEL[label]
    return None


def confidence_score(candidate: dict[str, Any]) -> float:
    labels = set(_labels(candidate))
    source = str(candidate.get("source") or "")
    text = str(candidate.get("text") or "")

    score = 0.20
    if source == "user_prompt":
        score += 0.25
    elif source == "tool_result":
        score += 0.05

    if "correction" in labels:
        score += 0.30
    if "decision" in labels:
        score += 0.25
    if "knowledge" in labels:
        score += 0.20
    if "task" in labels:
        score += 0.15
    if "implementation_observation" in labels:
        score += 0.05

    explicit_markers = (
        "确认", "确定", "最终", "记住", "以后", "必须", "采用", "决定",
        "confirmed", "decided", "must", "source of truth",
    )
    if any(marker in text.lower() for marker in explicit_markers):
        score += 0.10

    # Long raw tool dumps are less reliable as durable project knowledge.
    if source == "tool_result" and len(text) > 5000:
        score -= 0.10

    return round(max(0.0, min(score, 1.0)), 2)


def priority_for(score: float, labels: list[str]) -> str:
    if "correction" in labels or score >= 0.80:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def possible_conflict(candidate: dict[str, Any], related_context: str) -> str:
    labels = set(_labels(candidate))
    if not related_context.strip():
        return "none_detected"
    if "correction" in labels:
        return "possible"
    if "decision" in labels:
        return "possible"
    return "none_detected"


def _existing_queue_fingerprints() -> set[str]:
    return {
        str(row.get("candidate_fingerprint"))
        for row in _read_jsonl(QUEUE_PATH)
        if row.get("candidate_fingerprint")
    }


def _reviewed_fingerprints() -> set[str]:
    return {
        str(row.get("candidate_fingerprint"))
        for row in _read_jsonl(DECISIONS_PATH)
        if row.get("candidate_fingerprint")
    }


def build_review_queue(limit: int = 100) -> int:
    """Derive review items from new candidate events without changing curated truth."""
    config = load_config()
    promotion_cfg = config.get("promotion") if isinstance(config.get("promotion"), dict) else {}
    min_score = float(promotion_cfg.get("min_queue_confidence", 0.45))

    state = _load_state()
    processed = set(str(x) for x in state.get("processed", []))
    already_queued = _existing_queue_fingerprints()
    already_reviewed = _reviewed_fingerprints()

    added = 0
    for candidate in _read_jsonl(CANDIDATES_PATH):
        if added >= limit:
            break

        fp = str(candidate.get("fingerprint") or "")
        if not fp or fp in processed or fp in already_queued or fp in already_reviewed:
            continue

        labels = _labels(candidate)
        target = proposed_target(labels)
        score = confidence_score(candidate)

        # Ordinary observations remain runtime-only and do not consume review attention.
        if target is None or score < min_score:
            processed.add(fp)
            continue

        text = sanitize(candidate.get("text") or "")
        try:
            related = retrieve(text, limit=3, max_chars=3000)
        except Exception:
            related = ""

        queue_record = {
            "timestamp": utc_now(),
            "status": "needs_review",
            "candidate_fingerprint": fp,
            "source": candidate.get("source"),
            "labels": labels,
            "text": text,
            "proposed_target": target,
            "confidence": score,
            "priority": priority_for(score, labels),
            "conflict_status": possible_conflict(candidate, related),
            "related_context": related,
            "requires_review": True,
            "meta": candidate.get("meta") or {},
        }
        _append_jsonl(QUEUE_PATH, queue_record)
        processed.add(fp)
        already_queued.add(fp)
        added += 1

    state["processed"] = sorted(processed)
    state["last_build_at"] = utc_now()
    _save_state(state)
    return added


def pending_queue() -> list[dict[str, Any]]:
    decisions = {
        str(row.get("candidate_fingerprint")): row
        for row in _read_jsonl(DECISIONS_PATH)
        if row.get("candidate_fingerprint")
    }
    result: list[dict[str, Any]] = []
    for row in _read_jsonl(QUEUE_PATH):
        fp = str(row.get("candidate_fingerprint") or "")
        if not fp:
            continue
        decision = decisions.get(fp)
        if decision and str(decision.get("action")) in {"approve", "reject", "supersede"}:
            continue
        result.append(row)
    order = {"high": 0, "medium": 1, "low": 2}
    result.sort(key=lambda x: (order.get(str(x.get("priority")), 9), -float(x.get("confidence") or 0)))
    return result


def record_review(
    candidate_fingerprint: str,
    action: str,
    target: str | None = None,
    note: str | None = None,
    supersedes: str | None = None,
) -> dict[str, Any]:
    if action not in {"approve", "reject", "supersede"}:
        raise ValueError("action must be approve, reject, or supersede")

    queue = {
        str(row.get("candidate_fingerprint")): row
        for row in _read_jsonl(QUEUE_PATH)
        if row.get("candidate_fingerprint")
    }
    item = queue.get(candidate_fingerprint)
    if not item:
        raise KeyError(f"candidate not found in promotion queue: {candidate_fingerprint}")

    final_target = target or item.get("proposed_target")
    record = {
        "timestamp": utc_now(),
        "candidate_fingerprint": candidate_fingerprint,
        "action": action,
        "target": final_target,
        "note": sanitize(note or ""),
        "supersedes": supersedes,
        "applied_to_curated": False,
    }
    _append_jsonl(DECISIONS_PATH, record)
    return record


def approved_items() -> list[tuple[dict[str, Any], dict[str, Any]]]:
    queue = {
        str(row.get("candidate_fingerprint")): row
        for row in _read_jsonl(QUEUE_PATH)
        if row.get("candidate_fingerprint")
    }
    latest_decisions: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(DECISIONS_PATH):
        fp = str(row.get("candidate_fingerprint") or "")
        if fp:
            latest_decisions[fp] = row

    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for fp, decision in latest_decisions.items():
        if decision.get("action") not in {"approve", "supersede"}:
            continue
        item = queue.get(fp)
        if item:
            result.append((item, decision))
    return result


def main() -> None:
    added = build_review_queue()
    print(json.dumps({"queued": added, "pending": len(pending_queue())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
