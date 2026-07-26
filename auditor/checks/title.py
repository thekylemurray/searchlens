from auditor.models import AuditResult

from auditor.constants import (
    MIN_TITLE_LENGTH,
    MAX_TITLE_LENGTH,
)

def check_title(soup):
    """
    Audit the page title.
    """

    if not soup.title:
        return AuditResult(
            name="Title Tag",
            status="fail",
            message="No title tag found."
        )

    title = soup.title.get_text(strip=True)

    title_length = len(title)

    if title_length < MIN_TITLE_LENGTH:
        return AuditResult(
            name="Title Tag",
            status="warning",
            message=f"Title is too short ({title_length} characters).",
            value=title
        )

    if title_length > MAX_TITLE_LENGTH:
        return AuditResult(
            name="Title Tag",
            status="warning",
            message=f"Title is too long ({title_length} characters).",
            value=title
        )

    return AuditResult(
        name="Title Tag",
        status="pass",
        message=f"Title length is good ({title_length} characters).",
        value=title
    )