import re

import cv2
from loguru import logger
from paddleocr import PaddleOCR

from agequip_rw.processor import constants


STAT_REGEX = "({})".format("|".join(re.escape(i) for i in constants.STAT_TYPE_MAPPING))
MAINSTAT_REGEX = STAT_REGEX + r"\s*?(\d+?%?)\s"
SUBSTAT_REGEX = STAT_REGEX + r"\s*?[\(\[\{]Locked[\)\]\}]\s*?(\d+?(\.\d+?)?%?)\s"

logger.info("If this is your first start, the OCR model will be downloaded (roughly 20MB).")
logger.info("Loading OCR model.")
OCR = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)


def extract_text(image: cv2.Mat) -> str:
    """Extract text from gear info box. At least it's more accurate than Tesseract"""
    logger.info("Starting OCR on gear info.")
    result = OCR.ocr(image, cls=False)
    logger.debug(f"OCR result:\n{result}")
    return " ".join(i[-1][0] for i in result)


def extract_gear_set(ocr_string: str) -> str:
    """Extract gear grade from OCR-ed string"""
    for i in constants.SET_NAME_MAPPING:
        if i in ocr_string:
            logger.info(f"Gear set detected as {i}")
            return i


def extract_gear_type(ocr_string: str) -> str:
    """Extract gear type from the OCR-ed string."""
    for i in constants.GEAR_TYPE_MAPPING:
        if i in ocr_string:
            logger.info(f"Gear type detected as {i}")
            return i


def extract_mainstat(ocr_string: str) -> tuple[str, str]:
    """Extract gear mainstat from the OCR-ed string."""
    main_stat = re.search(MAINSTAT_REGEX, ocr_string).groups()
    logger.info(f"Main stat detected as: {main_stat}")
    return main_stat


def extract_substat(ocr_string: str) -> list[tuple[str, str]]:
    """Extract gear substats from the OCR-ed string."""
    substats = [i[:2] for i in re.findall(SUBSTAT_REGEX, ocr_string)]
    logger.info(f"Sub stats detected as: {substats}")
    return substats
