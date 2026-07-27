import argparse
from pathlib import Path

from auditor.context import PageContext
from auditor.exporter import export_results
from auditor.fetcher import fetch_page
from auditor.html_reporter import export_html_report
from auditor.reporter import print_report
from auditor.runner import run_all_checks
from auditor.scoring import calculate_score


APP_NAME = "SEO Auditor"
VERSION = "0.2.0"


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Audit a webpage for common technical SEO issues."
    )

    parser.add_argument(
        "url",
        help="The webpage URL to audit.",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        dest="export_json",
        help="Export the audit results as JSON.",
    )

    parser.add_argument(
        "--html",
        action="store_true",
        dest="export_html",
        help="Export the audit results as an HTML report.",
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
    """Add an HTTPS scheme when the user does not provide one."""

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        return f"https://{url}"

    return url


def main() -> None:
    """Run the SEO auditor."""

    args = parse_arguments()
    user_url = normalize_url(args.url)

    print(f"{APP_NAME} {VERSION}")
    print(f"Auditing: {user_url}")
    print()

    page = fetch_page(user_url)

    context = PageContext(
    response=page["response"],
    soup=page["soup"],
    html=page["html"],
    )

    print(f"Status Code: {context.response.status_code}")
    print(f"Final URL: {context.url}")

    results = run_all_checks(context)
    print_report(results)

    score = calculate_score(results)

    if args.export_json or args.export_html:
        output_directory = Path(args.output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)

        if args.export_json:
            json_path = export_results(
                results=results,
                score=score,
                url=context.url,
                output_file=str(output_directory / "seo-audit.json"),
            )

            print(f"JSON report saved to: {json_path}")

        if args.export_html:
            html_path = export_html_report(
                results=results,
                score=score,
                url=context.url,
                output_file=str(output_directory / "seo-audit.html"),
            )

            print(f"HTML report saved to: {html_path}")


if __name__ == "__main__":
    main()