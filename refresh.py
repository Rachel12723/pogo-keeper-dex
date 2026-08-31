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
PVE_RAW = "pve_type_ranks_raw.json"
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
    for name, (url, ok) in SOURCES.items():
        dest = os.path.join(DATA, name)
        before = top_species(dest)
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
    return changed


def top_species_of(parsed):
    if isinstance(parsed, list) and parsed:
        return parsed[0].get("speciesId")
    if isinstance(parsed, dict) and parsed.get("pokemon"):
        return f'{len(parsed["pokemon"])} species'
    return None


def fetch_pve_board(page, tp):
    """Render one PGHub best-per-type board and return its ordered token list.

    The board is client-rendered, so we load the page, wait for the ranking anchors
    to hydrate, and read the "<dex>[-<Form>]" suffix off each /pokemon/<token> href
    (top -> bottom = best -> worst). Returns [] if the list never populated."""
    page.goto(PGHUB_BOARD.format(type=tp), wait_until="domcontentloaded", timeout=60_000)
    # wait until the list has hydrated (>= 40 attacker links) rather than a fixed sleep
    page.wait_for_function(
        "() => document.querySelectorAll('a[href*=\"/pokemon/\"]').length >= 40",
        timeout=30_000,
    )
    hrefs = page.eval_on_selector_all(
        'a[href*="/pokemon/"]',
        "els => els.map(e => e.getAttribute('href').replace('/pokemon/',''))",
    )
    return hrefs[:PVE_KEEP_TOP]


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

    boards, failures = {}, []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            for tp in PVE_TYPES:
                try:
                    arr = fetch_pve_board(page, tp)
                except Exception as e:  # noqa: BLE001 - one type failing shouldn't sink the rest
                    print(f"  ! {tp}: PGHub fetch failed ({type(e).__name__}) — keeping existing")
                    failures.append(tp)
                    continue
                if len(arr) < 40:
                    print(f"  ! {tp}: only {len(arr)} entries rendered (expected ~50) — keeping existing")
                    failures.append(tp)
                    continue
                boards[tp] = arr
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
    return [PVE_RAW]


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
