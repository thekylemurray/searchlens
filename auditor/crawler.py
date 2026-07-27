from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

import requests

from auditor.fetcher import fetch_page


SKIPPED_SCHEMES = (
    "mailto:",
    "tel:",
    "javascript:",
    "data:",
)


def normalize_crawl_url(url: str) -> str:
    """Remove URL fragments and normalize trailing fragments."""

    clean_url, _ = urldefrag(url)
    return clean_url


def is_internal_url(url: str, start_domain: str) -> bool:
    """Return True when a URL belongs to the starting domain."""

    parsed_url = urlparse(url)

    return (
        parsed_url.scheme in ("http", "https")
        and parsed_url.netloc == start_domain
    )


def crawl_site(
    start_url: str,
    max_pages: int = 25,
) -> list[str]:
    """Discover internal pages using breadth-first crawling."""

    normalized_start_url = normalize_crawl_url(start_url)
    start_domain = urlparse(normalized_start_url).netloc

    queue = deque([normalized_start_url])
    queued = {normalized_start_url}
    visited = set()

    while queue and len(visited) < max_pages:
        current_url = queue.popleft()
        queued.discard(current_url)

        if current_url in visited:
            continue

        try:
            page = fetch_page(current_url)
        except requests.RequestException as error:
            print(f"Could not crawl {current_url}: {error}")
            continue

        final_url = normalize_crawl_url(page["response"].url)

        if not is_internal_url(final_url, start_domain):
            continue

        visited.add(final_url)

        soup = page["soup"]

        for anchor in soup.find_all("a"):
            href = anchor.get("href")

            if not href:
                continue

            href = href.strip()

            if not href or href.startswith(SKIPPED_SCHEMES):
                continue

            absolute_url = urljoin(final_url, href)
            normalized_url = normalize_crawl_url(absolute_url)

            if not is_internal_url(normalized_url, start_domain):
                continue

            if (
                normalized_url not in visited
                and normalized_url not in queued
            ):
                queue.append(normalized_url)
                queued.add(normalized_url)

    return sorted(visited)