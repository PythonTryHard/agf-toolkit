import re

import numpy as np
from loguru import logger
from paddleocr import PaddleOCR

from agf_toolkit.processor.constant import (
    GEAR_TYPE_MAPPING,
    SET_NAME_MAPPING,
    STAT_TYPE_REGEX_MAPPING,
)

stat_types = f"({'|'.join(i.pattern for i in STAT_TYPE_REGEX_MAPPING)})"
STAT_REGEX = stat_types + r"\s*?([\[\{\(]\s*[LliI1]ocked\s*[\}\]\)])?\s*?(\d+?(\.\d+?)?%?)\s"

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


def extract_stats(ocr_string: str) -> list[tuple[str, str]]:
    """Extract gear sub stats from the OCR-ed string."""
    stats = [(parse_sub_stat_type(i[0]), i[2]) for i in re.findall(STAT_REGEX, ocr_string)]
    logger.info(f"Stats detected as: {stats}")
    return stats


def parse_sub_stat_type(sub_stat_regex_result: str) -> str:
    """Attempt to parse the sub stat type from the regex result."""
    for pattern, true_value in STAT_TYPE_REGEX_MAPPING.items():
        if pattern.match(sub_stat_regex_result):
            return true_value

    # Code shouldn't reach here!
    raise ValueError(f"Regex parsing failed on: {sub_stat_regex_result}! Please open an issue on GitHub!")
