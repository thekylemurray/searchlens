from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditResult:
    """Represent the result of one SEO audit check."""

    name: str
    status: str
    message: str
    value: Any = None
    weight: float = 1

    def is_pass(self) -> bool:
        """Return whether this check passed."""

        return self.status == "pass"

    def is_warning(self) -> bool:
        """Return whether this check produced a warning."""

        return self.status == "warning"

    def is_fail(self) -> bool:
        """Return whether this check failed."""

        return self.status == "fail"

    def is_info(self) -> bool:
        """Return whether this is an informational result."""

        return self.status == "info"


@dataclass
class PageAudit:
    """Represent the completed audit of one webpage."""

    url: str
    status_code: int
    score: int
    results: list[AuditResult] = field(default_factory=list)


@dataclass
class FailedPage:
    """Represent a webpage that could not be audited."""

    url: str
    error: str


@dataclass
class CrawlAudit:
    """Represent the complete result of a website crawl."""

    start_url: str
    pages: list[PageAudit] = field(default_factory=list)
    failed_pages: list[FailedPage] = field(default_factory=list)

    @property
    def pages_audited(self) -> int:
        """Return the number of successfully audited pages."""

        return len(self.pages)

    @property
    def pages_failed(self) -> int:
        """Return the number of pages that could not be audited."""

        return len(self.failed_pages)

    @property
    def average_score(self) -> int:
        """Return the rounded average SEO score."""

        if not self.pages:
            return 0

        total_score = sum(
            page.score
            for page in self.pages
        )

        return round(total_score / len(self.pages))