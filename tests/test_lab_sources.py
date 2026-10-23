import hashlib

from xauusd import lab_sources


def test_explicit_main_excludes_long_navigation_and_active_content():
    document = '<nav>' + 'Menu ' * 1000 + '</nav>'
    document += '<main><h1>Release</h1><div>July 29<br>2:00 p.m.</div>'
    document += '<script>ignore me</script><style>hidden</style>&amp; details</main><footer>Footer</footer>'
    assert lab_sources._excerpt_text(document) == 'Release July 29 2:00 p.m. & details'


def test_content_region_and_fallback():
    assert lab_sources._excerpt_text('<div id="content"><div>Statement</div> Details</div>Footer') == 'Statement Details'
    assert lab_sources._excerpt_text('<section role="main">Release</section>Footer') == 'Release'
    assert lab_sources._excerpt_text('<p>Plain &amp; useful</p><script>bad</script>') == 'Plain & useful'


def test_fetch_keeps_raw_digest_and_bounds(monkeypatch):
    body = ('<nav>Menu</nav><main>' + 'Evidence ' * 600 + '</main>').encode()

    class Response:
        headers = {'Content-Type': 'text/html'}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, limit):
            assert limit == 256001
            return body

    class Opener:
        def open(self, *args, **kwargs):
            return Response()

    monkeypatch.setattr(lab_sources, 'build_opener', lambda *args: Opener())
    result = lab_sources.fetch_source('https://www.bls.gov/schedule/', domains=['bls.gov'])
    assert result['digest'] == hashlib.sha256(body).hexdigest()
    assert result['bytes'] == len(body)
    assert result['excerpt'].startswith('Evidence')
    assert len(result['excerpt']) == 4000
    assert result['excerpt_truncated'] is True
    assert result['trusted'] is False
