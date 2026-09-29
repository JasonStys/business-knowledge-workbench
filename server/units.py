# @index-begin
# @symbol variable/parameter: FACTORS L31
# @symbol variable/parameter: DIMENSIONS L49
# @symbol variable/parameter: dimension L49
# @symbol variable/parameter: unit L49
# @symbol variable/parameter: values L49
# @symbol variable/parameter: PATTERN L50
# @symbol function/class: convert L55
# @symbol variable/parameter: source L55
# @symbol variable/parameter: target L55
# @symbol variable/parameter: value L55
# @symbol variable/parameter: number L60
# @symbol variable/parameter: context L65
# @symbol variable/parameter: kelvin L68
# @symbol function/class: normalize L89
# @symbol variable/parameter: targets L89
# @symbol variable/parameter: text L89
# @symbol variable/parameter: records L91
# @symbol variable/parameter: match L93
# @symbol function/class: replacement L93
# @symbol variable/parameter: result L100
# @index-end
"""Decimal, dimension-aware measurements with provenance. Symbols: docs/code-index.md."""

import re
from decimal import Decimal, InvalidOperation, localcontext

from .models import UNITS

# Each coefficient converts to the dimension's base unit; temperatures use offsets.
FACTORS = {
    "mm": "0.001",
    "cm": "0.01",
    "m": "1",
    "in": "0.0254",
    "ft": "0.3048",
    "g": "0.001",
    "kg": "1",
    "lb": "0.45359237",
    "Pa": "1",
    "kPa": "1000",
    "bar": "100000",
    "psi": "6894.757293168",
    "V": "1",
    "mV": "0.001",
    "Wh": "1",
    "kWh": "1000",
}
DIMENSIONS = {unit: dimension for dimension, values in UNITS.items() for unit in values}
PATTERN = re.compile(
    r"(?<![\w.])(-?\d{1,12}(?:\.\d{1,12})?)\s*(kWh|kPa|mV|mm|cm|kg|lb|ft|in|Wh|bar|psi|Pa|m|g|V|C|F|K)\b"
)


def convert(value: str, source: str, target: str) -> str:
    """Convert a finite decimal without crossing dimensions or silently rounding money."""
    if source not in DIMENSIONS or DIMENSIONS.get(source) != DIMENSIONS.get(target):
        raise ValueError("Unknown unit or incompatible dimensions")
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("Invalid decimal") from error
    if not number.is_finite() or abs(number) > Decimal("1e15") or number.as_tuple().exponent < -20:
        raise ValueError("Measurement must be finite and within supported precision/range")
    with localcontext() as context:
        context.prec = 32
        if DIMENSIONS[source] == "temperature":
            kelvin = (
                number
                if source == "K"
                else number + Decimal("273.15")
                if source == "C"
                else (number - 32) * 5 / 9 + Decimal("273.15")
            )
            if kelvin < 0:
                raise ValueError("Temperature below absolute zero")
            result = (
                kelvin
                if target == "K"
                else kelvin - Decimal("273.15")
                if target == "C"
                else (kelvin - Decimal("273.15")) * 9 / 5 + 32
            )
        else:
            result = number * Decimal(FACTORS[source]) / Decimal(FACTORS[target])
        return format(result.quantize(Decimal("0.000001")), "f").rstrip("0").rstrip(".") or "0"


def normalize(text: str, targets: dict[str, str]) -> tuple[str, list[dict]]:
    """Normalize recognized, explicit measurements; preserve their exact source spelling."""
    records: list[dict] = []

    def replacement(match: re.Match) -> str:
        """Convert one unambiguous unit match and retain its source character offsets."""
        value, source = match.groups()
        # "in" is also an English preposition. Without a clause boundary, leave it for review.
        if source == "in" and re.match(r"\s+[A-Za-z]", text[match.end() :]):
            return match.group()
        target = targets.get(DIMENSIONS[source], source)
        result = convert(value, source, target)
        records.append(
            {
                "original": match.group(),
                "value": result,
                "unit": target,
                "dimension": DIMENSIONS[source],
                "source_start": match.start(),
                "source_end": match.end(),
            }
        )
        return f"{result} {target}"

    return PATTERN.sub(replacement, text), records
