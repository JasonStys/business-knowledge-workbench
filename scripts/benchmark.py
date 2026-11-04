# @index-begin
# @symbol function/class: main L35
# @symbol variable/parameter: config L37
# @symbol variable/parameter: index L38
# @symbol variable/parameter: rows L38
# @symbol variable/parameter: conversions L39
# @symbol variable/parameter: _ L40
# @symbol variable/parameter: start L41
# @symbol variable/parameter: directory L44
# @symbol variable/parameter: path L45
# @symbol variable/parameter: database L47
# @symbol variable/parameter: exemplar L48
# @symbol variable/parameter: searches L53
# @symbol variable/parameter: library_searches L54
# @symbol function/class: summary L65
# @symbol variable/parameter: values L65
# @symbol variable/parameter: result L72
# @symbol variable/parameter: output L80
# @index-end
"""Measured small-workspace budgets, not hardware-independent performance claims. Index: docs/code-index.md."""

import json
import platform
import statistics
import tempfile
import time
from pathlib import Path

from server.conversion import ingest
from server.library import LibraryQuery, search
from server.models import WorkspaceConfig
from server.store import connect, documents, initialize


def main():
    """Measure median and p95 import/search over a fixed synthetic workload."""
    config = WorkspaceConfig(title="Benchmark", profile="industrial")
    rows = "part,width\n" + "\n".join(f"P-{index},2 in" for index in range(500))
    conversions = []
    for _ in range(15):
        start = time.perf_counter()
        ingest("benchmark.csv", rows.encode(), config)
        conversions.append((time.perf_counter() - start) * 1000)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bench.sqlite"
        initialize(path, True)
        with connect(path) as database:
            exemplar = database.execute("SELECT result FROM documents LIMIT 1").fetchone()[0]
            database.executemany(
                "INSERT INTO documents(id,workspace,title,visibility,result) VALUES (?,'industrial',?,'public',?)",
                [(f"bench-{index}", f"bench-{index}", exemplar) for index in range(180)],
            )
        searches = []
        library_searches = []
        for _ in range(100):
            start = time.perf_counter()
            with connect(path) as database:
                documents(database, None, "industrial", "controller")
            searches.append((time.perf_counter() - start) * 1000)
            start = time.perf_counter()
            with connect(path) as database:
                search(database, None, "industrial", LibraryQuery(q="controller", kind="table"))
            library_searches.append((time.perf_counter() - start) * 1000)

    def summary(values):
        """Return measured percentiles with an intentionally generous CI regression budget."""
        return {
            "median_ms": round(statistics.median(values), 3),
            "p95_ms": round(sorted(values)[int(len(values) * 0.95) - 1], 3),
        }

    result = {
        "workload": {"csv_rows": 500, "search_documents": 189, "search_iterations": 100},
        "runtime": platform.python_version(),
        "import": summary(conversions),
        "search": summary(searches),
        "library_search_with_facets": summary(library_searches),
        "budgets": {"import_p95_ms": 2000, "search_p95_ms": 500},
    }
    output = Path("docs/reports/performance.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    assert (
        result["import"]["p95_ms"] < 2000
        and result["search"]["p95_ms"] < 500
        and result["library_search_with_facets"]["p95_ms"] < 500
    ), result
    print(json.dumps(result))


if __name__ == "__main__":
    main()
