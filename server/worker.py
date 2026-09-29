# @index-begin
# @symbol function/class: main L15
# @symbol variable/parameter: data L18
# @symbol variable/parameter: result L19
# @index-end
"""Short-lived conversion process with no application credentials. Index: docs/code-index.md."""

import json
import sys

from .conversion import MAX_BYTES, ingest
from .models import WorkspaceConfig


def main() -> None:
    """Read a bounded payload from stdin and return a single structured conversion result."""
    try:
        data = sys.stdin.buffer.read(MAX_BYTES + 1)
        result = ingest(sys.argv[1], data, WorkspaceConfig.model_validate_json(sys.argv[2]))
        print(json.dumps({"result": result}))
    except Exception:
        # A malformed source must not leak internal parser paths, secrets, or exception data.
        print(
            json.dumps(
                {
                    "error": "Conversion rejected: corrupt, unsafe, unsupported, or over-budget source"
                }
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
