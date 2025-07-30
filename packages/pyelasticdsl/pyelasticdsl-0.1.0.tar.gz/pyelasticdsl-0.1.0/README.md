# pyelasticdsl

A minimal, Pythonic DSL for building Elasticsearch queries with method chaining.  
Supports common query types such as `MatchQuery`, `TermQuery`, `QueryStringQuery`, `RegexpQuery`, `ExistsQuery`, `PercolatorQuery`, and more.

> ✅ Compatible with Python 3.12+

---

## 📦 Installation

```bash
pip install pyelasticdsl
````

## 🧱 Basic Usage

```python
from pyelasticdsl.query import QueryStringQuery

query = (
    QueryStringQuery("user:kimchy AND message:search")
    .DefaultField("content")
    .DefaultOperator("AND")
    .AnalyzeWildcard(True)
    .Boost(2.0)
)

print(query.to_dict())
```

Produces:

```json
{
  "query_string": {
    "query": "user:kimchy AND message:search",
    "default_field": "content",
    "default_operator": "AND",
    "analyze_wildcard": true,
    "boost": 2.0
  }
}
```

---

## 🧪 Supported Queries

* `MatchQuery`
* `TermQuery`
* `QueryStringQuery`
* `RegexpQuery`
* `ExistsQuery`
* `PercolatorQuery`
* ...more coming soon
