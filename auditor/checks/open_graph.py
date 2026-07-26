from bs4 import BeautifulSoup

from auditor.models import AuditResult


REQUIRED_OG_TAGS = {
    "og:title": "Title",
    "og:description": "Description",
    "og:image": "Image",
    "og:url": "URL",
}


def check_open_graph(soup: BeautifulSoup) -> AuditResult:
    """Check for important Open Graph metadata."""

    found_tags = {}
    missing_tags = []

    for property_name, label in REQUIRED_OG_TAGS.items():
        tag = soup.find("meta", attrs={"property": property_name})

        if tag is None:
            missing_tags.append(property_name)
            continue

        content = tag.get("content", "").strip()

        if not content:
            missing_tags.append(property_name)
            continue

        found_tags[label] = content

    if not found_tags:
        return AuditResult(
            name="Open Graph",
            status="warning",
            message="No required Open Graph tags were found.",
            value=missing_tags,
        )

    if missing_tags:
        return AuditResult(
            name="Open Graph",
            status="warning",
            message=(
                f"{len(missing_tags)} required Open Graph "
                f"{'tag is' if len(missing_tags) == 1 else 'tags are'} missing."
            ),
            value={
                "found": found_tags,
                "missing": missing_tags,
            },
        )

    return AuditResult(
        name="Open Graph",
        status="pass",
        message="All required Open Graph tags were found.",
        value=found_tags,
    )