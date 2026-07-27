from auditor.context import PageContext
from auditor.models import AuditResult


def check_http_headers(context: PageContext) -> AuditResult:
    """Inspect important HTTP response headers."""

    headers = context.response.headers

    content_type = headers.get("Content-Type")
    content_encoding = headers.get("Content-Encoding")
    cache_control = headers.get("Cache-Control")
    expires = headers.get("Expires")

    security_headers = {
        "Strict-Transport-Security": headers.get(
            "Strict-Transport-Security"
        ),
        "X-Frame-Options": headers.get("X-Frame-Options"),
        "X-Content-Type-Options": headers.get(
            "X-Content-Type-Options"
        ),
        "Referrer-Policy": headers.get("Referrer-Policy"),
        "Content-Security-Policy": headers.get(
            "Content-Security-Policy"
        ),
    }

    missing_security_headers = [
        name
        for name, value in security_headers.items()
        if not value
    ]

    if content_type and "text/html" not in content_type.lower():
        status = "warning"
        message = (
            "The response Content-Type does not appear to be HTML."
        )

    elif missing_security_headers:
        status = "warning"
        message = (
            f"{len(missing_security_headers)} recommended HTTP "
            "security header(s) are missing."
        )

    else:
        status = "pass"
        message = "Important HTTP response headers were found."

    return AuditResult(
        name="HTTP Headers",
        status=status,
        message=message,
        value={
            "Response Headers": {
                "Content Type": content_type,
                "Content Encoding": content_encoding,
                "Cache Control": cache_control,
                "Expires": expires,
            },
            "Security Headers": {
                "Found": {
                    name: value
                    for name, value in security_headers.items()
                    if value
                },
                "Missing": missing_security_headers,
            },
        },
    )