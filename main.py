import argparse
from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
    as_completed,
)
from pathlib import Path

import requests

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


APP_NAME = "SEO Auditor"
VERSION = "0.8.0"

DEFAULT_WORKERS = 5
MAX_WORKERS = 20


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Audit a webpage or crawl a website for common "
            "technical SEO issues."
        )
    )

    parser.add_argument(
        "url",
        help="The webpage URL to audit.",
    )

    parser.add_argument(
        "--crawl",
        action="store_true",
        help="Crawl the website and audit multiple pages.",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=25,
        help="Maximum number of pages to crawl. Default: 25",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=(
            "Number of pages to audit concurrently in crawl mode. "
            f"Default: {DEFAULT_WORKERS}; maximum: {MAX_WORKERS}"
        ),
    )

    parser.add_argument(
        "--json",
        action="store_true",
        dest="export_json",
        help="Export single-page audit results as JSON.",
    )

    parser.add_argument(
        "--html",
        action="store_true",
        dest="export_html",
        help=(
            "Export an HTML report. In crawl mode, exports "
            "the interactive site dashboard."
        ),
    )

    parser.add_argument(
        "--csv",
        action="store_true",
        dest="export_csv",
        help="Export crawl issues as CSV.",
    )

    parser.add_argument(
        "--graph",
        action="store_true",
        dest="export_graph",
        help="Export the internal link graph as Graphviz DOT.",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default="reports",
        help="Directory for exported reports. Default: reports",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} {VERSION}",
    )

    return parser.parse_args()


def normalize_url(url: str) -> str:
    """Add an HTTPS scheme when one is not provided."""

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        return f"https://{url}"

    return url


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


def run_single_page_audit(
    url: str,
    args: argparse.Namespace,
) -> None:
    """Audit one webpage and optionally export reports."""

    print(f"Auditing: {url}")
    print()

    context = create_context(url)

    print(f"Status Code: {context.response.status_code}")
    print(f"Final URL: {context.url}")
    print()

    results = run_all_checks(context)
    score = calculate_score(results)

    print_report(results)

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


def audit_crawled_page(
    page_url: str,
) -> PageAudit:
    """Fetch and audit one page discovered during a crawl."""

    context = create_context(page_url)
    results = run_all_checks(context)
    score = calculate_score(results)

    return PageAudit(
        url=context.url,
        status_code=context.response.status_code,
        score=score,
        results=results,
    )


def audit_pages_concurrently(
    page_urls: list[str],
    workers: int,
) -> tuple[list[PageAudit], list[FailedPage]]:
    """Audit crawled pages concurrently using a worker pool."""

    page_audits: list[PageAudit] = []
    failed_pages: list[FailedPage] = []

    if not page_urls:
        return page_audits, failed_pages

    future_to_url: dict[Future[PageAudit], str] = {}

    with ThreadPoolExecutor(
        max_workers=workers,
        thread_name_prefix="seo-audit",
    ) as executor:
        for page_url in page_urls:
            future = executor.submit(
                audit_crawled_page,
                page_url,
            )

            future_to_url[future] = page_url

        total_pages = len(future_to_url)

        for completed_count, future in enumerate(
            as_completed(future_to_url),
            start=1,
        ):
            requested_url = future_to_url[future]

            try:
                page_audit = future.result()

            except requests.RequestException as error:
                failed_page = FailedPage(
                    url=requested_url,
                    error=str(error),
                )

                failed_pages.append(failed_page)

                print(
                    f"[{completed_count}/{total_pages}] "
                    f"Failed {requested_url}"
                )
                print(f"  Error: {error}")

            except Exception as error:
                failed_page = FailedPage(
                    url=requested_url,
                    error=(
                        f"Unexpected audit error: "
                        f"{type(error).__name__}: {error}"
                    ),
                )

                failed_pages.append(failed_page)

                print(
                    f"[{completed_count}/{total_pages}] "
                    f"Failed {requested_url}"
                )
                print(
                    f"  Unexpected error: "
                    f"{type(error).__name__}: {error}"
                )

            else:
                page_audits.append(page_audit)

                print(
                    f"[{completed_count}/{total_pages}] "
                    f"Completed {page_audit.url}"
                )
                print(
                    f"  Score: {page_audit.score}/100"
                )

    page_audits.sort(
        key=lambda page: page.url.lower()
    )

    failed_pages.sort(
        key=lambda page: page.url.lower()
    )

    return page_audits, failed_pages


def export_crawl_reports(
    crawl_audit: CrawlAudit,
    args: argparse.Namespace,
) -> None:
    """Export requested crawl reports."""

    if not any(
        [
            args.export_csv,
            args.export_html,
            args.export_graph,
        ]
    ):
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
        f"Discovered {len(discovery.pages)} internal page(s)."
    )
    print(
        f"Recorded {len(discovery.links)} internal link(s)."
    )
    print()

    print(
        f"Auditing with {workers} concurrent worker(s)."
    )
    print()

    page_audits, failed_pages = audit_pages_concurrently(
        page_urls=discovery.pages,
        workers=workers,
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


def validate_arguments(
    args: argparse.Namespace,
) -> None:
    """Validate combinations of command-line arguments."""

    if args.max_pages < 1:
        raise SystemExit(
            "--max-pages must be greater than zero."
        )

    if args.workers < 1:
        raise SystemExit(
            "--workers must be greater than zero."
        )

    if args.workers > MAX_WORKERS:
        raise SystemExit(
            f"--workers cannot exceed {MAX_WORKERS}."
        )

    if args.export_csv and not args.crawl:
        raise SystemExit(
            "--csv can only be used together with --crawl."
        )

    if args.export_graph and not args.crawl:
        raise SystemExit(
            "--graph can only be used together with --crawl."
        )

    if args.export_json and args.crawl:
        raise SystemExit(
            "Crawl-mode JSON export is not supported yet."
        )

    if (
        not args.crawl
        and args.workers != DEFAULT_WORKERS
    ):
        raise SystemExit(
            "--workers can only be customized in crawl mode."
        )


def main() -> None:
    """Run the SEO auditor."""

    args = parse_arguments()
    validate_arguments(args)

    user_url = normalize_url(args.url)

    print(f"{APP_NAME} {VERSION}")
    print()

    try:
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

    except requests.RequestException as error:
        raise SystemExit(
            f"Unable to retrieve the requested page: {error}"
        ) from error


if __name__ == "__main__":
    main()