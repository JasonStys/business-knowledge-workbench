# @index-begin
# @symbol function/class: LibraryQuery L64
# @symbol variable/parameter: model_config L67
# @symbol variable/parameter: workspace L68
# @symbol variable/parameter: q L69
# @symbol variable/parameter: category L70
# @symbol variable/parameter: source_format L71
# @symbol variable/parameter: kind L72
# @symbol variable/parameter: dimension L73
# @symbol variable/parameter: visibility L74
# @symbol variable/parameter: review_status L75
# @symbol variable/parameter: field L76
# @symbol variable/parameter: value L77
# @symbol variable/parameter: minimum L78
# @symbol variable/parameter: maximum L81
# @symbol variable/parameter: unit L84
# @symbol variable/parameter: sort L85
# @symbol variable/parameter: offset L86
# @symbol variable/parameter: limit L87
# @symbol function/class: paired_field L90
# @symbol variable/parameter: self L90
# @symbol variable/parameter: ranged L94
# @symbol function/class: literal_pattern L104
# @symbol function/class: search L111
# @symbol variable/parameter: database L112
# @symbol variable/parameter: query L112
# @symbol variable/parameter: user L112
# @symbol variable/parameter: predicate L120
# @symbol variable/parameter: scope L120
# @symbol variable/parameter: text L122
# @symbol variable/parameter: clauses L125
# @symbol variable/parameter: values L125
# @symbol variable/parameter: expression L131
# @symbol variable/parameter: selected L131
# @symbol variable/parameter: field_clause L151
# @symbol variable/parameter: where L173
# @symbol variable/parameter: order L174
# @symbol variable/parameter: total L179
# @symbol variable/parameter: rows L180
# @symbol variable/parameter: facets L194
# @symbol variable/parameter: expressions L195
# @symbol variable/parameter: name L202
# @symbol variable/parameter: records L203
# @symbol variable/parameter: row L211
# @index-end
"""Jason Stys: bounded, ACL-first library search over standardized content only.

Functions/classes/variables: docs/code-index.md (generated exact line locations).
No source bytes or full HTML are returned by the search endpoint. All user values
are bound SQL parameters; sort fragments and JSON paths are authored constants.
"""

import sqlite3
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .quantitative import in_range
from .store import acl
from .units import DIMENSIONS


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
    minimum: Decimal | None = Field(
        default=None, ge=Decimal("-1e15"), le=Decimal("1e15"), max_digits=28, decimal_places=12
    )
    maximum: Decimal | None = Field(
        default=None, ge=Decimal("-1e15"), le=Decimal("1e15"), max_digits=28, decimal_places=12
    )
    unit: str = Field(default="", max_length=4)
    sort: Literal["title", "newest", "category"] = "title"
    offset: int = Field(default=0, ge=0, le=200)
    limit: int = Field(default=25, ge=1, le=200)

    @model_validator(mode="after")
    def paired_field(self):
        """Never imply that an unqualified cell value is bound to a particular field."""
        if self.value and not self.field:
            raise ValueError("Choose a table field when filtering a field value")
        ranged = self.minimum is not None or self.maximum is not None
        if ranged and not self.field:
            raise ValueError("Choose a table field for numeric bounds")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("Minimum must not exceed maximum")
        if self.unit and (self.unit not in DIMENSIONS or not ranged):
            raise ValueError("Choose a supported unit and at least one numeric bound")
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
    database.create_function("kbw_in_range", 4, in_range, deterministic=True)
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
        ranged = query.minimum is not None or query.maximum is not None
        if query.value or ranged:
            field_clause += """ AND EXISTS(SELECT 1 FROM json_each(b.value,'$.rows') r
                WHERE CAST(r.key AS INTEGER)>0"""
            if query.value:
                field_clause += " AND kbw_casefold(json_extract(r.value,'$[' || h.key || ']')) LIKE ? ESCAPE '\\'"
                values.append(literal_pattern(query.value))
            if ranged:
                field_clause += " AND json_type(r.value,'$[' || h.key || ']') IN ('text','integer','real') AND kbw_in_range(json_extract(r.value,'$[' || h.key || ']'),?,?,?)=1"
                values.extend(
                    [
                        str(query.minimum) if query.minimum is not None else None,
                        str(query.maximum) if query.maximum is not None else None,
                        query.unit,
                    ]
                )
            field_clause += ")"
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
