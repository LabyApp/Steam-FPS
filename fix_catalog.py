import json
import re

with open('steam_catalog_cache.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

# Список РЕАЛЬНЫХ полноценных VR игр
GENUINE_VR_EXACT = {
    "half-life: alyx", "beat saber", "boneworks", "bonelab", "blade and sorcery",
    "pavlov", "pavlov vr", "superhot vr", "the walking dead: saints & sinners",
    "into the radius vr", "into the radius", "vrchat", "rec room", "pistol whip",
    "gorn", "arizona sunshine", "arizona sunshine 2", "until you fall", "moss",
    "moss: book ii", "contractors", "contractors vr", "vtoline vr", "vtol vr",
    "the room vr: a dark matter", "i expect you to die", "i expect you to die 2",
    "eleven table tennis", "walkabout mini golf vr", "kayak vr: mirage",
    "synthrider", "synth riders", "creed: rise to glory", "budget cuts",
    "budget cuts 2", "duck season", "job simulator", "vacation simulator",
    "space pirate trainer", "fnaf vr: help wanted", "five nights at freddy's: help wanted",
    "five nights at freddy's: help wanted 2", "phasmophobia"
}

# Известные базовые требования игр (min_gpu_score, min_cpu_score, min_ram, min_vram, genre)
KNOWN_REQUIREMENTS = {
    # Тяжелые современные AAA
    "cyberpunk 2077": (45.0, 48.0, 12, 6, "Action / Open World"),
    "alan wake 2": (60.0, 55.0, 16, 6, "Survival Horror"),
    "starfield": (55.0, 58.0, 16, 8, "RPG / Sci-Fi"),
    "black myth: wukong": (50.0, 52.0, 16, 6, "Action RPG"),
    "hogwarts legacy": (45.0, 48.0, 16, 6, "Open World / Magic"),
    "the last of us part i": (52.0, 55.0, 16, 6, "Action / Story"),
    "red dead redemption 2": (42.0, 44.0, 12, 4, "Open World / Western"),
    "forza horizon 5": (38.0, 36.0, 8, 4, "Racing / Open World"),
    "forza horizon 4": (32.0, 30.0, 8, 4, "Racing / Open World"),
    "forza motorsport": (52.0, 50.0, 16, 6, "Racing Sim"),
    "baldurs gate 3": (42.0, 46.0, 16, 6, "CRPG / Fantasy"),
    "baldur's gate 3": (42.0, 46.0, 16, 6, "CRPG / Fantasy"),
    "elden ring": (40.0, 42.0, 12, 4, "Action RPG / Souls"),
    "dragons dogma 2": (58.0, 65.0, 16, 6, "Action RPG"),
    "escape from tarkov": (48.0, 58.0, 16, 6, "Tactical FPS / Hardcore"),
    "rust": (40.0, 52.0, 16, 6, "Survival / Multiplayer"),
    "ark: survival ascended": (60.0, 58.0, 16, 8, "Survival / Dinosaurs"),
    "helldivers 2": (46.0, 48.0, 16, 6, "Co-op Shooter"),
    "dying light 2": (42.0, 42.0, 12, 4, "Action / Zombie"),
    "god of war": (42.0, 40.0, 12, 4, "Action / Adventure"),
    "marvel's spider-man remastered": (40.0, 42.0, 12, 4, "Action / Open World"),
    "gta v": (24.0, 24.0, 8, 2, "Action / Open World"),
    "grand theft auto v": (24.0, 24.0, 8, 2, "Action / Open World"),
    "the witcher 3: wild hunt": (28.0, 28.0, 8, 3, "RPG / Open World"),

    # Популярные соревновательные (легкие и средние)
    "counter-strike 2": (22.0, 26.0, 8, 2, "Tactical FPS"),
    "counter-strike: global offensive": (14.0, 18.0, 4, 1, "Tactical FPS"),
    "dota 2": (14.0, 16.0, 4, 1, "MOBA"),
    "league of legends": (10.0, 12.0, 4, 1, "MOBA"),
    "valorant": (12.0, 15.0, 4, 1, "Tactical FPS"),
    "apex legends": (25.0, 28.0, 8, 3, "Battle Royale"),
    "pubg: battlegrounds": (27.0, 31.0, 8, 3, "Battle Royale"),
    "pubg": (27.0, 31.0, 8, 3, "Battle Royale"),
    "rainbow six siege": (20.0, 22.0, 8, 2, "Tactical Shooter"),
    "team fortress 2": (12.0, 14.0, 4, 1, "Hero Shooter"),
    "war thunder": (24.0, 24.0, 8, 2, "Vehicular Combat"),
    "overwatch 2": (25.0, 26.0, 8, 2, "Hero Shooter"),
    "rocket league": (18.0, 18.0, 4, 1, "Sports / Cars"),
    "left 4 dead 2": (12.0, 14.0, 4, 1, "Co-op Shooter"),
    "payday 2": (18.0, 20.0, 4, 1, "Co-op Heist"),

    # Песочницы и Инди
    "minecraft": (15.0, 22.0, 6, 2, "Sandbox / Survival"),
    "terraria": (8.0, 10.0, 4, 1, "2D Sandbox"),
    "stardew valley": (6.0, 8.0, 2, 1, "Farming Sim"),
    "hollow knight": (10.0, 12.0, 4, 1, "Metroidvania"),
    "hades": (14.0, 14.0, 4, 1, "Rogue-like / Action"),
    "hades ii": (18.0, 18.0, 8, 2, "Rogue-like / Action"),
    "lethal company": (16.0, 18.0, 4, 1, "Co-op Horror"),
    "palworld": (38.0, 40.0, 16, 4, "Survival / Crafting"),
    "subnautica": (28.0, 30.0, 8, 2, "Survival / Ocean"),
    "valheim": (32.0, 36.0, 8, 3, "Survival / Viking"),
    "the forest": (26.0, 26.0, 8, 2, "Survival / Horror"),
    "sons of the forest": (44.0, 46.0, 16, 6, "Survival / Horror"),
    "sea of thieves": (30.0, 30.0, 8, 3, "Pirate Adventure"),

    # Настоящие VR игры
    "half-life: alyx": (52.0, 50.0, 12, 6, "VR Story / Shooter"),
    "beat saber": (24.0, 24.0, 6, 2, "VR Rhythm"),
    "boneworks": (45.0, 48.0, 16, 6, "VR Physics Action"),
    "vrchat": (35.0, 45.0, 12, 4, "VR Social"),
    "blade and sorcery": (42.0, 46.0, 16, 6, "VR Physics Melee"),
    "into the radius vr": (46.0, 48.0, 16, 6, "VR Survival / Stalker"),
    "superhot vr": (26.0, 26.0, 8, 2, "VR Action / Puzzle"),
    "phasmophobia": (30.0, 32.0, 8, 3, "Co-op Ghost Hunting")
}

def guess_requirements(name, is_vr):
    low_name = name.lower().strip()
    
    # 1. Точное совпадение
    if low_name in KNOWN_REQUIREMENTS:
        req = KNOWN_REQUIREMENTS[low_name]
        return req[0], req[1], req[2], req[3], req[4]

    # 2. Частичное совпадение
    for k, req in KNOWN_REQUIREMENTS.items():
        if k in low_name:
            return req[0], req[1], req[2], req[3], req[4]

    # 3. Эвристика по ключевым словам
    genre = "Action / Adventure"
    if any(w in low_name for w in ["simulator", "sim", "flight"]):
        genre = "Simulation"
    elif any(w in low_name for w in ["racing", "drift", "speed", "rally", "car"]):
        genre = "Racing"
    elif any(w in low_name for w in ["horror", "fear", "dead", "evil", "ghost", "amnesia", "zombie"]):
        genre = "Horror"
    elif any(w in low_name for w in ["strategy", "war", "total", "civ", "crusader", "age of"]):
        genre = "Strategy"
    elif any(w in low_name for w in ["rpg", "quest", "scrolls", "witcher", "souls", "dragon"]):
        genre = "RPG"

    if is_vr:
        return 42.0, 44.0, 12, 6, "VR / " + genre

    # Базовая оценка для неизвестных ПК игр (средние требования)
    return 30.0, 32.0, 8, 3, genre

updated_games = []
for g in games:
    raw_name = g['name']
    norm_name = raw_name.lower().strip()
    
    # Проверяем, является ли это действительно VR игрой
    is_real_vr = False
    if norm_name in GENUINE_VR_EXACT or any(norm_name.startswith(v) for v in ["half-life: alyx", "beat saber", "boneworks", "blade and sorcery", "into the radius", "superhot vr", "vrchat", "rec room", "gorn", "pistol whip", "moss", "contractors vr", "vtol vr"]):
        is_real_vr = True
    elif " vr" in norm_name or norm_name.endswith("vr") or "(vr)" in norm_name or "[vr]" in norm_name:
        is_real_vr = True
    
    # Исправляем Forza, RE, Fishing Planet, War Thunder, Assetto Corsa и прочее
    if any(fake in norm_name for fake in ["forza horizon", "forza motorsport", "fishing planet", "soundpad", "golf with your friends", "carx drift", "tabletop simulator", "house flipper", "alien: isolation", "liar's bar", "pacify", "devour"]):
        is_real_vr = False

    min_gpu, min_cpu, min_ram, min_vram, genre = guess_requirements(raw_name, is_real_vr)

    entry = {
        'id': g['id'],
        'name': raw_name,
        'genre': genre,
        'dev': g.get('developer', 'Game Studio'),
        'is_vr': is_real_vr,
        'min_gpu': min_gpu,
        'min_cpu': min_cpu,
        'min_ram': min_ram,
        'min_vram': min_vram
    }
    if 'img' in g:
        entry['img'] = g['img']
    updated_games.append(entry)

print(f"Total processed games: {len(updated_games)}")
real_vr_count = sum(1 for g in updated_games if g['is_vr'])
print(f"Real VR games count: {real_vr_count}, Non-VR games count: {len(updated_games) - real_vr_count}")

# Сохраняем в games_data_cpp.h
js_arr = json.dumps(updated_games, ensure_ascii=True, separators=(',', ':'))
js_code = 'const GAMES_DATA = ' + js_arr + ';'

delimiter = 'GAMESRAW'
cpp_const = f'static const char* GAMES_JS_DATA = R"{delimiter}(' + js_code + f'){delimiter}";'

with open('games_data_cpp.h', 'w', encoding='utf-8') as f:
    f.write('#pragma once\n')
    f.write(cpp_const)
    f.write('\n')

print('Written updated games_data_cpp.h successfully!')
