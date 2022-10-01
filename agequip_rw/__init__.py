__name__ = "agequip_rw"
__description__ = "A tool to aid collection of Artery Gear: Fusion (AGF)'s gear data"
__version__ = "0.1.0"
__author__ = "PythonTryHard - Arisu#9695 (<@!263986827214585857>)"

import os
import re
import sys

from dotenv import load_dotenv
from loguru import logger


load_dotenv()


def _verify_substat_env_var(name: str) -> bool:
    return name in os.environ and re.match(r"^\d+,\d+", os.environ[name])


logger.remove()
logger.add(
    sys.stderr,
    level="DEBUG" if bool(os.environ.get("DEBUG")) else "INFO",
    format=(
        "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | "
        "<level>{level: <8}</> | "
        "<c>{name}</>:<c>{function}</>:<c>{line}</c> - <level>{message}</>"
    ),
)

logger.debug("Logging 'DEBUG' messages too.")

logger.info("Verifying environment variables.")
if not all(
    [
        _verify_substat_env_var("SUBSTAT_1"),
        _verify_substat_env_var("SUBSTAT_2"),
        _verify_substat_env_var("SUBSTAT_3"),
        _verify_substat_env_var("SUBSTAT_4"),
    ]
):
    logger.error("Missing/Malformed substat coordinate settings! Check your .env file! Exiting...")
    if __name__ == "__main__":
        sys.exit(1)

logger.info("Loading libraries, this may take a while!")
