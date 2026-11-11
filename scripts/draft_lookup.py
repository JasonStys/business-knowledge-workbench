# @index-begin
# @symbol variable/parameter: Reader L45
# @symbol variable/parameter: PER_PAGE L46
# @symbol variable/parameter: MAX_PAGES L47
# @symbol variable/parameter: MAX_ID L48
# @symbol variable/parameter: condition L51
# @symbol variable/parameter: message L51
# @symbol function/class: require L51
# @symbol function/class: namespace L57
# @symbol variable/parameter: repository L57
# @symbol function/class: release_id L67
# @symbol variable/parameter: value L67
# @symbol function/class: identity L73
# @symbol variable/parameter: record L73
# @symbol variable/parameter: identifier L76
# @symbol variable/parameter: tag L77
# @symbol variable/parameter: target L83
# @symbol variable/parameter: read L93
# @symbol function/class: read_by_id L93
# @symbol function/class: find_release L112
# @symbol variable/parameter: missing L113
# @symbol variable/parameter: base L116
# @symbol variable/parameter: matches L123
# @symbol variable/parameter: seen L124
# @symbol variable/parameter: page L125
# @symbol variable/parameter: records L126
# @symbol variable/parameter: current L129
# @symbol variable/parameter: candidate L142
# @symbol function/class: require_draft L151
# @symbol variable/parameter: expected_id L152
# @symbol variable/parameter: source L152
# @symbol variable/parameter: version L152
# @index-end
"""Bounded authenticated draft lookup by Jason Stys.

Functions: namespace, release_id, identity, read_by_id, find_release, require_draft.
Variables: fixed page budget, unique tag and exact numeric identity; lines: docs/code-index.md.
No published-only tag lookup, permissive404 fallback or automatic mutation.
"""

import re
from collections.abc import Callable
from typing import Any

Reader = Callable[[str], Any]
PER_PAGE = 100
MAX_PAGES = 3
MAX_ID = 2**63 - 1


def require(condition: bool, message: str) -> None:
    """Fail closed even under optimized Python; no retry/fallback authorizes a write."""
    if not condition:
        raise ValueError(message)


def namespace(repository: str) -> str:
    """Namespace."""
    require(
        isinstance(repository, str)
        and re.fullmatch("[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is not None,
        "Invalid repository",
    )
    return f"repos/{repository}"


def release_id(value: Any) -> int:
    """Release id."""
    require(type(value) is int and 0 < value <= MAX_ID, "Invalid release ID")
    return value


def identity(record: Any, repository: str) -> tuple[Any, ...]:
    """Validate only documented immutable lookup fields; draft HTML URLs may use an untagged alias."""
    require(isinstance(record, dict), "Malformed release metadata")
    identifier = release_id(record.get("id"))
    tag = record.get("tag_name")
    require(isinstance(tag, str) and 0 < len(tag) <= 256, "Invalid release tag")
    require(
        type(record.get("draft")) is bool and type(record.get("prerelease")) is bool,
        "Invalid release state",
    )
    target = record.get("target_commitish")
    require(isinstance(target, str) and 0 < len(target) <= 256, "Invalid release target")
    require(
        record.get("url")
        == f"https://api.github.com/{namespace(repository)}/releases/{identifier}",
        "Foreign release URL",
    )
    return (identifier, tag, record["draft"], record["prerelease"], target)


def read_by_id(read: Reader, repository: str, identifier: int) -> dict[str, Any]:
    """Construct the same-repo numeric GET ourselves; never follow a returned URL or accept an ID swap."""
    identifier = release_id(identifier)
    record = read(f"{namespace(repository)}/releases/{identifier}")
    require(identity(record, repository)[0] == identifier, "Release ID changed")
    require(
        record.get("upload_url")
        == f"https://uploads.github.com/{namespace(repository)}/releases/{identifier}/assets{{?name,label}}",
        "Foreign upload URL",
    )
    require(
        record.get("assets_url")
        == f"https://api.github.com/{namespace(repository)}/releases/{identifier}/assets",
        "Foreign assets URL",
    )
    require(isinstance(record.get("assets"), list), "Malformed release assets")
    return record


def find_release(
    read: Reader, repository: str, tag: str, *, missing: bool = False
) -> dict[str, Any] | None:
    """List all visible releases within a fixed cap, require a unique exact tag, then reread its ID."""
    base = namespace(repository)
    require(
        isinstance(tag, str)
        and re.fullmatch("v(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)", tag)
        is not None,
        "Invalid requested tag",
    )
    matches = []
    seen = set()
    for page in range(1, MAX_PAGES + 1):
        records = read(f"{base}/releases?per_page={PER_PAGE}&page={page}")
        require(isinstance(records, list) and len(records) <= PER_PAGE, "Malformed release page")
        for record in records:
            current = identity(record, repository)
            require(current[0] not in seen, "Duplicate release ID or unstable pagination")
            seen.add(current[0])
            if current[1] == tag:
                matches.append(record)
        if len(records) < PER_PAGE:
            break
    else:
        raise ValueError("Release history exceeds bounded complete lookup; absence not established")
    require(len(matches) <= 1, "Ambiguous release tag")
    if not matches:
        require(missing, "Release not found in complete authenticated listing")
        return None
    candidate = matches[0]
    record = read_by_id(read, repository, candidate["id"])
    require(
        identity(record, repository) == identity(candidate, repository),
        "Release identity changed between list and ID read",
    )
    return record


def require_draft(
    read: Reader, repository: str, version: str, source: str, *, expected_id: int | None = None
) -> dict[str, Any]:
    """Separate exact clean-source/draft policy from general collision detection during prepare."""
    require(
        isinstance(source, str) and re.fullmatch("[a-f0-9]{40}", source) is not None,
        "Invalid expected source",
    )
    record = find_release(read, repository, f"v{version}")
    require(record is not None, "Draft missing")
    require(
        record["draft"] is True
        and record["prerelease"] is False
        and (record["target_commitish"] == source),
        "Draft target/source/state mismatch",
    )
    if expected_id is not None:
        require(record["id"] == release_id(expected_id), "Prepared release ID changed")
    return record
