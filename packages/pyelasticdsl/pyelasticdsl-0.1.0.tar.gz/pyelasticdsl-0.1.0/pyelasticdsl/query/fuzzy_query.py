from typing import Any

from pyelasticdsl.dsl import Query

class FuzzyQuery(Query):

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value
        self.boost: float | None = None
        self.fuzziness: Any = None
        self.prefix_length: int | None = None
        self.max_expansions: int | None = None
        self.transpositions: bool | None = None
        self.rewrite: str = ""
        self.query_name: str = ""

    def boost(self, boost: float) -> "FuzzyQuery":
        self.boost = boost
        return self

    def fuzziness(self, fuzziness: Any) -> "FuzzyQuery":
        self.fuzziness = fuzziness
        return self

    def prefix_length(self, prefix_length: int) -> "FuzzyQuery":
        self.prefix_length = prefix_length
        return self

    def max_expansions(self, max_expansions: int) -> "FuzzyQuery":
        self.max_expansions = max_expansions
        return self

    def transpositions(self, transpositions: bool) -> "FuzzyQuery":
        self.transpositions = transpositions
        return self

    def rewrite(self, rewrite: str) -> "FuzzyQuery":
        self.rewrite = rewrite
        return self

    def query_name(self, query_name: str) -> "FuzzyQuery":
        self.query_name = query_name
        return self

    def to_dict(self) -> dict[str, Any]:
        fq = {"value": self.value}
        if self.boost is not None:
            fq["boost"] = self.boost
        if self.transpositions is not None:
            fq["transpositions"] = self.transpositions
        if self.fuzziness is not None:
            fq["fuzziness"] = self.fuzziness
        if self.prefix_length is not None:
            fq["prefix_length"] = self.prefix_length
        if self.max_expansions is not None:
            fq["max_expansions"] = self.max_expansions
        if self.rewrite:
            fq["rewrite"] = self.rewrite
        if self.query_name:
            fq["_name"] = self.query_name
        return {"fuzzy": {self.name: fq}}
