from auditor.checks.links import check_links
from auditor.checks.performance import check_performance
from auditor.context import PageContext
from auditor.models import AuditResult
from auditor.checks.canonical import check_canonical
from auditor.checks.h1 import check_h1
from auditor.checks.images import check_images
from auditor.checks.meta_description import check_meta_description
from auditor.checks.open_graph import check_open_graph
from auditor.checks.robots import check_robots
from auditor.checks.site_files import check_site_files
from auditor.checks.sitemap import check_sitemap
from auditor.checks.structured_data import check_structured_data
from auditor.checks.title import check_title
from auditor.checks.twitter_cards import check_twitter_cards

SOUP_CHECKS = [
    check_title,
    check_meta_description,
    check_canonical,
    check_h1,
    check_robots,
    check_images,
    check_open_graph,
    check_twitter_cards,
    check_structured_data,
]

CONTEXT_CHECKS = [
    check_performance,
    check_links,
]


SITE_CHECKS = [
    check_site_files,
    check_sitemap,
]


def run_page_checks(context: PageContext) -> list[AuditResult]:
    """Run checks that inspect the current page."""

    results = []

    for check in SOUP_CHECKS:
        results.append(check(context.soup))

    for check in CONTEXT_CHECKS:
        results.append(check(context))

    return results


def run_site_checks(context: PageContext) -> list[AuditResult]:
    """Run checks that inspect site-level resources."""

    return [
        check(context.url)
        for check in SITE_CHECKS
    ]


def run_all_checks(context: PageContext) -> list[AuditResult]:
    """Run every registered SEO check."""

    results = []

    results.extend(run_page_checks(context))
    results.extend(run_site_checks(context))

    return results