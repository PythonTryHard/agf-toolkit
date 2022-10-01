import re

import cv2
from loguru import logger
from paddleocr import PaddleOCR

from agequip_rw.processor import gears


STAT_REGEX = "({})".format("|".join(re.escape(i) for i in gears.STAT_TYPE_MAPPING))
MAINSTAT_REGEX = STAT_REGEX + r"\s*?\s*?(\d+?(\.\d+?)?%?)\s"
SUB_STAT_REGEX = STAT_REGEX + r"\s*?[\(\[\{]Locked[\)\]\}]\s*?(\d+?(\.\d+?)?%?)\s"

logger.info("If this is your first start, the OCR model will be downloaded (roughly 20MB).")
logger.info("Loading OCR model.")
OCR = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)


def extract_text(image: cv2.Mat) -> str:
    """Extract text from gear info box. At least it's more accurate than Tesseract"""
    logger.info("Starting OCR on gear info.")
    result = " ".join(i[-1][0] for i in OCR.ocr(image, cls=False))
    logger.debug(f"OCR result: {result}")
    return result


def extract_gear_set(ocr_string: str) -> str:
    """Extract gear grade from OCR-ed string"""
    for i in gears.SET_NAME_MAPPING:
        if i in ocr_string:
            logger.info(f"Gear set detected as {i}")
            return i


def extract_gear_type(ocr_string: str) -> str:
    """Extract gear type from the OCR-ed string."""
    for i in gears.GEAR_TYPE_MAPPING:
        if i in ocr_string:
            logger.info(f"Gear type detected as {i}")
            return i


def extract_main_stat(ocr_string: str) -> gears.Stat:
    """Extract gear mainstat from the OCR-ed string."""
    main_stat = re.search(MAINSTAT_REGEX, ocr_string).groups()[:2]
    logger.info(f"Main stat detected as: {main_stat}")
    return gears.Stat(*main_stat, None)


def extract_sub_stats(ocr_string: str) -> list[tuple[str, str]]:
    """Extract gear substats from the OCR-ed string."""
    substats = [i[:2] for i in re.findall(SUB_STAT_REGEX, ocr_string)]
    logger.info(f"Sub stats detected as: {substats}")
    return substats
