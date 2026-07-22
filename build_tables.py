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
PVP = "PvP rank ≤100  (≈ stat-prod ≥99% / low ATK)"
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
  ("Sobble", [("Collection", "Inteleon — not meta", COLL, "—", 1)], "No mega."),
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
