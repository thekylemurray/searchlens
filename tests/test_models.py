from auditor.models import (
    AuditResult,
    CrawlAudit,
    FailedPage,
    PageAudit,
)


def test_audit_result_status_helpers() -> None:
    passing_result = AuditResult(
        name="Title",
        status="pass",
        message="Passed.",
    )

    warning_result = AuditResult(
        name="Title",
        status="warning",
        message="Warning.",
    )

    failing_result = AuditResult(
        name="Title",
        status="fail",
        message="Failed.",
    )

    info_result = AuditResult(
        name="Title",
        status="info",
        message="Informational.",
    )

    assert passing_result.is_pass()
    assert warning_result.is_warning()
    assert failing_result.is_fail()
    assert info_result.is_info()


def test_audit_result_to_dict() -> None:
    result = AuditResult(
        name="Title",
        status="pass",
        message="Title is valid.",
        value="Example title",
    )

    result_dictionary = result.to_dict()

    assert result_dictionary["name"] == "Title"
    assert result_dictionary["status"] == "pass"
    assert result_dictionary["message"] == "Title is valid."
    assert result_dictionary["value"] == "Example title"


def test_crawl_audit_counts_pages() -> None:
    crawl_audit = CrawlAudit(
        start_url="https://example.com",
        pages=[
            PageAudit(
                url="https://example.com",
                status_code=200,
                score=90,
            ),
            PageAudit(
                url="https://example.com/about",
                status_code=200,
                score=80,
            ),
        ],
        failed_pages=[
            FailedPage(
                url="https://example.com/missing",
                error="Page could not be fetched.",
            )
        ],
    )

    assert crawl_audit.pages_audited == 2
    assert crawl_audit.pages_failed == 1


def test_crawl_audit_calculates_average_score() -> None:
    crawl_audit = CrawlAudit(
        start_url="https://example.com",
        pages=[
            PageAudit(
                url="https://example.com",
                status_code=200,
                score=90,
            ),
            PageAudit(
                url="https://example.com/about",
                status_code=200,
                score=80,
            ),
        ],
    )

    assert crawl_audit.average_score == 85


def test_empty_crawl_has_zero_average() -> None:
    crawl_audit = CrawlAudit(
        start_url="https://example.com"
    )

    assert crawl_audit.average_score == 0