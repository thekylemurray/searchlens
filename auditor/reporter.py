from auditor.models import AuditResult


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
        print(f"  Value: {result.value}")

    print()


def print_report(results: list[AuditResult]) -> None:
    """Print a complete SEO audit report."""

    print()
    print("=" * 50)
    print("SEO AUDIT RESULTS")
    print("=" * 50)
    print()

    for result in results:
        print_result(result)