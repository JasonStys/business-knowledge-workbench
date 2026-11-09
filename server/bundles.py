# @index-begin
# @symbol variable/parameter: MAX_BUNDLE_BYTES L35
# @symbol function/class: create_bundle L38
# @symbol variable/parameter: rows L38
# @symbol variable/parameter: output L47
# @symbol variable/parameter: manifest L48
# @symbol variable/parameter: size L53
# @symbol variable/parameter: archive L54
# @symbol variable/parameter: index L55
# @symbol variable/parameter: row L55
# @symbol variable/parameter: result L56
# @symbol variable/parameter: standard L57
# @symbol variable/parameter: format_name L58
# @symbol variable/parameter: payload L61
# @symbol variable/parameter: slug L65
# @symbol variable/parameter: name L69
# @symbol variable/parameter: encoded L83
# @index-end
"""Jason Stys: bounded, flat ZIP exports of already-authorized standardized files.

Declarations/variables and exact lines: docs/code-index.md. Original attachments
and account material are never included. Manifest hashes describe this download,
not a digital signature, access grant or permanent reproducible-build guarantee.
"""

import hashlib
import io
import json
import re
import zipfile
from pathlib import PurePath

from .exports import FORMATS, export_document

MAX_BUNDLE_BYTES = 32 * 1024 * 1024


def create_bundle(rows):
    """Export <=12 immutable document snapshots using each saved standard, then hash entries.

    All permission checks must precede this function. Names are flat, bounded,
    indexed and Windows-safe; a malicious source title cannot create ZIP paths.
    Processing is O(total exported content), with a 32 MiB uncompressed budget.
    """
    if not 1 <= len(rows) <= 12:
        raise ValueError("Select one to twelve documents")
    output = io.BytesIO()
    manifest = {
        "schema": "kbw-standardized-bundle/v1",
        "originals_included": False,
        "documents": [],
    }
    size = 0
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for index, row in enumerate(rows, start=1):
            result = json.loads(row["result"])
            standard = result.get("standard", {})
            format_name = standard.get("output_standard", {}).get("default_export", "html")
            if format_name not in FORMATS:
                raise ValueError("A saved document has an unsupported export format")
            payload = export_document(result, format_name)
            size += len(payload)
            if size > MAX_BUNDLE_BYTES:
                raise OverflowError("Selected exports exceed 32 MiB; select fewer documents")
            slug = (
                re.sub(r"[^A-Za-z0-9_-]+", "-", PurePath(row["title"]).stem).strip("-")[:48]
                or "document"
            )
            name = f"{index:02d}-{slug}.{format_name}"
            archive.writestr(name, payload)
            manifest["documents"].append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "file": name,
                    "format": format_name,
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "standard_revision": standard.get("revision"),
                    "standard_sha256": standard.get("sha256"),
                }
            )
        encoded = json.dumps(manifest, ensure_ascii=False, indent=2).encode()
        if size + len(encoded) > MAX_BUNDLE_BYTES:
            raise OverflowError("Bundle manifest exceeds the output budget; select fewer documents")
        archive.writestr("manifest.json", encoded)
    return output.getvalue()
