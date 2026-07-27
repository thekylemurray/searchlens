from collections import Counter
from typing import Any

from auditor.models import AuditResult


def build_issue_counts(
    page_audits: list[dict[str, Any]],
) -> Counter:
    """Count warnings and failures across all audited pages."""

    issue_counts = Counter()

    for page_audit in page_audits:
        results: list[AuditResult] = page_audit["results"]

        for result in results:
            if result.status in ("warning", "fail"):
                issue_key = (
                    result.name,
                    result.status,
                    result.message,
                )

                issue_counts[issue_key] += 1

    return issue_counts


def count_statuses(
    page_audits: list[dict[str, Any]],
) -> Counter:
    """Count all audit result statuses across the site."""

    status_counts = Counter()

    for page_audit in page_audits:
        results: list[AuditResult] = page_audit["results"]

        for result in results:
            status_counts[result.status] += 1

    return status_counts


def print_ranked_pages(
    page_audits: list[dict[str, Any]],
    *,
    reverse: bool,
    limit: int = 5,
) -> None:
    """Print pages ranked by SEO score."""

    ranked_pages = sorted(
        page_audits,
        key=lambda page: page["score"],
        reverse=reverse,
    )

    for page_audit in ranked_pages[:limit]:
        score = page_audit["score"]
        url = page_audit["url"]

        print(f"  {score:>3}/100  {url}")


def print_site_report(
    page_audits: list[dict[str, Any]],
    failed_pages: list[dict[str, str]],
) -> None:
    """Print a site-wide crawl and SEO audit summary."""

    print()
    print("=" * 70)
    print("SITE AUDIT SUMMARY")
    print("=" * 70)

    if not page_audits:
        print("No pages were successfully audited.")

        if failed_pages:
            print()
            print("Failed Pages")

            for failed_page in failed_pages:
                print(
                    f"  • {failed_page['url']}: "
                    f"{failed_page['error']}"
                )

        return

    average_score = round(
        sum(page["score"] for page in page_audits)
        / len(page_audits)
    )

    status_counts = count_statuses(page_audits)
    issue_counts = build_issue_counts(page_audits)

    print(f"Pages Audited: {len(page_audits)}")
    print(f"Pages Failed:  {len(failed_pages)}")
    print(f"Average Score: {average_score}/100")

    print()
    print("Audit Results")
    print("-" * 70)
    print(f"Pass:     {status_counts['pass']}")
    print(f"Warnings: {status_counts['warning']}")
    print(f"Failures: {status_counts['fail']}")
    print(f"Info:     {status_counts['info']}")

    print()
    print("Most Common Issues")
    print("-" * 70)

    if not issue_counts:
        print("  No warnings or failures were detected.")
    else:
        for (
            check_name,
            status,
            message,
        ), count in issue_counts.most_common(10):
            status_label = status.upper()

            print(
                f"  • {count} page(s) — "
                f"{check_name} [{status_label}]"
            )
            print(f"    {message}")

    print()
    print("Lowest-Scoring Pages")
    print("-" * 70)

    print_ranked_pages(
        page_audits,
        reverse=False,
    )

    print()
    print("Highest-Scoring Pages")
    print("-" * 70)

    print_ranked_pages(
        page_audits,
        reverse=True,
    )

    if failed_pages:
        print()
        print("Pages That Could Not Be Audited")
        print("-" * 70)

        for failed_page in failed_pages:
            print(f"  • {failed_page['url']}")
            print(f"    {failed_page['error']}")

    print("=" * 70)