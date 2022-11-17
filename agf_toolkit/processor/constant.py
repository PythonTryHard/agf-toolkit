import re

GEAR_TYPE_MAPPING = {
    None: -1,
    "Weapon System": 0,
    "Power System": 1,
    "Shield System": 2,
    "Propulsion System": 3,
    "Aiming Component": 4,
    "Amplifier Component": 5,
}

STAT_TYPE_REGEX_MAPPING = {
    re.compile(r"ATK"): "ATK",
    re.compile(r"DEF"): "DEF",
    re.compile(r"HP"): "HP",
    re.compile(r"ATK\s*?\(%\)"): "ATK (%)",
    re.compile(r"DEF\s*?\(%\)"): "DEF (%)",
    re.compile(r"HP\s*?\(%\)"): "HP (%)",
    re.compile(r"SPD"): "SPD",
    re.compile(r"Critical"): "Critical",
    re.compile(r"CRIT\s*?DMG"): "CRIT DMG",
    re.compile(r"Status\s*?ACC"): "Status ACC",
    re.compile(r"Status\s*?RES"): "Status RES",
}

STAT_TYPE_MAPPING = {
    None: -1,
    "ATK": 0,
    "DEF": 1,
    "HP": 2,
    "ATK (%)": 3,
    "DEF (%)": 4,
    "HP (%)": 5,
    "SPD": 6,
    "Critical": 7,
    "CRIT DMG": 8,
    "Status ACC": 9,
    "Status RES": 10,
}

SET_NAME_MAPPING = {
    None: -1,
    "ATK set": 0,
    "Counter Engine set": 1,
    "Critical set": 2,
    "Critical DMG set": 3,
    "DEF set": 4,
    "HP set": 5,
    "Lifesteal set": 6,
    "Immunity set": 7,
    "Riposte set": 8,
    "SPD set": 9,
    "Status ACC set": 10,
    "Status Resistance set": 11,
}

RARITY_GRADE_MAPPING = {
    None: -1,
    "Yellow": 0,
    "Purple": 1,
    "Blue": 2,
    "Green": 3,
    "White": 4,
}
