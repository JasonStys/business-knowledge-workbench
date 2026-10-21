# @index-begin
# @symbol variable/parameter: config L58
# @symbol function/class: identity L58
# @symbol variable/parameter: settings L60
# @symbol variable/parameter: digest L65
# @symbol variable/parameter: blocks L76
# @symbol function/class: prepare_tables L76
# @symbol variable/parameter: warnings L76
# @symbol variable/parameter: prepared L78
# @symbol variable/parameter: standard L79
# @symbol variable/parameter: aliases L83
# @symbol variable/parameter: column L85
# @symbol variable/parameter: alias L86
# @symbol variable/parameter: block L88
# @symbol variable/parameter: rows L91
# @symbol variable/parameter: headers L92
# @symbol variable/parameter: header L93
# @symbol variable/parameter: mapped L93
# @symbol variable/parameter: recognized L94
# @symbol variable/parameter: missing L104
# @symbol variable/parameter: extras L111
# @symbol variable/parameter: key L111
# @symbol variable/parameter: index L116
# @symbol variable/parameter: positions L116
# @symbol variable/parameter: order L117
# @symbol variable/parameter: row L119
# @symbol variable/parameter: values L120
# @symbol variable/parameter: value L122
# @symbol variable/parameter: match L129
# @symbol variable/parameter: number L131
# @symbol variable/parameter: unit L131
# @symbol function/class: expand_html_tables L152
# @symbol variable/parameter: output L154
# @symbol variable/parameter: node L156
# @symbol function/class: walk L156
# @symbol variable/parameter: cell L169
# @symbol variable/parameter: soup L185
# @symbol variable/parameter: child L186
# @index-end
"""Jason Stys: deterministic data-only table standards and immutable conversion identities.

Functions and variables have exact generated locations in docs/code-index.md.
No user HTML, CSS, expressions, filesystem paths or model calls are executed.
"""

import copy
import hashlib
import json
import re
from html import escape

from bs4 import BeautifulSoup, NavigableString

from .models import WorkspaceConfig
from .units import DIMENSIONS, PATTERN, convert


def identity(config: WorkspaceConfig) -> dict:
    """Bind every output to the full selected unit/structure/presentation contract."""
    settings = {
        "units": config.units,
        "sections": config.sections,
        "output_standard": config.output_standard.model_dump(),
    }
    digest = hashlib.sha256(
        json.dumps(settings, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "name": config.output_standard.name,
        "revision": config.revision,
        "sha256": digest,
        **settings,
    }


def prepare_tables(blocks: list[dict], config: WorkspaceConfig, warnings: list[str]) -> list[dict]:
    """Map headers in O(cells + aliases), retaining unknown data or rejecting it explicitly."""
    prepared = copy.deepcopy(blocks)
    standard = config.output_standard
    if not standard.columns:
        return prepared
    prepared = expand_html_tables(prepared)
    aliases = {
        alias.strip().casefold(): column.key
        for column in standard.columns
        for alias in [column.key, column.label, *column.aliases]
    }
    for block in prepared:
        if block["kind"] != "table" or not block["rows"]:
            continue
        rows = block["rows"]
        headers = rows[0]
        mapped = [aliases.get(header.strip().casefold(), header) for header in headers]
        recognized = set(mapped) & {column.key for column in standard.columns}
        if not recognized and standard.table_scope == "matching":
            warnings.append(
                "A table did not match this standard's fields; preserved unchanged for review."
            )
            continue
        if len(set(mapped)) != len(mapped):
            raise ValueError("Duplicate or ambiguous table headers")
        if any(len(row) != len(headers) for row in rows[1:]):
            raise ValueError("Table row width does not match headers")
        missing = [
            column.key
            for column in standard.columns
            if column.required and column.key not in recognized
        ]
        if missing:
            raise ValueError("Missing required standard columns: " + ", ".join(missing))
        extras = [key for key in mapped if key not in recognized]
        if extras and standard.extra_columns == "reject":
            raise ValueError("Unknown columns rejected by the active standard")
        if extras:
            warnings.append("Additional table columns were retained after the standardized fields.")
        positions = {key: index for index, key in enumerate(mapped)}
        order = [column.key for column in standard.columns] + extras
        output = [order]
        for row in rows[1:]:
            values = {key: row[index] for key, index in positions.items()}
            for column in standard.columns:
                value = values.get(column.key, "").strip()
                if not value:
                    if column.required:
                        raise ValueError("Required standard field is empty: " + column.key)
                    values[column.key] = ""
                    continue
                if column.dimension:
                    match = PATTERN.fullmatch(value)
                    if match:
                        number, unit = match.groups()
                    elif column.source_unit and re.fullmatch(r"-?\d{1,12}(?:\.\d{1,12})?", value):
                        number, unit = value, column.source_unit
                        # Declare the source unit in the canonical cell; generic normalization
                        # below records the original value and conversion rather than guessing.
                        values[column.key] = value + " " + unit
                    else:
                        raise ValueError(
                            "Measurement field needs an explicit supported unit: " + column.key
                        )
                    if DIMENSIONS[unit] != column.dimension:
                        raise ValueError(
                            "Measurement field has incompatible dimensions: " + column.key
                        )
                    convert(number, unit, config.units[column.dimension])
            output.append([values.get(key, "") for key in order])
        block["rows"] = output
        block["column_labels"] = {column.key: column.label for column in standard.columns}
    return prepared


def expand_html_tables(blocks: list[dict]) -> list[dict]:
    """Expose sanitized HTML tables to the same schema pipeline, preserving surrounding content order."""
    output = []

    def walk(node):
        """Split only wrappers containing tables; reject merged/nested cells rather than inventing data."""
        if isinstance(node, NavigableString):
            if str(node).strip():
                output.append({"kind": "html", "text": escape(str(node))})
        elif node.name == "table":
            if (
                node.find("table")
                or node.find(attrs={"rowspan": True})
                or node.find(attrs={"colspan": True})
            ):
                raise ValueError("Nested or merged HTML table cells require source review")
            rows = [
                [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                for row in node.find_all("tr")
            ]
            if len(rows) > 2000 or any(len(row) > 40 for row in rows):
                raise ValueError("HTML table exceeds schema limits")
            output.append({"kind": "table", "rows": rows})
        elif node.find("table"):
            for child in node.children:
                walk(child)
        else:
            output.append({"kind": "html", "text": str(node)})

    for block in blocks:
        if block["kind"] != "html":
            output.append(block)
        else:
            soup = BeautifulSoup(block["text"], "html.parser")
            for child in soup.children:
                walk(child)
    return output
