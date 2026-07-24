# Ultra Unlock: 10th Anniversary Edition — IV Keeper Guide

Which spawns from the [LeekDuck event page](https://leekduck.com/events/ultra-unlock-10th-anniversary-edition/)
are worth keeping, and with which IVs.

- **[KEEPERS.md](KEEPERS.md)** — the rendered tables (read this).
- **[keepers.csv](keepers.csv)** — same data, import into Google Sheets / Numbers.
- **[build_tables.py](build_tables.py)** — regenerates both from the ranking data.
- **[data/](data/)** — raw pvpoke ranking JSON (the evidence).

## How to read a keeper

Two opposite goals, so a species can want **two different IV builds**:

| Purpose | You want | Bar |
|---|---|---|
| **Capped PvP** — Little (500) / Great (1500) / Ultra (2500) | **LOW Attack**, high DEF + HP | Poke Genie **Rank ≤ #100** (Rank% ≥ 97.6) |
| **Master League + Raids + Mega** (no CP cap) | **HIGH Attack / overall** | appraisal **IV% ≥ 96%** (14/15/15) or **15 ATK**; hundo ideal |

### Poke Genie shows THREE numbers — don't confuse them

For each league Poke Genie's PvP tab shows e.g. `Rank 85.64% (#589)` and `Stat Prod 97.63%`,
and the other screen shows the plain appraisal `%`:

- **Ordinal `#N`** — the N-th best IV of 4096. *Use this — it's unambiguous.*
- **Rank %** = a **percentile** = `(4096 − N) / 4096`. This is the big % most people read.
- **Stat Prod %** — closeness of stat product to the #1 IV (very compressed; poor discriminator).
- **Appraisal %** = `(ATK+DEF+HP)/45` — the in-game star rating. **Ignore this for capped PvP**
  (a *high* appraisal % usually means high Attack = a *worse* GL/UL IV).

Mapping so every threshold lines up:

| Ordinal | Rank % (percentile) | Stat Prod % |
|---|---|---|
| ≤ #41  | 99.0 | ~99.8 |
| ≤ #100 | **97.6** | ~99.0 |
| ≤ #205 | **95.0** | ~98.7 |
| ≤ #500 | 87.8 | ~98.0 |
| ≤ #1000| 75.6 | ~97.0 |

**Practical keeper bar (in the Rank % you read):** ≥ **95** (≤ #205) to keep & main;
≥ 97.6 (≤ #100) for tournaments; ≥ ~88 (≤ #500) if it's your only copy — **but only for a
top-~50 species that also reaches the CP cap.** There's no % where a *meta* species becomes
worthless; it just gets outclassed. Species viability is the gate; this % is the tiebreaker.

Notes:
- 0-attack spreads (0/15/15, 0/14/15, 1/15/15…) are usually **ordinal single digits** for
  most species, so they clear the capped-PvP bar easily — even though their *appraisal* % looks low.
- **Reaching the CP cap matters as much as rank** — a rank-10 IV that only hits 1,420 in
  GL is worse than a rank-60 one that hits 1,498. Poke Genie shows the max CP; check it.
- **Species viability is a gate; IV quality is only a tiebreaker.** A perfect 0/15/15 of a
  species ranked #700 is a *transfer* — IVs can't rescue an unusable species. Conversely a
  meta species with a rank-40-within-species IV is still a keep (capped-league stat gap
  from rank-1 to rank-100 is <1%).

## Decision rule used for the tables

1. **Species gate** — is the family top-**50** in any league? (Your chosen threshold.)
   If not, and it has no Mega / raid value → **Collection only** (keep 1 best-IV or shiny).
2. **List every league it clears**, with its **absolute rank** (never collapsed to one
   "winner" — so you can compare across your own boxes). Near-misses (51–~110) are in *Notes*.
3. **Form follows league** — base form for Little Cup, final evo for GL/UL/ML.
4. **Keep count is additive**: one low-ATK copy per capped league it clears (GL and UL kept
   **separate** — they need different levels) + one high-ATK hundo if it's a Master / raid /
   Mega piece.
   - **† Mega X *and* Y**: counted as 2 per request, but *one* Charizard Mega-evolves into
     either — 1 hundo mechanically covers both (same high-ATK IV goal).
   - **‡ ML + Mega overlap** (Beldum, Gible): one hundo serves Master League, raids, and the
     Mega — counted on both rows for visibility, but it's the same physical mon.

## Sources & honesty note

- **PvP ranks + movesets**: pvpoke's public ranking dataset (`data/rankings-*.json`, pulled
  **2026-07-21** from `raw.githubusercontent.com/pvpoke/pvpoke`). Same data behind pvpoke.com.
  This is the authority for exact per-league rank numbers and rank-1 IV spreads.
- **Mega existence + raid-attacker value**: established PvE knowledge (no live raid tier list
  was fetched). These are stable facts (e.g. Mega Metagross = best Steel raider).
- `db.pokemongohub.net` was the originally requested source but blocks automated access
  (**403**), and the local browser read-tool was disabled by org policy — hence pvpoke, which
  is the better source for exact PvP ranks anyway.
- **Meta shifts fast.** Re-run `build_tables.py` after a big move/rebalance update to refresh
  ranks. Confirm anything borderline on pvpoke.com before spending dust.

## Event spawn list (source of truth, page order)

- **Jul 21–23**: Bulbasaur, Charmander, Squirtle, Chikorita, Cyndaquil, Totodile, Treecko, Torchic, Mudkip
- **Jul 23–25**: Turtwig, Chimchar, Piplup, Snivy, Tepig, Oshawott, Chespin, Fennekin, Froakie
- **Jul 25–27**: Rowlet, Litten, Popplio, Grookey, Scorbunny, Sobble, Sprigatito, Fuecoco, Quaxly
- **Lure (normal)**: Beldum, Gible, Dreepy
- **Raids**: Party Hat Grimer (1★); Party Hat Raticate / Nidorino / Gengar / Wobbuffet (3★)

## Quick in-game search strings

Pokémon GO per-stat IV search uses a **0–4 bucket scale**: `0`=0IV · `1`=1–5 · `2`=6–10 ·
`3`=11–14 · `4`=15. Star tiers: `4*`=100%, `3*`=82–99% (so use **`3*,4*`** for "high IV" incl.
hundos). `+name`=**whole evolution line** (`+bulbasaur` → Bulbasaur/Ivysaur/Venusaur). `,`=OR
(binds tighter), `&`=AND, `!`=NOT — a trailing `&filter` applies to the whole comma list.
(If your client parses it per-name instead, repeat the filter after each name.)

**String 1 — KEEP (high IV): a good copy of EVERY species** (all 30 wild + lure — Mega / Raid /
Master / Max-Battle / PvP / collection). Grab the best of each:
```
+bulbasaur,+charmander,+squirtle,+chikorita,+cyndaquil,+totodile,+treecko,+torchic,+mudkip,+turtwig,+chimchar,+piplup,+snivy,+tepig,+oshawott,+chespin,+fennekin,+froakie,+rowlet,+litten,+popplio,+grookey,+scorbunny,+sobble,+sprigatito,+fuecoco,+quaxly,+beldum,+gible,+dreepy&3*,4*
```
(Raid bosses — Party Hats / Solgaleo / Salamence — aren't here; you catch few, judge by hand.)
For raid / Mega / Max-Battle attack focus, append `&3-4attack` (or `&4attack` = perfect attack).

**String 2 — PvP shape** (capped-league species) → low-ATK / high-bulk, then Poke Genie (keep Rank % ≥ 95):
```
+squirtle,+chikorita,+totodile,+mudkip,+piplup,+tepig,+oshawott,+popplio,+fuecoco&0-1attack&3-4defense&3-4hp
```

**Transfer — junk copies.** All 30 species (same as String 1), opposite IV filter — dumps low-IV,
non-shiny, **non-tagged** copies while keeping hundos, shinies, and your tagged PvP gems:
```
+bulbasaur,+charmander,+squirtle,+chikorita,+cyndaquil,+totodile,+treecko,+torchic,+mudkip,+turtwig,+chimchar,+piplup,+snivy,+tepig,+oshawott,+chespin,+fennekin,+froakie,+rowlet,+litten,+popplio,+grookey,+scorbunny,+sobble,+sprigatito,+fuecoco,+quaxly,+beldum,+gible,+dreepy&0*,1*,2*&!shiny&!pvp
```

- **Order matters:** run String 2 → nickname each PvP keeper so its name contains **`pvp`** →
  *then* run Transfer. `!pvp` protects the tagged low-star PvP gems that `0*,1*,2*` would otherwise dump.
  (Change `pvp` to whatever tag you use.)
- **Mudkip is in String 1 & String 2** — keep a hundo for Mega Swampert/ML *and* a low-ATK one for GL/UL.
- **Review rares before transferring** — even low-IV **Beldum / Gible / Dreepy** are worth the candy.
- **Galar starters (Grookey/Scorbunny/Sobble)** have Gigantamax Max-Battle value (G-Max Inteleon is
  the top Water Max attacker) — keep high-ATK ones.
- **Raids** (few catches, judge individually): high-IV **Party Hat Gengar** (Mega Gengar) &
  **Solgaleo** (ML #37) + a junk Solgaleo to fuse; high-ATK **Mega Salamence**. Other Party Hats
  = shiny/costume only.
