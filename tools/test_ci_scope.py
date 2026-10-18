"""Independent synthetic Git/event fixtures for the closed CI001 contract."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import ci_scope as scope


# Literal test oracle, independent of the implementation's reader constant.
READERS = ["docs/api/CONTINUOUS_QUOTES.md", "docs/api/PUBLIC_API.md", "docs/contracts/RESULTS.md"]
REPO = "atulsrivas1/equity-features"
KEYS = {"schema", "valid", "decision", "reason", "repository", "event", "base",
        "source_head", "checkout_head", "checkout_tree", "diff_sha256", "allowlist_sha256", "changes_count"}


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="eq-ci001-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Synthetic Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "commit.gpgsign", "false")
        for path in READERS:
            self.write(path, b"Original synthetic reader.\n")
        self.write("packages/demo/input.py", b"VALUE = 1\n")
        (self.root / "tools").mkdir()
        shutil.copyfile(Path(scope.__file__), self.root / "tools/ci_scope.py")
        self.base = self.commit()

    def git(self, *args, data=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        return subprocess.check_output(["git", *args], cwd=self.root, env=env, input=data,
                                       stderr=subprocess.DEVNULL)

    def write(self, path, data=b"Changed synthetic content.\n"):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def commit(self, staged=False):
        if not staged:
            self.git("add", "--all")
        self.git("commit", "-m", "Synthetic fixture")
        return self.git("rev-parse", "HEAD").decode().strip()

    def push(self, before=None):
        head = self.git("rev-parse", "HEAD").decode().strip()
        event = dict(repository=dict(full_name=REPO), before=before or self.base, after=head,
                     ref="refs/heads/fixture", deleted=False)
        context = dict(GITHUB_REPOSITORY=REPO, GITHUB_EVENT_NAME="push", GITHUB_SHA=head,
                       GITHUB_REF="refs/heads/fixture")
        return event, context

    def check(self, event, context, decision, reason, count=None):
        result = scope.classify(self.root, event, context)
        self.assertEqual(set(result), KEYS)
        self.assertIs(result["valid"], reason != "SOURCE_INVALID")
        self.assertEqual((result["decision"], result["reason"]), (decision, reason))
        self.assertEqual(result["changes_count"], count)
        self.assertEqual(result["allowlist_sha256"], hashlib.sha256(
            b"equity-features.ci-allowlist.v1\ndocs/api/CONTINUOUS_QUOTES.md\ndocs/api/PUBLIC_API.md\ndocs/contracts/RESULTS.md\n"
        ).hexdigest())
        if reason == "SOURCE_INVALID":
            for key in ("event", "base", "source_head", "checkout_head", "checkout_tree", "diff_sha256", "changes_count"):
                self.assertIsNone(result[key])
        return result

    def test_each_reader_and_union(self):
        before = self.base
        for index, path in enumerate(READERS):
            with self.subTest(path=path):
                self.write(path, f"Reader change {index}.\n".encode())
                after = self.commit()
                self.check(*self.push(before), "DOCS", "READERS_ONLY", 1)
                before = after
        for path in READERS:
            self.write(path, b"All three readers.\n")
        self.commit()
        event, context = self.push(before)
        result = self.check(event, context, "DOCS", "READERS_ONLY", 3)
        raw = self.git("diff", "--raw", "-z", "--no-abbrev", "--no-renames", before, context["GITHUB_SHA"], "--")
        self.assertEqual(result["diff_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["base"], before)
        self.assertEqual(result["source_head"], context["GITHUB_SHA"])
        self.assertEqual(result["checkout_tree"], self.git("rev-parse", "HEAD^{tree}").decode().strip())

    def test_other_paths_and_mixed_change(self):
        paths = ["packages/demo/input.py", "tools/other.py", ".github/workflows/test.yml", "README.md",
                 "docs/new.md", "docs/unknown.json", "docs/frozen.txt", "docs/CHANGELOG.md",
                 "docs/PROJECT_KNOWLEDGE.md", "docs/SESSION_HANDOFF.md", "docs/knowledge/LESSONS.md"]
        before = self.base
        for path in paths:
            with self.subTest(path=path):
                self.write(path)
                after = self.commit()
                self.check(*self.push(before), "FULL", "NON_READER_CHANGE", 1)
                before = after
        self.write(READERS[0])
        self.write("packages/demo/input.py", b"VALUE = 999\n")
        self.commit()
        self.check(*self.push(before), "FULL", "NON_READER_CHANGE", 2)

    def test_deleted_added_and_renamed_reader(self):
        (self.root / READERS[0]).unlink()
        deleted = self.commit()
        self.check(*self.push(), "FULL", "NON_READER_CHANGE", 1)
        self.write(READERS[0])
        added = self.commit()
        self.check(*self.push(deleted), "FULL", "NON_READER_CHANGE", 1)
        self.git("mv", READERS[0], "docs/api/RENAMED.md")
        self.commit()
        self.check(*self.push(added), "FULL", "NON_READER_CHANGE", 2)

    def test_executable_and_symlink_index_modes(self):
        self.git("update-index", "--chmod=+x", READERS[0])
        executable = self.commit(staged=True)
        self.check(*self.push(), "FULL", "NON_READER_CHANGE", 1)
        blob = self.git("hash-object", "-w", "--stdin", data=b"some-target").decode().strip()
        self.git("update-index", "--cacheinfo", "120000," + blob + "," + READERS[0])
        self.commit(staged=True)
        self.check(*self.push(executable), "FULL", "NON_READER_CHANGE", 1)

    def test_non_utf8_and_nul_reader_blobs(self):
        before = self.base
        for data in (b"\xff", b"text\0binary"):
            self.write(READERS[0], data)
            after = self.commit()
            self.check(*self.push(before), "FULL", "NON_READER_CHANGE", 1)
            before = after

    def test_non_utf8_git_index_path(self):
        blob = self.git("hash-object", "-w", "--stdin", data=b"synthetic").strip()
        self.git("update-index", "-z", "--index-info", data=b"100644 " + blob + b"\tdocs/\xff.md\0")
        self.commit(staged=True)
        self.check(*self.push(), "FULL", "NON_READER_CHANGE", 1)

    def test_submodule_ignore_cannot_hide_gitlink_change(self):
        self.git("update-index", "--add", "--cacheinfo", "160000," + self.base + ",vendor/synthetic")
        before = self.commit(staged=True)
        self.write(READERS[0])
        self.git("add", "--", READERS[0])
        self.commit(staged=True)
        self.git("update-index", "--cacheinfo", "160000," + before + ",vendor/synthetic")
        self.commit(staged=True)
        self.git("config", "diff.ignoreSubmodules", "all")
        self.check(*self.push(before), "FULL", "NON_READER_CHANGE", 2)

    def test_empty_diff_and_initial_push(self):
        self.check(*self.push(), "FULL", "EMPTY_DIFF", 0)
        result = self.check(*self.push("0" * 40), "FULL", "INITIAL_PUSH")
        self.assertIsNone(result["base"])
        self.assertIsNone(result["diff_sha256"])
        self.assertEqual(result["source_head"], self.base)

    def test_large_real_diff_and_complete_adversarial_stream(self):
        for i in range(301):
            self.write(f"docs/bulk/{i:03}.md")
        self.commit()
        self.check(*self.push(), "FULL", "NON_READER_CHANGE", 301)
        # A synthetic stream puts the unsafe entry AFTER 300 apparently safe entries.
        old = self.git("rev-parse", self.base + ":" + READERS[0]).strip()
        metadata = b":100644 100644 " + old + b" " + old + b" M\0"
        raw = (metadata + READERS[0].encode() + b"\0") * 300 + metadata + b"tools/last.py\0"
        original = scope.git
        def supplied(root, *args):
            return raw if args and args[0] == "diff" else original(root, *args)
        with patch.object(scope, "git", supplied):
            result = self.check(*self.push(), "FULL", "NON_READER_CHANGE", 301)
            self.assertEqual(result["diff_sha256"], hashlib.sha256(raw).hexdigest())

    def test_push_identity_failures(self):
        event, context = self.push()
        cases = []
        for key, value in [("after", "f" * 40), ("before", "f" * 40), ("before", 3),
                           ("ref", "refs/heads/wrong"), ("deleted", True), ("deleted", 0)]:
            e = copy.deepcopy(event);e[key] = value;cases.append((e, context))
        e = copy.deepcopy(event);e["repository"]["full_name"] = "wrong/repo";cases.append((e, context))
        for key, value in [("GITHUB_SHA", "f" * 40), ("GITHUB_REPOSITORY", "wrong/repo"),
                           ("GITHUB_EVENT_NAME", "workflow_dispatch"), ("GITHUB_REF", "refs/tags/v1")]:
            c = dict(context);c[key] = value;cases.append((event, c))
        cases.extend([(None, context), ({}, context), (event, {})])
        for e, c in cases:
            with self.subTest(event=e, context=c):
                self.check(e, c, "FULL", "SOURCE_INVALID")

    def test_pull_request_exact_merge_and_mismatches(self):
        self.git("switch", "-c", "source")
        self.write(READERS[1]);source = self.commit()
        self.git("switch", "main")
        self.git("merge", "--no-ff", "source", "-m", "Synthetic merge")
        merge = self.git("rev-parse", "HEAD").decode().strip()
        event = dict(repository=dict(full_name=REPO), number=17,
                     pull_request=dict(base=dict(repo=dict(full_name=REPO), sha=self.base), head=dict(sha=source)))
        context = dict(GITHUB_REPOSITORY=REPO, GITHUB_EVENT_NAME="pull_request",
                       GITHUB_SHA=merge, GITHUB_REF="refs/pull/17/merge")
        result = self.check(event, context, "DOCS", "READERS_ONLY", 1)
        self.assertEqual((result["base"], result["source_head"], result["checkout_head"]), (self.base, source, merge))
        for number in (True, 0, "17"):
            e = copy.deepcopy(event);e["number"] = number
            self.check(e, context, "FULL", "SOURCE_INVALID")
        for part in ("base", "head"):
            e = copy.deepcopy(event);e["pull_request"][part]["sha"] = merge
            self.check(e, context, "FULL", "SOURCE_INVALID")
        e = copy.deepcopy(event);e["pull_request"]["base"]["repo"]["full_name"] = "wrong/repo"
        self.check(e, context, "FULL", "SOURCE_INVALID")
        c = dict(context);c["GITHUB_REF"] = "refs/pull/17/head"
        self.check(event, c, "FULL", "SOURCE_INVALID")

    def test_malformed_diff_is_not_accepted(self):
        good = b":100644 100644 " + b"a" * 40 + b" " + b"b" * 40 + b" M\0docs/ok.md\0"
        for raw in (good[:-1], good + b"extra\0", good.replace(b"100644", b"badmod", 1),
                    good.replace(b" M\0", b" R100\0"), good.replace(b"docs/ok.md", b""), b"\0"):
            with self.subTest(raw=raw), self.assertRaises(scope.SourceInvalid):
                scope.parse_diff(raw)
        event, context = self.push()
        original = scope.git
        with patch.object(scope, "git", lambda root, *args: b"bad" if args[0] == "diff" else original(root, *args)):
            self.check(event, context, "FULL", "SOURCE_INVALID")

    def test_cli_encoding_exit_and_duplicate_json(self):
        self.write(READERS[2]);self.commit()
        event, context = self.push()
        event_path = self.root / "event.json"
        event_path.write_text(json.dumps(event), encoding="utf-8")
        env = dict(os.environ, **context, GITHUB_EVENT_PATH=str(event_path))
        command = [sys.executable, str(self.root / "tools/ci_scope.py")]
        done = subprocess.run(command, env=env, capture_output=True, check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        value = json.loads(done.stdout)
        self.assertEqual((value["decision"], value["reason"]), ("DOCS", "READERS_ONLY"))
        self.assertEqual(done.stdout, (json.dumps(value, sort_keys=True, indent=2) + "\n").encode())
        for body in ('{"repository":{},"repository":{}}', '{', 'null'):
            event_path.write_text(body, encoding="utf-8")
            done = subprocess.run(command, env=env, capture_output=True, check=False)
            self.assertEqual(done.returncode, 1)
            self.assertEqual(json.loads(done.stdout), scope.invalid())
            self.assertEqual(done.stderr, b"")


if __name__ == "__main__":
    unittest.main(verbosity=2)
