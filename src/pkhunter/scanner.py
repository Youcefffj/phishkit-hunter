"""Core scanning engine for PhishKit-Hunter."""

from __future__ import annotations

import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .utils import iter_targets, safe_filename

# Compromised hosts routinely serve broken/self-signed TLS; we scan them anyway.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger("pkhunter")

DEFAULT_USER_AGENT = "PhishKit-Hunter/0.1 (+defensive-research)"


@dataclass
class ScanConfig:
    targets: List[str]
    wordlist: List[str]
    out_dir: str = "captures/"
    log_file: str = "captures/hits.log"
    sentinel: str = "__pkhunter_probe__.html"
    walk_parents: bool = False
    timeout: float = 15.0
    workers: int = 20
    retries: int = 2
    user_agent: str = DEFAULT_USER_AGENT


@dataclass
class ScanResult:
    hits: List[str] = field(default_factory=list)
    scanned: int = 0
    skipped_catch_all: int = 0


def build_session(config: ScanConfig) -> requests.Session:
    """A pooled session with retries and a stable User-Agent."""
    session = requests.Session()
    retry = Retry(
        total=config.retries,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=config.workers)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": config.user_agent})
    session.verify = False
    return session


def _is_catch_all(session: requests.Session, base_url: str, config: ScanConfig) -> bool:
    """True if the decoy sentinel path returns 200 — the host answers 200 to
    everything, so any 'hit' would be a false positive."""
    url = f"{base_url}{config.sentinel}"
    try:
        resp = session.get(
            url, allow_redirects=False, timeout=config.timeout
        )
    except requests.RequestException:
        return False
    return resp.status_code == 200 and bool(resp.content)


def _should_keep(resp: requests.Response) -> bool:
    """Skip dynamic / non-artifact responses (login redirects, JSON APIs...)."""
    if resp.status_code != 200 or not resp.content:
        return False
    cache_control = resp.headers.get("Cache-Control", "")
    content_type = resp.headers.get("Content-Type", "")
    return not (
        "no-cache" in cache_control
        or "private" in cache_control
        or "application/json" in content_type
    )


def _probe_and_save(
    session: requests.Session,
    base_url: str,
    path: str,
    config: ScanConfig,
    lock: threading.Lock,
) -> Optional[str]:
    """Fetch ``base_url + path``; save and log it if it is a real artifact.

    Returns the saved URL on a hit, otherwise ``None``.
    """
    url = f"{base_url}{path}"
    try:
        resp = session.get(url, allow_redirects=False, timeout=config.timeout)
    except requests.RequestException as exc:
        log.debug("error on %s: %s", url, exc)
        return None

    if not _should_keep(resp):
        return None

    filename = safe_filename(url)
    dest = os.path.join(config.out_dir, filename)
    with lock:
        if os.path.exists(dest):
            log.debug("already saved: %s", filename)
            return None
        with open(dest, "wb") as fh:
            fh.write(resp.content)
        with open(config.log_file, "a", encoding="utf-8") as journal:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            journal.write(f"{stamp}\t{url}\t{filename}\n")
    log.info("hit: %s", url)
    return url


def _expand_targets(config: ScanConfig) -> List[str]:
    """Expand targets (optionally walking parents) into a de-duplicated list."""
    seen: set[str] = set()
    expanded: List[str] = []
    for target in config.targets:
        for url in iter_targets(target, config.walk_parents):
            if url not in seen:
                seen.add(url)
                expanded.append(url)
    return expanded


def run_scan(config: ScanConfig) -> ScanResult:
    """Run the full scan and return a :class:`ScanResult`."""
    os.makedirs(config.out_dir, exist_ok=True)
    log_dir = os.path.dirname(config.log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    base_urls = _expand_targets(config)
    session = build_session(config)
    result = ScanResult()

    # Phase 1 — drop catch-all hosts (concurrent).
    good: List[str] = []
    with ThreadPoolExecutor(max_workers=config.workers) as pool:
        futures = {
            pool.submit(_is_catch_all, session, url, config): url
            for url in base_urls
        }
        for future in as_completed(futures):
            url = futures[future]
            if future.result():
                log.info("skip catch-all host: %s", url)
                result.skipped_catch_all += 1
            else:
                good.append(url)

    # Phase 2 — probe the wordlist against surviving hosts (concurrent).
    paths = [p for p in config.wordlist if p != config.sentinel]
    combos = [(url, path) for url in good for path in paths]
    result.scanned = len(combos)
    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=config.workers) as pool:
        futures = [
            pool.submit(_probe_and_save, session, url, path, config, lock)
            for url, path in combos
        ]
        for future in as_completed(futures):
            saved = future.result()
            if saved:
                result.hits.append(saved)

    return result
