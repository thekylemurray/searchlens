"""Central configuration for SEO audit scoring weights."""


DEFAULT_CHECK_WEIGHT = 1


CHECK_WEIGHTS: dict[str, float] = {
    # Core on-page SEO
    "Title": 10,
    "Title Tag": 10,
    "Meta Description": 10,
    "Canonical": 10,
    "H1": 10,
    "H1 Tags": 10,
    "Heading Structure": 8,
    "Robots Meta": 8,

    # Content and media
    "Images": 6,
    "Links": 8,

    # Search enhancements and social metadata
    "Structured Data": 8,
    "Open Graph": 5,
    "Twitter Cards": 3,

    # Technical performance
    "Performance": 10,
    "HTTP Headers": 5,

    # Site-level discoverability
    "robots.txt": 5,
    "Robots.txt": 5,
    "Sitemap": 5,
}


def get_check_weight(check_name: str) -> float:
    """Return the configured weight for an audit check."""

    return CHECK_WEIGHTS.get(
        check_name,
        DEFAULT_CHECK_WEIGHT,
    )