from typing import Any, Optional
from pyelasticdsl.dsl import Query


class PercolatorQuery(Query):
    def __init__(self) -> None:
        self.field: str = ""
        self.name: str = ""
        self.document_type: str = ""  # Deprecated
        self.documents: list[Any] = []

        self.indexed_document_index: str = ""
        self.indexed_document_type: str = ""
        self.indexed_document_id: str = ""
        self.indexed_document_routing: str = ""
        self.indexed_document_preference: str = ""
        self.indexed_document_version: Optional[int] = None

    def field_(self, field: str) -> "PercolatorQuery":
        self.field = field
        return self

    def name_(self, name: str) -> "PercolatorQuery":
        self.name = name
        return self

    def document_type_(self, typ: str) -> "PercolatorQuery":
        self.document_type = typ
        return self

    def document(self, *docs: Any) -> "PercolatorQuery":
        self.documents.extend(docs)
        return self

    def indexed_document_index(self, index: str) -> "PercolatorQuery":
        self.indexed_document_index = index
        return self

    def indexed_document_type(self, typ: str) -> "PercolatorQuery":
        self.indexed_document_type = typ
        return self

    def indexed_document_id(self, doc_id: str) -> "PercolatorQuery":
        self.indexed_document_id = doc_id
        return self

    def indexed_document_routing(self, routing: str) -> "PercolatorQuery":
        self.indexed_document_routing = routing
        return self

    def indexed_document_preference(self, pref: str) -> "PercolatorQuery":
        self.indexed_document_preference = pref
        return self

    def indexed_document_version(self, version: int) -> "PercolatorQuery":
        self.indexed_document_version = version
        return self

    def to_dict(self) -> dict[str, Any]:
        if not self.field:
            raise ValueError("Field is required in PercolatorQuery")

        params: dict[str, Any] = {"field": self.field}

        if self.document_type:
            params["document_type"] = self.document_type
        if self.name:
            params["name"] = self.name

        if len(self.documents) == 1:
            params["document"] = self.documents[0]
        elif len(self.documents) > 1:
            params["documents"] = self.documents

        if self.indexed_document_index:
            params["index"] = self.indexed_document_index
        if self.indexed_document_type:
            params["type"] = self.indexed_document_type
        if self.indexed_document_id:
            params["id"] = self.indexed_document_id
        if self.indexed_document_routing:
            params["routing"] = self.indexed_document_routing
        if self.indexed_document_preference:
            params["preference"] = self.indexed_document_preference
        if self.indexed_document_version is not None:
            params["version"] = self.indexed_document_version

        return {"percolate": params}
