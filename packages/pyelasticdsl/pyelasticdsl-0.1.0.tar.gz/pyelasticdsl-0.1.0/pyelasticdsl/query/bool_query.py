from typing import Any

from pyelasticdsl.dsl import Query

class BoolQuery(Query):

    def __init__(self):
        self.must_clauses: list[Query] = []
        self.must_not_clauses: list[Query] = []
        self.filter_clauses: list[Query] = []
        self.should_clauses: list[Query] = []
        self.boost: float | None = None
        self.minimum_should_match: str = ""
        self.adjust_pure_negative: bool | None = None
        self.query_name: str = ""

    def must(self, *queries: Query) -> "BoolQuery":
        self.must_clauses.extend(queries)
        return self

    def must_not(self, *queries: Query) -> "BoolQuery":
        self.must_not_clauses.extend(queries)
        return self

    def filter(self, *queries: Query) -> "BoolQuery":
        self.filter_clauses.extend(queries)
        return self

    def should(self, *queries: Query) -> "BoolQuery":
        self.should_clauses.extend(queries)
        return self

    def boost(self, boost: float) -> "BoolQuery":
        self.boost = boost
        return self

    def minimum_should_match(self, minimum_should_match: str) -> "BoolQuery":
        self.minimum_should_match = str(minimum_should_match)
        return self

    def adjust_pure_negative(self, adjust: bool) -> "BoolQuery":
        self.adjust_pure_negative = adjust
        return self

    def query_name(self, name: str) -> "BoolQuery":
        self.query_name = name
        return self

    def to_dict(self) -> dict[str, Any]:
        bool_clause: dict[str, Any] = {}

        def serialize_clauses(clauses: list[Query]) -> Any:
            if not clauses:
                return None
            if len(clauses) == 1:
                return clauses[0].to_dict()
            return [clause.to_dict() for clause in clauses]

        must_src = serialize_clauses(self.must_clauses)
        if must_src is not None:
            bool_clause["must"] = must_src

        must_not_src = serialize_clauses(self.must_not_clauses)
        if must_not_src is not None:
            bool_clause["must_not"] = must_not_src

        filter_src = serialize_clauses(self.filter_clauses)
        if filter_src is not None:
            bool_clause["filter"] = filter_src

        should_src = serialize_clauses(self.should_clauses)
        if should_src is not None:
            bool_clause["should"] = should_src

        if self.boost is not None:
            bool_clause["boost"] = self.boost
        if self.minimum_should_match:
            bool_clause["minimum_should_match"] = self.minimum_should_match
        if self.adjust_pure_negative is not None:
            bool_clause["adjust_pure_negative"] = self.adjust_pure_negative
        if self.query_name:
            bool_clause["_name"] = self.query_name

        return {"bool": bool_clause}
