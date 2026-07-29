from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from auditor import crawler


ROOT_URL = "https://example.com/"


@dataclass
class FakeResponse:
    """Minimal response object needed by the crawler."""

    url: str
    status_code: int = 200


def build_fake_page(
    url: str,
    html: str,
) -> dict:
    """Build a fetch_page-style dictionary for tests."""

    return {
        "response": FakeResponse(url=url),
        "soup": BeautifulSoup(html, "html.parser"),
        "html": html,
    }


def test_normalize_crawl_url_removes_fragment() -> None:
    result = crawler.normalize_crawl_url(
        "https://example.com/about#team"
    )

    assert result == "https://example.com/about"


def test_is_internal_url_accepts_same_domain() -> None:
    assert crawler.is_internal_url(
        "https://example.com/about",
        "example.com",
    )


def test_is_internal_url_rejects_external_domain() -> None:
    assert not crawler.is_internal_url(
        "https://other-example.com/about",
        "example.com",
    )


def test_is_internal_url_rejects_non_http_scheme() -> None:
    assert not crawler.is_internal_url(
        "mailto:person@example.com",
        "example.com",
    )


def test_crawl_site_discovers_internal_pages(
    monkeypatch,
) -> None:
    pages = {
        ROOT_URL: build_fake_page(
            ROOT_URL,
            """
            <html>
                <body>
                    <a href="/about">About</a>
                    <a href="/contact">Contact</a>
                    <a href="https://external.com">External</a>
                </body>
            </html>
            """,
        ),
        "https://example.com/about": build_fake_page(
            "https://example.com/about",
            """
            <html>
                <body>
                    <a href="/">Home</a>
                    <a href="/contact#form">Contact</a>
                </body>
            </html>
            """,
        ),
        "https://example.com/contact": build_fake_page(
            "https://example.com/contact",
            """
            <html>
                <body>
                    <a href="/">Home</a>
                    <a href="mailto:test@example.com">Email</a>
                </body>
            </html>
            """,
        ),
    }

    def fake_fetch_page(url: str) -> dict:
        return pages[url]

    monkeypatch.setattr(
        crawler,
        "fetch_page",
        fake_fetch_page,
    )

    discovery = crawler.crawl_site(
        ROOT_URL,
        max_pages=10,
    )

    assert discovery.pages == [
        ROOT_URL,
        "https://example.com/about",
        "https://example.com/contact",
    ]

    assert (
        ROOT_URL,
        "https://example.com/about",
    ) in discovery.links

    assert (
        "https://example.com/about",
        "https://example.com/contact",
    ) in discovery.links

    assert all(
        "external.com" not in target
        for _, target in discovery.links
    )


def test_crawl_site_respects_max_pages(
    monkeypatch,
) -> None:
    pages = {
        ROOT_URL: build_fake_page(
            ROOT_URL,
            """
            <a href="/one">One</a>
            <a href="/two">Two</a>
            <a href="/three">Three</a>
            """,
        ),
        "https://example.com/one": build_fake_page(
            "https://example.com/one",
            "<a href='/'>Home</a>",
        ),
        "https://example.com/two": build_fake_page(
            "https://example.com/two",
            "<a href='/'>Home</a>",
        ),
        "https://example.com/three": build_fake_page(
            "https://example.com/three",
            "<a href='/'>Home</a>",
        ),
    }

    monkeypatch.setattr(
        crawler,
        "fetch_page",
        lambda url: pages[url],
    )

    discovery = crawler.crawl_site(
        ROOT_URL,
        max_pages=2,
    )

    assert len(discovery.pages) == 2


def test_crawl_site_ignores_duplicate_and_fragment_links(
    monkeypatch,
) -> None:
    pages = {
        ROOT_URL: build_fake_page(
            ROOT_URL,
            """
            <a href="/about">About</a>
            <a href="/about#team">Team</a>
            <a href="/about#history">History</a>
            """,
        ),
        "https://example.com/about": build_fake_page(
            "https://example.com/about",
            "<p>About page</p>",
        ),
    }

    monkeypatch.setattr(
        crawler,
        "fetch_page",
        lambda url: pages[url],
    )

    discovery = crawler.crawl_site(
        ROOT_URL,
        max_pages=10,
    )

    assert discovery.pages.count(
        "https://example.com/about"
    ) == 1

    assert discovery.links.count(
        (
            ROOT_URL,
            "https://example.com/about",
        )
    ) == 1


def test_crawl_site_continues_after_request_failure(
    monkeypatch,
) -> None:
    pages = {
        ROOT_URL: build_fake_page(
            ROOT_URL,
            """
            <a href="/broken">Broken</a>
            <a href="/working">Working</a>
            """,
        ),
        "https://example.com/working": build_fake_page(
            "https://example.com/working",
            "<p>Working page</p>",
        ),
    }

    def fake_fetch_page(url: str) -> dict:
        if url == "https://example.com/broken":
            raise requests.RequestException(
                "Simulated request failure"
            )

        return pages[url]

    monkeypatch.setattr(
        crawler,
        "fetch_page",
        fake_fetch_page,
    )

    discovery = crawler.crawl_site(
        ROOT_URL,
        max_pages=10,
    )

    assert ROOT_URL in discovery.pages

    assert (
        "https://example.com/working"
        in discovery.pages
    )

    assert (
        "https://example.com/broken"
        not in discovery.pages
    )