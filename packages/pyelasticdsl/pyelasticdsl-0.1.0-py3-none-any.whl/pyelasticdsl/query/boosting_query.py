from typing import Any, Optional

from pyelasticdsl.dsl import Query

class BoostingQuery(Query):
    def __init__(self) -> None:
        self.positive_clause: Optional[Query] = None
        self.negative_clause: Optional[Query] = None
        self.negative_boost: Optional[float] = None
        self.boost: Optional[float] = None

    def positive(self, positive: Query) -> "BoostingQuery":
        self.positive_clause = positive
        return self

    def negative(self, negative: Query) -> "BoostingQuery":
        self.negative_clause = negative
        return self

    def negative_boost(self, negative_boost: float) -> "BoostingQuery":
        self.negative_boost = negative_boost
        return self

    def boost(self, boost: float) -> "BoostingQuery":
        self.boost = boost
        return self

    def to_dict(self) -> dict[str, Any]:
        boosting_clause: dict[str, Any] = {}

        if self.positive_clause is not None:
            boosting_clause["positive"] = self.positive_clause.to_dict()
        if self.negative_clause is not None:
            boosting_clause["negative"] = self.negative_clause.to_dict()
        if self.negative_boost is not None:
            boosting_clause["negative_boost"] = self.negative_boost
        if self.boost is not None:
            boosting_clause["boost"] = self.boost

        return {"boosting": boosting_clause}
