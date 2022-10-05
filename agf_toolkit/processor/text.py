import re

import cv2
from loguru import logger
from paddleocr import PaddleOCR

from agf_toolkit.processor import gears

STAT_REGEX = f"{'|'.join(re.escape(i) for i in gears.STAT_TYPE_MAPPING)}"
MAIN_STAT_REGEX = STAT_REGEX + r"\s*?\s*?(\d+?(\.\d+?)?%?)\s"
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

    # Code shouldn't reach here. If it does, it's a bug.
    raise RuntimeError("Gear set not detected! Please run again under debug mode and report this issues!")


def extract_gear_type(ocr_string: str) -> str:
    """Extract gear type from the OCR-ed string."""
    for i in gears.GEAR_TYPE_MAPPING:
        if i in ocr_string:
            logger.info(f"Gear type detected as {i}")
            return i

    # Code shouldn't reach here. If it does, it's a bug.
    raise RuntimeError("Gear set not detected! Please run again under debug mode and report this issues!")


def extract_main_stat(ocr_string: str) -> gears.Stat:
    """Extract gear mainstat from the OCR-ed string."""
    regex_result = re.search(MAIN_STAT_REGEX, ocr_string)

    if regex_result is None:
        raise RuntimeError("Main stat not detected! Please run again under debug mode and report this issues!")

    main_stat = regex_result.groups()
    logger.info(f"Main stat detected as: {main_stat}")
    return gears.Stat(main_stat[0], main_stat[1], None)


def extract_sub_stats(ocr_string: str) -> list[tuple[str, str]]:
    """Extract gear sub_stats from the OCR-ed string."""
    sub_stats = [i[:2] for i in re.findall(SUB_STAT_REGEX, ocr_string)]
    logger.info(f"Sub stats detected as: {sub_stats}")
    return sub_stats
