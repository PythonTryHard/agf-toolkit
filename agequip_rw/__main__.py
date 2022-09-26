import sys
from loguru import logger

from agequip_rw import templates
from agequip_rw.utils import adb
from agequip_rw.processor import image, text, codec


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
        substat_rarity = image.extract_substat_rarity(info_image)
        substat_data = text.extract_substat(info_text)

        mainstat_data = text.extract_mainstat(info_text)

        gear_star = image.extract_gear_star(info_image, templates.STARS)
        gear_rarity = len(substat_rarity)  # Number of substats correlate to rarity
        gear_set = text.extract_gear_set(info_text)
        gear_type = text.extract_gear_type(info_text)

        # Print out encoded data
        encoded_string = codec.encode(
            gear_type,
            gear_rarity,
            gear_star,
            gear_set,
            mainstat_data,
            substat_rarity,
            substat_data,
        )
        print(encoded_string)

except KeyboardInterrupt:
    logger.info("Received keyboard interrupt. Exiting...")
    sys.exit(0)
