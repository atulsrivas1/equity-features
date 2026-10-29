#!/usr/bin/env python3
"""Independent recompute harness for the DV1 definition-variants contract proposal (stdlib only).

Reads docs/dv1/DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json. For EVERY result fixture (ATR, window extremes, log
relative statistics, core spread, range over open) it re-derives status, reasons, expected/observed counts, the value
(exact rational, 250-digit logarithm/root value, or int), float64 and float.hex, the acceptance class and the
witnesses from the fixture inputs and the contract text. It also recomputes every wrong-convention rival value, the
window-extreme prior-high cross-check, the V12a consumer binding, the equality with the frozen EF4 range fixtures
(read only), the exact-identity claims and the near-tie distance of every irrational value from a float64 midpoint.
Every result fixture must pass the admission model; for EVERY refusal fixture the recorded mutation is applied to the
base fixture and the admission model must report exactly one fault, equal to the recorded stage and error code.

Nothing here is taken from any library: there is none. Logarithms use an own atanh series on big integers, roots use
integer square roots, and the formulation (state tables, deviation form of the variance, reversed scans for ties)
differs on purpose from the scratch builder that wrote the JSON; it shares no code with it.
Usage: python dv1_fixture_expand.py [PATH_TO_CONTRACT_JSON]
"""
import copy
import json
import math
import os
import re
import sys
from decimal import Decimal
from fractions import Fraction

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEFAULT = os.path.join(os.environ.get("DV1_DOCS_DIR") or os.path.join(REPO_ROOT, "docs", "dv1"),
                       "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json")
EF4 = os.path.join(REPO_ROOT, "docs", "ef4", "PATH_PROJECTIONS_CONTRACT_PROPOSAL.json")
KCUT = 100
INT64 = 2 ** 63 - 1
FAIL = []
PRECEDENCE = ["absent_input", "unknown_availability", "future_knowledge", "null_field", "ineligible", "governed_gap",
              "future_market", "partial_universe", "insufficient_history", "no_eligible_observations", "zero_denominator"]
STATUS = {"absent_input": "missing_input", "unknown_availability": "missing_input", "future_knowledge": "missing_input",
          "null_field": "missing_input", "ineligible": "missing_input", "governed_gap": "incomplete_coverage",
          "future_market": "incomplete_coverage", "partial_universe": "incomplete_coverage",
          "insufficient_history": "insufficient_history", "no_eligible_observations": "not_applicable",
          "zero_denominator": "not_applicable"}
OUTPUTS = {
    "atr_simple_mean": ["history.atr_simple_mean"],
    "window_extreme": ["history.window_high", "history.window_high_offset", "history.window_low", "history.window_low_offset"],
    "relative_log_stats": ["relative.log_return_beta", "relative.log_return_correlation"],
    "core_spread": ["core.benchmark_return_range_fraction", "core.benchmark_return_stdev_fraction"],
    "session_range_over_open": ["session.price.range_over_open"],
}
POLICY = {"atr_simple_mean": "dv1-atrs1", "window_extreme": "dv1-wext1", "relative_log_stats": "dv1-rlog1", "core_spread": "dv1-core1"}


def fail(where, msg):
    FAIL.append("%s: %s" % (where, msg))


# ------------------------------------------------------------------ high precision logarithm and root
DIG = 270
SC = 10 ** DIG


def _atanh_scaled(z):
    """atanh(z) * SC for a Fraction |z| <= 1/3, by the odd power series on integers."""
    sign = -1 if z < 0 else 1
    z = abs(z)
    zs = z.numerator * SC // z.denominator
    z2 = zs * zs // SC
    term, total, k = zs, 0, 0
    while term:
        total += term // (2 * k + 1)
        term = term * z2 // SC
        k += 1
    return sign * total


LN2 = 2 * _atanh_scaled(Fraction(1, 3))


def ln_exact(q):
    """natural log of a positive Fraction as a Fraction approximating it to about 1e-265."""
    q = Fraction(q)
    e = q.numerator.bit_length() - q.denominator.bit_length()
    m = q / Fraction(2) ** e if e >= 0 else q * Fraction(2) ** (-e)
    z = (m - 1) / (m + 1)
    return Fraction(e * LN2 + 2 * _atanh_scaled(z), SC)


def sqrt_exact(v):
    v = Fraction(v)
    return Fraction(math.isqrt(v.numerator * SC * SC // v.denominator), SC)


def to_float(q):
    return float(Fraction(q))


def midpoint_distance_ok(q):
    """relative distance of q from the midpoints of the two float64 neighbours of its rounding is >= 1e-60."""
    f = float(q)
    for g in (math.nextafter(f, -math.inf), math.nextafter(f, math.inf)):
        mid = (Fraction(f) + Fraction(g)) / 2
        if abs(q - mid) < abs(q) * Fraction(1, 10 ** 60):
            return False
    return True


# ------------------------------------------------------------------ slots
def split(slot):
    if isinstance(slot, dict):
        return slot["row"], (slot["ka"] if "ka" in slot else 50)
    return slot, 50


TOKEN_CAUSE = {"absent": "absent_input", "gap": "governed_gap", "forming": "future_market"}


def cause(slot, need):
    body, ka = split(slot)
    if isinstance(body, str):
        return TOKEN_CAUSE[body]
    if ka is None:
        return "unknown_availability"
    if ka > KCUT:
        return "future_knowledge"
    if body is None:
        return "null_field"
    if isinstance(body, list) and any(body[i] is None for i in need):
        return "null_field"
    return None


def rows_of(fx):
    if "slots_fill" in fx:
        sf = fx["slots_fill"]
        rows = [list(sf["base"]) for _ in range(sf["n"])]
        for k, v in sf["set"].items():
            rows[int(k)] = v
        return rows
    return fx["slots"]


def values_of(slot):
    return split(slot)[0]


def decide(reasons):
    for r in PRECEDENCE:
        if r in reasons:
            return STATUS[r]
    return "available"


def rat_value(q):
    q = Fraction(q)
    f = float(q)
    if q == 0:
        acc = "exact_plus_zero"
    elif q.denominator & (q.denominator - 1) == 0 and abs(q.numerator) < 2 ** 53:
        acc = "exact_float64"
    else:
        acc = "correctly_rounded"
    return {"exact": "%d/%d" % (q.numerator, q.denominator), "float64": f, "hex": f.hex(), "acceptance": acc, "_q": q}


def irr_value(q):
    f = float(q)
    return {"float64": f, "hex": f.hex(), "acceptance": "decimal_correctly_rounded", "_q": q}


def result(reasons, expected, observed, value, wit, limit, basis=None):
    reasons = sorted(set(reasons))
    out = {"status": "available" if value is not None else decide(reasons), "reasons": reasons, "expected": expected,
           "observed": observed, "value": value, "witnesses": wit[:limit] if value is not None else []}
    if basis is not None:
        out["basis"] = basis
    return out


def target_index(fx, n):
    return fx["target"] if "target" in fx else n - 1


# ------------------------------------------------------------------ ATR
def tr_sum(rows, t, n):
    total = 0
    for i in range(t - n + 1, t + 1):
        h, l, pc = rows[i][0], rows[i][1], rows[i - 1][2]
        total += max(h - l, abs(h - pc), abs(l - pc))
    return total


def wilder(rows, t, n):
    trs = [tr_sum(rows, i, 1) for i in range(1, t + 1)]
    avg = Fraction(sum(trs[:n]), n)
    for x in trs[n:]:
        avg = (avg * (n - 1) + x) / n
    return avg


def eval_atr(fx):
    slots = rows_of(fx)
    t = target_index(fx, len(slots))
    n = fx["params"]["period"]
    lim = fx["params"]["evidence_limit"]
    reasons, ready = set(), 0
    for i in range(t - n, t + 1):
        if i < 0:
            reasons.add("insufficient_history")
            continue
        need = (2,) if i == t - n else ((0, 1) if i == t else (0, 1, 2))
        c = cause(slots[i], need)
        if c:
            reasons.add(c)
        else:
            ready += 1
    value, wit = None, []
    if not reasons:
        rows = [values_of(s) for s in slots]
        value = rat_value(Fraction(tr_sum(rows, t, n), n * 10 ** fx["unit"]["scale"]))
        wit = ["slot:%d" % i for i in [t] + list(range(t - n, t))]
    return {"history.atr_simple_mean": result(reasons, n + 1, ready, value, wit, lim, fx["adjustment"])}


# ------------------------------------------------------------------ window extremes
def eval_wx(fx):
    slots = rows_of(fx)
    t = target_index(fx, len(slots))
    p = fx["params"]["period"]
    close = fx["params"]["extreme_basis"] == "close"
    lim = fx["params"]["evidence_limit"]
    out = {}
    for name in OUTPUTS["window_extreme"]:
        col = 2 if close else (0 if "high" in name else 1)
        reasons, ready, seen = set(), 0, {}
        for i in range(t - p + 1, t + 1):
            if i < 0:
                reasons.add("insufficient_history")
                continue
            c = cause(slots[i], (col,))
            if c:
                reasons.add(c)
            else:
                ready += 1
                seen[i] = values_of(slots[i])[col]
        value, wit = None, []
        if not reasons:
            best, best_i = None, None
            for i in range(t, t - p, -1):          # scan newest first: strict improvement keeps the latest on ties
                v = seen[i]
                if best is None or (v > best if "high" in name else v < best):
                    best, best_i = v, i
            wit = ["slot:%d" % i for i in [t] + list(range(t - p + 1, t))]
            value = {"int": t - best_i, "acceptance": "exact_integer"} if name.endswith("offset") \
                else rat_value(Fraction(best, 10 ** fx["unit"]["scale"]))
        out[name] = result(reasons, p, ready, value, wit, lim, fx["adjustment"])
    return out


def window_pick(rows, t, p, col, high, latest=True):
    seq = [(rows[i][col], i) for i in range(t - p + 1, t + 1)]
    best = max(v for v, _ in seq) if high else min(v for v, _ in seq)
    idx = [i for v, i in seq if v == best]
    return best, (max(idx) if latest else min(idx))


# ------------------------------------------------------------------ relative log
def eval_rl(fx, want_parts=False):
    p = fx["params"]
    w, minp, lim = p["window"], p["min_pairs"], p["evidence_limit"]
    inst, bench = fx["inst"], fx["bench"]
    length = len(inst) if isinstance(inst, list) else len(bench)
    t = target_index(fx, length)

    def why(series, i):
        return "absent_input" if series == "absent" else cause(series[i], ())

    reasons, good = set(), []
    for j in range(max(t - w + 1, 1), t + 1):
        lost = {c for s in (inst, bench) for c in (why(s, j - 1), why(s, j)) if c}
        if lost:
            reasons |= lost
        else:
            good.append(j)
    if t - w < 0:
        reasons.add("insufficient_history")
    n = len(good)
    names = OUTPUTS["relative_log_stats"]
    if n < minp or t - w < 0:
        return {k: result(reasons, w, n, None, [], lim, fx["adjustment"]) for k in names}
    ratios_x = [Fraction(values_of(inst[j]), values_of(inst[j - 1])) for j in good]
    ratios_y = [Fraction(values_of(bench[j]), values_of(bench[j - 1])) for j in good]
    var_y_zero = len(set(ratios_y)) == 1
    var_x_zero = len(set(ratios_x)) == 1
    xs = [ln_exact(q) for q in ratios_x]
    ys = [ln_exact(q) for q in ratios_y]
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((b - my) ** 2 for b in ys)
    syy = sum((a - mx) ** 2 for a in xs)
    used = sorted({k for j in good for k in (j - 1, j)})
    order = ([t] if t in used else []) + [k for k in used if k != t]
    wit = [("instrument/slot:%d" % k) if s == 0 else ("benchmark/slot:%d" % k) for k in order for s in (0, 1)]
    out = {}
    if var_y_zero:
        out[names[0]] = result(reasons | {"zero_denominator"}, w, n, None, [], lim, fx["adjustment"])
    elif var_x_zero:
        out[names[0]] = result(reasons, n, n, rat_value(0), wit, lim, fx["adjustment"])
    else:
        out[names[0]] = result(reasons, n, n, irr_value(sxy / sxx), wit, lim, fx["adjustment"])
    if var_y_zero or var_x_zero:
        out[names[1]] = result(reasons | {"zero_denominator"}, w, n, None, [], lim, fx["adjustment"])
    else:
        out[names[1]] = result(reasons, n, n, irr_value(sxy / sqrt_exact(sxx * syy)), wit, lim, fx["adjustment"])
    if want_parts:
        return out, good
    return out


def simple_rel(fx, good):
    inst, bench = fx["inst"], fx["bench"]
    a = [Fraction(values_of(inst[j]), values_of(inst[j - 1])) - 1 for j in good]
    b = [Fraction(values_of(bench[j]), values_of(bench[j - 1])) - 1 for j in good]
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sxy = sum((u - ma) * (v - mb) for u, v in zip(a, b))
    sxx = sum((v - mb) ** 2 for v in b)
    syy = sum((u - ma) ** 2 for u in a)
    return sxy, sxx, syy


# ------------------------------------------------------------------ core spread
def fund_returns(fx, start_key=None):
    """(eligible ids, returns by id, facts by id); start_key substitutes a decoy start price."""
    pr = fx["params"]
    cutoff = fx["C"]
    book = {}
    for f in fx["facts"]:
        book.setdefault(f["inst"], {})[f["kind"]] = f
    good, rets = [], {}
    for b in pr["core_benchmark_ids"]:
        s, e = book.get(b, {}).get("start"), book.get(b, {}).get("end")
        if s is None or e is None:
            continue
        if any(f["ka"] is None or f["ka"] > KCUT for f in (s, e)):
            continue
        if not (e["t"] <= cutoff and cutoff - e["t"] <= pr["max_endpoint_age_ns"] and s["act"] == e["act"]):
            continue
        prof = pr["core_profile"]
        if prof == "prior_close" and not (s["pf"] == prof and s["ss"] != e["ss"]):
            continue
        if prof == "window_start" and not (s["pf"] == prof and s["ss"] == e["ss"] and
                                           abs(e["t"] - s["t"] - pr["window_ns"]) <= pr["alignment_tolerance_ns"]):
            continue
        if prof == "regular_open" and not (s["pf"] == prof and s.get("op") == "daily_bar_open" and s["ss"] == e["ss"]):
            continue
        good.append(b)
        base = s["p"] if start_key is None else fx["decoys"][b][start_key]
        rets[b] = Fraction(e["p"], base) - 1
    return good, rets, book


def spread_values(rets, ids):
    r = [rets[b] for b in ids]
    k = len(r)
    mean = sum(r) / k
    var = sum((x - mean) ** 2 for x in r) / k
    rng = max(r) - min(r)
    n, d = var.numerator, var.denominator
    if var == 0:
        sd = rat_value(0)
    elif math.isqrt(n) ** 2 == n and math.isqrt(d) ** 2 == d:
        sd = rat_value(Fraction(math.isqrt(n), math.isqrt(d)))
    else:
        sd = irr_value(sqrt_exact(var))
    return rat_value(rng), sd


def eval_cs(fx):
    pr = fx["params"]
    ids = pr["core_benchmark_ids"]
    lim = pr["evidence_limit"]
    good, rets, book = fund_returns(fx)
    names = OUTPUTS["core_spread"]
    k = len(ids)
    reasons = set()
    if not fx["facts"]:
        reasons.add("absent_input")
    elif len(good) < k:
        reasons.add("partial_universe")
    else:
        ends = [book[b]["end"]["t"] for b in ids]
        starts = [book[b]["start"]["t"] for b in ids]
        tol = pr["alignment_tolerance_ns"]
        prof = pr["core_profile"]
        if max(ends) - min(ends) > tol or len({book[b]["end"]["ss"] for b in ids}) != 1:
            reasons.add("ineligible")
        elif prof == "window_start" and max(starts) - min(starts) > tol:
            reasons.add("ineligible")
        elif prof in ("prior_close", "regular_open") and len({book[b]["start"]["ss"] for b in ids}) != 1:
            reasons.add("ineligible")
    if reasons:
        return {n: result(reasons, k, len(good), None, [], lim) for n in names}
    rng, sd = spread_values(rets, ids)
    wit = ["leg:%s:%s" % (b, kind) for b in ids for kind in ("start", "end")]
    return {names[0]: result((), k, k, rng, wit, lim), names[1]: result((), k, k, sd, wit, lim)}


# ------------------------------------------------------------------ range over open
def eval_ro(fx):
    lim = fx["params"]["evidence_limit"]
    name = "session.price.range_over_open"
    if fx["trades"] == "absent":
        return {name: result({"absent_input"}, 1, 0, None, [], lim)}
    live = [(p, s) for p, s in fx["trades"] if s > 0]
    if not live:
        return {name: result({"no_eligible_observations"}, 1, 0, None, [], lim)}
    prices = [p for p, _ in live]
    return {name: result((), 1, 1, rat_value(Fraction(max(prices) - min(prices), prices[0])), ["session:S1"], lim)}


def ro_modes(fx):
    """update/restore/merge: reduce each chunk, merge the reductions, compare with the batch reduction."""
    live = [(p, s) for p, s in fx["trades"] if s > 0]

    def reduce(chunk):
        c = [p for p, s in chunk if s > 0]
        return (c[0], max(c), min(c)) if c else None
    parts = [reduce(fx["trades"][a:b]) for a, b in fx["chunks"]]
    parts = [x for x in parts if x]
    o = parts[0][0]
    h = max(x[1] for x in parts)
    l = min(x[2] for x in parts)
    whole = reduce(fx["trades"])
    return Fraction(h - l, o) == Fraction(whole[1] - whole[2], whole[0])


# ------------------------------------------------------------------ comparison
def compare_value(where, got, want):
    if (got is None) != (want is None):
        fail(where, "value presence differs")
        return
    if got is None:
        return
    identity = "exact" in want and "exact" not in got
    for key in ("float64", "hex", "acceptance"):
        if identity and key == "acceptance":
            continue
        if key in want and want[key] != got.get(key):
            fail(where, "%s: fixture %r recomputed %r" % (key, want[key], got.get(key)))
    if "int" in want:
        if want["int"] != got.get("int"):
            fail(where, "int differs")
        return
    q = got["_q"]
    if "exact" in want and "exact" not in got:
        if abs(q - Fraction(want["exact"])) > Fraction(1, 10 ** 200):
            fail(where, "identity %s not reproduced to 1e-200" % want["exact"])
    elif "exact" in want:
        if want["exact"] != got["exact"]:
            fail(where, "exact: fixture %s recomputed %s" % (want["exact"], got["exact"]))
    else:
        d = Fraction(Decimal(want["decimal"]))
        if abs(d - q) > abs(q) * Fraction(1, 10 ** 45):
            fail(where, "decimal differs from the 270-digit recompute")
        if not midpoint_distance_ok(q):
            fail(where, "value within 1e-60 of a float64 midpoint (near-tie rule)")


def compare(fx, got):
    for name, want in fx["expected"].items():
        g = got.get(name)
        where = "%s %s" % (fx["id"], name)
        if g is None:
            fail(where, "not recomputed")
            continue
        for key in ("status", "reasons", "expected", "observed", "witnesses"):
            if want[key] != g[key]:
                fail(where, "%s: fixture %r recomputed %r" % (key, want[key], g[key]))
        if want.get("basis") != g.get("basis"):
            fail(where, "basis echo differs")
        compare_value(where, g["value"], want["value"])
        if (want["value"] is None) != (want["status"] != "available"):
            fail(where, "value null exactly when not available is violated")
        if want["status"] != "available" and not want["reasons"]:
            fail(where, "unavailable without a reason")
    if set(fx["expected"]) != set(fx["outputs"]):
        fail(fx["id"], "outputs and expected differ")
    if "joint_evidence" in fx:
        # evidence_limit bounds the combined list of a joint call: outputs in lexical order, then truncated.
        lim = fx["params"]["evidence_limit"]
        flat = [w for name in sorted(fx["outputs"]) for w in got[name]["witnesses"]]
        full = [w for name in sorted(fx["outputs"]) for w in fx["expected"][name]["witnesses"]]
        if fx["joint_evidence"] != flat[:lim] or len(fx["joint_evidence"]) != lim or lim >= len(full):
            fail(fx["id"], "joint_evidence differs from the recomputed combined list or does not cut mid-list")


# ------------------------------------------------------------------ wrong conventions and cross checks
def rival_check(doc):
    count = 0
    for fx in doc["atr_fixtures"]:
        got = eval_atr(fx)["history.atr_simple_mean"]["value"]
        slots = rows_of(fx)
        t = target_index(fx, len(slots))
        n = fx["params"]["period"]
        sc = 10 ** fx["unit"]["scale"]
        rows = [values_of(s) for s in slots]
        for w in fx.get("wrong_convention", []):
            c = w["convention"]
            if c == "wilder_atr":
                v = wilder(rows, t, n) / sc
            elif c == "prior_only_mean":
                v = Fraction(tr_sum(rows, t - 1, n), n * sc)
            else:
                v = Fraction(sum(rows[i][0] - rows[i][1] for i in range(t - n + 1, t + 1)), n * sc)
            if "%d/%d" % (v.numerator, v.denominator) != w["exact"]:
                fail(fx["id"], "rival %s: recomputed %s fixture %s" % (c, v, w["exact"]))
            same = v == got["_q"]
            if same != (fx["id"] in ("AT02", "AT04") and c == "wilder_atr"):
                fail(fx["id"], "rival %s equality with the id value is %s" % (c, same))
            count += 1
        if "consumer_binding" in fx:
            b = fx["consumer_binding"]
            closes = [r[2] for r in rows]
            sma = Fraction(sum(closes[t - 19:t + 1]), 20)
            sma_p = Fraction(sum(closes[t - 20:t]), 20)
            atr = got["_q"]
            atr_p = Fraction(tr_sum(rows, t - 1, n), n)
            checks = {"sma_inclusive_exact": sma, "prior_only_sma_exact": sma_p, "prior_only_atr_exact": atr_p,
                      "multiple_exact": (closes[t] - sma) / atr, "prior_only_multiple_exact": (closes[t] - sma_p) / atr_p}
            for key, v in checks.items():
                if b[key] != "%d/%d" % (v.numerator, v.denominator):
                    fail(fx["id"], "consumer binding %s: recomputed %s fixture %s" % (key, v, b[key]))
            if closes[t] != b["target_close"]:
                fail(fx["id"], "target_close")
    for fx in doc["window_fixtures"]:
        slots = rows_of(fx)
        t = target_index(fx, len(slots))
        p = fx["params"]["period"]
        sc = 10 ** fx["unit"]["scale"]
        rows = [values_of(s) for s in slots]
        got = eval_wx(fx)
        for w in fx.get("wrong_convention", []):
            c, out = w["convention"], w["output"]
            high = "high" in out
            basis = fx["params"]["extreme_basis"]
            pp = p
            if c == "close_basis":
                basis = "close"
            elif c == "intraday_basis":
                basis = "intraday"
            elif c == "period_plus_one":
                pp = p + 1
            elif c == "period_252":
                pp = 252
            elif c == "period_253":
                pp = 253
            col = 2 if basis == "close" else (0 if high else 1)
            best, idx = window_pick(rows, t, pp, col, high, latest=(c != "earliest_wins"))
            if "int" in w:
                ok = w["int"] == t - idx
                mine = got[out]["value"]["int"]
                same = mine == t - idx
            else:
                v = Fraction(best, sc)
                ok = w["exact"] == "%d/%d" % (v.numerator, v.denominator)
                same = v == got[out]["value"]["_q"]
            if not ok:
                fail(fx["id"], "rival %s does not match its recorded value" % c)
            if same:
                fail(fx["id"], "rival %s equals the value of the id" % c)
            count += 1
        if "cross_check" in fx:
            pp = fx["cross_check"]["prior_period"]
            if fx["params"]["extreme_basis"] != "intraday" or pp != p - 1:
                fail(fx["id"], "cross_check needs the intraday basis and prior_period = period - 1")
            prior_high = max(rows[i][0] for i in range(t - pp, t))
            prior_low = min(rows[i][1] for i in range(t - pp, t))
            if max(prior_high, rows[t][0]) * 1 != got["history.window_high"]["value"]["_q"] * sc:
                fail(fx["id"], "max(prior_high, current high) differs from history.window_high")
            if min(prior_low, rows[t][1]) != got["history.window_low"]["value"]["_q"] * sc:
                fail(fx["id"], "min(prior_low, current low) differs from history.window_low")
            count += 1
    for fx in doc["relative_log_fixtures"]:
        out, good = eval_rl(fx, True) if True else None
        if "wrong_convention" in fx:
            sxy, sxx, syy = simple_rel(fx, good)
            beta_s = sxy / sxx
            rho_s = sxy / sqrt_exact(sxx * syy)
            beta_l, rho_l = out["relative.log_return_beta"]["value"]["_q"], out["relative.log_return_correlation"]["value"]["_q"]
            w0, w1 = fx["wrong_convention"]
            if w0["exact"] != "%d/%d" % (beta_s.numerator, beta_s.denominator):
                fail(fx["id"], "simple beta rival differs")
            if abs(Fraction(Decimal(w1["decimal"])) - rho_s) > abs(rho_s) * Fraction(1, 10 ** 45):
                fail(fx["id"], "simple correlation rival differs")
            if abs(beta_l - beta_s) < abs(beta_l) / 1000:
                fail(fx["id"], "simple and log beta agree to three digits: not a wrong-convention fixture")
            count += 2
        if "identity" in fx["tags"]:
            for name, want in fx["expected"].items():
                v = want["value"]
                if v is not None and v["acceptance"] == "correctly_rounded":
                    q = out[name]["value"]["_q"]
                    if abs(q - Fraction(v["exact"])) > Fraction(1, 10 ** 200):
                        fail(fx["id"], "%s: identity %s not reproduced to 1e-200" % (name, v["exact"]))
                    count += 1
    ef4 = json.load(open(EF4, encoding="utf-8"))["relative_fixtures"]
    ef4_by = {f["id"]: f for f in ef4}
    for fx in doc["core_spread_fixtures"]:
        good, rets, book = fund_returns(fx)
        for w in fx.get("wrong_convention", []):
            c = w["convention"]
            ids = fx["params"]["core_benchmark_ids"]
            rng, sd = spread_values(rets, ids)
            if c == "range_instead_of_stdev":
                rival, mine, field = rng, sd, "exact"
            elif c == "stdev_instead_of_range":
                rival, mine = sd, rng
            else:
                key = {"first_trade_operand": "first_trade_price", "first_bar_open_operand": "first_bar_open",
                       "prior_close_basis": "prior_close"}[c]
                _, r2, _ = fund_returns(fx, key)
                rival, mine = spread_values(r2, ids)[1], sd
            if "exact" in w and w["exact"] is not None:
                if "_q" not in rival or w["exact"] != "%d/%d" % (rival["_q"].numerator, rival["_q"].denominator):
                    fail(fx["id"], "rival %s exact differs" % c)
            else:
                if abs(Fraction(Decimal(w["decimal"])) - rival["_q"]) > abs(rival["_q"]) * Fraction(1, 10 ** 45):
                    fail(fx["id"], "rival %s decimal differs" % c)
            if rival["_q"] == mine["_q"]:
                fail(fx["id"], "rival %s equals the id value" % c)
            count += 1
        if "ef4_reference" in fx:
            ref = ef4_by[fx["ef4_reference"]["fixture"]]
            old = ref["expected"][fx["ef4_reference"]["old_id"]]["value"]["exact"]
            mine = fx["expected"][fx["ef4_reference"]["equals"]]["value"]["exact"]
            if old != mine:
                fail(fx["id"], "EF4 %s: deprecated id publishes %s, range output %s" % (ref["id"], old, mine))
            if ref["facts"] != fx["facts"] or ref["params"]["core_benchmark_ids"] != fx["params"]["core_benchmark_ids"]:
                fail(fx["id"], "inputs are not the EF4 inputs")
            count += 1
    for fx in doc["range_over_open_fixtures"]:
        for w in fx.get("wrong_convention", []):
            live = [p for p, s in fx["trades"] if s > 0]
            den = fx["official_daily_open"] if w["convention"] == "daily_bar_open_operand" else live[-1]
            v = Fraction(max(live) - min(live), den)
            if w["exact"] != "%d/%d" % (v.numerator, v.denominator):
                fail(fx["id"], "close-denominator rival differs")
            if v == eval_ro(fx)["session.price.range_over_open"]["value"]["_q"] and v != 0:
                fail(fx["id"], "rival equals the id value")
            count += 1
        if "chunks" in fx and not ro_modes(fx):
            fail(fx["id"], "update/merge reduction differs from batch")
    return count


# ------------------------------------------------------------------ admission model (single-fault audit)
def is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def faults(fx):
    """every (stage, code) the independent admission model finds in a fixture."""
    out = []
    prod = fx["producer"]
    pr = fx.get("params", {})

    def add(stage, code):
        out.append((stage, code))

    # --- config
    if prod != "session_range_over_open":
        if "adjustment" not in fx and prod in ("atr_simple_mean", "window_extreme", "relative_log_stats"):
            add("config", "INVALID_CONFIG")
        elif prod in ("atr_simple_mean", "window_extreme", "relative_log_stats"):
            adj, spec = fx["adjustment"], fx.get("adjustment_spec", {})
            pair = {"unadjusted": "raw-v1", "split_adjusted": "split-factors-v1"}
            if adj not in pair or spec.get("policy_version") != pair[adj]:
                add("config", "UNSUPPORTED_ADJUSTMENT")
            elif adj == "split_adjusted" and not (spec.get("action_snapshot") and spec.get("anchor")):
                add("config", "UNSUPPORTED_ADJUSTMENT")
    unit = fx.get("unit", {})
    if not (isinstance(unit.get("currency"), str) and re.fullmatch(r"[A-Z]{3}", unit["currency"])
            and is_int(unit.get("scale")) and 0 <= unit["scale"] <= 18):
        add("config", "INVALID_UNIT")
    if not fx.get("outputs"):
        add("config", "INVALID_CONFIG")
    elif any(o not in OUTPUTS[prod] for o in fx["outputs"]):
        add("config", "UNKNOWN_FEATURE")
    if prod == "window_extreme" and fx.get("offset_unit", "sessions") != "sessions":
        add("config", "INVALID_UNIT")
    if fx.get("capability", "batch") != "batch":
        add("config", "UNSUPPORTED_CAPABILITY")

    def need_int(key, lo, hi):
        v = pr.get(key)
        if not (is_int(v) and lo <= v <= hi):
            add("config", "INVALID_CONFIG")
            return None
        return v
    if prod == "session_range_over_open":
        need_int("evidence_limit", 0, 10000)
        if pr.get("algorithm") != "v1":
            add("version", "INCOMPATIBLE_VERSION")
    else:
        need_int("evidence_limit", 0, 10000)
        if "policy_version" not in pr:
            add("config", "INVALID_CONFIG")
        elif pr["policy_version"] != POLICY[prod]:
            add("version", "INCOMPATIBLE_VERSION")
        if prod == "atr_simple_mean":
            need_int("period", 1, 4096)
        if prod == "window_extreme":
            need_int("period", 1, 4096)
            if pr.get("extreme_basis") not in ("intraday", "close"):
                add("config", "INVALID_CONFIG")
        if prod == "relative_log_stats":
            w = need_int("window", 2, 4096)
            need_int("min_pairs", 2, w if w else 4096) if w else need_int("min_pairs", 2, 4096)
            b = pr.get("benchmark_id")
            if not (isinstance(b, str) and b):
                add("config", "INVALID_CONFIG")
            elif b == fx.get("instrument_id", "X"):
                add("identity", "INCONSISTENT_IDENTITY")
        if prod == "core_spread":
            ids = pr.get("core_benchmark_ids")
            if not (isinstance(ids, list) and 2 <= len(ids) <= 16 and len(set(ids)) == len(ids)):
                add("config", "INVALID_CONFIG")
            prof = pr.get("core_profile")
            if prof not in ("prior_close", "window_start", "regular_open"):
                add("config", "INVALID_CONFIG")
            elif (prof == "window_start") != ("window_ns" in pr):
                add("config", "INVALID_CONFIG")
            elif "window_ns" in pr and not (is_int(pr["window_ns"]) and pr["window_ns"] > 0):
                add("config", "INVALID_CONFIG")
            need_int("alignment_tolerance_ns", 0, 2 ** 62)
            need_int("max_endpoint_age_ns", 0, 2 ** 62)
    if "batch_instrument" in fx and fx["batch_instrument"] != fx.get("instrument_id", "X"):
        add("identity", "INCONSISTENT_IDENTITY")

    # --- delivery
    if fx.get("coverage") == "undeclared":
        add("shared", "INVALID_SCHEMA")
    elif fx.get("coverage") == "partial":
        add("shared", "INCONSISTENT_IDENTITY")
    if fx.get("delivered_after_cutoff"):
        add("shared", "BOUNDS")
    d = fx.get("delivery")
    if d is not None:
        if len(set(d)) != len(d):
            add("shared", "DUPLICATE")
        elif d != sorted(d):
            add("shared", "INVALID_ORDER")

    def cell_ok(x):
        """wire stage for one integer cell; returns the usable int or None."""
        if not is_int(x):
            add("wire", "INVALID_SCHEMA")
            return None
        if abs(x) > INT64:
            add("wire", "OVERFLOW")
            return None
        return x

    # --- cells
    if prod in ("atr_simple_mean", "window_extreme"):
        for s in rows_of(fx):
            body = values_of(s)
            if isinstance(body, list):
                if len(body) != 3:
                    add("wire", "INVALID_SCHEMA")
                    continue
                h, l, c = [None if v is None else cell_ok(v) for v in body]
                present = [v for v in (h, l, c) if v is not None]
                if any(v <= 0 for v in present) or (h is not None and l is not None and h < l) \
                        or (h is not None and c is not None and c > h) or (l is not None and c is not None and c < l):
                    add("shared", "INVALID_SCHEMA")
    if prod == "relative_log_stats":
        for series in (fx["inst"], fx["bench"]):
            if series == "absent":
                continue
            for s in series:
                body = values_of(s)
                if body is None or isinstance(body, str):
                    continue
                v = cell_ok(body)
                if v is not None and v <= 0:
                    add("shared", "INVALID_SCHEMA")
    if prod == "core_spread":
        seen = set()
        for f in fx["facts"]:
            key = (f["inst"], f["kind"])
            ids = pr.get("core_benchmark_ids")
            ids_ok = isinstance(ids, list) and 2 <= len(ids) <= 16 and len(set(ids)) == len(ids)
            if ids_ok and f["inst"] not in ids:
                add("identity", "INCONSISTENT_IDENTITY")
            if key in seen:
                add("shared", "DUPLICATE")
            seen.add(key)
            v = cell_ok(f["p"])
            if v is not None and v <= 0:
                add("shared", "INVALID_SCHEMA")
        book = {}
        for f in fx["facts"]:
            book.setdefault(f["inst"], {})[f["kind"]] = f
        for b, kinds in book.items():
            if "start" in kinds and "end" in kinds and kinds["start"]["t"] >= kinds["end"]["t"]:
                add("data", "BOUNDS")
    if prod == "session_range_over_open" and fx["trades"] != "absent":
        for t in fx["trades"]:
            if len(t) != 2:
                add("wire", "INVALID_SCHEMA")
                continue
            p, s = cell_ok(t[0]), cell_ok(t[1])
            if (p is not None and p <= 0) or (s is not None and s < 0):
                add("shared", "INVALID_SCHEMA")
    return out


def set_path(root, path, value):
    parts = path.split(".")
    node = root
    for p in parts[:-1]:
        node = node[int(p)] if isinstance(node, list) else node[p]
    last = parts[-1]
    if isinstance(node, list):
        i = int(last)
        if i == len(node):
            node.append(value)
        else:
            node[i] = value
    else:
        node[last] = value


def del_path(root, path):
    parts = path.split(".")
    node = root
    for p in parts[:-1]:
        node = node[int(p)] if isinstance(node, list) else node[p]
    del node[parts[-1]]


def apply(base, mutation):
    holder = {"fixture": copy.deepcopy(base)}
    for op in mutation:
        if "set" in op:
            set_path(holder, op["set"], copy.deepcopy(op["value"]))
        else:
            del_path(holder, op["delete"])
    return holder["fixture"]


# ------------------------------------------------------------------ main
EVAL = {"atr_simple_mean": eval_atr, "window_extreme": eval_wx, "relative_log_stats": eval_rl, "core_spread": eval_cs,
        "session_range_over_open": eval_ro}
LISTS = ("atr_fixtures", "window_fixtures", "relative_log_fixtures", "core_spread_fixtures", "range_over_open_fixtures")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    doc = json.load(open(path, encoding="utf-8"))
    fixtures = {}
    outputs = 0
    for key in LISTS:
        for fx in doc[key]:
            fixtures[fx["id"]] = fx
            compare(fx, EVAL[fx["producer"]](fx))
            outputs += len(fx["outputs"])
            for stage, code in faults(fx):
                fail(fx["id"], "result fixture fails its own admission model: %s %s" % (stage, code))
            if "inputs" not in fx:
                fail(fx["id"], "no inputs block (input contract)")
    count = rival_check(doc)
    codes = set()
    for r in doc["refusal_fixtures"]:
        base = fixtures[r["base"]]
        found = faults(apply(base, r["mutation"]))
        codes.add(r["error_code"])
        if found != [(r["stage"], r["error_code"])]:
            fail(r["id"], "admission model reports %r, fixture records %r" % (found, [(r["stage"], r["error_code"])]))
    counts = {k: len(doc[k]) for k in LISTS}
    if counts != {"atr_fixtures": doc["fixture_counts"]["atr_result"], "window_fixtures": doc["fixture_counts"]["window_result"],
                  "relative_log_fixtures": doc["fixture_counts"]["relative_log_result"],
                  "core_spread_fixtures": doc["fixture_counts"]["core_spread_result"],
                  "range_over_open_fixtures": doc["fixture_counts"]["range_over_open_result"]}:
        fail("counts", "fixture_counts does not match the lists")
    for line in FAIL:
        print("MISMATCH", line)
    if FAIL:
        print("%d mismatch(es)" % len(FAIL))
        return 1
    print("ALL FIXTURES AND REFUSALS RECOMPUTED AND MATCHED")
    print("atr=%d window=%d relative_log=%d core=%d range_over_open=%d refusal=%d (%d outputs recomputed; %d distinct refusal codes; %d rival/cross checks)"
          % (counts["atr_fixtures"], counts["window_fixtures"], counts["relative_log_fixtures"], counts["core_spread_fixtures"],
             counts["range_over_open_fixtures"], len(doc["refusal_fixtures"]), outputs, len(codes), count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
