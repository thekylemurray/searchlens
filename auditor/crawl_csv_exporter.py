import csv
from pathlib import Path

from auditor.models import CrawlAudit


def export_crawl_csv(
    crawl_audit: CrawlAudit,
    output_file: str,
) -> str:
    """Export crawl audit issues and failed pages to CSV."""

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "URL",
        "Status Code",
        "Score",
        "Check",
        "Result Status",
        "Message",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for page_audit in crawl_audit.pages:
            issues = [
                result
                for result in page_audit.results
                if result.status in ("warning", "fail")
            ]

            if not issues:
                writer.writerow(
                    {
                        "URL": page_audit.url,
                        "Status Code": page_audit.status_code,
                        "Score": page_audit.score,
                        "Check": "No issues",
                        "Result Status": "pass",
                        "Message": (
                            "No warnings or failures were detected."
                        ),
                    }
                )

                continue

            for result in issues:
                writer.writerow(
                    {
                        "URL": page_audit.url,
                        "Status Code": page_audit.status_code,
                        "Score": page_audit.score,
                        "Check": result.name,
                        "Result Status": result.status,
                        "Message": result.message,
                    }
                )

        for failed_page in crawl_audit.failed_pages:
            writer.writerow(
                {
                    "URL": failed_page.url,
                    "Status Code": "",
                    "Score": "",
                    "Check": "Page Fetch",
                    "Result Status": "fail",
                    "Message": failed_page.error,
                }
            )

    return str(output_path)