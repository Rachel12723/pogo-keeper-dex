#!/usr/bin/env python3
"""Complete Pokédex ('our flavor') — every released species, folded by family.

Source: pvpoke's Pokémon GO gamemaster (data/gamemaster.json) + our rank pools.
- Cosmetic COSTUME forms are de-duplicated (same dex+types+stats as the base) so a
  species shows once; real alt-formes (Deoxys, Rotom, regionals…) survive.
- One row per evolutionary family at its lowest ('first appearance') dex #, by dex.
- League / Purpose lists ALL usage: each PvP league a form ranks in (LC50/GL·UL·ML60),
  (LC top 50 / GL·UL top 100 / ML top 75) plus PvE raid-attacker lines (real PGHub per-type
  ranks via pve_ranks.by_dex(): top-10 catchable / top-20 owned-legendary). Best form & rank is
  one line per usage. Families with no usage show 'Collection only' + the folded forms.
- Far-apart folded members get a pointer row.
Regenerate:  python3 build_dex.py
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
FAR = 5

LEAGUES = [("little", "LC", 50), ("great", "GL", 100), ("ultra", "UL", 100), ("master", "ML", 75)]
LORDER = {k: i for i, (k, _s, _c) in enumerate(LEAGUES)}
SHORT = {k: s for k, s, _c in LEAGUES}

pool, mvpool = {}, {}
for key, _s, cut in LEAGUES:
    arr = json.load(open(os.path.join(DATA, f"rankings-{key}.json")))
    pool[key] = {e["speciesId"]: i + 1 for i, e in enumerate(arr[:cut])}
    mvpool[key] = {e["speciesId"]: " / ".join(m.replace("_", " ").title() for m in e.get("moveset", []))
                   for e in arr[:cut]}

gm = json.load(open(os.path.join(DATA, "gamemaster.json")))
poke = gm["pokemon"] if isinstance(gm, dict) else gm
by = {p["speciesId"]: p for p in poke}


def is_mega(p):
    return "mega" in (p.get("tags") or []) or "_mega" in p["speciesId"] or "primal" in p["speciesId"]


def plain(name):
    return re.sub(r"\s*\(.*?\)", "", name).strip()


# dex-forms: released, not shadow, not mega/primal
cand = [p for p in poke if p.get("dex") and p.get("released")
        and "shadow" not in (p.get("tags") or []) and "_shadow" not in p["speciesId"]
        and not is_mega(p)]

# de-dupe cosmetic costumes: same (dex, types, stats) -> keep plainest speciesId
canon = {}
for p in sorted(cand, key=lambda p: (len(p["speciesId"]), p["speciesId"])):
    bs = p["baseStats"]
    k = (p["dex"], tuple(p["types"]), bs["atk"], bs["def"], bs["hp"])
    canon.setdefault(k, p)
forms = list(canon.values())


def fkey_of(sid):
    return (by.get(sid, {}).get("family") or {}).get("id") or sid


# group into families
fams = {}
for p in forms:
    fams.setdefault(fkey_of(p["speciesId"]), []).append(p)

LOW, HIGH = "low ATK / high bulk", "high ATK"

# Raid-locked rarities: legendary / mythical / ultra beast (incl. wild-legendary). These are
# only obtainable from raids (or research) and should be excluded from the 'everything else'
# collection string regardless of whether they have a listed PvP/PvE usage.
RARE_TAGS = {"legendary", "mythical", "ultrabeast", "wildlegendary"}

# Real per-type PvE raid-attacker ranks from PGHub (data/pve_type_ranks.json via
# pve_ranks.by_dex()), attached by member dex. Replaces the old curated TOP_PVE dict
# AND the blanket 'every Mega -> PvE raids' line: a form is a PvE keeper only if it is
# a top-10 catchable (or top-20 owned-legendary) attacker of some type, with real rank.
import pve_ranks
PVE_BY_DEX = pve_ranks.by_dex()


def ranks(vid):
    return [(k, pool[k][vid]) for k, _s, _c in LEAGUES if vid in pool[k]]


rows, pointers = [], []
for key, members in fams.items():
    members = sorted(members, key=lambda p: (p["dex"], len(p["speciesId"]), p["speciesId"]))
    anchor = members[0]
    adex, aname = anchor["dex"], plain(anchor["speciesName"])

    usages = []
    for m in members:
        fid = m["speciesId"]
        for pref, vid in [("", fid), ("Shadow ", fid + "_shadow")]:
            for k, r in ranks(vid):
                usages.append({"kind": 0, "ord": LORDER[k], "rank": r, "lp": SHORT[k],
                               "best": f'{pref}{m["speciesName"]} #{r}',
                               "iv": LOW if k != "master" else HIGH, "moves": mvpool[k][vid]})
    # PvE raid-attacker lines: attach by member dex, one line per type, best rank wins.
    member_dexes = {m["dex"] for m in members}
    pve_by_type = {}
    for d in member_dexes:
        for u in PVE_BY_DEX.get(d, []):
            cur = pve_by_type.get(u["type"])
            if cur is None or u["rank"] < cur["rank"]:
                pve_by_type[u["type"]] = u
    for u in sorted(pve_by_type.values(), key=lambda u: u["rank"]):
        # catchable keepers show a 2nd rank (position within the non-locked pool) and a 3rd rank
        # (position within the non-locked AND non-shadow pool) — e.g. "Bug #7, #6, #5".
        tail = ""
        if u.get("crank"):
            tail = f', #{u["crank"]}'
            if u.get("trank"):
                tail += f', #{u["trank"]}'
        usages.append({"kind": 1, "ord": 5, "rank": u["rank"], "lp": "PvE",
                       "best": f'{u["form"]} — {u["type"]} #{u["rank"]}{tail}',
                       "iv": HIGH, "moves": "—"})
    usages.sort(key=lambda u: (u["kind"], u["ord"], u["rank"]))

    chain = " · ".join(f'{m["speciesName"]} <span class=dex>#{m["dex"]}</span>' for m in members)
    rare = any(RARE_TAGS & set(m.get("tags") or []) for m in members)
    rows.append({"dex": adex, "name": aname, "sid": anchor["speciesId"], "usages": usages,
                 "chain": chain, "total": len(usages), "rare": rare})
    for m in members:
        if m is not anchor and m["dex"] - adex > FAR:
            pointers.append((m["dex"], plain(m["speciesName"]), adex, aname))

rows.sort(key=lambda r: r["dex"])
items = [("fam", r["dex"], r) for r in rows] + [("ptr", d, (d, n, a, an)) for (d, n, a, an) in pointers]
items.sort(key=lambda x: (x[1], 0 if x[0] == "fam" else 1))

# ---- CSV (one row per family) ----
with open(os.path.join(HERE, "dex.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Dex", "Spawn", "League / Purpose", "Best form & rank", "Folded forms", "Total"])
    for r in rows:
        lp = " ".join(sorted({u["lp"] for u in r["usages"]})) or "Collection only"
        best = " | ".join(f'{u["lp"]}: {re.sub("<.*?>","",u["best"])}' for u in r["usages"])
        forms = re.sub("<.*?>", "", r["chain"])
        w.writerow([r["dex"], r["name"], lp, best, forms, r["total"] or ""])
print(f"wrote dex.csv  (families: {len(rows)}, pointers: {len(pointers)})")

# ---- HTML ----
ART = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"
# Rows anchored on a regional form fold into their OWN family (separate family id), so the
# base national-dex art is wrong. Map those anchors to the correct PokeAPI form-id sprite.
SPRITE_OVERRIDE = {
    "farfetchd_galarian": 10166, "tauros_combat": 10250, "tauros_blaze": 10251,
    "tauros_aqua": 10252, "articuno_galarian": 10169, "zapdos_galarian": 10170,
    "moltres_galarian": 10171, "wooper_paldean": 10253, "qwilfish_hisuian": 10234,
    "corsola_galarian": 10173, "stunfisk_galarian": 10180,
}
h = ["""<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Complete Pokédex — folded by family</title>
<style>
:root{color-scheme:light}
body{font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:24px;background:#fff;color:#1b2733}
h1{font-size:24px;margin:0 0 4px} .sub{color:#5b6b7a;margin:0 0 16px;max-width:82ch}
table{border-collapse:collapse;width:100%}
td,th{padding:6px 9px;border-bottom:1px solid #edf1f5;vertical-align:middle;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#6b7b8a}
img{width:42px;height:42px;object-fit:contain;vertical-align:middle}
.mon{font-weight:600;white-space:nowrap} .dex{color:#9aa7b4;font-size:12px;font-variant-numeric:tabular-nums}
.note{color:#6b7b8a;font-size:13px} .keep{text-align:center} .tot{text-align:center;font-weight:700;color:#b26b00}
.coll{color:#9aa7b4}
.ptr td{background:#fafbfc;color:#9aa7b4;font-size:12px}
.lg{display:inline-block;padding:1px 6px;border-radius:9px;font-size:11px;font-weight:700}
.LC{background:#efe7f7;color:#6b3fa0} .GL{background:#e3f6ea;color:#14713a}
.UL{background:#fdeee2;color:#9a4a12} .ML{background:#e3eefb;color:#1e5fa8} .Mega{background:#fce4ec;color:#b0146b} .PvE{background:#ffedd5;color:#9a3412}
.ss{margin-top:12px} .ss>b{font-size:13px}
.codewrap{position:relative;margin:4px 0 14px}
.codewrap pre{margin:0;padding:10px 12px;padding-right:44px;white-space:pre-wrap;word-break:break-all;background:#f5f8fb;border:1px solid #e2e8ee;border-radius:8px;font-size:12px}
.copy{position:absolute;top:6px;right:6px;display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;padding:0;border:1px solid #cbd5e1;border-radius:6px;background:#fff;color:#475569;cursor:pointer}
.copy:hover{background:#eef2f6;color:#0f172a} .copy svg{width:15px;height:15px}
.copy.ok{background:#e3f6ea;border-color:#86efac;color:#14713a}
.copy.ok svg{display:none} .copy.ok::after{content:'✓';font-size:16px;font-weight:700;line-height:1}
.views{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:18px 0 4px;padding:8px 0;background:#fff;border-bottom:1px solid #edf1f5}
.view{padding:5px 11px;border:1px solid #cbd5e1;border-radius:16px;background:#fff;color:#475569;font-size:13px;font-weight:600;cursor:pointer}
.view:hover{background:#eef2f6;color:#0f172a}
.view.on{background:#1e5fa8;border-color:#1e5fa8;color:#fff}
.viewcount{margin-left:auto;color:#6b7b8a;font-size:12px;font-variant-numeric:tabular-nums}
tbody.fam.hide{display:none}
</style>
<h1>Complete Pokédex — folded by family</h1>
<p style="margin:0 0 10px"><a href="index.html">🏠 Home</a> &nbsp;·&nbsp; <a href="pokedex.html">→ ranked-only by dex #</a> &nbsp;·&nbsp; <a href="rankings.html">→ by League</a> &nbsp;·&nbsp; <a href="event.html">→ Ultra Unlock event</a> &nbsp;·&nbsp; <a href="max.html">→ Max Battles</a></p>
<p class=sub>Every released species in Pokémon GO (pvpoke gamemaster), <b>one row per family</b> at its first dex #.
Cosmetic costumes are de-duplicated. <b>League / Purpose</b> lists every usage — each PvP league a form ranks in
(LC top 50 / GL·UL top 100 / ML top 75), one line each. No usage → <span class=coll>Collection only</span> with the folded forms.
A <span class="lg PvE">PvE</span> line flags a family as a top raid attacker of a type, with its real
<a href="https://db.pokemongohub.net/pokemon-list/best-per-type/dragon">PGHub</a> rank + best form — top-6 catchable
(or top-20 for a legendary/mythical/UB you own) per type. Catchable lines show up to three numbers:
1st = rank <b>overall</b>, 2nd = rank <b>within the non-locked pool</b> (legendary/mythical/UB excluded),
3rd = rank <b>within the non-locked &amp; non-shadow pool</b> (shadow can't be traded, so this is the best
you can catch a tradeable high-IV of). The <b>top-6 by that 3rd rank</b> are kept
(e.g. <code>Bug #7, #6, #5</code> = Mega Beedrill, 7th overall, 6th non-locked, 5th non-locked-non-shadow).
A Mega only earns a PvE line if that Mega is actually a top attacker (no more blanket "has-a-Mega" flag).</p>
"""]
def uniq(seq):  # order-preserving de-dup (regional variants / multi-form legendaries share a name)
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x); out.append(x)
    return out


COPYBTN = '<button class=copy title="Copy" aria-label="Copy"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>'
capped_fams = uniq(r["name"] for r in rows if any(u["lp"] in ("LC", "GL", "UL") for u in r["usages"]))
cap_join = ",".join("+" + n for n in capped_fams)
neg_join = "&".join("!+" + n for n in capped_fams)
h.append("<h2>Quick search strings</h2>")
h.append(f"<p class=note>{len(capped_fams)} families have ≥ 1 capped-league (LC/GL/UL) usage. "
         "<b>String 1</b> = those at low-ATK / high-bulk (then run Poke Genie). "
         "<b>String 2</b> = <b>everything else</b> — the capped families negated with <code>!+</code> joined by "
         "<code>&amp;</code> (AND) so all are excluded — at high IV. <code>+name</code> = whole evolution family.</p>")
h.append(f"<div class=ss><b>Capped-PvP candidates — low ATK / high bulk</b>"
         f"<div class=codewrap>{COPYBTN}<pre>{cap_join}&0-1attack&3-4defense&3-4hp</pre></div></div>")
h.append(f"<div class=ss><b>Everything else — high IV / high ATK</b> (negated capped list)"
         f"<div class=codewrap>{COPYBTN}<pre>{neg_join}&!3*</pre></div></div>")
highiv_fams = uniq(r["name"] for r in rows if any(u["lp"] in ("ML", "PvE") for u in r["usages"]))
hi_join = ",".join("+" + n for n in highiv_fams)
hineg_join = "&".join("!+" + n for n in highiv_fams)
h.append(f"<p class=note>{len(highiv_fams)} families have a <b>Raid (PvE) / Master-league</b> usage — all want "
         "<b>high ATK / hundo</b>. Next = those; last = everything else (them negated).</p>")
h.append(f"<div class=ss><b>Raid (PvE) / Master — high IV / high ATK</b>"
         f"<div class=codewrap>{COPYBTN}<pre>{hi_join}&3*,4*</pre></div></div>")
h.append(f"<div class=ss><b>Everything else</b> (negated Raid/Master list)"
         f"<div class=codewrap>{COPYBTN}<pre>{hineg_join}&!3*</pre></div></div>")
# Raid/Master list with the capped-PvP families removed (set difference).
cap_set = set(capped_fams)
raid_minus_capped = [n for n in highiv_fams if n not in cap_set]
rmc_join = ",".join("+" + n for n in raid_minus_capped)
h.append(f"<div class=ss><b>Raid (PvE) / Master minus Capped-PvP candidates</b> "
         "(Raid/Master list with capped-PvP families removed)"
         f"<div class=codewrap>{COPYBTN}<pre>{rmc_join}</pre></div></div>")
# Combined: negate the capped-PvP list AND negate the Raid/Master list AND negate every
# raid-locked rarity (legendary / mythical / ultra beast), de-duplicated (a family appearing
# in more than one of those groups is negated once) so the string keeps only the pure,
# freely-catchable collection families.
rare_fams = uniq(r["name"] for r in rows if r["rare"])
combined_fams = uniq(list(capped_fams) + list(highiv_fams) + list(rare_fams))
combined_neg = "&".join("!+" + n for n in combined_fams)
h.append(f"<p class=note>{len(combined_fams)} families are either a keeper "
         "(capped-PvP <b>or</b> Raid/Master) <b>or</b> a raid-locked rarity "
         f"(legendary / mythical / ultra beast — {len(rare_fams)} families), de-duplicated. "
         "Negating all of them leaves only the freely-catchable, pure-collection families.</p>")
h.append(f"<div class=ss><b>Neither Capped-PvP nor Raid/Master, no legendary/mythical/UB</b> "
         "(all three lists negated, de-duplicated)"
         f"<div class=codewrap>{COPYBTN}<pre>{combined_neg}&!3*&!4*</pre></div></div>")
h.append(
    '<div class=views role=tablist aria-label="Dex views">'
    '<button class="view on" data-view=all>All families</button>'
    '<button class=view data-view=capped>Capped-PvP</button>'
    '<button class=view data-view=raid>Raid / Master</button>'
    '<button class=view data-view=raidonly>Raid / Master − Capped</button>'
    '<button class=view data-view=rare>Legendary / Mythical / UB</button>'
    '<button class=view data-view=collection>Collection only</button>'
    '<span class=viewcount id=viewcount></span></div>'
    '<p class=note id=viewhint>Showing every family. Each view below is a strict subset '
    'of this same list — the rows are identical, only filtered.</p>')
h.append('<table><thead><tr><th></th><th>Spawn</th><th>League / Purpose</th><th>Best form &amp; rank</th>'
         '<th>IV target</th><th>Moveset</th><th>Keep</th><th>Total</th></tr></thead>')
def fam_cats(r):
    """Space-separated category tokens for a family — drives the client-side view tabs.
    Mirrors the search-string groupings exactly so each view is a strict subset."""
    capped = any(u["lp"] in ("LC", "GL", "UL") for u in r["usages"])
    raid = any(u["lp"] in ("ML", "PvE") for u in r["usages"])
    rare = bool(r["rare"])
    cats = []
    if capped:
        cats.append("capped")
    if raid:
        cats.append("raid")
    if raid and not capped:
        cats.append("raidonly")
    if rare:
        cats.append("rare")
    if not capped and not raid and not rare:
        cats.append("collection")
    return " ".join(cats)


for kind, _d, payload in items:
    if kind == "ptr":
        d, n, a, an = payload
        h.append(f'<tbody class=fam data-cat="ptr"><tr class=ptr><td></td>'
                 f'<td>{n} <span class=dex>#{d}</span></td>'
                 f'<td colspan=6>→ folded into #{a} ({an} family)</td></tr></tbody>')
        continue
    r = payload
    h.append(f'<tbody class=fam data-cat="{fam_cats(r)}">')
    img = f'<img loading=lazy src="{ART.format(SPRITE_OVERRIDE.get(r["sid"], r["dex"]))}" alt="">'
    lines = [dict(u, keep="1") for u in r["usages"]]
    lines.append({"lp": "Collection only", "best": r["chain"], "iv": "—", "moves": "—", "keep": "", "coll": True})
    n = len(lines)
    totval = r["total"] or ""
    for j, u in enumerate(lines):
        if j == 0:
            c0 = (f'<td rowspan={n} style="text-align:center">{img}</td>'
                  f'<td rowspan={n} class=mon>{r["name"]}<br><span class=dex>#{r["dex"]}</span></td>')
            ct = f'<td rowspan={n} class=tot>{totval}</td>'
        else:
            c0 = ct = ""
        if u.get("coll"):
            lp_html, best_html = '<span class=coll>Collection only</span>', f'<span class=note>{u["best"]}</span>'
        else:
            lp_html, best_html = f'<span class="lg {u["lp"]}">{u["lp"]}</span>', f'<b>{u["best"]}</b>'
        h.append(f'<tr>{c0}<td>{lp_html}</td><td class=rank>{best_html}</td>'
                 f'<td class=note>{u["iv"]}</td><td class=note>{u["moves"]}</td>'
                 f'<td class=keep>{u["keep"]}</td>{ct}</tr>')
    h.append("</tbody>")
h.append("</table>")
h.append("<script>document.querySelectorAll('.copy').forEach(function(b){b.addEventListener('click',function(){var p=b.closest('.ss').querySelector('pre');navigator.clipboard.writeText(p.innerText).then(function(){b.classList.add('ok');setTimeout(function(){b.classList.remove('ok');},1500);});});});</script>")
h.append("""<script>
(function(){
  var fams=[].slice.call(document.querySelectorAll('tbody.fam'));
  var btns=[].slice.call(document.querySelectorAll('.view'));
  var count=document.getElementById('viewcount');
  var hints={all:'Showing every family. Each view below is a strict subset of this same list — the rows are identical, only filtered.',
    capped:'Capped-PvP candidates — families with a LC/GL/UL usage (breed for low ATK / high bulk).',
    raid:'Raid (PvE) / Master-league families — want high ATK / hundo.',
    raidonly:'Raid/Master families that are NOT also Capped-PvP candidates.',
    rare:'Legendary / Mythical / Ultra Beast families (raid-locked rarities).',
    collection:'Neither Capped-PvP nor Raid/Master, and not a legendary/mythical/UB — the freely-catchable collection.'};
  var hint=document.getElementById('viewhint');
  function apply(v){
    var shown=0;
    fams.forEach(function(t){
      var cats=(t.getAttribute('data-cat')||'').split(' ');
      // 'All' shows everything (incl. pointer rows); any filtered view matches by token
      // and drops pointer rows, whose fold target may be hidden.
      var vis=(v==='all')?true:(cats.indexOf(v)>=0);
      t.classList.toggle('hide',!vis);
      if(vis&&cats.indexOf('ptr')<0)shown++;
    });
    count.textContent=shown+' families';
    if(hint)hint.textContent=hints[v]||'';
    if(history.replaceState)history.replaceState(null,'',v==='all'?location.pathname:('#'+v));
  }
  btns.forEach(function(b){b.addEventListener('click',function(){
    btns.forEach(function(x){x.classList.remove('on');});
    b.classList.add('on');
    apply(b.getAttribute('data-view'));
  });});
  var start=(location.hash||'').replace('#','');
  var match=btns.filter(function(b){return b.getAttribute('data-view')===start;})[0];
  if(match){btns.forEach(function(x){x.classList.remove('on');});match.classList.add('on');apply(start);}
  else apply('all');
})();
</script>""")
h.append("</html>")
open(os.path.join(HERE, "dex.html"), "w").write("\n".join(h))
print("wrote dex.html")
