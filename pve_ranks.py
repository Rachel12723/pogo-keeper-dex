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
    """Per type, rank each attacker FORM (not family) and keep the notable ones.

    A 'candidate' is (family, shadow?) — a family's best shadow form and best non-shadow
    form are separate candidates, each keeping its own board position. Every candidate gets:
      rank  (1st) = its position on the full board (all forms, all rarities)
      crank (2nd) = its position among the NON-LOCKED candidates (legendary/mythical/UB removed)
      trank (3rd) = its position among the non-locked AND non-shadow candidates
                    (only non-shadow forms get this — shadow can't be traded, so it's the best
                     copy you can catch a high-IV, tradeable version of)
    Keepers: non-shadow candidates in the top-6 by trank, plus shadow candidates in the top-6
    by crank (so a strong shadow like Shadow Mamoswine still shows, with rank+crank and no trank).
    Owned legendaries/mythicals/UBs are kept family-deduped (best form) if in the top-20 overall,
    shown with rank only."""
    raw = json.load(open(os.path.join(DATA, "pve_type_ranks_raw.json")))
    try:  # best fast / charged move per board entry (scraped alongside the ranks)
        mv = json.load(open(os.path.join(DATA, "pve_type_moves.json")))
    except (OSError, ValueError):
        mv = {}
    result = {}
    for tp, arr in raw.items():
        cand = {}  # (fam, is_shadow) -> (pos, dex, tok)  best form of that candidate
        for i, suf in enumerate(arr):
            dex, tok = parse(suf)
            key = (dex_fam.get(dex, str(dex)), is_shadow(tok))
            if key not in cand:
                cand[key] = (i + 1, dex, tok)
        ordered = sorted(cand.items(), key=lambda kv: kv[1][0])
        # rank the non-locked candidates: crank over all, trank over the non-shadow subset.
        crank_of, trank_of, nc, nt = {}, {}, 0, 0
        for (fam, sh), (pos, dex, tok) in ordered:
            if dex in locked_dex:
                continue
            nc += 1
            crank_of[(fam, sh)] = nc
            if not sh:
                nt += 1
                trank_of[(fam, sh)] = nt
        keepers = []
        for (fam, sh), (pos, dex, tok) in ordered:
            if dex in locked_dex:
                # owned legendary/mythical/UB: keep each candidate (best non-shadow form and best
                # shadow form are separate) inside the top-20 overall, shown with rank only. The
                # (fam, shadow) key already collapses same-rarity forms (e.g. White/Black Kyurem).
                if pos > LOCKED_OVERALL_CAP:
                    continue
                crank = trank = None
            else:
                crank = crank_of[(fam, sh)]
                trank = trank_of.get((fam, sh))  # None for shadow candidates
                if sh:
                    if crank > TOP_N_CATCHABLE:
                        continue
                elif trank > TOP_N_CATCHABLE:
                    continue
            keepers.append({"fam": fam, "rank": pos, "dex": dex, "crank": crank, "trank": trank,
                            "form": form_name(dex, tok), "base": dex_base.get(dex),
                            "locked": dex in locked_dex, "shadow": sh,
                            "moves": " / ".join(x for x in mv.get(tp, {}).get(arr[pos - 1], []) if x)})
        result[tp] = keepers
    return result


MAX_TOP_N = 5  # Max Battle attackers kept per type (the PGHub Max boards are short: 3-32 rows)


def max_by_dex():
    """dex -> Max Battle (Dynamax / Gigantamax) usages: the top MAX_TOP_N attacker FAMILIES of each
    type on PGHub's best-dynamax-per-type board (data/max_type_ranks.json). Rank is the board
    position of the family's best form; 'tier' is PGHub's tier letter. Fail-soft if the file's absent."""
    try:
        raw = json.load(open(os.path.join(DATA, "max_type_ranks.json")))
    except (OSError, ValueError):
        return {}
    m = {}
    for tp, rows in raw.items():
        seen = set()
        for i, r in enumerate(rows):
            dex, _tok = parse(r["token"])
            fam = dex_fam.get(dex, str(dex))
            if fam in seen:
                continue
            seen.add(fam)
            if len(seen) > MAX_TOP_N:
                break
            m.setdefault(dex, []).append(
                {"type": tp.capitalize(), "rank": i + 1, "form": r["name"], "tier": r.get("tier", ""),
                 "moves": " / ".join(x for x in (r.get("fast"), r.get("max")) if x)})
    return m


def by_dex():
    """dex -> list of PvE keeper usages. A family can now have two lines for one type
    (its non-shadow form and its shadow form), each with its own ranks."""
    res = compute()
    m = {}
    for tp, ks in res.items():
        for k in ks:
            m.setdefault(k["dex"], []).append(
                {"type": tp.capitalize(), "rank": k["rank"], "crank": k["crank"],
                 "trank": k["trank"], "form": k["form"], "base": k["base"],
                 "locked": k["locked"], "shadow": k["shadow"], "moves": k.get("moves", "")})
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
