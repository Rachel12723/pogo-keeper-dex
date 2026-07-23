#!/usr/bin/env python3
"""Build keeper tables for the Ultra Unlock: 10th Anniversary event.

Ranks come from pvpoke's public ranking dataset (data/rankings-*.json, the same
data behind pvpoke.com). Mega / raid-attacker value is annotated from established
PvE knowledge. Regenerate with:  python3 build_tables.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
LEAGUES = ["little", "great", "ultra", "master"]

rank = {}
for lg in LEAGUES:
    arr = json.load(open(os.path.join(DATA, f"rankings-{lg}.json")))
    rank[lg] = {e["speciesId"]: (i + 1, round(e["score"], 1)) for i, e in enumerate(arr)}


def rk(sid, lg):
    """Absolute rank string or None."""
    if sid in rank[lg]:
        r, s = rank[lg][sid]
        return f"#{r}", r, s
    return None


# IV target shorthands
PVP = "Rank % ≥ 97.6  (≤ #100; low ATK)"
HI = "IV% ≥96% or 15 ATK  (high ATK)"
COLL = "1× best IV or shiny"

# Each family -> list of rows: (league/purpose, best form & rank, iv target, moveset, keep)
# Sections keep the exact page order of the event.
FAMILIES = [
 ("Wild Spawns — Jul 21–23 (Kanto/Johto/Hoenn)", [
  ("Bulbasaur", [
     ("Raid / Mega", "Mega Venusaur (good Grass/Poison raider)", HI, "Vine Whip / Frenzy Plant", 1)],
     "No league top-50 (Venusaur best UL #224). Bulbasaur Little #275 — not viable."),
  ("Charmander", [
     ("Raid / Mega", "Mega Charizard X & Y (Y = top Fire raider)", HI, "Fire Spin / Blast Burn", 2)],
     "† One Charizard Mega-evolves into EITHER X or Y — 1 hundo mechanically covers both. No PvP top-50."),
  ("Squirtle", [
     ("Ultra", "Blastoise #22", PVP, "Rollout / Hydro Cannon / Skull Bash", 1),
     ("Raid / Mega", "Mega Blastoise (weak raider — optional)", HI, "Water Gun / Hydro Cannon", 1)],
     "Blastoise GL #51 (near-miss — a low-ATK one is usable in GL too). Mega is outclassed; hundo optional."),
  ("Chikorita", [
     ("Little Cup", "Chikorita #41 (base)", PVP, "Vine Whip / Body Slam / Grass Knot", 1)],
     "Only Little Cup. Meganium not a raider; no mega."),
  ("Cyndaquil", [
     ("Collection", "Typhlosion — budget Fire attacker, outclassed", COLL, "Ember / Blast Burn", 1)],
     "No PvP top-50, no mega. (Hisuian Typhlosion is the good one — different mon.)"),
  ("Totodile", [
     ("Great", "Feraligatr #14", PVP, "Shadow Claw / Hydro Cannon / Ice Beam", 1),
     ("Ultra", "Feraligatr #46", PVP, "Shadow Claw / Hydro Cannon / Ice Beam", 1)],
     "Strong in both capped leagues. No mega."),
  ("Treecko", [
     ("Raid / Mega", "Mega Sceptile (top Grass raider)", HI, "Fury Cutter / Frenzy Plant", 1)],
     "No PvP top-50 (Sceptile best GL #446). Value is the Mega."),
  ("Torchic", [
     ("Raid / Mega", "Mega Blaziken (strong Fire/Fighting)", HI, "Counter / Blast Burn", 1)],
     "No PvP top-50. Value is the Mega."),
  ("Mudkip", [
     ("Ultra", "Swampert #45", PVP, "Mud Shot / Hydro Cannon / Earthquake", 1),
     ("Raid / Mega", "Mega Swampert (top Water raider)", HI, "Water Gun / Hydro Cannon", 1)],
     "Swampert GL #64 & ML #105 = near-misses/budget — the UL low-ATK one also plays GL. Mega + ML both want a hundo."),
 ]),
 ("Wild Spawns — Jul 23–25 (Sinnoh/Unova/Kalos)", [
  ("Turtwig", [("Collection", "Torterra — fringe, no mega", COLL, "—", 1)],
     "No PvP top-50."),
  ("Chimchar", [("Collection", "Infernape — glass attacker, outclassed", COLL, "Fire Spin / Blast Burn", 1)],
     "No PvP top-50, no mega."),
  ("Piplup", [
     ("Great", "Empoleon #5", PVP, "Metal Sound / Hydro Cannon / Drill Peck", 1),
     ("Ultra", "Empoleon #9", PVP, "Metal Sound / Hydro Cannon / Drill Peck", 1)],
     "Top-tier in both capped leagues. No mega."),
  ("Snivy", [("Collection", "Serperior — fringe", COLL, "—", 1)], "No PvP top-50, no mega."),
  ("Tepig", [
     ("Little Cup", "Tepig #48 (base)", PVP, "Ember / Body Slam / Flame Charge", 1)],
     "Only Little Cup. Emboar not meta."),
  ("Oshawott", [("Collection", "Samurott — regular form meh", COLL, "—", 1)],
     "Hisuian Samurott is the PvP one (needs Hisuian Oshawott, a different mon)."),
  ("Chespin", [("Collection", "Chesnaught — best ML #208, not top-50", COLL, "—", 1)],
     "Fell out of the meta; no mega."),
  ("Fennekin", [("Collection", "Delphox — not meta", COLL, "—", 1)], "No PvP top-50, no mega."),
  ("Froakie", [("Collection", "Greninja — glass, niche", COLL, "—", 1)], "No PvP top-50, no mega."),
 ]),
 ("Wild Spawns — Jul 25–27 (Alola/Galar/Paldea)", [
  ("Rowlet", [("Collection", "Decidueye — not top-50", COLL, "—", 1)], "No mega."),
  ("Litten", [("Collection", "Incineroar — fringe", COLL, "—", 1)], "No PvP top-50, no mega."),
  ("Popplio", [
     ("Master", "Primarina #49", HI, "Waterfall / Disarming Voice / Hydro Cannon", 1)],
     "Also UL #71 (near-miss — a strong UL closer; a low-ATK one is worth it too). No mega."),
  ("Grookey", [("Collection", "Rillaboom — fringe", COLL, "—", 1)], "No PvP top-50, no mega."),
  ("Scorbunny", [("Collection", "Cinderace — glass, niche", COLL, "—", 1)], "No mega."),
  ("Sobble", [("Raid / Max", "Inteleon #16 Water attacker (w/ Hydro Cannon or Snipe Shot); G-Max = TOP Water in Max Battles", HI, "Water Gun / Snipe Shot (or Hydro Cannon)", 1)],
     "Sobble CD was 4 Jul 2026 — evolve for the CD move. Keep a high-ATK one for Water raids + Max Battles. Not top-50 PvP."),
  ("Sprigatito", [("Collection", "Meowscarada — glass, niche", COLL, "—", 1)], "No mega."),
  ("Fuecoco", [("Collection / watch", "Skeledirge — UL #94, ML #109 (just outside)", COLL, "Incinerate / Torch Song / Shadow Ball", 1)],
     "Emerging — Fuecoco Little #52 & Skeledirge UL #94 all near-miss top-50. Keep a low-ATK one if you want to gamble. No mega."),
  ("Quaxly", [("Collection", "Quaquaval — fringe", COLL, "—", 1)], "No PvP top-50, no mega."),
 ]),
 ("Lure Module Encounters (normal Lure) — the standouts", [
  ("Beldum", [
     ("Master", "Metagross #3", HI, "Shadow Claw / Meteor Mash / Earthquake", 1),
     ("Raid / Mega", "Mega Metagross (best Steel raider) + Metagross itself top raider", HI, "Bullet Punch / Meteor Mash", 1)],
     "‡ One hundo serves ML + raids + Mega. Rare spawn — keep several high-ATK ones."),
  ("Gible", [
     ("Master", "Garchomp #23", HI, "Dragon Tail / Twister / Earth Power", 1),
     ("Raid / Mega", "Mega Garchomp + Garchomp strong Ground/Dragon raider", HI, "Mud Shot / Outrage", 1)],
     "‡ One hundo serves ML + raids + Mega. Rare spawn — keep high-ATK ones."),
  ("Dreepy", [
     ("Master", "Dragapult #193 (fell off; budget / Premier ML)", HI, "Dragon Tail / Shadow Ball / Outrage", 1)],
     "No mega. Rare/valuable spawn — keep a high-IV one for ML & collection."),
 ]),
 ("Raids (all costumed ‘Party Hat’ — value is the cosmetic/shiny)", [
  ("Party Hat Grimer (1★)", [("Collection", "Muk (Kanto) — not meta", COLL, "—", 1)],
     "Costume/shiny keep. No mega."),
  ("Party Hat Raticate (3★)", [("Collection", "Raticate — not meta", COLL, "—", 1)],
     "Costume/shiny keep."),
  ("Party Hat Nidorino (3★)", [("Collection", "Nidoking — not top-50", COLL, "—", 1)],
     "Costume/shiny keep. No mega."),
  ("Party Hat Gengar (3★)", [
     ("Raid / Mega", "Mega Gengar (top Ghost/Poison glass raider)", HI, "Lick / Shadow Ball  |  Shadow Claw / Sludge Bomb", 1)],
     "Raid gives final Gengar. Also a costume/shiny keep."),
  ("Party Hat Wobbuffet (3★)", [("Collection", "Wobbuffet — not meta", COLL, "—", 1)],
     "Costume/shiny keep. (Wynaut is Little Cup #2, but the raid yields Wobbuffet, not Wynaut — no Little Cup use here.)"),
 ]),
 ("Current Raid Bosses (leekduck.com/raid-bosses)", [
  ("Solgaleo (5★)", [
     ("Master", "Solgaleo #37 (to run Solgaleo itself)", HI, "Fire Spin / Psychic Fangs / Iron Head", 1),
     ("Raid / Fusion", "Fuse → Dusk Mane Necrozma (ML #31, top Steel raider) — inherits NECROZMA's IVs", "Any IV (fusion uses Necrozma's, not Solgaleo's)", "Metal Claw / Sunsteel Strike", 1)],
     "Fusion takes Necrozma's stats, NOT Solgaleo's — fuse with a JUNK Solgaleo, save your hundo Necrozma. A high-ATK Solgaleo is only worth it to run Solgaleo itself in ML (#37). Legendary raid = 10/10/10 IV floor."),
  ("Mega Salamence", [
     ("Raid / Mega", "Mega Salamence — top-tier mega Dragon/Flying raider (behind Mega Rayquaza, ≈ Mega Latios)", HI, "Dragon Tail / Draco Meteor", 1)],
     "PvP-fringe (ML #108, UL #321). Not #1 dragon — Mega Rayquaza leads — but far more accessible, and you can bring your own mega for the party damage boost. Keep a high-ATK one."),
 ]),
]

# ---- emit CSV ----
csv_path = os.path.join(HERE, "keepers.csv")
with open(csv_path, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Section", "Spawn", "League / Purpose", "Best form & rank",
                "IV target (Poke Genie)", "Recommended moveset", "Keep", "Family total", "Notes"])
    for section, fams in FAMILIES:
        for spawn, rows, note in fams:
            total = sum(r[4] for r in rows)
            for i, (lg, form, iv, mv, keep) in enumerate(rows):
                w.writerow([
                    section if (i == 0) else "",
                    spawn if i == 0 else "",
                    lg, form, iv, mv, keep,
                    total if i == 0 else "",
                    note if i == 0 else "",
                ])
print("wrote", csv_path)

# ---- emit markdown ----
md = ["# Ultra Unlock: 10th Anniversary — IV Keeper Guide\n",
      "Ranks from pvpoke's public dataset (see README for method). "
      "Legend: **PvP rows** = low ATK / high DEF+HP (rank ≤100). "
      "**Master / Raid / Mega rows** = high ATK (IV% ≥96% or 15 ATK). "
      "Only leagues where the family is top-50 get a keeper row; near-misses are in Notes.\n"]
for section, fams in FAMILIES:
    md.append(f"\n## {section}\n")
    md.append("| Spawn | League / Purpose | Best form & rank | IV target | Moveset | Keep | Total |")
    md.append("|---|---|---|---|---|:--:|:--:|")
    for spawn, rows, note in fams:
        total = sum(r[4] for r in rows)
        for i, (lg, form, iv, mv, keep) in enumerate(rows):
            md.append(f"| {spawn if i==0 else ''} | {lg} | {form} | {iv} | {mv} | {keep} | {total if i==0 else ''} |")
        md.append(f"| | | *{note}* | | | | |")
md_path = os.path.join(HERE, "KEEPERS.md")
open(md_path, "w").write("\n".join(md) + "\n")
print("wrote", md_path)

# ---- emit HTML (with sprites) ----
DEX = {
 "Bulbasaur": 1, "Charmander": 4, "Squirtle": 7, "Chikorita": 152, "Cyndaquil": 155,
 "Totodile": 158, "Treecko": 252, "Torchic": 255, "Mudkip": 258, "Turtwig": 387,
 "Chimchar": 390, "Piplup": 393, "Snivy": 495, "Tepig": 498, "Oshawott": 501,
 "Chespin": 650, "Fennekin": 653, "Froakie": 656, "Rowlet": 722, "Litten": 725,
 "Popplio": 728, "Grookey": 810, "Scorbunny": 813, "Sobble": 816, "Sprigatito": 906,
 "Fuecoco": 909, "Quaxly": 912, "Beldum": 374, "Gible": 443, "Dreepy": 885,
 "Party Hat Grimer (1★)": 88, "Party Hat Raticate (3★)": 20, "Party Hat Nidorino (3★)": 33,
 "Party Hat Gengar (3★)": 94, "Party Hat Wobbuffet (3★)": 202,
 "Solgaleo (5★)": 791, "Mega Salamence": 373,
}
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"


def cls(lg):
    l = lg.lower()
    if "collection" in l:
        return "coll"
    if "raid" in l or "master" in l:
        return "hi"
    return "pvp"


h = ["""<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Ultra Unlock 10th Anniversary — IV Keepers</title>
<style>
:root{color-scheme:light}
body{font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:24px;
 background:#ffffff;color:#1b2733}
h1{font-size:24px;margin:0 0 4px} .sub{color:#5b6b7a;margin:0 0 20px;max-width:70ch}
h2{font-size:16px;margin:28px 0 8px;color:#2a3a49;border-bottom:1px solid #e2e8ee;padding-bottom:6px}
table{border-collapse:collapse;width:100%;margin-bottom:8px}
td,th{padding:7px 9px;border-bottom:1px solid #edf1f5;vertical-align:middle;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#6b7b8a}
img{width:52px;height:52px;object-fit:contain;vertical-align:middle}
.mon{font-weight:600;white-space:nowrap}
.tag{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600}
.pvp{background:#e3f6ea;color:#14713a} .hi{background:#fdeee2;color:#9a4a12}
.coll{background:#eef1f4;color:#5b6b7a}
.rank{font-variant-numeric:tabular-nums} .note{color:#6b7b8a;font-size:13px}
.keep{text-align:center;font-weight:700} .tot{text-align:center;font-weight:700;color:#b26b00}
.legend span{margin-right:14px}
.tiers{background:#f5f8fb;border:1px solid #e2e8ee;border-radius:10px;padding:12px 16px;
 margin:0 0 18px;max-width:80ch}
.tiers b{color:#1b2733} .tiers ul{margin:8px 0 6px;padding-left:20px} .tiers li{margin:2px 0}
.tiers .pct{color:#14713a;font-weight:700;font-variant-numeric:tabular-nums}
.ss b{font-size:13px} .ss code{background:#eef1f4;padding:1px 4px;border-radius:4px}
pre{white-space:pre-wrap;word-break:break-all;background:#f5f8fb;border:1px solid #e2e8ee;
 border-radius:8px;padding:10px 12px;font-size:13px;margin:4px 0 14px;max-width:90ch}
</style>
<h1>Ultra Unlock: 10th Anniversary — IV Keepers</h1>
<p style="margin:0 0 10px"><a href="rankings.html">→ PvP Rankings by League (Little / Great / Ultra / Master)</a></p>
<p class=sub>PvP ranks from pvpoke (pulled 2026-07-21). <b class=tag style="background:none;color:#14713a">green = capped PvP</b> keep low ATK / high DEF+HP.
<b class=tag style="background:none;color:#9a4a12">orange = Master/Raid/Mega</b> keep high ATK (IV% &ge;96 / 15 ATK).
<b class=tag style="background:none;color:#5b6b7a">grey = collection</b> keep 1 best/shiny.</p>
<div class=tiers>
<b>Capped-PvP keeper bar</b> — read Poke Genie's <b>Rank %</b> (the percentile, e.g. &ldquo;Rank 85.64%&rdquo;) — <b>not</b> the appraisal star %:
<ul>
<li>&#127942; Tournament / perfect &mdash; <span class=pct>Rank % &ge; 97.6</span> &nbsp;(&le; #100)</li>
<li>&#9989; Keep &amp; main it (recommended) &mdash; <span class=pct>Rank % &ge; 95</span> &nbsp;(&le; #205)</li>
<li>&#128076; Fine if it&rsquo;s your only copy &mdash; <span class=pct>Rank % &ge; 88</span> &nbsp;(&le; #500)</li>
</ul>
&hellip;only for a <b>top-~50 species</b> that also <b>reaches the CP cap</b>. Master / Raid / Mega ignore this &mdash; use appraisal <b>IV% &ge; 96</b> / 15 ATK.
</div>
"""]
S1 = ("+bulbasaur,+charmander,+squirtle,+chikorita,+cyndaquil,+totodile,+treecko,+torchic,"
      "+mudkip,+turtwig,+chimchar,+piplup,+snivy,+tepig,+oshawott,+chespin,+fennekin,+froakie,"
      "+rowlet,+litten,+popplio,+grookey,+scorbunny,+sobble,+sprigatito,+fuecoco,+quaxly,"
      "+beldum,+gible,+dreepy&3*,4*")
S2 = "+squirtle,+chikorita,+totodile,+mudkip,+piplup,+tepig&0-1attack&3-4defense&3-4hp"
ST = ("+bulbasaur,+charmander,+squirtle,+chikorita,+cyndaquil,+totodile,+treecko,+torchic,"
      "+mudkip,+turtwig,+chimchar,+piplup,+snivy,+tepig,+oshawott,+chespin,+fennekin,+froakie,"
      "+rowlet,+litten,+popplio,+grookey,+scorbunny,+sobble,+sprigatito,+fuecoco,+quaxly,"
      "+beldum,+gible,+dreepy&0*,1*,2*&!shiny&!pvp")
h.append("<h2>Quick in-game search strings</h2>")
h.append("<p class=note>Paste into the Pokémon GO search bar. <code>+name</code> = whole evolution "
         "line, <code>3*,4*</code> = high IV (incl. hundos); IV stats use a 0–4 scale (3–4 = 11–15 IV). "
         "<b>Order:</b> run String 2 first, nickname each PvP keeper so its name contains "
         "<code>pvp</code>, THEN run Transfer — <code>!pvp</code> + <code>!shiny</code> + the "
         "<code>0*,1*,2*</code> filter keep your tagged gems, shinies, and hundos safe.</p>")
for label, s in [("KEEP — high IV (Mega / Raid / Master / Max-Battle + collection)", S1),
                 ("PvP shape → then run Poke Genie (keep Rank % ≥ 95)", S2),
                 ("TRANSFER — junk copies (low IV, non-shiny)", ST)]:
    h.append(f"<div class=ss><b>{label}</b><pre>{s}</pre></div>")
for section, fams in FAMILIES:
    h.append(f"<h2>{section}</h2>")
    h.append("<table><tr><th></th><th>Spawn</th><th>League / Purpose</th><th>Best form &amp; rank</th>"
             "<th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr>")
    for spawn, rows, note in fams:
        total = sum(r[4] for r in rows)
        n = len(rows)
        dex = DEX.get(spawn)
        img = f'<img loading=lazy src="{ART.format(dex)}" alt="">' if dex else ""
        for i, (lg, form, iv, mv, keep) in enumerate(rows):
            c1 = f'<td rowspan={n} style="text-align:center">{img}</td>' if i == 0 else ""
            c2 = f'<td rowspan={n} class=mon>{spawn}</td>' if i == 0 else ""
            ct = f'<td rowspan={n} class=tot>{total}</td>' if i == 0 else ""
            h.append(f"<tr>{c1}{c2}<td><span class='tag {cls(lg)}'>{lg}</span></td>"
                     f"<td class=rank>{form}</td><td class=note>{iv}</td>"
                     f"<td>{mv}</td><td class=keep>{keep}</td>{ct}</tr>")
        h.append(f"<tr><td></td><td></td><td colspan=6 class=note>{note}</td></tr>")
    h.append("</table>")
h.append("</html>")
html_path = os.path.join(HERE, "index.html")
open(html_path, "w").write("\n".join(h))
print("wrote", html_path)
