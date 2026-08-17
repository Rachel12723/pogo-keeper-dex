#!/usr/bin/env python3
"""Compute PvE raid-attacker keepers per type from PGHub per-type boards.

Rule (agreed): exclude raid-locked (legendary/mythical/ultra-beast) from the pool so
they don't demote catchable mons. Keep the top-10 catchable families per type. ALSO
keep any raid-locked family that sits in the top-10 OVERALL (you own it -> keeper).
Each keeper carries its real PGHub overall rank (best form's position) + that form.
Source: data/pve_type_ranks_raw.json (href suffix arrays, position = rank).
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TOP_N_CATCHABLE = 6    # catchable families kept per type (strict)
LOCKED_OVERALL_CAP = 20  # owned legendaries/mythicals/UBs kept if within top-20 overall (generous)

gm = json.load(open(os.path.join(DATA, "gamemaster.json")))
poke = gm["pokemon"] if isinstance(gm, dict) else gm

# dex -> base info
locked_dex, dex_name, dex_fam = set(), {}, {}
for p in poke:
    d = p.get("dex")
    if not d:
        continue
    tags = set(p.get("tags") or [])
    if {"legendary", "mythical", "ultrabeast"} & tags:
        locked_dex.add(d)
    # prefer plainest speciesId as the dex's base name/family
    base = re.sub(r"\s*\(.*?\)", "", p["speciesName"]).strip()
    sid = p["speciesId"]
    fam = (p.get("family") or {}).get("id") or sid
    if d not in dex_name or len(sid) < dex_name[d][1]:
        dex_name[d] = (base, len(sid), fam)
dex_base = {d: v[0] for d, v in dex_name.items()}
dex_fam = {d: v[2] for d, v in dex_name.items()}

TOK_PRETTY = {
    "mega": "Mega", "mega_x": "Mega X", "mega_y": "Mega Y", "primal": "Primal",
    "shadow": "Shadow", "origin": "Origin", "alola": "Alolan", "galarian": "Galarian",
    "hisuian": "Hisuian", "paldean": "Paldean", "alola_shadow": "Shadow Alolan",
    "apex_shadow": "Apex Shadow", "therian": "Therian", "incarnate": "Incarnate",
    "standard": "", "standard_shadow": "Shadow", "galarian_standard": "Galarian",
    "galarian_standard_shadow": "Shadow Galarian", "crowned_sword": "Crowned Sword",
    "crowned_shield": "Crowned Shield", "dusk_mane": "Dusk Mane", "dawn_wings": "Dawn Wings",
    "black": "Black", "white": "White", "rapid_strike": "Rapid Strike",
    "single_strike": "Single Strike", "incarnate_shadow": "Shadow Incarnate",
    "therian_shadow": "Shadow Therian", "hero": "Hero", "sky": "Sky",
}

def parse(suffix):
    m = re.match(r"^(\d+)(?:-(.+))?$", suffix)
    dex = int(m.group(1)); tok = (m.group(2) or "").lower()
    return dex, tok

def form_name(dex, tok):
    base = dex_base.get(dex, f"#{dex}")
    pretty = TOK_PRETTY.get(tok, tok.replace("_", " ").title() if tok else "")
    return f"{pretty} {base}".strip() if pretty else base

def is_shadow(tok):
    return "shadow" in tok


def compute():
    raw = json.load(open(os.path.join(DATA, "pve_type_ranks_raw.json")))
    result = {}
    for tp, arr in raw.items():
        fam_best = {}     # fam -> (pos, dex, tok)  best form overall (shadow allowed)
        fam_best_ns = {}  # fam -> (pos, dex, tok)  best NON-shadow form (tradeable-catchable)
        for i, suf in enumerate(arr):
            pos = i + 1
            dex, tok = parse(suf)
            fam = dex_fam.get(dex, str(dex))
            if fam not in fam_best:
                fam_best[fam] = (pos, dex, tok)
            if not is_shadow(tok) and fam not in fam_best_ns:
                fam_best_ns[fam] = (pos, dex, tok)
        # crank = family rank within the non-locked pool, ordered by best overall pos
        # (excludes legendary/mythical/UB; shadow forms still count).
        crank_of, n_catch = {}, 0
        for fam, (pos, dex, tok) in sorted(fam_best.items(), key=lambda kv: kv[1][0]):
            if dex in locked_dex:
                continue
            n_catch += 1
            crank_of[fam] = n_catch
        # trank = family rank within the non-locked AND non-shadow pool, ordered by best
        # non-shadow pos. This is the pool we cap at TOP_N_CATCHABLE: the best attacker we can
        # actually catch a high-IV, tradeable copy of (shadow can't be traded).
        trank_of, n_ns = {}, 0
        for fam, (pos, dex, tok) in sorted(fam_best_ns.items(), key=lambda kv: kv[1][0]):
            if dex in locked_dex:
                continue
            n_ns += 1
            trank_of[fam] = n_ns
        keepers = []
        for fam, (pos, dex, tok) in sorted(fam_best.items(), key=lambda kv: kv[1][0]):
            locked = dex in locked_dex
            crank = trank = None
            if locked:
                if pos > LOCKED_OVERALL_CAP:
                    continue
            else:
                trank = trank_of.get(fam)
                # non-locked keepers are the top-6 by third (non-shadow) rank; a family with
                # no non-shadow board entry (shadow-only) is not a catchable-tradeable keeper.
                if trank is None or trank > TOP_N_CATCHABLE:
                    continue
                crank = crank_of.get(fam)
            keepers.append({"fam": fam, "rank": pos, "dex": dex, "crank": crank, "trank": trank,
                            "form": form_name(dex, tok), "base": dex_base.get(dex),
                            "locked": locked})
        result[tp] = keepers
    return result

def by_dex():
    """dex -> list of PvE keeper usages {type, rank, form, base, locked}.
    All forms of a species share a dex, so a family's PvE lines attach by member dex."""
    res = compute()
    m = {}
    for tp, ks in res.items():
        for k in ks:
            m.setdefault(k["dex"], []).append(
                {"type": tp.capitalize(), "rank": k["rank"], "crank": k["crank"],
                 "trank": k["trank"], "form": k["form"], "base": k["base"], "locked": k["locked"]})
    return m


if __name__ == "__main__":
    res = compute()
    json.dump(res, open(os.path.join(DATA, "pve_type_ranks.json"), "w"), indent=1)
    print("wrote data/pve_type_ranks.json\n")
    TYPE_TITLE = lambda t: t.capitalize()
    for tp in ["fire","water","grass","electric","ice","fighting","poison","ground",
               "flying","psychic","bug","rock","ghost","dragon","dark","steel","fairy","normal"]:
        ks = res[tp]
        catch = [k for k in ks if not k["locked"]]
        lock = [k for k in ks if k["locked"]]
        print(f"=== {TYPE_TITLE(tp)} ===")
        print("  catchable:", ", ".join(f'{k["form"]} #{k["rank"]}' for k in catch))
        print("  locked   :", ", ".join(f'{k["base"]} #{k["rank"]}' for k in lock))
