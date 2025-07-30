from typing import Optional, Any

from pyelasticdsl.dsl import Query


class MatchAllQuery(Query):
    def __init__(self):
        self.__boost: Optional[float] = None
        self.__query_name: Optional[str] = None

    def boost(self, boost: float) -> "MatchAllQuery":
        self.__boost = boost
        return self

    def query_name(self, name: str) -> "MatchAllQuery":
        self.__query_name = name
        return self

    def to_dict(self) -> dict[str, Any]:
        match_all_body: dict[str, Any] = {}

        if self.__boost is not None:
            match_all_body["boost"] = self.__boost
        if self.__query_name:
            match_all_body["_name"] = self.__query_name

        return {"match_all": match_all_body}


class MatchNoneQuery(Query):
    def __init__(self):
        self.__query_name: Optional[str] = None

    def query_name(self, name: str) -> "MatchNoneQuery":
        self.__query_name = name
        return self

    def to_dict(self) -> dict[str, Any]:
        match_none_body: dict[str, Any] = {}
        if self.__query_name:
            match_none_body["_name"] = self.__query_name
        return {"match_none": match_none_body}


class MatchQuery(Query):
    def __init__(self, name: str, text: Any):
        self.__name = name
        self.__text = text
        self.__operator: Optional[str] = None  # "and" / "or"
        self.__analyzer: Optional[str] = None
        self.__boost: Optional[float] = None
        self.__fuzziness: Optional[str] = None
        self.__prefix_length: Optional[int] = None
        self.__max_expansions: Optional[int] = None
        self.__minimum_should_match: Optional[str] = None
        self.__fuzzy_rewrite: Optional[str] = None
        self.__lenient: Optional[bool] = None
        self.__fuzzy_transpositions: Optional[bool] = None
        self.__zero_terms_query: Optional[str] = None  # "none" / "all"
        self.__cutoff_frequency: Optional[float] = None
        self.__query_name: Optional[str] = None

    def operator(self, op: str) -> "MatchQuery":
        self.__operator = op
        return self

    def analyzer(self, analyzer: str) -> "MatchQuery":
        self.__analyzer = analyzer
        return self

    def fuzziness(self, fuzziness: str) -> "MatchQuery":
        self.__fuzziness = fuzziness
        return self

    def prefix_length(self, length: int) -> "MatchQuery":
        self.__prefix_length = length
        return self

    def max_expansions(self, expansions: int) -> "MatchQuery":
        self.__max_expansions = expansions
        return self

    def minimum_should_match(self, minimum: str) -> "MatchQuery":
        self.__minimum_should_match = minimum
        return self

    def fuzzy_rewrite(self, rewrite: str) -> "MatchQuery":
        self.__fuzzy_rewrite = rewrite
        return self

    def lenient(self, is_lenient: bool) -> "MatchQuery":
        self.__lenient = is_lenient
        return self

    def fuzzy_transpositions(self, enable: bool) -> "MatchQuery":
        self.__fuzzy_transpositions = enable
        return self

    def zero_terms_query(self, val: str) -> "MatchQuery":
        self.__zero_terms_query = val
        return self

    def cutoff_frequency(self, freq: float) -> "MatchQuery":
        self.__cutoff_frequency = freq
        return self

    def boost(self, boost: float) -> "MatchQuery":
        self.__boost = boost
        return self

    def query_name(self, name: str) -> "MatchQuery":
        self.__query_name = name
        return self

    def to_dict(self) -> dict[str, Any]:
        query: dict[str, Any] = {
            "query": self.__text
        }
        if self.__operator:
            query["operator"] = self.__operator
        if self.__analyzer:
            query["analyzer"] = self.__analyzer
        if self.__fuzziness:
            query["fuzziness"] = self.__fuzziness
        if self.__prefix_length is not None:
            query["prefix_length"] = self.__prefix_length
        if self.__max_expansions is not None:
            query["max_expansions"] = self.__max_expansions
        if self.__minimum_should_match:
            query["minimum_should_match"] = self.__minimum_should_match
        if self.__fuzzy_rewrite:
            query["fuzzy_rewrite"] = self.__fuzzy_rewrite
        if self.__lenient is not None:
            query["lenient"] = self.__lenient
        if self.__fuzzy_transpositions is not None:
            query["fuzzy_transpositions"] = self.__fuzzy_transpositions
        if self.__zero_terms_query:
            query["zero_terms_query"] = self.__zero_terms_query
        if self.__cutoff_frequency is not None:
            query["cutoff_frequency"] = self.__cutoff_frequency
        if self.__boost is not None:
            query["boost"] = self.__boost
        if self.__query_name:
            query["_name"] = self.__query_name

        return {
            "match": {
                self.__name: query
            }
        }


class MatchPhraseQuery(Query):
    def __init__(self, name: str, value: Any):
        self.__name = name
        self.__value = value
        self.__analyzer: Optional[str] = None
        self.__slop: Optional[int] = None
        self.__boost: Optional[float] = None
        self.__query_name: Optional[str] = None
        self.__zero_terms_query: Optional[str] = None

    def analyzer(self, analyzer: str) -> "MatchPhraseQuery":
        self.__analyzer = analyzer
        return self

    def slop(self, slop: int) -> "MatchPhraseQuery":
        self.__slop = slop
        return self

    def zero_terms_query(self, zero_terms_query: str) -> "MatchPhraseQuery":
        self.__zero_terms_query = zero_terms_query
        return self

    def boost(self, boost: float) -> "MatchPhraseQuery":
        self.__boost = boost
        return self

    def query_name(self, query_name: str) -> "MatchPhraseQuery":
        self.__query_name = query_name
        return self

    def to_dict(self) -> dict[str, Any]:
        query: dict[str, Any] = {"query": self.__value}

        if self.__analyzer:
            query["analyzer"] = self.__analyzer
        if self.__slop is not None:
            query["slop"] = self.__slop
        if self.__zero_terms_query:
            query["zero_terms_query"] = self.__zero_terms_query
        if self.__boost is not None:
            query["boost"] = self.__boost
        if self.__query_name:
            query["_name"] = self.__query_name

        return {"match_phrase": {self.__name: query}}


class MatchPhrasePrefixQuery(Query):
    def __init__(self, name: str, value: Any):
        self.__name = name
        self.__value = value
        self.__analyzer: Optional[str] = None
        self.__slop: Optional[int] = None
        self.__max_expansions: Optional[int] = None
        self.__boost: Optional[float] = None
        self.__query_name: Optional[str] = None

    def analyzer(self, analyzer: str) -> "MatchPhrasePrefixQuery":
        self.__analyzer = analyzer
        return self

    def slop(self, slop: int) -> "MatchPhrasePrefixQuery":
        self.__slop = slop
        return self

    def max_expansions(self, max_expansions: int) -> "MatchPhrasePrefixQuery":
        self.__max_expansions = max_expansions
        return self

    def boost(self, boost: float) -> "MatchPhrasePrefixQuery":
        self.__boost = boost
        return self

    def query_name(self, query_name: str) -> "MatchPhrasePrefixQuery":
        self.__query_name = query_name
        return self

    def to_dict(self) -> dict[str, Any]:
        query: dict[str, Any] = {"query": self.__value}

        if self.__analyzer:
            query["analyzer"] = self.__analyzer
        if self.__slop is not None:
            query["slop"] = self.__slop
        if self.__max_expansions is not None:
            query["max_expansions"] = self.__max_expansions
        if self.__boost is not None:
            query["boost"] = self.__boost
        if self.__query_name:
            query["_name"] = self.__query_name

        return {"match_phrase_prefix": {self.__name: query}}


class MatchBoolPrefixQuery(Query):
    def __init__(self, name: str, query_text: Any):
        self.__name = name
        self.__query_text = query_text
        self.__analyzer: Optional[str] = None
        self.__minimum_should_match: Optional[str] = None
        self.__operator: Optional[str] = None
        self.__fuzziness: Optional[str] = None
        self.__prefix_length: Optional[int] = None
        self.__max_expansions: Optional[int] = None
        self.__fuzzy_transpositions: Optional[bool] = None
        self.__fuzzy_rewrite: Optional[str] = None
        self.__boost: Optional[float] = None

    def analyzer(self, analyzer: str) -> "MatchBoolPrefixQuery":
        self.__analyzer = analyzer
        return self

    def minimum_should_match(self, minimum_should_match: str) -> "MatchBoolPrefixQuery":
        self.__minimum_should_match = minimum_should_match
        return self

    def operator(self, operator: str) -> "MatchBoolPrefixQuery":
        self.__operator = operator
        return self

    def fuzziness(self, fuzziness: str) -> "MatchBoolPrefixQuery":
        self.__fuzziness = fuzziness
        return self

    def prefix_length(self, prefix_length: int) -> "MatchBoolPrefixQuery":
        self.__prefix_length = prefix_length
        return self

    def max_expansions(self, max_expansions: int) -> "MatchBoolPrefixQuery":
        self.__max_expansions = max_expansions
        return self

    def fuzzy_transpositions(self, fuzzy_transpositions: bool) -> "MatchBoolPrefixQuery":
        self.__fuzzy_transpositions = fuzzy_transpositions
        return self

    def fuzzy_rewrite(self, fuzzy_rewrite: str) -> "MatchBoolPrefixQuery":
        self.__fuzzy_rewrite = fuzzy_rewrite
        return self

    def boost(self, boost: float) -> "MatchBoolPrefixQuery":
        self.__boost = boost
        return self

    def to_dict(self) -> dict[str, Any]:
        query: dict[str, Any] = {"query": self.__query_text}

        if self.__analyzer:
            query["analyzer"] = self.__analyzer
        if self.__minimum_should_match:
            query["minimum_should_match"] = self.__minimum_should_match
        if self.__operator:
            query["operator"] = self.__operator
        if self.__fuzziness:
            query["fuzziness"] = self.__fuzziness
        if self.__prefix_length is not None:
            query["prefix_length"] = self.__prefix_length
        if self.__max_expansions is not None:
            query["max_expansions"] = self.__max_expansions
        if self.__fuzzy_transpositions is not None:
            query["fuzzy_transpositions"] = self.__fuzzy_transpositions
        if self.__fuzzy_rewrite:
            query["fuzzy_rewrite"] = self.__fuzzy_rewrite
        if self.__boost is not None:
            query["boost"] = self.__boost

        return {"match_bool_prefix": {self.__name: query}}


class MultiMatchQuery:
    def __init__(self, text: Any, *fields: str):
        self.__text = text
        self.__fields = list(fields)
        self.__field_boosts: dict[str, Optional[float]] = {}
        self.__type = ""
        self.__operator = ""
        self.__analyzer = ""
        self.__boost: Optional[float] = None
        self.__slop: Optional[int] = None
        self.__fuzziness = ""
        self.__prefix_length: Optional[int] = None
        self.__max_expansions: Optional[int] = None
        self.__minimum_should_match = ""
        self.__rewrite = ""
        self.__fuzzy_rewrite = ""
        self.__tie_breaker: Optional[float] = None
        self.__lenient: Optional[bool] = None
        self.__cutoff_frequency: Optional[float] = None
        self.__zero_terms_query = ""
        self.__query_name = ""

    def field(self, field: str) -> "MultiMatchQuery":
        self.__fields.append(field)
        return self

    def field_with_boost(self, field: str, boost: float) -> "MultiMatchQuery":
        self.__fields.append(field)
        self.__field_boosts[field] = boost
        return self

    def type(self, typ: str) -> "MultiMatchQuery":
        typ_lower = typ.lower()
        if typ_lower in ["most_fields", "cross_fields", "phrase", "phrase_prefix", "bool_prefix"]:
            self.__type = typ_lower
        else:
            self.__type = "best_fields"
        return self

    def operator(self, operator: str) -> "MultiMatchQuery":
        self.__operator = operator
        return self

    def analyzer(self, analyzer: str) -> "MultiMatchQuery":
        self.__analyzer = analyzer
        return self

    def boost(self, boost: float) -> "MultiMatchQuery":
        self.__boost = boost
        return self

    def slop(self, slop: int) -> "MultiMatchQuery":
        self.__slop = slop
        return self

    def fuzziness(self, fuzziness: str) -> "MultiMatchQuery":
        self.__fuzziness = fuzziness
        return self

    def prefix_length(self, prefix_length: int) -> "MultiMatchQuery":
        self.__prefix_length = prefix_length
        return self

    def max_expansions(self, max_expansions: int) -> "MultiMatchQuery":
        self.__max_expansions = max_expansions
        return self

    def minimum_should_match(self, minimum_should_match: str) -> "MultiMatchQuery":
        self.__minimum_should_match = minimum_should_match
        return self

    def rewrite(self, rewrite: str) -> "MultiMatchQuery":
        self.__rewrite = rewrite
        return self

    def fuzzy_rewrite(self, fuzzy_rewrite: str) -> "MultiMatchQuery":
        self.__fuzzy_rewrite = fuzzy_rewrite
        return self

    def tie_breaker(self, tie_breaker: float) -> "MultiMatchQuery":
        self.__tie_breaker = tie_breaker
        return self

    def lenient(self, lenient: bool) -> "MultiMatchQuery":
        self.__lenient = lenient
        return self

    def cutoff_frequency(self, cutoff_frequency: float) -> "MultiMatchQuery":
        self.__cutoff_frequency = cutoff_frequency
        return self

    def zero_terms_query(self, zero_terms_query: str) -> "MultiMatchQuery":
        self.__zero_terms_query = zero_terms_query
        return self

    def query_name(self, query_name: str) -> "MultiMatchQuery":
        self.__query_name = query_name
        return self

    def to_dict(self) -> dict[str, Any]:
        multi_match: dict[str, Any] = {"query": self.__text}

        fields_list = []
        for field in self.__fields:
            boost = self.__field_boosts.get(field)
            if boost is not None:
                fields_list.append(f"{field}^{boost}")
            else:
                fields_list.append(field)
        multi_match["fields"] = fields_list or []

        if self.__type:
            multi_match["type"] = self.__type
        if self.__operator:
            multi_match["operator"] = self.__operator
        if self.__analyzer:
            multi_match["analyzer"] = self.__analyzer
        if self.__boost is not None:
            multi_match["boost"] = self.__boost
        if self.__slop is not None:
            multi_match["slop"] = self.__slop
        if self.__fuzziness:
            multi_match["fuzziness"] = self.__fuzziness
        if self.__prefix_length is not None:
            multi_match["prefix_length"] = self.__prefix_length
        if self.__max_expansions is not None:
            multi_match["max_expansions"] = self.__max_expansions
        if self.__minimum_should_match:
            multi_match["minimum_should_match"] = self.__minimum_should_match
        if self.__rewrite:
            multi_match["rewrite"] = self.__rewrite
        if self.__fuzzy_rewrite:
            multi_match["fuzzy_rewrite"] = self.__fuzzy_rewrite
        if self.__tie_breaker is not None:
            multi_match["tie_breaker"] = self.__tie_breaker
        if self.__lenient is not None:
            multi_match["lenient"] = self.__lenient
        if self.__cutoff_frequency is not None:
            multi_match["cutoff_frequency"] = self.__cutoff_frequency
        if self.__zero_terms_query:
            multi_match["zero_terms_query"] = self.__zero_terms_query
        if self.__query_name:
            multi_match["_name"] = self.__query_name

        return {"multi_match": multi_match}
