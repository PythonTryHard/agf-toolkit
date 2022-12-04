import re

GEAR_TYPE_MAPPING = {
    None: -1,
    "Weapon System": 1,
    "Power System": 2,
    "Shield System": 3,
    "Propulsion System": 4,
    "Aiming Component": 5,
    "Amplifier Component": 6,
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
    "ATK": 1,
    "DEF": 2,
    "HP": 3,
    "ATK (%)": 4,
    "DEF (%)": 5,
    "HP (%)": 6,
    "SPD": 7,
    "Critical": 8,
    "CRIT DMG": 9,
    "Status ACC": 10,
    "Status RES": 11,
}

SET_NAME_MAPPING = {
    None: -1,
    "ATK set": 1,
    "Counter Engine set": 2,
    "Critical set": 3,
    "Critical DMG set": 4,
    "DEF set": 5,
    "HP set": 6,
    "Lifesteal set": 7,
    "Immunity set": 8,
    "Riposte set": 9,
    "SPD set": 10,
    "Status ACC set": 11,
    "Status Resistance set": 12,
}

RARITY_GRADE_MAPPING = {
    None: -1,
    "Yellow": 1,
    "Purple": 2,
    "Blue": 3,
    "Green": 4,
    "White": 5,
}
