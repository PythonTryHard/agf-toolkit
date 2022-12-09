import cv2
import pytest

from agf_toolkit.processor.gear import Gear, Stat
from agf_toolkit.processor.utils import parse_screenshot


class TestParsers:
    """Test the parsing of screenshots."""

    @pytest.mark.parametrize(
        "file_name,gear_object",
        [
            (
                "tests/Normal_1.jpg",
                Gear(
                    gear_set="Status ACC set",
                    gear_type="Weapon System",
                    gear_rarity="Blue",
                    gear_star=6,
                    main_stat=Stat(stat_type="ATK", stat_value=125.0, stat_rarity=None),
                    sub_stats=[
                        Stat(stat_type="Status ACC", stat_value="9.8%", stat_rarity="Blue"),
                        Stat(stat_type="HP", stat_value=399.0, stat_rarity="Blue"),
                    ],
                ),
            ),
            (
                "tests/Normal_2.jpg",
                Gear(
                    gear_set="DEF set",
                    gear_type="Amplifier Component",
                    gear_rarity="White",
                    gear_star=1,
                    main_stat=Stat(stat_type="DEF", stat_value=10, stat_rarity=None),
                    sub_stats=[],
                ),
            ),
            (
                "tests/Normal_3.jpg",
                Gear(
                    gear_set="SPD set",
                    gear_type="Weapon System",
                    gear_rarity="Yellow",
                    gear_star=6,
                    main_stat=Stat(stat_type="ATK", stat_value=125.0, stat_rarity=None),
                    sub_stats=[
                        Stat(stat_type="HP", stat_value=527.0, stat_rarity="Blue"),
                        Stat(stat_type="Status ACC", stat_value="13.9%", stat_rarity="Blue"),
                        Stat(stat_type="Status RES", stat_value="9.2%", stat_rarity="Blue"),
                        Stat(stat_type="DEF", stat_value=104.0, stat_rarity="Purple"),
                    ],
                ),
            ),
        ],
    )
    def test_normal_screenshots(self, file_name, gear_object):
        """Test against images used to build this tool"""
        parser_result = parse_screenshot(cv2.imread(file_name))
        assert parser_result == gear_object

    @pytest.mark.parametrize("file_name,gear_object", [])
    def test_foreign_screenshots(self, file_name, gear_object):
        """Test auto calibration for foreign screenshots"""
        parser_result = parse_screenshot(cv2.imread(file_name))
        assert parser_result == gear_object
