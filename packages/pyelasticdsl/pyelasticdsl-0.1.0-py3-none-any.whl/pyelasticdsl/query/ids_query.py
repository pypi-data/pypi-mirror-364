from typing import Any, Optional
from pyelasticdsl.dsl import Query

class IdsQuery(Query):
    def __init__(self, *types: str) -> None:
        self.types: list[str] = list(types)
        self.values: list[str] = []
        self.boost: Optional[float] = None
        self.query_name: str = ""

    def ids(self, *ids: str) -> "IdsQuery":
        self.values.extend(ids)
        return self

    def boost(self, boost: float) -> "IdsQuery":
        self.boost = boost
        return self

    def query_name(self, query_name: str) -> "IdsQuery":
        self.query_name = query_name
        return self

    def to_dict(self) -> dict[str, Any]:
        query: dict[str, Any] = {}

        # types - note Elasticsearch is removing types
        if len(self.types) == 1:
            query["type"] = self.types[0]
        elif len(self.types) > 1:
            query["types"] = self.types

        query["values"] = self.values

        if self.boost is not None:
            query["boost"] = self.boost
        if self.query_name:
            query["_name"] = self.query_name

        return {"ids": query}
