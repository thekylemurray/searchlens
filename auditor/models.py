from dataclasses import asdict, dataclass
from typing import Any, Literal

AuditStatus = Literal["pass", "warning", "fail", "info"]


@dataclass(slots=True)
class AuditResult:
    name: str
    status: AuditStatus
    message: str
    value: Any = None

    def is_pass(self) -> bool:
        return self.status == "pass"

    def is_warning(self) -> bool:
        return self.status == "warning"

    def is_fail(self) -> bool:
        return self.status == "fail"

    def to_dict(self):
        return asdict(self)