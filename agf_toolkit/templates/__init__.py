import logging
import sys
from importlib import resources
from types import NoneType

import cv2
from loguru import logger

__all__ = ["INFO_BOX", "STARS"]

logging.getLogger(cv2.__name__).setLevel(logging.CRITICAL)

INFO_BOX = cv2.imread(str(resources.path("agf_toolkit.templates", "info_box.png")))
SUB_STAT_1 = (30, 400)
SUB_STAT_2 = (30, 450)
SUB_STAT_3 = (30, 500)
SUB_STAT_4 = (30, 550)
STARS = {
    1: cv2.imread(str(resources.path("agf_toolkit.templates", "1.png"))),
    2: cv2.imread(str(resources.path("agf_toolkit.templates", "2.png"))),
    3: cv2.imread(str(resources.path("agf_toolkit.templates", "3.png"))),
    4: cv2.imread(str(resources.path("agf_toolkit.templates", "4.png"))),
    5: cv2.imread(str(resources.path("agf_toolkit.templates", "5.png"))),
    6: cv2.imread(str(resources.path("agf_toolkit.templates", "6.png"))),
}

if any(isinstance(i, NoneType) for i in [INFO_BOX, *STARS.values()]):
    logger.critical(
        "Failed to load templates! "
        "Please verify that ALL templates are present in the 'templates' directory as instructed!"
    )
    sys.exit(1)
