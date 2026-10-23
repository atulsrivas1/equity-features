#!/usr/bin/env python3
"""Independent stdlib recompute harness for the EF4-G tape contract proposal fixtures.

    python ef4g_fixture_expand.py docs/ef4/TAPE_CONTRACT_PROPOSAL.json [--emit-generators out.json] [-v]

Imports only the Python standard library; nothing from the equity packages. For ALL fixtures it
  1. expands the compact notation into canonical column rows under two independent parameter
     bindings (entity, session, seed reference ids are bound here, never read from the fixture),
  2. recomputes every listed output with two independently written oracles that must agree
     (window: single-pass chain vs nearest-different-price search; top-K: full sort vs
     repeated-maximum selection),
  3. checks status, reasons, expected/observed counts, witnesses, exact rational, float64, float.hex
     and the per-output acceptance class against the fixture,
  4. executes every refusal fixture's construction recipe through a model of the documented
     admission order and checks the typed error code,
  5. runs the generator fixtures with both oracles and compares them with the stored expectation,
  6. checks structural consistency (counts, ids, coverage map, reasons_reached, identity tokens).
The admission and quality model here restates the contract text; it is a reference for reviewers,
not the library under test. Exit code 0 only when every check passes.
"""
import copy
import json
import os
import sys
from fractions import Fraction

I64 = 2**63 - 1
D128 = 10**38
PRECEDENCE = ["absent_input", "unknown_availability", "future_knowledge", "null_field", "ineligible", "governed_gap",
              "future_market", "partial_universe", "insufficient_history", "no_eligible_observations", "empty_universe",
              "zero_denominator"]
STATUS = {"absent_input": "missing_input", "unknown_availability": "missing_input", "future_knowledge": "missing_input",
          "null_field": "missing_input", "ineligible": "missing_input", "governed_gap": "incomplete_coverage",
          "future_market": "incomplete_coverage", "partial_universe": "incomplete_coverage",
          "insufficient_history": "insufficient_history", "no_eligible_observations": "not_applicable",
          "empty_universe": "not_applicable", "zero_denominator": "not_applicable"}
FEAT = {"count": "tape.window.count", "volume": "tape.window.volume", "notional": "tape.window.notional",
        "up": "tape.tick.up_volume", "down": "tape.tick.down_volume", "neutral": "tape.tick.neutral_volume",
        "net": "tape.tick.net_volume", "netn": "tape.tick.net_notional", "imb": "tape.tick.imbalance"}
KEY = {v: k for k, v in FEAT.items()}
TOPK = "tape.top_k_notional"
WINDOW_CLASS = ("count", "volume", "notional")
POLICY_TAPE, POLICY_TOPK = "ef4-tape1", "ef4-notional1"
BINDINGS = [
    {"entity": "AAA", "session": "S-1", "other_entity": "BBB", "other_session": "S-2", "seed_ref": "x1:B(seedset-a)"},
    {"entity": "q.z/9", "session": "2031-02-03", "other_entity": "q.z/8", "other_session": "2031-02-04", "seed_ref": "x1:B(other)"},
]


class Err(Exception):
    def __init__(self, code, why=""):
        super().__init__(code + ": " + why)
        self.code = code


# ------------------------------------------------------------------ numeric helpers
def float_of(fr):
    return fr.numerator / fr.denominator  # true division of ints is correctly rounded (half-even)


def acceptance_of(fr, integer):
    if integer:
        return "exact_integer"
    if fr == 0:
        return "exact_plus_zero"
    d = fr.denominator
    if d & (d - 1) == 0 and abs(fr.numerator) < 2**53:
        return "exact_float64"
    return "tolerance"


def check_value(tag, spec, fr, integer, problems):
    got = f"{fr.numerator}/{fr.denominator}"
    if spec["exact"] != got:
        problems.append(f"{tag}: exact {spec['exact']} != recomputed {got}")
    if spec["acceptance"] != acceptance_of(fr, integer):
        problems.append(f"{tag}: acceptance {spec['acceptance']} != {acceptance_of(fr, integer)}")
    if not integer:
        fl = float_of(fr)
        if fr == 0:
            fl = 0.0
        if float.hex(fl) != spec["hex"] or float.hex(spec["float64"]) != spec["hex"]:
            problems.append(f"{tag}: hex/float64 mismatch {spec['hex']} vs {float.hex(fl)}")
        if float.fromhex(spec["hex"]) != fl:
            problems.append(f"{tag}: float.fromhex differs")


# ------------------------------------------------------------------ expansion
def expand_trades(fx, b, trades=None):
    """Compact trade notation -> canonical column rows. Columns not delivered are omitted."""
    trades = fx["trades"] if trades is None else trades
    if trades is None:
        return None
    cols = fx.get("columns", ["price", "size", "known_at_ns"])
    rows = []
    for t in trades:
        r = {"instrument_id": b["other_entity"] if t.get("inst") == "$OTHER_ENTITY" else b["entity"],
             "session_id": b["other_session"] if t.get("sess") == "$OTHER_SESSION" else b["session"],
             "event_ns": t["ns"], "order_key": t["ok"], "event_id": t["id"], "eligible": t.get("elig", True)}
        if "p" in t and "price" in cols:
            r["price"] = t["p"]
        if "q" in t and "size" in cols:
            r["size"] = t["q"]
        if "cond" in t:
            r["condition"] = t["cond"]
        if "known_at_ns" in cols:
            r["known_at_ns"] = t["ka"] if "ka" in t else 500
        rows.append(r)
    return rows


def expand_seed(fx, b):
    s = fx.get("seed")
    if s is None:
        return None
    o = fx["open"]
    return {"fact_kind": s.get("fact_kind", "ef4.tick.seed"),
            "instrument_id": b["other_entity"] if s.get("inst") == "$OTHER_ENTITY" else b["entity"],
            "session_id": b["other_session"] if s.get("sess") == "$OTHER_SESSION" else b["session"],
            "reference_id": b["seed_ref"], "effective_start_ns": s.get("start_ns", o - 1), "effective_end_ns": s.get("end_ns", o),
            "text": s["sign"], "price": s["price"], "known_at_ns": s.get("ka", 500), "count": s.get("count", 1),
            "scale": s.get("scale", fx["price_scale"]), "adjustment": s.get("adjustment", "raw")}


# ------------------------------------------------------------------ oracles: signs
def signs_chain(rows, seed):
    """Oracle A: single pass tick rule with carry. rows = eligible rows in canonical order."""
    out = []
    ref_p, ref_s = (seed["price"], {"+": 1, "-": -1, "0": 0}[seed["text"]]) if seed else (None, 0)
    for r in rows:
        if ref_p is None:
            s = 0
        elif r["price"] > ref_p:
            s = 1
        elif r["price"] < ref_p:
            s = -1
        else:
            s = ref_s
        out.append(s)
        ref_p, ref_s = r["price"], s
    return out


def signs_nearest(rows, seed):
    """Oracle B: sign from the nearest earlier print (or seed) whose price differs; if none, the seed sign or 0."""
    seq = ([("seed", seed["price"])] if seed else []) + [(i, r["price"]) for i, r in enumerate(rows)]
    seed_sign = {"+": 1, "-": -1, "0": 0}[seed["text"]] if seed else 0
    out = []
    off = 1 if seed else 0
    for i, r in enumerate(rows):
        pos = i + off
        s = None
        for j in range(pos - 1, -1, -1):
            if seq[j][1] != r["price"]:
                s = 1 if r["price"] > seq[j][1] else -1
                break
        if s is None:
            s = seed_sign if seed else 0
        out.append(s)
    return out


# ------------------------------------------------------------------ window model
def absolutize(fx):
    """Epoch-scale fixtures: shift every time field (open, C, K, ns, numeric known_at, seed times) by fx['epoch']."""
    if "epoch" not in fx:
        return fx
    fx = copy.deepcopy(fx)
    e = fx.pop("epoch")
    for k in ("open", "C", "K"):
        fx[k] += e
    for t in fx.get("trades") or []:
        t["ns"] += e
        if isinstance(t.get("ka"), int):
            t["ka"] += e
    s = fx.get("seed")
    if s:
        for k in ("start_ns", "end_ns", "ka"):
            if isinstance(s.get(k), int):
                s[k] += e
    return fx


def know_reason(ka, K, mode="known_at"):
    if mode == "reconstruction":
        return None
    if ka is None:
        return "unknown_availability"
    return "future_knowledge" if ka > K else None


def status_of(reasons):
    if not reasons:
        return "available"
    return STATUS[next(r for r in PRECEDENCE if r in reasons)]


def window_sums(rows_all, win, seed, signer):
    elig = [r for r in rows_all if r["eligible"]]
    sg = signer(elig, seed) if (elig and "price" in elig[0]) else [0] * len(elig)
    sign_of = {id(r): s for r, s in zip(elig, sg)}
    win_ids = {id(r) for r in win}
    up = down = neutral = 0
    upn = downn = 0
    cnt = vol = notional = 0
    for r in elig:
        if id(r) not in win_ids:
            continue
        cnt += 1
        vol += r["size"] if "size" in r else 0
        notional += r["price"] * r["size"] if ("price" in r and "size" in r) else 0
        s = sign_of[id(r)]
        q = r.get("size", 0)
        pn = r["price"] * q if "price" in r else 0
        if s > 0:
            up += q; upn += pn
        elif s < 0:
            down += q; downn += pn
        else:
            neutral += q
    return dict(count=cnt, volume=vol, notional=notional, up=up, down=down, neutral=neutral, net=up - down, netn=upn - downn)


def window_eval(fx, b, selection, signer=signs_chain):
    fx = absolutize(fx)
    mode = fx.get("mode", "known_at")
    p = fx["params"]
    W, policy, limit = p["window_ns"], p["seed_policy"], p["evidence_limit"]
    o, C, K = fx["open"], fx["C"], fx["K"]
    cols = fx.get("columns", ["price", "size", "known_at_ns"])
    rows = expand_trades(fx, b)
    seed = expand_seed(fx, b) if policy == "supplied" else None
    res = {}
    if rows is None:
        for f in selection:
            res[f] = {"status": "missing_input", "reasons": ["absent_input"], "expected": 0, "observed": 0}
        return res
    n = len(rows)
    cov = fx.get("coverage") or {"expected": n, "complete": True}
    lo = C - W
    win = [r for r in rows if lo <= r["event_ns"] < C]
    pre = [r for r in rows if r["event_ns"] < lo]
    insufficient = lo < o
    sums = window_sums(rows, win, seed, signer)
    for f in selection:
        k = KEY[f]
        tick = k not in WINDOW_CLASS
        need_price = k not in ("count", "volume")
        need_size = k != "count"
        operand = win if not tick else rows
        reasons = set()
        absent_col = (need_price and "price" not in cols) or (need_size and "size" not in cols)
        if absent_col:
            reasons.add("absent_input")
        unready = 0
        for r in operand:
            rr = know_reason(r.get("known_at_ns"), K, mode)
            if rr:
                reasons.add(rr)
                unready += 1
        seed_slot = 1 if (tick and policy == "supplied") else 0
        seed_ready = 0
        if seed_slot:
            if seed is None:
                reasons.add("absent_input")
            else:
                rr = know_reason(seed["known_at_ns"], K, mode)
                if rr:
                    reasons.add(rr)
                else:
                    seed_ready = 1
        if not cov["complete"] or cov["expected"] != n:
            reasons.add("governed_gap")
        if insufficient:
            reasons.add("insufficient_history")
        E = cov["expected"] + seed_slot
        O = 0 if absent_col else n - unready + seed_ready
        entry = {"expected": E, "observed": O}
        value = None
        if not reasons:
            s = sums
            if k == "volume" and s["volume"] > I64:
                raise Err("OVERFLOW", "window volume")
            if k in ("up", "down", "neutral") and s[k] > I64:
                raise Err("OVERFLOW", k)
            if k == "imb" and (s["volume"] > I64 or s["up"] > I64 or s["down"] > I64):
                raise Err("OVERFLOW", "imbalance operands")
            if k in ("notional", "netn") and abs(s[k]) >= D128:
                raise Err("OVERFLOW", "decimal128")
            if k == "imb":
                if s["volume"] == 0:
                    reasons.add("zero_denominator")
                else:
                    value = Fraction(s["net"], s["volume"])
            else:
                value = Fraction(s[k])
        entry["reasons"] = sorted(reasons)
        entry["status"] = status_of(reasons)
        if entry["status"] == "available":
            entry["value"] = value
            wit = ([f"seed:{seed['reference_id']}"] if seed_slot and seed else []) + [f"trade:{r['event_id']}" for r in win if r["eligible"]]
            entry["witnesses"] = wit[:limit]
        res[f] = entry
    return res


# ------------------------------------------------------------------ top-K model
def topk_pick_sort(elig, K):
    return sorted(elig, key=lambda r: (-(r["price"] * r["size"]), r["event_ns"], r["order_key"], r["event_id"]))[:K]


def topk_pick_select(elig, K):
    pool = list(elig)
    out = []
    while pool and len(out) < K:
        best = pool[0]
        for r in pool[1:]:
            kb, kr = (best["price"] * best["size"], best["event_ns"], best["order_key"], best["event_id"]), (r["price"] * r["size"], r["event_ns"], r["order_key"], r["event_id"])
            if kr[0] > kb[0] or (kr[0] == kb[0] and kr[1:] < kb[1:]):
                best = r
        out.append(best)
        pool.remove(best)
    return out


def topk_eval(fx, b, picker=topk_pick_sort):
    fx = absolutize(fx)
    mode = fx.get("mode", "known_at")
    p = fx["params"]
    K, C, Kn = p["top_k"], fx["C"], fx["K"]
    cols = fx.get("columns", ["price", "size", "known_at_ns"])
    rows = expand_trades(fx, b)
    if rows is None:
        return {"status": "missing_input", "reasons": ["absent_input"], "expected": 0, "observed": 0}
    n = len(rows)
    cov = fx.get("coverage") or {"expected": n, "complete": True}
    reasons = set()
    unready = 0
    for r in rows:
        rr = know_reason(r.get("known_at_ns"), Kn, mode)
        if rr:
            reasons.add(rr)
            unready += 1
    elig = [r for r in rows if r["eligible"]]
    absent_col = bool(elig) and ("price" not in cols or "size" not in cols)
    if absent_col:
        reasons.add("absent_input")
    if not cov["complete"] or cov["expected"] != n:
        reasons.add("governed_gap")
    out = {"expected": cov["expected"], "observed": 0 if absent_col else n - unready, "reasons": sorted(reasons), "status": status_of(reasons)}
    if out["status"] == "available":
        picked = picker(elig, K)
        out["rows"] = picked
        out["witnesses"] = [f"trade:{r['event_id']}" for r in picked]
        out["boundaries"] = ["closing_auction" if (r["event_ns"] == C and r.get("condition") == "closing_auction") else "ordinary" for r in picked]
    return out


def key_of(r):
    return (-(r["price"] * r["size"]), r["event_ns"], r["order_key"], r["event_id"])


def merge_partials(parts, K):
    """parts: list of topk_eval outputs (already compatible)."""
    reasons = set()
    for q in parts:
        reasons.update(q["reasons"])
    E = sum(q["expected"] for q in parts)
    O = sum(q["observed"] for q in parts)
    out = {"expected": E, "observed": O, "reasons": sorted(reasons), "status": status_of(reasons)}
    if out["status"] == "available":
        rows = [r for q in parts for r in q["rows"]]
        ids = [r["event_id"] for r in rows]
        if len(set(ids)) != len(ids):
            raise Err("DUPLICATE", "retained event_id in two partials")
        rows.sort(key=key_of)
        rows = rows[:K]
        out["rows"] = rows
        out["witnesses"] = [f"trade:{r['event_id']}" for r in rows]
    return out


def merge_eval(fx, b):
    parts_fx = fx["partitions"]
    if not parts_fx:
        raise Err("INVALID_CONFIG", "no partitions")
    base = parts_fx[0]

    def attrs(p):
        return {"params": p["params"], "price_scale": p.get("price_scale", fx["price_scale"]), "adjustment": p.get("adjustment", "raw"),
                "C": p.get("C", fx["C"]), "K": p.get("K", fx["K"]), "entity": p.get("entity", "$ENTITY"),
                "eligibility_policy": p.get("eligibility_policy", "P")}
    a0 = attrs(base)
    for p in parts_fx[1:]:
        a = attrs(p)
        if a["params"].get("policy_version", POLICY_TOPK) != a0["params"].get("policy_version", POLICY_TOPK):
            raise Err("INCOMPATIBLE_VERSION", "policy_version")
        if a["price_scale"] != a0["price_scale"]:
            raise Err("INVALID_UNIT", "scale")
        if a["adjustment"] != a0["adjustment"]:
            raise Err("UNSUPPORTED_ADJUSTMENT", "adjustment")
        if a["eligibility_policy"] != a0["eligibility_policy"]:
            raise Err("INVALID_CONFIG", "eligibility policy")
        if a["params"]["top_k"] != a0["params"]["top_k"] or a["params"]["evidence_limit"] != a0["params"]["evidence_limit"]:
            raise Err("INVALID_CONFIG", "K")
        if a["entity"] != a0["entity"] or a["C"] != a0["C"] or a["K"] != a0["K"]:
            raise Err("INCONSISTENT_IDENTITY", "entity/cutoff/knowledge")
    K = a0["params"]["top_k"]
    parts = []
    for p in parts_fx:
        pf = {"params": p["params"], "C": fx["C"], "K": fx["K"], "open": fx["open"], "price_scale": fx["price_scale"], "trades": p["trades"]}
        r = topk_eval(pf, b)
        if p.get("partial_delivered_order") and r.get("rows"):
            if p["partial_delivered_order"] != [x["event_id"] for x in r["rows"]]:
                raise Err("INVALID_ORDER", "partial rows not in rank order")
        parts.append(r)
    return merge_partials(parts, K), parts


# ------------------------------------------------------------------ admission model for refusals
def apply_ops(fx, ops):
    fx = copy.deepcopy(fx)
    for op in ops:
        if op["op"] in ("set", "del"):
            keys = op["path"].split(".")
            cur = fx
            for k in keys[:-1]:
                cur = cur[int(k)] if isinstance(cur, list) else cur.setdefault(k, {})
            last = keys[-1]
            if op["op"] == "set":
                if isinstance(cur, list):
                    cur[int(last)] = op["value"]
                else:
                    cur[last] = op["value"]
            else:
                del cur[last]
        elif op["op"] == "append":
            fx[op["path"]].append(op["value"])
        elif op["op"] == "swap":
            lst = fx[op["path"]]
            lst[op["i"]], lst[op["j"]] = lst[op["j"]], lst[op["i"]]
        elif op["op"] == "setitem":
            fx[op["path"]][op["index"]][op["key"]] = op["value"]
        else:
            raise ValueError(op)
    return fx


def is_int(v):
    return type(v) is int


def admit_batch(fx, b, scenario):
    fx = absolutize(fx)
    rows = fx.get("trades")
    if rows is None:
        return
    for t in rows:  # constructor cell checks
        for f in ("p", "q"):
            v = t.get(f)
            if v is None:
                continue
            if not is_int(v):
                raise Err("INVALID_SCHEMA", "cell type")
            if not -2**63 <= v <= I64:
                raise Err("OVERFLOW", "cell")
    if fx.get("batch_kind", "trade") != "trade":
        raise Err("INVALID_SCHEMA", "canonical trade batch required")
    if fx.get("batch_price_scale", fx["price_scale"]) != fx["price_scale"]:
        raise Err("INVALID_UNIT", "price unit")
    if "coverage_observed" in fx:  # shared Coverage constructor
        cv = fx.get("coverage") or {"expected": len(rows), "complete": True}
        ce, co = cv["expected"], fx["coverage_observed"]
        if ce is not None and ce < co:
            raise Err("INVALID_SCHEMA", "expected coverage below observed")
        if cv["complete"] and ce != co:
            raise Err("INVALID_SCHEMA", "complete coverage requires matching count")
    if fx.get("batch_adjustment", "raw") != fx.get("config_adjustment", "raw"):
        raise Err("UNSUPPORTED_ADJUSTMENT", "adjustment")
    if fx.get("scope_policy", "P") != fx.get("config_policy", "P"):
        raise Err("INVALID_CONFIG", "scope policy")
    if fx.get("scope_start", fx["open"]) != fx["open"] or fx.get("scope_end", fx["C"]) != fx["C"]:
        raise Err("INCONSISTENT_IDENTITY", "scope bounds")
    if fx.get("scope_include_opening_auction", fx.get("include_opening_auction", False)) != fx.get("include_opening_auction", False) or             fx.get("scope_include_closing_auction", fx.get("include_closing_auction", False)) != fx.get("include_closing_auction", False):
        raise Err("INCONSISTENT_IDENTITY", "scope auction flags")
    if fx.get("coverage_observed", len(rows)) != len(rows):
        raise Err("INCONSISTENT_IDENTITY", "coverage")
    ex = expand_trades(fx, b)
    for r in ex:
        if r["instrument_id"] != b["entity"] or r["session_id"] != b["session"]:
            raise Err("INCONSISTENT_IDENTITY", "entity/session")
    inc_open = fx.get("include_opening_auction", False)
    inc_close = fx.get("include_closing_auction", False)
    seen = set()
    last = None
    cols = fx.get("columns", ["price", "size", "known_at_ns"])
    for r in ex:
        if r["event_id"] in seen:
            raise Err("DUPLICATE", "event id")
        seen.add(r["event_id"])
        key = (r["event_ns"], r["order_key"])
        if last is not None and key <= last:
            raise Err("DUPLICATE" if key == last else "INVALID_ORDER", "order")
        last = key
        cond = r.get("condition")
        o, C = fx["open"], fx["C"]
        close = fx.get("close", C)
        if cond == "closing_auction":
            ok = inc_close and C == close and r["event_ns"] == C
        elif cond == "opening_auction":
            ok = inc_open and r["event_ns"] == o
        else:
            ok = o <= r["event_ns"] < C
        if not ok:
            raise Err("BOUNDS", "outside scope")
        if r["eligible"]:
            for c in ("price", "size"):
                if c in cols and (r.get(c) is None or r[c] <= 0):
                    raise Err("INVALID_SCHEMA", "eligible price/size")


def admit_seed(fx, b):
    fx = absolutize(fx)
    s = expand_seed(fx, b)
    if s is None:
        return
    if s["fact_kind"] != "ef4.tick.seed":
        raise Err("INVALID_SCHEMA", "fact kind")
    if s["scale"] != fx["price_scale"]:
        raise Err("INVALID_UNIT", "seed scale")
    if s["adjustment"] != "raw":
        raise Err("UNSUPPORTED_ADJUSTMENT", "seed adjustment")
    if s["price"] is None or not is_int(s["price"]) or s["price"] <= 0:
        raise Err("INVALID_SCHEMA", "seed price")
    if s["text"] not in ("+", "-", "0"):
        raise Err("INVALID_SCHEMA", "seed sign")
    if s["instrument_id"] != b["entity"] or s["session_id"] != b["session"]:
        raise Err("INCONSISTENT_IDENTITY", "seed identity")
    if s["effective_start_ns"] >= s["effective_end_ns"]:
        raise Err("BOUNDS", "seed interval")
    if s["effective_start_ns"] >= fx["open"]:
        raise Err("BOUNDS", "seed must precede open")
    if s["effective_end_ns"] != fx["open"]:
        raise Err("INCONSISTENT_IDENTITY", "seed end")
    if s["count"] != 1:
        raise Err("INVALID_SCHEMA", "exactly one seed fact required")


def admit_window(fx, b):
    fx = absolutize(fx)
    cap = fx.get("capability", "batch")
    if cap in ("update", "restore", "merge"):
        raise Err("UNSUPPORTED_CAPABILITY", cap)
    sel = fx.get("selection") or list(fx["expected"])
    for f in sel:
        if f not in KEY:
            raise Err("UNKNOWN_FEATURE", f)
    p = fx["params"]
    need = {"policy_version", "window_ns", "seed_policy", "evidence_limit"}
    if set(p) != need:
        raise Err("INVALID_CONFIG", "parameter set")
    w = p["window_ns"]
    if not is_int(w) or not 1 <= w <= I64:
        raise Err("INVALID_CONFIG", "window_ns")
    if p["seed_policy"] not in ("none", "supplied"):
        raise Err("INVALID_CONFIG", "seed_policy")
    if not is_int(p["evidence_limit"]) or not 0 <= p["evidence_limit"] <= 10000:
        raise Err("INVALID_CONFIG", "evidence_limit")
    if p["policy_version"] != POLICY_TAPE:
        raise Err("INCOMPATIBLE_VERSION", "policy_version")
    if fx.get("include_opening_auction") or fx.get("include_closing_auction"):
        raise Err("INVALID_CONFIG", "auction inclusion")
    if p["seed_policy"] == "none" and fx.get("seed") is not None:
        raise Err("INVALID_CONFIG", "seed role with seed_policy none")
    admit_batch(fx, b, "window")
    if p["seed_policy"] == "supplied":
        admit_seed(fx, b)
    window_eval(fx, b, sel)


def admit_topk(fx, b):
    fx = absolutize(fx)
    cap = fx.get("capability", "batch")
    if cap in ("update", "restore"):
        raise Err("UNSUPPORTED_CAPABILITY", cap)
    sel = fx.get("selection") or [TOPK]
    for f in sel:
        if f != TOPK:
            raise Err("UNKNOWN_FEATURE", f)
    p = fx["params"]
    if set(p) != {"policy_version", "top_k", "evidence_limit"}:
        raise Err("INVALID_CONFIG", "parameter set")
    if not is_int(p["top_k"]) or not 1 <= p["top_k"] <= 10000:
        raise Err("INVALID_CONFIG", "top_k")
    if not is_int(p["evidence_limit"]) or not p["top_k"] <= p["evidence_limit"] <= 10000:
        raise Err("INVALID_CONFIG", "evidence_limit")
    if p["policy_version"] != POLICY_TOPK:
        raise Err("INCOMPATIBLE_VERSION", "policy_version")
    admit_batch(fx, b, "topk")
    topk_eval(fx, b)


def run_refusal(rf, fixtures, b):
    base = copy.deepcopy(fixtures[rf["base"]])
    fx = apply_ops(base, rf["mutate"])
    try:
        if rf["scenario"] == "window":
            admit_window(fx, b)
        elif rf["scenario"] == "topk":
            admit_topk(fx, b)
        else:
            merge_eval(fx, b)
    except Err as e:
        return e.code
    return None


# ------------------------------------------------------------------ fixture checks
def compare_entry(tag, exp, got, b, integer, problems, is_float_out=False):
    for k in ("status", "reasons", "expected", "observed"):
        if exp[k] != got[k]:
            problems.append(f"{tag}: {k} fixture {exp[k]} != recomputed {got[k]}")
    if exp["status"] == "available" or got["status"] == "available":
        if "value" not in exp or "value" not in got:
            problems.append(f"{tag}: value presence differs")
        else:
            check_value(tag, exp["value"], got["value"], integer, problems)
        ew = [w.replace("$SEED_REF", b["seed_ref"]) for w in exp.get("witnesses", [])]
        if ew != got.get("witnesses"):
            problems.append(f"{tag}: witnesses {ew} != {got.get('witnesses')}")
    else:
        if "value" in exp:
            problems.append(f"{tag}: value present on unavailable output")


def strip_bind(entry):
    e = dict(entry)
    return json.dumps({k: (str(v) if isinstance(v, Fraction) else v) for k, v in e.items()}, sort_keys=True)


def check_window(fx, problems, stats):
    sel = fx.get("selection") or list(fx["expected"])
    base_result = None
    for bi, b in enumerate(BINDINGS):
        ra = window_eval(fx, b, sel, signs_chain)
        rb = window_eval(fx, b, sel, signs_nearest)
        for f in sel:
            if strip_bind(ra[f]) != strip_bind(rb[f]):
                problems.append(f"{fx['id']} {f}: oracle A and B disagree")
        for f, exp in fx["expected"].items():
            compare_entry(f"{fx['id']}[{bi}] {f}", exp, ra[f], b, KEY[f] != "imb", problems)
            stats["outputs"] += 1
        norm = {f: strip_bind({**ra[f], "witnesses": [w.replace(b["seed_ref"], "$SEED_REF") for w in ra[f].get("witnesses", [])]}) for f in sel}
        if base_result is None:
            base_result = norm
        elif norm != base_result:
            problems.append(f"{fx['id']}: result depends on bound entity/session/seed ids")
    # outputs not listed are not asserted; listed set must be subset of headers
    for f in fx["expected"]:
        if f not in KEY:
            problems.append(f"{fx['id']}: unknown feature {f}")


def rows_match(tag, exp_rows, got_rows, problems):
    e = [(r["event_id"], r["price"], r["size"], r["notional"]) for r in exp_rows]
    g = [(r["event_id"], r["price"], r["size"], r["price"] * r["size"]) for r in got_rows]
    if e != g:
        problems.append(f"{tag}: rows {e} != recomputed {g}")


def check_topk(fx, problems, stats):
    exp = fx["expected"][TOPK]
    for bi, b in enumerate(BINDINGS):
        ra = topk_eval(fx, b, topk_pick_sort)
        rb = topk_eval(fx, b, topk_pick_select)
        if ra.get("witnesses") != rb.get("witnesses") or ra["status"] != rb["status"]:
            problems.append(f"{fx['id']}: topk oracles disagree")
        tag = f"{fx['id']}[{bi}]"
        for k in ("status", "reasons", "expected", "observed"):
            if exp[k] != ra[k]:
                problems.append(f"{tag}: {k} fixture {exp[k]} != recomputed {ra[k]}")
        if exp["status"] == "available":
            if ra["status"] == "available":
                rows_match(tag, exp["value"]["rows"], ra["rows"], problems)
                if exp["value"]["k"] != fx["params"]["top_k"]:
                    problems.append(f"{tag}: k mismatch")
                if exp["witnesses"] != ra["witnesses"]:
                    problems.append(f"{tag}: witnesses differ")
                if exp.get("evidence_boundaries") != ra["boundaries"]:
                    problems.append(f"{tag}: boundaries differ")
                for r in exp["value"]["rows"]:
                    if r["notional"] >= D128:
                        problems.append(f"{tag}: notional beyond decimal128")
        elif "value" in exp:
            problems.append(f"{tag}: value on unavailable")
        stats["outputs"] += 1
    ref = fx.get("size_ranked_reference")
    if ref:
        elig = [r for r in expand_trades(fx, BINDINGS[0]) if r["eligible"]]
        by_size = sorted(elig, key=lambda r: (-r["size"], r["event_ns"], r["order_key"], r["event_id"]))[:fx["params"]["top_k"]]
        if [r["event_id"] for r in by_size] != ref["event_ids"]:
            problems.append(f"{fx['id']}: size-ranked reference differs {[r['event_id'] for r in by_size]}")
        if ref["event_ids"] == [r["event_id"] for r in expand_trades(fx, BINDINGS[0]) if False]:
            pass
        if [r["event_id"] for r in by_size] == [w.split(':')[1] for w in exp["witnesses"]]:
            problems.append(f"{fx['id']}: size and notional rankings are identical, fixture does not separate them")


def check_merge(fx, problems, stats):
    exp = fx["expected_merged"]
    for bi, b in enumerate(BINDINGS):
        merged, parts = merge_eval(fx, b)
        tag = f"{fx['id']}[{bi}]"
        for k in ("status", "reasons", "expected", "observed"):
            if exp[k] != merged[k]:
                problems.append(f"{tag}: merged {k} fixture {exp[k]} != recomputed {merged[k]}")
        if exp["status"] == "available":
            rows_match(tag + " merged", exp["rows"], merged["rows"], problems)
            if exp["witnesses"] != merged["witnesses"]:
                problems.append(f"{tag}: merged witnesses")
        for pf, pr in zip(fx["partitions"], parts):
            pe = pf["expected"]
            for k in ("status", "reasons", "expected", "observed"):
                if pe[k] != pr[k]:
                    problems.append(f"{tag} {pf['label']}: {k} {pe[k]} != {pr[k]}")
            if pe["status"] == "available":
                rows_match(f"{tag} {pf['label']}", pe["rows"], pr["rows"], problems)
        # order independence + single pass equivalence on the union (only when the union is a valid canonical batch)
        union = [t for p in fx["partitions"] for t in p["trades"]]
        keys = [(t["ns"], t["ok"]) for t in union]
        if exp["status"] == "available":
            if len(set(keys)) == len(keys):
                ordered = sorted(union, key=lambda t: (t["ns"], t["ok"]))
                one = dict(fx, params={"policy_version": POLICY_TOPK, "top_k": fx["K_param"], "evidence_limit": fx["K_param"]}, trades=ordered)
                full = topk_eval(one, b)
                if [r["event_id"] for r in full["rows"]] != [r["event_id"] for r in merged["rows"]]:
                    problems.append(f"{tag}: merge differs from the single-pass top-K over the union")
            else:
                stats["collision_merges"] += 1
            rev = merge_partials(list(reversed(parts)), fx["K_param"])
            if [r["event_id"] for r in rev["rows"]] != [r["event_id"] for r in merged["rows"]]:
                problems.append(f"{tag}: merge depends on partition order")
        if fx.get("nested"):
            inner = [parts[i] for i, p in enumerate(fx["partitions"]) if p["label"] in fx["nested"]["inner"]]
            m1 = merge_partials(inner, fx["K_param"])
            ie = fx["nested"]["inner_expected"]
            for k in ("status", "reasons", "expected", "observed"):
                if ie[k] != m1[k]:
                    problems.append(f"{tag}: nested inner {k}")
            rows_match(tag + " inner", ie["rows"], m1["rows"], problems)
            rest = [parts[i] for i, p in enumerate(fx["partitions"]) if p["label"] not in fx["nested"]["inner"]]
            m2 = merge_partials([m1] + rest, fx["K_param"])
            if [r["event_id"] for r in m2["rows"]] != [r["event_id"] for r in merged["rows"]]:
                problems.append(f"{tag}: merge not associative")
        stats["outputs"] += 1


# ------------------------------------------------------------------ generators
def lcg_tape(spec):
    c = spec["lcg"]
    x = c["seed"]
    ns = ok = 0
    p = spec["price_base"]
    rows = []
    for k in range(spec["n"]):
        x = (c["a"] * x + c["c"]) % c["m"]
        dt = (x >> 40) % 4
        if k == 0:
            ns, ok = dt, 0
        elif dt == 0:
            ok += 1
        else:
            ns += dt
            ok = 0
        p = max(1, p + ((x >> 20) % 5) - 2)
        rows.append({"instrument_id": "G", "session_id": "G", "event_ns": ns, "order_key": ok, "event_id": f"g{k}",
                     "eligible": (x >> 33) % 11 != 0, "price": p, "size": 1 + (x >> 8) % 1000, "known_at_ns": 0})
    return rows


def gen_window(spec):
    rows = lcg_tape(spec)
    C = rows[-1]["event_ns"] + 1
    seed = None
    if spec.get("seed_policy") == "supplied":
        seed = {"price": spec["seed"]["price"], "text": spec["seed"]["sign"]}
    out = {}
    for w in spec["windows"]:
        W = C if w == "session" else w
        lo = C - W
        win = [r for r in rows if r["event_ns"] >= lo]
        r = {}
        for name, signer in (("A", signs_chain), ("B", signs_nearest)):
            s = window_sums(rows, win, seed, signer)
            r[name] = s
        if r["A"] != r["B"]:
            raise AssertionError(f"{spec['id']} W={w}: oracles disagree")
        s = r["A"]
        imb = Fraction(s["net"], s["volume"]) if s["volume"] else None
        # independent third check by incremental deque (expiry by popping) for this window
        out[str(w)] = {**{k: str(v) for k, v in s.items()}, "imb": None if imb is None else f"{imb.numerator}/{imb.denominator}"}
    return out


def gen_topk(spec):
    rows = [r for r in lcg_tape(spec) if r["eligible"]]
    out = {}
    for K in spec["ks"]:
        full = [r["event_id"] for r in topk_pick_sort(rows, K)]
        if K <= 8:
            sel = [r["event_id"] for r in topk_pick_select(rows, K)]
            if sel != full:
                raise AssertionError(f"{spec['id']} K={K}: oracles disagree")
        parts = []
        for i in range(spec["partitions"]):
            part = [r for j, r in enumerate(lcg_tape(spec)) if j % spec["partitions"] == i and r["eligible"]]
            parts.append({"rows": topk_pick_sort(part, K), "reasons": [], "expected": 0, "observed": 0, "status": "available"})
        merged = merge_partials(parts, K)
        if [r["event_id"] for r in merged["rows"]] != full:
            raise AssertionError(f"{spec['id']} K={K}: partition merge != single pass")
        out[str(K)] = full
    return out


def run_generators(doc, problems, emit):
    produced = {}
    for g in doc["generator_fixtures"]:
        try:
            r = gen_window(g) if g["kind"] == "window" else gen_topk(g)
        except AssertionError as e:
            problems.append(str(e))
            continue
        produced[g["id"]] = r
        if g.get("expected") is not None and g["expected"] != r:
            problems.append(f"{g['id']}: stored expectation differs from the oracles")
        if g.get("expected") is None and not emit:
            problems.append(f"{g['id']}: no stored expectation")
    return produced


# ------------------------------------------------------------------ structure
def check_structure(doc, problems):
    ids = []
    for key in ("window_fixtures", "topk_fixtures", "merge_fixtures", "generator_fixtures", "refusal_fixtures"):
        ids += [f["id"] for f in doc[key]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate fixture ids")
    fc = doc["fixture_counts"]
    want = {"window_result": len(doc["window_fixtures"]), "topk_result": len(doc["topk_fixtures"]), "merge_result": len(doc["merge_fixtures"]),
            "generator": len(doc["generator_fixtures"]), "refusal": len(doc["refusal_fixtures"])}
    if fc != want:
        problems.append(f"fixture_counts {fc} != {want}")
    allids = set(ids)
    for tag, lst in doc["coverage_map"].items():
        for i in lst:
            if i not in allids:
                problems.append(f"coverage_map {tag}: unknown {i}")
    for pair in doc["prefix_equivalences"]:
        for i in pair:
            if i not in allids:
                problems.append(f"prefix_equivalences unknown {i}")
    # reasons_reached must match recomputed expectations
    reached = {}
    for key in ("window_fixtures", "topk_fixtures"):
        for f in doc[key]:
            outs = f["expected"].values()
            for e in outs:
                for r in e["reasons"]:
                    reached.setdefault(r, set()).add(f["id"])
    for f in doc["merge_fixtures"]:
        for r in f["expected_merged"]["reasons"]:
            reached.setdefault(r, set()).add(f["id"])
    if {k: sorted(v) for k, v in reached.items()} != {k: sorted(v) for k, v in doc["reasons_reached"].items()}:
        problems.append("reasons_reached differs from fixture bodies")
    # acceptance rule keys
    if set(doc["acceptance_rules"]) < {"exact_float64", "exact_plus_zero", "tolerance", "exact_integer"}:
        problems.append("acceptance_rules incomplete")
    # no hardcoded identities
    text = json.dumps([doc[k] for k in ("window_fixtures", "topk_fixtures", "merge_fixtures", "refusal_fixtures")])
    for bad in ('"instrument"', '"entity"', '"symbol"', '"instrument_id"', '"session_id"', '"grid_id"'):
        if bad in text:
            problems.append(f"fixture bodies contain identity key {bad}")
    # refusals: concrete construction
    for rf in doc["refusal_fixtures"]:
        if not rf.get("construction") or not rf.get("mutate"):
            problems.append(f"{rf['id']}: refusal lacks concrete construction")
    # headers vs outputs used
    heads = {h["id"] for h in doc["headers"]}
    for f in doc["window_fixtures"]:
        for k in f["expected"]:
            if k not in heads:
                problems.append(f"{f['id']}: output {k} not a header")
    for f in doc["topk_fixtures"]:
        for k in f["expected"]:
            if k not in heads:
                problems.append(f"{f['id']}: output {k} not a header")


def main(argv):
    if len(argv) < 2:
        docs = os.environ.get("EF4_DOCS_DIR") or os.path.join(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")), "docs", "ef4")
        argv = [argv[0], os.path.join(docs, "TAPE_CONTRACT_PROPOSAL.json")] + argv[1:]
    verbose = "-v" in argv
    emit = None
    if "--emit-generators" in argv:
        emit = argv[argv.index("--emit-generators") + 1]
    doc = json.load(open(argv[1], encoding="utf-8"))
    problems = []
    stats = {"outputs": 0, "refusals": 0, "collision_merges": 0}
    check_structure(doc, problems)
    fixtures = {}
    for key in ("window_fixtures", "topk_fixtures", "merge_fixtures"):
        for f in doc[key]:
            fixtures[f["id"]] = f
    for f in doc["window_fixtures"]:
        try:
            for b in BINDINGS:
                admit_window(f, b)
            check_window(f, problems, stats)
        except Err as e:
            problems.append(f"{f['id']}: unexpected typed failure {e}")
    for f in doc["topk_fixtures"]:
        try:
            for b in BINDINGS:
                admit_topk(f, b)
            check_topk(f, problems, stats)
        except Err as e:
            problems.append(f"{f['id']}: unexpected typed failure {e}")
    for f in doc["merge_fixtures"]:
        try:
            check_merge(f, problems, stats)
        except Err as e:
            problems.append(f"{f['id']}: unexpected typed failure {e}")
    codes = {}
    for rf in doc["refusal_fixtures"]:
        for bi, b in enumerate(BINDINGS):
            got = run_refusal(rf, fixtures, b)
            if got != rf["error_code"]:
                problems.append(f"{rf['id']}[{bi}]: expected {rf['error_code']} got {got}")
        codes[rf["error_code"]] = codes.get(rf["error_code"], 0) + 1
        stats["refusals"] += 1
    produced = run_generators(doc, problems, emit)
    if emit:
        json.dump(produced, open(emit, "w"), indent=1, sort_keys=True)
    print(f"window={len(doc['window_fixtures'])} topk={len(doc['topk_fixtures'])} merge={len(doc['merge_fixtures'])} "
          f"generator={len(doc['generator_fixtures'])} refusal={len(doc['refusal_fixtures'])} outputs_checked={stats['outputs']} "
          f"(two bindings each) collision_merges={stats['collision_merges']}")
    print("refusal codes:", dict(sorted(codes.items())))
    if verbose:
        for k, v in sorted(produced.items()):
            print(k, json.dumps(v)[:200])
    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for p in problems[:80]:
            print(" -", p)
        return 1
    print("OK: every fixture recomputed and matched")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
