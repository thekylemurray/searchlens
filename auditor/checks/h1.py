from bs4 import BeautifulSoup

from auditor.models import AuditResult


def check_h1(soup: BeautifulSoup) -> AuditResult:
    """Check the page's H1 tags."""

    h1_tags = soup.find_all("h1")

    h1_text = [
        h1.get_text(strip=True)
        for h1 in h1_tags
    ]

    count = len(h1_text)

    if count == 0:
        return AuditResult(
            name="H1 Tags",
            status="fail",
            message="No H1 tags found."
        )

    if count > 1:
        return AuditResult(
            name="H1 Tags",
            status="warning",
            message=f"{count} H1 tags found. Pages should generally have one H1.",
            value=h1_text
        )

    return AuditResult(
        name="H1 Tags",
        status="pass",
        message="Exactly one H1 tag found.",
        value=h1_text
    )