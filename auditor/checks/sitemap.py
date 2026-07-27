from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import requests

from auditor.models import AuditResult


def get_site_root(page_url: str) -> str:
    """Return the scheme and hostname for a webpage URL."""

    parsed_url = urlparse(page_url)

    return f"{parsed_url.scheme}://{parsed_url.netloc}/"


def extract_sitemap_urls(robots_text: str) -> list[str]:
    """Extract sitemap declarations from robots.txt."""

    sitemap_urls = []

    for line in robots_text.splitlines():
        stripped_line = line.strip()

        if stripped_line.lower().startswith("sitemap:"):
            sitemap_url = stripped_line.split(":", 1)[1].strip()

            if sitemap_url:
                sitemap_urls.append(sitemap_url)

    return sitemap_urls


def find_sitemap_urls(page_url: str) -> list[str]:
    """Find declared sitemap URLs or fall back to /sitemap.xml."""

    site_root = get_site_root(page_url)
    robots_url = urljoin(site_root, "robots.txt")

    try:
        response = requests.get(
            robots_url,
            timeout=10,
            headers={"User-Agent": "SEO-Auditor/0.2.0"},
        )

        if response.status_code == 200:
            sitemap_urls = extract_sitemap_urls(response.text)

            if sitemap_urls:
                return sitemap_urls

    except requests.RequestException:
        pass

    return [urljoin(site_root, "sitemap.xml")]


def get_xml_root_name(root: ElementTree.Element) -> str:
    """Return an XML element name without its namespace."""

    return root.tag.split("}")[-1].lower()


def count_sitemap_entries(root: ElementTree.Element) -> int:
    """Count URLs or nested sitemaps in a sitemap document."""

    root_name = get_xml_root_name(root)

    if root_name == "urlset":
        return sum(
            1
            for element in root
            if get_xml_root_name(element) == "url"
        )

    if root_name == "sitemapindex":
        return sum(
            1
            for element in root
            if get_xml_root_name(element) == "sitemap"
        )

    return 0


def validate_sitemap(sitemap_url: str) -> dict:
    """Fetch and validate one sitemap URL."""

    result = {
        "url": sitemap_url,
        "status code": None,
        "type": None,
        "entries": 0,
        "valid": False,
        "error": None,
    }

    try:
        response = requests.get(
            sitemap_url,
            timeout=15,
            headers={"User-Agent": "SEO-Auditor/0.2.0"},
        )
    except requests.RequestException as error:
        result["error"] = str(error)
        return result

    result["status code"] = response.status_code

    if response.status_code != 200:
        result["error"] = (
            f"Sitemap returned HTTP {response.status_code}."
        )
        return result

    try:
        root = ElementTree.fromstring(response.content)
    except ElementTree.ParseError as error:
        result["error"] = f"Invalid XML: {error}"
        return result

    sitemap_type = get_xml_root_name(root)

    if sitemap_type not in {"urlset", "sitemapindex"}:
        result["error"] = (
            f"Unexpected XML root element: {sitemap_type}"
        )
        return result

    entry_count = count_sitemap_entries(root)

    result["type"] = sitemap_type
    result["entries"] = entry_count
    result["valid"] = entry_count > 0

    if entry_count == 0:
        result["error"] = "Sitemap contains no entries."

    return result


def check_sitemap(page_url: str) -> AuditResult:
    """Find and validate the site's sitemap files."""

    sitemap_urls = find_sitemap_urls(page_url)

    sitemap_results = [
        validate_sitemap(sitemap_url)
        for sitemap_url in sitemap_urls
    ]

    valid_sitemaps = [
        result
        for result in sitemap_results
        if result["valid"]
    ]

    invalid_sitemaps = [
        result
        for result in sitemap_results
        if not result["valid"]
    ]

    if not valid_sitemaps:
        return AuditResult(
            name="Sitemap",
            status="warning",
            message="No valid sitemap could be found.",
            value={
                "checked": sitemap_results,
            },
        )

    if invalid_sitemaps:
        return AuditResult(
            name="Sitemap",
            status="warning",
            message=(
                f"{len(valid_sitemaps)} valid and "
                f"{len(invalid_sitemaps)} invalid sitemap files were found."
            ),
            value={
                "valid": valid_sitemaps,
                "invalid": invalid_sitemaps,
            },
        )

    total_entries = sum(
        result["entries"]
        for result in valid_sitemaps
    )

    return AuditResult(
        name="Sitemap",
        status="pass",
        message=(
            f"{len(valid_sitemaps)} valid sitemap "
            f"{'file was' if len(valid_sitemaps) == 1 else 'files were'} "
            f"found with {total_entries} total entries."
        ),
        value={
            "sitemaps": valid_sitemaps,
        },
    )