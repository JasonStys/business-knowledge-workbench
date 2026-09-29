# @index-begin
# @symbol variable/parameter: UNITS L54
# @symbol function/class: WorkspaceConfig L64
# @symbol variable/parameter: model_config L67
# @symbol variable/parameter: title L68
# @symbol variable/parameter: profile L69
# @symbol variable/parameter: customers L70
# @symbol variable/parameter: units L73
# @symbol variable/parameter: sections L76
# @symbol variable/parameter: forecasting L81
# @symbol variable/parameter: ai_enabled L82
# @symbol variable/parameter: data_columns L83
# @symbol variable/parameter: key L85
# @symbol variable/parameter: revision L88
# @symbol variable/parameter: cls L92
# @symbol function/class: validate_customers L92
# @symbol variable/parameter: label L98
# @symbol function/class: validate_columns L105
# @symbol variable/parameter: alias L110
# @symbol function/class: validate_units L117
# @symbol variable/parameter: dimension L121
# @symbol variable/parameter: unit L121
# @symbol function/class: validate_sections L128
# @symbol function/class: Login L135
# @symbol variable/parameter: workspace L138
# @symbol variable/parameter: username L139
# @symbol variable/parameter: password L140
# @symbol function/class: MergeRequest L143
# @symbol variable/parameter: ids L146
# @symbol function/class: Question L150
# @symbol variable/parameter: question L153
# @symbol function/class: MeasurementRequest L156
# @symbol variable/parameter: value L159
# @symbol variable/parameter: source L160
# @symbol variable/parameter: target L161
# @symbol function/class: ProductRequest L164
# @symbol variable/parameter: id L167
# @symbol variable/parameter: name L168
# @symbol variable/parameter: category L169
# @symbol variable/parameter: description L170
# @symbol variable/parameter: price_cents L171
# @symbol variable/parameter: customer L172
# @symbol variable/parameter: specifications L173
# @index-end
"""Validated configuration and API contracts. Symbols/variables: docs/code-index.md.

Configuration is data, never executable templates, code, paths, or remote credentials.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

UNITS = {
    "length": ["mm", "cm", "m", "in", "ft"],
    "mass": ["g", "kg", "lb"],
    "temperature": ["C", "F", "K"],
    "pressure": ["Pa", "kPa", "bar", "psi"],
    "voltage": ["V", "mV"],
    "energy": ["Wh", "kWh"],
}


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


class MergeRequest(BaseModel):
    """Ordered selection of existing, authorized documents for a new compilation."""

    ids: list[str] = Field(min_length=1, max_length=12)
    title: str = Field(min_length=2, max_length=120)


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
