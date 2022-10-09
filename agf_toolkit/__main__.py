import json
import sys

from loguru import logger

from agf_toolkit import templates
from agf_toolkit.processor import gears, image, text
from agf_toolkit.utils import adb

# Enter infinite loop
try:
    while True:
        input("Press Enter to capture screen...")

        # Grab screenshot and pre-process
        scrsht = adb.screencap()
        info_image = image.extract_info_box(scrsht, templates.INFO_BOX)
        info_text = text.extract_text(info_image)  # pylint: disable=invalid-name

        # Extract information from info_box
        gear_rarity, _sub_stat_rarity = image.extract_sub_stat_rarity(info_image)
        _sub_stat_data = text.extract_sub_stats(info_text)

        main_stat = text.extract_main_stat(info_text)
        sub_stats = list(gears.Stat(*data, rarity) for data, rarity in zip(_sub_stat_data, _sub_stat_rarity.values()))

        gear_star = image.extract_gear_star(info_image, templates.STARS)
        gear_set = text.extract_gear_set(info_text)
        gear_type = text.extract_gear_type(info_text)

        # Compose the gear
        gear = gears.Gear(
            gear_set=gear_set,
            gear_type=gear_type,
            star=gear_star,
            rarity=gear_rarity,
            main_stat=main_stat,
            sub_stats=sub_stats,
        )
        logger.info(f"Result (JSON): {json.dumps(gear.as_dict())}")
        logger.info(f"Result (encoded): {gear}")

except KeyboardInterrupt:
    logger.info("Received keyboard interrupt. Exiting...")
    sys.exit(0)
