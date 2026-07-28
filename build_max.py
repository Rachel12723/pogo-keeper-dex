#!/usr/bin/env python3
"""Build the Max Battles (Dynamax / Gigantamax) roster page.

NOT data-driven: the Max-Battle roster is event-driven and NOT encoded in any
game-master file, and the live trackers are anti-bot. So this is a HAND-CURATED,
dated snapshot (~Aug 2026). Edit the ROSTER list below to update; regenerate:
    python3 build_max.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"

ATT = "high ATK (hundo ideal)"
TANK = "high HP + DEF (bulk)"
COLL = "best IV / shiny"
LVL_A = "STAB fast move · level Max Attack"
LVL_T = "level Max Guard + Max Spirit"

# row = (name, dex, gmax, purpose, best_form, iv, moveset, keep)
ROSTER = [
 ("Max Attackers — S tier (your damage core)", [
  ("Inteleon", 818, True, "Attacker — Water", "G-Max", ATT, LVL_A, 1),
  ("Kingler", 99, True, "Attacker — Water", "G-Max", ATT, LVL_A, 1),
  ("Cinderace", 815, True, "Attacker — Fire", "G-Max", ATT, LVL_A, 1),
  ("Gengar", 94, True, "Attacker — Ghost/Poison (glass)", "G-Max", ATT, LVL_A, 1),
  ("Rillaboom", 812, True, "Attacker — Grass", "G-Max", ATT, LVL_A, 1),
  ("Machamp", 68, True, "Attacker — Fighting", "G-Max", ATT, LVL_A, 1),
  ("Eternatus", 890, False, "Attacker — Poison/Dragon", "D-Max", ATT, "Dragon fast move · level Max Attack", 1),
  ("Zacian", 888, False, "Attacker — Fairy (Crowned Sword)", "D-Max", ATT, "level Max Attack", 1),
 ]),
 ("Max Attackers — A tier", [
  ("Charizard", 6, True, "Attacker — Fire/Flying", "G-Max", ATT, LVL_A, 1),
  ("Venusaur", 3, True, "Attacker — Grass/Poison (bulky)", "G-Max", ATT, LVL_A, 1),
  ("Blastoise", 9, True, "Attacker — Water (bulky)", "G-Max", ATT, LVL_A, 1),
  ("Toxtricity", 849, True, "Attacker — Electric", "G-Max", ATT, LVL_A, 1),
  ("Urshifu", 892, True, "Attacker — Fighting/Dark", "G-Max", ATT, LVL_A, 1),
  ("Metagross", 376, False, "Attacker — Steel", "D-Max", ATT, "Steel fast move · level Max Attack", 1),
  ("Raikou", 243, False, "Attacker — Electric", "D-Max", ATT, "level Max Attack", 1),
  ("Entei", 244, False, "Attacker — Fire", "D-Max", ATT, "level Max Attack", 1),
  ("Suicune", 245, False, "Attacker — Water (bulky)", "D-Max", ATT, "level Max Attack", 1),
  ("Drednaw", 834, False, "Attacker — Water/Rock", "D-Max", ATT, "level Max Attack", 1),
 ]),
 ("Bulky anchors — Max Guard / Max Spirit (bring 1)", [
  ("Snorlax", 143, True, "Guard / Spirit (top tank)", "G-Max", TANK, LVL_T, 1),
  ("Lapras", 131, True, "Guard / Spirit (+ Ice dmg)", "G-Max", TANK, LVL_T, 1),
  ("Zamazenta", 889, False, "Guard / Spirit (Crowned Shield)", "D-Max", TANK, LVL_T, 1),
  ("Grimmsnarl", 861, True, "Guard / Spirit (Dark/Fairy)", "G-Max", TANK, LVL_T, 1),
  ("Blissey", 242, False, "Spirit (huge HP healer)", "D-Max", TANK, LVL_T, 1),
  ("Greedent", 820, False, "Guard / Spirit (budget tank)", "D-Max", TANK, LVL_T, 1),
  ("Dubwool", 832, False, "Guard / Spirit (budget tank)", "D-Max", TANK, LVL_T, 1),
  ("Corviknight", 823, False, "Guard (Flying/Steel bulk)", "D-Max", TANK, LVL_T, 1),
  ("Stonjourner", 874, False, "Guard (high DEF)", "D-Max", TANK, LVL_T, 1),
 ]),
 ("Collection / niche", [
  ("Pikachu", 25, True, "Collection (Electric niche)", "G-Max", COLL, "—", 1),
  ("Meowth", 52, True, "Collection", "G-Max", COLL, "—", 1),
  ("Wooloo", 831, False, "Collection (→ Dubwool tank)", "D-Max", COLL, "—", 1),
  ("Skwovet", 819, False, "Collection (→ Greedent tank)", "D-Max", COLL, "—", 1),
  ("Rookidee", 821, False, "Collection (→ Corviknight)", "D-Max", COLL, "—", 1),
  ("Falinks", 870, False, "Collection / niche Fighting", "D-Max", COLL, "—", 1),
  ("Sandaconda", 844, False, "Collection / niche", "D-Max", COLL, "—", 1),
  ("Toxel", 848, False, "Collection (→ Toxtricity)", "D-Max", COLL, "—", 1),
  ("Chewtle", 833, False, "Collection (→ Drednaw)", "D-Max", COLL, "—", 1),
 ]),
]

h = ["""<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Pokémon GO — Max Battles (Dynamax & Gigantamax)</title>
<style>
:root{color-scheme:light}
body{font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0 auto;padding:24px;background:#fff;color:#1b2733;max-width:1000px}
h1{font-size:24px;margin:0 0 4px} h2{font-size:16px;margin:26px 0 8px;color:#2a3a49;border-bottom:1px solid #e2e8ee;padding-bottom:6px}
.sub{color:#5b6b7a;margin:0 0 14px;max-width:82ch}
.warn{background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:10px 14px;color:#7c2d12;font-size:13px;margin:0 0 16px}
ul{max-width:82ch}
table{border-collapse:collapse;width:100%;margin-bottom:8px}
td,th{padding:6px 9px;border-bottom:1px solid #edf1f5;vertical-align:middle;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#6b7b8a}
img{width:44px;height:44px;object-fit:contain;vertical-align:middle}
.mon{font-weight:600;white-space:nowrap} .note{color:#5b6b7a;font-size:13px}
.keep{text-align:center} .tot{text-align:center;font-weight:700;color:#b26b00}
.tag{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px;font-weight:700}
.gmax{background:#fde2e4;color:#9b1c31} .dmax{background:#e3eefb;color:#1e5fa8}
.role{background:#eef2f6;color:#334155}
a{color:#1e5fa8}
footer{margin-top:26px;color:#9aa7b4;font-size:12px;border-top:1px solid #edf1f5;padding-top:14px} footer a{color:#6b7b8a}
</style>
<h1>Pokémon GO — Max Battles (Dynamax &amp; Gigantamax)</h1>
<p style="margin:0 0 10px"><a href="index.html">🏠 Home</a> &nbsp;·&nbsp; <a href="rankings.html">→ by League</a> &nbsp;·&nbsp; <a href="pokedex.html">→ by Pokédex #</a> &nbsp;·&nbsp; <a href="dex.html">→ complete Pokédex</a> &nbsp;·&nbsp; <a href="event.html">→ Ultra Unlock event</a></p>
<p class=warn>⚠️ <b>Hand-curated, dated snapshot (~Aug 2026).</b> The Max roster is <b>event-driven</b> (not in any game-master file) and
<b>rotates weekly</b> — this list will drift and may miss recent additions. Check a live tracker for what's raidable now:
<a href="https://www.snacknap.com/max-battles">snacknap</a> ·
<a href="https://db.pokemongohub.net/pokemon-list/category/dynamax">pokemongohub</a> ·
<a href="https://www.dexerto.com/pokemon/every-dynamax-and-gigantamax-pokemon-in-pokemon-go-so-far-2876339/">Dexerto</a>.</p>
<h2>Before you read the table</h2>
<ul>
<li><b>Only Max-Battle-caught Pokémon can be used</b> — a normal wild/egg/raid catch of the same species can't Dynamax (shares candy + dex only).</li>
<li><b>D-Max vs G-Max:</b> most just Dynamax (generic typed Max Moves); a subset can <span class="tag gmax">G-Max</span> — unique look + a stronger exclusive move, so G-Max forms top the attacker tables.</li>
<li><b>Three roles</b> — <b>Max Attack</b> (damage), <b>Max Guard</b> (team shield), <b>Max Spirit</b> (heal). Bring <b>1–2 attackers + 1 bulky Guard/Spirit anchor</b>, not three glass cannons.</li>
<li><b>IV target follows the role:</b> attackers want <b>high ATK</b>; Guard/Spirit anchors want <b>high HP + DEF</b> (they survive and shield/heal). The Max Attack move's type follows your <b>fast move</b>, so pick a STAB fast move.</li>
</ul>
<table><tr><th></th><th>Spawn</th><th>Purpose (role)</th><th>Best form</th><th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>"""]

for title, rows in ROSTER:
    h.append(f'<tr><td colspan=8 style="background:#f7fafc;font-weight:700;color:#2a3a49;padding-top:10px">{title}</td></tr>')
    total = sum(r[7] for r in rows)
    n = len(rows)
    for i, (name, dex, gmax, purpose, form, iv, moves, keep) in enumerate(rows):
        img = f'<img loading=lazy src="{ART.format(dex)}" alt="">'
        badge = '<span class="tag gmax">G-Max</span>' if gmax else '<span class="tag dmax">D-Max</span>'
        ct = f'<td rowspan={n} class=tot>{total}</td>' if i == 0 else ""
        h.append(f'<tr><td style="text-align:center">{img}</td>'
                 f'<td class=mon>{name} <span class=dex>#{dex}</span></td>'
                 f'<td><span class="tag role">{purpose}</span></td>'
                 f'<td>{badge} {form}</td><td class=note>{iv}</td>'
                 f'<td class=note>{moves}</td><td class=keep>{keep}</td>{ct}</tr>')

h.append("</table>")
h.append("""<footer>Fan-made reference; not affiliated with Niantic or The Pokémon Company. Max roster/tiers are a
~Aug 2026 snapshot from web research and change frequently — verify on a live tracker.
Sources: <a href="https://pokemongohub.net/post/guide/max-attackers-tier-list/">GO Hub Max Attackers tier list</a>,
<a href="https://www.dittobase.com/pokemon-go/best-attackers/max-battles/overall">Dittobase Max Battle attackers</a>.</footer>
</html>""")
open(os.path.join(HERE, "max.html"), "w").write("\n".join(h))
print("wrote max.html")
