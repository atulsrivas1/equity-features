"""Run from an installed editable/wheel environment; exact foundation pins."""
import importlib.metadata as md
import json
import platform
import sys
import numpy as np
import pyarrow as pa
import equity_feature_contracts as c
import equity_features as f

assert sys.version_info[:2]==(3,12) and sys.maxsize==2**63-1
assert c.__version__==f.__version__==f.contracts_version
assert np.__version__=='2.2.6' and pa.__version__=='20.0.0'
a=np.array([2**63-1,-2**63],dtype=np.int64)
assert a.tolist()==[2**63-1,-2**63]
arr=pa.array([1_700_000_000_000_000_001,None,1_700_000_000_000_000_002],type=pa.timestamp('ns',tz='UTC'))
assert arr.cast(pa.int64()).to_pylist()==[1_700_000_000_000_000_001,None,1_700_000_000_000_000_002]
assert pa.array(a).to_numpy(zero_copy_only=True).tolist()==a.tolist()
print(json.dumps(dict(python=platform.python_version(),system=platform.system(),machine=platform.machine(),numpy=np.__version__,pyarrow=pa.__version__,setuptools=md.version('setuptools'))))
print('Installed package and optional columnar precision/null compatibility verified.')
