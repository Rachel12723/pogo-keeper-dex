# Data changelog

What each `refresh.py` run changed in the pvpoke sources, newest first.

## 2026-10-01

### Gamemaster (moves / species)
- New moves: BRAVE_BIRD_PLUS, DARK_PULSE_PLUS, FELL_STINGER_PLUS
- Move AIR_CUTTER: power 45->60; energy 35->40
- Move BITE: power 4->2; energyGain 2->4
- Move BLAZE_KICK: energy 40->35
- Move BODY_SLAM: power 55->65; energy 35->40
- Move BRINE: power 60->100; energy 50->60
- Move BUBBLE_BEAM: power 25->50; energy 40->50
- Move BULLDOZE: power 45->80; energy 45->55
- Move CHARGE_BEAM: power 5->6
- Move DARK_PULSE: energy 50->45
- Move DOUBLE_IRON_BASH: power 55->70
- Move DRAINING_KISS: power 60->80; buffs None->[0, 1]
- Move HIGH_HORSEPOWER: energy 60->55
- Move INFESTATION: power 6->10
- Move IRON_HEAD: power 70->85
- Move LOW_KICK: power 5->6
- Move LUNGE: power 60->70
- Move MAGNET_BOMB: energy 45->40
- Move MIRROR_COAT: power 60->75; energy 55->45
- Move MOONBLAST: power 110->90; energy 60->50
- Move POISON_FANG: power 45->50
- Move PSYCHO_BOOST: power 70->85
- Move RAGE_FIST: power 50->55; energy 35->40
- Move SAND_TOMB: power 40->55; energy 40->45
- Move SCRATCH: power 4->3; energyGain 2->4
- Move SHADOW_BALL: power 100->90
- Move SHADOW_FORCE: energy 90->65
- Move TAKE_DOWN: power 5->14; energyGain 8->9
- New species/forms: staraptor_mega
- Species arbok: charged +['BRUTAL_SWING', 'WRAP'] -[]
- Species arbok_shadow: charged +['BRUTAL_SWING', 'WRAP'] -[]
- Species raichu: charged +['VOLT_TACKLE'] -[]
- Species raichu_mega_x: charged +['VOLT_TACKLE'] -[]
- Species raichu_mega_y: charged +['VOLT_TACKLE'] -[]
- Species raichu_alolan: charged +['VOLT_TACKLE'] -[]
- Species nidoking: charged +['AVALANCHE'] -[]
- Species nidoking_shadow: charged +['AVALANCHE'] -[]
- Species victreebel: fast +['SUCKER_PUNCH'] -[]
- Species victreebel_mega: fast +['SUCKER_PUNCH'] -[]
- Species victreebel_shadow: fast +['SUCKER_PUNCH'] -[]
- Species muk_alolan: charged +['BRUTAL_SWING', 'ICE_PUNCH'] -[]
- Species muk_alolan_shadow: charged +['BRUTAL_SWING', 'ICE_PUNCH'] -[]
- Species aerodactyl: charged +['BRUTAL_SWING'] -[]
- Species aerodactyl_mega: charged +['BRUTAL_SWING'] -[]
- Species aerodactyl_shadow: charged +['BRUTAL_SWING'] -[]
- Species snorlax: fast +['PSYWAVE'] -[]
- Species snorlax_shadow: fast +['PSYWAVE'] -[]
- Species ariados: charged +['FOUL_PLAY'] -[]
- Species crobat: fast +['GUST'] -[]
- Species crobat_shadow: fast +['GUST'] -[]
- Species skarmory: charged +['DRILL_RUN'] -[]
- Species skarmory_shadow: charged +['DRILL_RUN'] -[]
- Species skarmory_mega: charged +['DRILL_RUN'] -[]
- Species houndoom: fast +['INCINERATE'] -[]; charged +['TRAILBLAZE'] -[]
- Species houndoom_mega: fast +['INCINERATE'] -[]; charged +['TRAILBLAZE'] -[]
- Species houndoom_shadow: fast +['INCINERATE'] -[]; charged +['TRAILBLAZE'] -[]
- Species miltank: charged +['HIGH_HORSEPOWER'] -[]
- Species lugia: charged +['EARTH_POWER'] -[]
- Species lugia_shadow: charged +['EARTH_POWER'] -[]
- Species aggron: charged +['BRICK_BREAK'] -[]
- Species aggron_mega: charged +['BRICK_BREAK'] -[]
- Species aggron_shadow: charged +['BRICK_BREAK'] -[]
- Species volbeat: fast +['INFESTATION'] -[]; charged +['LUNGE'] -[]
- Species illumise: fast +['INFESTATION'] -[]; charged +['SHADOW_BALL'] -[]
- Species deoxys_defense: fast +['LOW_KICK'] -[]
- Species mismagius: charged +['MYSTICAL_FIRE'] -[]
- Species mismagius_shadow: charged +['MYSTICAL_FIRE'] -[]
- Species gallade: charged +['SACRED_SWORD'] -[]
- Species gallade_mega: charged +['SACRED_SWORD'] -[]
- Species gallade_shadow: charged +['SACRED_SWORD'] -[]
- Species darkrai: fast +['SUCKER_PUNCH'] -[]; charged +['FOUL_PLAY'] -[]
- Species darkrai_shadow: fast +['SUCKER_PUNCH'] -[]; charged +['FOUL_PLAY'] -[]
- Species audino: fast +['CHARGE_BEAM'] -[]
- Species audino_mega: fast +['CHARGE_BEAM'] -[]
- Species cofagrigus: charged +['ENERGY_BALL'] -[]
- Species cofagrigus_shadow: charged +['ENERGY_BALL'] -[]
- Species zoroark_hisuian: charged +['SWIFT'] -[]
- Species chandelure: fast +['ASTONISH'] -[]
- Species chandelure_shadow: fast +['ASTONISH'] -[]
- Species greninja: charged +['BRUTAL_SWING'] -[]
- Species greninja_mega: charged +['BRUTAL_SWING'] -[]
- Species greninja_shadow: charged +['BRUTAL_SWING'] -[]
- Species zeraora: charged +['DYNAMIC_PUNCH'] -[]
- Species toxtricity: charged +['SWIFT'] -[]
- Species grimmsnarl: charged +['DRAINING_KISS'] -[]
- Species ursaluna: fast +['SCRATCH'] -[]
- Species ursaluna_shadow: fast +['SCRATCH'] -[]
- Species maschiff: charged +['PSYCHIC_FANGS'] -['PAYBACK']
- Species mabosstiff: charged +['PSYCHIC_FANGS'] -['PAYBACK']
- Species grafaiai: fast +['SCRATCH'] -[]; charged +['FOUL_PLAY'] -[]
- Species bombirdier: charged +['DRILL_RUN'] -[]
- Species flamigo: fast +['PECK'] -[]
- Species kingambit: fast +['LOW_KICK'] -[]

### Great League (CP 1500)
- Top 10: lickilicky, tinkaton, altaria, empoleon, mimikyu, altaria_shadow, empoleon_shadow, quagsire_shadow, quagsire, jellicent  ->  melmetal, altaria, ninetales_shadow, cramorant, tinkaton, mimikyu, corviknight, corsola_galarian, altaria_shadow, corviknight_shadow
- Top 30 in: melmetal, florges, thievul, araquanid, sableye_shadow, marowak, stunfisk, vigoroth, mantine, snorlax, umbreon, araquanid_shadow; out: lickilicky, forretress, forretress_shadow, jumpluff, feraligatr_shadow, kingdra, azumarill, guzzlord, furret, kingdra_shadow, lapras, dragonair_shadow
- Pool added: maschiff, mabosstiff; removed: cradily_b
- Biggest top-50 movers: rillaboom #833->#35, deoxys_defense #540->#33, vigoroth_shadow #457->#37, vigoroth #388->#21, snorlax #292->#27, snorlax_shadow #283->#40, electrode_hisuian #191->#34, greedent #40->#184

### Ultra League (CP 2500)
- Top 10: mimikyu, lickilicky, corviknight, tinkaton, corviknight_shadow, florges, virizion, empoleon_shadow, empoleon, moltres_galarian  ->  tinkaton, corviknight, snorlax_shadow, corviknight_shadow, melmetal, virizion, zygarde_complete, empoleon, empoleon_shadow, mimikyu
- Top 30 in: snorlax_shadow, melmetal, snorlax, feraligatr, giratina_altered, guzzlord, skeledirge, rillaboom, dondozo; out: lickilicky, annihilape, annihilape_shadow, primeape, forretress, forretress_shadow, kingdra, malamar, malamar_shadow
- Pool added: mabosstiff; removed: -
- Biggest top-50 movers: rillaboom #680->#21, muk_alolan #404->#36, snorlax_shadow #306->#3, deoxys_defense #345->#42, snorlax #258->#11, primeape #14->#258, lickilicky #2->#100, skeledirge #99->#20

### Master League (CP 10000)
- Top 10: zacian_crowned_sword, palkia_origin, metagross, kyurem_white, lunala, xerneas, dialga_origin, reshiram, zamazenta_crowned_shield, kyurem_black  ->  palkia_origin, zacian_crowned_sword, zygarde_complete, metagross, kyurem_white, xerneas, kyogre, dialga_origin, reshiram, ursaluna
- Top 30 in: ursaluna, ursaluna_shadow, necrozma_dusk_mane, groudon, melmetal, keldeo_resolute; out: yveltal, meloetta_aria, palkia, latios, latios_shadow, kyogre_shadow
- Pool added: mabosstiff; removed: -
- Biggest top-50 movers: rillaboom #288->#34, ursaluna #124->#10, ursaluna_shadow #120->#17, annihilape_shadow #47->#91, giratina_altered_shadow #75->#38, giratina_altered #87->#50, zygarde_complete #25->#3, latios #28->#49
