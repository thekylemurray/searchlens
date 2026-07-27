from urllib.parse import urljoin, urlparse

from auditor.context import PageContext
from auditor.models import AuditResult


def check_links(context: PageContext) -> AuditResult:
    """Analyze internal and external links on the current page."""

    anchors = context.soup.find_all("a")

    internal = 0
    external = 0
    nofollow = 0
    missing_href = 0
    empty_text = 0

    internal_urls = set()
    external_urls = set()

    current_domain = urlparse(context.url).netloc

    for anchor in anchors:
        href = anchor.get("href")

        if not href:
            missing_href += 1
            continue

        absolute_url = urljoin(context.url, href)
        link_domain = urlparse(absolute_url).netloc

        if link_domain == current_domain:
            internal += 1
            internal_urls.add(absolute_url)
        else:
            external += 1
            external_urls.add(absolute_url)

        rel = anchor.get("rel", [])

        if "nofollow" in rel:
            nofollow += 1

        if not anchor.get_text(strip=True):
            empty_text += 1

    if missing_href > 0:
        status = "warning"
        message = f"{missing_href} link(s) are missing an href."

    elif empty_text > 0:
        status = "warning"
        message = f"{empty_text} link(s) have empty anchor text."

    else:
        status = "pass"
        message = f"Found {len(anchors)} links."

    return AuditResult(
        name="Links",
        status=status,
        message=message,
        value={
            "Total Links": len(anchors),
            "Internal": internal,
            "External": external,
            "Unique Internal": len(internal_urls),
            "Unique External": len(external_urls),
            "nofollow": nofollow,
            "Missing href": missing_href,
            "Empty Anchor Text": empty_text,
        },
    )