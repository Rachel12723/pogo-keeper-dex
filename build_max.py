#!/usr/bin/env python3
"""Build the Max Battles (Dynamax / Gigantamax) page.

HAND-CURATED, dated snapshot (~Aug 2026). Max roster is event-driven / not in any
game-master file; complete list from Serebii's Max Battles page (+ a few omitted
bosses). Dex #s + evolution families from data/gamemaster.json.

Two parts:
  1. Curated best-picks-by-role tables.
  2. COMPLETE roster FOLDED by evolution line (like dex.html): one block per base
     species (evolutions fold in), Purpose = Max mode (D-Max / G-Max), Best form =
     the evolved form + role. Lines available in both modes get two rows.
Regenerate:  python3 build_max.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def plain(name):
    return re.sub(r"\s*\(.*?\)", "", name).strip()


# ---- gamemaster: dex, families, name->species ----
gm = json.load(open(os.path.join(HERE, "data", "gamemaster.json")))
poke = gm["pokemon"] if isinstance(gm, dict) else gm


def is_mega(p):
    return "mega" in (p.get("tags") or []) or "_mega" in p["speciesId"] or "primal" in p["speciesId"]


cand = [p for p in poke if p.get("dex") and p.get("released")
        and "shadow" not in (p.get("tags") or []) and "_shadow" not in p["speciesId"] and not is_mega(p)]
canon = {}
for p in sorted(cand, key=lambda p: (len(p["speciesId"]), p["speciesId"])):
    bs = p["baseStats"]
    canon.setdefault((p["dex"], tuple(p["types"]), bs["atk"], bs["def"], bs["hp"]), p)
forms = list(canon.values())


def fkey_of(sid):
    return (BY.get(sid, {}).get("family") or {}).get("id") or sid


BY = {p["speciesId"]: p for p in forms}
NID = {}
for p in forms:
    NID.setdefault(norm(plain(p["speciesName"])), p["speciesId"])
FAM = {}
for p in forms:
    FAM.setdefault(fkey_of(p["speciesId"]), []).append(p)
DEXALL = {}
for p in poke:
    DEXALL.setdefault(norm(plain(p["speciesName"])), p.get("dex"))


def dexof(name):
    return DEXALL.get(norm(name), 9999)


# ---- roster ----
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
DMAX_N = {norm(n) for n in DMAX}
GMAX_N = {norm(n) for n in GMAX}

ATT, TANK, COLL = "high ATK (hundo ideal)", "high HP + DEF (bulk)", "best IV / shiny"
LA, LT = "STAB fast move · level Max Attack", "level Max Guard + Max Spirit"
# name -> (role label, iv, moveset)
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


def rclass(role):
    return "att" if role.startswith("Attacker") else "sup"


def sprite(dex):
    return f'<img loading=lazy src="{ART.format(dex)}" alt="">' if dex and dex != 9999 else ""


def badge_gmax():
    return '<span class="tag gmax">G-Max</span>'


def badge_dmax():
    return '<span class="tag dmax">D-Max</span>'


# ---- fold the Max roster into families ----
maxfams = {}  # fkey -> {"base_dex","base_name","dmax":bool,"gmax_names":[],"members":[names]}
for nm in GMAX + DMAX:
    sid = NID.get(norm(nm))
    fk = fkey_of(sid) if sid else ("solo_" + norm(nm))
    maxfams.setdefault(fk, {"names": set()})["names"].add(nm)

families = []
for fk, info in maxfams.items():
    members = FAM.get(fk)
    if members:
        base = min(members, key=lambda p: p["dex"])
        base_name, base_dex = plain(base["speciesName"]), base["dex"]
        mem_names = [plain(m["speciesName"]) for m in members]
    else:  # solo (name not found in gamemaster forms)
        nm = next(iter(info["names"]))
        base_name, base_dex, mem_names = nm, dexof(nm), [nm]
    dmax = any(norm(n) in DMAX_N for n in mem_names)
    gmax_names = [n for n in mem_names if norm(n) in GMAX_N]
    # D-Max "best form" = evolved form you'd use: prefer an annotated member, else highest-dex
    ann_mem = [n for n in mem_names if n in ANNOT]
    dfinal = max(ann_mem, key=dexof) if ann_mem else max(mem_names, key=dexof)
    chain = sorted([n for n in mem_names if norm(n) in DMAX_N or norm(n) in GMAX_N], key=dexof)
    families.append({"dex": base_dex, "name": base_name, "dmax": dmax,
                     "gmax": gmax_names[0] if gmax_names else None, "dfinal": dfinal, "chain": chain})
families.sort(key=lambda f: (f["dex"], f["name"]))


def role_cells(name):
    """(role_label, iv, moveset) for a form name."""
    if name in ANNOT:
        return ANNOT[name]
    return ("Collection", COLL, "—")


# ================= HTML =================
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
.sec td{background:#f7fafc;font-weight:700;color:#2a3a49} .grp td{border-top:2px solid #dfe6ee}
.tag{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px;font-weight:700}
.gmax{background:#fde2e4;color:#9b1c31} .dmax{background:#e3eefb;color:#1e5fa8}
.att{background:#fdeee2;color:#9a4a12} .sup{background:#e3f6ea;color:#14713a} .coll{background:#eef1f4;color:#5b6b7a}
a{color:#1e5fa8} footer{margin-top:26px;color:#9aa7b4;font-size:12px;border-top:1px solid #edf1f5;padding-top:14px} footer a{color:#6b7b8a}
</style>
<h1>Pokémon GO — Max Battles (Dynamax &amp; Gigantamax)</h1>
<p style="margin:0 0 10px"><a href="index.html">🏠 Home</a> &nbsp;·&nbsp; <a href="rankings.html">→ by League</a> &nbsp;·&nbsp; <a href="pokedex.html">→ by Pokédex #</a> &nbsp;·&nbsp; <a href="dex.html">→ complete Pokédex</a> &nbsp;·&nbsp; <a href="event.html">→ Ultra Unlock event</a></p>
<p class=warn>⚠️ <b>Hand-curated, dated snapshot (~Aug 2026).</b> Max roster is event-driven (not in any game-master file) and rotates weekly.
Complete list from <a href="https://www.serebii.net/pokemongo/maxbattles.shtml">Serebii's Max Battles page</a> (+ a few omitted bosses) — may miss recent additions.
Live: <a href="https://www.snacknap.com/max-battles">snacknap</a> · <a href="https://db.pokemongohub.net/pokemon-list/category/dynamax">pokemongohub</a>.</p>
<h2>How to read this</h2>
<ul>
<li><b>Only Max-Battle-caught Pokémon can be used</b> (a normal wild/raid catch of the same species can't Dynamax).</li>
<li><b>Evolving never grants G-Max</b> — a D-Max Charmander → <b>D-Max</b> Charizard; Gigantamax is a separate catch. So many lines exist in <b>both</b> modes (they get two rows below).</li>
<li><b>Roles:</b> Max Attack (damage) / Max Guard (team shield) / Max Spirit (heal). Bring 1–2 attackers + a bulky Guard/Spirit anchor.</li>
<li><b>IV by role:</b> attackers → high ATK; anchors → high HP + DEF. Max Attack type follows your fast move (pick STAB).</li>
</ul>"""]

# ---- Part 1: best picks by role ----
h.append("<h2>Best picks by role (the ones worth building)</h2>")
h.append('<table><tr><th></th><th>Spawn</th><th>Purpose (role)</th><th>Best form</th><th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>')
for title, names in BEST:
    h.append(f'<tr class=sec><td colspan=8>{title}</td></tr>')
    n = len(names)
    for i, nm in enumerate(names):
        role, iv, mv = role_cells(nm)
        b = badge_gmax() if norm(nm) in GMAX_N else badge_dmax()
        ct = f'<td rowspan={n} class=tot>{n}</td>' if i == 0 else ""
        h.append(f'<tr><td style="text-align:center">{sprite(dexof(nm))}</td>'
                 f'<td class=mon>{nm} <span class=dex>#{dexof(nm)}</span></td>'
                 f'<td><span class="tag {rclass(role)}">{role}</span></td><td>{b}</td>'
                 f'<td class=note>{iv}</td><td class=note>{mv}</td><td class=keep>1</td>{ct}</tr>')
h.append("</table>")

# ---- Part 2: complete roster, FOLDED by evolution line, by dex # ----
h.append(f"<h2>Complete roster — folded by evolution line, by Pokédex # ({len(families)} lines)</h2>")
h.append("<p class=note>Evolutions fold into the base (e.g. Zweilous &amp; Hydreigon → Deino). "
         "<b>Purpose</b> = the Max mode; <b>Best form</b> = the evolved form you'd use + its role. "
         "Lines obtainable in both modes get two rows.</p>")
h.append('<table><tr><th></th><th>Spawn (base)</th><th>Purpose</th><th>Best form / forms</th><th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>')


def mbadge(mode):
    return badge_gmax() if mode == "gmax" else badge_dmax()


for f in families:
    # battle rows: only a mode whose usable form has a real role (attacker/tank)
    battle = []
    if f["gmax"] and f["gmax"] in ANNOT:
        battle.append(("gmax", f["gmax"]))
    if f["dmax"] and f["dfinal"] in ANNOT:
        battle.append(("dmax", f["dfinal"]))
    covered = {m for m, _ in battle}
    coll_modes = [m for m in ("gmax", "dmax")
                  if ((m == "gmax" and f["gmax"]) or (m == "dmax" and f["dmax"])) and m not in covered]

    rows = []  # (purpose_html, bestform_html, iv, moveset)
    for mode, form in battle:
        role, iv, mv = ANNOT[form]
        rows.append((mbadge(mode), f'<b>{form}</b> <span class="tag {rclass(role)}">{role}</span>', iv, mv))
    if coll_modes:  # no battle purpose in these modes → show the collectible forms, not a "best form"
        pill = " ".join(mbadge(m) for m in coll_modes)
        chain = " · ".join(f'{n} <span class=dex>#{dexof(n)}</span>' for n in f["chain"])
        rows.append((pill, f'{chain} <span class="tag coll">Collection</span>', COLL, "—"))
    if not rows:
        continue

    n = len(rows)
    img = sprite(f["dex"])
    for i, (purpose, best, iv, mv) in enumerate(rows):
        c0 = (f'<td rowspan={n} style="text-align:center">{img}</td>'
              f'<td rowspan={n} class=mon>{f["name"]}<br><span class=dex>#{f["dex"]}</span></td>') if i == 0 else ""
        ct = f'<td rowspan={n} class=tot>{n}</td>' if i == 0 else ""
        grp = " class=grp" if i == 0 else ""
        h.append(f'<tr{grp}>{c0}<td>{purpose}</td><td class=note>{best}</td>'
                 f'<td class=note>{iv}</td><td class=note>{mv}</td><td class=keep>1</td>{ct}</tr>')
h.append("</table>")

h.append("""<footer>Fan-made reference; not affiliated with Niantic or The Pokémon Company. Roster/tiers are a ~Aug 2026 snapshot
and change frequently. Complete list from <a href="https://www.serebii.net/pokemongo/maxbattles.shtml">Serebii</a>;
tiers from <a href="https://pokemongohub.net/post/guide/max-attackers-tier-list/">GO Hub</a> /
<a href="https://www.dittobase.com/pokemon-go/best-attackers/max-battles/overall">Dittobase</a>.</footer>
</html>""")
open(os.path.join(HERE, "max.html"), "w").write("\n".join(h))
print(f"wrote max.html  ({len(families)} folded lines)")
