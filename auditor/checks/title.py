from bs4 import BeautifulSoup

from auditor.constants import MAX_TITLE_LENGTH, MIN_TITLE_LENGTH
from auditor.models import AuditResult

def check_title(soup: BeautifulSoup) -> AuditResult:
    """Check whether the page has an appropriately sized title tag."""

    if soup.title is None:
        return AuditResult(
            name="Title Tag",
            status="fail",
            message="No title tag found.",
        )

    title = soup.title.get_text(strip=True)

    if not title:
        return AuditResult(
            name="Title Tag",
            status="fail",
            message="The title tag is empty.",
            value=title,
        )

    title_length = len(title)

    if title_length < MIN_TITLE_LENGTH:
        return AuditResult(
            name="Title Tag",
            status="warning",
            message=(
                f"Title is too short "
                f"({title_length} characters; minimum is {MIN_TITLE_LENGTH})."
            ),
            value=title,
        )

    if title_length > MAX_TITLE_LENGTH:
        return AuditResult(
            name="Title Tag",
            status="warning",
            message=(
                f"Title is too long "
                f"({title_length} characters; maximum is {MAX_TITLE_LENGTH})."
            ),
            value=title,
        )

    return AuditResult(
        name="Title Tag",
        status="pass",
        message=f"Title length is good ({title_length} characters).",
        value=title,
    )