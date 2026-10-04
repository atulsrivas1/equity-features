"""Independent exact reference checks for EQ-002; not the package API."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "tests/fixtures/session_math/golden.json").read_text(encoding="utf-8"))
I64 = 2**63 - 1


def total(values):
    result = sum(values)
    if not 0 <= result <= I64:
        raise ValueError("integer total overflow")
    return result


def trade_reference(rows, cutoff=120, close=120, closing_auction=False, opening_auction=False, k=2):
    if type(k) is not int or k < 1 or not 0 < cutoff <= close:
        raise ValueError("invalid K/target")
    if rows is None:
        return None
    seen = set()
    previous = None
    admitted = []
    for row in rows:
        key = (row["ts"], row["order"])
        if previous is not None and key <= previous:
            raise ValueError("ambiguous or unordered event")
        previous = key
        if row["id"] in seen:
            raise ValueError("duplicate identity")
        seen.add(row["id"])
        auction = row.get("auction")
        endpoint = row["ts"] == cutoff == close and auction == "close" and closing_auction
        if not (0 <= row["ts"] < cutoff or endpoint):
            raise ValueError("out of target")
        if auction == "open" and not opening_auction:
            continue
        if auction == "close" and not closing_auction:
            continue
        if not row.get("eligible", True):
            continue
        if any(type(row[x]) is not int or not 0 < row[x] <= I64 for x in ("price", "size")):
            raise ValueError("invalid price/size")
        admitted.append(row)
    volume = total([r["size"] for r in admitted])
    notional = sum(r["price"] * r["size"] for r in admitted)
    return {
        "count": len(admitted), "volume": volume, "notional": notional,
        "vwap": F(notional, volume) if volume else None,
        "mean_size": F(volume, len(admitted)) if admitted else None,
        "top_k": [r["id"] for r in sorted(admitted, key=lambda r: (-r["size"], r["ts"], r["order"], r["id"]))[:k]],
    }


def bar_reference(rows, expected=((0, 60), (60, 120)), cutoff=120, prior=98):
    if rows is None:
        return {"status": "missing_input", "value": None}
    previous_end = 0
    seen = set()
    for r in rows:
        if r["id"] in seen or r["start"] < previous_end or not 0 <= r["start"] < r["end"] <= cutoff:
            raise ValueError("bar identity/order/bounds")
        seen.add(r["id"])
        previous_end = r["end"]
        if type(r["volume"]) is not int or not 0 <= r["volume"] <= I64:
            raise ValueError("invalid volume")
        prices = [r[k] for k in ("open", "high", "low", "close")]
        if r["volume"] == 0:
            if any(p is not None for p in prices) or r.get("notional") not in (None, 0):
                raise ValueError("empty bar prices")
        else:
            if any(type(p) is not int or not 0 < p <= I64 for p in prices):
                raise ValueError("invalid bar price")
            if not r["low"] <= min(r["open"], r["close"]) <= max(r["open"], r["close"]) <= r["high"]:
                raise ValueError("inconsistent OHLC")
            n = r.get("notional")
            if n is not None and type(n) is not int:
                raise ValueError("notional must be exact integer coefficient in this scale0 fixture")
            if n is not None and not r["low"] * r["volume"] <= n <= r["high"] * r["volume"]:
                raise ValueError("inconsistent notional")
    if [(r["start"], r["end"]) for r in rows] != list(expected):
        return {"status": "incomplete_coverage", "value": None}
    volume = total([r["volume"] for r in rows])
    active = [r for r in rows if r["volume"]]
    o = active[0]["open"] if active else None
    c = active[-1]["close"] if active else None
    h = max((r["high"] for r in active), default=None)
    l = min((r["low"] for r in active), default=None)
    n = sum(r.get("notional", 0) or 0 for r in rows) if all(r.get("notional") is not None or not r["volume"] for r in rows) else None
    if prior is not None and (type(prior) is not int or prior <= 0):
        raise ValueError("invalid prior")
    return {"status": "available", "value": {
        "open": o, "high": h, "low": l, "close": c, "volume": volume, "notional": n,
        "close_weighted_price": F(sum(r["close"] * r["volume"] for r in active), volume) if volume else None,
        "open_close_return": F(c, o)-1 if o is not None else None,
        "range_fraction": F(h-l, c) if c is not None else None,
        "close_location": F(c-l, h-l) if h is not None and h > l else None,
        "overnight_gap": F(o, prior)-1 if o is not None and prior is not None else None,
        "close_close_return": F(c, prior)-1 if c is not None and prior is not None else None,
    }}


def interval(rows, start, end, cutoff=120):
    if not 0 <= start < end <= cutoff:
        raise ValueError("invalid window")
    if any(r["start"] < end and r["end"] > start and not (start <= r["start"] and r["end"] <= end) for r in rows):
        raise ValueError("straddling bar")
    subset = [r for r in rows if start <= r["start"] and r["end"] <= end]
    if not subset or subset[0]["start"] != start or subset[-1]["end"] != end or any(a["end"] != b["start"] for a, b in zip(subset, subset[1:])):
        return None
    active = [r for r in subset if r["volume"]]
    return [active[0]["open"] if active else None, max((r["high"] for r in active), default=None), min((r["low"] for r in active), default=None), active[-1]["close"] if active else None, sum(r["volume"] for r in subset)]


class SpecificationEvidence(unittest.TestCase):
    def test_all_twenty_exact_golden_values(self):
        bars, trades = FIXTURE["bars"], FIXTURE["trades"]
        b = bar_reference(bars)["value"]
        actual = {"session.bar."+k: b[k] for k in ("open", "high", "low", "close", "volume", "notional", "close_weighted_price")}
        actual.update({"session.price."+k: b[k] for k in ("open_close_return", "range_fraction", "close_location", "overnight_gap", "close_close_return")})
        windows = {"first": interval(bars, 0, 60), "last": interval(bars, 60, 120)}
        actual["session.structure.interval_ohlcv"] = windows
        actual["session.structure.interval_volume_share"] = {k: F(v[-1], b["volume"]) for k, v in windows.items()}
        actual.update({"session.trade."+k: v for k, v in trade_reference(trades).items()})
        self.assertEqual(set(actual), set(FIXTURE["expected"]))
        for k, v in FIXTURE["expected"].items():
            with self.subTest(feature=k):
                expected = F(v) if isinstance(v, str) else ({a: F(z) for a, z in v.items()} if k.endswith("volume_share") else v)
                self.assertEqual(actual[k], expected)

    def test_scope_and_specification_coverage(self):
        scope = (ROOT/"docs/features/V1_SCOPE.md").read_text(encoding="utf-8")
        wanted = {line.split("|")[1].strip() for line in scope.splitlines() if line.startswith("| session.") and "EQ-002" in line}
        spec = (ROOT/"docs/features/SESSION_FORMULAS.md").read_text(encoding="utf-8")
        documented = set(re.findall(r"^\| (session\.[a-z_.]+) \|", spec, re.M))
        self.assertEqual(wanted, documented)
        self.assertEqual(wanted, set(FIXTURE["expected"]))
        self.assertEqual(len(wanted), 20)

    def test_proxy_is_not_actual_notional_average(self):
        b = bar_reference(FIXTURE["bars"])["value"]
        self.assertNotEqual(b["close_weighted_price"], F(b["notional"], b["volume"]))

    def test_missing_notional_independent_fields(self):
        rows=deepcopy(FIXTURE["bars"]); rows[0].pop("notional")
        b=bar_reference(rows)["value"]
        self.assertIsNone(b["notional"]); self.assertEqual(b["volume"],500)

    def test_prior_absent_and_incompatible(self):
        b=bar_reference(FIXTURE["bars"],prior=None)["value"]
        self.assertIsNone(b["overnight_gap"]); self.assertIsNone(b["close_close_return"])
        self.assertEqual(b["close"],103)
        with self.assertRaises(ValueError):bar_reference(FIXTURE["bars"],prior=0)
        # Compatibility/availability flags are supplied contracts, not inferred from prices.
        for compatible, available in [(False,True),(True,False)]:
            selected=98 if compatible and available else None
            self.assertIsNone(bar_reference(FIXTURE["bars"],prior=selected)["value"]["overnight_gap"])

    def test_missing_empty_zero_denominator(self):
        self.assertIsNone(trade_reference(None))
        empty=trade_reference([])
        self.assertEqual([empty[x] for x in ("count","volume","notional")],[0,0,0])
        self.assertIsNone(empty["vwap"]); self.assertIsNone(empty["mean_size"]); self.assertEqual(empty["top_k"],[])
        self.assertEqual(bar_reference(None)["status"],"missing_input")
        zero={"id":"z","start":0,"end":120,"open":None,"high":None,"low":None,"close":None,"volume":0,"notional":0}
        b=bar_reference([zero],expected=((0,120),))["value"]
        self.assertEqual(b["volume"],0); self.assertEqual(b["notional"],0); self.assertIsNone(b["close_weighted_price"])
        self.assertEqual(interval([zero],0,120),[None,None,None,None,0])

    def test_flat_range(self):
        row={"id":"flat","start":0,"end":120,"open":100,"high":100,"low":100,"close":100,"volume":1,"notional":100}
        b=bar_reference([row],expected=((0,120),))["value"]
        self.assertEqual(b["range_fraction"],0); self.assertIsNone(b["close_location"])

    def test_invalid_trade_values(self):
        for key,value in [("price",0),("price",-1),("price",float("nan")),("size",0),("size",-1),("size",I64+1)]:
            rows=deepcopy(FIXTURE["trades"]);rows[0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):trade_reference(rows)

    def test_invalid_bars(self):
        for key,value in [("high",99),("volume",-1),("close",float("inf")),("notional",1),("notional",float("nan")),("volume",0)]:
            rows=deepcopy(FIXTURE["bars"]);rows[0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):bar_reference(rows)

    def test_duplicate_and_unordered(self):
        rows=deepcopy(FIXTURE["trades"]);rows[1]["id"]=rows[0]["id"]
        with self.assertRaises(ValueError):trade_reference(rows)
        with self.assertRaises(ValueError):trade_reference(list(reversed(FIXTURE["trades"])))
        with self.assertRaises(ValueError):bar_reference(list(reversed(FIXTURE["bars"])))

    def test_boundary_auction_and_early_close(self):
        event={"id":"a","ts":120,"order":0,"price":100,"size":1,"auction":"close"}
        with self.assertRaises(ValueError):trade_reference([event])
        self.assertEqual(trade_reference([event],closing_auction=True)["count"],1)
        open_event={**event,"ts":0,"auction":"open"}
        self.assertEqual(trade_reference([open_event])["count"],0)
        self.assertEqual(trade_reference([open_event],opening_auction=True)["count"],1)
        event={**event,"ts":60}
        self.assertEqual(trade_reference([event],cutoff=60,close=60,closing_auction=True)["count"],1)
        with self.assertRaises(ValueError):trade_reference([event],cutoff=60,close=120,closing_auction=True)

    def test_partial_cutoff_and_coverage(self):
        self.assertEqual(bar_reference(FIXTURE["bars"][:1],expected=((0,60),),cutoff=60)["value"]["volume"],200)
        self.assertEqual(bar_reference(FIXTURE["bars"][:1])["status"],"incomplete_coverage")
        with self.assertRaises(ValueError):bar_reference(FIXTURE["bars"],cutoff=60)
        with self.assertRaises(ValueError):trade_reference([{**FIXTURE["trades"][0],"ts":61}],cutoff=60)

    def test_windows_alignment_and_conservation(self):
        bars=FIXTURE["bars"]
        self.assertEqual(interval(bars,0,60)[-1]+interval(bars,60,120)[-1],500)
        with self.assertRaises(ValueError):interval(bars,30,90)
        self.assertIsNone(interval(bars[:1],60,120))

    def test_top_k_stable_ties(self):
        rows=deepcopy(FIXTURE["trades"])
        for i,r in enumerate(rows):r.update(size=5,ts=10,order=i)
        self.assertEqual(trade_reference(rows)["top_k"],["t1","t2"])
        rows[1]["order"]=0
        with self.assertRaises(ValueError):trade_reference(rows)

    def test_top_k_bounds_and_target_validation(self):
        self.assertEqual(trade_reference(FIXTURE["trades"],k=1)["top_k"],["t3"])
        self.assertEqual(trade_reference(FIXTURE["trades"],k=100)["top_k"],["t3","t2","t1"])
        for bad_k in (0,-1,1.5,True):
            with self.assertRaises(ValueError):trade_reference([],k=bad_k)
        with self.assertRaises(ValueError):trade_reference([],cutoff=121)

    def test_wide_product_and_overflow(self):
        event={"id":"big","ts":1,"order":0,"price":I64,"size":2}
        self.assertEqual(trade_reference([event])["notional"],I64*2)
        self.assertGreater(trade_reference([event])["notional"],I64)
        with self.assertRaises(ValueError):total([I64,1])

    def test_partition_arithmetic_not_average_of_ratios(self):
        rows=FIXTURE["trades"]
        a,b=trade_reference(rows[:1]),trade_reference(rows[1:])
        all_rows=trade_reference(rows)
        self.assertEqual(a["notional"]+b["notional"],all_rows["notional"])
        self.assertEqual(F(a["notional"]+b["notional"],a["volume"]+b["volume"]),all_rows["vwap"])
        self.assertNotEqual((a["vwap"]+b["vwap"])/2,all_rows["vwap"])
        combined=sorted(rows[:1]+rows[1:],key=lambda r:(-r["size"],r["ts"],r["order"],r["id"]))[:2]
        self.assertEqual([r["id"] for r in combined],all_rows["top_k"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
