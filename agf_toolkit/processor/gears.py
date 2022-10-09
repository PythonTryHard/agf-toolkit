from dataclasses import dataclass
from typing import Union

GEAR_TYPE_MAPPING = {
    "Weapon System": 0,
    "Power System": 1,
    "Shield System": 2,
    "Propulsion System": 3,
    "Aiming Component": 4,
    "Amplifier Component": 5,
}

STAT_TYPE_MAPPING = {
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
    "Yellow": 0,
    "Purple": 1,
    "Blue": 2,
    "Green": 3,
    "White": 4,
}


def _reverse_dict(input_dict: dict) -> dict:
    return {v: k for k, v in input_dict.items()}


@dataclass
class Stat:
    """
    Stat class for gear sub stats.

    Attributes
    ----------
    stat_type   : str               = Type of stat.
    value       : str               = Value of stat. May contain "%" if gear type is percentage.
    rarity      : Union[str, None]  = Rarity of stat. None if not applicable (i.e. main stat).
    """

    stat_type: str
    value: str
    rarity: Union[str, None]

    def __repr__(self):
        return f"Stat(type={self.stat_type}, value={self.value}, rarity={self.rarity})"

    def __str__(self):
        return (
            f"{STAT_TYPE_MAPPING[self.stat_type]},"
            f"{self.value},"
            f"{-1 if self.rarity is None else RARITY_GRADE_MAPPING[self.rarity]}"
        )

    def as_dict(self):
        """Return a dict representing the stat"""
        return {
            "stat_type": self.stat_type,
            "value": self.value,
            "rarity": self.rarity,
        }

    @classmethod
    def parse(cls, stat_type, value, rarity):
        """Parse comma-separated stats into a Stat object"""
        return cls(
            stat_type=_reverse_dict(STAT_TYPE_MAPPING)[int(stat_type)],
            value=value,
            rarity=None if int(rarity) == -1 else _reverse_dict(RARITY_GRADE_MAPPING)[int(rarity)],
        )


@dataclass
class Gear:
    """
    Gear class for gear info.

    Attributes
    ----------
    gear_set    : str           = Set of gear.
    gear_type   : str           = Type of gear.
    rarity      : str           = Rarity of gear.
    star        : int           = Star count of gear.
    main_stat   : Stat          = Main stat of gear.
    sub_stats   : list[Stat]    = Sub stats of gear.
    """

    gear_set: str
    gear_type: str
    rarity: str
    star: int
    main_stat: Stat
    sub_stats: list[Stat]

    def __repr__(self):
        return (
            "Gear("
            f"set={self.gear_set}, "
            f"type={self.gear_type}, "
            f"rarity={self.rarity}, "
            f"star={self.star}, "
            f"main_stat={self.main_stat}, "
            f"sub_stats={self.sub_stats})"
        )

    def __str__(self):
        return (
            f"{SET_NAME_MAPPING[self.gear_set]},"
            f"{GEAR_TYPE_MAPPING[self.gear_type]},"
            f"{RARITY_GRADE_MAPPING[self.rarity]},"
            f"{self.star},"
            f"{self.main_stat},"
            f"{','.join(str(i) for i in self.sub_stats)}"
        )

    def as_dict(self):
        """Return a dict representing the gear"""
        return {
            "set": self.gear_set,
            "type": self.gear_type,
            "rarity": self.rarity,
            "star": self.star,
            "main_stat": self.main_stat.as_dict(),
            "sub_stats": list(i.as_dict() for i in self.sub_stats),
        }

    @classmethod
    def parse_string(cls, gear_string: str):
        """Parse a string into a Gear object."""
        gear_set, gear_type, rarity, star, *stats = gear_string.split(",")

        main_stat = Stat.parse(*stats[:3])
        sub_stats = [Stat.parse(*i) for i in [stats[i : i + 3] for i in range(3, len(stats), 3)]]  # Split to 3s

        return cls(
            gear_set=_reverse_dict(SET_NAME_MAPPING)[int(gear_set)],
            gear_type=_reverse_dict(GEAR_TYPE_MAPPING)[int(gear_type)],
            rarity=_reverse_dict(RARITY_GRADE_MAPPING)[int(rarity)],
            star=int(star),
            main_stat=main_stat,
            sub_stats=sub_stats,
        )
