from auditor.models import AuditResult


def check_heading_structure(soup) -> AuditResult:
    """Analyze the page's heading hierarchy."""

    heading_tags = soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6"]
    )

    headings = []

    for tag in heading_tags:
        headings.append(
            {
                "Level": tag.name.upper(),
                "Text": tag.get_text(strip=True),
            }
        )

    counts = {}

    for heading in headings:
        level = heading["Level"]
        counts[level] = counts.get(level, 0) + 1

    previous_level = 0
    skipped_levels = []

    for heading in headings:
        current_level = int(heading["Level"][1])

        if (
            previous_level
            and current_level > previous_level + 1
        ):
            skipped_levels.append(
                f"H{previous_level} → H{current_level}"
            )

        previous_level = current_level

    if not headings:
        status = "warning"
        message = "No headings were found on the page."

    elif skipped_levels:
        status = "warning"
        message = (
            f"{len(skipped_levels)} heading level jump(s) "
            "were detected."
        )

    else:
        status = "pass"
        message = "Heading hierarchy looks consistent."

    return AuditResult(
        name="Heading Structure",
        status=status,
        message=message,
        value={
            "Counts": counts,
            "Heading Order": headings,
            "Skipped Levels": skipped_levels,
        },
    )