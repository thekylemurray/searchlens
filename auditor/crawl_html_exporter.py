from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path

from auditor.models import CrawlAudit


def count_result_statuses(
    crawl_audit: CrawlAudit,
) -> Counter[str]:
    """Count audit-result statuses across all crawled pages."""

    status_counts: Counter[str] = Counter()

    for page_audit in crawl_audit.pages:
        for result in page_audit.results:
            status_counts[result.status] += 1

    return status_counts


def get_score_class(score: int) -> str:
    """Return the CSS class associated with a score."""

    if score >= 95:
        return "score-good"

    if score >= 80:
        return "score-warning"

    return "score-poor"


def build_summary_card(
    label: str,
    value: str | int,
    *,
    modifier_class: str = "",
) -> str:
    """Build one dashboard summary card."""

    class_names = "summary-card"

    if modifier_class:
        class_names += f" {modifier_class}"

    return f"""
        <article class="{escape(class_names)}">
            <span class="summary-label">
                {escape(label)}
            </span>

            <strong class="summary-value">
                {escape(str(value))}
            </strong>
        </article>
    """


def export_crawl_html_report(
    crawl_audit: CrawlAudit,
    output_file: str,
) -> str:
    """Export a website crawl audit as a standalone HTML dashboard."""

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
                modifier_class=(
                    "card-danger"
                    if crawl_audit.pages_failed
                    else ""
                ),
            ),
            build_summary_card(
                "Checks passed",
                status_counts["pass"],
                modifier_class="card-success",
            ),
            build_summary_card(
                "Warnings",
                status_counts["warning"],
                modifier_class=(
                    "card-warning"
                    if status_counts["warning"]
                    else ""
                ),
            ),
            build_summary_card(
                "Failures",
                status_counts["fail"],
                modifier_class=(
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

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <title>SEO Site Audit — {escape(crawl_audit.start_url)}</title>

    <style>
        :root {{
            color-scheme: light;

            --background: #f4f6f8;
            --surface: #ffffff;
            --surface-muted: #f8fafc;

            --text-primary: #172033;
            --text-secondary: #5f6b7a;
            --border: #dfe4ea;

            --brand: #3454d1;
            --brand-dark: #263ea3;

            --good: #18794e;
            --good-background: #e9f8f0;

            --warning: #9a6700;
            --warning-background: #fff6d8;

            --poor: #c62828;
            --poor-background: #fdecec;

            --shadow:
                0 18px 45px rgba(23, 32, 51, 0.08);
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            min-width: 320px;

            background:
                radial-gradient(
                    circle at top right,
                    rgba(52, 84, 209, 0.12),
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

        .eyebrow {{
            display: inline-block;
            margin-bottom: 0.55rem;

            color: var(--brand);

            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}

        h1 {{
            margin: 0;

            font-size: clamp(2rem, 5vw, 3.5rem);
            line-height: 1.05;
            letter-spacing: -0.04em;
        }}

        .site-url {{
            margin: 1rem 0 0;

            color: var(--text-secondary);
            font-size: 1rem;
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

            font-size: 0.75rem;
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

        .section-heading {{
            margin: 0 0 1rem;

            font-size: 1.35rem;
            letter-spacing: -0.025em;
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
        }}

        @media (max-width: 520px) {{
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
                aria-label="Average SEO score: {crawl_audit.average_score} out of 100"
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
            <h2
                class="section-heading"
                id="summary-heading"
            >
                Crawl summary
            </h2>

            <div class="summary-grid">
                {summary_cards}
            </div>
        </section>

        {
            '''
            <section class="section">
                <div class="empty-state">
                    Detailed page results will appear here in
                    the next dashboard update.
                </div>
            </section>
            '''
            if crawl_audit.pages
            else
            '''
            <section class="section">
                <div class="empty-state">
                    No pages were successfully audited.
                </div>
            </section>
            '''
        }

        <footer class="dashboard-footer">
            Generated by SEO Auditor
        </footer>
    </main>
</body>
</html>
"""

    output_path.write_text(
        html_document,
        encoding="utf-8",
    )

    return str(output_path)