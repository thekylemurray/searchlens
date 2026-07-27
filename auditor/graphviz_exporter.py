from pathlib import Path
from urllib.parse import urlparse

from auditor.models import CrawlAudit


def escape_dot_text(value: str) -> str:
    """Escape text for use inside a Graphviz quoted string."""

    return (
        value
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
    )


def build_node_label(url: str) -> str:
    """Build a readable graph label from a full URL."""

    parsed_url = urlparse(url)

    path = parsed_url.path or "/"

    if parsed_url.query:
        path = f"{path}?{parsed_url.query}"

    return path


def get_score_style(score: int | None) -> tuple[str, str]:
    """Return Graphviz fill and border colors for a page score."""

    if score is None:
        return "#eef1f4", "#667085"

    if score >= 95:
        return "#e9f8f0", "#18794e"

    if score >= 80:
        return "#fff4ce", "#946200"

    return "#feeceb", "#b42318"


def export_link_graph(
    crawl_audit: CrawlAudit,
    output_file: str,
) -> str:
    """Export internal crawl relationships as a Graphviz DOT file."""

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    scores_by_url = {
        page.url: page.score
        for page in crawl_audit.pages
    }

    failed_urls = {
        failed_page.url
        for failed_page in crawl_audit.failed_pages
    }

    all_urls = {
        crawl_audit.start_url,
        *scores_by_url.keys(),
        *failed_urls,
    }

    for source_url, target_url in crawl_audit.link_edges:
        all_urls.add(source_url)
        all_urls.add(target_url)

    node_ids = {
        url: f"node_{index}"
        for index, url in enumerate(
            sorted(all_urls),
            start=1,
        )
    }

    lines = [
        "digraph SiteArchitecture {",
        '    graph [',
        '        rankdir="LR",',
        '        bgcolor="white",',
        '        pad="0.35",',
        '        nodesep="0.45",',
        '        ranksep="0.75",',
        '        overlap="false",',
        '        splines="spline"',
        "    ];",
        "",
        '    node [',
        '        shape="box",',
        '        style="rounded,filled",',
        '        fontname="Arial",',
        '        fontsize="10",',
        '        margin="0.15,0.10"',
        "    ];",
        "",
        '    edge [',
        '        color="#98a2b3",',
        '        arrowsize="0.65"',
        "    ];",
        "",
    ]

    for url in sorted(all_urls):
        node_id = node_ids[url]
        score = scores_by_url.get(url)

        fill_color, border_color = get_score_style(score)

        label = build_node_label(url)

        if score is not None:
            label = f"{label}\\nScore: {score}"
        elif url in failed_urls:
            label = f"{label}\\nAudit failed"

        attributes = [
            f'label="{escape_dot_text(label)}"',
            f'tooltip="{escape_dot_text(url)}"',
            f'URL="{escape_dot_text(url)}"',
            f'fillcolor="{fill_color}"',
            f'color="{border_color}"',
            f'fontcolor="{border_color}"',
        ]

        if url == crawl_audit.start_url:
            attributes.extend(
                [
                    'penwidth="3"',
                    'shape="doubleoctagon"',
                ]
            )

        lines.append(
            f'    {node_id} [{", ".join(attributes)}];'
        )

    lines.append("")

    for source_url, target_url in sorted(
        set(crawl_audit.link_edges)
    ):
        source_id = node_ids.get(source_url)
        target_id = node_ids.get(target_url)

        if not source_id or not target_id:
            continue

        lines.append(
            f"    {source_id} -> {target_id};"
        )

    lines.extend(
        [
            "}",
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return str(output_path)