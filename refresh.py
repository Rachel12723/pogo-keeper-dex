#!/usr/bin/env python3
"""Refresh the dex's source data, then rebuild every generated page.

Why this exists: the meta shifts fast (new Megas, move rebalances, pvpoke
re-scores), so the committed data goes stale — e.g. Mega Delphox becoming the
#1 Fire attacker never shows up until the data behind it is pulled again. This
is the one command that re-pulls the sources and regenerates everything, so a
refresh is reproducible instead of a pile of hand edits. See REFRESH.md for the
full runbook (and for the one source that must be updated by hand).

Usage:
    python3 refresh.py            # fetch pvpoke sources, then rebuild all pages
    python3 refresh.py --no-fetch # skip the download, just rebuild from data/
    python3 refresh.py --check    # report what would change, download nothing

What it CAN refresh automatically (pvpoke, public + reachable):
    data/gamemaster.json                     species, forms, tags, movesets
    data/rankings-little.json   (CP 500)     Little Cup overall ranking
    data/rankings-great.json    (CP 1500)    Great League overall ranking
    data/rankings-ultra.json    (CP 2500)    Ultra League overall ranking
    data/rankings-master.json   (CP 10000)   Master League overall ranking

What it can NOT (PvE per-type raid boards): data/pve_type_ranks_raw.json comes
from db.pokemongohub.net, which blocks automated access (403) and is denied by
this environment's egress policy. That board is what ranks the Fire/Water/...
raid attackers, so it must be refreshed by hand — REFRESH.md, step 2.
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
        if check_only:
            print("\n(--check: nothing written, nothing rebuilt.)")
            return
    else:
        print("== 1. Skipped source fetch (--no-fetch) ==")

    print("\n== 2. PvE per-type raid boards (manual) ==")
    print("   data/pve_type_ranks_raw.json is from db.pokemongohub.net, which blocks")
    print("   automated access. It is NOT refreshed here — see REFRESH.md step 2 if the")
    print("   raid-attacker ranks (e.g. the #1 Fire attacker) look out of date.")

    print("\n== 3. Rebuild all pages ==")
    rebuild()

    print("\nDone. Review `git diff`, sanity-check a few ranks on pvpoke.com, then commit.")


if __name__ == "__main__":
    main(sys.argv[1:])
