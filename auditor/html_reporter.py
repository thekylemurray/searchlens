from html import escape
from pathlib import Path

from auditor.models import AuditResult


STATUS_COLORS = {
    "pass": "#166534",
    "warning": "#92400e",
    "fail": "#991b1b",
    "info": "#1e3a8a",
}


def format_value(value) -> str:
    """Convert an audit value into HTML."""

    if value in (None, ""):
        return ""

    if isinstance(value, list):
        items = "".join(
            f"<li>{escape(str(item))}</li>"
            for item in value
        )
        return f"<ul>{items}</ul>"

    if isinstance(value, dict):
        sections = []

        for key, item in value.items():
            if isinstance(item, dict):
                nested_items = "".join(
                    f"<li><strong>{escape(str(nested_key))}:</strong> "
                    f"{escape(str(nested_value))}</li>"
                    for nested_key, nested_value in item.items()
                )

                sections.append(
                    f"<h4>{escape(str(key).title())}</h4>"
                    f"<ul>{nested_items}</ul>"
                )

            elif isinstance(item, list):
                list_items = "".join(
                    f"<li>{escape(str(list_item))}</li>"
                    for list_item in item
                )

                sections.append(
                    f"<h4>{escape(str(key).title())}</h4>"
                    f"<ul>{list_items}</ul>"
                )

            else:
                sections.append(
                    f"<p><strong>{escape(str(key))}:</strong> "
                    f"{escape(str(item))}</p>"
                )

        return "".join(sections)

    return f"<p>{escape(str(value))}</p>"


def build_result_card(result: AuditResult) -> str:
    """Build one HTML result card."""

    color = STATUS_COLORS.get(result.status, "#374151")
    value_html = format_value(result.value)

    return f"""
    <article class="result-card">
        <div class="result-header">
            <h2>{escape(result.name)}</h2>
            <span class="status" style="background-color: {color};">
                {escape(result.status.upper())}
            </span>
        </div>

        <p>{escape(result.message)}</p>

        <div class="result-value">
            {value_html}
        </div>
    </article>
    """


def export_html_report(
    results: list[AuditResult],
    score: int,
    url: str,
    output_file: str = "seo-audit.html",
) -> Path:
    """Export the SEO audit results as an HTML report."""

    result_cards = "".join(
        build_result_card(result)
        for result in results
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>SEO Audit Report</title>

    <style>
        body {{
            margin: 0;
            padding: 40px 20px;
            background: #f3f4f6;
            color: #111827;
            font-family: Arial, sans-serif;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        .report-header {{
            padding: 32px;
            margin-bottom: 24px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}

        .report-header h1 {{
            margin-top: 0;
        }}

        .score {{
            font-size: 36px;
            font-weight: bold;
        }}

        .url {{
            overflow-wrap: anywhere;
            color: #4b5563;
        }}

        .result-card {{
            padding: 24px;
            margin-bottom: 16px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}

        .result-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}

        .result-header h2 {{
            margin: 0;
        }}

        .status {{
            padding: 6px 10px;
            border-radius: 999px;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}

        .result-value {{
            overflow-wrap: anywhere;
            color: #374151;
        }}

        li {{
            margin-bottom: 6px;
        }}
    </style>
</head>

<body>
    <main class="container">
        <header class="report-header">
            <h1>SEO Audit Report</h1>
            <div class="score">{score}/100</div>
            <p class="url">{escape(url)}</p>
        </header>

        {result_cards}
    </main>
</body>
</html>
"""

    output_path = Path(output_file)

    with output_path.open("w", encoding="utf-8") as file:
        file.write(html)

    return output_path