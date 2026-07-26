from dataclasses import asdict, dataclass, field
from typing import Any, Literal
from auditor.constants import CHECK_WEIGHTS

AuditStatus = Literal["pass", "warning", "fail", "info"]


@dataclass(slots=True)
class AuditResult:
    name: str
    status: AuditStatus
    message: str
    value: Any = None
    weight: int = field(init=False)

    def __post_init__(self):
        self.weight = CHECK_WEIGHTS.get(self.name, 10)

    def is_pass(self) -> bool:
        return self.status == "pass"

    def is_warning(self) -> bool:
        return self.status == "warning"

    def is_fail(self) -> bool:
        return self.status == "fail"

    def is_info(self) -> bool:
        return self.status == "info"

    def to_dict(self):
        return asdict(self)