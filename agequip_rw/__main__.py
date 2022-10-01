import sys
from loguru import logger

from agequip_rw import templates
from agequip_rw.utils import adb
from agequip_rw.processor import image, text, gears


# Initialise ADB connection
ADB = adb.get_adb_client()
DEVICE = adb.get_device(ADB)

# Enter infinite loop
try:
    while True:
        input("Press Enter to capture screen...")

        # Grab screenshot and pre-process
        scrsht = adb.screencap(DEVICE)
        info_image = image.extract_info_box(scrsht, templates.INFO_BOX)
        info_text = text.extract_text(info_image)

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
        print(gear)

except KeyboardInterrupt:
    logger.info("Received keyboard interrupt. Exiting...")
    sys.exit(0)
