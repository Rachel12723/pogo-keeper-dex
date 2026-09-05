# Repo conventions

## Workflow

- **Always merge to `main` after implementation.** Once a change is implemented,
  verified, and pushed on its feature branch, merge it into `main` (and push
  `main`) as part of finishing the task — don't leave completed work stranded on
  a branch. This is the default here; no need to ask each time.

## Regenerating pages

Generated pages (`dex.html`, `pokedex.html`, `rankings.html`, `event.html`,
`max.html`, `KEEPERS.md`, and the `*.csv`) are built from `data/` by the
`build_*.py` / `pve_ranks.py` scripts — never hand-edit them. After changing a
builder or the data, run `python3 refresh.py --no-fetch` (rebuild only) or
`python3 refresh.py` (re-pull sources + rebuild). See `REFRESH.md` for the full
data-refresh runbook.
