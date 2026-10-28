#!/usr/bin/env python3
"""Independent recompute harness for the EF5 price-structures contract proposal (stdlib only).

Reads docs/ef5/PRICE_STRUCTURES_CONTRACT_PROPOSAL.json. For EVERY result fixture (candle, structure, technical and the
known_at KA-set) it re-derives status, reasons, expected/observed counts, exact value, float64, float.hex, acceptance
rule and witnesses from the fixture inputs and the contract text, and requires the fixture to pass its own admission
model. For EVERY refusal fixture it applies the recorded mutation to the base fixture and requires the admission model
to report exactly one fault, equal to the recorded stage and error code (single-fault audit).

Formulation differs on purpose from the scratch builder that wrote the JSON: integer cross-multiplication and
extreme-value comparisons instead of per-neighbour loops, boundary-close differences for the trend count, and a
slot-state table built before any arithmetic. It shares no code with that builder.
Usage: python ef5_fixture_expand.py [PATH_TO_CONTRACT_JSON]
"""
import copy
import json
import os
import re
import sys
from fractions import Fraction

INT64 = 2 ** 63 - 1
REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEFAULT = os.path.join(os.environ.get("EF5_DOCS_DIR") or os.path.join(REPO_ROOT, "docs", "ef5"),
                       "PRICE_STRUCTURES_CONTRACT_PROPOSAL.json")
BASE_NS = 1700000000000000000
SLOT_NS = 60 * 10 ** 9
DAY_NS = 86400 * 10 ** 9
FAIL = []

PRECEDENCE = ["absent_input", "unknown_availability", "future_knowledge", "null_field", "ineligible", "governed_gap",
              "future_market", "partial_universe", "insufficient_history", "no_eligible_observations",
              "empty_universe", "zero_denominator"]
STATUS_OF = {"absent_input": "missing_input", "unknown_availability": "missing_input",
             "future_knowledge": "missing_input", "null_field": "missing_input", "governed_gap": "incomplete_coverage",
             "future_market": "incomplete_coverage", "insufficient_history": "insufficient_history",
             "no_eligible_observations": "not_applicable", "zero_denominator": "not_applicable"}
POLICY = {"candle": "ef5-candle1", "structure": "ef5-structure1", "technical": "ef5-technical1"}
CATALOGUE = {
    "candle": ["candle.body_fraction", "candle.doji", "candle.engulfing_bearish", "candle.engulfing_bullish",
               "candle.inside_bar", "candle.lower_shadow_fraction", "candle.upper_shadow_fraction"],
    "structure": ["structure.last_swing_high_price", "structure.last_swing_low_price",
                  "structure.swing_high_confirmed", "structure.swing_low_confirmed"],
    "technical": ["technical.momentum_acceleration_fraction_per_second_squared",
                  "technical.price_velocity_fraction_per_second", "technical.session_return_fraction",
                  "technical.signed_trend_window_count"],
}
PARAMS = {"candle": ["doji_body_max_fraction"], "structure": ["swing_strength", "lookback"],
          "technical": ["trend_window", "trend_count"]}
COMMON = ["policy_version", "epoch_profile", "evidence_limit"]
CLOSE_ONLY_OK = {"technical.momentum_acceleration_fraction_per_second_squared",
                 "technical.price_velocity_fraction_per_second", "technical.signed_trend_window_count"}


def fail(where, msg):
    FAIL.append("%s: %s" % (where, msg))


# ------------------------------------------------------------------ knowledge
def know_reason(ka, k):
    """known_at null is unknown_availability, later than K is future_knowledge, equal to K is known."""
    if ka is None:
        return "unknown_availability"
    if ka > k:
        return "future_knowledge"
    return None


def parts(slot):
    """(token_or_row, ka, rev) of a compact slot."""
    if isinstance(slot, dict):
        return slot.get("row"), slot["ka"] if "ka" in slot else 50, slot.get("rev")
    return slot, 50, None


def classify_slot(slot, k):
    """(reason, row): the single cause of a slot being unusable, or (None, row)."""
    body, ka, _ = parts(slot)
    if body == "absent":
        return "absent_input", None
    if body == "gap":
        return "governed_gap", None
    if body == "forming":
        return "future_market", None
    why = know_reason(ka, k)
    if why:
        return why, None
    if body == "null":
        return "null_field", None
    if body == "empty":
        return "no_eligible_observations", None
    return None, body


def decide(reasons):
    for r in PRECEDENCE:
        if r in reasons:
            return STATUS_OF[r]
    return "available"


# ------------------------------------------------------------------ grid
def grid_end(fx, i):
    if fx.get("grid") == "daily":
        ends = fx.get("ends_s")
        return BASE_NS + (ends[i] if ends else (i + 1) * 86400) * 10 ** 9
    return BASE_NS + (i + 1) * SLOT_NS


def grid_start(fx, i):
    return grid_end(fx, i) - (DAY_NS if fx.get("grid") == "daily" else SLOT_NS)


# ------------------------------------------------------------------ evaluation
def span_of(name, p):
    if name in ("candle.inside_bar", "candle.engulfing_bullish", "candle.engulfing_bearish"):
        return 1
    if name.startswith("candle."):
        return 0
    if name.endswith("confirmed"):
        return 2 * p["swing_strength"]
    if name.startswith("structure."):
        return p["lookback"]
    if name.endswith("session_return_fraction"):
        return None
    if name.endswith("price_velocity_fraction_per_second"):
        return 1
    if name.startswith("technical.momentum"):
        return 2
    return p["trend_window"] * p["trend_count"]


def required(name, p, t):
    if name.endswith("session_return_fraction"):
        return [0, t] if t else [0]
    return list(range(t - span_of(name, p), t + 1))


def sgn(a, b):
    return (a > b) - (a < b)


def evaluate(fx):
    p, k_cut, cols = fx["params"], fx["K"], fx.get("columns", "ohlcv")
    n = len(fx["slots"])
    t = fx["target"] if "target" in fx else n - 1
    table = [classify_slot(s, k_cut) for s in fx["slots"]]
    scale = fx["unit"]["scale"]
    results = {}
    for name in fx["outputs"]:
        need = required(name, p, t)
        causes, ready = [], {}
        for i in need:
            if i < 0:
                continue
            why, row = table[i]
            if why is None and cols == "close":
                lacks = name not in CLOSE_ONLY_OK
                if name.endswith("session_return_fraction") and i == t and t > 0:
                    lacks = False
                if lacks:
                    why = "absent_input"
            if why:
                causes.append(why)
            else:
                ready[i] = row
        if need[0] < 0:
            causes.append("insufficient_history")
        out = {"expected": len(need), "observed": len(ready)}
        value = kind = None
        located = None
        if not causes:
            value, kind, located, extra = compute(name, fx, p, t, ready, scale)
            causes.extend(extra)
        status = decide(causes)
        out["status"], out["reasons"] = status, sorted(set(causes))
        out["value"], out["witnesses"] = None, []
        if status == "available":
            out["value"] = (kind, value)
            order = [t] + [i for i in sorted(ready) if i != t]
            if located is not None:
                order = [located, t] + [i for i in sorted(ready) if i not in (located, t)]
            out["witnesses"] = ["slot:%d" % i for i in order][: p["evidence_limit"]]
        results[name] = out
    return results


def compute(name, fx, p, t, ready, scale):
    """returns (value, kind, located slot, extra reasons); value is bool, int or Fraction."""
    if name.startswith("candle."):
        o, h, lo, c, _ = ready[t]
        rng, body = h - lo, abs(c - o)
        if name in ("candle.inside_bar", "candle.engulfing_bullish", "candle.engulfing_bearish"):
            o1, h1, l1, c1, _ = ready[t - 1]
            if name == "candle.inside_bar":
                return (h < h1) and (lo > l1), "bool", None, []
            cur_lo, cur_hi, pre_lo, pre_hi = min(o, c), max(o, c), min(o1, c1), max(o1, c1)
            covers = cur_lo <= pre_lo and cur_hi >= pre_hi and (cur_lo < pre_lo or cur_hi > pre_hi)
            if name == "candle.engulfing_bullish":
                return (c1 < o1) and (c > o) and covers, "bool", None, []
            return (c1 > o1) and (c < o) and covers, "bool", None, []
        kind = "bool" if name == "candle.doji" else "float"
        if rng == 0:
            return None, kind, None, ["zero_denominator"]
        if name == "candle.doji":
            num, den = (int(x) for x in p["doji_body_max_fraction"].split("/"))
            return body * den <= num * rng, "bool", None, []
        top = {"candle.body_fraction": body, "candle.upper_shadow_fraction": h - max(o, c),
               "candle.lower_shadow_fraction": min(o, c) - lo}[name]
        return Fraction(top, rng), "float", None, []
    if name.startswith("structure."):
        high = "high" in name
        col = 1 if high else 2
        series = {i: r[col] for i, r in ready.items()}
        kk = p["swing_strength"]

        def is_swing(s):
            around = [series[i] for i in range(s - kk, s + kk + 1) if i != s]
            return series[s] > max(around) if high else series[s] < min(around)
        if name.endswith("confirmed"):
            return is_swing(t - kk), "bool", None, []
        hits = [s for s in range(t - p["lookback"] + kk, t - kk + 1) if is_swing(s)]
        if not hits:
            return None, "float", None, ["no_eligible_observations"]
        return Fraction(series[hits[-1]], 10 ** scale), "float", hits[-1], []
    # technical
    def close(i):
        return ready[i][-1] if fx.get("columns") == "close" else ready[i][3]

    def secs(i):
        return Fraction(grid_end(fx, i) - grid_end(fx, i - 1), 10 ** 9)

    def velocity(i):
        return Fraction(close(i) - close(i - 1), close(i - 1)) / secs(i)
    if name.endswith("session_return_fraction"):
        return Fraction(close(t) - ready[0][0], ready[0][0]), "float", None, []
    if name.endswith("price_velocity_fraction_per_second"):
        return velocity(t), "float", None, []
    if name.startswith("technical.momentum"):
        return (velocity(t) - velocity(t - 1)) / secs(t), "float", None, []
    nn, mm = p["trend_window"], p["trend_count"]
    marks = [close(t - j * nn) for j in range(mm, -1, -1)]
    return sum(sgn(b, a) for a, b in zip(marks, marks[1:])), "int", None, []


# ------------------------------------------------------------------ value comparison
def accept_rule(x):
    if x == 0:
        return "exact_plus_zero"
    d = x.denominator
    return "exact_float64" if (d & (d - 1)) == 0 and abs(x.numerator) < 2 ** 53 else "tolerance"


def compare(where, exp, got):
    for key in ("status", "reasons", "expected", "observed", "witnesses"):
        if exp[key] != got[key]:
            fail(where, "%s: fixture %r recomputed %r" % (key, exp[key], got[key]))
    ev, gv = exp["value"], got["value"]
    if (ev is None) != (gv is None):
        fail(where, "value presence differs (fixture %r)" % (ev,))
        return
    if ev is None:
        return
    kind, val = gv
    if kind == "bool":
        if ev != {"bool": val, "acceptance": "exact_bool"}:
            fail(where, "bool value %r recomputed %r" % (ev, val))
    elif kind == "int":
        if ev != {"int": val, "acceptance": "exact_integer"}:
            fail(where, "int value %r recomputed %r" % (ev, val))
    else:
        f = float(val)
        want = {"exact": "%d/%d" % (val.numerator, val.denominator), "float64": f, "hex": f.hex(),
                "acceptance": accept_rule(val)}
        if ev != want:
            fail(where, "float value %r recomputed %r" % (ev, want))


# ------------------------------------------------------------------ admission
def wire_rows(fx):
    """expand compact slots to explicit delivered rows; tokens deliver nothing."""
    rows = []
    adj = fx.get("adjustment")
    for i, slot in enumerate(fx["slots"]):
        base = {"i": i, "inst": "X", "ss": "D%d" % i if fx.get("grid") == "daily" else "S1",
                "start": grid_start(fx, i), "end": grid_end(fx, i), "basis": adj, "ka": 50, "rev": None}
        if isinstance(slot, dict) and "wire" in slot:
            base.update(slot["wire"])
            rows.append(base)
            continue
        body, ka, rev = parts(slot)
        if isinstance(body, str):
            continue
        versions = slot.get("versions") if isinstance(slot, dict) else None
        for v in versions or [{"ka": ka, "rev": rev}]:
            r = dict(base)
            r.update({"row": body, "ka": v["ka"], "rev": v["rev"]})
            rows.append(r)
    return rows


def is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def admission(fx):
    """every fault the independent model finds, as a sorted list of (stage, code) pairs."""
    faults = set()
    prod = fx["producer"]
    rows = wire_rows(fx)
    width = 5 if fx.get("columns", "ohlcv") == "ohlcv" else 1
    bad = set()
    for r in rows:
        cells = r.get("row")
        if cells is None:
            continue
        problem = None
        if not isinstance(cells, list) or len(cells) != width:
            problem = "INVALID_SCHEMA"
        elif any(not is_int(c) for c in cells):
            problem = "INVALID_SCHEMA"
        elif any(c > INT64 or c < -INT64 - 1 for c in cells):
            problem = "OVERFLOW"
        elif r["ka"] is not None and not is_int(r["ka"]):
            problem = "INVALID_SCHEMA"
        if problem:
            faults.add(("wire", problem))
            bad.add(id(r))
    cutoff = grid_end(fx, len(fx["slots"]) - 1)
    # shared stage
    if fx.get("coverage", "declared") != "declared" and rows:
        faults.add(("shared", "INVALID_SCHEMA"))
    if "context" in fx and fx["context"] is None:
        faults.add(("shared", "INVALID_SCHEMA"))
    seen, prev_end = set(), None
    for r in rows:
        if id(r) in bad:
            continue
        cells = r.get("row")
        code = None
        if cells is not None:
            prices = cells[:4] if len(cells) == 5 else cells
            if any(c <= 0 for c in prices):
                code = "INVALID_SCHEMA"
            elif len(cells) == 5:
                o, h, lo, c, v = cells
                if h < lo or h < max(o, c) or lo > min(o, c) or v < 0:
                    code = "INVALID_SCHEMA"
        if code is None and (r["start"] >= r["end"] or r["end"] > cutoff):
            code = "BOUNDS"
        key = (r["inst"], r["ss"], r["start"], r["end"])
        if code is None and key in seen:
            code = "DUPLICATE"
        if code is None and prev_end is not None and r["start"] < prev_end:
            code = "INVALID_ORDER"
        if code:
            faults.add(("shared", code))
            bad.add(id(r))
            continue
        seen.add(key)
        prev_end = r["end"]
    # config stage
    p = fx["params"]
    want = set(COMMON + PARAMS[prod])
    if set(p) != want:
        faults.add(("config", "INVALID_CONFIG"))
    if fx.get("adjustment") is None:
        faults.add(("config", "INVALID_CONFIG"))
    elif fx["adjustment"] not in ("unadjusted", "split_adjusted"):
        faults.add(("config", "UNSUPPORTED_ADJUSTMENT"))
    if p.get("epoch_profile") not in (None, "session_reset", "governed_history"):
        faults.add(("config", "INVALID_CONFIG"))
    if "evidence_limit" in p and not (is_int(p["evidence_limit"]) and 0 <= p["evidence_limit"] <= 10000):
        faults.add(("config", "INVALID_CONFIG"))
    if prod == "candle" and "doji_body_max_fraction" in p:
        m = re.fullmatch(r"([1-9][0-9]*)/([1-9][0-9]*)", str(p["doji_body_max_fraction"]))
        if not m or int(m.group(1)) > int(m.group(2)):
            faults.add(("config", "INVALID_CONFIG"))
    if prod == "structure" and "swing_strength" in p and "lookback" in p:
        k, lb = p["swing_strength"], p["lookback"]
        if not (is_int(k) and 1 <= k <= 64 and is_int(lb) and 2 * k <= lb <= 4096):
            faults.add(("config", "INVALID_CONFIG"))
    elif prod == "structure" and ("swing_strength" in p) != ("lookback" in p):
        pass  # missing key already reported by the parameter-set check
    if prod == "technical" and "trend_window" in p and "trend_count" in p:
        if not (is_int(p["trend_window"]) and 1 <= p["trend_window"] <= 1024 and is_int(p["trend_count"])
                and 1 <= p["trend_count"] <= 256):
            faults.add(("config", "INVALID_CONFIG"))
    names = fx["outputs"]
    if any(nm not in CATALOGUE[prod] for nm in names):
        faults.add(("config", "UNKNOWN_FEATURE"))
    elif p.get("epoch_profile") == "governed_history" and want <= set(p):
        for nm in names:
            sp = span_of(nm, p)
            if sp is None or sp > 63:
                faults.add(("config", "INVALID_CONFIG"))
    if fx.get("call", "compute") != "compute":
        faults.add(("config", "UNSUPPORTED_CAPABILITY"))
    sc, cur = fx["unit"]["scale"], fx["unit"]["currency"]
    if not (is_int(sc) and 0 <= sc <= 18) or not re.fullmatch(r"[A-Z]{3}", str(cur)):
        faults.add(("config", "INVALID_UNIT"))
    # version stage
    if "policy_version" in p and p["policy_version"] != POLICY[prod]:
        faults.add(("version", "INCOMPATIBLE_VERSION"))
    # identity stage
    on_grid = {(grid_start(fx, i), grid_end(fx, i)): i for i in range(len(fx["slots"]))}
    for r in rows:
        if id(r) in bad:
            continue
        slot_index = on_grid.get((r["start"], r["end"]))
        ss_ok = slot_index is not None and r["ss"] == ("D%d" % slot_index if fx.get("grid") == "daily" else "S1")
        if r["inst"] != "X" or not ss_ok or r["basis"] != fx.get("adjustment"):
            faults.add(("identity", "INCONSISTENT_IDENTITY"))
    return sorted(faults)


# ------------------------------------------------------------------ mutation
def set_path(root, path, value=None, delete=False):
    keys = path.split(".")
    assert keys[0] == "fixture"
    cur = root
    for key in keys[1:-1]:
        cur = cur[int(key)] if isinstance(cur, list) else cur[key]
    last = keys[-1]
    if isinstance(cur, list):
        last = int(last)
    if delete:
        del cur[last]
    else:
        cur[last] = value


def mutate(base, muts):
    fx = copy.deepcopy(base)
    for m in muts:
        if "delete" in m:
            set_path(fx, m["delete"], delete=True)
        else:
            set_path(fx, m["set"], m["value"])
    return fx


# ------------------------------------------------------------------ driver
LISTS = ("candle_fixtures", "structure_fixtures", "technical_fixtures", "ka_fixtures")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    by_id = {}
    for key in LISTS:
        for fx in doc[key]:
            if fx["id"] in by_id:
                fail(fx["id"], "duplicate fixture id")
            by_id[fx["id"]] = fx
            if fx["K"] != 100:
                fail(fx["id"], "K must be 100")
            got = evaluate(fx)
            if list(got) != sorted(got):
                fail(fx["id"], "outputs not listed in lexical feature-id order")
            if set(fx["expected"]) != set(got):
                fail(fx["id"], "expected outputs differ from selected outputs")
            for name, res in got.items():
                compare("%s %s" % (fx["id"], name), fx["expected"][name], res)
            faults = admission(fx)
            if faults:
                fail(fx["id"], "result fixture fails admission: %r" % (faults,))
    cnt = doc["fixture_counts"]
    for key, label in (("candle_fixtures", "candle_result"), ("structure_fixtures", "structure_result"),
                       ("technical_fixtures", "technical_result"), ("ka_fixtures", "ka_result")):
        if len(doc[key]) != cnt[label]:
            fail(label, "declared %d, found %d" % (cnt[label], len(doc[key])))
    codes = {}
    for rf in doc["refusal_fixtures"]:
        base = by_id.get(rf["base"])
        if base is None:
            fail(rf["id"], "unknown base %s" % rf["base"])
            continue
        faults = admission(mutate(base, rf["mutation"]))
        if faults != [(rf["stage"], rf["error_code"])]:
            fail(rf["id"], "recorded (%s, %s), independent admission found %r" % (rf["stage"], rf["error_code"], faults))
        codes[rf["error_code"]] = codes.get(rf["error_code"], 0) + 1
    if len(doc["refusal_fixtures"]) != cnt["refusal"]:
        fail("refusal", "declared %d, found %d" % (cnt["refusal"], len(doc["refusal_fixtures"])))
    ids = [rf["id"] for rf in doc["refusal_fixtures"]]
    if len(set(ids)) != len(ids):
        fail("refusal", "duplicate refusal ids")
    outputs = sum(len(fx["expected"]) for key in LISTS for fx in doc[key])
    print("EF5 price structures: candle=%d structure=%d technical=%d ka=%d refusal=%d (%d outputs recomputed; "
          "%d distinct refusal codes)" % (len(doc["candle_fixtures"]), len(doc["structure_fixtures"]),
                                          len(doc["technical_fixtures"]), len(doc["ka_fixtures"]),
                                          len(doc["refusal_fixtures"]), outputs, len(codes)))
    if FAIL:
        for line in FAIL:
            print("MISMATCH", line)
        print("%d MISMATCH(ES)" % len(FAIL))
        return 1
    print("ALL FIXTURES AND REFUSALS RECOMPUTED AND MATCHED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
