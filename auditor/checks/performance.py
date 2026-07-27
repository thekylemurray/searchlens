from auditor.context import PageContext
from auditor.models import AuditResult


def check_performance(context: PageContext) -> AuditResult:
    """Inspect basic HTTP performance characteristics."""

    response = context.response

    response_time_ms = round(
        response.elapsed.total_seconds() * 1000
    )

    page_size_kb = round(
        len(response.content) / 1024,
        1,
    )

    compression = (
        response.headers.get("Content-Encoding", "None")
    )

    redirect_count = len(response.history)

    return AuditResult(
        name="Performance",
        status="pass",
        message="Collected page performance metrics.",
        value={
            "Response Time (ms)": response_time_ms,
            "Page Size (KB)": page_size_kb,
            "Compression": compression,
            "Redirects": redirect_count,
            "Status Code": response.status_code,
        },
    )