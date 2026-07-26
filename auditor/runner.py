from bs4 import BeautifulSoup

from auditor.checks.meta_description import check_meta_description
from auditor.checks.title import check_title
from auditor.models import AuditResult
from auditor.checks.canonical import check_canonical
from auditor.checks.h1 import check_h1
from auditor.checks.robots import check_robots
from auditor.checks.images import check_images

def run_all_checks(soup: BeautifulSoup) -> list[AuditResult]:
    """Run every registered page-level SEO check."""

    checks = [
        check_title,
        check_meta_description,
        check_canonical,
        check_h1,
        check_robots,
        check_images,
    ]

    results = []

    for check in checks:
        result = check(soup)
        results.append(result)

    return results