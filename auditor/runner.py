from bs4 import BeautifulSoup

from auditor.checks.meta_description import check_meta_description
from auditor.checks.title import check_title
from auditor.models import AuditResult


def run_all_checks(soup: BeautifulSoup) -> list[AuditResult]:
    """Run every registered page-level SEO check."""

    checks = [
        check_title,
        check_meta_description,
    ]

    results = []

    for check in checks:
        result = check(soup)
        results.append(result)

    return results