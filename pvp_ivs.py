#!/usr/bin/env python3
"""Rank-1 PvP IV spreads, computed locally from base stats.

The ideal ('rank 1') IV combination for a species in a capped PvP league is a
deterministic function of its base stats, the league CP cap, and the level cap
— it maximizes stat product (atk·def·hp) among all builds that stay under the
cap. It is NOT user-specific data: Poke Genie shows these same numbers because
it runs the same math, so there's nothing to fetch — we compute it from the
base stats already in data/gamemaster.json.

Notable consequence: for an *undersized* species (one whose max CP falls short
of the cap even at the level cap) the CP penalty never bites, so the rank-1
spread is simply 15/15/15 — the opposite of the usual "low ATK / high bulk".
That's why Altaria wants 0/14/15 in Great but 15/15/15 in Ultra.

Shadow forms use the shadow atk/def multipliers, which shift both CP and the
stat-product ranking, so they're computed separately.
"""

# Standard Pokémon GO CP multiplier per level (half-steps), levels 1..51.
CPM = {
    1: 0.094, 1.5: 0.1351374318, 2: 0.16639787, 2.5: 0.192650919, 3: 0.21573247,
    3.5: 0.2365726613, 4: 0.25572005, 4.5: 0.2749761605, 5: 0.29024988,
    5.5: 0.3049159566, 6: 0.3210876, 6.5: 0.3364826075, 7: 0.34921268,
    7.5: 0.3641380786, 8: 0.3775215, 8.5: 0.3910873516, 9: 0.4020575,
    9.5: 0.4132480074, 10: 0.4225871, 10.5: 0.4329264091, 11: 0.44310755,
    11.5: 0.4530599482, 12: 0.46279839, 12.5: 0.472336093, 13: 0.48168495,
    13.5: 0.4908558003, 14: 0.49985844, 14.5: 0.508701765, 15: 0.51739395,
    15.5: 0.5259425113, 16: 0.5343543, 16.5: 0.5426697346, 17: 0.5507927,
    17.5: 0.5588305862, 18: 0.5667934, 18.5: 0.5746500416, 19: 0.5824234,
    19.5: 0.5901075648, 20: 0.5974, 20.5: 0.6048236651, 21: 0.6121573,
    21.5: 0.6194041216, 22: 0.6265671, 22.5: 0.6336491815, 23: 0.6406530,
    23.5: 0.6475809666, 24: 0.6544356, 24.5: 0.6612192524, 25: 0.667934,
    25.5: 0.6745818983, 26: 0.6811649, 26.5: 0.6876849038, 27: 0.694144,
    27.5: 0.7005337693, 28: 0.7068842, 28.5: 0.7131740926, 29: 0.7194056,
    29.5: 0.7255756136, 30: 0.7317, 30.5: 0.7347410385, 31: 0.7377695,
    31.5: 0.7407855938, 32: 0.74378943, 32.5: 0.7467812109, 33: 0.74976104,
    33.5: 0.7527290867, 34: 0.7556855, 34.5: 0.7586303683, 35: 0.76156384,
    35.5: 0.7644860647, 36: 0.76739717, 36.5: 0.7702972656, 37: 0.7731865,
    37.5: 0.7760649616, 38: 0.77893275, 38.5: 0.7817900548, 39: 0.7846370,
    39.5: 0.7874736075, 40: 0.7903, 40.5: 0.792803968, 41: 0.7953, 41.5: 0.7978,
    42: 0.8003, 42.5: 0.8028, 43: 0.8053, 43.5: 0.8078, 44: 0.8103, 44.5: 0.8128,
    45: 0.8153, 45.5: 0.8178, 46: 0.8203, 46.5: 0.8228, 47: 0.8253, 47.5: 0.8278,
    48: 0.8303, 48.5: 0.8328, 49: 0.8353, 49.5: 0.8378, 50: 0.8403, 50.5: 0.8428,
    51: 0.8453,
}
LEVELS = sorted(CPM)

SHADOW_ATK_MULT = 1.2
SHADOW_DEF_MULT = 5.0 / 6.0

_cache = {}


def _cp(a_stat, d_stat, h_stat):
    return max(10, int((a_stat * (d_stat ** 0.5) * (h_stat ** 0.5)) / 10))


def rank1_iv(base_stats, cap, max_level=51, shadow=False):
    """Return (atk_iv, def_iv, hp_iv, level, cp) of the max-stat-product build
    that stays at or under `cap` CP, searching levels up to `max_level`.
    `base_stats` is {"atk","def","hp"}. Returns None if no build fits (can't
    happen for real caps, but guards against bad input)."""
    ba, bd, bh = base_stats["atk"], base_stats["def"], base_stats["hp"]
    amul = SHADOW_ATK_MULT if shadow else 1.0
    dmul = SHADOW_DEF_MULT if shadow else 1.0
    key = (ba, bd, bh, cap, max_level, shadow)
    if key in _cache:
        return _cache[key]
    levels = [lv for lv in LEVELS if lv <= max_level]
    best_sp, best = -1.0, None
    for ia in range(16):
        for idf in range(16):
            for ih in range(16):
                # Highest level whose CP is still within the cap (CP rises with
                # level, so scan upward and keep the last that fits).
                top = None
                for lv in levels:
                    cpm = CPM[lv]
                    a = (ba + ia) * amul * cpm
                    d = (bd + idf) * dmul * cpm
                    h = (bh + ih) * cpm
                    if _cp(a, d, h) <= cap:
                        top = lv
                    else:
                        break
                if top is None:
                    continue
                cpm = CPM[top]
                a = (ba + ia) * amul * cpm
                d = (bd + idf) * dmul * cpm
                h = int((bh + ih) * cpm)
                sp = a * d * h
                if sp > best_sp:
                    best_sp = sp
                    best = (ia, idf, ih, top, _cp(a, d, h))
    _cache[key] = best
    return best


def _fmt_lvl(lv):
    return str(int(lv)) if lv == int(lv) else str(lv)


def iv_target(base_stats, cap, shadow=False):
    """Human-readable rank-1 target for a league, showing both the level-50 and
    level-51 (best-buddy) spreads. Collapses to one when they match."""
    r50 = rank1_iv(base_stats, cap, max_level=50, shadow=shadow)
    r51 = rank1_iv(base_stats, cap, max_level=51, shadow=shadow)
    if not r50 or not r51:
        return "—"
    s50 = f"{r50[0]}/{r50[1]}/{r50[2]}"
    s51 = f"{r51[0]}/{r51[1]}/{r51[2]}"
    if s50 == s51:
        return s50
    return f"L50 {s50} · L51 {s51}"
