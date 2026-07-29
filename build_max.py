#!/usr/bin/env python3
"""Build the Max Battles (Dynamax / Gigantamax) page.

HAND-CURATED, dated snapshot (~Aug 2026). The Max roster is event-driven and NOT
in any game-master file; the complete list is sourced from Serebii's Max Battles
page (+ a few known bosses it omitted). Dex #s come from data/gamemaster.json.
Two parts: (1) curated best-picks-by-role tables, (2) the COMPLETE roster by dex #.
Regenerate:  python3 build_max.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"

# ---- dex lookup from local gamemaster ----
gm = json.load(open(os.path.join(HERE, "data", "gamemaster.json")))
poke = gm["pokemon"] if isinstance(gm, dict) else gm


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


DEX = {}
for p in poke:
    DEX.setdefault(norm(re.sub(r"\s*\(.*?\)", "", p["speciesName"])), p.get("dex"))

# ---- complete roster (Serebii Max Battles + known omissions) ----
GMAX = ["Venusaur", "Charizard", "Blastoise", "Butterfree", "Pikachu", "Meowth", "Machamp",
        "Gengar", "Kingler", "Lapras", "Snorlax", "Rillaboom", "Cinderace", "Inteleon",
        "Toxtricity", "Grimmsnarl"]
DMAX = ["Bulbasaur", "Ivysaur", "Charmander", "Charmeleon", "Squirtle", "Wartortle", "Caterpie",
        "Metapod", "Growlithe", "Arcanine", "Abra", "Kadabra", "Alakazam", "Machop", "Machoke",
        "Gastly", "Haunter", "Krabby", "Hitmonlee", "Hitmonchan", "Chansey", "Electabuzz", "Eevee",
        "Vaporeon", "Jolteon", "Flareon", "Omanyte", "Omastar", "Kabuto", "Kabutops", "Articuno",
        "Zapdos", "Moltres", "Hoothoot", "Noctowl", "Espeon", "Umbreon", "Shuckle", "Blissey",
        "Raikou", "Entei", "Suicune", "Lugia", "Ho-Oh", "Ralts", "Kirlia", "Gardevoir", "Sableye",
        "Wailmer", "Wailord", "Trapinch", "Vibrava", "Flygon", "Beldum", "Metang", "Metagross",
        "Regirock", "Regice", "Registeel", "Latias", "Latios", "Combee", "Vespiquen", "Electivire",
        "Leafeon", "Glaceon", "Gallade", "Pidove", "Tranquill", "Unfezant", "Roggenrola", "Boldore",
        "Gigalith", "Woobat", "Swoobat", "Drilbur", "Excadrill", "Darumaka", "Darmanitan", "Trubbish",
        "Garbodor", "Cryogonal", "Deino", "Zweilous", "Hydreigon", "Inkay", "Malamar", "Sylveon",
        "Bounsweet", "Steenee", "Tsareena", "Passimian", "Drampa", "Grookey", "Thwackey", "Scorbunny",
        "Raboot", "Sobble", "Drizzile", "Skwovet", "Greedent", "Rookidee", "Corvisquire", "Corviknight",
        "Wooloo", "Dubwool", "Hatenna", "Hattrem", "Hatterene", "Falinks", "Duraludon", "Kubfu",
        "Urshifu", "Eternatus", "Zacian", "Zamazenta"]
GMAX_SET = set(GMAX)
# Finals obtainable as BOTH forms: G-Max (direct catch) AND D-Max (evolve a D-Max pre-evo).
# Evolving never grants G-Max — a D-Max base → D-Max final; G-Max is a separate catch.
DUAL = {"Charizard", "Venusaur", "Blastoise", "Machamp", "Gengar", "Kingler",
        "Rillaboom", "Cinderace", "Inteleon", "Butterfree"}

# ---- curated best picks (subset), role + IV + moveset ----
ATT, TANK, COLL = "high ATK (hundo ideal)", "high HP + DEF (bulk)", "best IV / shiny"
LA, LT = "STAB fast move · level Max Attack", "level Max Guard + Max Spirit"
# name -> (purpose, iv, moveset)
ANNOT = {
 "Inteleon": ("Attacker — Water", ATT, LA), "Kingler": ("Attacker — Water", ATT, LA),
 "Cinderace": ("Attacker — Fire", ATT, LA), "Gengar": ("Attacker — Ghost/Poison", ATT, LA),
 "Rillaboom": ("Attacker — Grass", ATT, LA), "Machamp": ("Attacker — Fighting", ATT, LA),
 "Eternatus": ("Attacker — Poison/Dragon", ATT, LA), "Zacian": ("Attacker — Fairy", ATT, LA),
 "Charizard": ("Attacker — Fire/Flying", ATT, LA), "Venusaur": ("Attacker — Grass/Poison", ATT, LA),
 "Blastoise": ("Attacker — Water", ATT, LA), "Toxtricity": ("Attacker — Electric", ATT, LA),
 "Urshifu": ("Attacker — Fighting/Dark", ATT, LA), "Metagross": ("Attacker — Steel", ATT, LA),
 "Hydreigon": ("Attacker — Dark", ATT, LA), "Excadrill": ("Attacker — Ground/Steel", ATT, LA),
 "Darmanitan": ("Attacker — Fire", ATT, LA), "Gigalith": ("Attacker — Rock", ATT, LA),
 "Raikou": ("Attacker — Electric", ATT, LA), "Entei": ("Attacker — Fire", ATT, LA),
 "Suicune": ("Attacker — Water (bulky)", ATT, LA), "Gardevoir": ("Attacker — Fairy", ATT, LA),
 "Snorlax": ("Guard / Spirit (top tank)", TANK, LT), "Lapras": ("Guard / Spirit (+Ice)", TANK, LT),
 "Zamazenta": ("Guard / Spirit", TANK, LT), "Grimmsnarl": ("Guard / Spirit", TANK, LT),
 "Blissey": ("Spirit (huge-HP healer)", TANK, LT), "Chansey": ("Spirit (huge-HP healer)", TANK, LT),
 "Shuckle": ("Guard (wall)", TANK, LT), "Greedent": ("Guard / Spirit (budget)", TANK, LT),
 "Dubwool": ("Guard / Spirit (budget)", TANK, LT), "Corviknight": ("Guard (Steel/Flying)", TANK, LT),
}
BEST = [
 ("Max Attackers — S tier (your damage core)",
  ["Inteleon", "Kingler", "Cinderace", "Gengar", "Rillaboom", "Machamp", "Eternatus", "Zacian"]),
 ("Max Attackers — A tier",
  ["Charizard", "Venusaur", "Blastoise", "Toxtricity", "Urshifu", "Metagross", "Hydreigon",
   "Excadrill", "Darmanitan", "Gigalith", "Raikou", "Entei", "Suicune", "Gardevoir"]),
 ("Bulky anchors — Max Guard / Max Spirit (bring 1)",
  ["Snorlax", "Lapras", "Zamazenta", "Grimmsnarl", "Blissey", "Chansey", "Shuckle",
   "Greedent", "Dubwool", "Corviknight"]),
]


def dexof(name):
    return DEX.get(norm(name), 9999)


def badge(name):
    return ('<span class="tag gmax">G-Max</span>' if name in GMAX_SET
            else '<span class="tag dmax">D-Max</span>')


def avail(name):
    """Availability badge(s) — duals show both G-Max and D-Max."""
    if name in DUAL:
        return '<span class="tag gmax">G-Max</span> <span class="tag dmax">D-Max</span>'
    return badge(name)


def sprite(name):
    d = dexof(name)
    return f'<img loading=lazy src="{ART.format(d)}" alt="">' if d != 9999 else ""


h = ["""<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Pokémon GO — Max Battles (Dynamax & Gigantamax)</title>
<style>
:root{color-scheme:light}
body{font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0 auto;padding:24px;background:#fff;color:#1b2733;max-width:1000px}
h1{font-size:24px;margin:0 0 4px} h2{font-size:16px;margin:26px 0 8px;color:#2a3a49;border-bottom:1px solid #e2e8ee;padding-bottom:6px}
.warn{background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:10px 14px;color:#7c2d12;font-size:13px;margin:0 0 16px}
ul{max-width:82ch}
table{border-collapse:collapse;width:100%;margin-bottom:8px}
td,th{padding:6px 9px;border-bottom:1px solid #edf1f5;vertical-align:middle;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#6b7b8a}
img{width:42px;height:42px;object-fit:contain;vertical-align:middle}
.mon{font-weight:600;white-space:nowrap} .dex{color:#9aa7b4;font-size:12px;font-variant-numeric:tabular-nums}
.note{color:#5b6b7a;font-size:13px} .keep{text-align:center} .tot{text-align:center;font-weight:700;color:#b26b00}
.sec td{background:#f7fafc;font-weight:700;color:#2a3a49}
.tag{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px;font-weight:700}
.gmax{background:#fde2e4;color:#9b1c31} .dmax{background:#e3eefb;color:#1e5fa8} .role{background:#eef2f6;color:#334155} .coll{background:#eef1f4;color:#5b6b7a}
a{color:#1e5fa8} footer{margin-top:26px;color:#9aa7b4;font-size:12px;border-top:1px solid #edf1f5;padding-top:14px} footer a{color:#6b7b8a}
</style>
<h1>Pokémon GO — Max Battles (Dynamax &amp; Gigantamax)</h1>
<p style="margin:0 0 10px"><a href="index.html">🏠 Home</a> &nbsp;·&nbsp; <a href="rankings.html">→ by League</a> &nbsp;·&nbsp; <a href="pokedex.html">→ by Pokédex #</a> &nbsp;·&nbsp; <a href="dex.html">→ complete Pokédex</a> &nbsp;·&nbsp; <a href="event.html">→ Ultra Unlock event</a></p>
<p class=warn>⚠️ <b>Hand-curated, dated snapshot (~Aug 2026).</b> The Max roster is event-driven (not in any game-master file) and rotates weekly.
The complete list below is from <a href="https://www.serebii.net/pokemongo/maxbattles.shtml">Serebii's Max Battles page</a> (+ a few bosses it omitted) — it may still miss recent additions.
Live rotation: <a href="https://www.snacknap.com/max-battles">snacknap</a> · <a href="https://db.pokemongohub.net/pokemon-list/category/dynamax">pokemongohub</a>.</p>
<h2>How to read this</h2>
<ul>
<li><b>Only Max-Battle-caught Pokémon can be used</b> (a normal wild/raid catch of the same species can't Dynamax).</li>
<li><span class="tag gmax">G-Max</span> = unique form + stronger exclusive move (tops the attacker tables); <span class="tag dmax">D-Max</span> = generic typed Max Moves.</li>
<li><b>Evolving never grants G-Max</b> — a D-Max Charmander → <b>D-Max</b> Charizard; Gigantamax is a separate catch. So many finals (Charizard, Venusaur, Gengar, Inteleon…) exist as <b>both</b> — shown <span class="tag gmax">G-Max</span> <span class="tag dmax">D-Max</span> in the roster.</li>
<li><b>Roles:</b> Max Attack (damage) / Max Guard (team shield) / Max Spirit (heal). Bring 1–2 attackers + a bulky Guard/Spirit anchor.</li>
<li><b>IV by role:</b> attackers → high ATK; anchors → high HP + DEF. Max Attack type follows your fast move (pick STAB).</li>
</ul>"""]

# ---- Part 1: curated best picks ----
h.append("<h2>Best picks by role (the ones worth building)</h2>")
h.append('<table><tr><th></th><th>Spawn</th><th>Purpose (role)</th><th>Best form</th><th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>')
for title, names in BEST:
    h.append(f'<tr class=sec><td colspan=8>{title}</td></tr>')
    n = len(names)
    for i, nm in enumerate(names):
        purpose, iv, mv = ANNOT[nm]
        ct = f'<td rowspan={n} class=tot>{n}</td>' if i == 0 else ""
        h.append(f'<tr><td style="text-align:center">{sprite(nm)}</td>'
                 f'<td class=mon>{nm} <span class=dex>#{dexof(nm)}</span></td>'
                 f'<td><span class="tag role">{purpose}</span></td><td>{badge(nm)}</td>'
                 f'<td class=note>{iv}</td><td class=note>{mv}</td><td class=keep>1</td>{ct}</tr>')
h.append("</table>")

# ---- Part 2: complete roster by dex # ----
allmons = sorted(set(GMAX + DMAX), key=lambda nm: (dexof(nm), nm))
h.append(f"<h2>Complete roster — every Max-available Pokémon, by Pokédex # ({len(allmons)})</h2>")
h.append('<table><tr><th></th><th>Spawn</th><th>Form</th><th>Purpose (role)</th><th>IV target</th><th>Moveset</th><th>Keep</th></tr>')
for nm in allmons:
    if nm in ANNOT:
        purpose, iv, mv = ANNOT[nm]
        ptag = f'<span class="tag role">{purpose}</span>'
    else:
        iv, mv = COLL, "—"
        ptag = '<span class="tag coll">Collection</span>'
    h.append(f'<tr><td style="text-align:center">{sprite(nm)}</td>'
             f'<td class=mon>{nm} <span class=dex>#{dexof(nm)}</span></td>'
             f'<td>{avail(nm)}</td><td>{ptag}</td>'
             f'<td class=note>{iv}</td><td class=note>{mv}</td><td class=keep>1</td></tr>')
h.append("</table>")

h.append("""<footer>Fan-made reference; not affiliated with Niantic or The Pokémon Company. Roster/tiers are a ~Aug 2026 snapshot
and change frequently. Complete list from <a href="https://www.serebii.net/pokemongo/maxbattles.shtml">Serebii</a>;
tiers from <a href="https://pokemongohub.net/post/guide/max-attackers-tier-list/">GO Hub</a> /
<a href="https://www.dittobase.com/pokemon-go/best-attackers/max-battles/overall">Dittobase</a>.</footer>
</html>""")

miss = [nm for nm in set(GMAX + DMAX) if dexof(nm) == 9999]
if miss:
    print("WARN unresolved dex:", miss)
open(os.path.join(HERE, "max.html"), "w").write("\n".join(h))
print(f"wrote max.html  (complete roster: {len(allmons)} mons, {len(GMAX)} G-Max)")
