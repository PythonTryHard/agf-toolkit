import cv2
import pytest

from agf_toolkit.processor.calibration import auto_calibrate_scale
from agf_toolkit.processor.gear import Gear, Stat
from agf_toolkit.processor.utils import parse_screenshot, rescale


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

    @pytest.mark.parametrize(
        "file_name,gear_object",
        [
            (
                "tests/Foreign_1.png",
                Gear(
                    gear_set="Critical set",
                    gear_type="Propulsion System",
                    gear_rarity="Purple",
                    gear_star=5,
                    main_stat=Stat(stat_type="SPD", stat_value=17.5, stat_rarity=None),
                    sub_stats=[
                        Stat(stat_type="Critical", stat_value="6.2%", stat_rarity="Blue"),
                        Stat(stat_type="Status RES", stat_value="11.4%", stat_rarity="Blue"),
                        Stat(stat_type="HP (%)", stat_value="9.5%", stat_rarity="Blue"),
                    ],
                ),
            ),
            (
                "tests/Foreign_2.png",
                Gear(
                    gear_set="Critical DMG set",
                    gear_type="Shield System",
                    gear_rarity="Yellow",
                    gear_star=6,
                    main_stat=Stat(stat_type="DEF", stat_value=70, stat_rarity=None),
                    sub_stats=[
                        Stat(stat_type="Critical", stat_value="14.3%", stat_rarity="Yellow"),
                        Stat(stat_type="CRIT DMG", stat_value="24.6%", stat_rarity="Yellow"),
                        Stat(stat_type="SPD", stat_value=15.4, stat_rarity="Yellow"),
                        Stat(stat_type="DEF (%)", stat_value="25.5%", stat_rarity="Yellow"),
                    ],
                ),
            ),
            (
                "tests/Foreign_3.jpg",
                Gear(
                    gear_set="SPD set",
                    gear_type="Amplifier Component",
                    gear_rarity="Yellow",
                    gear_star=5,
                    main_stat=Stat(stat_type="HP (%)", stat_value="8.0%", stat_rarity=None),
                    sub_stats=[
                        Stat(stat_type="HP", stat_value=362, stat_rarity="Blue"),
                        Stat(stat_type="Critical", stat_value="8.2%", stat_rarity="Purple"),
                        Stat(stat_type="DEF (%)", stat_value="14.9%", stat_rarity="Purple"),
                        Stat(stat_type="ATK (%)", stat_value="10.8%", stat_rarity="Blue"),
                    ],
                ),
            ),
        ],
    )
    def test_foreign_screenshots(self, file_name, gear_object):
        """Test auto calibration for foreign screenshots"""
        image = cv2.imread(file_name)
        scaling_factor = auto_calibrate_scale(image, rounds=1)
        parser_result = parse_screenshot(rescale(image, scaling_factor))
        assert parser_result == gear_object
