# @index-begin
# @symbol variable/parameter: CELL L25
# @symbol function/class: in_range L30
# @symbol variable/parameter: maximum L30
# @symbol variable/parameter: minimum L30
# @symbol variable/parameter: unit L30
# @symbol variable/parameter: value L30
# @symbol variable/parameter: text L39
# @symbol variable/parameter: match L40
# @symbol variable/parameter: number L42
# @symbol variable/parameter: source L42
# @symbol variable/parameter: measured L46
# @index-end
"""Jason Stys: finite, unit-aware comparisons for persisted table cells.

Declarations/variables and exact source locations: docs/code-index.md. This module
does not evaluate expressions, infer units or turn unparseable data into zero.
"""

import re
from decimal import Decimal, InvalidOperation

from .units import convert

CELL = re.compile(
    r"([+-]?(?:\d{1,16}(?:\.\d{1,12})?|\.\d{1,12})(?:[eE][+-]?\d{1,2})?)(?:\s*([A-Za-z]{1,4}))?"
)


def in_range(value, minimum, maximum, unit):
    """SQLite predicate: one complete numeric cell, inclusive bounds in one explicit unit.

    Unitless queries match only unitless numbers. Invalid/unknown/incompatible cells
    do not match. Decimal conversions use the same six-place precision as canonical
    exports, so this searches stored standardized values rather than source precision.
    """
    if value is None or isinstance(value, bool):
        return 0
    text = str(value).strip()
    if len(text) > 100 or not (match := CELL.fullmatch(text)):
        return 0
    number, source = match.groups()
    if bool(source) != bool(unit):
        return 0
    try:
        measured = Decimal(convert(number, source, unit)) if unit else Decimal(number)
        if not measured.is_finite() or abs(measured) > Decimal("1e15"):
            return 0
        return int(
            (minimum is None or measured >= Decimal(minimum))
            and (maximum is None or measured <= Decimal(maximum))
        )
    except (InvalidOperation, ValueError, TypeError, OverflowError):
        return 0
