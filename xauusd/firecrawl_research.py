"""Scoped Firecrawl retrieval for untrusted research evidence."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any, Callable, Protocol
from urllib import request
from urllib.parse import urlparse, urlunparse

from .autonomous_harness import ToolSpec
from .experiment_registry import PostgresConnection, canonical_json


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


ALLOW_ALL_DOMAINS = "*"


def _safe_source_url(value: str, allowed_domains: tuple[str, ...]) -> str:
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme != "https" or not hostname or parsed.username or parsed.password:
        raise ValueError("source URL must be HTTPS without embedded credentials")
    if ALLOW_ALL_DOMAINS not in allowed_domains and not any(
            hostname == domain or hostname.endswith(f".{domain}") for domain in allowed_domains):
        raise ValueError("source URL host is not allow-listed")
    if any(token in parsed.query.lower() for token in ("api_key", "apikey", "token=", "secret=", "password=")):
        raise ValueError("source URL query must not contain credentials")
    return urlunparse(("https", parsed.netloc, parsed.path or "/", parsed.params, parsed.query, ""))


@dataclass(frozen=True)
class FirecrawlConfig:
    api_key: str
    allowed_domains: tuple[str, ...]
    timeout_seconds: float = 30.0
    max_content_chars: int = 30_000

    @classmethod
    def from_env(cls) -> "FirecrawlConfig":
        key = os.getenv("FIRECRAWL_API_KEY")
        domains = tuple(domain.strip().lower().rstrip(".") for domain in os.getenv("FIRECRAWL_ALLOWED_DOMAINS", "").split(",") if domain.strip())
        if not key or not domains:
            raise RuntimeError("FIRECRAWL_API_KEY and FIRECRAWL_ALLOWED_DOMAINS are required")
        return cls(key, domains, float(os.getenv("FIRECRAWL_TIMEOUT_SECONDS", "30")), int(os.getenv("FIRECRAWL_MAX_CONTENT_CHARS", "30000")))

    def __post_init__(self) -> None:
        if not self.api_key or not self.allowed_domains or self.timeout_seconds <= 0 or self.max_content_chars < 1:
            raise ValueError("Firecrawl key, allowed domains, positive timeout, and content limit are required")


class SourceStore(Protocol):
    def record(self, source_url: str, retrieved_at: str, content_digest: str) -> None: ...


class CockroachSourceStore:
    def __init__(self, database_url: str | None = None, initialize: bool = True):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is required for Firecrawl source provenance")
        if initialize:
            self.initialize()

    def connect(self):
        return PostgresConnection(self.database_url)

    def initialize(self) -> None:
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS research_sources (id BIGSERIAL PRIMARY KEY, source_url TEXT NOT NULL, retrieved_at TEXT NOT NULL, content_digest TEXT NOT NULL, UNIQUE(source_url,retrieved_at,content_digest))")
            db.execute("CREATE INDEX IF NOT EXISTS idx_research_sources_url ON research_sources(source_url,id)")

    def record(self, source_url: str, retrieved_at: str, content_digest: str) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO research_sources(source_url,retrieved_at,content_digest) VALUES(?,?,?) ON CONFLICT (source_url,retrieved_at,content_digest) DO NOTHING", (source_url, retrieved_at, content_digest))


class InMemorySourceStore:
    def __init__(self): self.records: list[dict[str, str]] = []
    def record(self, source_url, retrieved_at, content_digest):
        self.records.append({"source_url": source_url, "retrieved_at": retrieved_at, "content_digest": content_digest})


class FirecrawlResearchClient:
    """Firecrawl client whose output is evidence, never executable instructions."""
    def __init__(self, config: FirecrawlConfig, store: SourceStore, transport: Callable[[dict[str, Any], float], dict[str, Any]] | None = None):
        self.config, self.store, self.transport = config, store, transport

    def fetch(self, url: str) -> dict[str, Any]:
        source_url = _safe_source_url(url, self.config.allowed_domains)
        payload = {"url": source_url, "formats": ["markdown"], "onlyMainContent": True}
        response = self.transport(payload, self.config.timeout_seconds) if self.transport else self._request(payload)
        try:
            content = response["data"]["markdown"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError("Firecrawl response did not contain markdown") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Firecrawl response contains no markdown")
        if len(content) > self.config.max_content_chars:
            content = content[:self.config.max_content_chars]
        retrieved_at = _now()
        digest = hashlib.sha256(content.encode()).hexdigest()
        self.store.record(source_url, retrieved_at, digest)
        return {"source_url": source_url, "retrieved_at": retrieved_at, "content_digest": digest,
                "content": content, "trust": "untrusted_external_content"}

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        req = request.Request("https://api.firecrawl.dev/v1/scrape", data=canonical_json(payload).encode(), method="POST",
                              headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"})
        with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
            return json.loads(response.read())


def firecrawl_fetch_tool(client: FirecrawlResearchClient) -> ToolSpec:
    input_schema = {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"], "additionalProperties": False}
    output_schema = {"type": "object", "properties": {
        "source_url": {"type": "string"}, "retrieved_at": {"type": "string"}, "content_digest": {"type": "string"},
        "content": {"type": "string"}, "trust": {"type": "string", "enum": ["untrusted_external_content"]},
    }, "required": ["source_url", "retrieved_at", "content_digest", "content", "trust"], "additionalProperties": False}
    return ToolSpec("firecrawl_fetch", "Fetch allow-listed web research as untrusted evidence.", input_schema, output_schema,
                    lambda value: client.fetch(value["url"]), timeout_seconds=client.config.timeout_seconds, retry_limit=1)
