from agequip_rw.processor import gears


def reverse_dict(d: dict) -> dict:
    return {v: k for k, v in d.items()}


def encode(
    gear_type: str,
    gear_rarity: int,
    gear_star: int,
    gear_set: str,
    mainstat_data: tuple[str, str],
    substat_rarity: dict[int, int],
    substat_data: tuple[str, str],
):
    """Encode the gear data into a string."""
    # Gear infos
    encoded_type = gears.GEAR_TYPE_MAPPING[gear_type]
    encoded_set = gears.SET_NAME_MAPPING[gear_set]

    # Main stat
    mainstat_type = gears.STAT_TYPE_MAPPING[mainstat_data[0]]
    mainstat_value = mainstat_data[1]

    # Substat infos
    substats = []
    for i in zip(substat_data, substat_rarity.values()):
        (stat_type, value), rarity = i

        if stat_type in ("ATK", "DEF", "HP") and "%" in value:
            stat_type += " (%)"

        encoded_substat = ",".join(map(str, (gears.STAT_TYPE_MAPPING[stat_type], value, rarity)))
        substats.append(encoded_substat)

    return "{},{},{},{},{},{},{}".format(
        encoded_type,
        encoded_set,
        gear_rarity,
        gear_star,
        mainstat_type,
        mainstat_value,
        ",".join(substats),
    )


def decode(text: str) -> dict:
    """Decode the gear data from encoded string."""
    decode_result = {}

    # Gear infos
    (
        encoded_type,
        encoded_set,
        gear_rarity,
        gear_star,
        mainstat_type,
        mainstat_value,
        *substats,
    ) = text.split(",")

    decode_result["gear_type"] = reverse_dict(gears.GEAR_TYPE_MAPPING)[int(encoded_type)]
    decode_result["gear_set"] = reverse_dict(gears.SET_NAME_MAPPING)[int(encoded_set)]
    decode_result["gear_rarity"] = int(gear_rarity)
    decode_result["gear_star"] = int(gear_star)

    # Main stat
    decode_result["mainstat_type"] = reverse_dict(gears.STAT_TYPE_MAPPING)[int(mainstat_type)]
    decode_result["mainstat_value"] = mainstat_value

    # Substat infos
    decode_result["substats"] = []
    for substat in [substats[i : i + 3] for i in range(0, len(substats), 3)]:  # Split into 3s
        stat_type, value, rarity = substat

        stat_type = reverse_dict(gears.STAT_TYPE_MAPPING)[int(stat_type)]
        rarity = gears.RARITY_GRADE_MAPPING[int(rarity)]

        decode_result["substats"].append({"type": stat_type, "value": value, "rarity": rarity})

    return decode_result
