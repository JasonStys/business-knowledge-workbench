# @index-begin
# @symbol variable/parameter: ROOT L52
# @symbol variable/parameter: SUFFIXES L53
# @symbol variable/parameter: BEGIN L54
# @symbol variable/parameter: END L55
# @symbol variable/parameter: path L58
# @symbol function/class: symbols L58
# @symbol variable/parameter: text L58
# @symbol variable/parameter: records L60
# @symbol variable/parameter: node L62
# @symbol variable/parameter: output L72
# @symbol variable/parameter: line L82
# @symbol variable/parameter: number L82
# @symbol variable/parameter: match L86
# @symbol variable/parameter: identifier L93
# @symbol variable/parameter: record L96
# @symbol variable/parameter: unique L96
# @symbol function/class: header L100
# @symbol variable/parameter: entries L102
# @symbol variable/parameter: marker L106
# @symbol variable/parameter: finish L108
# @symbol variable/parameter: start L108
# @symbol variable/parameter: entry L110
# @symbol function/class: strip_header L115
# @symbol variable/parameter: lines L117
# @symbol variable/parameter: offset L118
# @symbol variable/parameter: end L120
# @symbol function/class: main L125
# @symbol variable/parameter: check L127
# @symbol variable/parameter: files L128
# @symbol variable/parameter: folder L130
# @symbol variable/parameter: catalog L135
# @symbol variable/parameter: stale L141
# @symbol variable/parameter: original L143
# @symbol variable/parameter: raw L144
# @symbol variable/parameter: content L145
# @symbol variable/parameter: _ L146
# @symbol variable/parameter: inventory L147
# @symbol variable/parameter: relative L158
# @symbol variable/parameter: expected L180
# @symbol variable/parameter: index L181
# @index-end
"""Synchronize exact line maps in code headers and the complete file/symbol catalog. Index: docs/code-index.md."""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUFFIXES = {".py", ".ts", ".js", ".mjs", ".css", ".html", ".sql", ".sh"}
BEGIN = "@index-begin"
END = "@index-end"


def symbols(path: Path, text: str) -> list[dict]:
    """Extract declarations with language parsers; use structural labels for markup/styles/SQL."""
    records = []
    if path.suffix == ".py":
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                records.append({"kind": "function/class", "name": node.name, "line": node.lineno})
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                records.append({"kind": "variable/parameter", "name": node.id, "line": node.lineno})
            elif isinstance(node, ast.arg):
                records.append(
                    {"kind": "variable/parameter", "name": node.arg, "line": node.lineno}
                )
    elif path.suffix in {".ts", ".js", ".mjs"}:
        output = subprocess.run(
            ["node", str(ROOT / "scripts/symbols.mjs"), str(path)],
            capture_output=True,
            input=text,
            text=True,
            encoding="utf-8",
            check=True,
        )
        records = json.loads(output.stdout)
    else:
        for number, line in enumerate(text.splitlines(), 1):
            if BEGIN in line or END in line or "@symbol" in line:
                continue
            if path.suffix == ".sql":
                match = re.search(r"CREATE (?:TABLE|INDEX)(?: IF NOT EXISTS)? (\w+)", line)
                if match:
                    records.append({"kind": "schema", "name": match[1], "line": number})
            elif path.suffix == ".css":
                if re.match(r"^[.#:@\w].*\{$", line):
                    records.append({"kind": "selector", "name": line.rstrip(" {"), "line": number})
            elif path.suffix == ".html":
                for identifier in re.findall(r'id="([\w-]+)"', line):
                    records.append({"kind": "element", "name": identifier, "line": number})
    # Retain first declaration per name/kind; the detailed source is still the authority.
    unique = {(record["kind"], record["name"]): record for record in reversed(records)}
    return sorted(unique.values(), key=lambda record: (record["line"], record["name"]))


def header(path: Path, records: list[dict]) -> str:
    """Generate compact comment inventories with names, kinds and exact one-based locations."""
    entries = [
        f"@symbol {record['kind']}: {record['name']} L{record['line']}" for record in records
    ]
    if path.suffix in {".py", ".sh", ".sql"}:
        marker = "-- " if path.suffix == ".sql" else "# "
        return "\n".join(marker + line for line in [BEGIN, *entries, END]) + "\n"
    start, finish = ("<!--", "-->") if path.suffix == ".html" else ("/*", "*/")
    return (
        "\n".join([start + " " + BEGIN, *[" * " + entry for entry in entries], END + " " + finish])
        + "\n"
    )


def strip_header(text: str) -> str:
    """Remove only this generator's known top-of-file comment block, preserving authored code."""
    lines = text.splitlines(keepends=True)
    offset = 1 if lines and lines[0].startswith("#!") else 0
    if len(lines) > offset and BEGIN in lines[offset]:
        end = next(index for index in range(offset, len(lines)) if END in lines[index])
        return "".join(lines[:offset] + lines[end + 1 :])
    return text


def main():
    """Update inventories to a fixed point, or fail CI when documentation differs from code."""
    check = "--check" in sys.argv
    files = sorted(
        path
        for folder in ["server", "web", "scripts", "tests", "public", "examples"]
        for path in (ROOT / folder).rglob("*")
        if path.suffix in SUFFIXES and "__pycache__" not in path.parts
    )
    files += sorted(ROOT.glob("*.ts")) + [ROOT / "index.html"]
    catalog = [
        "# File and code index",
        "",
        "Generated from AST/compiler declarations. Each code header repeats exact function/class/type and variable/parameter locations. Local variables are indexed at their first binding; callbacks share their enclosing function's description. Run `python scripts/code_index.py` after code changes.",
        "",
    ]
    stale = []
    for path in files:
        original = path.read_text(encoding="utf-8")
        raw = strip_header(original)
        content = raw
        for _ in range(3):
            inventory = header(path, symbols(path, content))
            content = (
                inventory + raw
                if not raw.startswith("#!")
                else raw.split("\n", 1)[0] + "\n" + inventory + raw.split("\n", 1)[1]
            )
        if content != original:
            if check:
                stale.append(str(path.relative_to(ROOT)))
            else:
                path.write_text(content, encoding="utf-8", newline="\n")
        relative = path.relative_to(ROOT).as_posix()
        catalog.extend(
            [
                f"## `{relative}`",
                "",
                f"[Source](../{relative}) — descriptive module header and function contracts are in this file.",
                "",
                "| Kind | Name | Line |",
                "| --- | --- | ---: |",
            ]
        )
        catalog.extend(
            f"| {record['kind']} | `{record['name'].replace('|', '/')}` | {record['line']} |"
            for record in symbols(path, content)
        )
        catalog.append("")
    catalog += [
        "## Other files",
        "",
        "Binary examples and PWA PNG icons: generated, synthetic test inputs. JSON files: package/runtime/schema data. `docs/`: architecture, contracts, limits, operations and validation evidence. `.github/workflows/`: automated release gates. `Dockerfile`, `compose.yaml`, and `.dockerignore`: portable container packaging. `requirements.lock`: pinned portable Python dependencies. `LICENSE`, `SECURITY.md`, and `CONTRIBUTING.md`: project policies.",
        "",
    ]
    expected = "\n".join(catalog)
    index = ROOT / "docs/code-index.md"
    if check:
        if not index.exists() or index.read_text(encoding="utf-8") != expected:
            stale.append("docs/code-index.md")
        if stale:
            raise SystemExit("Stale code index: " + ", ".join(stale))
    else:
        index.parent.mkdir(exist_ok=True)
        index.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Verified {len(files)} code-file inventories")


if __name__ == "__main__":
    main()
