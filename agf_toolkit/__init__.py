__description__ = "A toolkit for Artery Gear: Fusion"
__version__ = "0.0.1"
__author__ = "PythonTryHard - Arisu#9695 (<@!263986827214585857>)"

import os
import re
import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def _verify_sub_stat_env_var(name: str) -> bool:
    return name in os.environ and bool(re.match(r"^\d+,\d+", os.environ[name]))


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
        _verify_sub_stat_env_var("SUB_STAT_1"),
        _verify_sub_stat_env_var("SUB_STAT_2"),
        _verify_sub_stat_env_var("SUB_STAT_3"),
        _verify_sub_stat_env_var("SUB_STAT_4"),
    ]
):
    logger.critical("Missing/Malformed sub stat coordinate settings! Check your .env file! Exiting...")
    sys.exit(1)

logger.info("Loading processing functions and libraries, this may take a while!")
