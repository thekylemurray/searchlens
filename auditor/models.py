from dataclasses import asdict, dataclass
from typing import Any, Literal


AuditStatus = Literal["pass", "warning", "fail", "info"]


@dataclass
class AuditResult:
    """Represents the result of one SEO audit check."""

    name: str
    status: AuditStatus
    message: str
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the audit result into a dictionary for exporting."""

        return asdict(self)