"""Import isolation in a new interpreter, including explicit forbidden import hooks."""
import os
import subprocess
import sys
import unittest


class OptionalTests(unittest.TestCase):
    def test_root_does_not_import_calculator_or_source(self):
        code='''import importlib.abc,sys
class Deny(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in ('equity_features','numpy','pyarrow','requests','httpx','equity_feature_io_contracts','equity_feature_io_sdk','equity_feature_workers'):
            raise AssertionError('forbidden optional import')
sys.meta_path.insert(0,Deny())
import equity_feature_diagnostics as d
assert d.__version__=='0.1.0a1'
assert not any(n.startswith('equity_features') for n in sys.modules)
'''
        # Development source-path execution is explicitly distinct from installed -I.
        args=[sys.executable]
        if 'PYTHONPATH' not in os.environ:args+=['-I']
        subprocess.run([*args,'-c',code],check=True)


if __name__=='__main__':unittest.main()
