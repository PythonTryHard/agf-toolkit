import json
import sys

from loguru import logger

from agf_toolkit.processor.utils import parse_screenshot
from agf_toolkit.utils import adb

# Enter infinite loop
try:
    while True:
        # Grab screenshot and load it in
        gear = parse_screenshot(adb.screencap())

        logger.info(f"Result (JSON): {json.dumps(gear.as_dict())}")
        logger.info(f"Result (encoded): {gear}")

except KeyboardInterrupt:
    logger.info("Received keyboard interrupt. Exiting...")
    sys.exit(0)
