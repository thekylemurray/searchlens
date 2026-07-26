import json
from pathlib import Path

from auditor.models import AuditResult


def export_results(
    results: list[AuditResult],
    score: int,
    url: str,
    output_file: str = "seo-audit.json",
) -> Path:
    """Export the SEO audit results to a JSON file."""

    report_data = {
        "url": url,
        "score": score,
        "results": [result.to_dict() for result in results],
    }

    output_path = Path(output_file)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=2, ensure_ascii=False)

    return output_path