"""Independent archive fixtures prevent consumer/core namespace contamination."""
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile

root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('distribution_gate',root/'tools/build_foundation.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


class DistributionIsolation(unittest.TestCase):
    def test_typed_licensed_consumer_wheel_rejects_core_and_escape(self):
        files={'equity_feature_demo/__init__.py':b'# synthetic consumer\n',
               'equity_feature_demo/py.typed':b'',
               'equity_feature_demo-0.3.0.dist-info/METADATA':b'Name: equity-feature-demo\nLicense-Expression: Apache-2.0\n',
               'equity_feature_demo-0.3.0.dist-info/licenses/LICENSE':(root/'LICENSE').read_bytes()}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'equity_feature_demo-0.3.0-py3-none-any.whl'
            for extra in (None,'equity_features/__init__.py','equity_feature_demo/../equity_features/__init__.py','equity_feature_demo/.env'):
                with self.subTest(extra=extra):
                    with zipfile.ZipFile(path,'w') as archive:
                        for name,data in files.items():archive.writestr(name,data)
                        if extra is not None:archive.writestr(extra,b'# synthetic contamination\n')
                    if extra is None:gate.inspect(path)
                    else:
                        with self.assertRaises(AssertionError):gate.inspect(path)

    def test_consumer_sdist_excludes_bundled_core_and_private_path(self):
        prefix='equity_feature_demo-0.3.0/'
        files={'src/equity_feature_demo/__init__.py':b'# synthetic consumer\n',
               'src/equity_feature_demo/py.typed':b'', 'pyproject.toml':b'# synthetic project\n',
               'LICENSE':(root/'LICENSE').read_bytes()}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'equity_feature_demo-0.3.0.tar.gz'
            for extra,data in ((None,b''),('src/equity_features/__init__.py',b'# synthetic contamination'),
                               ('src/equity_feature_demo/private.py',b'C:\\Users\\synthetic-owner\\private.csv')):
                with self.subTest(extra=extra):
                    with tarfile.open(path,'w:gz') as archive:
                        for name,content in {**files,**({extra:data} if extra else {})}.items():
                            member=tarfile.TarInfo(prefix+name);member.size=len(content);archive.addfile(member,io.BytesIO(content))
                    if extra is None:gate.inspect(path)
                    else:
                        with self.assertRaises(AssertionError):gate.inspect(path)


if __name__=='__main__':unittest.main()
