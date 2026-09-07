#!/usr/bin/env python3

"""Incremental reviewed promotion queue for high-signal memory candidates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterator

from memory_engine import MEMORY_DIR, RUNTIME_DIR, retrieve, sanitize, utc_now

CANDIDATES_PATH = RUNTIME_DIR / "candidates.jsonl"
QUEUE_PATH = RUNTIME_DIR / "promotion-queue.jsonl"
STATE_PATH = RUNTIME_DIR / "promotion-state.json"
DECISIONS_PATH = RUNTIME_DIR / "promotion-decisions.jsonl"

TARGET_BY_LABEL = {
    "decision": ".memory/DECISIONS.md",
    "task": ".memory/TASKS.md",
    "knowledge": "docs/wiki/",
    "correction": ".memory/MEMORY.md",
}


def load_config() -> dict[str, Any]:
    try:
        value = json.loads((MEMORY_DIR / "config.json").read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
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
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _save_state(state: dict[str, Any]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _file_identity(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        with path.open("rb") as fh:
            first = fh.read(512)
        return hashlib.sha256(first).hexdigest()[:16]
    except Exception:
        return ""


def _new_candidates(state: dict[str, Any]) -> tuple[Iterator[dict[str, Any]], dict[str, Any]]:
    current_identity = _file_identity(CANDIDATES_PATH)
    previous_identity = str(state.get("candidate_identity") or "")
    offset = int(state.get("candidate_offset") or 0)

    try:
        size = CANDIDATES_PATH.stat().st_size
    except Exception:
        size = 0

    if previous_identity != current_identity or offset > size:
        offset = 0

    progress = {"candidate_identity": current_identity, "candidate_offset": offset}

    def iterator() -> Iterator[dict[str, Any]]:
        if not CANDIDATES_PATH.exists():
            return
        with CANDIDATES_PATH.open("rb") as fh:
            fh.seek(offset)
            while True:
                raw = fh.readline()
                if not raw:
                    break
                progress["candidate_offset"] = fh.tell()
                try:
                    value = json.loads(raw.decode("utf-8"))
                except Exception:
                    continue
                if isinstance(value, dict):
                    yield value

    return iterator(), progress


def _labels(candidate: dict[str, Any]) -> list[str]:
    raw = candidate.get("labels") or []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return []


def proposed_target(labels: list[str]) -> str | None:
    for label in ("decision", "knowledge", "task", "correction"):
        if label in labels:
            return TARGET_BY_LABEL[label]
    return None


def confidence_score(candidate: dict[str, Any]) -> float:
    labels = set(_labels(candidate))
    source = str(candidate.get("source") or "")
    text = str(candidate.get("text") or "").lower()

    score = 0.20
    if source == "user_prompt":
        score += 0.30
    if "correction" in labels:
        score += 0.25
    if "decision" in labels:
        score += 0.20
    if "knowledge" in labels:
        score += 0.15
    if "task" in labels:
        score += 0.10

    explicit_markers = ("确认", "确定", "最终", "记住", "以后", "必须", "采用", "决定", "confirmed", "decided", "must")
    if any(marker in text for marker in explicit_markers):
        score += 0.10
    return round(max(0.0, min(score, 1.0)), 2)


def priority_for(score: float, labels: list[str]) -> str:
    if "correction" in labels or score >= 0.80:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def _existing_fingerprints(path: Path) -> set[str]:
    return {
        str(row.get("candidate_fingerprint"))
        for row in _read_jsonl(path)
        if row.get("candidate_fingerprint")
    }


def build_review_queue(limit: int | None = None) -> int:
    """Process only newly appended candidate lines; never edit curated Markdown."""
    config = load_config()
    promotion = config.get("promotion") if isinstance(config.get("promotion"), dict) else {}
    min_score = float(promotion.get("min_queue_confidence", 0.45))
    limit = int(limit or promotion.get("batch_size", 25))

    state = _load_state()
    candidates, progress = _new_candidates(state)
    queued = _existing_fingerprints(QUEUE_PATH)
    reviewed = _existing_fingerprints(DECISIONS_PATH)

    added = 0
    for candidate in candidates:
        fp = str(candidate.get("fingerprint") or "")
        if not fp or fp in queued or fp in reviewed:
            continue

        labels = _labels(candidate)
        target = proposed_target(labels)
        score = confidence_score(candidate)
        if target is None or score < min_score:
            continue

        text = sanitize(candidate.get("text") or "")
        related = ""
        conflict = "none_detected"
        if any(label in labels for label in ("correction", "decision", "knowledge")):
            try:
                related = retrieve(text, limit=2, max_chars=1800)
            except Exception:
                related = ""
            if related and any(label in labels for label in ("correction", "decision")):
                conflict = "possible"

        _append_jsonl(
            QUEUE_PATH,
            {
                "timestamp": utc_now(),
                "status": "needs_review",
                "candidate_fingerprint": fp,
                "source": candidate.get("source"),
                "labels": labels,
                "text": text,
                "proposed_target": target,
                "confidence": score,
                "priority": priority_for(score, labels),
                "conflict_status": conflict,
                "related_context": related,
                "requires_review": True,
                "meta": candidate.get("meta") or {},
            },
        )
        queued.add(fp)
        added += 1
        if added >= limit:
            break

    state.update(progress)
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

    record = {
        "timestamp": utc_now(),
        "candidate_fingerprint": candidate_fingerprint,
        "action": action,
        "target": target or item.get("proposed_target"),
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
    latest: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(DECISIONS_PATH):
        fp = str(row.get("candidate_fingerprint") or "")
        if fp:
            latest[fp] = row

    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for fp, decision in latest.items():
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
