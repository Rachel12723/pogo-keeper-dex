#!/usr/bin/env python3
"""Build a PvP ranking reference page from pvpoke's public dataset.

Sections = leagues (Little top 50, Great/Ultra/Master top 60), each ordered by rank.
The "League / Purpose" column lists a mon's OTHER leagues (within these cutoffs).
Keep = 1 per row; Total = # of leagues that species ranks in. Shadows included.

Data: data/rankings-*.json + data/gamemaster.json (types/dex). Regenerate:
    python3 build_rankings.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# league key -> (display, short code, top-N cutoff)
LEAGUES = [
    ("little", "Little Cup", "LC", 50),
    ("great", "Great League", "GL", 60),
    ("ultra", "Ultra League", "UL", 60),
    ("master", "Master League", "ML", 60),
]
SHORT = {k: s for k, _, s, _ in LEAGUES}

# dex map for sprites (gamemaster); strip _shadow to reuse base sprite
gm = json.load(open(os.path.join(DATA, "gamemaster.json")))
poke = gm["pokemon"] if isinstance(gm, dict) else gm
DEX = {p["speciesId"]: p.get("dex") for p in poke}


def dex_of(sid):
    return DEX.get(sid) or DEX.get(sid.replace("_shadow", ""))


BY = {p["speciesId"]: p for p in poke}
# reverse map: some entries lack family.parent but a pre-evo lists them in evolutions
PARENT = {}
for _p in poke:
    for _evo in ((_p.get("family") or {}).get("evolutions") or []):
        PARENT.setdefault(_evo, _p["speciesId"])


def base_of(sid):
    """Climb to the base form via family.parent, falling back to reverse-evolution map."""
    cur = sid if sid in BY else sid.replace("_shadow", "")
    seen = set()
    while cur not in seen:
        seen.add(cur)
        parent = (BY.get(cur, {}).get("family") or {}).get("parent") or PARENT.get(cur)
        if not parent:
            break
        cur = parent
    return cur


# full ranked lists + rank lookup
full = {}
rankpos = {}
for key, *_ in [(l[0],) for l in LEAGUES]:
    arr = json.load(open(os.path.join(DATA, f"rankings-{key}.json")))
    full[key] = arr
    rankpos[key] = {e["speciesId"]: (i + 1, round(e["score"], 1)) for i, e in enumerate(arr)}

# which leagues (within cutoff) each species qualifies for, in league order
quals = {}
for key, _disp, _s, cut in LEAGUES:
    for i, e in enumerate(full[key][:cut]):
        quals.setdefault(e["speciesId"], []).append((key, i + 1, round(e["score"], 1)))


def mv(m):
    return m.replace("_", " ").title()


def moveset(e):
    return " / ".join(mv(x) for x in e.get("moveset", []))


PVP = "Rank ≤ #100  (low ATK / high bulk)"
HI = "IV% ≥96% or 15 ATK  (high ATK)"
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"

# ---- rows per section ----
sections = []  # (title, key, [row dicts])
for key, disp, short, cut in LEAGUES:
    rows = []
    for i, e in enumerate(full[key][:cut]):
        sid = e["speciesId"]
        base = base_of(sid)
        others = [(k2, r2) for (k2, r2, _sc) in quals[sid] if k2 != key]
        rows.append({
            "sid": sid,
            "base_name": BY.get(base, {}).get("speciesName", e["speciesName"]),
            "base_dex": DEX.get(base) or dex_of(sid),
            "best": e["speciesName"],
            "others": others,
            "rank": i + 1,
            "score": round(e["score"], 1),
            "iv": PVP if key != "master" else HI,
            "moves": moveset(e),
            "total": len(quals[sid]),
        })
    sections.append((f"{disp} — Top {cut}", key, rows))

# ---- CSV ----
with open(os.path.join(HERE, "rankings.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Section", "Spawn", "League / Purpose (other uses)", "Best form & rank",
                "IV target", "Moveset", "Keep", "Total"])
    for title, key, rows in sections:
        for r in rows:
            other = " · ".join(f"{SHORT[k2]} #{r2}" for k2, r2 in r["others"]) or "—"
            w.writerow([title, r["base_name"], other, f"{r['best']} #{r['rank']} (score {r['score']})",
                        r["iv"], r["moves"], 1, r["total"]])
print("wrote rankings.csv")

# ---- HTML (same look as index.html) ----
h = ["""<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Pokémon GO PvP Rankings — by League</title>
<style>
:root{color-scheme:light}
body{font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:24px;
 background:#ffffff;color:#1b2733}
h1{font-size:24px;margin:0 0 4px} .sub{color:#5b6b7a;margin:0 0 20px;max-width:74ch}
h2{font-size:16px;margin:28px 0 8px;color:#2a3a49;border-bottom:1px solid #e2e8ee;padding-bottom:6px}
table{border-collapse:collapse;width:100%;margin-bottom:8px}
td,th{padding:6px 9px;border-bottom:1px solid #edf1f5;vertical-align:middle;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#6b7b8a}
img{width:44px;height:44px;object-fit:contain;vertical-align:middle}
.mon{font-weight:600;white-space:nowrap}
.rank{font-variant-numeric:tabular-nums;white-space:nowrap}
.note{color:#6b7b8a;font-size:13px} .keep{text-align:center} .tot{text-align:center;font-weight:700;color:#b26b00}
.lg{display:inline-block;padding:1px 6px;border-radius:9px;font-size:12px;font-weight:700;margin-right:3px}
.LC{background:#efe7f7;color:#6b3fa0} .GL{background:#e3f6ea;color:#14713a}
.UL{background:#fdeee2;color:#9a4a12} .ML{background:#e3eefb;color:#1e5fa8}
</style>
<h1>Pokémon GO PvP Rankings — by League</h1>
<p style="margin:0 0 10px"><a href="pokedex.html">→ by Pokédex # view</a> &nbsp;·&nbsp; <a href="index.html">→ Ultra Unlock event guide</a></p>
<p class=sub>pvpoke overall rankings (pulled 2026-07-21). Sections are leagues, ordered by rank.
The <b>Spawn</b> sprite/name is the <i>base</i> form (what you catch); <b>Best form &amp; rank</b> is the ideal evolved form.
<b>League / Purpose</b> = the mon's <i>other</i> leagues within these cutoffs.
<b>Keep</b> = 1 per league row; <b>Total</b> = how many of the 4 leagues it ranks in (copies worth keeping).
Capped leagues want <b>low ATK / high bulk</b>; Master wants <b>high ATK</b>. Shadow forms included.</p>
"""]
for title, key, rows in sections:
    h.append(f"<h2>{title}</h2>")
    h.append("<table><tr><th></th><th>Spawn</th><th>League / Purpose</th><th>Best form &amp; rank</th>"
             "<th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>")
    for r in rows:
        img = f'<img loading=lazy src="{ART.format(r["base_dex"])}" alt="">' if r["base_dex"] else ""
        other = " ".join(f'<span class="lg {SHORT[k2]}">{SHORT[k2]} #{r2}</span>' for k2, r2 in r["others"]) or '<span class=note>—</span>'
        h.append(f'<tr><td style="text-align:center">{img}</td><td class=mon>{r["base_name"]}</td>'
                 f'<td>{other}</td><td class=rank><b>{r["best"]}</b> #{r["rank"]} <span class=note>· {r["score"]}</span></td>'
                 f'<td class=note>{r["iv"]}</td><td>{r["moves"]}</td>'
                 f'<td class=keep>1</td><td class=tot>{r["total"]}</td></tr>')
    h.append("</table>")
h.append("</html>")
open(os.path.join(HERE, "rankings.html"), "w").write("\n".join(h))
print("wrote rankings.html")
