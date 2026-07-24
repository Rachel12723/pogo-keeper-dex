#!/usr/bin/env python3
"""Complete Pokédex ('our flavor') — every released species, folded by family.

Source: pvpoke's Pokémon GO gamemaster (data/gamemaster.json) + our rank pools.
- Cosmetic COSTUME forms are de-duplicated (same dex+types+stats as the base) so a
  species shows once; real alt-formes (Deoxys, Rotom, regionals…) survive.
- One row per evolutionary family at its lowest ('first appearance') dex #, by dex.
- League / Purpose lists ALL usage: each PvP league a form ranks in (LC50/GL·UL·ML60),
  plus 'Mega' if the family has a Mega/Primal (a PvE raid option). Best form & rank is
  one line per usage. Families with no usage show 'Collection only' + the folded forms.
- Far-apart folded members get a pointer row. NOTE: non-mega PvE attacker tiers are
  not in this dataset (PvP-only), so raid-only attackers read 'Collection only'.
Regenerate:  python3 build_dex.py
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
FAR = 5

LEAGUES = [("little", "LC", 50), ("great", "GL", 60), ("ultra", "UL", 60), ("master", "ML", 60)]
LORDER = {k: i for i, (k, _s, _c) in enumerate(LEAGUES)}
SHORT = {k: s for k, s, _c in LEAGUES}

pool, mvpool = {}, {}
for key, _s, cut in LEAGUES:
    arr = json.load(open(os.path.join(DATA, f"rankings-{key}.json")))
    pool[key] = {e["speciesId"]: i + 1 for i, e in enumerate(arr[:cut])}
    mvpool[key] = {e["speciesId"]: " / ".join(m.replace("_", " ").title() for m in e.get("moveset", []))
                   for e in arr[:cut]}

gm = json.load(open(os.path.join(DATA, "gamemaster.json")))
poke = gm["pokemon"] if isinstance(gm, dict) else gm
by = {p["speciesId"]: p for p in poke}


def is_mega(p):
    return "mega" in (p.get("tags") or []) or "_mega" in p["speciesId"] or "primal" in p["speciesId"]


def plain(name):
    return re.sub(r"\s*\(.*?\)", "", name).strip()


# dex-forms: released, not shadow, not mega/primal
cand = [p for p in poke if p.get("dex") and p.get("released")
        and "shadow" not in (p.get("tags") or []) and "_shadow" not in p["speciesId"]
        and not is_mega(p)]

# de-dupe cosmetic costumes: same (dex, types, stats) -> keep plainest speciesId
canon = {}
for p in sorted(cand, key=lambda p: (len(p["speciesId"]), p["speciesId"])):
    bs = p["baseStats"]
    k = (p["dex"], tuple(p["types"]), bs["atk"], bs["def"], bs["hp"])
    canon.setdefault(k, p)
forms = list(canon.values())


def fkey_of(sid):
    return (by.get(sid, {}).get("family") or {}).get("id") or sid


# group into families
fams = {}
for p in forms:
    fams.setdefault(fkey_of(p["speciesId"]), []).append(p)

# megas per family
megafams = {}
for p in poke:
    if p.get("released") and is_mega(p):
        base = re.split(r"_mega|_primal", p["speciesId"])[0]
        megafams.setdefault(fkey_of(base), []).append(p["speciesName"])

LOW, HIGH = "low ATK / high bulk", "high ATK"


def ranks(vid):
    return [(k, pool[k][vid]) for k, _s, _c in LEAGUES if vid in pool[k]]


rows, pointers = [], []
for key, members in fams.items():
    members = sorted(members, key=lambda p: (p["dex"], len(p["speciesId"]), p["speciesId"]))
    anchor = members[0]
    adex, aname = anchor["dex"], plain(anchor["speciesName"])

    usages = []
    for m in members:
        fid = m["speciesId"]
        for pref, vid in [("", fid), ("Shadow ", fid + "_shadow")]:
            for k, r in ranks(vid):
                usages.append({"kind": 0, "ord": LORDER[k], "rank": r, "lp": SHORT[k],
                               "best": f'{pref}{m["speciesName"]} #{r}',
                               "iv": LOW if k != "master" else HIGH, "moves": mvpool[k][vid]})
    for mname in megafams.get(key, []):
        usages.append({"kind": 1, "ord": 9, "rank": 0, "lp": "Mega",
                       "best": f"{mname} — PvE raids", "iv": HIGH, "moves": "—"})
    usages.sort(key=lambda u: (u["kind"], u["ord"], u["rank"]))

    chain = " · ".join(f'{m["speciesName"]} <span class=dex>#{m["dex"]}</span>' for m in members)
    rows.append({"dex": adex, "name": aname, "usages": usages, "chain": chain,
                 "total": len(usages)})
    for m in members:
        if m is not anchor and m["dex"] - adex > FAR:
            pointers.append((m["dex"], plain(m["speciesName"]), adex, aname))

rows.sort(key=lambda r: r["dex"])
items = [("fam", r["dex"], r) for r in rows] + [("ptr", d, (d, n, a, an)) for (d, n, a, an) in pointers]
items.sort(key=lambda x: (x[1], 0 if x[0] == "fam" else 1))

# ---- CSV (one row per family) ----
with open(os.path.join(HERE, "dex.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Dex", "Spawn", "League / Purpose", "Best form & rank", "Folded forms", "Total"])
    for r in rows:
        lp = " ".join(sorted({u["lp"] for u in r["usages"]})) or "Collection only"
        best = " | ".join(f'{u["lp"]}: {re.sub("<.*?>","",u["best"])}' for u in r["usages"])
        forms = re.sub("<.*?>", "", r["chain"])
        w.writerow([r["dex"], r["name"], lp, best, forms, r["total"] or ""])
print(f"wrote dex.csv  (families: {len(rows)}, pointers: {len(pointers)})")

# ---- HTML ----
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"
h = ["""<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Complete Pokédex — folded by family</title>
<style>
:root{color-scheme:light}
body{font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:24px;background:#fff;color:#1b2733}
h1{font-size:24px;margin:0 0 4px} .sub{color:#5b6b7a;margin:0 0 16px;max-width:82ch}
table{border-collapse:collapse;width:100%}
td,th{padding:6px 9px;border-bottom:1px solid #edf1f5;vertical-align:middle;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#6b7b8a}
img{width:42px;height:42px;object-fit:contain;vertical-align:middle}
.mon{font-weight:600;white-space:nowrap} .dex{color:#9aa7b4;font-size:12px;font-variant-numeric:tabular-nums}
.note{color:#6b7b8a;font-size:13px} .keep{text-align:center} .tot{text-align:center;font-weight:700;color:#b26b00}
.coll{color:#9aa7b4}
.ptr td{background:#fafbfc;color:#9aa7b4;font-size:12px}
.lg{display:inline-block;padding:1px 6px;border-radius:9px;font-size:11px;font-weight:700}
.LC{background:#efe7f7;color:#6b3fa0} .GL{background:#e3f6ea;color:#14713a}
.UL{background:#fdeee2;color:#9a4a12} .ML{background:#e3eefb;color:#1e5fa8} .Mega{background:#fce4ec;color:#b0146b}
</style>
<h1>Complete Pokédex — folded by family</h1>
<p style="margin:0 0 10px"><a href="pokedex.html">→ ranked-only by dex #</a> &nbsp;·&nbsp; <a href="rankings.html">→ by League</a> &nbsp;·&nbsp; <a href="index.html">→ Ultra Unlock event</a></p>
<p class=sub>Every released species in Pokémon GO (pvpoke gamemaster), <b>one row per family</b> at its first dex #.
Cosmetic costumes are de-duplicated. <b>League / Purpose</b> lists every usage — each PvP league a form ranks in
(LC top 50 / GL·UL·ML top 60) plus <span class="lg Mega">Mega</span> if the family has a Mega/Primal (a PvE raid
option), one line each. No usage → <span class=coll>Collection only</span> with the folded forms.
<i>Note: non-mega PvE raid tiers aren't in this PvP dataset, so raid-only attackers may read Collection only.</i></p>
<table><tr><th></th><th>Spawn</th><th>League / Purpose</th><th>Best form &amp; rank</th>
<th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>"""]
for kind, _d, payload in items:
    if kind == "ptr":
        d, n, a, an = payload
        h.append(f'<tr class=ptr><td></td><td>{n} <span class=dex>#{d}</span></td>'
                 f'<td colspan=6>→ folded into #{a} ({an} family)</td></tr>')
        continue
    r = payload
    img = f'<img loading=lazy src="{ART.format(r["dex"])}" alt="">'
    lines = [dict(u, keep="1") for u in r["usages"]]
    lines.append({"lp": "Collection only", "best": r["chain"], "iv": "—", "moves": "—", "keep": "", "coll": True})
    n = len(lines)
    totval = r["total"] or ""
    for j, u in enumerate(lines):
        if j == 0:
            c0 = (f'<td rowspan={n} style="text-align:center">{img}</td>'
                  f'<td rowspan={n} class=mon>{r["name"]}<br><span class=dex>#{r["dex"]}</span></td>')
            ct = f'<td rowspan={n} class=tot>{totval}</td>'
        else:
            c0 = ct = ""
        if u.get("coll"):
            lp_html, best_html = '<span class=coll>Collection only</span>', f'<span class=note>{u["best"]}</span>'
        else:
            lp_html, best_html = f'<span class="lg {u["lp"]}">{u["lp"]}</span>', f'<b>{u["best"]}</b>'
        h.append(f'<tr>{c0}<td>{lp_html}</td><td class=rank>{best_html}</td>'
                 f'<td class=note>{u["iv"]}</td><td class=note>{u["moves"]}</td>'
                 f'<td class=keep>{u["keep"]}</td>{ct}</tr>')
h.append("</table></html>")
open(os.path.join(HERE, "dex.html"), "w").write("\n".join(h))
print("wrote dex.html")
