from bs4 import BeautifulSoup

from auditor.models import AuditResult


REQUIRED_TWITTER_TAGS = {
    "twitter:card": "Card Type",
    "twitter:title": "Title",
    "twitter:description": "Description",
    "twitter:image": "Image",
}


def find_twitter_tag(
    soup: BeautifulSoup,
    tag_name: str,
) -> str | None:
    """Find a Twitter Card meta tag and return its content."""

    tag = soup.find("meta", attrs={"name": tag_name})

    if tag is None:
        tag = soup.find("meta", attrs={"property": tag_name})

    if tag is None:
        return None

    content = tag.get("content", "").strip()

    return content or None


def check_twitter_cards(soup: BeautifulSoup) -> AuditResult:
    """Check for important Twitter Card metadata."""

    found_tags = {}
    missing_tags = []

    for tag_name, label in REQUIRED_TWITTER_TAGS.items():
        content = find_twitter_tag(soup, tag_name)

        if content is None:
            missing_tags.append(tag_name)
        else:
            found_tags[label] = content

    if not found_tags:
        return AuditResult(
            name="Twitter Cards",
            status="info",
            message="No Twitter Card metadata was found.",
            value=missing_tags,
        )

    if missing_tags:
        missing_count = len(missing_tags)
        tag_word = "tag is" if missing_count == 1 else "tags are"

        return AuditResult(
            name="Twitter Cards",
            status="warning",
            message=(
                f"{missing_count} recommended Twitter Card "
                f"{tag_word} missing."
            ),
            value={
                "found": found_tags,
                "missing": missing_tags,
            },
        )

    return AuditResult(
        name="Twitter Cards",
        status="pass",
        message="All recommended Twitter Card tags were found.",
        value=found_tags,
    )