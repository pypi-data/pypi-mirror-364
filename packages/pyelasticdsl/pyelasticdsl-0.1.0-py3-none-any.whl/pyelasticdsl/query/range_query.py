from typing import Any, Optional

from pyelasticdsl.dsl import Query


class RangeQuery(Query):
    def __init__(self, name: str) -> None:
        self.name = name
        self.from_: Optional[Any] = None
        self.to: Optional[Any] = None
        self.time_zone: str = ""
        self.include_lower: bool = True
        self.include_upper: bool = True
        self.boost: Optional[float] = None
        self.query_name: str = ""
        self.format: str = ""
        self.relation: str = ""

    def from_value(self, value: Any) -> "RangeQuery":
        self.from_ = value
        return self

    def gt(self, value: Any) -> "RangeQuery":
        self.from_ = value
        self.include_lower = False
        return self

    def gte(self, value: Any) -> "RangeQuery":
        self.from_ = value
        self.include_lower = True
        return self

    def to_value(self, value: Any) -> "RangeQuery":
        self.to = value
        return self

    def lt(self, value: Any) -> "RangeQuery":
        self.to = value
        self.include_upper = False
        return self

    def lte(self, value: Any) -> "RangeQuery":
        self.to = value
        self.include_upper = True
        return self

    def include_lower_(self, include: bool) -> "RangeQuery":
        self.include_lower = include
        return self

    def include_upper_(self, include: bool) -> "RangeQuery":
        self.include_upper = include
        return self

    def boost_(self, boost: float) -> "RangeQuery":
        self.boost = boost
        return self

    def query_name_(self, name: str) -> "RangeQuery":
        self.query_name = name
        return self

    def time_zone_(self, tz: str) -> "RangeQuery":
        self.time_zone = tz
        return self

    def format_(self, fmt: str) -> "RangeQuery":
        self.format = fmt
        return self

    def relation_(self, relation: str) -> "RangeQuery":
        self.relation = relation
        return self

    def to_dict(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "from": self.from_,
            "to": self.to,
            "include_lower": self.include_lower,
            "include_upper": self.include_upper,
        }

        if self.time_zone:
            params["time_zone"] = self.time_zone
        if self.format:
            params["format"] = self.format
        if self.relation:
            params["relation"] = self.relation
        if self.boost is not None:
            params["boost"] = self.boost

        query = {"range": {self.name: params}}

        if self.query_name:
            query["_name"] = self.query_name

        return query
