import re

import numpy as np
from loguru import logger
from paddleocr import PaddleOCR

from agf_toolkit.processor.constants import (
    GEAR_TYPE_MAPPING,
    SET_NAME_MAPPING,
    STAT_TYPE_REGEX_MAPPING,
)
from agf_toolkit.processor.gears import Stat

STAT_REGEX = f"({'|'.join(i.pattern for i in STAT_TYPE_REGEX_MAPPING)})"
MAIN_STAT_REGEX = STAT_REGEX + r"\s*?\s*?(\d+?(\.\d+?)?%?)\s"
SUB_STAT_REGEX = STAT_REGEX + r"\s*?[\(\[\{]Locked[\)\]\}]\s*?(\d+?(\.\d+?)?%?)\s"

logger.info("If this is your first start, the OCR model will be downloaded (roughly 20MB).")
logger.info("Loading OCR model.")
OCR = PaddleOCR(use_angle_cls=False, lang="en", show_log=False, rec_algorithm="SVTR_LCNet")


def extract_text(image: np.ndarray[int, np.dtype[np.generic]]) -> str:
    """Extract text from gear info box. At least it's more accurate than Tesseract."""
    logger.info("Starting OCR on gear info.")
    result = " ".join(i[-1][0] for i in OCR.ocr(image, cls=False)[0])  # The last [0] is introduced in PaddleOCR 2.6.0.2
    logger.debug(f"OCR result: {result}")
    return result


def extract_gear_set(ocr_string: str) -> str:
    """Extract gear grade from OCR-ed string"""
    for i in SET_NAME_MAPPING:
        if i is not None and i in ocr_string:
            logger.info(f"Gear set detected as {i}")
            return i

    # Code shouldn't reach here. If it does, it's a bug.
    raise RuntimeError("Gear set not detected! Please run again under debug mode and report this issues!")


def extract_gear_type(ocr_string: str) -> str:
    """Extract gear type from the OCR-ed string."""
    for i in GEAR_TYPE_MAPPING:
        if i is not None and i in ocr_string:
            logger.info(f"Gear type detected as {i}")
            return i

    # Code shouldn't reach here. If it does, it's a bug.
    raise RuntimeError("Gear set not detected! Please run again under debug mode and report this issues!")


def extract_main_stat(ocr_string: str) -> Stat:
    """Extract gear's main stat from the OCR-ed string."""
    regex_result = re.search(MAIN_STAT_REGEX, ocr_string)

    if regex_result is None:
        raise RuntimeError("Main stat not detected! Please run again under debug mode and report this issues!")

    main_stat = regex_result.groups()
    logger.info(f"Main stat detected as: {main_stat}")
    return Stat(main_stat[0], main_stat[1], None)


def extract_sub_stats(ocr_string: str) -> list[tuple[str, str]]:
    """Extract gear sub stats from the OCR-ed string."""
    sub_stats = [(parse_sub_stat_type(i[0]), i[1]) for i in re.findall(SUB_STAT_REGEX, ocr_string)]
    logger.info(f"Sub stats detected as: {sub_stats}")
    return sub_stats


def parse_sub_stat_type(sub_stat_regex_result: str) -> str:
    """Attempt to parse the sub stat type from the regex result."""
    for pattern, true_value in STAT_TYPE_REGEX_MAPPING.items():
        if pattern.match(sub_stat_regex_result):
            return true_value

    # Code shouldn't reach here!
    raise ValueError(f"Regex parsing failed on: {sub_stat_regex_result}! Please open an issue on GitHub!")
