import re
from collections.abc import Sequence
from typing import overload

from agf_toolkit.abc import Encodable
from agf_toolkit.processor.constant import (
    GEAR_TYPE_MAPPING,
    RARITY_GRADE_MAPPING,
    SET_NAME_MAPPING,
    STAT_TYPE_MAPPING,
)


def _reverse_dict(input_dict: dict) -> dict:
    return {v: k for k, v in input_dict.items()}


# type: ignore
class Stat(Encodable):
    """Represents a stat of a gear."""

    VALUE_REGEX = re.compile(r"\d+\.?\d*%?")

    def __init__(self, stat_type, stat_value, stat_rarity) -> None:
        """
        Initialise a Stat object and validate it.

        Since all attributes are validated immediately, type check ignores should be fine.

        Note:
        -   This class is not intended to be used directly, as it is meant to be a processor for the raw stat data
            extracted by various processors.
        -   While the constructor will accept any string as the stat type, after validation all unknown values will be
            set to `None`.

        :param stat_type: The type of the stat. This must be one of the keys in STAT_TYPE_MAPPING.
        :param stat_value: The stat_value of the stat. This must be a valid number, or a percentage.
        :param stat_rarity: The rarity grade of the stat. This must be one of the keys in RARITY_GRADE_MAPPING.
        """
        self.stat_type = stat_type
        self.stat_value = stat_value
        self.stat_rarity = stat_rarity
        self.validate()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.as_dict() == other.as_dict()

    def __repr__(self) -> str:
        return f"Stat(stat_type={self.stat_type !r}, stat_value={self.stat_value !r}, rarity={self.stat_rarity !r})"

    def validate(self) -> None:  # type: ignore
        """Validate the data in the object and modify the data in-place. All invalid data will be set to `None`."""
        # type: ignore
        for mapping, attribute in [
            (STAT_TYPE_MAPPING, "stat_type"),
            (RARITY_GRADE_MAPPING, "stat_rarity"),
        ]:
            if (mapping.get(getattr(self, attribute), None) is None) or (getattr(self, attribute) == -1):
                setattr(self, attribute, None)

        if not self.VALUE_REGEX.match(str(self.stat_value)):
            self.stat_value = None
        else:
            if not str(self.stat_value).endswith("%"):
                self.stat_value = float(self.stat_value)

    def as_dict(self) -> dict:
        """Return the Stat object as a dictionary."""
        return {
            "stat_type": self.stat_type,
            "stat_value": self.stat_value,
            "rarity": self.stat_rarity,
        }

    def encode(self) -> str:
        """Encode the gear object"""
        encoded_stat_type = STAT_TYPE_MAPPING.get(self.stat_type)
        encoded_rarity = RARITY_GRADE_MAPPING.get(self.stat_rarity)
        encoded_stat_value = -1 if self.stat_value is None else self.stat_value

        return f"{encoded_stat_type},{encoded_rarity},{encoded_stat_value}"

    @classmethod
    @overload
    def decode(cls, encoded_string: str):
        ...

    @classmethod
    @overload
    def decode(cls, encoded_string: Sequence[str]):
        ...

    @classmethod
    def decode(cls, encoded_string: str | Sequence[str]):
        """
        Decode an encoded stat string into a Stat object.

        Method is overloaded to accept either a stat string as-is, or a Sequence of strings that composes into a stat
        string, i.e.: `"12,5,88.6"` or `["12", "5", "88.6"]`. Note that only the first 3 comma-separated values are used
        for decoding.

        :param encoded_string: The encoded stat string, or a Sequence of encoded stat strings.
        :return: A Stat object.
        """
        if isinstance(encoded_string, str):
            args = encoded_string.replace(" ", "").split(",")[:3]
        else:
            args = [i.replace(" ", "") for i in encoded_string[:3]]

        raw_stat_type, raw_rarity, raw_value = args

        return cls(raw_stat_type, raw_value, raw_rarity)


class Gear(Encodable):
    """Represents a gear."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        gear_set="",
        gear_type="",
        gear_rarity="",
        gear_star=-1,
        main_stat: Stat = Stat("", "", ""),
        sub_stats: Sequence[Stat] = (),
    ):
        """
        Initialise a Gear object and validate it.

        Note:
        -   This class is not intended to be used directly, as it is meant to be a processor for the raw gear data
            extracted by various processors.
        -   While the constructor will accept any string as the gear set, gear type and gear rarity, after validation
            all unknown values will be set to `None`.

        :param gear_set: The gear set of the gear. This must be one of the keys in SET_NAME_MAPPING.
        :param gear_type: The type of the gear. This must be one of the keys in GEAR_TYPE_MAPPING.
        :param gear_rarity: The rarity grade of the gear. This must be one of the keys in RARITY_GRADE_MAPPING.
        :param gear_star: The number of stars the gear has.
        :param main_stat: The main stat of the gear.
        :param sub_stats: The sub stats of the gear.
        """
        self.gear_set = gear_set
        self.gear_type = gear_type
        self.gear_rarity = gear_rarity
        self.gear_star = gear_star
        self.main_stat = main_stat
        self.sub_stats = sub_stats
        self.validate()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.as_dict() == other.as_dict()

    def validate(self) -> None:
        """
        Validate the data in the object and modify the data in-place. All invalid data will be set to `None`.

        This is only run once after initialising an object, so typing error should be ignored.
        """
        for mapping, attribute in [
            (SET_NAME_MAPPING, "gear_set"),
            (GEAR_TYPE_MAPPING, "gear_type"),
            (RARITY_GRADE_MAPPING, "gear_rarity"),
        ]:
            if (mapping.get(getattr(self, attribute), None) is None) or (getattr(self, attribute) == -1):
                setattr(self, attribute, None)

        if not str(self.gear_star).isdigit():
            self.gear_star = None
        else:
            self.gear_star = int(self.gear_star)

        self.main_stat.validate()
        for i in self.sub_stats:
            i.validate()
        self.sub_stats = list(self.sub_stats)

    def as_dict(self) -> dict:
        """Return the Gear object as a dictionary."""
        return {
            "gear_set": self.gear_set,
            "gear_type": self.gear_type,
            "gear_rarity": self.gear_rarity,
            "gear_star": self.gear_star,
            "main_stat": self.main_stat.as_dict(),
            "sub_stats": [sub_stat.as_dict() for sub_stat in self.sub_stats],
        }

    def encode(self) -> str:
        """Encode the gear object"""
        encoded_gear_set = SET_NAME_MAPPING.get(self.gear_set)
        encoded_gear_type = GEAR_TYPE_MAPPING.get(self.gear_type)
        encoded_gear_rarity = RARITY_GRADE_MAPPING.get(self.gear_rarity)
        encoded_main_stat = self.main_stat.encode()

        encoded_sub_stats = ",".join([sub_stat.encode() for sub_stat in self.sub_stats])
        if encoded_sub_stats:
            encoded_sub_stats = f",{encoded_sub_stats}"

        return (
            f"{encoded_gear_set},"
            f"{encoded_gear_type},"
            f"{encoded_gear_rarity},"
            f"{self.gear_star},"
            f"{encoded_main_stat}"
            f"{encoded_sub_stats}"
        )

    @classmethod
    @overload
    def decode(cls, encoded_string: str):
        ...

    @classmethod
    @overload
    def decode(cls, encoded_string: Sequence[str]):
        ...

    @classmethod
    def decode(cls, encoded_string: str | Sequence[str]):
        """
        Decode an encoded gear string into a Gear object.

        Method is overloaded to accept either a gear string as-is, or a Sequence of strings that composes into a gear
        string, i.e.: `"5,5,2,3,10,43%,0,7,12.2,4,9,40%,1,6,0.4%,3,1,988.0,2"` or `["5", "5", "2", "3", "10,43%", "0",
        "7", "12.2", "4", "9", "40%", "1", "6", "0.4%", "3", "1", "988.0", "2"]`.

        :param encoded_string: The encoded gear string, or a Sequence of encoded gear strings.
        :return: A Gear object.
        """
        if isinstance(encoded_string, str):
            args = encoded_string.replace(" ", "").split(",")
        else:
            args = [i.replace(" ", "") for i in encoded_string]

        raw_gear_set, raw_gear_type, raw_gear_rarity, raw_gear_star, *raw_stats = args

        stats = [raw_stats[i : i + 3] for i in range(0, len(raw_stats), 3)]
        raw_main_stat, *raw_sub_stats = [Stat.decode(sub_stat) for sub_stat in stats]

        return cls(raw_gear_set, raw_gear_type, raw_gear_rarity, raw_gear_star, raw_main_stat, raw_sub_stats)
