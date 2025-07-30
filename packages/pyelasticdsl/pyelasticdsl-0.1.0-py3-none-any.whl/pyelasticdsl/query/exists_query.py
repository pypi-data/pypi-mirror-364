from typing import Any
from pyelasticdsl.dsl import Query

class ExistsQuery(Query):

    def __init__(self, name: str):
        self.name: str = name
        self.query_name: str = ""

    def query_name(self, query_name: str) -> "ExistsQuery":
        self.query_name = query_name
        return self

    def to_dict(self) -> dict[str, Any]:
        query = {"exists": {"field": self.name}}
        if self.query_name:
            query["exists"]["_name"] = self.query_name
        return query
