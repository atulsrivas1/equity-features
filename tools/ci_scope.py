"""Conservative committed-source CI routing; no routing changes in CI001.

Contract: docs/stories/CI-001_CONTRACT.json. This is not a security boundary
against an authorized author replacing workflow or classifier source.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

REPOSITORY = "atulsrivas1/equity-features"
SCHEMA = "equity-features.ci-scope.v1"
READERS = (
    "docs/api/CONTINUOUS_QUOTES.md",
    "docs/api/PUBLIC_API.md",
    "docs/contracts/RESULTS.md",
)
ALLOWLIST_SHA256 = hashlib.sha256(
    ("equity-features.ci-allowlist.v1\n" + "\n".join(READERS) + "\n").encode("ascii")
).hexdigest()
OID = re.compile(r"[0-9a-f]{40}\Z")
METADATA = re.compile(rb":([0-7]{6}) ([0-7]{6}) ([0-9a-f]{40}) ([0-9a-f]{40}) ([ADMT])\Z")
ZERO = "0" * 40


class SourceInvalid(ValueError):
    """A source binding cannot establish qualification."""


def require(condition: bool) -> None:
    if not condition:
        raise SourceInvalid()


def oid(value: Any) -> str:
    require(type(value) is str and OID.fullmatch(value) is not None)
    return value


def field(value: Any, *keys: str) -> Any:
    for key in keys:
        require(type(value) is dict and key in value)
        value = value[key]
    return value


def git(root: Path, *args: str) -> bytes:
    # Read Git objects, not caller-selected commands, replacement refs or diff helpers.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_OPTIONAL_LOCKS="0")
    try:
        done = subprocess.run(
            ["git", "--no-pager", *args], cwd=root, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
        )
    except OSError as exc:
        raise SourceInvalid() from exc
    require(done.returncode == 0)
    return done.stdout


def resolved(root: Path, value: str, kind: str) -> str:
    try:
        result = git(root, "rev-parse", "--verify", value + "^{" + kind + "}").decode("ascii").strip()
    except UnicodeError as exc:
        raise SourceInvalid() from exc
    return oid(result)


def parse_diff(raw: bytes) -> list[tuple[bytes, ...]]:
    """Consume the entire NUL-framed raw diff before a routing decision."""
    if not raw:
        return []
    parts = raw.split(b"\0")
    require(parts[-1] == b"" and (len(parts) - 1) % 2 == 0)
    result = []
    for index in range(0, len(parts) - 1, 2):
        match = METADATA.fullmatch(parts[index])
        require(match is not None and bool(parts[index + 1]))
        assert match is not None
        result.append((*match.groups(), parts[index + 1]))
    return result


def reader_change(root: Path, entry: tuple[bytes, ...]) -> bool:
    old_mode, new_mode, old_oid, new_oid, status, path = entry
    if (old_mode, new_mode, status) != (b"100644", b"100644", b"M"):
        return False
    if old_oid == ZERO.encode() or new_oid == ZERO.encode():
        return False
    if path not in {p.encode("ascii") for p in READERS}:
        return False
    for value in (old_oid, new_oid):
        data = git(root, "cat-file", "blob", value.decode("ascii"))
        try:
            data.decode("utf-8", errors="strict")
        except UnicodeError:
            return False
        if b"\0" in data:
            return False
    return True


def invalid() -> dict[str, Any]:
    return dict(
        schema=SCHEMA, valid=False, decision="FULL", reason="SOURCE_INVALID",
        repository=REPOSITORY, event=None, base=None, source_head=None,
        checkout_head=None, checkout_tree=None, diff_sha256=None,
        allowlist_sha256=ALLOWLIST_SHA256, changes_count=None,
    )


def classify(root: Path, event: Any, context: dict[str, str]) -> dict[str, Any]:
    """Bind an actual push/PR merge checkout; invalid source never qualifies."""
    try:
        require(context.get("GITHUB_REPOSITORY") == REPOSITORY)
        require(field(event, "repository", "full_name") == REPOSITORY)
        kind = context.get("GITHUB_EVENT_NAME")
        require(kind in ("push", "pull_request"))
        checkout = oid(context.get("GITHUB_SHA"))
        require(resolved(root, "HEAD", "commit") == checkout)
        require(resolved(root, checkout, "commit") == checkout)
        tree = resolved(root, checkout, "tree")
        if kind == "push":
            require(oid(field(event, "after")) == checkout)
            ref = field(event, "ref")
            require(type(ref) is str and re.fullmatch(r"refs/heads/.+", ref) is not None)
            require(ref == context.get("GITHUB_REF") and field(event, "deleted") is False)
            before = oid(field(event, "before"))
            source = checkout
            base = None if before == ZERO else before
        else:
            number = field(event, "number")
            require(type(number) is int and number > 0)
            require(context.get("GITHUB_REF") == f"refs/pull/{number}/merge")
            require(field(event, "pull_request", "base", "repo", "full_name") == REPOSITORY)
            base = oid(field(event, "pull_request", "base", "sha"))
            source = oid(field(event, "pull_request", "head", "sha"))
            parents = git(root, "rev-list", "--parents", "-n", "1", checkout).decode("ascii").split()
            require(parents == [checkout, base, source])
        result = invalid()
        result.update(valid=True, event=kind, base=base, source_head=source,
                      checkout_head=checkout, checkout_tree=tree)
        if base is None:
            result.update(reason="INITIAL_PUSH")
            return result
        require(resolved(root, base, "commit") == base)
        require(resolved(root, source, "commit") == source)
        raw = git(root, "diff", "--raw", "-z", "--no-abbrev", "--no-ext-diff",
                  "--no-textconv", "--no-renames", "--ignore-submodules=none", base, checkout, "--")
        entries = parse_diff(raw)
        result.update(diff_sha256=hashlib.sha256(raw).hexdigest(), changes_count=len(entries))
        if not entries:
            result.update(reason="EMPTY_DIFF")
        elif all(reader_change(root, entry) for entry in entries):
            result.update(decision="DOCS", reason="READERS_ONLY")
        else:
            result.update(reason="NON_READER_CHANGE")
        return result
    except (SourceInvalid, UnicodeError):
        return invalid()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        require(key not in value)
        value[key] = item
    return value


def main() -> int:
    try:
        require(len(sys.argv) == 1)
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes(),
                           object_pairs_hook=unique_object)
        result = classify(Path(__file__).resolve().parents[1], event, dict(os.environ))
    except (KeyError, OSError, ValueError, UnicodeError):
        result = invalid()
    sys.stdout.buffer.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
