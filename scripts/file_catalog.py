# @index-begin
# @symbol variable/parameter: ROOT L22
# @symbol variable/parameter: DESCRIPTIONS L23
# @symbol function/class: description L45
# @symbol variable/parameter: path L45
# @symbol variable/parameter: text L56
# @symbol variable/parameter: tail L57
# @symbol variable/parameter: line L58
# @symbol variable/parameter: title L68
# @symbol function/class: main L81
# @symbol variable/parameter: output L83
# @symbol variable/parameter: paths L86
# @symbol variable/parameter: content L87
# @symbol variable/parameter: target L94
# @index-end
"""Generate a one-row-per-tracked-file catalog with useful responsibility summaries. Index: docs/code-index.md."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESCRIPTIONS = {
    ".gitattributes": "LF text checkout and binary Office/PDF/raster preservation across operating systems.",
    ".gitignore": "Exclude runtime business data, secrets, environments and machine-specific artifacts.",
    ".dockerignore": "Limit the container build context to runtime/build inputs.",
    "Dockerfile": "Multi-stage frontend build and non-root single-origin Python service.",
    "compose.yaml": "Loopback-only synthetic demo with durable volume and resource/isolation limits.",
    "README.md": "Repository overview, capabilities, quick start, validation commands and module summary.",
    "SECURITY.md": "Trust boundaries, vulnerability reporting and production limitations.",
    "CONTRIBUTING.md": "Coding, test, documentation and source-safety expectations.",
    "LICENSE": "MIT terms for this repository; dependencies retain their own licenses.",
    "package.json": "Frontend tooling versions and build/test/format/documentation commands.",
    "package-lock.json": "Exact JavaScript dependency resolution, including platform-optional native build bindings.",
    "pyproject.toml": "Python project metadata, dependencies, lint rules and coverage gates.",
    "requirements.lock": "Pinned Python application/test/audit dependencies for portable installs.",
    "tsconfig.json": "Strict browser/test TypeScript contracts and module resolution.",
    "vite.config.ts": "Frontend bundling and same-origin API development proxy.",
    "playwright.config.ts": "Four browser targets, isolated database/server and retained test evidence.",
    "index.html": "Semantic browser entry, metadata, manifest reference and skip link.",
    "docs/file-catalog.md": "This generated responsibility catalog.",
}


def description(path: str) -> str:
    """Read authored module descriptions or provide format-specific asset/policy summaries."""
    if path in DESCRIPTIONS:
        return DESCRIPTIONS[path]
    if path.startswith(".github/"):
        return (
            "Automated test/build/container/dependency gates."
            if path.endswith("ci.yml")
            else "Pinned Python and JavaScript/TypeScript CodeQL security analysis."
        )
    if path.endswith((".py", ".ts", ".mjs", ".js", ".css", ".sql", ".sh", ".html")):
        text = (ROOT / path).read_text(encoding="utf-8")
        tail = text.split("@index-end", 1)[-1].lstrip(" */->\n")
        line = tail.splitlines()[0].strip('"/*# -') if tail.splitlines() else "Code entry point"
        return (
            line.split("Index:")[0].split("Symbols:")[0].split("Symbols/variables:")[0].strip()
            or "Documented code module."
        )
    if path.startswith("docs/screenshots/"):
        return "Visually inspected synthetic responsive UI evidence."
    if path.startswith("docs/reports/"):
        return "Recorded local validation/performance or rendered synthetic PDF evidence; see validation.md for scope."
    if path.startswith("docs/"):
        title = (ROOT / path).read_text(encoding="utf-8").splitlines()[0].lstrip("# ")
        return title + "."
    if path.startswith("examples/"):
        return (
            "Realistic synthetic source fixture for "
            + Path(path).suffix.lstrip(".").upper()
            + " extraction and workflow tests."
        )
    if path.startswith("public/"):
        return "Installable PWA metadata/icon asset; no private data is bundled."
    return "Repository configuration/support asset."


def main():
    """Generate or compare a catalog of precisely tracked files, excluding local/private artifacts."""
    output = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout
    paths = sorted(set(output.splitlines()) | {"scripts/file_catalog.py", "docs/file-catalog.md"})
    content = "# Complete file catalog\n\nGenerated from tracked repository paths. Code declarations/parameters and exact lines are in [code-index.md](code-index.md). Runtime databases, credentials, dependencies and temporary test traces are not published.\n\n| File | Responsibility |\n| --- | --- |\n"
    content += (
        "\n".join(
            f"| [{path}](../{path}) | {description(path).replace('|', '/')} |" for path in paths
        )
        + "\n"
    )
    target = ROOT / "docs/file-catalog.md"
    if "--check" in sys.argv:
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            raise SystemExit("Stale file catalog; regenerate scripts/file_catalog.py")
    else:
        target.write_text(content, encoding="utf-8", newline="\n")
    print(f"Cataloged {len(paths)} repository files")


if __name__ == "__main__":
    main()
