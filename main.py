import argparse
from pathlib import Path

import requests

from auditor.context import PageContext
from auditor.crawler import crawl_site
from auditor.exporter import export_results
from auditor.fetcher import fetch_page
from auditor.html_reporter import export_html_report
from auditor.reporter import print_report
from auditor.runner import run_all_checks
from auditor.scoring import calculate_score
from auditor.site_reporter import print_site_report


APP_NAME = "SEO Auditor"
VERSION = "0.3.0"


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
        "--json",
        action="store_true",
        dest="export_json",
        help="Export single-page audit results as JSON.",
    )

    parser.add_argument(
        "--html",
        action="store_true",
        dest="export_html",
        help="Export a single-page HTML audit report.",
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

    output_directory = Path(args.output_dir)
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
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


def run_crawl_audit(
    url: str,
    max_pages: int,
) -> None:
    """Crawl and audit multiple pages from one website."""

    print(f"Crawling: {url}")
    print(f"Maximum pages: {max_pages}")
    print()

    discovered_pages = crawl_site(
        url,
        max_pages=max_pages,
    )

    print(
        f"Discovered {len(discovered_pages)} internal page(s)."
    )
    print()

    page_audits = []
    failed_pages = []

    for index, page_url in enumerate(
        discovered_pages,
        start=1,
    ):
        print(
            f"[{index}/{len(discovered_pages)}] "
            f"Auditing {page_url}"
        )

        try:
            context = create_context(page_url)
            results = run_all_checks(context)
            score = calculate_score(results)

        except requests.RequestException as error:
            failed_pages.append(
                {
                    "url": page_url,
                    "error": str(error),
                }
            )

            print(f"  Failed: {error}")
            continue

        page_audits.append(
            {
                "url": context.url,
                "status_code": context.response.status_code,
                "score": score,
                "results": results,
            }
        )

        print(f"  Score: {score}/100")

    print_site_report(
        page_audits=page_audits,
        failed_pages=failed_pages,
    )


def main() -> None:
    """Run the SEO auditor."""

    args = parse_arguments()
    user_url = normalize_url(args.url)

    if args.max_pages < 1:
        raise SystemExit(
            "--max-pages must be greater than zero."
        )

    print(f"{APP_NAME} {VERSION}")
    print()

    try:
        if args.crawl:
            run_crawl_audit(
                url=user_url,
                max_pages=args.max_pages,
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