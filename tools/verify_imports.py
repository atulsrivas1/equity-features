"""Source layout/import isolation smoke; no installed-artifact claim."""
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[1]

for name,expected in [('contracts','equity-feature-contracts'),('features','equity-features')]:
    p=ROOT/'packages'/name
    meta=tomllib.loads((p/'pyproject.toml').read_text(encoding='utf-8'))['project']
    assert meta['name']==expected and meta['license']=='Apache-2.0'
    assert (p/'LICENSE').read_text(encoding='utf-8').strip()==(ROOT/'LICENSE').read_text(encoding='utf-8').strip()
    assert (p/'src'/expected.replace('-','_')/'py.typed').exists()

code='''
import sys, importlib.abc
class Deny(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in {'numpy','pyarrow','duckdb','requests','httpx','adapters','workers'}:
            raise AssertionError('Forbidden optional/source import: '+fullname)
sys.meta_path.insert(0,Deny())
import equity_feature_contracts as c
assert not any(x.startswith('equity_features') for x in sys.modules)
import equity_features as f
import equity_features.session
assert c.__version__==f.contracts_version==f.__version__==EXPECTED_VERSION
assert not hasattr(f,'compute')
'''
code=code.replace('EXPECTED_VERSION',repr(meta['version']))
prefix=f'import sys;sys.path[:0]={str([str(ROOT/"packages/contracts/src"),str(ROOT/"packages/features/src")])}\n'
subprocess.run([sys.executable,'-I','-c',prefix+code],check=True)
print('Two package source imports, metadata, py.typed and inward dependency verified.')
