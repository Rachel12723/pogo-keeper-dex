#!/usr/bin/env python3
"""Complete Pokédex ('our flavor') — every released species, folded by family.

One row per evolutionary family (gamemaster family.id), placed at the family's
lowest ('first appearance') dex #, ordered by dex. Evolutions + regional forms
fold in; shadow/mega are not separate rows (shadow used only to annotate ranks).
PvP ranks (our 4 pools) overlay where a form is relevant. Members whose dex is far
from the anchor get a pointer row ("→ folded into #X"). Regenerate:
    python3 build_dex.py
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
FAR = 5  # dex gap beyond which a folded member also gets a pointer row

LEAGUES = [("little", "LC", 50), ("great", "GL", 60), ("ultra", "UL", 60), ("master", "ML", 60)]
LORDER = {k: i for i, (k, _s, _c) in enumerate(LEAGUES)}
SHORT = {k: s for k, s, _c in LEAGUES}

# rank pools: speciesId -> (short, rank) per league  (+ moveset lookup)
pool = {}          # league key -> {sid: rank}
mvpool = {}        # league key -> {sid: moveset str}
for key, _s, cut in LEAGUES:
    arr = json.load(open(os.path.join(DATA, f"rankings-{key}.json")))
    pool[key] = {e["speciesId"]: i + 1 for i, e in enumerate(arr[:cut])}
    mvpool[key] = {e["speciesId"]: " / ".join(m.replace("_", " ").title() for m in e.get("moveset", []))
                   for e in arr[:cut]}


def ranks_for(sid):
    """[(short, rank)] across leagues for one speciesId, in league order."""
    return [(SHORT[k], pool[k][sid]) for k, _s, _c in LEAGUES if sid in pool[k]]


gm = json.load(open(os.path.join(DATA, "gamemaster.json")))
poke = gm["pokemon"] if isinstance(gm, dict) else gm

# released dex-forms only (drop shadow / mega / primal — they aren't dex rows)
forms = [p for p in poke if p.get("dex") and p.get("released")
         and not ({"shadow", "mega"} & set(p.get("tags") or []))
         and "primal" not in p["speciesId"] and "_mega" not in p["speciesId"]]

# group into families
fams = {}
for p in forms:
    key = (p.get("family") or {}).get("id") or p["speciesId"]
    fams.setdefault(key, []).append(p)


def plain(name):
    return re.sub(r"\s*\(.*?\)", "", name).strip()


ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"
LOW = "low ATK / high bulk"
HIGH = "high ATK"

rows = []      # family rows: dict
pointers = []  # pointer stubs: (dex, form_name, anchor_dex, anchor_name)
for key, members in fams.items():
    members = sorted(members, key=lambda p: (p["dex"], len(p["speciesId"]), p["speciesId"]))
    anchor = members[0]
    adex, aname = anchor["dex"], plain(anchor["speciesName"])

    chain = []           # rendered form cells
    leagues_hit = set()  # league short codes anywhere in family
    appearances = 0
    best = None          # (rank, moveset) of top ranked appearance
    for m in members:
        fid = m["speciesId"]
        normal = ranks_for(fid)
        shadow = ranks_for(fid + "_shadow")
        anno = []
        for s, r in normal:
            leagues_hit.add(s); appearances += 1
        for s, r in shadow:
            leagues_hit.add(s); appearances += 1
        if normal:
            anno.append(", ".join(f"{s} #{r}" for s, r in normal))
        if shadow:
            anno.append("Shadow " + ", ".join(f"{s} #{r}" for s, r in shadow))
        # track best moveset for the family (lowest rank number)
        for k, _s, _c in LEAGUES:
            for sid in (fid, fid + "_shadow"):
                if sid in pool[k]:
                    cand = (pool[k][sid], mvpool[k][sid])
                    if best is None or cand[0] < best[0]:
                        best = cand
        label = f'{m["speciesName"]} <span class=dex>#{m["dex"]}</span>'
        if anno:
            label = f'<b>{m["speciesName"]}</b> <span class=dex>#{m["dex"]}</span> <span class=note>— {" · ".join(anno)}</span>'
        chain.append(label)
        if m is not anchor and m["dex"] - adex > FAR:
            pointers.append((m["dex"], plain(m["speciesName"]), adex, aname))

    capped = leagues_hit & {"LC", "GL", "UL"}
    iv = " · ".join(x for x in [LOW if capped else "", HIGH if "ML" in leagues_hit else ""] if x) or "—"
    rows.append({
        "dex": adex, "name": aname, "chain": chain,
        "leagues": [s for s in ["LC", "GL", "UL", "ML"] if s in leagues_hit],
        "iv": iv, "moves": best[1] if best else "—",
        "keep": 1 if appearances else "", "total": appearances or "",
    })

rows.sort(key=lambda r: r["dex"])
items = [("fam", r["dex"], r) for r in rows] + [("ptr", d, (d, n, a, an)) for (d, n, a, an) in pointers]
items.sort(key=lambda x: (x[1], 0 if x[0] == "fam" else 1))

# ---- CSV (family rows only) ----
with open(os.path.join(HERE, "dex.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Dex", "Spawn", "League / Purpose", "Best form & rank (folded forms)",
                "IV target", "Moveset", "Keep", "Total"])
    for r in rows:
        w.writerow([r["dex"], r["name"], " ".join(r["leagues"]) or "—",
                    " · ".join(re.sub("<.*?>", "", c) for c in r["chain"]),
                    r["iv"], r["moves"], r["keep"], r["total"]])
print("wrote dex.csv  (families:", len(rows), ", pointers:", len(pointers), ")")

# ---- HTML ----
h = ["""<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Complete Pokédex — folded by family</title>
<style>
:root{color-scheme:light}
body{font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:24px;background:#fff;color:#1b2733}
h1{font-size:24px;margin:0 0 4px} .sub{color:#5b6b7a;margin:0 0 16px;max-width:80ch}
table{border-collapse:collapse;width:100%}
td,th{padding:6px 9px;border-bottom:1px solid #edf1f5;vertical-align:middle;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#6b7b8a}
img{width:42px;height:42px;object-fit:contain;vertical-align:middle}
.mon{font-weight:600;white-space:nowrap} .dex{color:#9aa7b4;font-size:12px;font-variant-numeric:tabular-nums}
.note{color:#6b7b8a;font-size:13px} .keep{text-align:center} .tot{text-align:center;font-weight:700;color:#b26b00}
.ptr td{background:#fafbfc;color:#9aa7b4;font-size:12px}
.lg{display:inline-block;padding:1px 6px;border-radius:9px;font-size:11px;font-weight:700;margin-right:2px}
.LC{background:#efe7f7;color:#6b3fa0} .GL{background:#e3f6ea;color:#14713a}
.UL{background:#fdeee2;color:#9a4a12} .ML{background:#e3eefb;color:#1e5fa8}
</style>
<h1>Complete Pokédex — folded by family</h1>
<p style="margin:0 0 10px"><a href="pokedex.html">→ ranked-only by Pokédex #</a> &nbsp;·&nbsp; <a href="rankings.html">→ by League</a> &nbsp;·&nbsp; <a href="index.html">→ Ultra Unlock event</a></p>
<p class=sub>Every released species in Pokémon GO, <b>one row per evolutionary family</b> at its first (lowest)
Pokédex #, ordered by dex. Evolutions &amp; regional forms fold in; the <b>Best form &amp; rank</b> cell lists the
folded forms and <b>bolds</b> any that are PvP-ranked (LC top 50 / GL·UL·ML top 60). Grey lines are pointers to a
form already folded into an earlier row. <b>Keep</b>=has a ranked form; <b>Total</b>=# ranked appearances.</p>
<table><tr><th></th><th>Spawn</th><th>League / Purpose</th><th>Best form &amp; rank (folded forms)</th>
<th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>"""]
for kind, _d, payload in items:
    if kind == "ptr":
        d, n, a, an = payload
        h.append(f'<tr class=ptr><td></td><td>{n} <span class=dex>#{d}</span></td>'
                 f'<td colspan=6>→ folded into #{a} ({an} family)</td></tr>')
        continue
    r = payload
    img = f'<img loading=lazy src="{ART.format(r["dex"])}" alt="">'
    badges = " ".join(f'<span class="lg {s}">{s}</span>' for s in r["leagues"]) or '<span class=note>—</span>'
    h.append(f'<tr><td style="text-align:center">{img}</td>'
             f'<td class=mon>{r["name"]}<br><span class=dex>#{r["dex"]}</span></td>'
             f'<td>{badges}</td><td>{" · ".join(r["chain"])}</td>'
             f'<td class=note>{r["iv"]}</td><td class=note>{r["moves"]}</td>'
             f'<td class=keep>{r["keep"]}</td><td class=tot>{r["total"]}</td></tr>')
h.append("</table></html>")
open(os.path.join(HERE, "dex.html"), "w").write("\n".join(h))
print("wrote dex.html")
