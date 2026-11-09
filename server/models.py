# @index-begin
# @symbol variable/parameter: UNITS L94
# @symbol function/class: StandardColumn L104
# @symbol variable/parameter: model_config L107
# @symbol variable/parameter: key L108
# @symbol variable/parameter: label L109
# @symbol variable/parameter: aliases L110
# @symbol variable/parameter: dimension L111
# @symbol variable/parameter: source_unit L114
# @symbol variable/parameter: required L115
# @symbol variable/parameter: enabled L116
# @symbol function/class: consistent L119
# @symbol variable/parameter: self L119
# @symbol function/class: OutputStandard L130
# @symbol variable/parameter: name L134
# @symbol variable/parameter: section_titles L135
# @symbol variable/parameter: default_export L143
# @symbol variable/parameter: enforce_export L144
# @symbol variable/parameter: paper L145
# @symbol variable/parameter: orientation L146
# @symbol variable/parameter: font L147
# @symbol variable/parameter: font_size L148
# @symbol variable/parameter: accent L149
# @symbol variable/parameter: margin_mm L150
# @symbol variable/parameter: alignment L151
# @symbol variable/parameter: line_spacing L152
# @symbol variable/parameter: paragraph_after_pt L153
# @symbol variable/parameter: header_text L154
# @symbol variable/parameter: footer_text L155
# @symbol variable/parameter: page_numbers L156
# @symbol variable/parameter: columns L157
# @symbol variable/parameter: extra_columns L158
# @symbol variable/parameter: table_scope L159
# @symbol function/class: unambiguous L162
# @symbol variable/parameter: names L168
# @symbol variable/parameter: column L169
# @symbol variable/parameter: alias L170
# @symbol variable/parameter: v L173
# @symbol function/class: WorkspaceConfig L187
# @symbol variable/parameter: title L191
# @symbol variable/parameter: profile L192
# @symbol variable/parameter: customers L193
# @symbol variable/parameter: units L196
# @symbol variable/parameter: sections L199
# @symbol variable/parameter: forecasting L204
# @symbol variable/parameter: ai_enabled L205
# @symbol variable/parameter: data_columns L206
# @symbol variable/parameter: revision L211
# @symbol variable/parameter: output_standard L212
# @symbol function/class: column_targets L215
# @symbol variable/parameter: cls L226
# @symbol function/class: validate_customers L226
# @symbol function/class: validate_columns L239
# @symbol function/class: validate_units L251
# @symbol variable/parameter: unit L255
# @symbol function/class: validate_sections L262
# @symbol function/class: Login L269
# @symbol variable/parameter: workspace L272
# @symbol variable/parameter: username L273
# @symbol variable/parameter: password L274
# @symbol function/class: StandardPreview L277
# @symbol variable/parameter: config L281
# @symbol variable/parameter: sample L282
# @symbol function/class: StandardRestore L285
# @symbol variable/parameter: expected_revision L290
# @symbol function/class: MergeRequest L293
# @symbol variable/parameter: ids L296
# @symbol function/class: BundleRequest L300
# @symbol function/class: valid_ids L308
# @symbol variable/parameter: item L310
# @symbol function/class: Question L315
# @symbol variable/parameter: question L318
# @symbol function/class: MeasurementRequest L321
# @symbol variable/parameter: value L324
# @symbol variable/parameter: source L325
# @symbol variable/parameter: target L326
# @symbol function/class: ProductRequest L329
# @symbol variable/parameter: id L332
# @symbol variable/parameter: category L334
# @symbol variable/parameter: description L335
# @symbol variable/parameter: price_cents L336
# @symbol variable/parameter: customer L337
# @symbol variable/parameter: specifications L338
# @index-end
"""Validated configuration and API contracts. Symbols/variables: docs/code-index.md.

Configuration is data, never executable templates, code, paths, or remote credentials.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

UNITS = {
    "length": ["mm", "cm", "m", "in", "ft"],
    "mass": ["g", "kg", "lb"],
    "temperature": ["C", "F", "K"],
    "pressure": ["Pa", "kPa", "bar", "psi"],
    "voltage": ["V", "mV"],
    "energy": ["Wh", "kWh"],
}


class StandardColumn(BaseModel):
    """One bounded output field; unitless quantities need an explicitly declared source unit."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    key: str = Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")
    label: str = Field(min_length=1, max_length=60)
    aliases: list[str] = Field(default_factory=list, max_length=8)
    dimension: Literal["length", "mass", "temperature", "pressure", "voltage", "energy"] | None = (
        None
    )
    source_unit: str | None = Field(default=None, max_length=5)
    required: bool = True
    enabled: bool = True

    @model_validator(mode="after")
    def consistent(self):
        """Reject ambiguous input labels and cross-dimensional defaults without executing templates."""
        if any(not value.strip() or len(value) > 60 for value in self.aliases):
            raise ValueError("Column aliases must be nonempty and at most 60 characters")
        if self.source_unit and (
            not self.dimension or self.source_unit not in UNITS[self.dimension]
        ):
            raise ValueError("A column source unit must belong to its declared dimension")
        return self


class OutputStandard(BaseModel):
    """Safe data-only output template: labels, print layout, schema and delivery policy."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(default="Business standard", min_length=2, max_length=80)
    section_titles: dict[str, str] = Field(
        default_factory=lambda: {
            "overview": "Overview",
            "content": "Content",
            "measurements": "Measurements",
            "provenance": "Provenance",
        }
    )
    default_export: Literal["html", "json", "md", "csv", "docx", "pdf"] = "html"
    enforce_export: bool = False
    paper: Literal["Letter", "A4"] = "Letter"
    orientation: Literal["portrait", "landscape"] = "portrait"
    font: Literal["sans", "serif", "mono"] = "sans"
    font_size: int = Field(default=12, ge=10, le=16, strict=True)
    accent: str = Field(default="#18312c", pattern=r"^#[0-9a-fA-F]{6}$")
    margin_mm: int = Field(default=20, ge=10, le=40, strict=True)
    alignment: Literal["left", "center", "right", "justify"] = "left"
    line_spacing: Literal[1.0, 1.15, 1.5, 2.0] = 1.15
    paragraph_after_pt: int = Field(default=8, ge=0, le=24, strict=True)
    header_text: str = Field(default="", max_length=120)
    footer_text: str = Field(default="", max_length=120)
    page_numbers: bool = False
    columns: list[StandardColumn] = Field(default_factory=list, max_length=20)
    extra_columns: Literal["preserve", "reject", "omit"] = "preserve"
    table_scope: Literal["matching", "all"] = "matching"

    @model_validator(mode="after")
    def unambiguous(self):
        """Require all section labels and an unambiguous canonical/alias column dictionary."""
        if set(self.section_titles) != {"overview", "content", "measurements", "provenance"} or any(
            not value.strip() or len(value) > 80 for value in self.section_titles.values()
        ):
            raise ValueError("Provide four nonempty section labels of at most 80 characters")
        names = {}
        for column in self.columns:
            for alias in {
                column.key.casefold(),
                column.label.casefold(),
                *(v.strip().casefold() for v in column.aliases),
            }:
                if alias in names and names[alias] != column.key:
                    raise ValueError(
                        "Output columns must have distinct, unambiguous labels and aliases"
                    )
                names[alias] = column.key
        if len({column.key for column in self.columns}) != len(self.columns):
            raise ValueError("Output column keys must be unique")
        if self.columns and not any(column.enabled for column in self.columns):
            raise ValueError("Enable at least one standard field or clear the schema")
        return self


class WorkspaceConfig(BaseModel):
    """Branding, normalization targets, template sections, and enabled capabilities."""

    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=2, max_length=60)
    profile: str = Field(pattern=r"^[a-z][a-z0-9-]{1,32}$")
    customers: dict[str, str] = Field(
        default_factory=lambda: {"north": "North account", "south": "South account"}
    )
    units: dict[str, str] = Field(
        default_factory=lambda: {"length": "mm", "mass": "kg", "temperature": "C"}
    )
    sections: list[Literal["overview", "content", "measurements", "provenance"]] = Field(
        default_factory=lambda: ["overview", "content", "measurements", "provenance"],
        min_length=1,
        max_length=4,
    )
    forecasting: bool = True
    ai_enabled: bool = False
    data_columns: dict[str, str] = Field(
        default_factory=lambda: {
            key: key for key in ["product", "customer", "month", "quantity", "revenue_cents"]
        }
    )
    revision: int = Field(default=1, ge=1)
    output_standard: OutputStandard = Field(default_factory=OutputStandard)

    @model_validator(mode="after")
    def column_targets(self):
        """Typed measurement fields require explicit target units; never infer a dimension."""
        if any(
            column.enabled and column.dimension and column.dimension not in self.units
            for column in self.output_standard.columns
        ):
            raise ValueError("Each measurement column needs a configured target unit")
        return self

    @field_validator("customers")
    @classmethod
    def validate_customers(cls, value: dict[str, str]) -> dict[str, str]:
        """Validate bounded customer identifiers and labels; IDs remain authorization attributes."""
        import re

        if not 1 <= len(value) <= 40 or any(
            not re.fullmatch(r"[a-z0-9-]{1,32}", key) or not 1 <= len(label) <= 60
            for key, label in value.items()
        ):
            raise ValueError("Provide 1-40 valid customer IDs with bounded labels")
        return value

    @field_validator("data_columns")
    @classmethod
    def validate_columns(cls, value: dict[str, str]) -> dict[str, str]:
        """Allow column aliases without changing the canonical sales schema."""
        if (
            set(value) != {"product", "customer", "month", "quantity", "revenue_cents"}
            or len(set(value.values())) != 5
            or any(not 1 <= len(alias) <= 40 for alias in value.values())
        ):
            raise ValueError("Provide five distinct, bounded sales column aliases")
        return value

    @field_validator("units")
    @classmethod
    def validate_units(cls, value: dict[str, str]) -> dict[str, str]:
        """Reject unknown dimensions and units before any conversion takes place."""
        if any(
            dimension not in UNITS or unit not in UNITS[dimension]
            for dimension, unit in value.items()
        ):
            raise ValueError("Each target unit must belong to its named dimension")
        return value

    @field_validator("sections")
    @classmethod
    def validate_sections(cls, value: list[str]) -> list[str]:
        """Require content and prevent duplicate sections in configured output."""
        if "content" not in value or len(set(value)) != len(value):
            raise ValueError("Include content exactly once; all sections must be unique")
        return value


class Login(BaseModel):
    """User-supplied login fields; roles always come from the database."""

    workspace: str = Field(pattern=r"^[a-z][a-z0-9-]{1,32}$")
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=128)


class StandardPreview(BaseModel):
    """An authorized draft and bounded CSV sample; preview never publishes changes."""

    model_config = ConfigDict(extra="forbid")
    config: WorkspaceConfig
    sample: str = Field(min_length=1, max_length=16000)


class StandardRestore(BaseModel):
    """Restore a saved standard as a new revision, conditional on the current revision."""

    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=1, strict=True)
    expected_revision: int = Field(ge=1, strict=True)


class MergeRequest(BaseModel):
    """Ordered selection of existing, authorized documents for a new compilation."""

    ids: list[str] = Field(min_length=1, max_length=12)
    title: str = Field(min_length=2, max_length=120)


class BundleRequest(BaseModel):
    """A unique ordered selection; export format comes from each document's saved standard."""

    model_config = ConfigDict(extra="forbid")
    ids: list[str] = Field(min_length=1, max_length=12)

    @field_validator("ids")
    @classmethod
    def valid_ids(cls, value):
        """Reject oversized/repeated identifiers before any lookup or file generation."""
        if len(set(value)) != len(value) or any(not 1 <= len(item) <= 80 for item in value):
            raise ValueError("Choose unique document identifiers of 1–80 characters")
        return value


class Question(BaseModel):
    """Bounded question sent only with authorized document context."""

    question: str = Field(min_length=3, max_length=800)


class MeasurementRequest(BaseModel):
    """Exact decimal measurement and explicitly named source and destination units."""

    value: str = Field(max_length=50)
    source: str = Field(max_length=12)
    target: str = Field(max_length=12)


class ProductRequest(BaseModel):
    """Staff-created catalog entry with a customer assignment and exact-cent price."""

    id: str = Field(pattern=r"^[A-Z0-9-]{2,32}$")
    name: str = Field(min_length=2, max_length=100)
    category: str = Field(min_length=2, max_length=60)
    description: str = Field(min_length=2, max_length=1000)
    price_cents: int = Field(ge=0, le=1_000_000_000, strict=True)
    customer: str = Field(max_length=32)
    specifications: str = Field(max_length=5000)
