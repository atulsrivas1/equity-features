"""Qualify positive/negative callers against actual installed public packages."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    import equity_feature_contracts as contracts
    import equity_features as features
    import equity_feature_demo as demo
    root = Path(__file__).resolve().parents[1]
    for module in (contracts, features, demo):
        folder = Path(module.__file__).resolve().parent
        assert 'site-packages' in folder.parts, 'installed qualification rejects editable/source imports'
        assert (folder/'py.typed').is_file(), folder
    assert contracts.__version__ == features.__version__ == features.contracts_version
    for module in (contracts, features):
        assert all(hasattr(module, name) for name in module.__all__)
    work = root/'work';work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='typed-', dir=work) as tmp:
        cwd = Path(tmp).resolve();assert cwd.is_relative_to(work.resolve())
        env = dict(os.environ, MYPYPATH='')
        command = [sys.executable, '-m', 'mypy', '--strict', '--no-incremental']
        sample = root/'examples/typed_caller.py'
        subprocess.run(command+[str(sample), str(Path(demo.__file__).parent)], cwd=cwd, env=env, check=True)
        negative = cwd/'invalid_caller.py'
        negative.write_text('''from equity_feature_contracts import EntityKey, PriceUnit
from equity_feature_contracts.adapter_kit import run_conformance
from equity_features.session import compute_bars
compute_bars(None, "not_config", entity=EntityKey("A", "S"))
PriceUnit("fraction", "USD")
run_conformance(("not_a_case",))
''', encoding='utf-8')
        result = subprocess.run(command+[str(negative)], cwd=cwd, env=env, capture_output=True, text=True)
        assert result.returncode == 1, result.stdout+result.stderr
        assert result.stdout.count('[arg-type]') == 3, result.stdout+result.stderr
        for name in ('compute_bars', 'PriceUnit', 'run_conformance'):
            assert name in result.stdout, result.stdout
        subprocess.run([sys.executable, '-I', str(sample)], cwd=cwd, check=True)
    print('Installed public py.typed/exports, positive caller+consumer typing and THREE rejected invalid calls verified.')


if __name__ == '__main__':
    main()
