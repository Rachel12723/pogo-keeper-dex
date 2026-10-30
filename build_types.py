#!/usr/bin/env python3
"""Build types.html — the top 3 species of each type for Great League and Ultra League.

For every one of the 18 types, take pvpoke's ranked list for the league and keep the first three
distinct SPECIES that have that type (a dual-type species counts under both of its types). A
species and its Shadow form are one species: the better-ranked of the two is shown and the other
is noted. Regional forms (Alolan, Galarian, ...) are separate species.

Data: data/rankings-great.json, data/rankings-ultra.json, data/gamemaster.json.
Regenerate:  python3 build_types.py   (also run by refresh.py)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"
TOP = 3
TYPES = ["normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison", "ground",
         "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"]
TYPE_COLOR = {
    "normal": "#a8a77a", "fire": "#ee8130", "water": "#6390f0", "electric": "#f7d02c",
    "grass": "#7ac74c", "ice": "#96d9d6", "fighting": "#c22e28", "poison": "#a33ea1",
    "ground": "#e2bf65", "flying": "#a98ff3", "psychic": "#f95587", "bug": "#a6b91a",
    "rock": "#b6a136", "ghost": "#735797", "dragon": "#6f35fc", "dark": "#705746",
    "steel": "#b7b7ce", "fairy": "#d685ad",
}
LEAGUES = [("great", "Great League", "CP 1500"), ("ultra", "Ultra League", "CP 2500")]

gm = json.load(open(os.path.join(DATA, "gamemaster.json")))
BY = {p["speciesId"]: p for p in (gm["pokemon"] if isinstance(gm, dict) else gm)}


def species_key(sid):
    return sid[:-7] if sid.endswith("_shadow") else sid


def pretty_moves(e):
    return " / ".join(m.replace("_", " ").title() for m in e.get("moveset", []))


def name_of(sid):
    p = BY.get(sid) or {}
    return re.sub(r"\s*\(Shadow\)", "", p.get("speciesName", sid)).strip()


def league_tops(key):
    """type -> up to TOP dicts {rank, sid, name, shadow, score, moves, dex, also}."""
    arr = json.load(open(os.path.join(DATA, f"rankings-{key}.json")))
    out = {t: [] for t in TYPES}
    seen = {t: {} for t in TYPES}  # type -> species_key -> entry (to note the other form's rank)
    for i, e in enumerate(arr):
        sid = e["speciesId"]
        p = BY.get(sid)
        if not p or not p.get("released", True):
            continue
        sk = species_key(sid)
        for t in p.get("types", []):
            if t not in out:
                continue
            if sk in seen[t]:  # second form of an already-listed species -> annotate it
                prev = seen[t][sk]
                prev["also"] = f'{"Shadow" if sid.endswith("_shadow") else "non-shadow"} form #{i + 1}'
                continue
            if len(out[t]) >= TOP:
                continue
            ent = {"rank": i + 1, "sid": sid, "name": name_of(sid), "shadow": sid.endswith("_shadow"),
                   "score": e.get("score"), "moves": pretty_moves(e), "dex": p.get("dex"), "also": ""}
            out[t].append(ent)
            seen[t][sk] = ent
    return out


tops = {k: league_tops(k) for k, _, _ in LEAGUES}


def card(ent):
    sh = ' <span class=sh>Shadow</span>' if ent["shadow"] else ""
    also = f'<div class=also>{ent["also"]}</div>' if ent["also"] else ""
    img = f'<img loading=lazy src="{ART.format(ent["dex"])}" alt="">' if ent["dex"] else ""
    return (f'<div class=mon>{img}<div class=txt><div class=nm><b>{ent["name"]}</b>{sh}</div>'
            f'<div class=rk>#{ent["rank"]} <span class=sc>score {ent["score"]}</span></div>'
            f'<div class=mv>{ent["moves"]}</div>{also}</div></div>')


h = ['<!doctype html><html lang=en><meta charset=utf-8>',
     '<meta name=viewport content="width=device-width,initial-scale=1">',
     '<title>Top 3 per Type — Great &amp; Ultra League</title>',
     """<style>
:root{color-scheme:light}
body{font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0 auto;padding:24px 16px;background:#fff;color:#1b2733;max-width:1100px}
h1{font-size:26px;margin:0 0 4px} p.sub{color:#5b6b7a;margin:0 0 14px;font-size:14px}
nav a{margin-right:10px} a{color:#14532d}
.tabs{display:flex;gap:8px;margin:14px 0 18px}
.tabs button{border:1px solid #cfd8e1;background:#fff;border-radius:18px;padding:6px 16px;font-size:14px;cursor:pointer}
.tabs button.on{background:#14532d;color:#fff;border-color:#14532d}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}
.type{border:1px solid #e2e8ee;border-radius:12px;overflow:hidden}
.type h3{margin:0;padding:7px 12px;color:#fff;font-size:15px;text-transform:capitalize;text-shadow:0 1px 1px rgba(0,0,0,.25)}
.mon{display:flex;gap:10px;align-items:center;padding:8px 12px;border-top:1px solid #edf1f5}
.mon img{width:52px;height:52px;flex:none}
.nm{font-size:15px} .rk{font-size:13px;color:#14532d;font-weight:600} .sc{color:#8a97a5;font-weight:400}
.mv{font-size:12px;color:#5b6b7a} .also{font-size:11px;color:#9a6b12}
.sh{display:inline-block;font-size:10px;font-weight:700;color:#6b3fa0;background:#efe7f7;border-radius:8px;padding:0 6px;vertical-align:middle}
.league{display:none} .league.on{display:block}
footer{margin-top:26px;color:#9aa7b4;font-size:12px;border-top:1px solid #edf1f5;padding-top:12px}
</style>""",
     '<h1>Top 3 per Type — Great &amp; Ultra League</h1>',
     '<nav><a href="index.html">🏠 Home</a> <a href="rankings.html">→ by League</a> <a href="dex.html">→ Complete Pokédex</a></nav>',
     f'<p class=sub>The three best <b>species</b> of each type by pvpoke rank. A dual-type species appears under both of its '
     f'types; a Pokémon and its Shadow form count as one species (the better-ranked form is shown). '
     f'Ranks are overall league ranks, not within-type.</p>',
     '<div class=tabs>' + "".join(
         f'<button data-l="{k}"{" class=on" if i == 0 else ""}>{name} <small>({cp})</small></button>'
         for i, (k, name, cp) in enumerate(LEAGUES)) + '</div>']
for i, (k, name, _cp) in enumerate(LEAGUES):
    h.append(f'<section class="league{" on" if i == 0 else ""}" id="{k}"><div class=grid>')
    for t in TYPES:
        h.append(f'<div class=type><h3 style="background:{TYPE_COLOR[t]}">{t}</h3>')
        h.extend(card(e) for e in tops[k][t])
        h.append('</div>')
    h.append('</div></section>')
h.append("""<footer>Data: <a href="https://pvpoke.com">pvpoke</a> overall rankings. Regenerate with <code>python3 build_types.py</code>
(runs automatically in <code>refresh.py</code>).</footer>
<script>
document.querySelectorAll('.tabs button').forEach(function(b){b.addEventListener('click',function(){
  document.querySelectorAll('.tabs button').forEach(function(x){x.classList.toggle('on',x===b)});
  document.querySelectorAll('.league').forEach(function(s){s.classList.toggle('on',s.id===b.dataset.l)});
  try{history.replaceState(null,'','#'+b.dataset.l)}catch(e){}});});
(function(){var h=(location.hash||'').slice(1);var b=document.querySelector('.tabs button[data-l="'+h+'"]');if(b)b.click();})();
</script></html>""")
open(os.path.join(HERE, "types.html"), "w").write("\n".join(h))
print("wrote types.html")
