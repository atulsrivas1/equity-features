"""Qualify positive/negative callers against actual installed public packages."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/_versions.py, also when loaded by path from tests
from _versions import CONTRACTS, FEATURES


def main():
    import equity_feature_contracts as contracts
    import equity_features as features
    import equity_feature_demo as demo
    root = Path(__file__).resolve().parents[1]
    for module in (contracts, features, demo):
        folder = Path(module.__file__).resolve().parent
        assert 'site-packages' in folder.parts, 'installed qualification rejects editable/source imports'
        assert (folder/'py.typed').is_file(), folder
    assert (contracts.__version__, features.__version__, features.contracts_version) == (CONTRACTS, FEATURES, CONTRACTS)
    for module in (contracts, features):
        assert all(hasattr(module, name) for name in module.__all__)
    work = root/'work';work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='typed-', dir=work) as tmp:
        cwd = Path(tmp).resolve();assert cwd.is_relative_to(work.resolve())
        env = dict(os.environ, MYPYPATH='')
        command = [sys.executable, '-m', 'mypy', '--strict', '--no-incremental']
        sample = root/'examples/typed_caller.py'
        subprocess.run(command+[str(sample)], cwd=cwd, env=env, check=True)
        subprocess.run(command+[str(root/'examples/typing/ef1_anchor_positive.py')],
                       cwd=cwd, env=env, check=True)
        # Package-name discovery preserves PEP561 lookup instead of adding site-packages
        # as a user source root (which shadows typing_extensions on Windows).
        subprocess.run(command+['-p', 'equity_feature_demo'], cwd=cwd, env=env, check=True)
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
        ef1_negative = cwd/'invalid_ef1_caller.py'
        ef1_negative.write_text('''from equity_feature_contracts import ConfigSpec, EntityKey
from equity_features.ef1 import compute_ef1, decode_ef1_context
def invalid(config: ConfigSpec, entity: EntityKey) -> None:
    compute_ef1((), "not_config", entity=entity)
    compute_ef1(("not_a_batch",), config, entity=entity)
    decode_ef1_context("not_config")
''', encoding='utf-8')
        ef1_result = subprocess.run(command+[str(ef1_negative)], cwd=cwd, env=env,
                                    capture_output=True, text=True)
        assert ef1_result.returncode == 1, ef1_result.stdout+ef1_result.stderr
        assert ef1_result.stdout.count('[arg-type]') == 3, ef1_result.stdout+ef1_result.stderr
        for name in ('compute_ef1', 'decode_ef1_context'):
            assert name in ef1_result.stdout, ef1_result.stdout
        subprocess.run([sys.executable, '-I', str(sample)], cwd=cwd, check=True)
    print('Installed public py.typed/exports, legacy+EF1 positive callers and THREE legacy/THREE EF1 rejected invalid calls verified.')


if __name__ == '__main__':
    main()
