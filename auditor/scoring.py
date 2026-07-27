from auditor.models import AuditResult
from auditor.scoring_weights import get_check_weight


PASS_CREDIT = 1.0
WARNING_CREDIT = 0.5
FAIL_CREDIT = 0.0


def calculate_score(
    results: list[AuditResult],
) -> int:
    """Calculate a weighted SEO score from audit results."""

    earned_points = 0.0
    possible_points = 0.0

    for result in results:
        if result.is_info():
            continue

        weight = get_check_weight(result.name)
        possible_points += weight

        if result.is_pass():
            earned_points += weight * PASS_CREDIT

        elif result.is_warning():
            earned_points += weight * WARNING_CREDIT

        elif result.is_fail():
            earned_points += weight * FAIL_CREDIT

    if possible_points == 0:
        return 100

    score = (
        earned_points
        / possible_points
    ) * 100

    return round(score)