import sys
from importlib import resources
from types import NoneType

import cv2
from loguru import logger

__all__ = ["INFO_BOX", "STARS"]

INFO_BOX = cv2.imread(str(resources.path("agf_toolkit.templates", "info_box.png")))
STARS = {
    1: cv2.imread(str(resources.path("agf_toolkit.templates", "1.png"))),
    2: cv2.imread(str(resources.path("agf_toolkit.templates", "2.png"))),
    3: cv2.imread(str(resources.path("agf_toolkit.templates", "3.png"))),
    4: cv2.imread(str(resources.path("agf_toolkit.templates", "4.png"))),
    5: cv2.imread(str(resources.path("agf_toolkit.templates", "5.png"))),
    6: cv2.imread(str(resources.path("agf_toolkit.templates", "6.png"))),
}

if any(isinstance(i, NoneType) for i in [INFO_BOX, *STARS.values()]):
    logger.error(
        "Failed to load templates! "
        "Please verify that all templates are present in the 'templates' directory as instructed!"
    )
    sys.exit(1)
