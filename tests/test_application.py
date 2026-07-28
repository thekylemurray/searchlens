from auditor.application import normalize_url


def test_normalize_url_adds_https() -> None:
    assert (
        normalize_url("example.com")
        == "https://example.com"
    )


def test_normalize_url_preserves_https() -> None:
    assert (
        normalize_url("https://example.com")
        == "https://example.com"
    )


def test_normalize_url_preserves_http() -> None:
    assert (
        normalize_url("http://example.com")
        == "http://example.com"
    )


def test_normalize_url_removes_surrounding_whitespace() -> None:
    assert (
        normalize_url("  example.com  ")
        == "https://example.com"
    )