#!/usr/bin/env python3
"""Pokédex-ordered view of the same ranked pool as rankings.html.

One row per BASE-species line (grouped by base Pokédex #), so a mon's normal /
shadow / Galarian (etc.) forms collapse into one row — you can `+`-search the whole
family. Each form×league appearance is a detail line under League/Purpose + Best
form & rank. Sprite = base form. Regenerate:  python3 build_pokedex.py
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

LEAGUES = [
    ("little", "Little Cup", "LC", 50),
    ("great", "Great League", "GL", 60),
    ("ultra", "Ultra League", "UL", 60),
    ("master", "Master League", "ML", 60),
]
SHORT = {k: s for k, _, s, _ in LEAGUES}
LORDER = {k: i for i, (k, *_ ) in enumerate(LEAGUES)}

gm = json.load(open(os.path.join(DATA, "gamemaster.json")))
poke = gm["pokemon"] if isinstance(gm, dict) else gm
BY = {p["speciesId"]: p for p in poke}
DEX = {p["speciesId"]: p.get("dex") for p in poke}


def dex_of(sid):
    return DEX.get(sid) or DEX.get(sid.replace("_shadow", ""))


def base_of(sid):
    cur = sid if sid in BY else sid.replace("_shadow", "")
    seen = set()
    while cur in BY and cur not in seen:
        seen.add(cur)
        parent = (BY[cur].get("family") or {}).get("parent")
        if not parent:
            break
        cur = parent
    return cur


def plain(name):
    """Strip form qualifiers like '(Shadow)' / '(Galarian)' → base species name."""
    return re.sub(r"\s*\(.*?\)", "", name).strip()


def mv(m):
    return m.replace("_", " ").title()


PVP = "Rank ≤ #100  (low ATK / high bulk)"
HI = "IV% ≥96% or 15 ATK  (high ATK)"
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"

# gather every qualifying (form, league) detail, grouped by base dex
groups = {}  # base_dex -> {"name","dex","details":[...]}
for key, disp, short, cut in LEAGUES:
    arr = json.load(open(os.path.join(DATA, f"rankings-{key}.json")))
    for i, e in enumerate(arr[:cut]):
        sid = e["speciesId"]
        base = base_of(sid)
        bdex = DEX.get(base) or dex_of(sid) or 9999
        g = groups.setdefault(bdex, {"name": plain(BY.get(base, {}).get("speciesName", e["speciesName"])),
                                     "dex": bdex, "details": []})
        g["details"].append({
            "form": e["speciesName"],
            "league": key,
            "rank": i + 1,
            "score": round(e["score"], 1),
            "iv": PVP if key != "master" else HI,
            "moves": " / ".join(mv(x) for x in e.get("moveset", [])),
        })

# sort details within a group: by form name, then league order, then rank
for g in groups.values():
    g["details"].sort(key=lambda d: (d["form"], LORDER[d["league"]], d["rank"]))

ordered = [groups[k] for k in sorted(groups)]

# ---- CSV ----
with open(os.path.join(HERE, "pokedex.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Dex", "Spawn (base)", "League / Purpose", "Best form & rank",
                "IV target", "Moveset", "Keep", "Total"])
    for g in ordered:
        for j, d in enumerate(g["details"]):
            w.writerow([g["dex"] if j == 0 else "", g["name"] if j == 0 else "",
                        SHORT[d["league"]], f"{d['form']} #{d['rank']} (score {d['score']})",
                        d["iv"], d["moves"], 1, len(g["details"]) if j == 0 else ""])
print("wrote pokedex.csv")

# ---- HTML ----
h = ["""<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Pokémon GO PvP Rankings — by Pokédex #</title>
<style>
:root{color-scheme:light}
body{font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:24px;
 background:#ffffff;color:#1b2733}
h1{font-size:24px;margin:0 0 4px} .sub{color:#5b6b7a;margin:0 0 16px;max-width:78ch}
h2{font-size:16px;margin:24px 0 8px;color:#2a3a49;border-bottom:1px solid #e2e8ee;padding-bottom:6px}
table{border-collapse:collapse;width:100%}
td,th{padding:6px 9px;border-bottom:1px solid #edf1f5;vertical-align:middle;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#6b7b8a}
img{width:44px;height:44px;object-fit:contain;vertical-align:middle}
.mon{font-weight:600;white-space:nowrap} .dex{color:#8ea0b2;font-size:12px;font-variant-numeric:tabular-nums}
.rank{font-variant-numeric:tabular-nums;white-space:nowrap}
.note{color:#6b7b8a;font-size:13px} .keep{text-align:center} .tot{text-align:center;font-weight:700;color:#b26b00}
.grp td{border-top:2px solid #dfe6ee}
.lg{display:inline-block;padding:1px 6px;border-radius:9px;font-size:12px;font-weight:700}
.LC{background:#efe7f7;color:#6b3fa0} .GL{background:#e3f6ea;color:#14713a}
.UL{background:#fdeee2;color:#9a4a12} .ML{background:#e3eefb;color:#1e5fa8}
.ss b{font-size:13px} .ss code{background:#eef1f4;padding:1px 4px;border-radius:4px}
pre{white-space:pre-wrap;word-break:break-all;background:#f5f8fb;border:1px solid #e2e8ee;
 border-radius:8px;padding:10px 12px;font-size:12px;margin:4px 0 14px}
</style>
<h1>Pokémon GO PvP Rankings — by Pokédex #</h1>
<p style="margin:0 0 10px"><a href="rankings.html">→ by League view</a> &nbsp;·&nbsp; <a href="index.html">→ Ultra Unlock event guide</a></p>
<p class=sub>Same pool as the by-League page (Little top 50, Great/Ultra/Master top 60), merged into one list
ordered by Pokédex #. One row per <b>base-species line</b> — normal / shadow / Galarian (etc.) forms are
grouped (search the family with <code>+name</code>); each form×league is a detail line. Sprite = base form.
<span class=lg style="background:none;color:#14713a">Capped</span> want low ATK; <span class=lg style="background:none;color:#1e5fa8">Master</span> wants high ATK.</p>
"""]
NAMES = [g["name"] for g in ordered]
_names = ",".join("+" + n for n in NAMES)
h.append("<h2>Quick search strings</h2>")
h.append(f"<p class=note>Every base species in this list ({len(NAMES)} — grouped, so <code>+name</code> "
         "covers each family incl. shadow / regional forms). If the game truncates such a long string, "
         "split the name list in half.</p>")
h.append("<div class=ss><b>PvP shape — low ATK / high bulk</b> (for the Little / Great / Ultra mons):"
         f"<pre>{_names}&0-1attack&3-4defense&3-4hp</pre></div>")
h.append("<div class=ss><b>High IV — high ATK / hundo</b> (for the Master-league &amp; raid mons):"
         f"<pre>{_names}&3*,4*</pre></div>")
h.append('<table><tr><th></th><th>Spawn</th><th>League / Purpose</th><th>Best form &amp; rank</th>'
         '<th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>')
for g in ordered:
    n = len(g["details"])
    img = f'<img loading=lazy src="{ART.format(g["dex"])}" alt="">' if g["dex"] and g["dex"] != 9999 else ""
    for j, d in enumerate(g["details"]):
        c1 = f'<td rowspan={n} style="text-align:center">{img}</td>' if j == 0 else ""
        c2 = (f'<td rowspan={n} class=mon>{g["name"]}<br><span class=dex>#{g["dex"]}</span></td>'
              if j == 0 else "")
        ct = f'<td rowspan={n} class=tot>{n}</td>' if j == 0 else ""
        cls = " class=grp" if j == 0 else ""
        h.append(f'<tr{cls}>{c1}{c2}<td><span class="lg {SHORT[d["league"]]}">{SHORT[d["league"]]}</span></td>'
                 f'<td class=rank><b>{d["form"]}</b> #{d["rank"]} <span class=note>· {d["score"]}</span></td>'
                 f'<td class=note>{d["iv"]}</td><td>{d["moves"]}</td><td class=keep>1</td>{ct}</tr>')
h.append("</table></html>")
open(os.path.join(HERE, "pokedex.html"), "w").write("\n".join(h))
print("wrote pokedex.html")
