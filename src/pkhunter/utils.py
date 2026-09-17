"""Pure helpers: no I/O, no network — easy to unit-test."""

from __future__ import annotations

import re
from typing import Iterator, List

# Characters that are illegal in filenames on common filesystems.
_ILLEGAL = re.compile(r'[\\/:*?"<>|]')

# A trailing "/name.ext" segment, e.g. the final file part of a URL.
_TRAILING_FILE = re.compile(r"/[^/]+\.[a-zA-Z0-9]+$")


def safe_filename(url: str) -> str:
    """Turn a full URL into a filesystem-safe filename."""
    return _ILLEGAL.sub("", url)


def iter_targets(url: str, walk_parents: bool = False) -> Iterator[str]:
    """Yield the URL, and — when ``walk_parents`` — each parent directory.

    Walking stops once fewer than three ``/`` remain (i.e. once we reach the
    host root ``https://host/``), guarding against an infinite loop.
    """
    if not walk_parents:
        yield url
        return

    seen: set[str] = set()
    current = url
    while current.count("/") >= 3 and current not in seen:
        seen.add(current)
        yield current
        current = current.rstrip("/")
        idx = current.rfind("/")
        if idx == -1:
            break
        current = current[: idx + 1]  # keep the trailing '/' -> parent dir


def strip_trailing_file(url: str) -> str:
    """Drop a trailing ``/file.ext`` and guarantee a trailing slash."""
    url = url.strip()
    match = _TRAILING_FILE.search(url)
    if match:
        url = url[: match.start() + 1]
    if not url.endswith("/"):
        url += "/"
    return url


def clean_url_list(urls: List[str]) -> List[str]:
    """Normalise a raw URL list for scanning.

    Steps: strip trailing filenames, drop duplicates (order-preserving), and
    remove any URL that is a strict prefix of another (keep the deepest paths).
    """
    normalised = [strip_trailing_file(u) for u in urls if u.strip()]
    normalised = list(dict.fromkeys(normalised))  # de-dup, keep order

    result: List[str] = []
    for i, url in enumerate(normalised):
        contained = any(
            i != j and other.startswith(url)
            for j, other in enumerate(normalised)
        )
        if not contained:
            result.append(url)
    return result
