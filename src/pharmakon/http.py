"""One shared HTTP client: on-disk cache, retries with backoff, polite per-host rate limits."""

from __future__ import annotations

import threading
import time
from typing import Any
from urllib.parse import urlparse

import requests
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pharmakon.common import CACHE, env

USER_AGENT = (
    "Pharmakon/0.1 (EthnoHack 2026 research pipeline; "
    "https://github.com/LSUDOKO/Pharmakon) python-requests"
)

# Minimum seconds between requests per host.
_RATE = {
    "eutils.ncbi.nlm.nih.gov": 0.11 if env("NCBI_API_KEY") else 0.35,
    "query.wikidata.org": 1.0,
    "query-scholarly.wikidata.org": 1.0,
    "api.gbif.org": 0.1,
    "www.ebi.ac.uk": 0.2,
    "id.nlm.nih.gov": 0.2,
    "api.platform.opentargets.org": 0.2,
    "en.wikipedia.org": 0.5,
}
_last: dict[str, float] = {}
_lock = threading.Lock()
_session: requests_cache.CachedSession | None = None


def session() -> requests_cache.CachedSession:
    global _session
    if _session is None:
        CACHE.mkdir(parents=True, exist_ok=True)
        s = requests_cache.CachedSession(
            str(CACHE / "http"),
            backend="sqlite",
            allowable_methods=("GET", "POST"),
            allowable_codes=(200, 404),
            expire_after=-1,  # research snapshot: never expire; clear cache to refresh
            stale_if_error=True,
        )
        retry = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "POST"}),
            respect_retry_after_header=True,
        )
        s.mount("https://", HTTPAdapter(max_retries=retry))
        s.headers.update({"User-Agent": USER_AGENT})
        _session = s
    return _session


def _throttle(url: str) -> None:
    host = urlparse(url).netloc
    gap = _RATE.get(host, 0.1)
    with _lock:
        wait = _last.get(host, 0.0) + gap - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.monotonic()


def get(url: str, params: dict[str, Any] | None = None, timeout: int = 60, **kw: Any) -> requests.Response:
    s = session()
    req = requests.Request("GET", url, params=params, headers=kw.pop("headers", None)).prepare()
    if not s.cache.contains(request=req):
        _throttle(url)
    r = s.get(url, params=params, timeout=timeout, headers=req.headers, **kw)
    return r


def post(url: str, json: Any = None, data: Any = None, timeout: int = 60, **kw: Any) -> requests.Response:
    s = session()
    req = requests.Request("POST", url, json=json, data=data, headers=kw.pop("headers", None)).prepare()
    if not s.cache.contains(request=req):
        _throttle(url)
    return s.post(url, json=json, data=data, timeout=timeout, headers=req.headers, **kw)


def get_json(url: str, params: dict[str, Any] | None = None, **kw: Any) -> Any:
    r = get(url, params=params, **kw)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def sparql(query: str, endpoint: str = "https://query.wikidata.org/sparql") -> list[dict[str, Any]]:
    r = get(endpoint, params={"query": query, "format": "json"}, headers={"Accept": "application/sparql-results+json"}, timeout=90)
    r.raise_for_status()
    out = []
    for b in r.json()["results"]["bindings"]:
        out.append({k: v.get("value") for k, v in b.items()})
    return out


def download(url: str, dest: str, timeout: int = 120) -> str:
    """Stream a file to disk (not cached in sqlite)."""
    _throttle(url)
    with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": USER_AGENT}) as r:
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(1 << 16):
                fh.write(chunk)
    return dest
