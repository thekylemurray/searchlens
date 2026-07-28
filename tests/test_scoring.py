from auditor.models import AuditResult
from auditor.scoring import calculate_score


def test_all_passing_results_score_100() -> None:
    results = [
        AuditResult(
            name="Title",
            status="pass",
            message="Title is valid.",
        ),
        AuditResult(
            name="Meta Description",
            status="pass",
            message="Description is valid.",
        ),
    ]

    assert calculate_score(results) == 100


def test_all_failing_results_score_zero() -> None:
    results = [
        AuditResult(
            name="Title",
            status="fail",
            message="Title is missing.",
        ),
        AuditResult(
            name="Meta Description",
            status="fail",
            message="Description is missing.",
        ),
    ]

    assert calculate_score(results) == 0


def test_warning_receives_half_credit() -> None:
    results = [
        AuditResult(
            name="Title",
            status="warning",
            message="Title length could be improved.",
        ),
    ]

    assert calculate_score(results) == 50


def test_info_results_are_excluded() -> None:
    results = [
        AuditResult(
            name="Title",
            status="pass",
            message="Title is valid.",
        ),
        AuditResult(
            name="Informational Check",
            status="info",
            message="Informational result.",
        ),
    ]

    assert calculate_score(results) == 100


def test_weighted_checks_affect_score_differently() -> None:
    results = [
        AuditResult(
            name="Title",
            status="fail",
            message="Title is missing.",
        ),
        AuditResult(
            name="Twitter Cards",
            status="pass",
            message="Twitter Cards are present.",
        ),
    ]

    assert calculate_score(results) == 23


def test_empty_results_score_100() -> None:
    assert calculate_score([]) == 100