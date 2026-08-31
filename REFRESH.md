# Data Refresh Runbook

The meta shifts fast — new Megas ship, moves get rebalanced, pvpoke re-scores —
so the data committed here goes stale. When a rank looks wrong (e.g. **Mega
Delphox should be the #1 Fire attacker but isn't listed**), the fix is almost
never a hand edit to a page: it's re-pulling the source data and rebuilding. This
runbook is that procedure.

## TL;DR

```bash
python3 refresh.py        # re-pull pvpoke + PGHub sources, rebuild every page
git diff                  # review — see "Verify" below
```

`refresh.py` now refreshes **both** sources: the pvpoke league data (step 1) and
the PGHub PvE per-type raid boards (step 2). The PGHub step needs Playwright — a
one-time setup (see step 2). If Playwright isn't installed, that step is skipped
gracefully and you fall back to editing the board by hand (also step 2).

---

## Where every number comes from

| File (in `data/`) | Feeds | Source | Auto? |
|---|---|---|---|
| `gamemaster.json` | species, forms, tags, movesets (all pages) | pvpoke `src/data/gamemaster.json` | ✅ |
| `rankings-little.json` | Little Cup (CP 500) | pvpoke `rankings/all/overall/rankings-500.json` | ✅ |
| `rankings-great.json` | Great League (CP 1500) | pvpoke `rankings/all/overall/rankings-1500.json` | ✅ |
| `rankings-ultra.json` | Ultra League (CP 2500) | pvpoke `rankings/all/overall/rankings-2500.json` | ✅ |
| `rankings-master.json` | Master League (CP 10000) | pvpoke `rankings/all/overall/rankings-10000.json` | ✅ |
| `pve_type_ranks_raw.json` | **PvE raid-attacker rank per type** | db.pokemongohub.net best-per-type boards | ✅ (Playwright) |
| `pve_type_ranks.json` | derived from the raw board by `pve_ranks.py` | *(generated)* | ✅ |

pvpoke lives on `raw.githubusercontent.com` and is public + reachable, so
`refresh.py` pulls it with plain `urllib`. The PGHub boards render **client-side**
(the served HTML contains no ranking), so they can't be scraped with `urllib` — they
need a real browser. `refresh.py` drives one via **Playwright** when it's installed;
if it isn't, or PGHub is unreachable (e.g. a cloud sandbox's egress policy), the
PvE step is skipped and the committed board is kept untouched — update it by hand
(step 2 fallback).

---

## Step 1 — Refresh the pvpoke sources (automatic)

```bash
python3 refresh.py --check   # dry run: what's reachable + what #1 would change
python3 refresh.py           # download + rebuild everything
python3 refresh.py --no-fetch # just rebuild from the current data/ (no download)
```

`refresh.py` downloads each pvpoke file to a temp file, validates it parses and
isn't truncated, and only then atomically replaces the committed copy — a failed
or blocked fetch leaves the old file untouched. Then it runs, in order:

```
pve_ranks.py → build_dex.py → build_pokedex.py → build_rankings.py → build_tables.py → build_max.py
```

## Step 2 — Refresh the PvE per-type raid boards (PGHub)

`data/pve_type_ranks_raw.json` maps each type to an ordered list of PGHub
best-per-type entries — **position = rank**:

```json
"fire": ["655-Mega", "6-Mega_Y", "643-Shadow", "257-Mega", "806", ...]
```

Each entry is `<dex>` or `<dex>-<Form>`, the suffix of the `/pokemon/<token>` links
on `https://db.pokemongohub.net/pokemon-list/best-per-type/<type>` (top → bottom =
best → worst; the repo keeps the top 50 per type). Form tokens match the map in
`pve_ranks.py` (`Mega`, `Mega_X`, `Mega_Y`, `Shadow`, `Primal`, `Apex_Shadow`, …).

### Automatic (default) — `refresh.py` does this in step 2

The PGHub boards render client-side, so `refresh.py` drives a headless browser
(Playwright) to load each of the 18 type pages and read the ranked `/pokemon/`
hrefs. **One-time setup** (Homebrew/system Python is PEP-668 "externally managed",
so use a venv):

```bash
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
```

Then run refreshes with the venv's Python so it can import Playwright:

```bash
.venv/bin/python refresh.py            # refreshes pvpoke AND PGHub, rebuilds pages
.venv/bin/python refresh.py --check    # report #1-per-type changes, write nothing
```

(`.venv/` is git-ignored.) If Playwright is missing or PGHub is unreachable,
`refresh.py` prints a note, leaves `pve_type_ranks_raw.json` untouched, and you use
the by-hand fallback below. A cloud sandbox can't reach PGHub, so it always falls
back there.

### By hand (fallback — no Playwright / no network to PGHub)

1. Open the best-per-type page for the affected type(s) in a browser.
2. Read the order top-to-bottom and edit that type's array in
   `data/pve_type_ranks_raw.json` to match (insert/reorder/remove entries; keep
   ~50). Use the `<dex>-<Form>` suffix format above.
3. Rebuild the derived board and pages from the current `data/` (no download):
   ```bash
   python3 refresh.py --no-fetch
   ```
   (or just `python3 pve_ranks.py && python3 build_dex.py`).

---

## Verify before committing

- `git diff --stat` — expect changes only in `data/*.json` and the regenerated
  `*.html` / `*.csv` (+ `KEEPERS.md`). No source `.py` should change.
- `refresh.py --check` prints when a file's #1 entry moves — a good gut check
  that the pull did something and nothing got truncated.
- Spot-check one or two borderline ranks against pvpoke.com / the PGHub board
  before spending dust on the strength of them.
- Update the "pulled YYYY-MM-DD" dates in `README.md`, `build_rankings.py`
  header, and the source note so the provenance stays honest.

## Commit

```bash
git add data/ *.html *.csv KEEPERS.md
git commit -m "chore(data): refresh pvpoke ranks + rebuild pages (YYYY-MM-DD)"
```
