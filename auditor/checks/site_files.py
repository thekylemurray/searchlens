from urllib.parse import urljoin, urlparse

import requests

from auditor.models import AuditResult


def get_site_root(page_url: str) -> str:
    """Return the scheme and hostname for a webpage URL."""

    parsed_url = urlparse(page_url)

    return f"{parsed_url.scheme}://{parsed_url.netloc}/"


def check_site_files(page_url: str) -> AuditResult:
    """Check for robots.txt and sitemap declarations."""

    site_root = get_site_root(page_url)
    robots_url = urljoin(site_root, "robots.txt")

    try:
        robots_response = requests.get(
            robots_url,
            timeout=10,
            headers={
                "User-Agent": "SEO-Auditor/0.2.0"
            },
        )
    except requests.RequestException as error:
        return AuditResult(
            name="Site Files",
            status="warning",
            message="Could not retrieve robots.txt.",
            value=str(error),
        )

    if robots_response.status_code != 200:
        return AuditResult(
            name="Site Files",
            status="warning",
            message=(
                f"robots.txt returned status "
                f"{robots_response.status_code}."
            ),
            value={
                "robots URL": robots_url,
            },
        )

    robots_text = robots_response.text
    sitemap_urls = []

    for line in robots_text.splitlines():
        stripped_line = line.strip()

        if stripped_line.lower().startswith("sitemap:"):
            sitemap_url = stripped_line.split(":", 1)[1].strip()

            if sitemap_url:
                sitemap_urls.append(sitemap_url)

    if sitemap_urls:
        return AuditResult(
            name="Site Files",
            status="pass",
            message="robots.txt was found and declares a sitemap.",
            value={
                "robots URL": robots_url,
                "sitemaps": sitemap_urls,
            },
        )

    default_sitemap_url = urljoin(site_root, "sitemap.xml")

    return AuditResult(
        name="Site Files",
        status="warning",
        message=(
            "robots.txt was found, but no sitemap declaration "
            "was detected."
        ),
        value={
            "robots URL": robots_url,
            "suggested sitemap URL": default_sitemap_url,
        },
    )