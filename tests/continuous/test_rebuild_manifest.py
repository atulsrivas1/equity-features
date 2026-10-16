"""Exact generated metadata transition; all other selected bytes stay bound."""
import ast
import hashlib
from pathlib import Path, PurePosixPath
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
TREE=ast.parse((ROOT/'tools/build_continuous.py').read_bytes())
FUNCTION=next(node for node in TREE.body if isinstance(node,ast.FunctionDef) and node.name=='verify_sdist_rebuild_inputs')
SPACE={'PurePosixPath':PurePosixPath,'sha':lambda body:hashlib.sha256(body).hexdigest()}
exec(compile(ast.Module(body=[FUNCTION],type_ignores=[]),'reviewed-byte-transition','exec'),SPACE)
VERIFY=SPACE['verify_sdist_rebuild_inputs']


class RebuiltManifest(unittest.TestCase):
    def test_exact_transition_and_every_other_source_byte(self):
        prefix='synthetic-1/';manifest=prefix+'src/synthetic.egg-info/SOURCES.txt'
        before={prefix+'LICENSE':b'license\n',prefix+'setup.cfg':b'generated\n',
            prefix+'src/synthetic/__init__.py':b'VALUE=1\n',
            manifest:b'LICENSE\nsrc/synthetic/__init__.py\nsrc/synthetic.egg-info/SOURCES.txt'}
        literal=b'LICENSE\nsetup.cfg\nsrc/synthetic/__init__.py\nsrc/synthetic.egg-info/SOURCES.txt'
        for mode in ('valid','source_drift','metadata_drift','manifest_extra','manifest_missing','manifest_newline'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory(prefix='continuous-rebuilt-metadata-') as directory:
                root=Path(directory)
                for name,body in before.items():
                    path=root/name.removeprefix(prefix);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
                path=root/'src/synthetic.egg-info/SOURCES.txt';path.write_bytes(literal)
                if mode=='source_drift':(root/'src/synthetic/__init__.py').write_bytes(b'VALUE=2\n')
                elif mode=='metadata_drift':(root/'setup.cfg').write_bytes(b'other\n')
                elif mode=='manifest_extra':path.write_bytes(literal+b'\nextra.py')
                elif mode=='manifest_missing':path.write_bytes(before[manifest])
                elif mode=='manifest_newline':path.write_bytes(literal+b'\n')
                if mode=='valid':
                    after=VERIFY(root,before,prefix,'synthetic')
                    self.assertEqual(after[manifest],{'sha256':hashlib.sha256(literal).hexdigest(),'bytes':len(literal)})
                else:
                    with self.assertRaises(AssertionError):VERIFY(root,before,prefix,'synthetic')


if __name__=='__main__':unittest.main()
