#!/usr/bin/env python3
"""Independent recompute harness for the EF4-I contract proposals (stdlib only).

Reads docs/ef4/PATH_EFFICIENCY_CONTRACT_PROPOSAL.json and
docs/ef4/PATH_PROJECTIONS_CONTRACT_PROPOSAL.json, and for EVERY result fixture
re-derives, from the fixture inputs and the contract text alone, the status,
reasons, expected/observed counts, value (exact rational / 90-digit decimal /
integer / bool / decimal128 coefficient), float64, float.hex, acceptance rule
and witnesses, and for EVERY refusal fixture applies the recorded mutation to its
base fixture and checks that an independent admission model raises the recorded
error code. It also checks that every result fixture passes admission.

It shares no code with the scratch builder that wrote the JSON.
Usage: python ef4i_fixture_expand.py [DIR_WITH_JSON]
"""
import copy
import json
import os
import re
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from math import ulp

getcontext().prec = 100

INT64 = 2 ** 63 - 1
DEC128 = 10 ** 38
REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEFAULT_DIR = os.environ.get("EF4_DOCS_DIR") or os.path.join(REPO_ROOT, "docs", "ef4")

FAIL = []


def fail(where, msg):
    FAIL.append("%s: %s" % (where, msg))


class Refused(Exception):
    def __init__(self, code, why=""):
        super().__init__(code)
        self.code = code
        self.why = why


# ------------------------------------------------------------------ reason machinery
ORDER = ["absent_input", "unknown_availability", "future_knowledge", "null_field", "ineligible", "governed_gap",
         "future_market", "partial_universe", "insufficient_history", "no_eligible_observations", "empty_universe",
         "zero_denominator"]
STATUS = dict(absent_input="missing_input", unknown_availability="missing_input", future_knowledge="missing_input",
              null_field="missing_input", ineligible="missing_input", governed_gap="incomplete_coverage",
              future_market="incomplete_coverage", partial_universe="incomplete_coverage",
              insufficient_history="insufficient_history", no_eligible_observations="not_applicable",
              empty_universe="not_applicable", zero_denominator="not_applicable")


def verdict(reasons):
    reasons = sorted(set(reasons))
    for r in ORDER:
        if r in reasons:
            return STATUS[r], reasons
    return "available", reasons


def pow2(d):
    return d > 0 and (d & (d - 1)) == 0


def acceptance_float(fr, log_derived):
    if fr == 0:
        return "exact_plus_zero"
    if log_derived:
        return "tolerance"
    if pow2(fr.denominator) and abs(fr.numerator) < 2 ** 53:
        return "exact_float64"
    return "tolerance"


def dec_ln_ratio(a, b):
    """ln(a/b) for positive integers, exact inputs, 100 digits."""
    return Decimal(a).ln() - Decimal(b).ln()


def dec_of(fr):
    return Decimal(fr.numerator) / Decimal(fr.denominator)


# ------------------------------------------------------------------ outcome constructors
def unavailable(exp, obs, reasons):
    st, rs = verdict(reasons)
    return dict(status=st, reasons=rs, expected=exp, observed=obs, truth=None, witnesses=[])


def available(exp, obs, truth, wit, limit):
    return dict(status="available", reasons=[], expected=exp, observed=obs, truth=truth, witnesses=wit[:limit])


def zero_den(exp, obs):
    return dict(status="not_applicable", reasons=["zero_denominator"], expected=exp, observed=obs, truth=None, witnesses=[])


def T_frac(fr, log=False):
    return ("frac", fr, log)


def T_dec(d):
    return ("dec", d)


# ------------------------------------------------------------------ slot reading
def classify_slot(s, K):
    """-> (reason or None, payload). payload is the row list for a usable slot."""
    if isinstance(s, str):
        return {"absent": "absent_input", "gap": "governed_gap", "null": "null_field",
                "empty": "no_eligible_observations"}[s], None
    if isinstance(s, dict) and "ka" in s:
        if s["ka"] is None:
            return "unknown_availability", None
        if s["ka"] > K:
            return "future_knowledge", None
        return None, s["row"]
    return None, s


# ================================================================== I1  path efficiency
def eval_path(fx, fid):
    p = fx["params"]
    N = p["window"]
    K = fx["K"]
    slots = fx["slots"]
    t = fx["target"] if "target" in fx else len(slots) - 1
    scale = fx["unit"]["scale"]
    full = fx["columns"] == "ohlcv"
    base = t - N
    kind = fid.split(".")[1]
    needs_range = kind in ("true_range_sum", "window_range", "choppiness_fraction")
    reasons = set()
    ok = {}
    for i in range(max(base, 0), t + 1):
        r, row = classify_slot(slots[i], K)
        if r:
            reasons.add(r)
        else:
            ok[i] = row
    obs = len(ok)
    if needs_range and not full:
        # high/low not delivered: only the base slot (close) can be READY
        reasons = {"absent_input"}
        if base >= 0:
            r0, _ = classify_slot(slots[base], K)
            if r0:
                reasons.add(r0)
        obs = 1 if base in ok else 0
    if base < 0:
        reasons.add("insufficient_history")
    if reasons:
        return unavailable(N + 1, obs, reasons)
    cidx = 3 if full else 0
    closes = [ok[i][cidx] for i in range(base, t + 1)]
    steps = [b - a for a, b in zip(closes, closes[1:])]
    path = sum(abs(x) for x in steps)
    net = closes[-1] - closes[0]
    scale_den = 10 ** scale
    if needs_range:
        trs = 0
        pts = [closes[0]]
        for j, i in enumerate(range(base + 1, t + 1)):
            hi, lo = ok[i][1], ok[i][2]
            prev = closes[j]
            trs += max(hi - lo, abs(hi - prev), abs(lo - prev))
            pts += [hi, lo]
        rng = max(pts) - min(pts)
    wit = [t, base] + list(range(base + 1, t))
    wit = ["slot:%d" % i for i in wit]
    lim = p["evidence_limit"]
    if kind == "net_displacement":
        return available(N + 1, obs, T_frac(Fraction(net, scale_den)), wit, lim)
    if kind == "path_length":
        return available(N + 1, obs, T_frac(Fraction(path, scale_den)), wit, lim)
    if kind == "true_range_sum":
        return available(N + 1, obs, T_frac(Fraction(trs, scale_den)), wit, lim)
    if kind == "window_range":
        return available(N + 1, obs, T_frac(Fraction(rng, scale_den)), wit, lim)
    if kind == "efficiency_ratio":
        if path == 0:
            return zero_den(N + 1, obs)
        return available(N + 1, obs, T_frac(Fraction(abs(net), path)), wit, lim)
    if kind == "log_efficiency_ratio":
        if path == 0:
            return zero_den(N + 1, obs)
        num = abs(dec_ln_ratio(closes[-1], closes[0]))
        den = sum((abs(dec_ln_ratio(b, a)) for a, b in zip(closes, closes[1:])), Decimal(0))
        return available(N + 1, obs, T_dec(num / den), wit, lim)
    if kind == "choppiness_fraction":
        if rng == 0:
            return zero_den(N + 1, obs)
        q = Fraction(trs, rng)
        assert 1 <= q <= N, ("bound violated", fx["id"])
        v = dec_ln_ratio(q.numerator, q.denominator) / Decimal(N).ln()
        return available(N + 1, obs, T_dec(v), wit, lim)
    raise AssertionError(fid)


# ================================================================== I2-A  session projection
def eval_session(fx, fid):
    N = fx["params"]["window"]
    K = fx["K"]
    cl = fx["closes"]
    t = fx["target"] if "target" in fx else len(cl) - 1
    kind = fid.split(".")[1]
    span = (N + 1) if kind in ("up_session_fraction", "down_session_fraction") else N
    first = t - span + 1
    reasons = set()
    vals = {}
    for i in range(max(first, 0), t + 1):
        s = cl[i]
        if isinstance(s, str):
            reasons.add({"absent": "absent_input", "gap": "governed_gap", "null": "null_field"}[s])
        elif isinstance(s, dict):
            if s["ka"] is None:
                reasons.add("unknown_availability")
            elif s["ka"] > K:
                reasons.add("future_knowledge")
            else:
                vals[i] = s["row"]
        else:
            vals[i] = s
    obs = len(vals)
    if first < 0:
        reasons.add("insufficient_history")
    if reasons:
        return unavailable(span, obs, reasons)
    lim = fx["params"]["evidence_limit"]
    if kind in ("up_session_fraction", "down_session_fraction"):
        ser = [vals[i] for i in range(t - N, t + 1)]
        pairs = list(zip(ser, ser[1:]))
        n = sum(1 for a, b in pairs if (b > a if kind.startswith("up") else b < a))
        wit = ["slot:%d" % i for i in [t] + list(range(t - N, t))]
        return available(span, obs, T_frac(Fraction(n, N)), wit, lim)
    w = [vals[i] for i in range(t - N + 1, t + 1)]
    wit = ["slot:%d" % i for i in [t] + list(range(t - N + 1, t))]
    last = w[-1]
    if kind == "drawdown_fraction":
        return available(span, obs, T_frac(Fraction(max(w) - last, max(w))), wit, lim)
    if kind == "max_drawdown_fraction":
        best = Fraction(0)
        for i in range(len(w)):
            for j in range(i, len(w)):
                best = max(best, Fraction(w[i] - w[j], w[i]))
        return available(span, obs, T_frac(best), wit, lim)
    if kind == "distance_from_low_fraction":
        return available(span, obs, T_frac(Fraction(last - min(w), min(w))), wit, lim)
    if kind == "close_vs_sma_fraction":
        mean = Fraction(sum(w), N)
        return available(span, obs, T_frac(Fraction(last) / mean - 1), wit, lim)
    if kind == "close_above_sma":
        return available(span, obs, ("bool", Fraction(last) > Fraction(sum(w), N)), wit, lim)
    raise AssertionError(fid)


# ================================================================== I2-B  bar projection
def eval_bars(fx, fid):
    K = fx["K"]
    bars = fx["bars"]
    t = fx["target"] if "target" in fx else len(bars) - 1
    kind = fid.split(".")[1]
    money = "dollar" in kind
    reasons = set()
    got = []
    for i in range(0, t + 1):
        s = bars[i]
        if isinstance(s, str):
            if s == "empty":
                got.append((i, None))  # volume 0, notional 0
                continue
            reasons.add({"absent": "absent_input", "gap": "governed_gap", "null": "null_field"}[s])
            continue
        row = s
        if isinstance(s, dict):
            if s["ka"] is None:
                reasons.add("unknown_availability")
                continue
            if s["ka"] > K:
                reasons.add("future_knowledge")
                continue
            row = s["row"]
        if money and fx["notional_column"] and row[4] > 0 and row[5] is None:
            reasons.add("null_field")
            continue
        got.append((i, row))
    obs = len(got)
    if money and not fx["notional_column"]:
        reasons = {"absent_input"}
        obs = 0
    if reasons:
        return unavailable(t + 1, obs, reasons)

    def vol(r):
        return 0 if r is None else r[4]

    def amt(r):
        return 0 if (r is None or r[5] is None) else r[5]

    def side(r):
        if r is None or r[4] == 0:
            return 0
        return (r[3] > r[0]) - (r[3] < r[0])
    tot_v = sum(vol(r) for _, r in got)
    tot_n = sum(amt(r) for _, r in got)
    up_v = sum(vol(r) for _, r in got if side(r) > 0)
    dn_v = sum(vol(r) for _, r in got if side(r) < 0)
    up_n = sum(amt(r) for _, r in got if side(r) > 0)
    dn_n = sum(amt(r) for _, r in got if side(r) < 0)
    wit = ["bar:%d" % i for i in [t] + list(range(0, t))]
    lim = fx["params"]["evidence_limit"]
    scale = fx["unit"]["scale"]
    N_ = t + 1
    if kind == "up_volume":
        return available(N_, obs, ("int", up_v), wit, lim)
    if kind == "down_volume":
        return available(N_, obs, ("int", dn_v), wit, lim)
    if kind == "up_volume_fraction":
        return zero_den(N_, obs) if tot_v == 0 else available(N_, obs, T_frac(Fraction(up_v, tot_v)), wit, lim)
    if kind == "up_dollar_volume":
        return available(N_, obs, ("dec128", up_n, scale), wit, lim)
    if kind == "down_dollar_volume":
        return available(N_, obs, ("dec128", dn_n, scale), wit, lim)
    if kind == "up_dollar_volume_fraction":
        return zero_den(N_, obs) if tot_n == 0 else available(N_, obs, T_frac(Fraction(up_n, tot_n)), wit, lim)
    raise AssertionError(fid)


# ================================================================== I2-C  relative excess
def find(facts, **kv):
    for f in facts:
        if all(f.get(k) == v for k, v in kv.items()):
            return f
    return None


def fact_state(f, K):
    if f is None:
        return "absent_input"
    if f["ka"] is None:
        return "unknown_availability"
    if f["ka"] > K:
        return "future_knowledge"
    return None


def leg_pair(fx, inst, profile):
    s = find(fx["facts"], inst=inst, kind="start", pf=profile)
    e = find(fx["facts"], inst=inst, kind="end")
    return s, e


def leg_ok(s, e, profile, P, C):
    """True if one leg is individually compatible."""
    if s["act"] != e["act"]:
        return False
    if profile == "prior_close":
        if s["ss"] == e["ss"]:
            return False
    else:
        if s["ss"] != e["ss"]:
            return False
        if abs((e["t"] - s["t"]) - P["window_ns"]) > P["alignment_tolerance_ns"]:
            return False
    if e["t"] <= C and C - e["t"] > P["max_endpoint_age_ns"]:
        return False
    return True


def eval_relative(fx, fid):
    P = fx["params"]
    K, C = fx["K"], fx["C"]
    lim = P["evidence_limit"]
    tol = P["alignment_tolerance_ns"]
    if fid.startswith("core."):
        ids = P["core_benchmark_ids"]
        prof = P["core_profile"]
        elig = []
        for b in ids:
            s, e = leg_pair(fx, b, prof)
            if fact_state(s, K) or fact_state(e, K):
                continue
            if e["t"] > C or not leg_ok(s, e, prof, P, C):
                continue
            elig.append((b, s, e))
        if len(elig) != len(ids):
            return unavailable(len(ids), len(elig), {"partial_universe"})
        ends = [e["t"] for _, _, e in elig]
        starts = [s["t"] for _, s, _ in elig]
        bad = max(ends) - min(ends) > tol
        if prof == "prior_close":
            bad = bad or len({s["ss"] for _, s, _ in elig}) > 1 or len({e["ss"] for _, _, e in elig}) > 1
        else:
            bad = bad or max(starts) - min(starts) > tol or len({e["ss"] for _, _, e in elig}) > 1
        if bad:
            return unavailable(len(ids), len(elig), {"ineligible"})
        rets = [Fraction(e["p"], s["p"]) - 1 for _, s, e in elig]
        wit = []
        for b, _, _ in elig:
            wit += ["leg:%s:start" % b, "leg:%s:end" % b]
        if fid.endswith("agreement_fraction"):
            cnt = [sum(1 for r in rets if r > 0), sum(1 for r in rets if r < 0), sum(1 for r in rets if r == 0)]
            return available(len(ids), len(elig), T_frac(Fraction(max(cnt), len(rets))), wit, lim)
        return available(len(ids), len(elig), T_frac(max(rets) - min(rets)), wit, lim)
    # excess output
    parts = fid.split(".")
    role, what = parts[2], parts[3]
    prof = "prior_close" if what.startswith("prior_close") else "window_start"
    X = fx["instrument"]
    B = P[role + "_benchmark_id"]
    xs, xe = leg_pair(fx, X, prof)
    bs, be = leg_pair(fx, B, prof)
    need = [xs, xe, bs, be]
    mem = None
    if role == "sector":
        mem = find(fx["membership"], inst=X)
        need.append(mem)
    states = [fact_state(f, K) for f in need]
    obs = sum(1 for s in states if s is None)
    miss = {s for s in states if s}
    if miss:
        return unavailable(len(need), obs, miss)
    why = set()
    if xe["t"] > C or be["t"] > C:
        why.add("future_market")
    if not leg_ok(xs, xe, prof, P, C) or not leg_ok(bs, be, prof, P, C):
        why.add("ineligible")
    if abs(xe["t"] - be["t"]) > tol:
        why.add("ineligible")
    if prof == "prior_close":
        if xs["ss"] != bs["ss"] or xe["ss"] != be["ss"]:
            why.add("ineligible")
    else:
        if xe["ss"] != be["ss"] or abs(xs["t"] - bs["t"]) > tol:
            why.add("ineligible")
    if mem is not None and (mem["bound"] != P["sector_benchmark_id"] or mem["eff"] > xe["t"]):
        why.add("ineligible")
    if why:
        return unavailable(len(need), obs, why)
    v = (Fraction(xe["p"]) / xs["p"] - 1) - (Fraction(be["p"]) / bs["p"] - 1)
    wit = ["leg:%s:start" % X, "leg:%s:end" % X, "leg:%s:start" % B, "leg:%s:end" % B]
    if mem is not None:
        wit.append("membership:%s" % X)
    return available(len(need), obs, T_frac(v), wit, lim)


# ================================================================== I2-D  rate projection
def eval_rate(fx, fid):
    P = fx["params"]
    K, C = fx["K"], fx["C"]
    W = P["window_ns"]
    lim = P["evidence_limit"]
    kind = fid.split(".")[2]
    scale = fx["unit"]["scale"]
    secs = Fraction(W, 10 ** 9)
    if kind in ("trade_rate", "notional_rate", "share_volume_rate"):
        k = {"trade_rate": "count", "notional_rate": "notional", "share_volume_rate": "volume"}[kind]
        f = find(fx["tape"], kind=k)
        st = fact_state(f, K)
        if st:
            return unavailable(1, 0, {st})
        why = set()
        if f["e"] > C:
            why.add("future_market")
        if f["e"] - f["s"] != W:
            why.add("ineligible")
        if f["e"] <= C and C - f["e"] > P["max_endpoint_age_ns"]:
            why.add("ineligible")
        if why:
            return unavailable(1, 1, why)
        v = Fraction(f["v"])
        if kind == "notional_rate":
            v = v / 10 ** scale
        return available(1, 1, T_frac(v / secs), ["tape:%s" % k], lim)
    X = fx["instrument"]
    slots = ["A"] if kind == "raw_return_fraction" else ["A", "B"]
    pairs = []
    states = []
    for sl in slots:
        s = find(fx["legs"], inst=X, kind="start", slot=sl)
        e = find(fx["legs"], inst=X, kind="end", slot=sl)
        pairs.append((s, e))
        states += [fact_state(s, K), fact_state(e, K)]
    obs = sum(1 for s in states if s is None)
    miss = {s for s in states if s}
    if miss:
        return unavailable(2 * len(slots), obs, miss)
    why = set()
    for n, (s, e) in enumerate(pairs):
        if e["t"] > C:
            why.add("future_market")
        if s["act"] != e["act"] or s["ss"] != e["ss"] or abs((e["t"] - s["t"]) - W) > P["alignment_tolerance_ns"]:
            why.add("ineligible")
        if n == 0 and e["t"] <= C and C - e["t"] > P["max_endpoint_age_ns"]:
            why.add("ineligible")
    if kind == "return_rate_difference":
        (sa, ea), (sb, eb) = pairs
        if P["adjacency"] == "adjacent":
            if abs(sa["t"] - eb["t"]) > P["alignment_tolerance_ns"]:
                why.add("ineligible")
        elif eb["t"] - sa["t"] > P["alignment_tolerance_ns"]:
            why.add("ineligible")
    if why:
        return unavailable(2 * len(slots), obs, why)
    r = [Fraction(e["p"], s["p"]) - 1 for s, e in pairs]
    if kind == "raw_return_fraction":
        return available(2, obs, T_frac(r[0]), ["leg:%s:start:A" % X, "leg:%s:end:A" % X], lim)
    rate_a, rate_b = r[0] / secs, r[1] / secs
    wit = ["leg:%s:start:A" % X, "leg:%s:end:A" % X, "leg:%s:start:B" % X, "leg:%s:end:B" % X]
    return available(4, obs, T_frac(rate_a - rate_b), wit, lim)


# ------------------------------------------------------------------ comparing recomputed truth with the JSON
def f64_ok(json_float, ref_float, ref_exact_required):
    if ref_exact_required:
        return json_float == ref_float and (json_float != 0 or str(json_float)[0] != "-")
    return abs(json_float - ref_float) <= max(8 * ulp(ref_float), 1e-12 * abs(ref_float))


def compare(where, exp, got, log_hint):
    if exp["status"] != got["status"]:
        return fail(where, "status %s != %s" % (exp["status"], got["status"]))
    if exp["reasons"] != got["reasons"]:
        return fail(where, "reasons %s != %s" % (exp["reasons"], got["reasons"]))
    if exp["expected"] != got["expected"] or exp["observed"] != got["observed"]:
        return fail(where, "counts %s/%s != %s/%s" % (exp["expected"], exp["observed"], got["expected"], got["observed"]))
    if exp["witnesses"] != got["witnesses"]:
        return fail(where, "witnesses %s != %s" % (exp["witnesses"], got["witnesses"]))
    tr = got["truth"]
    v = exp["value"]
    if tr is None:
        if v is not None:
            fail(where, "value present for unavailable output")
        return
    if v is None:
        return fail(where, "value missing")
    kind = tr[0]
    if kind == "int":
        if v != {"exact": str(tr[1]), "acceptance": "exact_integer"}:
            fail(where, "int value %s != %s" % (v, tr[1]))
    elif kind == "dec128":
        if v != {"exact": str(tr[1]), "scale": tr[2], "acceptance": "exact_integer"}:
            fail(where, "decimal128 value %s != %s@%s" % (v, tr[1], tr[2]))
        if tr[1] >= DEC128:
            fail(where, "decimal128 overflow in fixture")
    elif kind == "bool":
        if v != {"exact": tr[1], "acceptance": "exact_bool"}:
            fail(where, "bool value %s != %s" % (v, tr[1]))
    elif kind == "frac":
        fr = tr[1]
        if v["exact"] != "%d/%d" % (fr.numerator, fr.denominator):
            return fail(where, "exact %s != %s" % (v["exact"], fr))
        f = float(fr)
        if v["float64"] != f or v["hex"] != f.hex():
            return fail(where, "float64/hex %r %s != %r %s" % (v["float64"], v["hex"], f, f.hex()))
        acc = acceptance_float(fr, tr[2] or log_hint)
        if v["acceptance"] != acc:
            fail(where, "acceptance %s != %s" % (v["acceptance"], acc))
        if f == 0 and str(v["float64"]).startswith("-"):
            fail(where, "negative zero")
    elif kind == "dec":
        d = tr[1]
        if v.get("exact") is not None:
            ex = Fraction(*[int(x) for x in v["exact"].split("/")])
            if abs(dec_of(ex) - d) > Decimal("1e-70"):
                return fail(where, "logarithmic value %s differs from exact %s" % (d, v["exact"]))
            f = float(ex)
            if v["float64"] != f or v["hex"] != f.hex():
                fail(where, "float64/hex of exact log value")
            acc = acceptance_float(ex, True)
            if v["acceptance"] != acc:
                fail(where, "acceptance %s != %s" % (v["acceptance"], acc))
        else:
            ref = float(d)
            if not f64_ok(v["float64"], ref, False) or v["hex"] != v["float64"].hex():
                fail(where, "irrational float64 %r vs %r" % (v["float64"], ref))
            if abs(Decimal(v["decimal"]) - d) > Decimal("1e-55"):
                fail(where, "decimal60 differs")
            if v["acceptance"] != "tolerance":
                fail(where, "irrational value must be tolerance")
    else:
        fail(where, "unknown truth kind")


# ------------------------------------------------------------------ admission (refusal) model, staged
# Stages (the one refusal precedence order): wire, shared, config, version, identity, data.
STAGES = ["wire", "shared", "config", "version", "identity", "data"]
T0 = 1_700_000_000_000_000_000
D_BAR = 60 * 10 ** 9
D_DAY = 86_400 * 10 ** 9


def is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


class Trig:
    def __init__(self):
        self.t = []

    def add(self, stage, code, why=""):
        self.t.append((stage, code, why))

    def stages(self):
        return {s for s, _, _ in self.t}


def cfg_check(T, p, required, ranges, label):
    have, want = set(p), set(required)
    if have != want:
        T.add("config", "INVALID_CONFIG", "keys %s" % sorted(have ^ want))
    for k, (lo, hi) in ranges.items():
        if k in p and not (is_int(p[k]) and lo <= p[k] <= hi):
            T.add("config", "INVALID_CONFIG", "range " + k)
    if "policy_version" in p:
        if not isinstance(p["policy_version"], str):
            T.add("config", "INVALID_CONFIG", "version type")
        elif p["policy_version"] != label:
            T.add("version", "INCOMPATIBLE_VERSION", p["policy_version"])


def ctx_check(T, ctx, known):
    if ctx["capability"] != "batch":
        T.add("config", "UNSUPPORTED_CAPABILITY")
    for f in ctx["features"]:
        if f not in known:
            T.add("config", "UNKNOWN_FEATURE", f)
    cu = ctx["config_unit"]
    bu = ctx["batch"]["unit"]
    if cu is None or cu["scale"] != bu["scale"] or cu["currency"] != bu["currency"]:
        T.add("config", "INVALID_UNIT")
    if ctx["batch"]["adjustment"] != ctx["config_adjustment"]:
        T.add("config", "UNSUPPORTED_ADJUSTMENT")


def cell_check(T, vals, volume, notional=None, has_notional=False):
    """wire then shared BAR rules for one row; returns True when the row is clean."""
    cells = list(vals) + [volume] + ([notional] if has_notional else [])
    bad = False
    for x in cells:
        if x is None:
            continue
        if not is_int(x):
            T.add("wire", "INVALID_SCHEMA", "cell type")
            bad = True
    for x in list(vals) + [volume]:
        if is_int(x) and abs(x) > INT64:
            T.add("wire", "OVERFLOW", "int64")
            bad = True
    if has_notional and is_int(notional) and abs(notional) >= DEC128:
        T.add("wire", "OVERFLOW", "decimal128")
        bad = True
    if bad:
        return False
    if volume is not None and volume < 0:
        T.add("shared", "BOUNDS", "negative volume")
        return False
    if volume == 0:
        if any(x is not None for x in vals) or (has_notional and notional not in (None, 0)):
            T.add("shared", "INVALID_SCHEMA", "zero volume with prices")
            return False
        return True
    if volume is not None and volume > 0 and any(x is None for x in vals):
        T.add("shared", "INVALID_SCHEMA", "positive volume null price")
        return False
    if any(x is not None and x <= 0 for x in vals):
        T.add("shared", "INVALID_SCHEMA", "nonpositive price")
        return False
    o, h, l, c = vals
    if None not in vals and (h < l or not (l <= o <= h) or not (l <= c <= h)):
        T.add("shared", "INVALID_SCHEMA", "coherence")
        return False
    if has_notional and notional is not None and volume:
        if notional < 0 or (None not in vals and not (l * volume <= notional <= h * volume)):
            T.add("shared", "INVALID_SCHEMA", "notional bounds")
            return False
    return True


def slot_record(i, s, daily, session_reset):
    """default expansion of slot i, overridden by a wire slot; returns (record, payload) or None."""
    if isinstance(s, str):
        return None
    dur = D_DAY if daily else D_BAR
    rec = {"inst": "X", "ss": ("D%d" % i) if daily else "S1", "start": T0 + i * dur, "end": T0 + (i + 1) * dur}
    payload = s
    if isinstance(s, dict) and "wire" in s:
        w = dict(s["wire"])
        payload = w.pop("row")
        rec.update(w)
    elif isinstance(s, dict) and "row" in s:
        payload = s["row"]
    return rec, payload


def series_check(T, slots, daily, row_checker, session_reset=True):
    """shared interval rules and identity rules over the delivered slots."""
    n = len(slots)
    dur = D_DAY if daily else D_BAR
    cutoff = T0 + n * dur
    grid = {(T0 + j * dur, T0 + (j + 1) * dur) for j in range(n)}
    seen, prev_end = set(), {}
    for i, s in enumerate(slots):
        got = slot_record(i, s, daily, session_reset)
        if got is None:
            continue
        rec, payload = got
        before = len(T.t)
        clean = row_checker(payload)
        shared_fault = False
        key = (rec["inst"], rec["ss"]) if daily else (rec["inst"], rec["ss"], rec["start"], rec["end"])
        if key in seen:
            T.add("shared", "DUPLICATE", "interval identity")
            shared_fault = True
        else:
            seen.add(key)
            if rec["start"] >= rec["end"]:
                T.add("shared", "BOUNDS", "start >= end")
                shared_fault = True
            else:
                grp = (rec["inst"],) if daily else (rec["inst"], rec["ss"])
                if grp in prev_end and rec["start"] < prev_end[grp]:
                    T.add("shared", "INVALID_ORDER", "overlap")
                    shared_fault = True
                prev_end[grp] = rec["end"]
                if rec["end"] > cutoff:
                    T.add("shared", "BOUNDS", "after cutoff")
                    shared_fault = True
        if shared_fault or not clean:
            continue
        # identity stage (only for rows that passed wire and shared)
        if rec["inst"] != "X":
            T.add("identity", "INCONSISTENT_IDENTITY", "instrument")
        elif (not daily and rec["ss"] != "S1") or (daily and rec["ss"] not in {"D%d" % j for j in range(n)}):
            T.add("identity", "INCONSISTENT_IDENTITY", "session")
        elif (rec["start"], rec["end"]) not in grid:
            T.add("identity", "INCONSISTENT_IDENTITY", "not a governed slot bound")


def admit_path(o):
    fx, ctx = o["fixture"], o["ctx"]
    T = Trig()
    p = fx["params"]
    ctx_check(T, ctx, {"path.choppiness_fraction", "path.efficiency_ratio", "path.log_efficiency_ratio", "path.net_displacement",
                       "path.path_length", "path.true_range_sum", "path.window_range"})
    cfg_check(T, p, ["policy_version", "window", "epoch_profile", "evidence_limit"],
              {"window": (2, 4096), "evidence_limit": (0, 10000)}, "ef4-path1")
    if "epoch_profile" in p and p["epoch_profile"] not in ("session_reset", "governed_history"):
        T.add("config", "INVALID_CONFIG", "epoch_profile")
    width = 5 if fx["columns"] == "ohlcv" else 1
    daily = p.get("epoch_profile") == "governed_history"

    def rc(payload):
        if not isinstance(payload, list):
            return True
        if len(payload) != width:
            T.add("wire", "INVALID_SCHEMA", "width")
            return False
        if width == 5:
            return cell_check(T, payload[:4], payload[4])
        x = payload[0]
        if not is_int(x):
            T.add("wire", "INVALID_SCHEMA", "cell type")
            return False
        if abs(x) > INT64:
            T.add("wire", "OVERFLOW")
            return False
        if x <= 0:
            T.add("shared", "INVALID_SCHEMA", "nonpositive close")
            return False
        return True
    series_check(T, fx["slots"], daily, rc)
    return T


def admit_session(o):
    fx, ctx = o["fixture"], o["ctx"]
    T = Trig()
    p = fx["params"]
    ctx_check(T, ctx, {"projection.up_session_fraction", "projection.down_session_fraction", "projection.drawdown_fraction",
                       "projection.max_drawdown_fraction", "projection.distance_from_low_fraction",
                       "projection.close_vs_sma_fraction", "projection.close_above_sma"})
    cfg_check(T, p, ["policy_version", "window", "evidence_limit"], {"window": (1, 4096), "evidence_limit": (0, 10000)}, "ef4-proj1")

    def rc(x):
        if isinstance(x, str) or x is None:
            return True
        if not is_int(x):
            T.add("wire", "INVALID_SCHEMA", "cell type")
            return False
        if abs(x) > INT64:
            T.add("wire", "OVERFLOW")
            return False
        if x <= 0:
            T.add("shared", "INVALID_SCHEMA", "nonpositive close")
            return False
        return True
    series_check(T, fx["closes"], True, rc)
    return T


def admit_bars(o):
    fx, ctx = o["fixture"], o["ctx"]
    T = Trig()
    p = fx["params"]
    ctx_check(T, ctx, {"projection.up_volume", "projection.down_volume", "projection.up_volume_fraction",
                       "projection.up_dollar_volume", "projection.down_dollar_volume", "projection.up_dollar_volume_fraction"})
    cfg_check(T, p, ["policy_version", "evidence_limit"], {"evidence_limit": (0, 10000)}, "ef4-proj1")
    clean_rows = []

    def rc(payload):
        if not isinstance(payload, list):
            return True
        if len(payload) != 6:
            T.add("wire", "INVALID_SCHEMA", "width")
            return False
        ok = cell_check(T, payload[:4], payload[4], payload[5], True)
        if ok:
            clean_rows.append(payload)
        return ok
    series_check(T, fx["bars"], False, rc)
    up = sum(r[4] for r in clean_rows if r[4] > 0 and r[3] > r[0])
    dn = sum(r[4] for r in clean_rows if r[4] > 0 and r[3] < r[0])
    if "projection.up_volume" in fx["outputs"] and up > INT64:
        T.add("data", "OVERFLOW", "up_volume sum")
    if "projection.down_volume" in fx["outputs"] and dn > INT64:
        T.add("data", "OVERFLOW", "down_volume sum")
    return T


def fact_wire(T, f, profiles, slots):
    for k in ("inst", "ss", "act", "rev"):
        if not isinstance(f[k], str) or f[k] == "":
            T.add("wire", "INVALID_SCHEMA", k)
    if not is_int(f["t"]):
        T.add("wire", "INVALID_SCHEMA", "t")
    elif abs(f["t"]) > INT64:
        T.add("wire", "OVERFLOW", "t")
    p = f["p"]
    if not is_int(p):
        T.add("wire", "INVALID_SCHEMA", "price type")
    elif abs(p) > INT64:
        T.add("wire", "OVERFLOW", "price")
    elif p <= 0:
        T.add("wire", "INVALID_SCHEMA", "price sign")
    if f["kind"] not in ("start", "end"):
        T.add("wire", "INVALID_SCHEMA", "kind")
    if f["kind"] == "start" and f.get("pf") not in profiles:
        T.add("wire", "INVALID_SCHEMA", "profile")
    if slots is not None and f.get("slot", "A") not in slots:
        T.add("wire", "INVALID_SCHEMA", "slot")


def legs_check(T, facts, declared, profiles, slots):
    seen = set()
    for f in facts:
        fact_wire(T, f, profiles, slots)
    if "wire" in T.stages():
        return
    for f in sorted(facts, key=lambda f: (f["t"], f["kind"])):
        key = (f["inst"], f["kind"], f.get("pf") if f["kind"] == "start" else None, f.get("slot", "A"))
        if key in seen:
            T.add("shared", "DUPLICATE", "reference_id")
        seen.add(key)
    for f in facts:
        if f["inst"] not in declared:
            T.add("identity", "INCONSISTENT_IDENTITY", "undeclared " + str(f["inst"]))
    for s in facts:
        if s["kind"] == "start":
            for e in facts:
                if e["kind"] == "end" and e["inst"] == s["inst"] and e.get("slot", "A") == s.get("slot", "A") and s["t"] >= e["t"]:
                    T.add("data", "BOUNDS", "start >= end")


def admit_relative(o):
    fx, ctx = o["fixture"], o["ctx"]
    T = Trig()
    p = fx["params"]
    known = {"relative.session.%s.%s" % (r, w) for r in ("primary", "secondary", "sector") for w in ("prior_close_excess_fraction", "window_excess_fraction")}
    known |= {"core.benchmark_direction_agreement_fraction", "core.benchmark_return_dispersion_fraction"}
    ctx_check(T, ctx, known)
    outs = [x for x in ctx["features"] if x in known]
    pri = any(".primary." in x for x in outs)
    sec = any(".secondary." in x for x in outs)
    sct = any(".sector." in x for x in outs)
    core = any(x.startswith("core.") for x in outs)
    win = any(x.endswith("window_excess_fraction") for x in outs) or (core and p.get("core_profile") == "window_start")
    req = ["policy_version", "alignment_tolerance_ns", "max_endpoint_age_ns", "evidence_limit"]
    req += ["primary_benchmark_id"] * pri + ["secondary_benchmark_id"] * sec + ["sector_benchmark_id"] * sct
    req += ["window_ns"] * win + ["core_benchmark_ids", "core_profile"] * core
    cfg_check(T, p, req, {"alignment_tolerance_ns": (0, 2 ** 62), "max_endpoint_age_ns": (0, 2 ** 62), "evidence_limit": (0, 10000),
                          "window_ns": (1, 2 ** 62)}, "ef4-rel1")
    bound = []
    for key in ("primary_benchmark_id", "secondary_benchmark_id", "sector_benchmark_id"):
        if key in p:
            if not isinstance(p[key], str) or p[key] == "":
                T.add("config", "INVALID_CONFIG", key)
            else:
                bound.append(p[key])
    ids = p.get("core_benchmark_ids", [])
    if "core_benchmark_ids" in p:
        if not isinstance(ids, list) or not (2 <= len(ids) <= 16) or len(set(ids)) != len(ids) or not all(isinstance(i, str) and i for i in ids):
            T.add("config", "INVALID_CONFIG", "core ids")
            ids = ids if isinstance(ids, list) else []
    if "core_profile" in p and p["core_profile"] not in ("prior_close", "window_start"):
        T.add("config", "INVALID_CONFIG", "core_profile")
    if fx["instrument"] in bound or len(set(bound)) != len(bound):
        T.add("identity", "INCONSISTENT_IDENTITY", "roles")
    declared = set(bound) | {fx["instrument"]} | set(ids)
    legs_check(T, fx["facts"], declared, ("prior_close", "window_start", "regular_open"), None)
    seen = set()
    for m in fx["membership"]:
        if not isinstance(m["bound"], str) or m["bound"] == "":
            T.add("wire", "INVALID_SCHEMA", "membership bound")
        if m["inst"] in seen:
            T.add("identity", "DUPLICATE", "membership")
        seen.add(m["inst"])
        if m["inst"] != fx["instrument"]:
            T.add("identity", "INCONSISTENT_IDENTITY", "membership instrument")
    return T


def admit_rate(o):
    fx, ctx = o["fixture"], o["ctx"]
    T = Trig()
    p = fx["params"]
    ctx_check(T, ctx, {"rate.window.trade_rate", "rate.window.notional_rate", "rate.window.share_volume_rate",
                       "rate.window.raw_return_fraction", "rate.window.return_rate_difference"})
    outs = ctx["features"]
    ret = any(x.endswith(("raw_return_fraction", "return_rate_difference")) for x in outs)
    rd = any(x.endswith("return_rate_difference") for x in outs)
    req = ["policy_version", "window_ns", "max_endpoint_age_ns", "evidence_limit"] + ["alignment_tolerance_ns"] * ret + ["adjacency"] * rd
    cfg_check(T, p, req, {"window_ns": (1, 2 ** 62), "max_endpoint_age_ns": (0, 2 ** 62), "evidence_limit": (0, 10000),
                          "alignment_tolerance_ns": (0, 2 ** 62)}, "ef4-rate1")
    if "adjacency" in p and p["adjacency"] not in ("adjacent", "disjoint"):
        T.add("config", "INVALID_CONFIG", "adjacency")
    kinds = set()
    for f in fx["tape"]:
        if f["kind"] not in ("count", "volume", "notional"):
            T.add("wire", "INVALID_SCHEMA", "tape kind")
            continue
        v = f["v"]
        if isinstance(v, str):
            if not re.fullmatch(r"0|[1-9][0-9]*", v):
                T.add("wire", "INVALID_SCHEMA", "canonical decimal")
                continue
            v = int(v)
        elif not is_int(v) or v < 0:
            T.add("wire", "INVALID_SCHEMA", "operand value")
            continue
        if (f["kind"] == "notional" and v >= DEC128) or (f["kind"] != "notional" and v > INT64):
            T.add("wire", "OVERFLOW", "operand")
            continue
        if f["s"] >= f["e"]:
            T.add("shared", "BOUNDS", "reference bounds")
        if f["kind"] in kinds:
            T.add("shared", "DUPLICATE", "reference_id")
        kinds.add(f["kind"])
    legs_check(T, fx["legs"], {fx["instrument"]}, ("window_start",), ("A", "B"))
    return T


ADMIT = dict(path_efficiency=admit_path, session_projection=admit_session, bar_projection=admit_bars,
             relative_excess=admit_relative, rate_projection=admit_rate)
EVAL = dict(path_efficiency=eval_path, session_projection=eval_session, bar_projection=eval_bars,
            relative_excess=eval_relative, rate_projection=eval_rate)


def default_ctx(fx):
    u = fx["unit"]
    return {"config_unit": dict(u), "batch": {"unit": dict(u), "adjustment": "raw"}, "config_adjustment": "raw",
            "capability": "batch", "features": list(fx["outputs"])}


def set_path(root, path, value=None, delete=False):
    parts = path.split(".")
    cur = root
    for k in parts[:-1]:
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    last = parts[-1]
    if isinstance(cur, list):
        i = int(last)
        if delete:
            del cur[i]
        elif i == len(cur):
            cur.append(value)
        else:
            cur[i] = value
    elif delete:
        del cur[last]
    else:
        cur[last] = value


def run_file(path, fixture_lists, label):
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    byid = {}
    n_fx = n_out = 0
    for key in fixture_lists:
        for fx in doc[key]:
            byid[fx["id"]] = fx
            prod = fx["producer"]
            T = ADMIT[prod]({"fixture": copy.deepcopy(fx), "ctx": default_ctx(fx)})
            if T.t:
                fail(fx["id"], "result fixture refused: %s" % (T.t,))
            if set(fx["expected"]) != set(fx["outputs"]):
                fail(fx["id"], "outputs/expected mismatch")
            for fid in fx["outputs"]:
                got = EVAL[prod](fx, fid)
                compare("%s/%s" % (fx["id"], fid), fx["expected"][fid], got, fid.startswith("path.log") or fid.startswith("path.chop"))
                n_out += 1
            n_fx += 1
    n_ref = 0
    for r in doc["refusal_fixtures"]:
        base = byid.get(r["base"])
        if base is None:
            fail(r["id"], "unknown base %s" % r["base"])
            continue
        if base["producer"] != r["producer"]:
            fail(r["id"], "producer/base mismatch")
        obj = {"fixture": copy.deepcopy(base), "ctx": default_ctx(base)}
        for m in r["mutation"]:
            if "set" in m:
                set_path(obj, m["set"], m["value"])
            else:
                set_path(obj, m["del"], delete=True)
        T = ADMIT[r["producer"]](obj)
        codes = sorted({c for _, c, _ in T.t})
        if codes != [r["error_code"]]:
            fail(r["id"], "triggers %s, recorded %s" % (sorted(set(T.t)), r["error_code"]))
        else:
            first = min(T.stages(), key=STAGES.index)
            if first != r["stage"]:
                fail(r["id"], "first stage %s, recorded %s" % (first, r["stage"]))
            if T.stages() != {r["stage"]}:
                fail(r["id"], "faults in several stages %s" % sorted(T.stages()))
        n_ref += 1
    declared = doc["fixture_counts"]
    tot_decl = sum(declared.values()) - declared["refusal"]
    if tot_decl != n_fx or declared["refusal"] != n_ref:
        fail(label, "declared fixture_counts %s but found %d result, %d refusal" % (declared, n_fx, n_ref))
    print("%s: %d result fixtures (%d outputs), %d refusal fixtures" % (label, n_fx, n_out, n_ref))
    return n_fx, n_out, n_ref


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    a = run_file(os.path.join(d, "PATH_EFFICIENCY_CONTRACT_PROPOSAL.json"), ["path_fixtures"], "I1 path efficiency")
    b = run_file(os.path.join(d, "PATH_PROJECTIONS_CONTRACT_PROPOSAL.json"),
                 ["session_fixtures", "bar_fixtures", "relative_fixtures", "rate_fixtures"], "I2 projections")
    print("TOTAL: %d result fixtures, %d outputs, %d refusals" % (a[0] + b[0], a[1] + b[1], a[2] + b[2]))
    if FAIL:
        print("FAILURES (%d):" % len(FAIL))
        for f in FAIL:
            print(" -", f)
        sys.exit(1)
    print("ALL FIXTURES AND REFUSALS RECOMPUTED AND MATCHED")


if __name__ == "__main__":
    main()
