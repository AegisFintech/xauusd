"""Small, provenance-preserving retrieval from configured research domains."""
from datetime import datetime, timezone
import hashlib
import html
import os
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_DOMAINS = "gold.org,federalreserve.gov,bls.gov,cftc.gov,fred.stlouisfed.org"


class _MainContent(HTMLParser):
    """Prefer a publisher's explicit content region over repeated site menus."""

    def __init__(self):
        super().__init__()
        self.stack = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                       'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, tag == 'main' or attrs.get('role') == 'main'
                               or attrs.get('id') == 'content'))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if any(main for _, main in self.stack) and not any(
                tag in {'script', 'style'} for tag, _ in self.stack):
            self.parts.append(data)


def _excerpt_text(document, fragment=None):
    if fragment:
        # Documentation anchors usually sit on headings. Select through the
        # next heading of equal or higher rank, keeping nested subsections.
        target = re.search(
            r'<(?P<tag>[a-zA-Z][\w:-]*)\b[^>]*\bid\s*=\s*([\"\'])'
            + re.escape(fragment) + r'\2[^>]*>', document)
        if target is None:
            raise ValueError('source_fragment_not_found')
        selected = document[target.start():]
        tag = target.group('tag').lower()
        if re.fullmatch(r'h[1-6]', tag):
            boundary = re.search(r'<h[1-' + tag[1] + r']\b',
                                 selected[target.end() - target.start():], re.I)
            if boundary:
                selected = selected[:target.end() - target.start() + boundary.start()]
        else:
            raise ValueError('source_fragment_not_heading')
        document = selected
    parser = _MainContent()
    parser.feed(document)
    main = re.sub(r'\s+', ' ', ' '.join(parser.parts)).strip()
    if main:
        return main
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", document)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', text))).strip()


def fetch_source(url: str, *, domains: list[str] | None = None) -> dict:
    domains = domains if domains is not None else [v.strip().lower() for v in os.getenv("LAB_RESEARCH_DOMAINS", DEFAULT_DOMAINS).split(",") if v.strip()]
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port not in (None, 443) or not any(
            host == d or host.endswith("." + d) for d in domains):
        raise ValueError("source_domain_not_configured")

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = build_opener(NoRedirect())
    with opener.open(Request(url, headers={"User-Agent": "XAUUSD-Research/1.0"}), timeout=20) as response:
        content_type = response.headers.get("Content-Type", "").lower()
        if not any(t in content_type for t in ("text/", "application/json")):
            raise ValueError("source_format_unsupported")
        body = response.read(256001)
        if len(body) > 256000:
            raise ValueError("source_too_large")
    text = body.decode("utf-8", errors="replace")
    if 'html' in content_type:
        text = _excerpt_text(text, unquote(parsed.fragment))
    else:
        text = re.sub(r'\s+', ' ', text).strip()
    return {"url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "digest": hashlib.sha256(body).hexdigest(), "excerpt": text[:4000],
            "excerpt_truncated": len(text) > 4000, "bytes": len(body), "trusted": False}
