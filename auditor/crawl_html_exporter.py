from collections import Counter, defaultdict
from datetime import datetime
from html import escape
from pathlib import Path
from typing import DefaultDict

from auditor.models import CrawlAudit, PageAudit


IssueKey = tuple[str, str, str]


def count_result_statuses(
    crawl_audit: CrawlAudit,
) -> Counter[str]:
    """Count result statuses across all successfully audited pages."""

    counts: Counter[str] = Counter()

    for page in crawl_audit.pages:
        for result in page.results:
            counts[result.status] += 1

    return counts


def build_issue_groups(
    crawl_audit: CrawlAudit,
) -> DefaultDict[IssueKey, list[str]]:
    """Group warnings and failures by check, status, and message."""

    issue_groups: DefaultDict[IssueKey, list[str]] = defaultdict(list)

    for page in crawl_audit.pages:
        for result in page.results:
            if result.status not in ("warning", "fail"):
                continue

            key = (
                result.name,
                result.status,
                result.message,
            )

            issue_groups[key].append(page.url)

    return issue_groups


def get_score_class(score: int) -> str:
    """Return a CSS class for a numerical SEO score."""

    if score >= 95:
        return "score-good"

    if score >= 80:
        return "score-warning"

    return "score-poor"


def get_status_class(status: str) -> str:
    """Return a CSS class for an audit-result status."""

    return {
        "pass": "status-pass",
        "warning": "status-warning",
        "fail": "status-fail",
        "info": "status-info",
    }.get(status, "status-info")


def count_page_issues(
    page: PageAudit,
) -> tuple[int, int]:
    """Return warning and failure counts for one page."""

    warnings = 0
    failures = 0

    for result in page.results:
        if result.status == "warning":
            warnings += 1
        elif result.status == "fail":
            failures += 1

    return warnings, failures


def build_summary_card(
    label: str,
    value: str | int,
    modifier_class: str = "",
) -> str:
    """Build one summary card."""

    classes = "summary-card"

    if modifier_class:
        classes += f" {modifier_class}"

    return f"""
        <article class="{escape(classes)}">
            <span class="summary-label">
                {escape(label)}
            </span>

            <strong class="summary-value">
                {escape(str(value))}
            </strong>
        </article>
    """


def build_ranked_page_rows(
    pages: list[PageAudit],
    *,
    reverse: bool,
    limit: int = 5,
) -> str:
    """Build rows for a highest- or lowest-scoring page table."""

    ranked_pages = sorted(
        pages,
        key=lambda page: (
            page.score,
            page.url.lower(),
        ),
        reverse=reverse,
    )

    rows = []

    for page in ranked_pages[:limit]:
        rows.append(
            f"""
                <tr>
                    <td>
                        <span class="score-pill {get_score_class(page.score)}">
                            {page.score}
                        </span>
                    </td>

                    <td class="url-cell">
                        <a
                            href="{escape(page.url, quote=True)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {escape(page.url)}
                        </a>
                    </td>
                </tr>
            """
        )

    return "".join(rows)


def build_all_page_rows(
    pages: list[PageAudit],
) -> str:
    """Build the main page-results table rows."""

    rows = []

    for page in sorted(
        pages,
        key=lambda item: item.url.lower(),
    ):
        warnings, failures = count_page_issues(page)

        rows.append(
            f"""
                <tr
                    data-url="{escape(page.url.lower(), quote=True)}"
                    data-score="{page.score}"
                    data-status-code="{page.status_code}"
                    data-warnings="{warnings}"
                    data-failures="{failures}"
                >
                    <td class="url-cell">
                        <a
                            href="{escape(page.url, quote=True)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {escape(page.url)}
                        </a>
                    </td>

                    <td data-sort-value="{page.score}">
                        <span class="score-pill {get_score_class(page.score)}">
                            {page.score}
                        </span>
                    </td>

                    <td data-sort-value="{page.status_code}">
                        {page.status_code}
                    </td>

                    <td data-sort-value="{warnings}">
                        <span
                            class="count-pill {
                                "status-warning"
                                if warnings
                                else "status-muted"
                            }"
                        >
                            {warnings}
                        </span>
                    </td>

                    <td data-sort-value="{failures}">
                        <span
                            class="count-pill {
                                "status-fail"
                                if failures
                                else "status-muted"
                            }"
                        >
                            {failures}
                        </span>
                    </td>
                </tr>
            """
        )

    return "".join(rows)


def build_issue_sections(
    crawl_audit: CrawlAudit,
) -> str:
    """Build expandable issue groups with affected URLs."""

    issue_groups = build_issue_groups(crawl_audit)

    if not issue_groups:
        return """
            <div class="empty-state">
                No warnings or failures were detected.
            </div>
        """

    sorted_issues = sorted(
        issue_groups.items(),
        key=lambda item: (
            -len(item[1]),
            item[0][0].lower(),
            item[0][1],
        ),
    )

    issue_sections = []

    for (
        check_name,
        status,
        message,
    ), urls in sorted_issues:
        unique_urls = sorted(set(urls))
        status_class = get_status_class(status)

        url_items = "".join(
            f"""
                <li>
                    <a
                        href="{escape(url, quote=True)}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {escape(url)}
                    </a>
                </li>
            """
            for url in unique_urls
        )

        issue_sections.append(
            f"""
                <details class="issue-group">
                    <summary>
                        <span class="issue-summary-main">
                            <span class="status-badge {status_class}">
                                {escape(status.upper())}
                            </span>

                            <strong>
                                {escape(check_name)}
                            </strong>
                        </span>

                        <span class="issue-count">
                            {len(unique_urls)} page{
                                "" if len(unique_urls) == 1 else "s"
                            }
                        </span>
                    </summary>

                    <div class="issue-body">
                        <p class="issue-message">
                            {escape(message)}
                        </p>

                        <ul class="issue-url-list">
                            {url_items}
                        </ul>
                    </div>
                </details>
            """
        )

    return "".join(issue_sections)


def build_failed_pages_section(
    crawl_audit: CrawlAudit,
) -> str:
    """Build the failed-page table, if failures occurred."""

    if not crawl_audit.failed_pages:
        return ""

    rows = "".join(
        f"""
            <tr>
                <td class="url-cell">
                    {escape(failed_page.url)}
                </td>

                <td>
                    {escape(failed_page.error)}
                </td>
            </tr>
        """
        for failed_page in crawl_audit.failed_pages
    )

    return f"""
        <section
            class="section"
            aria-labelledby="failed-pages-heading"
        >
            <div class="section-header">
                <div>
                    <span class="section-eyebrow">
                        Crawl errors
                    </span>

                    <h2
                        class="section-heading"
                        id="failed-pages-heading"
                    >
                        Pages that could not be audited
                    </h2>
                </div>

                <span class="section-count status-fail">
                    {crawl_audit.pages_failed}
                </span>
            </div>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>URL</th>
                            <th>Error</th>
                        </tr>
                    </thead>

                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </section>
    """


def export_crawl_html_report(
    crawl_audit: CrawlAudit,
    output_file: str,
) -> str:
    """Export a complete standalone crawl-audit HTML dashboard."""

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    status_counts = count_result_statuses(crawl_audit)
    score_class = get_score_class(crawl_audit.average_score)

    generated_at = datetime.now().astimezone().strftime(
        "%B %d, %Y at %I:%M %p %Z"
    )

    summary_cards = "".join(
        [
            build_summary_card(
                "Pages audited",
                crawl_audit.pages_audited,
            ),
            build_summary_card(
                "Pages failed",
                crawl_audit.pages_failed,
                (
                    "card-danger"
                    if crawl_audit.pages_failed
                    else ""
                ),
            ),
            build_summary_card(
                "Checks passed",
                status_counts["pass"],
                "card-success",
            ),
            build_summary_card(
                "Warnings",
                status_counts["warning"],
                (
                    "card-warning"
                    if status_counts["warning"]
                    else ""
                ),
            ),
            build_summary_card(
                "Failures",
                status_counts["fail"],
                (
                    "card-danger"
                    if status_counts["fail"]
                    else ""
                ),
            ),
            build_summary_card(
                "Informational",
                status_counts["info"],
            ),
        ]
    )

    issue_sections = build_issue_sections(crawl_audit)

    lowest_page_rows = build_ranked_page_rows(
        crawl_audit.pages,
        reverse=False,
    )

    highest_page_rows = build_ranked_page_rows(
        crawl_audit.pages,
        reverse=True,
    )

    all_page_rows = build_all_page_rows(
        crawl_audit.pages
    )

    failed_pages_section = build_failed_pages_section(
        crawl_audit
    )

    page_results_section = (
        f"""
            <section
                class="section"
                aria-labelledby="page-results-heading"
            >
                <div class="section-header">
                    <div>
                        <span class="section-eyebrow">
                            Page inventory
                        </span>

                        <h2
                            class="section-heading"
                            id="page-results-heading"
                        >
                            All audited pages
                        </h2>
                    </div>

                    <span class="section-count">
                        {crawl_audit.pages_audited}
                    </span>
                </div>

                <div class="table-toolbar">
                    <label class="search-control">
                        <span>Filter pages</span>

                        <input
                            id="page-search"
                            type="search"
                            placeholder="Search by URL"
                            autocomplete="off"
                        >
                    </label>

                    <p
                        class="result-count"
                        id="result-count"
                        aria-live="polite"
                    >
                        Showing {crawl_audit.pages_audited} pages
                    </p>
                </div>

                <div class="table-container">
                    <table id="page-table">
                        <thead>
                            <tr>
                                <th>
                                    <button
                                        class="sort-button"
                                        data-column="0"
                                        data-type="text"
                                    >
                                        URL
                                        <span class="sort-indicator"></span>
                                    </button>
                                </th>

                                <th>
                                    <button
                                        class="sort-button"
                                        data-column="1"
                                        data-type="number"
                                    >
                                        Score
                                        <span class="sort-indicator"></span>
                                    </button>
                                </th>

                                <th>
                                    <button
                                        class="sort-button"
                                        data-column="2"
                                        data-type="number"
                                    >
                                        HTTP status
                                        <span class="sort-indicator"></span>
                                    </button>
                                </th>

                                <th>
                                    <button
                                        class="sort-button"
                                        data-column="3"
                                        data-type="number"
                                    >
                                        Warnings
                                        <span class="sort-indicator"></span>
                                    </button>
                                </th>

                                <th>
                                    <button
                                        class="sort-button"
                                        data-column="4"
                                        data-type="number"
                                    >
                                        Failures
                                        <span class="sort-indicator"></span>
                                    </button>
                                </th>
                            </tr>
                        </thead>

                        <tbody>
                            {all_page_rows}
                        </tbody>
                    </table>
                </div>
            </section>
        """
        if crawl_audit.pages
        else """
            <section class="section">
                <div class="empty-state">
                    No pages were successfully audited.
                </div>
            </section>
        """
    )

    ranking_section = (
        f"""
            <section
                class="section"
                aria-labelledby="rankings-heading"
            >
                <div class="section-header">
                    <div>
                        <span class="section-eyebrow">
                            Score comparison
                        </span>

                        <h2
                            class="section-heading"
                            id="rankings-heading"
                        >
                            Page rankings
                        </h2>
                    </div>
                </div>

                <div class="ranking-grid">
                    <article class="panel">
                        <h3>Lowest-scoring pages</h3>

                        <div class="table-container compact-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Score</th>
                                        <th>URL</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {lowest_page_rows}
                                </tbody>
                            </table>
                        </div>
                    </article>

                    <article class="panel">
                        <h3>Highest-scoring pages</h3>

                        <div class="table-container compact-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Score</th>
                                        <th>URL</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {highest_page_rows}
                                </tbody>
                            </table>
                        </div>
                    </article>
                </div>
            </section>
        """
        if crawl_audit.pages
        else ""
    )

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <title>
        SEO Site Audit — {escape(crawl_audit.start_url)}
    </title>

    <style>
        :root {{
            color-scheme: light;

            --background: #f3f5f8;
            --surface: #ffffff;
            --surface-muted: #f8fafc;
            --surface-hover: #f4f7fb;

            --text-primary: #172033;
            --text-secondary: #5f6b7a;
            --border: #dfe4ea;

            --brand: #3454d1;
            --brand-dark: #263ea3;
            --brand-soft: #edf1ff;

            --good: #18794e;
            --good-background: #e9f8f0;

            --warning: #946200;
            --warning-background: #fff4ce;

            --poor: #b42318;
            --poor-background: #feeceb;

            --info: #3168a8;
            --info-background: #eaf3ff;

            --muted: #667085;
            --muted-background: #eef1f4;

            --shadow:
                0 18px 45px rgba(23, 32, 51, 0.08);
        }}

        * {{
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            margin: 0;
            min-width: 320px;

            background:
                radial-gradient(
                    circle at top right,
                    rgba(52, 84, 209, 0.13),
                    transparent 34rem
                ),
                var(--background);

            color: var(--text-primary);

            font-family:
                Inter,
                ui-sans-serif,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            line-height: 1.5;
        }}

        a {{
            color: var(--brand);
            text-decoration-thickness: 1px;
            text-underline-offset: 0.2em;
        }}

        a:hover {{
            color: var(--brand-dark);
        }}

        button,
        input {{
            font: inherit;
        }}

        .page-shell {{
            width: min(1180px, calc(100% - 2rem));
            margin: 0 auto;
            padding: 3rem 0 4rem;
        }}

        .dashboard-header {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 2rem;
            align-items: center;

            margin-bottom: 2rem;
            padding: 2.5rem;

            border: 1px solid var(--border);
            border-radius: 22px;

            background: var(--surface);
            box-shadow: var(--shadow);
        }}

        .eyebrow,
        .section-eyebrow {{
            display: inline-block;

            color: var(--brand);

            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}

        .eyebrow {{
            margin-bottom: 0.55rem;
        }}

        h1 {{
            margin: 0;

            font-size: clamp(2rem, 5vw, 3.5rem);
            line-height: 1.05;
            letter-spacing: -0.04em;
        }}

        h2,
        h3 {{
            letter-spacing: -0.025em;
        }}

        .site-url {{
            margin: 1rem 0 0;

            color: var(--text-secondary);
            overflow-wrap: anywhere;
        }}

        .generated-time {{
            margin: 0.4rem 0 0;

            color: var(--text-secondary);
            font-size: 0.85rem;
        }}

        .score-panel {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;

            width: 180px;
            min-height: 180px;

            border: 8px solid currentColor;
            border-radius: 50%;
        }}

        .score-number {{
            font-size: 3.25rem;
            font-weight: 850;
            line-height: 1;
            letter-spacing: -0.06em;
        }}

        .score-total {{
            margin-top: 0.25rem;

            font-size: 0.9rem;
            font-weight: 700;
            opacity: 0.8;
        }}

        .score-label {{
            margin-top: 0.55rem;

            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .score-good {{
            color: var(--good);
            background: var(--good-background);
        }}

        .score-warning {{
            color: var(--warning);
            background: var(--warning-background);
        }}

        .score-poor {{
            color: var(--poor);
            background: var(--poor-background);
        }}

        .section {{
            margin-top: 2rem;
        }}

        .section-header {{
            display: flex;
            gap: 1rem;
            align-items: end;
            justify-content: space-between;

            margin-bottom: 1rem;
        }}

        .section-heading {{
            margin: 0.25rem 0 0;

            font-size: 1.45rem;
        }}

        .section-count {{
            display: inline-flex;
            min-width: 2.25rem;
            min-height: 2.25rem;
            align-items: center;
            justify-content: center;

            padding: 0.35rem 0.7rem;

            border-radius: 999px;

            background: var(--brand-soft);
            color: var(--brand);
            font-weight: 800;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns:
                repeat(3, minmax(0, 1fr));
            gap: 1rem;
        }}

        .summary-card {{
            position: relative;
            overflow: hidden;

            min-height: 145px;
            padding: 1.5rem;

            border: 1px solid var(--border);
            border-radius: 16px;

            background: var(--surface);
            box-shadow:
                0 8px 22px rgba(23, 32, 51, 0.05);
        }}

        .summary-card::before {{
            position: absolute;
            inset: 0 auto 0 0;

            width: 5px;

            background: var(--brand);

            content: "";
        }}

        .summary-label {{
            display: block;

            color: var(--text-secondary);

            font-size: 0.8rem;
            font-weight: 750;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        .summary-value {{
            display: block;
            margin-top: 1.25rem;

            font-size: 2.35rem;
            line-height: 1;
            letter-spacing: -0.045em;
        }}

        .card-success::before {{
            background: var(--good);
        }}

        .card-warning::before {{
            background: var(--warning);
        }}

        .card-danger::before {{
            background: var(--poor);
        }}

        .panel {{
            padding: 1.5rem;

            border: 1px solid var(--border);
            border-radius: 16px;

            background: var(--surface);
            box-shadow:
                0 8px 22px rgba(23, 32, 51, 0.05);
        }}

        .panel h3 {{
            margin: 0 0 1rem;
        }}

        .ranking-grid {{
            display: grid;
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
            gap: 1rem;
        }}

        .issues-list {{
            display: grid;
            gap: 0.75rem;
        }}

        .issue-group {{
            overflow: hidden;

            border: 1px solid var(--border);
            border-radius: 14px;

            background: var(--surface);
        }}

        .issue-group summary {{
            display: flex;
            gap: 1rem;
            align-items: center;
            justify-content: space-between;

            padding: 1.1rem 1.25rem;

            cursor: pointer;
            list-style: none;
        }}

        .issue-group summary::-webkit-details-marker {{
            display: none;
        }}

        .issue-group summary:hover {{
            background: var(--surface-hover);
        }}

        .issue-group summary::after {{
            margin-left: auto;

            color: var(--text-secondary);
            content: "+";
            font-size: 1.35rem;
            font-weight: 500;
        }}

        .issue-group[open] summary::after {{
            content: "−";
        }}

        .issue-summary-main {{
            display: flex;
            gap: 0.75rem;
            align-items: center;
        }}

        .issue-count {{
            margin-left: auto;

            color: var(--text-secondary);
            font-size: 0.88rem;
            font-weight: 700;
            white-space: nowrap;
        }}

        .issue-body {{
            padding: 0 1.25rem 1.25rem;

            border-top: 1px solid var(--border);
        }}

        .issue-message {{
            margin: 1rem 0;

            color: var(--text-secondary);
        }}

        .issue-url-list {{
            max-height: 18rem;
            margin: 0;
            padding-left: 1.25rem;
            overflow-y: auto;
        }}

        .issue-url-list li + li {{
            margin-top: 0.45rem;
        }}

        .status-badge,
        .score-pill,
        .count-pill {{
            display: inline-flex;
            align-items: center;
            justify-content: center;

            border-radius: 999px;

            font-weight: 800;
            white-space: nowrap;
        }}

        .status-badge {{
            padding: 0.3rem 0.55rem;

            font-size: 0.68rem;
            letter-spacing: 0.06em;
        }}

        .score-pill {{
            min-width: 3rem;
            padding: 0.35rem 0.65rem;
        }}

        .count-pill {{
            min-width: 2.1rem;
            padding: 0.25rem 0.55rem;
        }}

        .status-pass {{
            color: var(--good);
            background: var(--good-background);
        }}

        .status-warning {{
            color: var(--warning);
            background: var(--warning-background);
        }}

        .status-fail {{
            color: var(--poor);
            background: var(--poor-background);
        }}

        .status-info {{
            color: var(--info);
            background: var(--info-background);
        }}

        .status-muted {{
            color: var(--muted);
            background: var(--muted-background);
        }}

        .table-toolbar {{
            display: flex;
            gap: 1rem;
            align-items: end;
            justify-content: space-between;

            margin-bottom: 1rem;
        }}

        .search-control {{
            display: grid;
            gap: 0.4rem;

            width: min(100%, 28rem);

            color: var(--text-secondary);
            font-size: 0.82rem;
            font-weight: 700;
        }}

        .search-control input {{
            width: 100%;
            padding: 0.75rem 0.9rem;

            border: 1px solid var(--border);
            border-radius: 10px;

            background: var(--surface);
            color: var(--text-primary);
        }}

        .search-control input:focus {{
            border-color: var(--brand);
            outline: 3px solid rgba(52, 84, 209, 0.15);
        }}

        .result-count {{
            margin: 0;

            color: var(--text-secondary);
            font-size: 0.88rem;
        }}

        .table-container {{
            overflow-x: auto;

            border: 1px solid var(--border);
            border-radius: 14px;

            background: var(--surface);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th,
        td {{
            padding: 0.9rem 1rem;

            border-bottom: 1px solid var(--border);

            text-align: left;
            vertical-align: middle;
        }}

        th {{
            background: var(--surface-muted);
            color: var(--text-secondary);

            font-size: 0.74rem;
            letter-spacing: 0.055em;
            text-transform: uppercase;
        }}

        tbody tr:last-child td {{
            border-bottom: 0;
        }}

        tbody tr:hover {{
            background: var(--surface-hover);
        }}

        .url-cell {{
            max-width: 38rem;
            overflow-wrap: anywhere;
        }}

        .sort-button {{
            display: inline-flex;
            gap: 0.4rem;
            align-items: center;

            padding: 0;

            border: 0;

            background: transparent;
            color: inherit;
            cursor: pointer;

            font-size: inherit;
            font-weight: 800;
            letter-spacing: inherit;
            text-transform: inherit;
        }}

        .sort-button:hover {{
            color: var(--brand);
        }}

        .sort-button:focus-visible {{
            border-radius: 4px;
            outline: 3px solid rgba(52, 84, 209, 0.2);
        }}

        .sort-indicator {{
            min-width: 0.8rem;
        }}

        .compact-table th,
        .compact-table td {{
            padding: 0.75rem 0.85rem;
        }}

        .empty-state {{
            padding: 2rem;

            border: 1px dashed var(--border);
            border-radius: 16px;

            background: var(--surface-muted);
            color: var(--text-secondary);
            text-align: center;
        }}

        .dashboard-footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;

            border-top: 1px solid var(--border);

            color: var(--text-secondary);
            font-size: 0.85rem;
            text-align: center;
        }}

        @media (max-width: 800px) {{
            .dashboard-header {{
                grid-template-columns: 1fr;
                justify-items: start;
            }}

            .score-panel {{
                width: 150px;
                min-height: 150px;
            }}

            .summary-grid {{
                grid-template-columns:
                    repeat(2, minmax(0, 1fr));
            }}

            .ranking-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 600px) {{
            .page-shell {{
                width: min(100% - 1rem, 1180px);
                padding-top: 0.5rem;
            }}

            .dashboard-header {{
                padding: 1.5rem;
                border-radius: 16px;
            }}

            .summary-grid {{
                grid-template-columns: 1fr;
            }}

            .summary-card {{
                min-height: 120px;
            }}

            .section-header,
            .table-toolbar {{
                align-items: stretch;
                flex-direction: column;
            }}

            .issue-group summary {{
                align-items: flex-start;
                flex-wrap: wrap;
            }}

            .issue-count {{
                margin-left: 0;
            }}
        }}
    </style>
</head>

<body>
    <main class="page-shell">
        <header class="dashboard-header">
            <div>
                <span class="eyebrow">
                    Technical SEO report
                </span>

                <h1>SEO Site Audit</h1>

                <p class="site-url">
                    {escape(crawl_audit.start_url)}
                </p>

                <p class="generated-time">
                    Generated {escape(generated_at)}
                </p>
            </div>

            <div
                class="score-panel {escape(score_class)}"
                aria-label="Average SEO score:
                    {crawl_audit.average_score} out of 100"
            >
                <span class="score-number">
                    {crawl_audit.average_score}
                </span>

                <span class="score-total">
                    / 100
                </span>

                <span class="score-label">
                    Average score
                </span>
            </div>
        </header>

        <section
            class="section"
            aria-labelledby="summary-heading"
        >
            <div class="section-header">
                <div>
                    <span class="section-eyebrow">
                        Overview
                    </span>

                    <h2
                        class="section-heading"
                        id="summary-heading"
                    >
                        Crawl summary
                    </h2>
                </div>
            </div>

            <div class="summary-grid">
                {summary_cards}
            </div>
        </section>

        <section
            class="section"
            aria-labelledby="issues-heading"
        >
            <div class="section-header">
                <div>
                    <span class="section-eyebrow">
                        Actionable findings
                    </span>

                    <h2
                        class="section-heading"
                        id="issues-heading"
                    >
                        Issues by affected page
                    </h2>
                </div>

                <span class="section-count">
                    {
                        status_counts["warning"]
                        + status_counts["fail"]
                    }
                </span>
            </div>

            <div class="issues-list">
                {issue_sections}
            </div>
        </section>

        {ranking_section}

        {page_results_section}

        {failed_pages_section}

        <footer class="dashboard-footer">
            Generated by SEO Auditor
        </footer>
    </main>

    <script>
        (() => {{
            const table = document.getElementById("page-table");
            const searchInput = document.getElementById("page-search");
            const resultCount = document.getElementById("result-count");

            if (!table) {{
                return;
            }}

            const tableBody = table.querySelector("tbody");
            const sortButtons = table.querySelectorAll(".sort-button");

            let currentColumn = null;
            let currentDirection = "ascending";

            function getCellValue(row, columnIndex, type) {{
                const cell = row.children[columnIndex];

                if (type === "number") {{
                    const rawValue =
                        cell.dataset.sortValue
                        ?? cell.textContent;

                    return Number(rawValue.trim()) || 0;
                }}

                return cell.textContent.trim().toLowerCase();
            }}

            function updateSortIndicators(activeButton) {{
                sortButtons.forEach((button) => {{
                    const indicator =
                        button.querySelector(".sort-indicator");

                    button.removeAttribute("aria-sort");

                    if (button === activeButton) {{
                        const symbol =
                            currentDirection === "ascending"
                            ? "▲"
                            : "▼";

                        indicator.textContent = symbol;
                        button.setAttribute(
                            "aria-sort",
                            currentDirection
                        );
                    }} else {{
                        indicator.textContent = "";
                    }}
                }});
            }}

            function sortTable(button) {{
                const columnIndex = Number(button.dataset.column);
                const type = button.dataset.type;

                if (currentColumn === columnIndex) {{
                    currentDirection =
                        currentDirection === "ascending"
                        ? "descending"
                        : "ascending";
                }} else {{
                    currentColumn = columnIndex;
                    currentDirection = "ascending";
                }}

                const rows = Array.from(
                    tableBody.querySelectorAll("tr")
                );

                rows.sort((firstRow, secondRow) => {{
                    const firstValue = getCellValue(
                        firstRow,
                        columnIndex,
                        type
                    );

                    const secondValue = getCellValue(
                        secondRow,
                        columnIndex,
                        type
                    );

                    let comparison = 0;

                    if (firstValue < secondValue) {{
                        comparison = -1;
                    }} else if (firstValue > secondValue) {{
                        comparison = 1;
                    }}

                    return currentDirection === "ascending"
                        ? comparison
                        : -comparison;
                }});

                rows.forEach((row) => {{
                    tableBody.appendChild(row);
                }});

                updateSortIndicators(button);
            }}

            function filterRows() {{
                const searchTerm =
                    searchInput.value.trim().toLowerCase();

                const rows = tableBody.querySelectorAll("tr");
                let visibleRows = 0;

                rows.forEach((row) => {{
                    const url = row.dataset.url || "";
                    const matches = url.includes(searchTerm);

                    row.hidden = !matches;

                    if (matches) {{
                        visibleRows += 1;
                    }}
                }});

                resultCount.textContent =
                    `Showing ${{visibleRows}} page` +
                    `${{visibleRows === 1 ? "" : "s"}}`;
            }}

            sortButtons.forEach((button) => {{
                button.addEventListener("click", () => {{
                    sortTable(button);
                }});
            }});

            searchInput.addEventListener(
                "input",
                filterRows
            );
        }})();
    </script>
</body>
</html>
"""

    output_path.write_text(
        html_document,
        encoding="utf-8",
    )

    return str(output_path)