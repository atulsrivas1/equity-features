"""Offline license/name consistency checks; no reservation/publication."""
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[1]
license_text=(ROOT/'LICENSE').read_text(encoding='utf-8').strip()
assert 'Apache License' in license_text and 'Version 2.0' in license_text
for name,distribution in [('contracts','equity-feature-contracts'),('features','equity-features')]:
    p=ROOT/'packages'/name
    meta=tomllib.loads((p/'pyproject.toml').read_text(encoding='utf-8'))['project']
    assert meta['name']==distribution and meta['license']=='Apache-2.0'
    assert meta['license-files']==['LICENSE']
    assert (p/'LICENSE').read_text(encoding='utf-8').strip()==license_text
    assert meta['urls']['Repository']=='https://github.com/atulsrivas1/equity-features'
print('Both distribution names, SPDX/license texts and public repository metadata agree.')
