#!/usr/bin/env python3

"""Pluggable memory provider boundary.

Keep Claude Code hooks stable while allowing future semantic-memory backends.
The local provider always remains available as a safe fallback.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from memory_engine import MEMORY_DIR, retrieve


class MemoryProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 4) -> str:
        raise NotImplementedError

    @abstractmethod
    def remember(self, record: dict[str, Any]) -> bool:
        raise NotImplementedError


class LocalMarkdownProvider(MemoryProvider):
    def search(self, query: str, limit: int = 4) -> str:
        return retrieve(query, limit=limit)

    def remember(self, record: dict[str, Any]) -> bool:
        # Runtime candidate capture is handled by memory_engine. Curated Markdown
        # must not be changed silently from the provider boundary.
        return True


def load_config() -> dict[str, Any]:
    path = MEMORY_DIR / "config.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"provider": "local"}


def get_provider() -> MemoryProvider:
    config = load_config()
    provider_name = str(config.get("provider", "local")).lower()

    # Future providers are intentionally selected here. If an external provider
    # is unavailable or misconfigured, fall back to local curated memory rather
    # than breaking Claude Code startup.
    if provider_name == "local":
        return LocalMarkdownProvider()

    return LocalMarkdownProvider()
