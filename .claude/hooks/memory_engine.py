#!/usr/bin/env python3

"""Lean dependency-free project memory primitives for Claude Code hooks.

Curated Markdown remains authoritative. Runtime files are bounded evidence only.
The hot path intentionally avoids heavy deduplication, semantic services, and
full tool-response persistence.
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

_CONFIG_CACHE: tuple[str, int | None, dict[str, Any]] | None = None

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?"
        r"-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        re.S,
    ),
]

CORRECTION_HINTS = ("不对", "不是", "我说过", "记住", "以后不要", "应该是", "之前说过", "纠正")
DECISION_HINTS = ("确定", "决定", "确认", "采用", "就用", "最终方案", "定下来")
TASK_HINTS = ("下一步", "继续", "实现", "开发", "修复", "新增", "待办", "todo", "任务")
KNOWLEDGE_HINTS = ("业务规则", "接口", "字段", "口径", "定义", "规则", "背景")


def load_config() -> dict[str, Any]:
    global _CONFIG_CACHE
    path = MEMORY_DIR / "config.json"
    try:
        mtime = path.stat().st_mtime_ns
    except Exception:
        mtime = None
    cache_key = str(path)
    if _CONFIG_CACHE and _CONFIG_CACHE[0] == cache_key and _CONFIG_CACHE[1] == mtime:
        return _CONFIG_CACHE[2]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        config = value if isinstance(value, dict) else {}
    except Exception:
        config = {}
    _CONFIG_CACHE = (cache_key, mtime, config)
    return config


def _runtime_policy() -> dict[str, Any]:
    config = load_config()
    value = config.get("runtime")
    return value if isinstance(value, dict) else {}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize(value: Any, max_chars: int | None = None) -> str:
    policy = _runtime_policy()
    bound = int(max_chars or policy.get("max_record_chars", 4000))
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    text = text[:bound]
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(
            lambda m: (m.group(1) + "=[REDACTED]") if m.lastindex and m.lastindex >= 1 else "[REDACTED]",
            text,
        )
    return text


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def fingerprint(*parts: Any) -> str:
    body = "\n".join(normalize(sanitize(part, max_chars=4000)) for part in parts)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:24]


def _seen_path() -> Path:
    return RUNTIME_DIR / "seen.json"


def _load_seen() -> list[str]:
    try:
        data = json.loads(_seen_path().read_text(encoding="utf-8"))
        values = data.get("fingerprints", [])
        return [str(x) for x in values] if isinstance(values, list) else []
    except Exception:
        return []


def _save_seen(values: list[str]) -> None:
    limit = int(_runtime_policy().get("dedupe_cache_size", 512))
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    _seen_path().write_text(
        json.dumps({"fingerprints": values[-limit:]}, ensure_ascii=False),
        encoding="utf-8",
    )


def rotate_if_needed(path: Path) -> None:
    try:
        max_bytes = int(_runtime_policy().get("max_file_bytes", 1024 * 1024))
        if not path.exists() or path.stat().st_size < max_bytes:
            return
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path.replace(ARCHIVE_DIR / f"{path.stem}-{stamp}{path.suffix}")
    except Exception:
        pass


def append_record(filename: str, record: dict[str, Any]) -> bool:
    """Append bounded runtime evidence without global dedupe overhead."""
    try:
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        path = RUNTIME_DIR / filename
        rotate_if_needed(path)
        value = dict(record)
        value.setdefault("timestamp", utc_now())
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(value, ensure_ascii=False, default=str) + "\n")
        return True
    except Exception:
        return False


def append_unique(filename: str, record: dict[str, Any], dedupe_parts: Iterable[Any]) -> bool:
    """Use lightweight bounded dedupe only for durable-memory candidates."""
    try:
        fp = fingerprint(*dedupe_parts)
        seen = _load_seen()
        if fp in set(seen):
            return False
        value = dict(record)
        value["fingerprint"] = fp
        if not append_record(filename, value):
            return False
        seen.append(fp)
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


def is_high_signal(labels: Iterable[str]) -> bool:
    return any(str(label) != "observation" for label in labels)


def record_candidate(
    source: str,
    text: str,
    labels: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> bool:
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
            grams.update(chunk[i : i + 2] for i in range(len(chunk) - 1))
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
    return [(heading, body) for heading, body in chunks if body]


def retrieve(
    query: str,
    limit: int | None = None,
    max_chars: int | None = None,
    min_score: int | None = None,
) -> str:
    """Small lexical retrieval with a relevance floor and tight context budget."""
    config = load_config()
    retrieval = config.get("retrieval") if isinstance(config.get("retrieval"), dict) else {}
    limit = int(limit or retrieval.get("max_results", 2))
    max_chars = int(max_chars or retrieval.get("max_chars", 2500))

    q = _tokens(query)
    if not q:
        return ""
    threshold = int(min_score or retrieval.get("min_token_overlap", 2))
    if len(q) <= 1:
        threshold = 1

    scored: list[tuple[int, Path, str, str]] = []
    for path in CURATED_FILES:
        for heading, body in _markdown_chunks(path):
            score = len(q & _tokens(heading + "\n" + body))
            if score >= threshold:
                scored.append((score, path, heading, body))

    scored.sort(key=lambda item: item[0], reverse=True)
    output: list[str] = []
    used = 0
    for _score, path, heading, body in scored[:limit]:
        try:
            rel = path.relative_to(PROJECT_DIR)
        except Exception:
            rel = path
        chunk = f"### {rel} — {heading}\n{body}\n"
        remaining = max_chars - used
        if remaining <= 0:
            break
        if len(chunk) > remaining:
            chunk = chunk[:remaining]
        output.append(chunk)
        used += len(chunk)
    return "\n".join(output)
