#!/usr/bin/env python3
"""Independent stdlib recompute harness for the EF4-H contract fixtures (EQ-159, EQ-160).

Usage: python ef4h_fixture_expand.py path/to/QUOTE_VWAP_CONTRACT_PROPOSAL.json [path/to/proposal.md]

Reads only the fixture INPUTS (rows, windows, params, knowledge, coverage) and recomputes every
output from the contract mathematics with exact fractions, then compares status, reasons,
expected/observed, exact value, float64, float.hex, acceptance rule and witnesses against the
hand-derived expected values stored in the JSON. Imports nothing but the standard library and
nothing from the equity packages. Exits non-zero on any mismatch.
"""
import json
import math
import os
import re
import sys
from fractions import Fraction as Fr

SEC = 10**9
PREC = ["absent_input", "unknown_availability", "future_knowledge", "null_field", "ineligible", "governed_gap",
        "future_market", "partial_universe", "insufficient_history", "no_eligible_observations", "empty_universe", "zero_denominator"]
STAT = {"absent_input": "missing_input", "unknown_availability": "missing_input", "future_knowledge": "missing_input",
        "null_field": "missing_input", "ineligible": "missing_input", "governed_gap": "incomplete_coverage",
        "future_market": "incomplete_coverage", "partial_universe": "incomplete_coverage",
        "insufficient_history": "insufficient_history", "no_eligible_observations": "not_applicable",
        "empty_universe": "not_applicable", "zero_denominator": "not_applicable"}
INT_OUTS = {"quote.change.pair_count", "quote.change.midpoint_change_count", "vwap.path.point_count"}
errors = []


def err(fid, msg):
    errors.append(f"{fid}: {msg}")


def finish(reasons):
    """status from retained reasons: first applicable in the precedence."""
    rs = sorted(set(reasons))
    first = min(rs, key=PREC.index)
    return STAT[first], rs


def knowledge_reason(ka, K):
    if ka is None:
        return "unknown_availability"
    if ka > K:
        return "future_knowledge"
    return None


# --------------------------------------------------------------------------- quotes
def q_eval(fx):
    p = fx["params"]
    outs = p["outputs"]
    K = fx["knowledge_cutoff_ns"]
    C = fx["market_cutoff_ns"]
    E = fx["interval"]["end_ns"]
    scale = 10 ** fx["price_scale"]
    limit = p["evidence_limit"]
    res = {}
    qb = fx["quotes"]
    if qb is None or (not qb["rows"] and qb["coverage"] == "absent"):
        return {o: dict(status="missing_input", reasons=["absent_input"], expected=0, observed=0, value=None) for o in outs}
    rows = qb["rows"]
    n = len(rows)
    order = sorted(range(n), key=lambda i: (rows[i]["event_ns"], rows[i]["order_key"], rows[i]["event_id"]))
    assert order == list(range(n)), "fixture rows must already be in canonical order"
    bounds_reason = knowledge_reason(fx["bounds_known_at"], K)
    # per-row classification with exact values
    info = []
    for r in rows:
        b, a = r["bid"], r["ask"]
        cl = "invalid" if (b is None or a is None or b <= 0 or a <= 0) else ("normal" if a > b else ("locked" if a == b else "crossed"))
        d = {"id": "quote:" + r["event_id"], "cls": cl, "valid": cl in ("normal", "locked"), "bs": r["bid_size"], "as": r["ask_size"],
             "rk": knowledge_reason(r["known_at"], K)}
        if d["valid"]:
            d["s"] = Fr(a - b)
            d["m"] = Fr(a + b, 2)
            d["z"] = Fr(10000) * d["s"] / d["m"]
            if d["bs"] is not None and d["as"] is not None and d["bs"] > 0 and d["as"] > 0:
                d["mp"] = Fr(b * d["as"] + a * d["bs"], d["as"] + d["bs"])
            else:
                d["mp"] = None
        info.append(d)
    V = [d for d in info if d["valid"]]
    Z = [d for d in V if d["mp"] is not None]
    fin = info[-1] if info else None
    continuous = p["sampling"] == "continuous"
    for o in outs:
        reasons = []
        bad = set()
        if bounds_reason:
            reasons.append(bounds_reason)
        for i, d in enumerate(info):
            if d["rk"]:
                reasons.append(d["rk"])
                bad.add(i)
        # null size handling per output
        need_size = None
        if o == "quote.microprice.mean":
            need_size = [i for i, d in enumerate(info) if d["valid"]]
        elif o in ("quote.microprice.last", "quote.microprice.last_offset_bps"):
            need_size = [n - 1] if (fin and fin["valid"]) else []
        if need_size:
            for i in need_size:
                if info[i]["bs"] is None or info[i]["as"] is None:
                    reasons.append("null_field")
                    bad.add(i)
        if qb["coverage"] == "incomplete":
            reasons.append("governed_gap")
        if C < E:
            reasons.append("future_market")
        observed = 0 if bounds_reason else n - len(bad)
        if reasons:
            st, rs = finish(reasons)
            res[o] = dict(status=st, reasons=rs, expected=n, observed=observed, value=None)
            continue
        wit, val, reason, e_o = None, None, None, (n, n)
        if o == "quote.sampled.maximum_spread":
            if V:
                best = max(d["s"] for d in V)
                w = next(d for d in V if d["s"] == best)
                val, wit = best / scale, [w["id"]]
            else:
                reason = "no_eligible_observations"
        elif o == "quote.sampled.maximum_midpoint_bps":
            if V:
                best = max(d["z"] for d in V)
                w = next(d for d in V if d["z"] == best)
                val, wit = best, [w["id"]]
            else:
                reason = "no_eligible_observations"
        elif o in ("quote.microprice.last", "quote.microprice.last_offset_bps"):
            if fin is not None and fin.get("mp") is not None:
                if o.endswith("last"):
                    val = fin["mp"] / scale
                else:
                    val = Fr(10000) * (fin["mp"] - fin["m"]) / fin["m"]
                wit = [fin["id"]]
            else:
                reason = "no_eligible_observations"
        elif o == "quote.microprice.mean":
            if Z:
                val = sum(d["mp"] for d in Z) / len(Z) / scale
                wit = [d["id"] for d in Z]
            else:
                reason = "no_eligible_observations"
        elif o in ("quote.change.midpoint_bps", "quote.change.spread"):
            if len(V) >= 2:
                F, L = V[0], V[-1]
                val = Fr(10000) * (L["m"] - F["m"]) / F["m"] if o.endswith("bps") else (L["s"] - F["s"]) / scale
                wit = [F["id"], L["id"]]
            elif len(V) == 1:
                reason = "insufficient_history"
                e_o = (2, 1)
            else:
                reason = "no_eligible_observations"
        elif o in ("quote.change.pair_count", "quote.change.midpoint_change_count"):
            pairs = [(info[i], info[i + 1]) for i in range(n - 1) if info[i]["valid"] and info[i + 1]["valid"]]
            if o.endswith("midpoint_change_count"):
                pairs = [(x, y) for x, y in pairs if x["m"] != y["m"]]
            val = Fr(len(pairs))
            wit = []
            for x, y in pairs:
                for d in (x, y):
                    if d["id"] not in wit:
                        wit.append(d["id"])
        else:
            raise AssertionError(o)
        if o in ("quote.change.midpoint_bps", "quote.change.spread", "quote.change.pair_count", "quote.change.midpoint_change_count") and not continuous:
            raise AssertionError("change output on a snapshot fixture")
        if reason:
            st, rs = finish([reason])
            res[o] = dict(status=st, reasons=rs, expected=e_o[0], observed=e_o[1], value=None)
        else:
            res[o] = dict(status="available", reasons=[], expected=n, observed=n, value=val, witnesses=wit[:limit])
    return res


# --------------------------------------------------------------------------- vwap
def v_points(fx):
    """returns (slots, points, anchor/proof reasons, batch reasons, flags) used per output."""
    p = fx["params"]
    K = fx["knowledge_cutoff_ns"]
    src = p["series_source"]
    scale = 10 ** fx["price_scale"]
    pts = []  # (x, N, V, id)
    vpts = []  # (x, id) points that exist from volume/size alone
    slot_issue = []  # list of dict per slot: reasons for count output, reasons for price outputs
    if src == "trade":
        tb = fx["trades"]
        if tb is None or (not tb["rows"] and tb["coverage"] == "absent"):
            return None
        rows = [r for r in tb["rows"] if r["eligible"]]
        for r in rows:
            cnt, prc = [], []
            k = knowledge_reason(r["known_at"], K)
            if k:
                cnt.append(k)
                prc.append(k)
            if r["size"] is None:
                cnt.append("null_field")
                prc.append("null_field")
            if r["price"] is None:
                prc.append("null_field")
            slot_issue.append((cnt, prc))
            if r["size"] is not None:
                vpts.append((r["event_ns"], "trade:" + r["event_id"]))
            if r["size"] is not None and r["price"] is not None:
                pts.append((r["event_ns"], r["price"] * r["size"], r["size"], "trade:" + r["event_id"]))
        batch = ["governed_gap"] if tb["coverage"] == "incomplete" else []
    else:
        edges = fx["grid_edges_ns"]
        slots = fx["bars"]["slots"]
        assert len(slots) == len(edges) - 1
        batch = []
        for i, s in enumerate(slots):
            cnt, prc = [], []
            if s["state"] == "gap":
                cnt.append("governed_gap"); prc.append("governed_gap")
            elif s["state"] == "absent":
                cnt.append("absent_input"); prc.append("absent_input")
            else:
                k = None if s["volume"] == 0 else knowledge_reason(s["known_at"], K)
                if k:
                    cnt.append(k); prc.append(k)
                if s["volume"] is None:
                    cnt.append("null_field"); prc.append("null_field")
                elif s["volume"] > 0 and s["notional"] is None:
                    prc.append("null_field")
                if s["volume"] is not None and s["volume"] > 0:
                    vpts.append((edges[i + 1], f"bar:{edges[i]}:{edges[i + 1]}"))
                if s["volume"] is not None and s["volume"] > 0 and s["notional"] is not None:
                    pts.append((edges[i + 1], s["notional"], s["volume"], f"bar:{edges[i]}:{edges[i + 1]}"))
            slot_issue.append((cnt, prc))
    return slot_issue, pts, batch, vpts


def v_eval(fx):
    p = fx["params"]
    outs = p["outputs"]
    K = fx["knowledge_cutoff_ns"]
    C = fx["market_cutoff_ns"]
    E = fx["interval"]["end_ns"]
    scale = 10 ** fx["price_scale"]
    limit = p["evidence_limit"]
    src = p["series_source"]
    prep = v_points(fx)
    if prep is None:
        return {o: dict(status="missing_input", reasons=["absent_input"], expected=0, observed=0, value=None) for o in outs}
    slot_issue, pts, batch, vpts = prep
    nslots = len(slot_issue)
    anchor = knowledge_reason(fx["anchor_known_at"], K)
    proof_reason = None
    if src == "prepared_window":
        pr = fx["proof"]
        proof_reason = "absent_input" if not pr["present"] else knowledge_reason(pr["known_at"], K)
    edge_reasons = [knowledge_reason(a, K) for a in fx.get("edge_known_at", [])]
    unready_global = [r for r in [anchor, proof_reason] + edge_reasons if r]
    # canonical point order: by x, stable (slots / rows already in order)
    pts = sorted(pts, key=lambda t: t[0])
    n = len(pts)
    # cumulative path
    W = []
    cn = cv = 0
    for x, N, V, pid in pts:
        cn += N
        cv += V
        W.append(Fr(cn, cv))
    res = {}
    for o in outs:
        use_prc = o != "vwap.path.point_count"
        reasons = list(unready_global) + list(batch)
        unready_slots = 0
        for cnt, prc in slot_issue:
            iss = prc if use_prc else cnt
            if iss:
                reasons.extend(iss)
                unready_slots += 1
        if C < E:
            reasons.append("future_market")
        observed = 0 if unready_global else nslots - unready_slots
        if reasons:
            st, rs = finish(reasons)
            res[o] = dict(status=st, reasons=rs, expected=nslots, observed=observed, value=None)
            continue
        val, wit, reason, eo = None, None, None, (nslots, nslots)
        ids = [t[3] for t in pts]
        xs = [Fr(t[0]) for t in pts]
        allp = [t[3] for t in sorted(pts, key=lambda t: t[0])]
        if o == "vwap.path.point_count":
            val, wit = Fr(len(vpts)), [i for _, i in sorted(vpts, key=lambda t: t[0])]
        elif n == 0:
            reason = "no_eligible_observations"
        elif o == "vwap.path.last":
            val, wit = W[-1] / scale, list(ids)
        elif o == "vwap.path.maximum":
            m = max(W); val, wit = m / scale, ids[:W.index(m) + 1]
        elif o == "vwap.path.minimum":
            m = min(W); val, wit = m / scale, ids[:W.index(m) + 1]
        elif n < 2:
            reason, eo = "insufficient_history", (2, 1)
        elif o == "vwap.path.change_bps":
            val, wit = Fr(10000) * (W[-1] - W[0]) / W[0], list(ids)
        elif o == "vwap.slope.endpoint":
            dx = xs[-1] - xs[0]
            if dx == 0:
                reason = "zero_denominator"
            else:
                val, wit = (W[-1] - W[0]) / scale * SEC / dx, list(ids)
        elif o == "vwap.slope.ols":
            sx, sw = sum(xs), sum(W)
            sxw = sum(a * b for a, b in zip(xs, W))
            sxx = sum(a * a for a in xs)
            den = n * sxx - sx * sx
            if den == 0:
                reason = "zero_denominator"
            else:
                val, wit = (n * sxw - sx * sw) / den / scale * SEC, ids
        else:
            raise AssertionError(o)
        if reason:
            st, rs = finish([reason])
            res[o] = dict(status=st, reasons=rs, expected=eo[0], observed=eo[1], value=None)
        else:
            res[o] = dict(status="available", reasons=[], expected=nslots, observed=nslots, value=val, witnesses=wit[:limit])
    return res


# --------------------------------------------------------------------------- comparison
def rule_for(fr, integer):
    if integer:
        return "exact_integer"
    if fr == 0:
        return "exact_plus_zero"
    d = fr.denominator
    if d & (d - 1) == 0 and abs(fr.numerator) < 2**53:
        return "exact_float64"
    return "tolerance"


def compare(fx, got):
    fid = fx["id"]
    exp = fx["expected"]
    if set(exp) != set(fx["params"]["outputs"]):
        err(fid, f"expected keys {sorted(exp)} != selected outputs {sorted(fx['params']['outputs'])}")
    n_checked = 0
    for o, g in got.items():
        e = exp.get(o)
        if e is None:
            err(fid, f"{o}: no expected entry")
            continue
        n_checked += 1
        for k in ("status", "reasons", "expected", "observed"):
            if e[k] != g[k]:
                err(fid, f"{o}: {k} expected-in-json {e[k]} != recomputed {g[k]}")
        if g["value"] is None:
            if e["value"] is not None:
                err(fid, f"{o}: json has a value, recompute is null")
            if "witnesses" in e:
                err(fid, f"{o}: unavailable output carries witnesses")
            continue
        v, jv = g["value"], e["value"]
        if jv is None:
            err(fid, f"{o}: json null, recompute {v}")
            continue
        integer = o in INT_OUTS
        if Fr(jv["exact"]) != v:
            err(fid, f"{o}: exact json {jv['exact']} != recomputed {v}")
        if integer:
            if jv.get("int64") != int(v) or jv["acceptance"] != "exact_integer":
                err(fid, f"{o}: int64 field/acceptance wrong {jv}")
            if not (-2**63 <= int(v) < 2**63):
                err(fid, f"{o}: int64 range")
        else:
            f = float(v)  # correctly rounded half-even from the exact rational
            if jv["float64"] != f or jv["hex"] != f.hex():
                err(fid, f"{o}: float64/hex {jv['float64']!r}/{jv['hex']} != {f!r}/{f.hex()}")
            if math.copysign(1.0, jv["float64"]) < 0 and v == 0:
                err(fid, f"{o}: negative zero")
            if jv["acceptance"] != rule_for(v, False):
                err(fid, f"{o}: acceptance {jv['acceptance']} != {rule_for(v, False)}")
            if jv["acceptance"] == "exact_float64" and Fr(f) != v:
                err(fid, f"{o}: exact_float64 claimed but not representable")
            # tolerance clause check of the stored float against the exact rational
            tol = max(8 * math.ulp(f), 1e-12 * abs(f))
            if abs(f - float(v)) > tol:
                err(fid, f"{o}: tolerance clause violated")
        if e.get("witnesses") != g["witnesses"]:
            err(fid, f"{o}: witnesses {e.get('witnesses')} != {g['witnesses']}")
        if len(e.get("witnesses", [])) > fx["params"]["evidence_limit"]:
            err(fid, f"{o}: witnesses exceed evidence_limit")
    return n_checked



# --------------------------------------------------------------------------- refusal engine
import copy

CODE_OF = {
    "C.version": "INCOMPATIBLE_VERSION", "C.feature": "UNKNOWN_FEATURE", "C.capability": "UNSUPPORTED_CAPABILITY", "C.params": "INVALID_CONFIG",
    "K.cell_type": "INVALID_SCHEMA", "K.overflow": "OVERFLOW", "K.no_unit": "INVALID_UNIT", "K.no_sampling": "UNSUPPORTED_SAMPLING",
    "S.dup_identity": "DUPLICATE", "S.tie_key": "DUPLICATE", "S.order": "INVALID_ORDER", "S.ref_bounds": "BOUNDS", "S.negative_quantity": "BOUNDS",
    "S.cutoff": "BOUNDS", "S.eligible_trade": "INVALID_SCHEMA", "S.bar_zero_volume": "INVALID_SCHEMA", "S.bar_notional_bounds": "INVALID_SCHEMA",
    "S.bar_interval": "BOUNDS", "S.bar_end_cutoff": "BOUNDS",
    "L.batch_kind": "INVALID_SCHEMA", "L.fact_kind": "INVALID_SCHEMA", "L.scale": "INVALID_UNIT", "L.basis": "UNSUPPORTED_ADJUSTMENT",
    "L.sampling_mismatch": "UNSUPPORTED_SAMPLING", "L.change_on_snapshot": "UNSUPPORTED_SAMPLING",
    "L.bounds_count": "INCONSISTENT_IDENTITY", "L.bounds_text": "INCONSISTENT_IDENTITY", "L.row_identity": "INCONSISTENT_IDENTITY",
    "L.source_roles": "INCONSISTENT_IDENTITY", "L.proof_count": "INCONSISTENT_IDENTITY", "L.proof_text": "INCONSISTENT_IDENTITY",
    "L.grid_text": "INCONSISTENT_IDENTITY", "L.bar_align": "INCONSISTENT_IDENTITY",
    "L.row_before_start": "BOUNDS", "L.row_at_or_after_end": "BOUNDS", "L.grid_first_edge": "BOUNDS", "L.grid_last_edge": "BOUNDS",
    "L.grid_equal_edges": "BOUNDS", "L.bar_end_after_cutoff": "BOUNDS", "L.bar_notional_positive": "INVALID_SCHEMA",
}
HEADERS_OF = {
    "quote_dynamics": {"quote.change.midpoint_bps", "quote.change.midpoint_change_count", "quote.change.pair_count", "quote.change.spread",
                       "quote.microprice.last", "quote.microprice.last_offset_bps", "quote.microprice.mean",
                       "quote.sampled.maximum_midpoint_bps", "quote.sampled.maximum_spread"},
    "vwap_path": {"vwap.path.change_bps", "vwap.path.last", "vwap.path.maximum", "vwap.path.minimum", "vwap.path.point_count",
                  "vwap.slope.endpoint", "vwap.slope.ols"},
}
LABEL = {"quote_dynamics": "ef4-quote1", "vwap_path": "ef4-vwap1"}
INT64 = 2**63 - 1


def fact(ref, kind, start, end, text, ka=50):
    return {"instrument": "I", "session": "S0", "reference_id": ref, "kind": kind, "start": start, "end": end, "text": text, "known_at": ka}


def build_model(fx):
    """Expand a result fixture into the harness refusal model (placeholder identifiers only)."""
    P = fx["params"]
    prod = "quote_dynamics" if "quotes" in fx else "vwap_path"
    cfg = {"policy_version": LABEL[prod], "evidence_limit": P["evidence_limit"], "outputs": list(P["outputs"]), "capability": "batch",
           "price_scale": fx["price_scale"], "basis": "raw"}
    m = {"producer": prod, "config": cfg, "C": fx["market_cutoff_ns"],
         "bounds": [fact("x1:B(i1)", "ef4.interval.bounds", fx["interval"]["start_ns"], fx["interval"]["end_ns"], "snap", fx["bounds_known_at"] if prod == "quote_dynamics" else fx["anchor_known_at"])],
         "grid": [], "proof": [], "quotes": None, "trades": None, "bars": None}
    if prod == "quote_dynamics":
        cfg["sampling"] = P["sampling"]
        qb = fx["quotes"]
        m["quotes"] = {"kind": "quote", "sampling": P["sampling"], "scale": fx["price_scale"], "basis": "raw", "unit": True,
                       "rows": [{"instrument": "I", "session": "S0", "event_id": r["event_id"], "event_ns": r["event_ns"], "order_key": r["order_key"], "bid": r["bid"], "ask": r["ask"],
                                 "bid_size": r["bid_size"], "ask_size": r["ask_size"], "known_at": r["known_at"]} for r in qb["rows"]]}
    else:
        src = P["series_source"]
        cfg["series_source"] = src
        if src != "trade":
            cfg["grid_version"] = "G"
        if src == "prepared_window":
            cfg["series_policy_id"] = "P"
        if src == "trade":
            m["trades"] = {"kind": "trade", "scale": fx["price_scale"], "basis": "raw", "unit": True,
                           "rows": [{"instrument": "I", "session": "S0", "event_id": r["event_id"], "event_ns": r["event_ns"], "order_key": r["order_key"], "eligible": r["eligible"],
                                     "price": r["price"], "size": r["size"], "known_at": r["known_at"]} for r in fx["trades"]["rows"]]}
        else:
            ed = fx["grid_edges_ns"]
            m["grid"] = [fact(f"x1:B(G#{i})", "ef4.window.edge", e, None, "G", fx["edge_known_at"][i]) for i, e in enumerate(ed)]
            rows = []
            for i, sl in enumerate(fx["bars"]["slots"]):
                if sl["state"] == "row":
                    rows.append({"instrument": "I", "session": "S0", "start": ed[i], "end": ed[i + 1], "volume": sl["volume"], "notional": sl["notional"], "known_at": sl["known_at"], "ohlc": None})
            m["bars"] = {"kind": "bar", "scale": fx["price_scale"], "basis": "raw", "unit": True, "rows": rows}
            if src == "prepared_window":
                m["proof"] = [fact("x1:B(s1)", "ef4.series.proof", fx["interval"]["start_ns"], fx["interval"]["end_ns"], "P", fx["proof"].get("known_at", 50))]
    return m


def _walk(m, path):
    parts = path.split(".")
    cur = m
    for k in parts[:-1]:
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    return cur, parts[-1]


def apply_ops(m, ops):
    for op in ops:
        kind, path = op[0], op[1]
        if kind in ("set", "del_key"):
            parent, last = _walk(m, path)
            if kind == "set":
                if isinstance(parent, list):
                    parent[int(last)] = copy.deepcopy(op[2])
                else:
                    parent[last] = copy.deepcopy(op[2])
            else:
                del parent[last]
        else:
            parent, last = _walk(m, path + ".x")
            lst = parent if isinstance(parent, list) else parent
            # path addresses the list itself
            lst = m
            for k in path.split("."):
                lst = lst[int(k)] if isinstance(lst, list) else lst[k]
            if kind == "insert":
                lst.insert(op[2], copy.deepcopy(op[3]))
            elif kind == "delete":
                del lst[op[2]]
            elif kind == "dup":
                lst.insert(op[2] + 1, copy.deepcopy(lst[op[2]]))
            elif kind == "swap":
                lst[op[2]], lst[op[3]] = lst[op[3]], lst[op[2]]
            else:
                raise AssertionError(kind)
    return m


def _cells(b):
    for r in b["rows"]:
        for k, v in r.items():
            if k in ("instrument", "session", "event_id", "ohlc", "eligible"):
                continue
            yield k, v
        if r.get("ohlc"):
            for k, v in r["ohlc"].items():
                yield k, v


def shared_validate_events(b, C):
    """validation.py validate_batch for TRADE/QUOTE, first raise."""
    seen, last = set(), {}
    for r in b["rows"]:
        group = (r["instrument"], r["session"])
        ident = group + (r["event_id"],)
        if ident in seen:
            return "S.dup_identity"
        key = (r["event_ns"], r["order_key"])
        if group in last and key <= last[group]:
            return "S.tie_key" if key == last[group] else "S.order"
        last[group] = key
        if r["event_ns"] >= C:
            return "S.cutoff"
        if b["kind"] == "trade" and r.get("eligible") is True:
            for n in ("price", "size"):
                if r[n] is None or r[n] <= 0:
                    return "S.eligible_trade"
        seen.add(ident)
        for n in ("size", "bid_size", "ask_size"):
            if r.get(n) is not None and r[n] < 0:
                return "S.negative_quantity"
    return None


def shared_validate_bars(b, C):
    seen, prev_end = set(), {}
    ohlc_cols = any(r.get("ohlc") for r in b["rows"])
    for r in b["rows"]:
        group = (r["instrument"], r["session"])
        if r["start"] >= r["end"]:
            return "S.bar_interval"
        ident = group + (r["start"], r["end"])
        if ident in seen:
            return "S.dup_identity"
        if group in prev_end and r["start"] < prev_end[group]:
            return "S.order"
        prev_end[group] = r["end"]
        if r["end"] > C:
            return "S.bar_end_cutoff"
        vol, notional = r["volume"], r["notional"]
        px = {k: (r["ohlc"] or {}).get(k) for k in ("open", "high", "low", "close")} if ohlc_cols else {}
        if vol == 0:
            if any(v is not None for v in px.values()) or notional not in (None, 0):
                return "S.bar_zero_volume"
        elif vol is not None and vol > 0:
            if any(v is None or v <= 0 for v in px.values()):
                return "S.bar_zero_volume"
            if px:
                lo, hi = px["low"], px["high"]
                if lo > hi or any(not lo <= v <= hi for v in px.values()):
                    return "S.bar_notional_bounds"
                if notional is not None and not lo * vol <= notional <= hi * vol:
                    return "S.bar_notional_bounds"
        seen.add(ident)
        if vol is not None and vol < 0:
            return "S.negative_quantity"
    return None


def shared_validate_refs(facts):
    seen, last = set(), {}
    for f in facts:
        group = (f["instrument"], f["session"])
        ident = group + (f["reference_id"],)
        if ident in seen:
            return "S.dup_identity"
        key = (f["start"], f["reference_id"])
        if group in last and key < last[group]:
            return "S.order"
        last[group] = key
        if f["end"] is not None and f["start"] >= f["end"]:
            return "S.ref_bounds"
        seen.add(ident)
    return None


def fired_rules(m):
    prod, cfg, C = m["producer"], m["config"], m["C"]
    fired = []
    # T1 config
    if cfg.get("policy_version") != LABEL[prod]:
        fired.append("C.version")
    if any(o not in HEADERS_OF[prod] for o in cfg["outputs"]):
        fired.append("C.feature")
    if cfg.get("capability") != "batch":
        fired.append("C.capability")
    meta = {"outputs", "capability", "price_scale", "basis"}
    keys = set(cfg) - meta
    el = cfg.get("evidence_limit")
    bad = not (type(el) is int and 0 <= el <= 10000)
    if prod == "quote_dynamics":
        allowed = {"policy_version", "sampling", "evidence_limit"}
        bad |= keys != allowed or cfg.get("sampling") not in ("trade_snapshot", "continuous")
        samp_ok = cfg.get("sampling") in ("trade_snapshot", "continuous")
    else:
        src = cfg.get("series_source")
        allowed = {"policy_version", "series_source", "evidence_limit"}
        bad |= src not in ("trade", "bar", "prepared_window")
        if src in ("bar", "prepared_window"):
            allowed.add("grid_version")
            bad |= not (isinstance(cfg.get("grid_version"), str) and cfg.get("grid_version"))
        if src == "prepared_window":
            allowed.add("series_policy_id")
            bad |= not (isinstance(cfg.get("series_policy_id"), str) and cfg.get("series_policy_id"))
        bad |= keys != allowed
    if bad:
        fired.append("C.params")
    # batches
    roles = ["quotes"] if prod == "quote_dynamics" else ["trades", "bars"]
    for role in roles:
        b = m[role]
        if b is None:
            continue
        if any(type(v) is float or type(v) is bool for _, v in _cells(b)):
            fired.append("K.cell_type")
        if any(type(v) is int and v > INT64 for _, v in _cells(b)):
            fired.append("K.overflow")
        if not b["unit"]:
            fired.append("K.no_unit")
        if role == "quotes" and b["sampling"] == "none":
            fired.append("K.no_sampling")
    # T3 shared validate_batch (each batch separately)
    shared = []
    for facts in (m["bounds"], m["grid"], m["proof"]):
        if facts:
            shared.append(shared_validate_refs(facts))
    for role in roles:
        b = m[role]
        if b is None:
            continue
        shared.append(shared_validate_bars(b, C) if b["kind"] == "bar" else shared_validate_events(b, C))
    fired += [x for x in shared if x]
    # T4 library
    want_kind = {"quotes": "quote", "trades": "trade", "bars": "bar"}
    S = m["bounds"][0]["start"] if m["bounds"] else None
    E = m["bounds"][0]["end"] if m["bounds"] else None
    for role in roles:
        b = m[role]
        if b is None:
            continue
        if b["kind"] != want_kind[role]:
            fired.append("L.batch_kind")
        if b["scale"] != cfg["price_scale"]:
            fired.append("L.scale")
        if b["basis"] != cfg["basis"]:
            fired.append("L.basis")
        if any(r["instrument"] != "I" or r["session"] != "S0" for r in b["rows"]):
            fired.append("L.row_identity")
        if S is not None:
            ev = [r["event_ns"] for r in b["rows"] if "event_ns" in r]
            if any(x < S for x in ev):
                fired.append("L.row_before_start")
            if any(x >= E for x in ev):
                fired.append("L.row_at_or_after_end")
    if any(f["kind"] != "ef4.interval.bounds" for f in m["bounds"]) or any(f["kind"] != "ef4.window.edge" for f in m["grid"]) or any(f["kind"] != "ef4.series.proof" for f in m["proof"]):
        fired.append("L.fact_kind")
    if len({f["reference_id"] for f in m["bounds"]}) != 1:
        fired.append("L.bounds_count")
    if any(f["text"] != "snap" for f in m["bounds"]):
        fired.append("L.bounds_text")
    if prod == "quote_dynamics":
        if samp_ok and m["quotes"] is not None and m["quotes"]["sampling"] in ("trade_snapshot", "continuous") and cfg["sampling"] != m["quotes"]["sampling"]:
            fired.append("L.sampling_mismatch")
        if cfg.get("sampling") == "trade_snapshot" and any(o.startswith("quote.change") for o in cfg["outputs"]):
            fired.append("L.change_on_snapshot")
    else:
        src = cfg.get("series_source")
        if (src == "trade" and m["bars"] is not None) or (src in ("bar", "prepared_window") and m["trades"] is not None):
            fired.append("L.source_roles")
        if src in ("bar", "prepared_window") and m["bars"] is not None and S is not None:
            gv = cfg.get("grid_version")
            if isinstance(gv, str) and gv and any(f["text"] != gv for f in m["grid"]):
                fired.append("L.grid_text")
            edges = [f["start"] for f in m["grid"]]
            sound = bool(edges) and all(f["kind"] == "ef4.window.edge" for f in m["grid"])
            if edges and edges[0] != S:
                fired.append("L.grid_first_edge"); sound = False
            if edges and edges[-1] != E:
                fired.append("L.grid_last_edge"); sound = False
            if any(a == b for a, b in zip(edges, edges[1:])):
                fired.append("L.grid_equal_edges"); sound = False
            if any(a > b for a, b in zip(edges, edges[1:])):
                sound = False
            if isinstance(gv, str) and gv and any(f["text"] != gv for f in m["grid"]):
                sound = False
            if sound and any((r["start"], r["end"]) not in set(zip(edges, edges[1:])) for r in m["bars"]["rows"]):
                fired.append("L.bar_align")
            if E > C:
                fired.append("L.bar_end_after_cutoff")
            if not any(r.get("ohlc") for r in m["bars"]["rows"]) and any(r["volume"] is not None and r["volume"] > 0 and r["notional"] is not None and r["notional"] <= 0 for r in m["bars"]["rows"]):
                fired.append("L.bar_notional_positive")
        if src == "prepared_window":
            if len({f["reference_id"] for f in m["proof"]}) != 1:
                fired.append("L.proof_count")
            pid = cfg.get("series_policy_id")
            if isinstance(pid, str) and pid and any(f["text"] != pid for f in m["proof"]):
                fired.append("L.proof_text")
    return fired


def check_refusals(d, allf):
    n = 0
    for r in d["refusal_fixtures"]:
        fid = r["id"]
        if r["base"] not in allf:
            err(fid, "base fixture missing")
            continue
        base = allf[r["base"]]
        if ("quotes" in base) != (r["producer"] == "quote_dynamics"):
            err(fid, "base fixture belongs to the other producer")
            continue
        m = build_model(base)
        if fired_rules(m):
            err(fid, f"base {r['base']} already refused: {fired_rules(m)}")
            continue
        m = apply_ops(m, r["mutations"])
        f = fired_rules(m)
        if f != [r["rule"]]:
            err(fid, f"recipe fires {f}, stated rule {r['rule']}")
            continue
        if CODE_OF[r["rule"]] != r["error_code"]:
            err(fid, f"rule {r['rule']} is {CODE_OF[r['rule']]}, stated {r['error_code']}")
        layer = {"K": "shared constructor", "S": "shared validator", "L": "library", "C": "library"}[r["rule"][0]]
        if layer != r["raised_by"]:
            err(fid, f"layer {layer} != stated {r['raised_by']}")
        n += 1
    return n


def main():
    docs = os.environ.get("EF4_DOCS_DIR") or os.path.join(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")), "docs", "ef4")
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(docs, "QUOTE_VWAP_CONTRACT_PROPOSAL.json")
    d = json.load(open(path, encoding="utf-8"))
    total = 0
    qn = vn = 0
    for fx in d["quote_fixtures"]:
        K = fx["knowledge_cutoff_ns"]
        assert K == 100
        if fx["params"]["sampling"] == "trade_snapshot":
            bad = [o for o in fx["params"]["outputs"] if o.startswith("quote.change")]
            if bad:
                err(fx["id"], f"snapshot fixture selects continuous-only outputs {bad}")
        total += compare(fx, q_eval(fx))
        qn += 1
    for fx in d["vwap_fixtures"]:
        total += compare(fx, v_eval(fx))
        vn += 1
    # fixture counts
    fc = d["fixture_counts"]
    if (fc["quote_result"], fc["vwap_result"], fc["refusal"]) != (qn, vn, len(d["refusal_fixtures"])):
        err("counts", f"fixture_counts {fc} != ({qn},{vn},{len(d['refusal_fixtures'])})")
    allf = {f["id"]: f for f in d["quote_fixtures"] + d["vwap_fixtures"]}
    ids = [f["id"] for f in d["quote_fixtures"] + d["vwap_fixtures"] + d["refusal_fixtures"]]
    if len(ids) != len(set(ids)):
        err("ids", "duplicate fixture ids")
    # identical-result pairs and same_values_as relations
    def vals(f, outs):
        return {o: (f["expected"][o]["status"], f["expected"][o]["reasons"], f["expected"][o]["value"]) for o in outs}
    for a, b in d["prefix_equivalences"]:
        fa, fb = allf[a], allf[b]
        if vals(fa, sorted(fa["expected"])) != vals(fb, sorted(fb["expected"])):
            err("equiv", f"{a} and {b} differ")
    for f in allf.values():
        ref = f.get("same_values_as")
        if ref:
            g = allf[ref]
            common = [o for o in f["expected"] if o in g["expected"]]
            if not common:
                err(f["id"], "same_values_as shares no output")
            for o in common:
                x, y = f["expected"][o], g["expected"][o]
                if (x["status"], x["reasons"], x["value"]) != (y["status"], y["reasons"], y["value"]):
                    err(f["id"], f"{o}: differs from {ref}")
    # refusals: every recipe is applied to its base fixture and must fire exactly the stated rule
    nref = check_refusals(d, allf)
    base_ok = len({r['id'] for r in d['refusal_fixtures']}) == len(d['refusal_fixtures'])
    if not base_ok:
        err('refusals', 'duplicate refusal ids')
    # no hardcoded identities in fixture bodies
    forbidden = re.compile(r"^(instrument|entity|symbol|benchmark|role|grid|session|snapshot)(_id)?$|_(instrument|entity|symbol)_id$")
    def walk(o, fid):
        if isinstance(o, dict):
            for k, v in o.items():
                if forbidden.search(k):
                    err(fid, f"identity key {k} in fixture body")
                walk(v, fid)
        elif isinstance(o, list):
            for v in o:
                walk(v, fid)
    for f in allf.values():
        walk({k: v for k, v in f.items() if k != "description"}, f["id"])
    # reasons / header consistency
    hid = {h["id"] for h in d["headers"]}
    for f in allf.values():
        for o in f["params"]["outputs"]:
            if o not in hid:
                err(f["id"], f"output {o} not a header")
    # markdown count agreement
    md_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(docs, "QUOTE_VWAP_CONTRACT_PROPOSAL.md")
    if os.path.exists(md_path):
        md = open(md_path, encoding="utf-8").read()
        for s in (f"{qn} quote", f"{vn} VWAP", f"{len(d['refusal_fixtures'])} typed-refusal"):
            if s not in md:
                err("md", f"markdown does not state '{s}'")
    print(f"quote fixtures {qn}, vwap fixtures {vn}, refusal fixtures {len(d['refusal_fixtures'])} (recipes applied and verified: {nref}), outputs compared {total}")
    if errors:
        print(f"MISMATCHES: {len(errors)}")
        for e in errors:
            print("  " + e)
        sys.exit(1)
    print("ALL FIXTURES MATCH THE INDEPENDENT RECOMPUTE")


if __name__ == "__main__":
    main()
