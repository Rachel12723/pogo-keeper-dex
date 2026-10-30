#!/usr/bin/env python3
"""Refresh the dex's source data, then rebuild every generated page.

Why this exists: the meta shifts fast (new Megas, move rebalances, pvpoke
re-scores), so the committed data goes stale — e.g. Mega Delphox becoming the
#1 Fire attacker never shows up until the data behind it is pulled again. This
is the one command that re-pulls the sources and regenerates everything, so a
refresh is reproducible instead of a pile of hand edits. See REFRESH.md for the
full runbook (and for the one source that must be updated by hand).

Usage:
    python3 refresh.py            # fetch pvpoke + PGHub sources, then rebuild
    python3 refresh.py --no-fetch # skip the download, just rebuild from data/
    python3 refresh.py --check    # report what would change, download nothing

What it refreshes automatically:
    data/gamemaster.json                     species, forms, tags, movesets   (pvpoke)
    data/rankings-little.json   (CP 500)     Little Cup overall ranking       (pvpoke)
    data/rankings-great.json    (CP 1500)    Great League overall ranking     (pvpoke)
    data/rankings-ultra.json    (CP 2500)    Ultra League overall ranking     (pvpoke)
    data/rankings-master.json   (CP 10000)   Master League overall ranking    (pvpoke)
    data/pve_type_ranks_raw.json             PvE per-type raid boards         (PGHub)

The pvpoke files live on raw.githubusercontent.com (public, plain JSON) and are
fetched with urllib. The PGHub best-per-type boards render client-side (the served
HTML has no ranking in it), so they need a real browser: this uses Playwright, and
only when it's importable. Playwright is an OPTIONAL dependency — if it's missing
(or PGHub is unreachable, e.g. a cloud sandbox's egress policy blocks it), the PvE
step degrades gracefully: it prints one-time setup instructions, keeps the existing
data/pve_type_ranks_raw.json untouched, and you fall back to REFRESH.md step 2
(update that file by hand). See REFRESH.md for the full runbook.

One-time Playwright setup (so `python3 refresh.py` refreshes PGHub too):
    python3 -m venv .venv
    .venv/bin/pip install playwright
    .venv/bin/playwright install chromium
then run refreshes with  .venv/bin/python refresh.py  (or activate the venv first).
"""
import json
import os
import subprocess
import sys
import tempfile
import datetime
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

PVPOKE = "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data"

# PGHub best-per-type raid-attacker boards. Each type -> ordered list of "<dex>[-<Form>]"
# tokens (position = rank), taken from the /pokemon/<token> hrefs on the rendered board.
PGHUB_BOARD = "https://db.pokemongohub.net/pokemon-list/best-per-type/{type}"
PVE_TYPES = [
    "normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison",
    "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark",
    "steel", "fairy",
]
CHANGELOG = os.path.join(DATA, "CHANGELOG.md")
PVE_RAW = "pve_type_ranks_raw.json"
PVE_MOVES = "pve_type_moves.json"       # type -> {token: [fast, charged]} from the same raid boards
MAX_RAW = "max_type_ranks.json"         # type -> ordered Max Battle attackers (Dynamax / G-Max)
PGHUB_MAX_BOARD = "https://db.pokemongohub.net/pokemon-list/best-dynamax-per-type/{type}"
PVE_KEEP_TOP = 50  # entries kept per type (the file's existing convention)

# local filename -> (upstream url, quick sanity predicate on the parsed JSON)
SOURCES = {
    "gamemaster.json": (
        f"{PVPOKE}/gamemaster.json",
        lambda d: isinstance(d, dict) and len(d.get("pokemon", [])) > 500,
    ),
    "rankings-little.json": (
        f"{PVPOKE}/rankings/all/overall/rankings-500.json",
        lambda d: isinstance(d, list) and len(d) > 100 and "speciesId" in d[0],
    ),
    "rankings-great.json": (
        f"{PVPOKE}/rankings/all/overall/rankings-1500.json",
        lambda d: isinstance(d, list) and len(d) > 100 and "speciesId" in d[0],
    ),
    "rankings-ultra.json": (
        f"{PVPOKE}/rankings/all/overall/rankings-2500.json",
        lambda d: isinstance(d, list) and len(d) > 100 and "speciesId" in d[0],
    ),
    "rankings-master.json": (
        f"{PVPOKE}/rankings/all/overall/rankings-10000.json",
        lambda d: isinstance(d, list) and len(d) > 100 and "speciesId" in d[0],
    ),
}

# run in order: pve_ranks first (derives data/pve_type_ranks.json that build_dex
# reads), then every page builder. Each is independent given the data/ inputs.
BUILDERS = [
    "pve_ranks.py",
    "build_dex.py",
    "build_pokedex.py",
    "build_rankings.py",
    "build_tables.py",
    "build_max.py",
    "build_types.py",
]


def fetch(url):
    """Return the raw bytes at url. Honors HTTPS_PROXY/CA env if set (this repo's
    sandbox routes through an egress proxy); works unproxied on a normal box."""
    req = urllib.request.Request(url, headers={"User-Agent": "pogo-keeper-dex-refresh"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def top_species(path):
    """Best-effort '#1 entry' of a data file, for the before/after change report."""
    try:
        d = json.load(open(path))
    except (OSError, ValueError):
        return None
    if isinstance(d, list) and d:
        return d[0].get("speciesId")
    if isinstance(d, dict) and d.get("pokemon"):
        return f'{len(d["pokemon"])} species'
    return None


def refresh_sources(check_only):
    changed = []
    diffs = []
    for name, (url, ok) in SOURCES.items():
        dest = os.path.join(DATA, name)
        before = top_species(dest)
        try:
            old_parsed = json.load(open(dest))
        except (OSError, ValueError):
            old_parsed = None
        try:
            raw = fetch(url)
        except (urllib.error.URLError, OSError) as e:
            print(f"  ! {name}: FETCH FAILED ({e}) — keeping existing copy")
            continue
        try:
            parsed = json.loads(raw)
        except ValueError as e:
            print(f"  ! {name}: upstream is not valid JSON ({e}) — keeping existing copy")
            continue
        if not ok(parsed):
            print(f"  ! {name}: sanity check failed (truncated/unexpected) — keeping existing copy")
            continue
        after = top_species_of(parsed)
        mark = "" if before == after else f"   [top: {before} -> {after}]"
        if check_only:
            print(f"  - {name}: reachable, {len(raw):,} bytes{mark}")
            continue
        # atomic replace: write a temp in the same dir, fsync, rename over the old file
        fd, tmp = tempfile.mkstemp(dir=DATA, prefix=name + ".", suffix=".tmp")
        with os.fdopen(fd, "wb") as fh:
            fh.write(raw)
        os.replace(tmp, dest)
        print(f"  * {name}: updated ({len(raw):,} bytes){mark}")
        changed.append(name)
        diffs.append((name, old_parsed, parsed))
    write_changelog(diffs)
    return changed


LEAGUE_LABEL = {"rankings-little.json": "Little Cup (CP 500)",
                "rankings-great.json": "Great League (CP 1500)",
                "rankings-ultra.json": "Ultra League (CP 2500)",
                "rankings-master.json": "Master League (CP 10000)"}
MOVE_FIELDS = ("power", "energy", "energyGain", "cooldown", "buffs")


def diff_rankings(old, new):
    ids_o = [x["speciesId"] for x in old]
    ids_n = [x["speciesId"] for x in new]
    ro = {s: i + 1 for i, s in enumerate(ids_o)}
    rn = {s: i + 1 for i, s in enumerate(ids_n)}
    out = []
    if ids_o[:10] != ids_n[:10]:
        out.append(f"- Top 10: {', '.join(ids_o[:10])}  ->  {', '.join(ids_n[:10])}")
    top_in = [s for s in ids_n[:30] if ro.get(s, 10**9) > 30]
    top_out = [s for s in ids_o[:30] if rn.get(s, 10**9) > 30]
    if top_in or top_out:
        out.append(f"- Top 30 in: {', '.join(top_in) or '-'}; out: {', '.join(top_out) or '-'}")
    added = [s for s in ids_n if s not in ro]
    removed = [s for s in ids_o if s not in rn]
    if added or removed:
        out.append(f"- Pool added: {', '.join(added) or '-'}; removed: {', '.join(removed) or '-'}")
    movers = sorted(((abs(ro[s] - rn[s]), s) for s in rn if s in ro and min(ro[s], rn[s]) <= 50),
                    reverse=True)[:8]
    movers = [f"{s} #{ro[s]}->#{rn[s]}" for d, s in movers if d >= 5]
    if movers:
        out.append(f"- Biggest top-50 movers: {', '.join(movers)}")
    return out


def diff_gamemaster(old, new):
    out = []
    mo = {m["moveId"]: m for m in old.get("moves", [])}
    mn = {m["moveId"]: m for m in new.get("moves", [])}
    new_moves = [k for k in mn if k not in mo]
    if new_moves:
        out.append(f"- New moves: {', '.join(new_moves)}")
    for k, m in mn.items():
        if k in mo:
            d = [f"{f} {mo[k].get(f)}->{m.get(f)}" for f in MOVE_FIELDS if mo[k].get(f) != m.get(f)]
            if d:
                out.append(f"- Move {k}: {'; '.join(d)}")
    so = {m["speciesId"]: m for m in old.get("pokemon", [])}
    sn = {m["speciesId"]: m for m in new.get("pokemon", [])}
    new_sp = [k for k in sn if k not in so]
    if new_sp:
        out.append(f"- New species/forms: {', '.join(new_sp)}")
    for k, m in sn.items():
        if k in so:
            d = []
            if so[k].get("baseStats") != m.get("baseStats"):
                d.append(f"stats {so[k].get('baseStats')}->{m.get('baseStats')}")
            for f, label in (("fastMoves", "fast"), ("chargedMoves", "charged")):
                a, b = set(so[k].get(f, [])), set(m.get(f, []))
                if a != b:
                    d.append(f"{label} +{sorted(b - a)} -{sorted(a - b)}")
            if d:
                out.append(f"- Species {k}: {'; '.join(d)}")
    return out


def write_changelog(diffs):
    """Prepend a dated entry to data/CHANGELOG.md describing what this refresh changed
    (rank movements per league + gamemaster move/species/stat changes), so the history
    that the overwrite would otherwise lose is kept. Git history has the raw files."""
    sections = []
    for name, old, new in diffs:
        if old is None:
            continue
        try:
            lines = (diff_gamemaster(old, new) if name == "gamemaster.json"
                     else diff_rankings(old, new))
        except (KeyError, TypeError, AttributeError):
            continue
        if lines:
            title = "Gamemaster (moves / species)" if name == "gamemaster.json" else LEAGUE_LABEL.get(name, name)
            sections.append(f"### {title}\n" + "\n".join(lines))
    if not sections:
        print("  = changelog: no source changes")
        return
    entry = f"## {datetime.date.today().isoformat()}\n\n" + "\n\n".join(sections) + "\n"
    head = "# Data changelog\n\nWhat each `refresh.py` run changed in the pvpoke sources, newest first.\n\n"
    try:
        prev = open(CHANGELOG).read()
        prev = prev[len(head):] if prev.startswith(head) else prev
    except OSError:
        prev = ""
    with open(CHANGELOG, "w") as fh:
        fh.write(head + entry + ("\n" + prev if prev else ""))
    print(f"  * changelog: entry written to {os.path.relpath(CHANGELOG, HERE)}")


def top_species_of(parsed):
    if isinstance(parsed, list) and parsed:
        return parsed[0].get("speciesId")
    if isinstance(parsed, dict) and parsed.get("pokemon"):
        return f'{len(parsed["pokemon"])} species'
    return None


ROWS_JS = """() => [...document.querySelectorAll('tbody tr')].map(tr => {
  const o = {};
  tr.querySelectorAll('td').forEach(td => { o[td.getAttribute('data-column-id')] =
    td.innerText.trim().replace(/\\s+/g, ' '); });
  const a = tr.querySelector('a[href*="/pokemon/"]');
  o._href = a && a.getAttribute('href');
  return o; }).filter(o => o._href)"""


def fetch_board_rows(page, url, min_rows):
    """Render one PGHub board and return its rows, top -> bottom, as dicts keyed by the
    table's data-column-id (attacker_name, qm_name, cm_name, ... plus _href).

    The boards are client-rendered, so we load the page and wait until at least
    `min_rows` attacker rows have hydrated rather than sleeping a fixed time."""
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_function(
        "n => document.querySelectorAll('tbody tr a[href*=\"/pokemon/\"]').length >= n",
        arg=min_rows, timeout=40_000,
    )
    return page.evaluate(ROWS_JS)


def token_of(row):
    """'<dex>[-<Form>]' suffix of the row's /pokemon/<token> href."""
    return row["_href"].replace("/pokemon/", "")


def refresh_pve_boards(check_only):
    """Refresh data/pve_type_ranks_raw.json from the live PGHub boards via Playwright.

    Optional + fail-soft: if Playwright isn't installed or PGHub can't be reached, we
    print what to do and leave the committed file untouched (REFRESH.md step 2 covers
    the by-hand fallback). Never raises — a blocked PvE refresh must not abort the run."""
    dest = os.path.join(DATA, PVE_RAW)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ! Playwright not installed — skipping PGHub PvE refresh, keeping the")
        print("    existing data/pve_type_ranks_raw.json (update by hand per REFRESH.md")
        print("    step 2, or install it once:  python3 -m venv .venv &&")
        print("    .venv/bin/pip install playwright && .venv/bin/playwright install chromium)")
        return []

    try:
        before = json.load(open(dest))
    except (OSError, ValueError):
        before = {}

    boards, moves, failures = {}, {}, []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            for tp in PVE_TYPES:
                try:
                    rows = fetch_board_rows(page, PGHUB_BOARD.format(type=tp), 40)[:PVE_KEEP_TOP]
                    arr = [token_of(r) for r in rows]
                except Exception as e:  # noqa: BLE001 - one type failing shouldn't sink the rest
                    print(f"  ! {tp}: PGHub fetch failed ({type(e).__name__}) — keeping existing")
                    failures.append(tp)
                    continue
                if len(arr) < 40:
                    print(f"  ! {tp}: only {len(arr)} entries rendered (expected ~50) — keeping existing")
                    failures.append(tp)
                    continue
                boards[tp] = arr
                moves[tp] = {token_of(r): [r.get("qm_name", ""), r.get("cm_name", "")] for r in rows}
                b0 = (before.get(tp) or [None])[0]
                mark = "" if b0 == arr[0] else f"   [#1: {b0} -> {arr[0]}]"
                print(f"  - {tp}: {len(arr)} attackers{mark}" if check_only
                      else f"  * {tp}: {len(arr)} attackers{mark}")
            browser.close()
    except Exception as e:  # noqa: BLE001 - launch/connection failure -> whole step degrades
        print(f"  ! PGHub PvE refresh unavailable ({type(e).__name__}: {e}) — keeping existing file")
        return []

    if failures and boards:
        # keep the old ordering for any type we couldn't re-fetch, refresh the rest
        for tp in failures:
            if tp in before:
                boards[tp] = before[tp]

    if not boards or len(boards) < len(PVE_TYPES):
        missing = [t for t in PVE_TYPES if t not in boards]
        if missing:
            print(f"  ! incomplete PvE refresh (missing {', '.join(missing)}) — file left unchanged")
            return []

    if check_only:
        return []

    # atomic replace, same discipline as the pvpoke sources
    ordered = {tp: boards[tp] for tp in PVE_TYPES}  # keep the canonical type order
    fd, tmp = tempfile.mkstemp(dir=DATA, prefix=PVE_RAW + ".", suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(ordered, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, dest)
    print(f"  * {PVE_RAW}: updated (18 types)")
    if moves and all(tp in moves for tp in PVE_TYPES):
        write_json_atomic(os.path.join(DATA, PVE_MOVES), {tp: moves[tp] for tp in PVE_TYPES})
        print(f"  * {PVE_MOVES}: updated (best fast/charged move per board entry)")
    return [PVE_RAW]


def write_json_atomic(dest, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dest), prefix=os.path.basename(dest) + ".", suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(obj, fh, indent=1)
        fh.write("\n")
    os.replace(tmp, dest)


def refresh_max_boards(check_only):
    """Refresh data/max_type_ranks.json (PGHub best Max Battle attackers per type).

    Same fail-soft contract as the PvE step. Boards are short (Dynamax/G-Max only), so the
    hydration threshold is low; a type is kept only if >= 3 rows rendered."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ! Playwright not installed — skipping Max Battle refresh (keeping existing file)")
        return []
    dest = os.path.join(DATA, MAX_RAW)
    try:
        before = json.load(open(dest))
    except (OSError, ValueError):
        before = {}
    boards = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            for tp in PVE_TYPES:
                try:
                    rows = fetch_board_rows(page, PGHUB_MAX_BOARD.format(type=tp), 3)
                except Exception as e:  # noqa: BLE001
                    print(f"  ! {tp}: Max board fetch failed ({type(e).__name__}) — keeping existing")
                    continue
                boards[tp] = [{"token": token_of(r), "name": r.get("attacker_name", ""),
                               "tier": r.get("tier", ""), "fast": r.get("qm_name", ""),
                               "max": r.get("cm_name", ""), "dmg": r.get("dynamax_maxMoveDamage", "")}
                              for r in rows]
                # tier is only printed on the first row of each tier group -> carry it down
                last = ""
                for e in boards[tp]:
                    last = e["tier"] or last
                    e["tier"] = last
                b0 = (before.get(tp) or [{}])[0].get("token")
                mark = "" if b0 == boards[tp][0]["token"] else f"   [#1: {b0} -> {boards[tp][0]['token']}]"
                print(f"  {'-' if check_only else '*'} {tp}: {len(rows)} max attackers{mark}")
            browser.close()
    except Exception as e:  # noqa: BLE001
        print(f"  ! Max Battle refresh unavailable ({type(e).__name__}: {e}) — keeping existing file")
        return []
    for tp in PVE_TYPES:  # fill any type we couldn't re-fetch from the old file
        if tp not in boards and tp in before:
            boards[tp] = before[tp]
    if check_only or len(boards) < len(PVE_TYPES):
        if len(boards) < len(PVE_TYPES):
            print("  ! incomplete Max Battle refresh — file left unchanged")
        return []
    write_json_atomic(dest, {tp: boards[tp] for tp in PVE_TYPES})
    print(f"  * {MAX_RAW}: updated")
    return [MAX_RAW]


def rebuild():
    for script in BUILDERS:
        print(f"  $ python3 {script}")
        r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           cwd=HERE, capture_output=True, text=True)
        for line in r.stdout.splitlines():
            print(f"      {line}")
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            raise SystemExit(f"BUILD FAILED in {script} (exit {r.returncode})")


def main(argv):
    check_only = "--check" in argv
    no_fetch = "--no-fetch" in argv

    if not no_fetch:
        print("== 1. Refresh pvpoke sources ==")
        refresh_sources(check_only)
        print("\n== 2. Refresh PGHub PvE per-type raid boards ==")
        refresh_pve_boards(check_only)
        print("\n== 2b. Refresh PGHub Max Battle (Dynamax) per-type boards ==")
        refresh_max_boards(check_only)
        if check_only:
            print("\n(--check: nothing written, nothing rebuilt.)")
            return
    else:
        print("== 1. Skipped source fetch (--no-fetch) ==")
        print("== 2. Skipped PGHub PvE refresh (--no-fetch) ==")

    print("\n== 3. Rebuild all pages ==")
    rebuild()

    print("\nDone. Review `git diff`, sanity-check a few ranks on pvpoke.com, then commit.")


if __name__ == "__main__":
    main(sys.argv[1:])
