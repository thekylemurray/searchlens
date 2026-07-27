import argparse
from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
    as_completed,
)
from pathlib import Path

import requests

from auditor.cli import (
    APP_NAME,
    VERSION,
    parse_arguments,
    validate_arguments,
)
from auditor.context import PageContext
from auditor.crawl_csv_exporter import export_crawl_csv
from auditor.crawl_html_exporter import export_crawl_html_report
from auditor.crawler import crawl_site
from auditor.exporter import export_results
from auditor.fetcher import fetch_page
from auditor.graphviz_exporter import export_link_graph
from auditor.html_reporter import export_html_report
from auditor.models import CrawlAudit, FailedPage, PageAudit
from auditor.reporter import print_report
from auditor.runner import run_all_checks
from auditor.scoring import calculate_score
from auditor.site_reporter import print_site_report


def normalize_url(url: str) -> str:
    """Add an HTTPS scheme when one is not provided."""

    normalized_url = url.strip()

    if not normalized_url.startswith(
        ("http://", "https://")
    ):
        return f"https://{normalized_url}"

    return normalized_url


def create_context(url: str) -> PageContext:
    """Fetch a page and create its shared audit context."""

    page = fetch_page(url)

    return PageContext(
        response=page["response"],
        soup=page["soup"],
        html=page["html"],
    )


def get_output_directory(
    output_dir: str,
) -> Path:
    """Create and return the report output directory."""

    output_directory = Path(output_dir)

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_directory


def audit_page(
    page_url: str,
) -> PageAudit:
    """Fetch and audit one crawled webpage."""

    context = create_context(page_url)
    results = run_all_checks(context)
    score = calculate_score(results)

    return PageAudit(
        url=context.url,
        status_code=context.response.status_code,
        score=score,
        results=results,
    )


def format_unexpected_error(
    error: Exception,
) -> str:
    """Build a readable unexpected-error message."""

    return (
        "Unexpected audit error: "
        f"{type(error).__name__}: {error}"
    )


def audit_pages_concurrently(
    page_urls: list[str],
    workers: int,
) -> tuple[list[PageAudit], list[FailedPage]]:
    """Audit multiple pages concurrently."""

    successful_audits: list[PageAudit] = []
    failed_pages: list[FailedPage] = []

    if not page_urls:
        return successful_audits, failed_pages

    with ThreadPoolExecutor(
        max_workers=workers,
        thread_name_prefix="seo-audit",
    ) as executor:
        future_to_url: dict[
            Future[PageAudit],
            str,
        ] = {
            executor.submit(
                audit_page,
                page_url,
            ): page_url
            for page_url in page_urls
        }

        total_pages = len(future_to_url)

        for completed_count, future in enumerate(
            as_completed(future_to_url),
            start=1,
        ):
            requested_url = future_to_url[future]

            try:
                page_audit = future.result()

            except requests.RequestException as error:
                failed_pages.append(
                    FailedPage(
                        url=requested_url,
                        error=str(error),
                    )
                )

                print(
                    f"[{completed_count}/{total_pages}] "
                    f"Failed {requested_url}"
                )
                print(f"  Error: {error}")

            except Exception as error:
                error_message = format_unexpected_error(
                    error
                )

                failed_pages.append(
                    FailedPage(
                        url=requested_url,
                        error=error_message,
                    )
                )

                print(
                    f"[{completed_count}/{total_pages}] "
                    f"Failed {requested_url}"
                )
                print(f"  {error_message}")

            else:
                successful_audits.append(page_audit)

                print(
                    f"[{completed_count}/{total_pages}] "
                    f"Completed {page_audit.url}"
                )
                print(
                    f"  Score: {page_audit.score}/100"
                )

    successful_audits.sort(
        key=lambda page: page.url.lower()
    )

    failed_pages.sort(
        key=lambda page: page.url.lower()
    )

    return successful_audits, failed_pages


def export_single_page_reports(
    context: PageContext,
    results: list,
    score: int,
    args: argparse.Namespace,
) -> None:
    """Export requested reports for one webpage."""

    if not args.export_json and not args.export_html:
        return

    output_directory = get_output_directory(
        args.output_dir
    )

    if args.export_json:
        json_path = export_results(
            results=results,
            score=score,
            url=context.url,
            output_file=str(
                output_directory / "seo-audit.json"
            ),
        )

        print(f"JSON report saved to: {json_path}")

    if args.export_html:
        html_path = export_html_report(
            results=results,
            score=score,
            url=context.url,
            output_file=str(
                output_directory / "seo-audit.html"
            ),
        )

        print(f"HTML report saved to: {html_path}")


def export_crawl_reports(
    crawl_audit: CrawlAudit,
    args: argparse.Namespace,
) -> None:
    """Export requested crawl reports."""

    exports_requested = any(
        (
            args.export_csv,
            args.export_html,
            args.export_graph,
        )
    )

    if not exports_requested:
        return

    output_directory = get_output_directory(
        args.output_dir
    )

    if args.export_csv:
        csv_path = export_crawl_csv(
            crawl_audit=crawl_audit,
            output_file=str(
                output_directory / "site-audit.csv"
            ),
        )

        print(f"CSV report saved to: {csv_path}")

    if args.export_html:
        html_path = export_crawl_html_report(
            crawl_audit=crawl_audit,
            output_file=str(
                output_directory / "site-audit.html"
            ),
        )

        print(f"HTML dashboard saved to: {html_path}")

    if args.export_graph:
        graph_path = export_link_graph(
            crawl_audit=crawl_audit,
            output_file=str(
                output_directory / "site-graph.dot"
            ),
        )

        print(f"Link graph saved to: {graph_path}")


def run_single_page_audit(
    url: str,
    args: argparse.Namespace,
) -> None:
    """Audit one webpage."""

    print(f"Auditing: {url}")
    print()

    context = create_context(url)

    print(
        f"Status Code: "
        f"{context.response.status_code}"
    )
    print(f"Final URL: {context.url}")
    print()

    results = run_all_checks(context)
    score = calculate_score(results)

    print_report(results)

    export_single_page_reports(
        context=context,
        results=results,
        score=score,
        args=args,
    )


def run_crawl_audit(
    url: str,
    max_pages: int,
    workers: int,
    args: argparse.Namespace,
) -> CrawlAudit:
    """Crawl a website and audit its discovered pages."""

    print(f"Crawling: {url}")
    print(f"Maximum pages: {max_pages}")
    print()

    discovery = crawl_site(
        url,
        max_pages=max_pages,
    )

    print(
        f"Discovered {len(discovery.pages)} "
        "internal page(s)."
    )
    print(
        f"Recorded {len(discovery.links)} "
        "internal link(s)."
    )
    print()

    print(
        f"Auditing with {workers} "
        "concurrent worker(s)."
    )
    print()

    page_audits, failed_pages = (
        audit_pages_concurrently(
            page_urls=discovery.pages,
            workers=workers,
        )
    )

    crawl_audit = CrawlAudit(
        start_url=url,
        pages=page_audits,
        failed_pages=failed_pages,
        link_edges=discovery.links,
    )

    print_site_report(crawl_audit)
    export_crawl_reports(crawl_audit, args)

    return crawl_audit


def run_application(
    args: argparse.Namespace,
) -> None:
    """Run the requested audit mode."""

    user_url = normalize_url(args.url)

    print(f"{APP_NAME} {VERSION}")
    print()

    if args.crawl:
        run_crawl_audit(
            url=user_url,
            max_pages=args.max_pages,
            workers=args.workers,
            args=args,
        )
    else:
        run_single_page_audit(
            url=user_url,
            args=args,
        )


def main() -> None:
    """Parse arguments and start the application."""

    args = parse_arguments()
    validate_arguments(args)

    try:
        run_application(args)

    except requests.RequestException as error:
        raise SystemExit(
            "Unable to retrieve the requested page: "
            f"{error}"
        ) from error