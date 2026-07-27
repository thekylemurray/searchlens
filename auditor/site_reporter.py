from collections import Counter

from auditor.models import CrawlAudit, PageAudit


IssueKey = tuple[str, str, str]


def build_issue_counts(
    crawl_audit: CrawlAudit,
) -> Counter[IssueKey]:
    """Count warnings and failures across all audited pages."""

    issue_counts: Counter[IssueKey] = Counter()

    for page_audit in crawl_audit.pages:
        for result in page_audit.results:
            if result.status not in ("warning", "fail"):
                continue

            issue_key = (
                result.name,
                result.status,
                result.message,
            )

            issue_counts[issue_key] += 1

    return issue_counts


def count_statuses(
    crawl_audit: CrawlAudit,
) -> Counter[str]:
    """Count all audit result statuses across the site."""

    status_counts: Counter[str] = Counter()

    for page_audit in crawl_audit.pages:
        for result in page_audit.results:
            status_counts[result.status] += 1

    return status_counts


def print_ranked_pages(
    pages: list[PageAudit],
    *,
    reverse: bool,
    limit: int = 5,
) -> None:
    """Print pages ranked by SEO score."""

    ranked_pages = sorted(
        pages,
        key=lambda page: page.score,
        reverse=reverse,
    )

    for page_audit in ranked_pages[:limit]:
        print(
            f"  {page_audit.score:>3}/100  "
            f"{page_audit.url}"
        )


def print_site_report(
    crawl_audit: CrawlAudit,
) -> None:
    """Print a site-wide crawl and SEO audit summary."""

    print()
    print("=" * 70)
    print("SITE AUDIT SUMMARY")
    print("=" * 70)

    if not crawl_audit.pages:
        print("No pages were successfully audited.")

        if crawl_audit.failed_pages:
            print()
            print("Failed Pages")
            print("-" * 70)

            for failed_page in crawl_audit.failed_pages:
                print(
                    f"  • {failed_page.url}: "
                    f"{failed_page.error}"
                )

        return

    status_counts = count_statuses(crawl_audit)
    issue_counts = build_issue_counts(crawl_audit)

    print(f"Website:       {crawl_audit.start_url}")
    print(f"Pages Audited: {crawl_audit.pages_audited}")
    print(f"Pages Failed:  {crawl_audit.pages_failed}")
    print(f"Average Score: {crawl_audit.average_score}/100")

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
        for issue, count in issue_counts.most_common(10):
            check_name, status, message = issue

            print(
                f"  • {count} page(s) — "
                f"{check_name} [{status.upper()}]"
            )
            print(f"    {message}")

    print()
    print("Lowest-Scoring Pages")
    print("-" * 70)

    print_ranked_pages(
        crawl_audit.pages,
        reverse=False,
    )

    print()
    print("Highest-Scoring Pages")
    print("-" * 70)

    print_ranked_pages(
        crawl_audit.pages,
        reverse=True,
    )

    if crawl_audit.failed_pages:
        print()
        print("Pages That Could Not Be Audited")
        print("-" * 70)

        for failed_page in crawl_audit.failed_pages:
            print(f"  • {failed_page.url}")
            print(f"    {failed_page.error}")

    print("=" * 70)