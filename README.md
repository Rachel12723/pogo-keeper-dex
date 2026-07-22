# Ultra Unlock: 10th Anniversary Edition — IV Keeper Guide

Which spawns from the [LeekDuck event page](https://leekduck.com/events/ultra-unlock-10th-anniversary-edition/)
are worth keeping, and with which IVs.

- **[KEEPERS.md](KEEPERS.md)** — the rendered tables (read this).
- **[keepers.csv](keepers.csv)** — same data, import into Google Sheets / Numbers.
- **[build_tables.py](build_tables.py)** — regenerates both from the ranking data.
- **[data/](data/)** — raw pvpoke ranking JSON (the evidence).

## How to read a keeper

Two opposite goals, so a species can want **two different IV builds**:

| Purpose | You want | Poke Genie bar |
|---|---|---|
| **Capped PvP** — Little (500) / Great (1500) / Ultra (2500) | **LOW Attack**, high DEF + HP | **PvP rank ≤ 100** (≈ stat-product **≥ 99.0%**) |
| **Master League + Raids + Mega** (no CP cap) | **HIGH Attack / overall** | appraisal **IV% ≥ 96%** (14/15/15) or **15 ATK**; hundo ideal |

Notes:
- The percentage Poke Genie shows on the card is the **stat-product %** (100.0% = that
  species' rank-1 PvP IV). Tap in to see the ordinal **rank / 4096**. Mapping:
  rank ≤100 ≈ **99%**, ≤500 ≈ 98%, ≤1000 ≈ 97%. Keep at **≥99%** to match "rank ≤100".
- 0-attack spreads (0/15/15, 0/14/15, 1/15/15…) are usually **rank single digits** for
  most species, so they clear the capped-PvP bar easily.
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
