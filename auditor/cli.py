import argparse


APP_NAME = "SEO Auditor"
VERSION = "0.9.0"

DEFAULT_MAX_PAGES = 25
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
        default=DEFAULT_MAX_PAGES,
        help=(
            "Maximum number of pages to crawl. "
            f"Default: {DEFAULT_MAX_PAGES}"
        ),
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
        help="Export the internal-link graph as Graphviz DOT.",
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


def validate_arguments(
    args: argparse.Namespace,
) -> None:
    """Validate command-line arguments and option combinations."""

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