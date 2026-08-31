# Handoff: finish the PvE raid-attacker data refresh (needs local network)

**Purpose of this file:** the pvpoke half of the data has already been refreshed
and committed. The **PvE per-type raid-attacker boards** (`data/pve_type_ranks_raw.json`)
still could not be updated, because they come from `db.pokemongohub.net`, which is
**blocked by the cloud sandbox's network egress policy**. This file is a complete,
standalone brief so a **new Claude Code session running on a local machine** (whose
network can reach PGHub) can finish the job.

> **How to use this:** on your local machine, open a terminal, `cd` into a local
> clone of this repo, run `claude`, and paste this file's contents (or say
> "follow PVE_REFRESH_HANDOFF.md") as the first message.

---

## 0. Confirm you actually have network access (do this first)

A remote/cloud session will fail here exactly as the previous one did. Verify you
are local and unblocked:

```bash
pwd                 # should be your local clone path, NOT /home/user/...
curl -s -o /dev/null -w "%{http_code}\n" https://db.pokemongohub.net/pokemon-list/best-per-type/fire
```

- `200` → you're good, continue.
- `000` / `403` / an "agent-proxy … connect_rejected" message → you're still in a
  restricted environment. **Stop** — this can't be completed here; tell the user.

---

## 1. What's already done (don't redo)

- `refresh.py` re-pulls the pvpoke sources (gamemaster + 4 league rankings) and
  rebuilds every page. Already run; those files are fresh and committed.
- `REFRESH.md` is the full runbook. **Read it** — §"Step 2" defines the exact data
  format you're about to produce.
- Branch: `claude/mega-delphox-fire-attacker-hbxscv`.

## 2. What you need to do

Update `data/pve_type_ranks_raw.json` from the live PGHub best-per-type boards,
then rebuild and verify. This is the file that determines the raid-attacker rank
shown per type (e.g. it's why **Mega Delphox** should now top Fire but currently
doesn't).

### 2a. Pull each type's board

For every type below, fetch its board and read the ranking **top-to-bottom (best →
worst)**:

```
https://db.pokemongohub.net/pokemon-list/best-per-type/<type>
```

Types (all 18, keep these exact keys):
`normal, fire, water, electric, grass, ice, fighting, poison, ground, flying,
psychic, bug, rock, ghost, dragon, dark, steel, fairy`

Use the WebFetch tool (or open in a browser). The rank order is the display order;
each Pokémon links to a detail page whose URL/href suffix is the `<dex>-<Form>`
token you need.

### 2b. Encode each entry as `<dex>[-<Form>]`

- `<dex>` = National Pokédex number (e.g. Delphox = `655`).
- `<Form>` = form token, **omitted for the plain form**. Use exactly these tokens
  (they must match `TOK_PRETTY` in `pve_ranks.py`):

  `Mega`, `Mega_X`, `Mega_Y`, `Primal`, `Shadow`, `Origin`, `Apex_Shadow`,
  `Alola`, `Galarian`, `Hisuian`, `Paldean`, `Therian`, `Incarnate`,
  `Standard`, `Standard_Shadow`, `Crowned_Sword`, `Crowned_Shield`,
  `Dusk_Mane`, `Dawn_Wings`, `Black`, `White`

  Examples: Mega Charizard Y = `6-Mega_Y`; Shadow Moltres = `146-Shadow`;
  Delphox = `655`; **Mega Delphox = `655-Mega`**.

- Keep about the **top 50 per type** (the file's existing convention), in order.

Current shape for reference (Fire, first entries — this is the STALE data you're
replacing):

```json
"fire": ["6-Mega_Y", "643-Shadow", "257-Mega", "806", "485-Shadow", "6-Mega_X", ...]
```

Write all 18 arrays back into `data/pve_type_ranks_raw.json`, same structure (one
key per type, value = ordered list of tokens).

### 2c. Rebuild and verify

```bash
python3 refresh.py --no-fetch      # re-derives pve_type_ranks.json + rebuilds every page
```

`pve_ranks.py`'s printed "=== Fire ===" line should now show **Mega Delphox #1**
(the whole point). Then sanity-check:

```bash
git diff --stat                    # expect data/pve_type_ranks*.json + regenerated *.html/*.csv
grep -c "Mega Delphox" dex.html    # should be > 0
```

If a name doesn't resolve (shows as `#<dex>` instead of a name), the `<dex>` is
wrong or the form token isn't in the `TOK_PRETTY` map above — fix the token.

## 3. Commit & push

```bash
git add data/ *.html *.csv KEEPERS.md
git commit -m "chore(data): refresh PvE per-type raid boards from PGHub (YYYY-MM-DD)"
git push -u origin claude/mega-delphox-fire-attacker-hbxscv
```

## 4. Bonus (optional): make it permanent

If PGHub is reachable, wire the board fetch + `<dex>-<Form>` parsing into
`refresh.py` alongside the pvpoke sources (there's a note marking where), and
delete the "manual" caveat from `REFRESH.md` §Step 2. Then a full refresh —
pvpoke *and* PvE — is the single command `python3 refresh.py`.

---

### One-paragraph summary to paste as the opening message

> Follow `PVE_REFRESH_HANDOFF.md` in this repo. Short version: the pvpoke data is
> already refreshed; I need you to refresh the PvE raid-attacker boards in
> `data/pve_type_ranks_raw.json` from `db.pokemongohub.net/pokemon-list/best-per-type/<type>`
> (all 18 types), encoding each entry as `<dex>-<Form>` per the file's format,
> then run `python3 refresh.py --no-fetch`, verify Mega Delphox is now #1 Fire,
> and commit + push to branch `claude/mega-delphox-fire-attacker-hbxscv`. First
> confirm you have network access with the curl check in §0 — if it returns 000/403
> you're not on a local network and must stop.
