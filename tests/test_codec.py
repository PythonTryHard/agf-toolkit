import random
import string

import pytest

from agf_toolkit.processor.gear import Gear, Stat


@pytest.fixture
def gear_object():
    return Gear(
        gear_set="DEF set",
        gear_type="Aiming Component",
        gear_rarity="Purple",
        gear_star=3,
        main_stat=Stat(stat_type="Status ACC", stat_value="43%", stat_rarity=""),
        sub_stats=(
            Stat(stat_type="SPD", stat_value="12.2", stat_rarity="Green"),
            Stat(stat_type="CRIT DMG", stat_value="40%", stat_rarity="Yellow"),
            Stat(stat_type="HP (%)", stat_value="0.4%", stat_rarity="Blue"),
            Stat(stat_type="ATK", stat_value="988", stat_rarity="Purple"),
        ),
    )


@pytest.fixture
def gear_decode():
    return r"5,5,2,3,10,-1,43%,7,4,12.2,9,1,40%,6,3,0.4%,1,2,988.0"


@pytest.fixture
def stat_object():
    return Stat(stat_type="Status RES", stat_value="342", stat_rarity="Yellow")


@pytest.fixture
def stat_decode():
    return "11,1,342.0"


class TestNonNullOperations:
    """Test the encoding and decoding of a Gear instance under normal circumstances."""

    def test_encode_stat(self, stat_object, stat_decode):
        assert stat_object.encode() == stat_decode

    def test_decode_stat(self, stat_object, stat_decode):
        assert Stat.decode(stat_decode) == stat_object

    def test_encode_gear(self, gear_object, gear_decode):
        assert gear_object.encode() == gear_decode

    def test_decode_gear(self, gear_object, gear_decode):
        assert Gear.decode(gear_decode) == gear_object


class TestNullOperations:
    """Test the encoding and decoding of a Gear instance with some null values."""

    def test_encode_baseline(self):
        assert Gear().encode() == "-1,-1,-1,-1,-1,-1,-1"

    def test_decode_baseline(self):
        assert Gear.decode("-1,-1,-1,-1,-1,-1,-1") == Gear()


class TestInvallidCharacterHandling:
    """
    Test the decoder on handling invalid characters.

    This does not protect against rubbish data.
    """

    def test_invalid_character_gear(self, gear_object, gear_decode):
        gear_decode_array = list(gear_decode)
        for i in range(1000):
            gear_decode_array.insert(random.randint(0, len(gear_decode_array)), random.choice(string.ascii_letters))
        polluted_gear_decode = "".join(gear_decode_array)

        assert Gear.decode(polluted_gear_decode) == gear_object
