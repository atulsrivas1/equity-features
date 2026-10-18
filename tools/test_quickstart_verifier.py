"""Adversarial delivery-boundary tests; no product imports/network/installs."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import io
import json
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile
import hashlib
import base64
import verify_quickstart as q
import quickstart_probe as probe


def bundle(items):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, value in items:
            archive.writestr(name, value)
    return buffer.getvalue()


def map_for(items):
    return {name: {"sha256": q.sha(value), "bytes": len(value)} for name, value in items}


class DeliveryBoundaries(unittest.TestCase):
    def test_wheel_record_dependency_and_raw_drift(self):
        info = "demo-1.dist-info/"
        md = b"Name: demo\nVersion: 1\nRequires-Python: >=3.12\nLicense-Expression: Apache-2.0\n\n"
        files = {"demo/__init__.py": b"# fixed\n", info + "METADATA": md}
        def make(payload, broken=False):
            record = info + "RECORD"
            rows = [p + ",sha256=" + base64.urlsafe_b64encode(hashlib.sha256(v).digest()).decode().rstrip("=")
                    + "," + str(len(v)) for p, v in payload.items()]
            rows.append(record + ",,")
            data = dict(payload, **{record: ("\n".join(rows) + "\n").encode()})
            if broken:
                data[record] = data[record].replace(b"sha256=", b"invalid=", 1)
            raw = bundle(data.items())
            expected = {"sha256": q.sha(raw), "bytes": len(raw), "entries": map_for(data.items()),
                "metadata": {"name": "demo", "version": "1", "requires_python": ">=3.12",
                             "requires_dist": [], "license_expression": "Apache-2.0"}, "source_bindings": {}}
            return raw, expected
        raw, expected = make(files)
        q.validate_wheel(raw, expected)
        with self.assertRaises(ValueError):
            q.validate_wheel(raw + b"drift", expected)
        raw, expected = make(files, broken=True)
        with self.assertRaises(ValueError):
            q.validate_wheel(raw, expected)
        raw, expected = make(dict(files, **{info + "METADATA": md.replace(b"\n\n", b"\nRequires-Dist: unselected\n\n")}))
        with self.assertRaises(ValueError):
            q.validate_wheel(raw, expected)

    def test_exact_archive_and_corruption(self):
        items = [("manifest.json", b"{}"), ("demo.whl", b"fixed")]
        self.assertEqual(q.zip_files(bundle(items), map_for(items)), dict(items))
        with self.assertRaises(ValueError):
            q.zip_files(bundle([*items[:1], ("demo.whl", b"drift")]), map_for(items))
        with self.assertRaises(ValueError):
            q.zip_files(bundle(items), map_for(items[:1]))

    def test_duplicate_traversal_symlink(self):
        with self.assertWarns(UserWarning):
            duplicate = bundle([("x", b"1"), ("x", b"2")])
        with self.assertRaises(ValueError):
            q.zip_files(duplicate, map_for([("x", b"2")]))
        for name in ("../x", "/x", "x\\y", "C:x"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                q.zip_files(bundle([(name, b"x")]), map_for([(name, b"x")]))
        link = zipfile.ZipInfo("x")
        link.create_system = 3
        link.external_attr = 0o120777 << 16
        with self.assertRaises(ValueError):
            q.zip_files(bundle([(link, b"target")]), map_for([("x", b"target")]))

    def test_archive_caps(self):
        with self.assertRaises(ValueError):
            q.zip_files(b"x" * q.LIMIT, {})
        items = [(str(i), b"x") for i in range(65)]
        with self.assertRaises(ValueError):
            q.zip_files(bundle(items), map_for(items))

    def test_expiry_and_identity(self):
        now = datetime(2026, 10, 18, tzinfo=timezone.utc)
        expected = {"id": 1, "name": "fixed", "size_in_bytes": 100, "digest": "sha256:fixed",
                    "expires_at": (now + timedelta(days=1)).isoformat(), "workflow_run": {"id": 2}, "expired": False}
        q.validate_artifact(expected, expected, now)
        for key, value in (("id", 3), ("digest", "sha256:drift"), ("workflow_run", {"id": 3}), ("expired", True)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                q.validate_artifact(dict(expected, **{key: value}), expected, now)
        with self.assertRaises(ValueError):
            q.validate_artifact(expected, expected, now + timedelta(days=2))

    def test_four_complete_lines(self):
        lines = ["one", "two", "three", "four"]
        q.validate_stdout(b"one\r\ntwo\r\nthree\r\nfour\r\n", lines)
        for raw in (b"one\ntwo\nthree\n", b"one\ntwo\nthree\nfour\nextra\n", b"one\ntwo\nthree\nfour"):
            with self.assertRaises(ValueError):
                q.validate_stdout(raw, lines)

    def test_core_drift(self):
        before = {"core": {"file": "fixed"}, "core_sha256": "fixed"}
        q.unchanged_core(before, before)
        with self.assertRaises(ValueError):
            q.unchanged_core(before, {"core": {"file": "changed"}, "core_sha256": "fixed"})

    def test_runtime_and_owned_destination(self):
        q.validate_platform("Windows", "cpython", (3, 12), 64)
        for args in (("Darwin", "cpython", (3, 12), 64), ("Linux", "pypy", (3, 12), 64),
                     ("Linux", "cpython", (3, 11), 64), ("Linux", "cpython", (3, 12), 32)):
            with self.assertRaises(ValueError):
                q.validate_platform(*args)
        with self.assertRaises(ValueError):
            q.validate_platform("Linux", "cpython", (3, 12), 64, "aarch64")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = q.new_work(root, "Linux")
            (target / "retained.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaises(ValueError):
                q.new_work(root, "Linux")
            self.assertEqual((target / "retained.txt").read_text(encoding="utf-8"), "preserve")
        with tempfile.TemporaryDirectory() as raw:
            with patch.object(Path, "is_symlink", return_value=True), self.assertRaises(ValueError):
                q.new_work(Path(raw), "Linux")
            self.assertFalse((Path(raw) / "work").exists())

    def test_forbidden_dependency_and_source_fallback(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            prefix = root / "env"
            prefix.mkdir()
            (prefix / "pyvenv.cfg").write_text("include-system-site-packages = false\n", encoding="utf-8")
            valid = [("pip", "1"), ("equity-feature-contracts", "0.0.4a4"),
                     ("equity-features", "0.0.4a4"), ("equity-feature-demo", "0.4.0")]
            fake = lambda items: [SimpleNamespace(metadata={"Name": n}, version=v) for n, v in items]
            with patch.object(probe.sys, "prefix", str(prefix)):
                with patch.object(probe.metadata, "distributions", return_value=fake([*valid, ("numpy", "2")])):
                    with self.assertRaises(ValueError):
                        probe.installed_inventory({}, "full")
                with patch.object(probe.metadata, "distributions", return_value=fake(valid)):
                    with patch.object(probe.importlib.util, "find_spec", return_value=object()):
                        with self.assertRaises(ValueError):
                            probe.installed_inventory({}, "full")
            outside = root / "checkout.py"
            outside.write_text("# outside\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                probe.checked_origin(outside, prefix)

    def test_complete_filesystem_and_duplicate_distributions(self):
        with tempfile.TemporaryDirectory() as raw:
            prefix = Path(raw)
            site = prefix / "site-packages"
            site.mkdir()
            (site / "module.py").write_text("# owned\n", encoding="utf-8")
            dist = SimpleNamespace(metadata={"Name": "equity-features"}, version="0.0.4a4",
                files=[Path("module.py")], locate_file=lambda p: site / p)
            probe.complete_site_inventory([dist], prefix)
            unrecorded = site / "unrecorded.py"
            unrecorded.write_text("# must be refused\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                probe.complete_site_inventory([dist], prefix)
            unrecorded.unlink()
            (site / "injected.pth").write_text("# refused too\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                probe.complete_site_inventory([dist], prefix)
            duplicate = SimpleNamespace(metadata={"Name": "equity_features"}, version="0.0.4a4")
            with self.assertRaises(ValueError):
                probe.unique_distributions([dist, duplicate])
            with self.assertRaises(ValueError):
                probe.complete_site_inventory([dist, dist], prefix)

    def test_closed_installer_origin(self):
        with tempfile.TemporaryDirectory() as raw:
            wheel = (Path(raw) / "demo.whl").resolve()
            direct = {"archive_info": {"hashes": {"sha256": "fixed"}, "hash": "sha256=fixed"},
                      "url": wheel.as_uri()}
            probe.validate_direct_url(direct, "fixed", wheel)
            for bad in (dict(direct, dir_info={"editable": True}),
                        dict(direct, archive_info={"hashes": {"sha256": "fixed"}, "hash": "sha256:wrong"}),
                        dict(direct, url=wheel.as_uri() + "?query=1"),
                        dict(direct, url=wheel.as_uri() + "#fragment")):
                with self.assertRaises(ValueError):
                    probe.validate_direct_url(bad, "fixed", wheel)

    def test_nonzero_timeout_and_private_logs(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            replay = q.Replay.__new__(q.Replay)
            replay.root = root
            replay.work = root / "owned"
            for part in ("raw-private", "logs", "run"):
                (replay.work / part).mkdir(parents=True, exist_ok=True)
            replay.system = "Windows"
            replay.steps = []
            def fake(*args, **kwargs):
                kwargs["stdout"].write((str(replay.work) + " preserved\n").encode())
                return SimpleNamespace(returncode=2)
            with patch.object(q.subprocess, "run", side_effect=fake) as command:
                with self.assertRaises(ValueError):
                    replay.run("bad-exit", ["fixed"], 1)
                self.assertEqual(command.call_count, 1)
            self.assertEqual(replay.steps[0]["returncode"], 2)
            self.assertIn("$WORK", (replay.work / "logs/01-bad-exit-stdout.txt").read_text(encoding="utf-8"))
            with patch.object(q.subprocess, "run", side_effect=subprocess.TimeoutExpired(["fixed"], 1)) as command:
                with self.assertRaises(subprocess.TimeoutExpired):
                    replay.run("timeout", ["fixed"], 1)
                self.assertEqual(command.call_count, 1)
            self.assertTrue(replay.steps[1]["timed_out"])


if __name__ == "__main__":
    unittest.main()
