from typing import Any

from pyelasticdsl.dsl import Query

class TermsLookup(Query):
    def __init__(self):
        self.__index: str = ""
        self.__typ: str = ""  # deprecated
        self.__id: str = ""
        self.__path: str = ""
        self.__routing: str = ""

    def index(self, index: str) -> "TermsLookup":
        self.__index = index
        return self

    def typ(self, typ: str) -> "TermsLookup":
        self.__typ = typ
        return self

    def id(self, id: str) -> "TermsLookup":
        self.__id = id
        return self

    def path(self, path: str) -> "TermsLookup":
        self.__path = path
        return self

    def routing(self, routing: str) -> "TermsLookup":
        self.__routing = routing
        return self

    def to_dict(self) -> dict[str, Any]:
        src: dict[str, Any] = {}
        if self.__index:
            src["index"] = self.__index
        if self.__typ:
            src["type"] = self.__typ
        if self.__id:
            src["id"] = self.__id
        if self.__path:
            src["path"] = self.__path
        if self.__routing:
            src["routing"] = self.__routing
        return src
