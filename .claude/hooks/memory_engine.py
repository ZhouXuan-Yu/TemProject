#!/usr/bin/env python3

"""Small dependency-free memory engine used by Claude Code hooks.

The curated Markdown files remain the source of truth. This module only manages
runtime candidates, deduplication, lightweight retrieval, sanitisation and
rotation. A future semantic-memory provider can be plugged in without changing
hook contracts.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
MEMORY_DIR = PROJECT_DIR / ".memory"
RUNTIME_DIR = MEMORY_DIR / "runtime"
ARCHIVE_DIR = MEMORY_DIR / "archive"

CURATED_FILES = [
    MEMORY_DIR / "MEMORY.md",
    MEMORY_DIR / "TASKS.md",
    MEMORY_DIR / "LEARNING.md",
    MEMORY_DIR / "DECISIONS.md",
    PROJECT_DIR / "docs" / "ARCHITECTURE.md",
    PROJECT_DIR / "docs" / "wiki" / "README.md",
]

MAX_RECORD_CHARS = 12_000
MAX_RUNTIME_FILE_BYTES = 2 * 1024 * 1024

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.S),
]

CORRECTION_HINTS = ("不对", "不是", "我说过", "记住", "以后不要", "应该是", "之前说过", "纠正")
DECISION_HINTS = ("确定", "决定", "确认", "采用", "就用", "最终方案", "定下来")
TASK_HINTS = ("下一步", "继续", "实现", "开发", "修复", "新增", "待办", "todo", "任务")
KNOWLEDGE_HINTS = ("业务规则", "接口", "字段", "口径", "定义", "规则", "背景")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    text = text[:MAX_RECORD_CHARS]
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: (m.group(1) + "=[REDACTED]") if m.lastindex and m.lastindex >= 1 else "[REDACTED]", text)
    return text


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def fingerprint(*parts: Any) -> str:
    body = "\n".join(normalize(sanitize(part)) for part in parts)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:24]


def _load_seen() -> set[str]:
    path = RUNTIME_DIR / "seen.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data.get("fingerprints", []))
    except Exception:
        return set()


def _save_seen(seen: set[str]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    # Bound runtime state so it cannot grow forever.
    values = list(seen)[-5000:]
    (RUNTIME_DIR / "seen.json").write_text(
        json.dumps({"fingerprints": values}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def rotate_if_needed(path: Path) -> None:
    try:
        if not path.exists() or path.stat().st_size < MAX_RUNTIME_FILE_BYTES:
            return
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = ARCHIVE_DIR / f"{path.stem}-{stamp}{path.suffix}"
        path.replace(target)
    except Exception:
        pass


def append_unique(filename: str, record: dict[str, Any], dedupe_parts: Iterable[Any]) -> bool:
    try:
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        path = RUNTIME_DIR / filename
        rotate_if_needed(path)
        fp = fingerprint(*dedupe_parts)
        seen = _load_seen()
        if fp in seen:
            return False
        record = dict(record)
        record.setdefault("timestamp", utc_now())
        record["fingerprint"] = fp
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        seen.add(fp)
        _save_seen(seen)
        return True
    except Exception:
        return False


def classify_prompt(prompt: str) -> list[str]:
    lowered = prompt.lower()
    labels: list[str] = []
    if any(h in prompt for h in CORRECTION_HINTS):
        labels.append("correction")
    if any(h in prompt for h in DECISION_HINTS):
        labels.append("decision")
    if any(h in lowered for h in TASK_HINTS):
        labels.append("task")
    if any(h in lowered for h in KNOWLEDGE_HINTS):
        labels.append("knowledge")
    return labels or ["observation"]


def record_candidate(source: str, text: str, labels: list[str] | None = None, extra: dict[str, Any] | None = None) -> bool:
    clean = sanitize(text)
    if not clean.strip():
        return False
    labels = labels or ["observation"]
    record: dict[str, Any] = {
        "source": source,
        "labels": labels,
        "text": clean,
        "status": "candidate",
    }
    if extra:
        record["meta"] = extra
    return append_unique("candidates.jsonl", record, [source, labels, clean])


def _tokens(text: str) -> set[str]:
    latin = set(re.findall(r"[a-zA-Z0-9_.\-/]{2,}", text.lower()))
    chinese = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    grams: set[str] = set()
    for chunk in chinese:
        if len(chunk) <= 4:
            grams.add(chunk)
        else:
            grams.update(chunk[i:i+2] for i in range(len(chunk) - 1))
    return latin | grams


def _markdown_chunks(path: Path) -> list[tuple[str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    chunks: list[tuple[str, str]] = []
    title = path.name
    buf: list[str] = []
    current = title
    for line in text.splitlines():
        if line.startswith("#"):
            if buf:
                chunks.append((current, "\n".join(buf).strip()))
            current = line.lstrip("# ").strip() or title
            buf = [line]
        else:
            buf.append(line)
    if buf:
        chunks.append((current, "\n".join(buf).strip()))
    return [(h, b) for h, b in chunks if b]


def retrieve(query: str, limit: int = 4, max_chars: int = 6000) -> str:
    """Lightweight lexical retrieval from curated source-of-truth Markdown."""
    q = _tokens(query)
    if not q:
        return ""
    scored: list[tuple[int, Path, str, str]] = []
    for path in CURATED_FILES:
        for heading, body in _markdown_chunks(path):
            score = len(q & _tokens(heading + "\n" + body))
            if score:
                scored.append((score, path, heading, body))
    scored.sort(key=lambda item: item[0], reverse=True)
    output: list[str] = []
    used = 0
    for score, path, heading, body in scored[:limit]:
        rel = path.relative_to(PROJECT_DIR)
        chunk = f"### {rel} — {heading}\n{body}\n"
        if used + len(chunk) > max_chars:
            chunk = chunk[: max(0, max_chars - used)]
        if not chunk:
            break
        output.append(chunk)
        used += len(chunk)
    return "\n".join(output)
