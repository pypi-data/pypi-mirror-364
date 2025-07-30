from typing import Any, Optional
from pyelasticdsl.dsl import Query

class RegexpQuery(Query):
    def __init__(self, name: str, regexp: str) -> None:
        self.name = name
        self.regexp = regexp
        self.flags: str = ""
        self.boost: Optional[float] = None
        self.rewrite: str = ""
        self.case_insensitive: Optional[bool] = None
        self.query_name: str = ""
        self.max_determinized_states: Optional[int] = None

    def flags_(self, flags: str) -> "RegexpQuery":
        self.flags = flags
        return self

    def max_determinized_states_(self, value: int) -> "RegexpQuery":
        self.max_determinized_states = value
        return self

    def boost_(self, boost: float) -> "RegexpQuery":
        self.boost = boost
        return self

    def rewrite_(self, rewrite: str) -> "RegexpQuery":
        self.rewrite = rewrite
        return self

    def case_insensitive_(self, ci: bool) -> "RegexpQuery":
        self.case_insensitive = ci
        return self

    def query_name_(self, name: str) -> "RegexpQuery":
        self.query_name = name
        return self

    def to_dict(self) -> dict[str, Any]:
        x: dict[str, Any] = {"value": self.regexp}

        if self.flags:
            x["flags"] = self.flags
        if self.max_determinized_states is not None:
            x["max_determinized_states"] = self.max_determinized_states
        if self.boost is not None:
            x["boost"] = self.boost
        if self.rewrite:
            x["rewrite"] = self.rewrite
        if self.case_insensitive is not None:
            x["case_insensitive"] = self.case_insensitive
        if self.query_name:
            x["name"] = self.query_name

        return {"regexp": {self.name: x}}
