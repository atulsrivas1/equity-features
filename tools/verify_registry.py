"""Development-only catalog parity; runtime never reads these documents."""
from pathlib import Path
import sys
import re
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages/contracts/src"))
from equity_feature_contracts import builtin_registry
from equity_feature_contracts._implemented import BATCH_IDS, UPDATE_IDS, RESTORE_IDS, MERGE_IDS
catalog = {x.feature_id:x for x in builtin_registry().list_features()}
rows = re.findall(r"^\| ((?:session|history|baseline|relative|breadth)\.[a-z_.]+) \| ([^|]+) \| ([^|]+) \| (R[12]) \| ([^|]+) \|$", (ROOT/"docs/features/V1_SCOPE.md").read_text(encoding="utf-8"), re.M)
assert len(rows)==40 and set(catalog)=={x[0] for x in rows}
for feature_id,_,_,release,_ in rows:
    definition=catalog[feature_id]
    assert definition.planned_release==release, feature_id
    assert definition.capabilities.batch == (feature_id in BATCH_IDS)
    assert definition.capabilities.update == (feature_id in UPDATE_IDS)
    assert definition.capabilities.restore == (feature_id in RESTORE_IDS)
    assert definition.capabilities.merge == (feature_id in MERGE_IDS)
    assert (ROOT/definition.formula_document).is_file(), definition.formula_document
count=0
for document in ("SESSION_FORMULAS","QUOTE_FORMULAS","HISTORICAL_FORMULAS"):
    for line in (ROOT/f"docs/features/{document}.md").read_text(encoding="utf-8").splitlines():
        cells=[x.strip() for x in line.strip("|").split("|")]
        if len(cells)>1 and cells[0] in catalog:
            assert catalog[cells[0]].formula==cells[1], cells[0]
            count+=1
assert count==32, count
print("40 catalog IDs/releases (39 frozen plus the DV1 built-in), formula links, explicit implementation capabilities and 32 table formulas verified")
