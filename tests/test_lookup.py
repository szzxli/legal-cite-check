import json

from legalcite.extract import Citation, extract
from legalcite.lookup import (
    CourtListenerClient, build_payload, chunk_citations,
)


def _cite(text):
    return Citation(text=text, volume="576", reporter="U.S.", page="644",
                    case_name=None, year=None, start=0, end=len(text))


def _mock_post_factory(responses, seen):
    """responses: list of (status, body_dict_or_str) returned in order."""
    def post(url, data, headers):
        seen.append({"url": url, "data": data, "headers": dict(headers)})
        status, body = responses.pop(0)
        return status, body if isinstance(body, str) else json.dumps(body)
    return post


def test_payload_default_contains_only_citation_strings():
    text = "My confidential brief about a secret settlement. Obergefell v. Hodges, 576 U.S. 644 (2015)."
    citations = [c for c in extract(text) if c.kind == "full"]
    payload = build_payload(citations, send_full_text=False, full_text=text)
    assert payload == "576 U.S. 644"
    assert "confidential" not in payload
    assert "secret settlement" not in payload
    full = build_payload(citations, send_full_text=True, full_text=text)
    assert full == text


def test_chunking_splits_over_250_and_64000_chars():
    cites = [_cite(f"{i} U.S. {i}") for i in range(1, 302)]
    chunks = chunk_citations(cites)
    assert len(chunks) == 2
    assert len(chunks[0]) == 250 and len(chunks[1]) == 51
    big = [_cite("x" * 70000)]
    assert len(chunk_citations(big)) == 1  # a single over-long line stays one chunk
    many = [_cite("y" * 1000) for _ in range(100)]
    assert len(chunk_citations(many)) == 2  # 64,000-char cap splits it


def test_throttle_61_per_minute_waits():
    clock = [1000.0]
    slept = []

    def now():
        return clock[0]

    def sleep(s):
        slept.append(s)
        clock[0] += s

    client = CourtListenerClient("TOKEN", now_fn=now, sleep_fn=sleep,
                                 post_fn=lambda *a: (200, "[]"))
    # First 60 in one minute: no wait. The 61st must wait.
    client.limiter.wait_if_needed(60)
    assert slept == []
    client.limiter.wait_if_needed(1)
    assert len(slept) == 1 and slept[0] > 0


def test_retry_on_http_429_then_success():
    seen = []
    responses = [
        (429, {"wait_util": "2030-01-01T00:00:00Z"}),
        (200, [{"citation": "576 U.S. 644", "status": 200,
                "clusters": [{"case_name": "Obergefell v. Hodges",
                              "date_filed": "2015-06-26",
                              "absolute_url": "/opinion/123/"}]}]),
    ]
    client = CourtListenerClient("TOKEN", sleep_fn=lambda s: None,
                                 post_fn=_mock_post_factory(responses, seen))
    out = client.lookup_chunk([_cite("576 U.S. 644")])
    assert out[0]["api_status"] == 200
    assert out[0]["matches"][0]["case_name"] == "Obergefell v. Hodges"
    assert out[0]["matches"][0]["url"].startswith("https://www.courtlistener.com")


def test_network_error_is_not_checked_not_not_found():
    def post(*a):
        raise ConnectionError("boom")

    client = CourtListenerClient("TOKEN", post_fn=post)
    out = client.lookup_chunk([_cite("576 U.S. 644")])
    assert out[0]["api_status"] is None


def test_token_never_in_exception_or_body():
    secret = "SECRET_TOKEN_XYZ_123"
    seen = []

    def post(url, data, headers):
        seen.append(data)
        return 401, "unauthorized"

    client = CourtListenerClient(secret, post_fn=post)
    try:
        client.lookup_chunk([_cite("576 U.S. 644")])
        raise AssertionError("expected AuthError")
    except Exception as e:
        assert secret not in str(e)
        assert secret not in repr(e)
    # The request body must not contain the token either.
    assert all(secret.encode() not in d for d in seen)
