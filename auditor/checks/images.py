from bs4 import BeautifulSoup

from auditor.models import AuditResult


def check_images(soup: BeautifulSoup) -> AuditResult:
    """Audit images on the page."""

    images = soup.find_all("img")

    image_count = len(images)

    if image_count == 0:
        return AuditResult(
            name="Images",
            status="info",
            message="No images found on the page.",
        )

    missing_alt = []

    for image in images:
        alt = image.get("alt")

        if alt is None or not alt.strip():
            missing_alt.append(
                image.get("src", "(no src attribute)")
            )

    if missing_alt:
        return AuditResult(
            name="Images",
            status="warning",
            message=(
                f"{len(missing_alt)} of {image_count} images "
                "are missing alt text."
            ),
            value=missing_alt,
        )

    return AuditResult(
        name="Images",
        status="pass",
        message=f"All {image_count} images contain alt text.",
    )