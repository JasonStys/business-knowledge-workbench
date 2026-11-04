# @index-begin
# @symbol function/class: LibraryQuery L57
# @symbol variable/parameter: model_config L60
# @symbol variable/parameter: workspace L61
# @symbol variable/parameter: q L62
# @symbol variable/parameter: category L63
# @symbol variable/parameter: source_format L64
# @symbol variable/parameter: kind L65
# @symbol variable/parameter: dimension L66
# @symbol variable/parameter: visibility L67
# @symbol variable/parameter: review_status L68
# @symbol variable/parameter: field L69
# @symbol variable/parameter: value L70
# @symbol variable/parameter: sort L71
# @symbol variable/parameter: offset L72
# @symbol variable/parameter: limit L73
# @symbol function/class: paired_field L76
# @symbol variable/parameter: self L76
# @symbol function/class: literal_pattern L83
# @symbol function/class: search L90
# @symbol variable/parameter: database L91
# @symbol variable/parameter: query L91
# @symbol variable/parameter: user L91
# @symbol variable/parameter: predicate L99
# @symbol variable/parameter: scope L99
# @symbol variable/parameter: text L101
# @symbol variable/parameter: clauses L103
# @symbol variable/parameter: values L103
# @symbol variable/parameter: expression L109
# @symbol variable/parameter: selected L109
# @symbol variable/parameter: field_clause L129
# @symbol variable/parameter: where L138
# @symbol variable/parameter: order L139
# @symbol variable/parameter: total L144
# @symbol variable/parameter: rows L145
# @symbol variable/parameter: facets L159
# @symbol variable/parameter: expressions L160
# @symbol variable/parameter: name L167
# @symbol variable/parameter: records L168
# @symbol variable/parameter: row L176
# @index-end
"""Jason Stys: bounded, ACL-first library search over standardized content only.

Functions/classes/variables: docs/code-index.md (generated exact line locations).
No source bytes or full HTML are returned by the search endpoint. All user values
are bound SQL parameters; sort fragments and JSON paths are authored constants.
"""

import sqlite3
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .store import acl


class LibraryQuery(BaseModel):
    """Finite filters, literal substring terms and stable bounded pagination."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    workspace: str = Field(default="industrial", pattern=r"^[a-z][a-z0-9-]{1,32}$")
    q: str = Field(default="", max_length=120)
    category: str = Field(default="", max_length=40)
    source_format: str = Field(default="", pattern=r"^[a-z0-9-]{0,16}$")
    kind: Literal["", "table", "paragraph", "heading", "html", "figure", "equation"] = ""
    dimension: Literal["", "length", "mass", "temperature", "pressure", "voltage", "energy"] = ""
    visibility: Literal["", "public", "customer", "internal"] = ""
    review_status: Literal["", "extracted", "needs-review"] = ""
    field: str = Field(default="", max_length=120)
    value: str = Field(default="", max_length=120)
    sort: Literal["title", "newest", "category"] = "title"
    offset: int = Field(default=0, ge=0, le=200)
    limit: int = Field(default=25, ge=1, le=200)

    @model_validator(mode="after")
    def paired_field(self):
        """Never imply that an unqualified cell value is bound to a particular field."""
        if self.value and not self.field:
            raise ValueError("Choose a table field when filtering a field value")
        return self


def literal_pattern(value: str) -> str:
    """Case-fold Unicode text and escape wildcard syntax for literal LIKE matching."""
    return (
        "%" + value.casefold().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    )


def search(
    database: sqlite3.Connection, user: dict | None, workspace: str, query: LibraryQuery
) -> dict:
    """Search at most 200 profile documents; O(authorized content) without an N+1 fetch.

    Facets describe the entire authorized profile, not other tenants or customers.
    Field/value predicates bind the SAME table column and row; they do not match
    a key in one table and a coincidental value in an unrelated table.
    """
    predicate, scope = acl(user, workspace)
    database.create_function(
        "kbw_casefold", 1, lambda text: str(text or "").casefold(), deterministic=True
    )
    clauses, values = [predicate], list(scope)
    if query.q:
        clauses.append(
            "(kbw_casefold(title) LIKE ? ESCAPE '\\' OR kbw_casefold(json_extract(result,'$.text')) LIKE ? ESCAPE '\\')"
        )
        values.extend([literal_pattern(query.q)] * 2)
    for selected, expression in (
        (query.category, "category"),
        (query.visibility, "visibility"),
        (query.source_format, "json_extract(result,'$.provenance.conversion_path[0]')"),
        (query.review_status, "json_extract(result,'$.review_status')"),
    ):
        if selected:
            clauses.append(expression + "=?")
            values.append(selected)
    if query.kind:
        clauses.append(
            "EXISTS(SELECT 1 FROM json_each(result,'$.blocks') b WHERE json_extract(b.value,'$.kind')=?)"
        )
        values.append(query.kind)
    if query.dimension:
        clauses.append(
            "EXISTS(SELECT 1 FROM json_each(result,'$.measurements') m WHERE json_extract(m.value,'$.dimension')=?)"
        )
        values.append(query.dimension)
    if query.field:
        field_clause = """EXISTS(SELECT 1 FROM json_each(result,'$.blocks') b,
            json_each(b.value,'$.rows[0]') h WHERE json_extract(b.value,'$.kind')='table'
            AND kbw_casefold(h.value)=?"""
        values.append(query.field.casefold())
        if query.value:
            field_clause += """ AND EXISTS(SELECT 1 FROM json_each(b.value,'$.rows') r
                WHERE CAST(r.key AS INTEGER)>0 AND kbw_casefold(json_extract(r.value,'$[' || h.key || ']')) LIKE ? ESCAPE '\\')"""
            values.append(literal_pattern(query.value))
        clauses.append(field_clause + ")")
    where = " AND ".join(clauses)
    order = {
        "title": "title COLLATE NOCASE,id",
        "newest": "created DESC,id",
        "category": "category,title,id",
    }[query.sort]
    total = database.execute("SELECT COUNT(*) FROM documents WHERE " + where, values).fetchone()[0]
    rows = database.execute(
        """SELECT id,title,category,visibility,created,
        json_extract(result,'$.review_status') review_status,
        json_extract(result,'$.provenance.conversion_path[0]') source_format,
        COALESCE(json_extract(result,'$.standard.output_standard.default_export'),'html') standard_format,
        json_extract(result,'$.standard.revision') standard_revision,
        substr(json_extract(result,'$.text'),1,240) excerpt,
        source IS NOT NULL has_source FROM documents WHERE """
        + where
        + " ORDER BY "
        + order
        + " LIMIT ? OFFSET ?",
        [*values, query.limit, query.offset],
    ).fetchall()
    facets = {}
    expressions = {
        "categories": "SELECT category value FROM authorized",
        "formats": "SELECT json_extract(result,'$.provenance.conversion_path[0]') value FROM authorized",
        "visibility": "SELECT visibility value FROM authorized",
        "fields": "SELECT h.value FROM authorized,json_each(result,'$.blocks') b,json_each(b.value,'$.rows[0]') h WHERE json_extract(b.value,'$.kind')='table'",
        "dimensions": "SELECT json_extract(m.value,'$.dimension') value FROM authorized,json_each(result,'$.measurements') m",
    }
    for name, expression in expressions.items():
        records = database.execute(
            "WITH authorized AS (SELECT category,visibility,result FROM documents WHERE "
            + predicate
            + ") SELECT DISTINCT value FROM ("
            + expression
            + ") WHERE value IS NOT NULL AND length(value) BETWEEN 1 AND 120 ORDER BY value LIMIT 200",
            scope,
        ).fetchall()
        facets[name] = [row[0] for row in records]
    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "offset": query.offset,
        "limit": query.limit,
        "facets": facets,
    }
