from bs4 import BeautifulSoup

from auditor.models import AuditResult


def check_robots(soup: BeautifulSoup) -> AuditResult:
    """Check the page's robots meta directives."""

    robots_tag = soup.find("meta", attrs={"name": "robots"})

    if robots_tag is None:
        return AuditResult(
            name="Robots Meta Tag",
            status="info",
            message=(
                "No robots meta tag found. Search engines will generally "
                "use their default indexing behavior."
            ),
        )

    directives = robots_tag.get("content", "").strip()

    if not directives:
        return AuditResult(
            name="Robots Meta Tag",
            status="warning",
            message="The robots meta tag exists but has no content.",
        )

    normalized_directives = directives.lower()

    if "noindex" in normalized_directives:
        return AuditResult(
            name="Robots Meta Tag",
            status="warning",
            message="The page contains a noindex directive.",
            value=directives,
        )

    return AuditResult(
        name="Robots Meta Tag",
        status="pass",
        message="No blocking index directive was found.",
        value=directives,
    )