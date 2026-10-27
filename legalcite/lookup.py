"""CourtListener citation-lookup client.

Endpoint (confirmed in the Free Law Project wiki, read 2026-10-26):
  POST https://www.courtlistener.com/api/rest/v4/citation-lookup/
  Authorization: Token <user's own token>
  Form field: text=<citation strings, one per line>

Limits (same source): 60 valid citations/minute, 250 citations per
request, 64,000 characters per text request. Per-citation status:
200 found, 300 multiple, 404 not found, 400 invalid reporter, 429 too
many. A throttled HTTP 429 carries a ``wait_util`` key (spelling as in
the wiki); this client also accepts ``wait_until``.

The token is never logged, printed, or included in any result, report,
or exception message. All error messages here are generic on purpose.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE_URL = "https://www.courtlistener.com/api/rest/v4/citation-lookup/"
MAX_PER_REQUEST = 250
MAX_CHARS_PER_REQUEST = 64000
MAX_PER_MINUTE = 60
MAX_RETRIES = 3


class AuthError(Exception):
    """Authentication failed. Message intentionally contains no details."""


class RateLimiter:
    """60 citations per rolling minute, with injectable clock/sleep."""

    def __init__(self, now_fn=None, sleep_fn=None):
        self.now_fn = now_fn or time.time
        self.sleep_fn = sleep_fn or time.sleep
        self._window_start = None
        self._count = 0

    def wait_if_needed(self, n):
        now = self.now_fn()
        if self._window_start is None or now - self._window_start >= 60:
            self._window_start = now
            self._count = 0
        if self._count + n > MAX_PER_MINUTE:
            wait = 60 - (now - self._window_start)
            if wait > 0:
                self.sleep_fn(wait)
            self._window_start = self.now_fn()
            self._count = 0
        self._count += n


def build_payload(citations, send_full_text=False, full_text=None):
    """Request body. Default: ONLY the extracted citation strings.

    With send_full_text=True (off by default, documented, user-opt-in)
    the full text is sent instead. Never both, never anything else.
    """
    if send_full_text:
        return full_text or ""
    return "\n".join(c.text for c in citations)


def chunk_citations(citations):
    """Split into chunks of <=250 citations and <=64,000 payload chars."""
    chunks, current, current_chars = [], [], 0
    for c in citations:
        line = len(c.text) + 1
        if current and (len(current) >= MAX_PER_REQUEST
                        or current_chars + line > MAX_CHARS_PER_REQUEST):
            chunks.append(current)
            current, current_chars = [], 0
        current.append(c)
        current_chars += line
    if current:
        chunks.append(current)
    return chunks


def _parse_wait_seconds(body, now_fn):
    """Parse wait_util / wait_until (ISO-8601) to seconds, if present."""
    for key in ("wait_util", "wait_until"):
        raw = body.get(key) if isinstance(body, dict) else None
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
        except Exception:
            continue
    return None


def _default_post(url, data, headers, timeout=30):
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # network error: caller maps to NOT_CHECKED
        raise ConnectionError("network error") from e


class CourtListenerClient:
    def __init__(self, token, base_url=BASE_URL, post_fn=None,
                 now_fn=None, sleep_fn=None):
        if not token:
            raise ValueError("a CourtListener token is required")
        self._token = token
        self.base_url = base_url
        self.post_fn = post_fn or _default_post
        self.limiter = RateLimiter(now_fn=now_fn, sleep_fn=sleep_fn)
        self.sleep_fn = sleep_fn or time.sleep

    def _post_once(self, payload):
        data = urllib.parse.urlencode({"text": payload}).encode("utf-8")
        headers = {"Authorization": "Token " + self._token}
        return self.post_fn(self.base_url, data, headers)

    def lookup_chunk(self, citations, send_full_text=False, full_text=None):
        """Return a list of per-citation dicts, aligned to `citations`.

        Each dict: {api_status, matches, notes}. api_status None means
        the lookup produced no usable result -> NOT_CHECKED downstream.
        """
        payload = build_payload(citations, send_full_text, full_text)
        self.limiter.wait_if_needed(len(citations))
        status, body = None, ""
        for attempt in range(MAX_RETRIES + 1):
            try:
                status, body = self._post_once(payload)
            except ConnectionError:
                return [{"api_status": None, "matches": [],
                         "notes": ["network error; not checked"]} for _ in citations]
            if status == 429:
                try:
                    parsed = json.loads(body) if body else {}
                except Exception:
                    parsed = {}
                wait = _parse_wait_seconds(parsed, time.time)
                if attempt < MAX_RETRIES:
                    self.sleep_fn(wait if wait is not None else 2.0 * (attempt + 1))
                    continue
                return [{"api_status": 429, "matches": [],
                         "notes": ["rate limited"]} for _ in citations]
            break
        if status in (401, 403):
            raise AuthError("authentication failed")
        if status is None or status >= 500 or status != 200:
            # Any non-200, non-auth outcome without a usable body is
            # missing evidence, never a problem label.
            if status != 200:
                return [{"api_status": None, "matches": [],
                         "notes": ["lookup service did not return a usable result"]}
                        for _ in citations]
        try:
            results = json.loads(body) if body else []
        except Exception:
            return [{"api_status": None, "matches": [],
                     "notes": ["unparseable lookup response"]} for _ in citations]
        out = []
        for i, c in enumerate(citations):
            if i >= len(results) or not isinstance(results[i], dict):
                out.append({"api_status": None, "matches": [],
                            "notes": ["no result for this citation"]})
                continue
            r = results[i]
            matches = []
            for cluster in r.get("clusters") or []:
                if not isinstance(cluster, dict):
                    continue
                url = cluster.get("absolute_url") or ""
                if url.startswith("/"):
                    url = "https://www.courtlistener.com" + url
                matches.append({
                    "case_name": cluster.get("case_name") or "",
                    "date_filed": cluster.get("date_filed") or "",
                    "url": url,
                })
            out.append({"api_status": r.get("status"), "matches": matches,
                        "notes": [r.get("error_message")] if r.get("error_message") else []})
        return out

    def lookup(self, citations, send_full_text=False, full_text=None):
        """Look up full citations only; 'other' kinds are never sent."""
        full = [c for c in citations if c.kind == "full"]
        results = {}
        for chunk in chunk_citations(full):
            for c, r in zip(chunk, self.lookup_chunk(chunk, send_full_text, full_text)):
                results[id(c)] = r
        return results
