from auditor.models import AuditResult


def calculate_score(results: list[AuditResult]) -> int:
    earned = 0
    possible = 0

    for result in results:
        if result.is_info():
            continue

        possible += result.weight

        if result.is_pass():
            earned += result.weight
        elif result.is_warning():
            earned += result.weight * 0.5

    if possible == 0:
        return 100

    return round((earned / possible) * 100)