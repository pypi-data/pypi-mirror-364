from typing import Dict, Any,Optional

from pyelasticdsl.dsl import Query
from pyelasticdsl.query.term_query_lookup import TermsLookup
from pyelasticdsl.query.script import Script

class TermQuery(Query):
    def __init__(self, name: str, value: Any):
        self.__name = name
        self.__value = value
        self.__boost: Optional[float] = None
        self.__case_insensitive: Optional[bool] = None
        self.__query_name: Optional[str] = None

    def boost(self, boost: float) -> "TermQuery":
        self.__boost = boost
        return self

    def case_insensitive(self, case_insensitive: bool) -> "TermQuery":
        self.__case_insensitive = case_insensitive
        return self

    def query_name(self, query_name: str) -> "TermQuery":
        self.__query_name = query_name
        return self

    def to_dict(self) -> Dict[str, Any]:
        term_body: Dict[str, Any] = {}

        if self.__boost is None and self.__case_insensitive is None and self.__query_name is None:
            term_body[self.__name] = self.__value
        else:
            sub_body = {"value": self.__value}
            if self.__boost is not None:
                sub_body["boost"] = self.__boost
            if self.__case_insensitive is not None:
                sub_body["case_insensitive"] = self.__case_insensitive
            if self.__query_name:
                sub_body["_name"] = self.__query_name
            term_body[self.__name] = sub_body

        return {"term": term_body}


class TermsQuery:
    def __init__(self, name: str, *values: Any):
        self.__name = name
        self.__values: list[Any] = list(values) if values else []
        self.__terms_lookup: Optional[TermsLookup] = None
        self.__query_name: str = ""
        self.__boost: Optional[float] = None

    @classmethod
    def from_strings(cls, name: str, *values: str) -> "TermsQuery":
        return cls(name, *values)

    def terms_lookup(self, lookup: TermsLookup) -> "TermsQuery":
        self.__terms_lookup = lookup
        return self

    def boost(self, boost: float) -> "TermsQuery":
        self.__boost = boost
        return self

    def query_name(self, query_name: str) -> "TermsQuery":
        self.__query_name = query_name
        return self

    def to_dict(self) -> dict[str, Any]:
        params: dict[str, Any] = {}

        if self.__terms_lookup is not None:
            src = self.__terms_lookup.to_dict()
            params[self.__name] = src
        else:
            params[self.__name] = self.__values
            if self.__boost is not None:
                params["boost"] = self.__boost
            if self.__query_name:
                params["_name"] = self.__query_name

        return {"terms": params}


class SpanTermQuery(Query):
    def __init__(self, field: str, *value: Any):
        self.__field: str = field
        self.__value: Any = value[0] if value else None
        self.__boost: float | None = None
        self.__query_name: str = ""

    def field(self, field: str) -> "SpanTermQuery":
        self.__field = field
        return self

    def value(self, value: Any) -> "SpanTermQuery":
        self.__value = value
        return self

    def boost(self, boost: float) -> "SpanTermQuery":
        self.__boost = boost
        return self

    def query_name(self, query_name: str) -> "SpanTermQuery":
        self.__query_name = query_name
        return self

    def to_dict(self) -> dict[str, Any]:
        inner: dict[str, Any] = {"value": self.__value}
        if self.__boost is not None:
            inner["boost"] = self.__boost
        if self.__query_name:
            inner["query_name"] = self.__query_name

        return {
            "span_term": {
                self.__field: inner
            }
        }


class TermsSetQuery(Query):
    def __init__(self, name: str, *values: Any):
        self.__name = name
        self.__values = list(values) if values else []
        self.__minimum_should_match_field: str = ""
        self.__minimum_should_match_script: Script | None = None
        self.__query_name: str = ""
        self.__boost: float | None = None

    def minimum_should_match_field(self, field: str) -> "TermsSetQuery":
        self.__minimum_should_match_field = field
        return self

    def minimum_should_match_script(self, script: "Script") -> "TermsSetQuery":
        self.__minimum_should_match_script = script
        return self

    def boost(self, boost: float) -> "TermsSetQuery":
        self.__boost = boost
        return self

    def query_name(self, name: str) -> "TermsSetQuery":
        self.__query_name = name
        return self

    def to_dict(self) -> dict[str, Any]:
        params = {
            "terms": self.__values
        }

        if self.__minimum_should_match_field:
            params["minimum_should_match_field"] = self.__minimum_should_match_field

        if self.__minimum_should_match_script is not None:
            script_src = self.__minimum_should_match_script.to_dict()
            params["minimum_should_match_script"] = script_src

        if self.__boost is not None:
            params["boost"] = self.__boost

        if self.__query_name:
            params["_name"] = self.__query_name

        return {
            "terms_set": {
                self.__name: params
            }
        }

