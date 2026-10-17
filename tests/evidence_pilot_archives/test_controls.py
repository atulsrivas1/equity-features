"""Inert regression fixtures for the qualification tool; no build or install."""
import base64
import csv
import hashlib
import importlib.util
import io
from pathlib import Path
import sysconfig
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('pilot_archives', ROOT / 'tools/evidence_pilot_archives.py')
assert spec and spec.loader
audit = importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


class ArchiveControls(unittest.TestCase):
    def tree(self, root):
        files = {'LICENSE': b'synthetic license', 'README.md': b'probe\n', 'pyproject.toml': b'probe',
            'setup.cfg': b'probe', 'src/probe/__init__.py': b'VALUE=1\n', 'src/probe/py.typed': b'',
            'src/probe.egg-info/PKG-INFO': b'selected metadata',
            'src/probe.egg-info/top_level.txt': b'probe\n',
            'src/probe.egg-info/SOURCES.txt': b'original\n'}
        for name, raw in files.items():
            path = root / name;path.parent.mkdir(parents=True, exist_ok=True);path.write_bytes(raw)
        before = audit.file_map(root)
        sources = '\n'.join(sorted(files)) + '\n'
        (root / 'src/probe.egg-info/SOURCES.txt').write_text(sources, encoding='utf-8')
        for name in ('__init__.py', 'py.typed'):
            path = root / 'build/lib/probe' / name;path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((root / 'src/probe' / name).read_bytes())
        (root / ('build/bdist.' + sysconfig.get_platform())).mkdir()
        return before

    def test_supported_generated_tree_is_bound_to_selected_full_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);before = self.tree(root)
            result = audit.sdist_transition(before, audit.file_map(root), 'probe', root)
            self.assertEqual(result['after']['src/probe/__init__.py'], before['src/probe/__init__.py'])
            self.assertIn('build/lib/probe/__init__.py', result['changed'])

    def test_module_prefix_alias_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);before = self.tree(root)
            (root / 'build/lib/probe_extra.py').write_bytes(b'unselected')
            with self.assertRaises(AssertionError):audit.sdist_transition(before, audit.file_map(root), 'probe', root)

    def test_original_metadata_mutation_deletion_or_kind_change_is_rejected(self):
        for action in ('change', 'delete', 'directory'):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as temp:
                root = Path(temp);before = self.tree(root)
                path = root / 'src/probe.egg-info/PKG-INFO'
                if action == 'change':path.write_bytes(b'changed')
                else:
                    path.unlink()
                    if action == 'directory':path.mkdir()
                with self.assertRaises(AssertionError):audit.sdist_transition(before, audit.file_map(root), 'probe', root)

    def test_generated_package_bytes_and_manifest_omission_are_rejected(self):
        for action in ('package', 'manifest'):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as temp:
                root = Path(temp);before = self.tree(root)
                if action == 'package':(root / 'build/lib/probe/__init__.py').write_bytes(b'changed')
                else:(root / 'src/probe.egg-info/SOURCES.txt').write_bytes(b'LICENSE\n')
                with self.assertRaises(AssertionError):audit.sdist_transition(before, audit.file_map(root), 'probe', root)

    def test_package_metadata_without_optional_project_urls_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);module = 'equity_feature_bundles';version = '0.1.0a1'
            (root / 'src' / module).mkdir(parents=True)
            (root / 'src' / module / '__init__.py').write_bytes(b'VALUE=1\n')
            (root / 'src' / module / 'py.typed').write_bytes(b'')
            (root / 'README.md').write_bytes(b'probe\n');(root / 'LICENSE').write_bytes(b'license')
            (root / 'pyproject.toml').write_text('''[project]
name="equity-feature-bundles"
version="0.1.0a1"
description="probe"
requires-python=">=3.12,<3.13"
license="Apache-2.0"
license-files=["LICENSE"]
readme="README.md"
authors=[{name="Atul Srivastava"}]
dependencies=[]
''', encoding='utf-8')
            info = module + '-' + version + '.dist-info/'
            metadata = b'Metadata-Version: 2.4\nName: equity-feature-bundles\nVersion: 0.1.0a1\nSummary: probe\nRequires-Python: <3.13,>=3.12\nLicense-Expression: Apache-2.0\nLicense-File: LICENSE\nAuthor: Atul Srivastava\nDescription-Content-Type: text/markdown\n\nprobe\n'
            files = {module + '/__init__.py': b'VALUE=1\n', module + '/py.typed': b'',
                info + 'METADATA': metadata, info + 'WHEEL': b'probe',
                info + 'top_level.txt': (module + '\n').encode(), info + 'licenses/LICENSE': b'license'}
            rows = [(name, 'sha256=' + base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).rstrip(b'=').decode(), str(len(raw))) for name, raw in sorted(files.items())]
            rows.append((info + 'RECORD', '', ''))
            out = io.StringIO();csv.writer(out, lineterminator='\n').writerows(rows)
            files[info + 'RECORD'] = out.getvalue().encode()
            wheel = root / (module + '-' + version + '-py3-none-any.whl');wheel.write_bytes(b'inert physical placeholder')
            helper = SimpleNamespace(PACKAGES={'bundles': (module, version)}, contents=lambda path, with_members=False: (files, {}))
            result = audit.inspect(wheel, 'bundles', root, helper)
            self.assertTrue(result['metadata_source_readme_verified'])
            self.assertTrue(result['record_verified'])


if __name__ == '__main__':unittest.main()
