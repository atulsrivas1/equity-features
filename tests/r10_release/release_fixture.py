"""Fixed materialized outer tools/examples, never a package source fallback."""
from pathlib import Path
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT/'tools'))
import measure_r10 as measurement


def consumer():
    spec=importlib.util.spec_from_file_location('r10_consumer',ROOT/'examples/r10_point_in_time.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.example()
