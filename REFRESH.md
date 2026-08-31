# Data Refresh Runbook

The meta shifts fast — new Megas ship, moves get rebalanced, pvpoke re-scores —
so the data committed here goes stale. When a rank looks wrong (e.g. **Mega
Delphox should be the #1 Fire attacker but isn't listed**), the fix is almost
never a hand edit to a page: it's re-pulling the source data and rebuilding. This
runbook is that procedure.

## TL;DR

```bash
python3 refresh.py        # re-pull pvpoke sources + rebuild every page
git diff                  # review — see "Verify" below
```

Then do the **manual PvE step** if the raid-attacker (per-type) ranks are stale —
`refresh.py` cannot reach that source. See step 2.

---

## Where every number comes from

| File (in `data/`) | Feeds | Source | Auto? |
|---|---|---|---|
| `gamemaster.json` | species, forms, tags, movesets (all pages) | pvpoke `src/data/gamemaster.json` | ✅ |
| `rankings-little.json` | Little Cup (CP 500) | pvpoke `rankings/all/overall/rankings-500.json` | ✅ |
| `rankings-great.json` | Great League (CP 1500) | pvpoke `rankings/all/overall/rankings-1500.json` | ✅ |
| `rankings-ultra.json` | Ultra League (CP 2500) | pvpoke `rankings/all/overall/rankings-2500.json` | ✅ |
| `rankings-master.json` | Master League (CP 10000) | pvpoke `rankings/all/overall/rankings-10000.json` | ✅ |
| `pve_type_ranks_raw.json` | **PvE raid-attacker rank per type** | db.pokemongohub.net best-per-type boards | ❌ manual |
| `pve_type_ranks.json` | derived from the raw board by `pve_ranks.py` | *(generated)* | ✅ |

pvpoke lives on `raw.githubusercontent.com` and is public + reachable.
PGHub (`db.pokemongohub.net`) **blocks automated access (403)** and is denied by
this sandbox's egress policy, so its board is the one thing you update by hand.

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

## Step 2 — Refresh the PvE per-type raid boards (manual)

`data/pve_type_ranks_raw.json` maps each type to an ordered list of PGHub
best-per-type entries — **position = rank**:

```json
"fire": ["6-Mega_Y", "643-Shadow", "257-Mega", "806", ...]
```

Each entry is `<dex>` or `<dex>-<Form>`, taken from the `href` suffix on
`https://db.pokemongohub.net/pokemon-list/best-per-type/<type>` (top → bottom =
best → worst; the repo keeps the top 50 per type). Form tokens match the map in
`pve_ranks.py` (`Mega`, `Mega_X`, `Mega_Y`, `Shadow`, `Primal`, `Apex_Shadow`, …).

Because the board can't be fetched here, update it by hand when a new top attacker
lands (this is exactly the Mega Delphox case — a new `655-Mega` at the top of the
`fire` list):

1. Open the best-per-type page for the affected type(s) in a browser.
2. Read the order top-to-bottom and edit that type's array in
   `data/pve_type_ranks_raw.json` to match (insert/reorder/remove entries; keep
   ~50). Use the `<dex>-<Form>` suffix format above.
3. Rebuild the derived board and pages:
   ```bash
   python3 refresh.py --no-fetch
   ```
   (or just `python3 pve_ranks.py && python3 build_dex.py`).

If PGHub ever becomes reachable from the run environment, wire it into
`refresh.py` alongside the pvpoke sources and delete this manual step.

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
