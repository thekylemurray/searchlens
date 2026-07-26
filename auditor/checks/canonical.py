from bs4 import BeautifulSoup

from auditor.models import AuditResult


def check_canonical(soup: BeautifulSoup) -> AuditResult:
    """Check for a canonical URL."""

    canonical_tag = soup.find("link", attrs={"rel": "canonical"})

    if canonical_tag is None:
        return AuditResult(
            name="Canonical URL",
            status="fail",
            message="No canonical URL found.",
        )

    canonical_url = canonical_tag.get("href", "").strip()

    if not canonical_url:
        return AuditResult(
            name="Canonical URL",
            status="fail",
            message="Canonical tag exists but has no href.",
        )

    return AuditResult(
        name="Canonical URL",
        status="pass",
        message="Canonical URL found.",
        value=canonical_url,
    )