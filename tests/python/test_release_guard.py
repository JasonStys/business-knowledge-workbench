# @index-begin
# @symbol variable/parameter: SOURCE L135
# @symbol variable/parameter: IDENTIFIER L136
# @symbol function/class: analysis L139
# @symbol variable/parameter: category L139
# @symbol variable/parameter: changes L154
# @symbol function/class: release L154
# @symbol variable/parameter: row L156
# @symbol variable/parameter: name L172
# @symbol function/class: workflow L172
# @symbol function/class: GitHub L185
# @symbol function/class: __init__ L188
# @symbol variable/parameter: self L188
# @symbol variable/parameter: body L199
# @symbol variable/parameter: endpoint L199
# @symbol function/class: read L199
# @symbol function/class: github L237
# @symbol variable/parameter: monkeypatch L237
# @symbol variable/parameter: fake L238
# @symbol variable/parameter: github L243
# @symbol function/class: test_actual_successful_source_requires_full_main_analyses L243
# @symbol variable/parameter: item L246
# @symbol variable/parameter: field L263
# @symbol function/class: test_workflow_failure_cannot_authorize_a_draft L263
# @symbol variable/parameter: value L263
# @symbol function/class: test_incomplete_wrong_ref_or_zero_rule_analysis_fails L286
# @symbol variable/parameter: defect L295
# @symbol function/class: test_source_scope_ambiguity_and_open_alert_fail_closed L295
# @symbol function/class: test_prepare_checks_every_read_prerequisite_before_the_only_fresh_write L310
# @symbol variable/parameter: tmp_path L311
# @symbol variable/parameter: write_index L321
# @symbol variable/parameter: collision L328
# @symbol function/class: test_prepare_never_reuses_or_changes_any_existing_version L328
# @symbol function/class: test_prepared_numeric_id_cannot_be_swapped_published_or_retargeted L351
# @symbol function/class: asset L357
# @symbol variable/parameter: identifier L357
# @symbol variable/parameter: raw L357
# @symbol variable/parameter: capsys L368
# @symbol function/class: test_complete_verify_cli_only_reads_and_leaves_twelve_assets_draft L368
# @symbol variable/parameter: index L371
# @symbol variable/parameter: system L372
# @symbol variable/parameter: result L380
# @symbol function/class: test_bad_or_partial_uploaded_sets_cannot_complete L388
# @symbol variable/parameter: rows L389
# @symbol function/class: build_outputs L412
# @symbol variable/parameter: folder L414
# @symbol function/class: test_upload_streams_exact_files_to_prepared_id_without_clobber L425
# @symbol variable/parameter: sent L428
# @symbol variable/parameter: size L430
# @symbol variable/parameter: stream L430
# @symbol function/class: transmit L430
# @symbol variable/parameter: n L437
# @symbol function/class: test_checksum_failure_prevents_all_uploads L453
# @symbol variable/parameter: _ L457
# @symbol function/class: test_strict_metadata_and_complete_lookup_bounds L462
# @symbol variable/parameter: text L471
# @symbol function/class: workflow_contract L471
# @symbol variable/parameter: expected L478
# @symbol variable/parameter: job L478
# @symbol variable/parameter: section L483
# @symbol variable/parameter: maps L484
# @symbol variable/parameter: actual L486
# @symbol variable/parameter: line L487
# @symbol variable/parameter: match L491
# @symbol function/class: test_actual_workflow_retains_source_and_draft_privilege_contract L498
# @symbol variable/parameter: new L518
# @symbol variable/parameter: old L518
# @symbol function/class: test_actual_workflow_mutations_cannot_erase_guards L518
# @symbol variable/parameter: permission L535
# @symbol function/class: test_final_get_only_draft_verifier_still_requires_reviewed_push_visibility L535
# @symbol variable/parameter: before L539
# @symbol variable/parameter: marker L539
# @symbol variable/parameter: verifier L539
# @symbol variable/parameter: changed L541
# @symbol function/class: Response L546
# @symbol variable/parameter: accepted L566
# @symbol variable/parameter: missing L566
# @symbol variable/parameter: status L566
# @symbol function/class: test_only_actual_http404_means_absence L566
# @symbol variable/parameter: calls L567
# @symbol function/class: Connection L569
# @symbol variable/parameter: host L570
# @symbol variable/parameter: timeout L570
# @symbol variable/parameter: headers L573
# @symbol variable/parameter: method L573
# @symbol function/class: request L573
# @symbol function/class: getresponse L577
# @symbol function/class: close L580
# @symbol function/class: test_upload_transport_uses_fixed_host_id_and_real_stream_digest L593
# @symbol variable/parameter: digest L595
# @symbol variable/parameter: chunks L596
# @symbol variable/parameter: requests L596
# @symbol function/class: putrequest L602
# @symbol variable/parameter: key L605
# @symbol function/class: putheader L605
# @symbol function/class: endheaders L608
# @symbol variable/parameter: data L611
# @symbol function/class: send L611
# @symbol function/class: context_fixture L627
# @symbol variable/parameter: replies L640
# @symbol variable/parameter: arguments L642
# @symbol function/class: git L642
# @symbol variable/parameter: options L642
# @symbol function/class: test_clean_context_binds_actual_git_and_product_versions L656
# @symbol function/class: test_delivery_context_refuses_untrusted_or_unversioned_sources L664
# @symbol function/class: test_bounded_hash_checks_actual_shrink_and_growth L684
# @symbol function/class: test_output_descriptor_rejects_empty_oversize_and_hardlinks L692
# @symbol variable/parameter: path L693
# @symbol variable/parameter: alias L702
# @symbol function/class: test_changed_output_after_all_sidecar_preflight_cannot_upload L708
# @symbol variable/parameter: original L711
# @symbol function/class: changing L714
# @symbol variable/parameter: source L714
# @index-end
"""Jason Stys: independent source, draft, upload and actual-workflow negative release controls.

Tests use inert real-shape GitHub replies and small files. No network, releases,
accounts or OS installers are accessed. Exact declarations: docs/code-index.md.
"""

import copy
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import release_guard as guard

SOURCE = "a" * 40
IDENTIFIER = 439911956


def analysis(category):
    """A processed non-diff main analysis must identify actual rules, tool, ref and source."""
    return {
        "id": 100 + len(category),
        "commit_sha": SOURCE,
        "ref": "refs/heads/main",
        "category": category,
        "analysis_key": ".github/workflows/codeql.yml:analyze",
        "tool": {"name": "CodeQL"},
        "error": "",
        "warning": "",
        "rules_count": 43,
    }


def release(**changes):
    """Untyped draft aliases are legitimate; immutable numeric source/tag identity is still bound."""
    row = {
        "id": IDENTIFIER,
        "tag_name": "v" + guard.VERSION,
        "target_commitish": SOURCE,
        "draft": True,
        "prerelease": False,
        "assets": [],
        "url": f"https://api.github.com/{guard.BASE}/releases/{IDENTIFIER}",
        "assets_url": f"https://api.github.com/{guard.BASE}/releases/{IDENTIFIER}/assets",
        "upload_url": f"https://uploads.github.com/{guard.BASE}/releases/{IDENTIFIER}/assets{{?name,label}}",
        "html_url": f"https://github.com/{guard.REPOSITORY}/releases/tag/untagged-test",
    }
    row.update(changes)
    return row


def workflow(name):
    """Current-main push success, not a PR or an unrelated successful run."""
    return {
        "head_sha": SOURCE,
        "head_branch": "main",
        "event": "push",
        "status": "completed",
        "conclusion": "success",
        "path": f".github/workflows/{name}",
        "repository": {"full_name": guard.REPOSITORY},
    }


class GitHub:
    """Reject unknown API routes and record every write, rather than blanket-success stubbing."""

    def __init__(self):
        self.runs = {name: [workflow(name)] for name in guard.WORKFLOWS}
        self.analyses = [analysis(category) for category in sorted(guard.CATEGORIES)]
        self.alerts = []
        self.main = SOURCE
        self.tag = None
        self.drafts = []
        self.record = release()
        self.writes = []
        self.calls = []

    def read(self, endpoint, *, body=None, missing=False):
        self.calls.append(endpoint)
        if body is not None:
            assert endpoint == guard.BASE + "/releases"
            assert body["draft"] is True and body["target_commitish"] == SOURCE
            self.writes.append(copy.deepcopy(body))
            self.drafts = [copy.deepcopy(self.record)]
            return copy.deepcopy(self.record)
        if endpoint == guard.BASE + "/git/ref/heads/main":
            return {"object": {"sha": self.main}}
        if endpoint == guard.BASE + "/git/ref/tags/v" + guard.VERSION:
            assert missing
            return self.tag
        if endpoint == guard.BASE + "/releases?per_page=100&page=1":
            return copy.deepcopy(self.drafts)
        if endpoint == f"{guard.BASE}/releases/{IDENTIFIER}":
            return copy.deepcopy(self.record)
        for name, rows in self.runs.items():
            if (
                endpoint
                == f"{guard.BASE}/actions/workflows/{name}/runs?head_sha={SOURCE}&per_page=100"
            ):
                return {"workflow_runs": copy.deepcopy(rows), "total_count": len(rows)}
        if (
            endpoint
            == guard.BASE + "/code-scanning/analyses?ref=refs%2Fheads%2Fmain&per_page=100&page=1"
        ):
            return copy.deepcopy(self.analyses)
        if (
            endpoint
            == guard.BASE
            + "/code-scanning/alerts?ref=refs%2Fheads%2Fmain&state=open&per_page=100&page=1"
        ):
            return copy.deepcopy(self.alerts)
        raise AssertionError("Unexpected release API route: " + endpoint)


@pytest.fixture
def github(monkeypatch):
    fake = GitHub()
    monkeypatch.setattr(guard, "api", fake.read)
    return fake


def test_actual_successful_source_requires_full_main_analyses(github):
    guard.require_source(SOURCE)
    assert not github.writes
    assert any("state=open" in item for item in github.calls)


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "queued"),
        ("status", "in_progress"),
        ("conclusion", "failure"),
        ("conclusion", "cancelled"),
        ("head_sha", "b" * 40),
        ("path", ".github/workflows/other.yml"),
        ("event", "pull_request"),
        ("head_branch", "feature/source"),
        ("repository", {"full_name": "someone/else"}),
    ],
)
def test_workflow_failure_cannot_authorize_a_draft(github, field, value):
    github.runs["ci.yml"][0][field] = value
    with pytest.raises(ValueError):
        guard.require_source(SOURCE)
    assert not github.writes


@pytest.mark.parametrize(
    "field,value",
    [
        ("ref", "refs/pull/1/merge"),
        ("commit_sha", "b" * 40),
        ("category", "/language:python"),
        ("analysis_key", "other"),
        ("tool", {"name": "Other"}),
        ("error", "extraction failed"),
        ("warning", "partial"),
        ("rules_count", 0),
        ("rules_count", True),
        ("rules_count", None),
        ("id", True),
    ],
)
def test_incomplete_wrong_ref_or_zero_rule_analysis_fails(github, field, value):
    github.analyses[0][field] = value
    with pytest.raises(ValueError):
        guard.require_source(SOURCE)


@pytest.mark.parametrize(
    "defect", ["main", "missing-lane", "double-push", "missing-category", "open-alert"]
)
def test_source_scope_ambiguity_and_open_alert_fail_closed(github, defect):
    if defect == "main":
        github.main = "b" * 40
    elif defect == "missing-lane":
        github.runs["packages.yml"] = []
    elif defect == "double-push":
        github.runs["ci.yml"] *= 2
    elif defect == "missing-category":
        github.analyses.pop()
    else:
        github.alerts = [{"number": 1, "state": "open"}]
    with pytest.raises(ValueError):
        guard.require_source(SOURCE)


def test_prepare_checks_every_read_prerequisite_before_the_only_fresh_write(
    github, monkeypatch, tmp_path
):
    monkeypatch.setattr(guard, "ROOT", tmp_path)
    monkeypatch.setattr(guard, "context", lambda: SOURCE)
    (tmp_path / "docs/releases").mkdir(parents=True)
    (tmp_path / f"docs/releases/v{guard.VERSION}.md").write_text("New1.4.1 notes", "utf-8")
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "outputs"))
    monkeypatch.setattr(sys, "argv", ["release_guard.py", "prepare"])
    guard.main()
    assert len(github.writes) == 1
    write_index = github.calls.index(guard.BASE + "/releases")
    assert all(any(name in item for item in github.calls[:write_index]) for name in guard.WORKFLOWS)
    assert any("state=open" in item for item in github.calls[:write_index])
    assert (tmp_path / "outputs").read_text() == f"sha={SOURCE}\nrelease_id={IDENTIFIER}\n"


@pytest.mark.parametrize("collision", ["public", "draft", "tag"])
def test_prepare_never_reuses_or_changes_any_existing_version(github, monkeypatch, collision):
    monkeypatch.setattr(guard, "context", lambda: SOURCE)
    monkeypatch.setattr(sys, "argv", ["release_guard.py", "prepare"])
    if collision == "tag":
        github.tag = {"object": {"sha": "b" * 40}}
    else:
        github.drafts = [release(draft=collision == "draft")]
        github.record = copy.deepcopy(github.drafts[0])
    with pytest.raises(ValueError):
        guard.main()
    assert not github.writes


@pytest.mark.parametrize(
    "changes",
    [
        {"draft": False},
        {"prerelease": True},
        {"tag_name": "v1.4.0"},
        {"target_commitish": "b" * 40},
        {"id": IDENTIFIER + 1},
    ],
)
def test_prepared_numeric_id_cannot_be_swapped_published_or_retargeted(github, changes):
    github.record.update(changes)
    with pytest.raises(ValueError):
        guard.draft(IDENTIFIER, SOURCE)


def asset(name, identifier=1, raw=b"example"):
    """Provider metadata includes an independent payload digest, not merely a filename."""
    return {
        "name": name.replace(" ", "."),
        "id": identifier,
        "state": "uploaded",
        "size": len(raw),
        "digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
    }


def test_complete_verify_cli_only_reads_and_leaves_twelve_assets_draft(github, monkeypatch, capsys):
    github.record["assets"] = [
        asset(name, index)
        for index, name in enumerate(
            [name for system in ("Windows", "Linux", "macOS") for name in guard.names(system)],
            start=1,
        )
    ]
    monkeypatch.setattr(guard, "context", lambda: SOURCE)
    monkeypatch.setenv("EXPECTED_RELEASE_ID", str(IDENTIFIER))
    monkeypatch.setattr(sys, "argv", ["release_guard.py", "verify"])
    guard.main()
    result = json.loads(capsys.readouterr().out)
    assert result["draft"] is True and result["assets"] == 12
    assert github.record["draft"] and not github.writes


@pytest.mark.parametrize(
    "defect", ["missing", "foreign", "duplicate", "digest", "starter", "bool-size"]
)
def test_bad_or_partial_uploaded_sets_cannot_complete(github, defect):
    rows = [
        asset(name, index)
        for index, name in enumerate(
            [name for system in ("Windows", "Linux", "macOS") for name in guard.names(system)],
            start=1,
        )
    ]
    if defect == "missing":
        rows.pop()
    elif defect == "foreign":
        rows[0]["name"] = "unrelated.exe"
    elif defect == "duplicate":
        rows[1] = copy.deepcopy(rows[0])
    elif defect == "digest":
        rows[0]["digest"] = None
    elif defect == "starter":
        rows[0]["state"] = "starter"
    else:
        rows[0]["size"] = True
    with pytest.raises(ValueError):
        guard.attached(release(assets=rows), complete=True)


def build_outputs(tmp_path):
    """Create two inert build outputs and independently authored exact checksum records."""
    folder = tmp_path / "release/installers"
    folder.mkdir(parents=True)
    for name in guard.names("Windows")[::2]:
        raw = ("bounded synthetic binary " + name).encode()
        (folder / name).write_bytes(raw)
        (folder / (name + ".sha256")).write_text(
            hashlib.sha256(raw).hexdigest() + "  " + name.replace(" ", ".") + "\n", "ascii"
        )
    return folder


def test_upload_streams_exact_files_to_prepared_id_without_clobber(github, monkeypatch, tmp_path):
    monkeypatch.setattr(guard, "ROOT", tmp_path)
    folder = build_outputs(tmp_path)
    sent = []

    def transmit(identifier, stream, name, size, digest):
        assert identifier == IDENTIFIER
        raw = stream.read()
        assert len(raw) == size and hashlib.sha256(raw).hexdigest() == digest
        assert (
            raw
            == (
                folder / next(n for n in guard.names("Windows") if n.replace(" ", ".") == name)
            ).read_bytes()
        )
        row = asset(name, len(sent) + 1, raw)
        sent.append(name)
        github.record["assets"].append(row)
        return row

    monkeypatch.setattr(guard, "upload_bytes", transmit)
    guard.upload(IDENTIFIER, SOURCE, "Windows")
    assert sent == [name.replace(" ", ".") for name in guard.names("Windows")]
    with pytest.raises(ValueError, match="no clobber"):
        guard.upload(IDENTIFIER, SOURCE, "Windows")
    assert len(sent) == 4


def test_checksum_failure_prevents_all_uploads(github, monkeypatch, tmp_path):
    monkeypatch.setattr(guard, "ROOT", tmp_path)
    folder = build_outputs(tmp_path)
    (folder / guard.names("Windows")[0]).write_bytes(b"modified binary")
    monkeypatch.setattr(guard, "upload_bytes", lambda *_: pytest.fail("No network write may occur"))
    with pytest.raises(ValueError, match="checksum"):
        guard.upload(IDENTIFIER, SOURCE, "Windows")


def test_strict_metadata_and_complete_lookup_bounds(monkeypatch):
    for raw in ['{"id":1,"id":2}', '{"value":NaN}', '{"value":Infinity}']:
        with pytest.raises(ValueError):
            guard.strict_json(raw)
    monkeypatch.setattr(guard, "api", lambda *_: [{}] * 100)
    with pytest.raises(ValueError, match="bound"):
        guard.complete_list(guard.BASE + "/code-scanning/analyses?ref=main")


def workflow_contract(text):
    """A deliberate reviewed workflow-format contract, not a general YAML parser or trust boundary."""
    assert "--clobber" not in text and "--draft=false" not in text
    assert "gh release" not in text and "max-parallel: 1" in text
    assert "python scripts/release_guard.py prepare" in text
    assert "python scripts/release_guard.py upload" in text
    assert "python scripts/release_guard.py verify" in text
    for job, expected in {
        "prepare": {"contents": "write", "actions": "read", "security-events": "read"},
        "build": {"contents": "write"},
        "verify-draft": {"contents": "write", "actions": "read", "security-events": "read"},
    }.items():
        section = re.search(rf"(?ms)^  {job}:\n(.*?)(?=^  [a-z-]+:|\Z)", text).group(1)
        maps = re.findall(r"(?ms)^    permissions:\n(.*?)(?=^    \S|\Z)", section)
        assert len(maps) == 1
        actual = {}
        for line in maps[0].splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            match = re.fullmatch(r"([a-z-]+): (read|write|none)", line)
            assert match and match[1] not in actual
            actual[match[1]] = match[2]
        assert actual == expected
    assert text.count("EXPECTED_RELEASE_ID: ${{ needs.prepare.outputs.release_id }}") == 2


def test_actual_workflow_retains_source_and_draft_privilege_contract():
    workflow_contract(
        (Path(__file__).resolve().parents[2] / ".github/workflows/release-native.yml").read_text(
            "utf-8"
        )
    )


@pytest.mark.parametrize(
    "old,new",
    [
        ("--clobber", "--clobber"),
        ("max-parallel: 1", "max-parallel: 3"),
        ("  verify-draft:\n", "  publish:\n"),
        ("      security-events: read", "      security-events: write"),
        ("      contents: write", "      contents: read"),
        ("      contents: write", "      contents: write\n      packages: write # extra"),
        ("      contents: write", "      contents: write\n      contents: read # duplicate"),
    ],
)
def test_actual_workflow_mutations_cannot_erase_guards(old, new):
    text = (Path(__file__).resolve().parents[2] / ".github/workflows/release-native.yml").read_text(
        "utf-8"
    )
    text = text + "\n# --clobber" if old == "--clobber" else text.replace(old, new, 1)
    with pytest.raises((AssertionError, AttributeError)):
        workflow_contract(text)


@pytest.mark.parametrize(
    "permission",
    [
        "contents: read",
        "contents: write\n      packages: write # extra",
        "contents: write\n      contents: read # duplicate",
    ],
)
def test_final_get_only_draft_verifier_still_requires_reviewed_push_visibility(permission):
    text = (Path(__file__).resolve().parents[2] / ".github/workflows/release-native.yml").read_text(
        "utf-8"
    )
    before, marker, verifier = text.partition("  verify-draft:\n")
    assert marker and verifier.count("      contents: write") == 1
    changed = before + marker + verifier.replace("contents: write", permission, 1)
    with pytest.raises(AssertionError):
        workflow_contract(changed)


class Response:
    """Real HTTP response shape with a bounded inert byte body."""

    def __init__(self, status, raw):
        self.status, self.raw = status, raw

    def read(self, size):
        return self.raw[:size]


@pytest.mark.parametrize(
    "status,missing,accepted",
    [
        (404, True, True),
        (404, False, False),
        (403, True, False),
        (302, True, False),
        (500, True, False),
    ],
)
def test_only_actual_http404_means_absence(monkeypatch, status, missing, accepted):
    calls = []

    class Connection:
        def __init__(self, host, timeout):
            assert host == "api.github.com" and timeout == 30

        def request(self, method, path, body, headers):
            calls.append((method, path))
            assert headers["Authorization"] == "Bearer synthetic-test-token"

        def getresponse(self):
            return Response(status, b'{"message":"not available"}')

        def close(self):
            calls.append("closed")

    monkeypatch.setenv("GH_TOKEN", "synthetic-test-token")
    monkeypatch.setattr(guard.http.client, "HTTPSConnection", Connection)
    if accepted:
        assert guard.api(guard.BASE + "/git/ref/tags/v" + guard.VERSION, missing=missing) is None
    else:
        with pytest.raises(ValueError):
            guard.api(guard.BASE + "/git/ref/tags/v" + guard.VERSION, missing=missing)
    assert calls[-1] == "closed" and len(calls) == 2


def test_upload_transport_uses_fixed_host_id_and_real_stream_digest(monkeypatch):
    raw = b"bounded-payload"
    digest = hashlib.sha256(raw).hexdigest()
    chunks, requests = [], []

    class Connection:
        def __init__(self, host, timeout):
            assert host == "uploads.github.com" and timeout == 60

        def putrequest(self, method, path):
            requests.append((method, path))

        def putheader(self, key, value):
            assert "\r" not in key + value and "\n" not in key + value

        def endheaders(self):
            pass

        def send(self, data):
            chunks.append(data)

        def getresponse(self):
            return Response(201, json.dumps(asset("example.exe", raw=raw)).encode())

        def close(self):
            pass

    monkeypatch.setenv("GH_TOKEN", "synthetic-test-token")
    monkeypatch.setattr(guard.http.client, "HTTPSConnection", Connection)
    guard.upload_bytes(IDENTIFIER, io.BytesIO(raw), "example.exe", len(raw), digest)
    assert b"".join(chunks) == raw
    assert requests == [("POST", f"/{guard.BASE}/releases/{IDENTIFIER}/assets?name=example.exe")]


def context_fixture(tmp_path, monkeypatch):
    """Coherent product manifests and exact git calls; no real repository/account state."""
    monkeypatch.setattr(guard, "ROOT", tmp_path)
    (tmp_path / "package.json").write_text(json.dumps({"version": guard.VERSION}), "utf-8")
    (tmp_path / "package-lock.json").write_text(
        json.dumps({"version": guard.VERSION, "packages": {"": {"version": guard.VERSION}}}),
        "utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(f'[project]\nversion="{guard.VERSION}"\n', "utf-8")
    monkeypatch.setenv("GITHUB_REPOSITORY", guard.REPOSITORY)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.setenv("EXPECTED_SOURCE_SHA", SOURCE)
    replies = {("git", "rev-parse", "HEAD"): SOURCE + "\n", ("git", "status", "--porcelain"): ""}

    def git(arguments, **options):
        assert options == {
            "cwd": tmp_path,
            "check": True,
            "capture_output": True,
            "text": True,
            "timeout": 10,
        }
        return SimpleNamespace(stdout=replies[tuple(arguments)])

    monkeypatch.setattr(guard.subprocess, "run", git)
    return replies


def test_clean_context_binds_actual_git_and_product_versions(tmp_path, monkeypatch):
    context_fixture(tmp_path, monkeypatch)
    assert guard.context() == SOURCE


@pytest.mark.parametrize(
    "defect", ["foreign-repo", "pr", "branch", "dirty", "alias", "source", "old-version"]
)
def test_delivery_context_refuses_untrusted_or_unversioned_sources(tmp_path, monkeypatch, defect):
    replies = context_fixture(tmp_path, monkeypatch)
    if defect == "foreign-repo":
        monkeypatch.setenv("GITHUB_REPOSITORY", "someone/else")
    elif defect == "pr":
        monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    elif defect == "branch":
        monkeypatch.setenv("GITHUB_REF", "refs/heads/feature")
    elif defect == "dirty":
        replies[("git", "status", "--porcelain")] = " M web/main.ts\n"
    elif defect == "alias":
        replies[("git", "rev-parse", "HEAD")] = "main\n"
    elif defect == "source":
        monkeypatch.setenv("EXPECTED_SOURCE_SHA", "b" * 40)
    else:
        (tmp_path / "package.json").write_text('{"version":"1.4.0"}', "utf-8")
    with pytest.raises(ValueError):
        guard.context()


def test_bounded_hash_checks_actual_shrink_and_growth():
    assert guard.file_hash(io.BytesIO(b"1234"), 4) == hashlib.sha256(b"1234").hexdigest()
    with pytest.raises(ValueError, match="shrank"):
        guard.file_hash(io.BytesIO(b"123"), 4)
    with pytest.raises(ValueError, match="grew"):
        guard.file_hash(io.BytesIO(b"12345"), 4)


def test_output_descriptor_rejects_empty_oversize_and_hardlinks(tmp_path):
    path = tmp_path / "payload"
    path.write_bytes(b"")
    with pytest.raises(ValueError):
        guard.open_output(path)
    path.write_bytes(b"12345")
    with pytest.raises(ValueError):
        guard.open_output(path, 4)
    with guard.open_output(path, 5) as stream:
        assert stream.read() == b"12345"
    alias = tmp_path / "alias"
    os.link(path, alias)
    with pytest.raises(ValueError):
        guard.open_output(path)


def test_changed_output_after_all_sidecar_preflight_cannot_upload(github, monkeypatch, tmp_path):
    monkeypatch.setattr(guard, "ROOT", tmp_path)
    folder = build_outputs(tmp_path)
    original = guard.draft
    calls = 0

    def changing(identifier, source):
        nonlocal calls
        calls += 1
        if calls == 2:
            (folder / guard.names("Windows")[0]).write_bytes(b"modified after sidecar preflight")
        return original(identifier, source)

    monkeypatch.setattr(guard, "draft", changing)
    monkeypatch.setattr(
        guard, "upload_bytes", lambda *_: pytest.fail("Modified bytes must not be sent")
    )
    with pytest.raises(ValueError, match="changed after checksum"):
        guard.upload(IDENTIFIER, SOURCE, "Windows")
