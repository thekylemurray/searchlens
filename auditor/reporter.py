from auditor.models import AuditResult
from auditor.scoring import calculate_score
from auditor.html_reporter import export_html_report

STATUS_SYMBOLS = {
    "pass": "✓",
    "warning": "⚠",
    "fail": "✗",
    "info": "ℹ",
}


def print_result(result: AuditResult) -> None:
    """Print one audit result in a consistent format."""

    symbol = STATUS_SYMBOLS.get(result.status, "-")
    status = result.status.upper()

    print(f"{symbol} {result.name}")
    print(f"  Status: {status}")
    print(f"  {result.message}")

    if result.value not in (None, ""):
        if isinstance(result.value, list):
            print("  Values:")

            for item in result.value:
                print(f"    • {item}")

        elif isinstance(result.value, dict):
            print("  Details:")

            for key, value in result.value.items():
                if isinstance(value, dict):
                    print(f"    {key.title()}:")

                    for nested_key, nested_value in value.items():
                        print(f"      • {nested_key}: {nested_value}")

                elif isinstance(value, list):
                    print(f"    {key.title()}:")

                    for item in value:
                        print(f"      • {item}")

                else:
                    print(f"    • {key}: {value}")

        else:
            print(f"  Value: {result.value}")

    print()


def print_report(results: list[AuditResult]) -> None:
    """Print a complete SEO audit report and summary."""

    passes = 0
    warnings = 0
    failures = 0
    info_results = 0

    score = calculate_score(results)

    print()
    print("=" * 50)
    print("SEO AUDIT RESULTS")
    print(f"SEO Score: {score}/100")
    print("=" * 50)
    print()

    for result in results:
        if result.is_pass():
            passes += 1
        elif result.is_warning():
            warnings += 1
        elif result.is_fail():
            failures += 1
        else:
            info_results += 1

        print_result(result)

    print("=" * 50)
    print(
        f"Summary: {passes} pass, "
        f"{warnings} warning, "
        f"{failures} fail, "
        f"{info_results} info"
    )

