from bs4 import BeautifulSoup

from auditor.constants import (
    MAX_DESCRIPTION_LENGTH,
    MIN_DESCRIPTION_LENGTH,
)
from auditor.models import AuditResult


def check_meta_description(soup: BeautifulSoup) -> AuditResult:
    """Check whether the page has an appropriately sized meta description."""

    meta_tag = soup.find("meta", attrs={"name": "description"})

    if meta_tag is None:
        return AuditResult(
            name="Meta Description",
            status="fail",
            message="No meta description tag found.",
        )

    description = meta_tag.get("content", "").strip()

    if not description:
        return AuditResult(
            name="Meta Description",
            status="fail",
            message="The meta description tag is empty.",
            value=description,
        )

    description_length = len(description)

    if description_length < MIN_DESCRIPTION_LENGTH:
        return AuditResult(
            name="Meta Description",
            status="warning",
            message=(
                f"Description is too short "
                f"({description_length} characters; "
                f"minimum is {MIN_DESCRIPTION_LENGTH})."
            ),
            value=description,
        )

    if description_length > MAX_DESCRIPTION_LENGTH:
        return AuditResult(
            name="Meta Description",
            status="warning",
            message=(
                f"Description is too long "
                f"({description_length} characters; "
                f"maximum is {MAX_DESCRIPTION_LENGTH})."
            ),
            value=description,
        )

    return AuditResult(
        name="Meta Description",
        status="pass",
        message=(
            f"Description length is good "
            f"({description_length} characters)."
        ),
        value=description,
    )