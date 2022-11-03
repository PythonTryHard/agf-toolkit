from typing import Any, Collection, Optional, Union

from agf_toolkit.processor.constant import (
    GEAR_TYPE_MAPPING,
    RARITY_GRADE_MAPPING,
    SET_NAME_MAPPING,
    STAT_TYPE_MAPPING,
)


def _reverse_dict(input_dict: dict) -> dict:
    return {v: k for k, v in input_dict.items()}


def _null_safe_encode(
    value: Any, null_values: Optional[Collection[Any]] = None, null_representation: Any = "-1"
) -> Any:
    if not null_values:
        null_values = []
    return null_representation if value in [*null_values, None] else value


def _null_safe_decode(value: Any, null_indicator: Any = "-1", null_value: Any = None) -> Any:
    return value if value != null_indicator else null_value


class Stat:
    """
    Represent a gear's stat (singular).

    Unless absolutely necessary, this class should not be instantiated manually.
    Nevertheless, there is one way to create a Stat instance:
        1. Manually supplying the value as required by the constructor i.e., `Stat("HP", "20%", "Yellow")`

    The rationale is as this is meant to be used only as intermediate to add to a Gear instance, supporting decoding
    from comma-separated string is redundant; plus, decoding in a gear object most likely needs to split the string
    fully by commas rather than splitting 3 times, then skip ahead, split, skip ahead, split.
    """

    def __init__(self, stat_type: Union[str, None], value: Union[str, None], rarity: Union[str, None]) -> None:
        self.stat_type = stat_type
        self.value = value
        self.rarity = rarity

    def __repr__(self) -> str:
        return f"Stat(type={self.stat_type !r}, value={self.value !r}, rarity={self.rarity !r})"

    def __str__(self) -> str:
        return self.encode()

    def as_dict(self) -> dict:
        """Return a dict representing the stat"""
        return {
            "stat_type": self.stat_type,
            "value": self.value,
            "rarity": self.rarity,
        }

    def encode(self) -> str:
        """Encode the stat into a comma-separated string"""
        return (
            f"{_null_safe_encode(STAT_TYPE_MAPPING.get(self.stat_type))},"
            f"{_null_safe_encode(self.value)},"
            f"{_null_safe_encode(RARITY_GRADE_MAPPING.get(self.rarity))}"
        )

    @classmethod
    def decode(cls, stat_type, value, rarity):
        """Parse comma-separated stats into a Stat object"""
        return cls(
            stat_type=_reverse_dict(STAT_TYPE_MAPPING).get(_null_safe_decode(stat_type)),
            value=_null_safe_decode(value),
            rarity=_reverse_dict(RARITY_GRADE_MAPPING).get(_null_safe_decode(rarity)),
        )


class Gear:
    """
    Represent a unit of equipment in the game.

    There are two ways to create a Gear object:
        1. Pass a photo containing the gear info box into `parse_screenshot()` after instantiating.
        2. Manually input the needed values when instantiating.

    Note:
        - Any supplied constructor data will get overwritten after calling `parse_screenshot()`.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        gear_set: Union[str, None] = None,
        gear_type: Union[str, None] = None,
        rarity: Union[str, None] = None,
        star: Union[int, None] = None,
        main_stat: Union[Stat, None] = None,
        sub_stats: Union[Collection[Stat], None] = None,
    ) -> None:
        self.gear_set = gear_set
        self.gear_type = gear_type
        self.rarity = rarity
        self.star = star
        self.main_stat = Stat(None, None, None) if main_stat is None else main_stat
        self.sub_stats = [Stat(None, None, None)] if sub_stats is None else sub_stats

    def __repr__(self) -> str:
        return (
            "Gear("
            f"set={self.gear_set !r}, "
            f"type={self.gear_type !r}, "
            f"rarity={self.rarity !r}, "
            f"star={self.star !r}, "
            f"main_stat={self.main_stat !r}, "
            f"sub_stats={self.sub_stats !r})"
        )

    def __str__(self) -> str:
        return self.encode()

    def as_dict(self) -> dict:
        """Return a dict representing the gear"""
        return {
            "set": self.gear_set,
            "type": self.gear_type,
            "rarity": self.rarity,
            "star": self.star,
            "main_stat": self.main_stat.as_dict(),
            "sub_stats": list(i.as_dict() for i in self.sub_stats),
        }

    def encode(self) -> str:
        """
        Return a comma-separated compact representation of a gear.

        The encoding scheme is as follows:
            `set_name,gear_type,rarity,star,(main_stat),*(sub_stats)`.
        With:
            - `(main_stat)` is always a 3-tuple of `type,value,rarity`.
            - `(sub_stats)` is to be split exhaustively into 3-tuples: `type,value,rarity`.
        Note:
             - `None` is represented as `-1`.

        """
        return (
            f"{_null_safe_encode(SET_NAME_MAPPING.get(self.gear_set))},"
            f"{_null_safe_encode(GEAR_TYPE_MAPPING.get(self.gear_type))},"
            f"{_null_safe_encode(RARITY_GRADE_MAPPING.get(self.rarity))},"
            f"{self.star if self.star is not None and 0 < self.star <= 6 else -1},"
            f"{self.main_stat},"
            f"{','.join(str(i) for i in self.sub_stats)}"
        )

    @classmethod
    def decode(cls, input_string: str):
        """Decode a string and return a Gear instance."""
        if len(split_input := input_string.split(",")) - 4 % 3 != 0:
            raise ValueError("Invalid encoded string (number of components does not match expected length (3n + 4))")

        gear_set, gear_type, rarity, star, *stats = split_input

        main_stat = Stat.decode(*stats[:3])
        sub_stats = [Stat.decode(*i) for i in [stats[i : i + 3] for i in range(3, len(stats), 3)]]  # Split to 3s

        return cls(
            gear_set=_reverse_dict(SET_NAME_MAPPING).get(_null_safe_decode(gear_set)),
            gear_type=_reverse_dict(GEAR_TYPE_MAPPING).get(_null_safe_decode(gear_type)),
            rarity=_reverse_dict(RARITY_GRADE_MAPPING).get(_null_safe_decode(rarity)),
            star=int(star) if star.isdigit() else None,
            main_stat=main_stat,
            sub_stats=sub_stats,
        )
