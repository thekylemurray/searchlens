import json
from typing import Any

from bs4 import BeautifulSoup

from auditor.models import AuditResult


def extract_schema_types(data: Any) -> set[str]:
    """Recursively extract Schema.org @type values from JSON-LD."""

    schema_types = set()

    if isinstance(data, dict):
        type_value = data.get("@type")

        if isinstance(type_value, str):
            schema_types.add(type_value)

        elif isinstance(type_value, list):
            for item in type_value:
                if isinstance(item, str):
                    schema_types.add(item)

        for value in data.values():
            schema_types.update(extract_schema_types(value))

    elif isinstance(data, list):
        for item in data:
            schema_types.update(extract_schema_types(item))

    return schema_types


def check_structured_data(soup: BeautifulSoup) -> AuditResult:
    """Detect and validate JSON-LD structured data."""

    json_ld_scripts = soup.find_all(
        "script",
        attrs={"type": "application/ld+json"},
    )

    if not json_ld_scripts:
        return AuditResult(
            name="Structured Data",
            status="info",
            message="No JSON-LD structured data was found.",
        )

    schema_types = set()
    valid_blocks = 0
    invalid_blocks = 0

    for script in json_ld_scripts:
        raw_json = script.string or script.get_text()

        if not raw_json or not raw_json.strip():
            invalid_blocks += 1
            continue

        try:
            parsed_data = json.loads(raw_json)
        except json.JSONDecodeError:
            invalid_blocks += 1
            continue

        valid_blocks += 1
        schema_types.update(extract_schema_types(parsed_data))

    details = {
        "types": sorted(schema_types),
        "valid blocks": valid_blocks,
        "invalid blocks": invalid_blocks,
    }

    if valid_blocks == 0:
        return AuditResult(
            name="Structured Data",
            status="warning",
            message=(
                "JSON-LD blocks were found, but none contained valid JSON."
            ),
            value=details,
        )

    if invalid_blocks > 0:
        return AuditResult(
            name="Structured Data",
            status="warning",
            message=(
                f"{valid_blocks} valid and {invalid_blocks} invalid "
                "JSON-LD blocks were found."
            ),
            value=details,
        )

    if not schema_types:
        return AuditResult(
            name="Structured Data",
            status="warning",
            message=(
                "Valid JSON-LD was found, but no Schema.org @type "
                "values were detected."
            ),
            value=details,
        )

    return AuditResult(
        name="Structured Data",
        status="pass",
        message=(
            f"{valid_blocks} valid JSON-LD "
            f"{'block was' if valid_blocks == 1 else 'blocks were'} found."
        ),
        value=details,
    )