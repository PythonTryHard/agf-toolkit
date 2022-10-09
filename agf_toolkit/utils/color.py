from typing import TypeAlias

import cv2
import numpy as np
from skimage import color

# Type hints for dealing with OpenCV's BGR magic
R: TypeAlias = int
G: TypeAlias = int
B: TypeAlias = int


def get_rgb(bgr_image: np.ndarray[int, np.dtype[np.generic]], coord_x: int, coord_y: int) -> tuple[R, G, B]:
    """
    Get RGB color at coordinate (x,y) of a BGR image.

    mypy will complain about typing but since this should only be used in a well-known way, we
    can ignore it.
    """
    return tuple(bgr_image[coord_y, coord_x])[::-1]  # type: ignore


def color_distance(base: tuple[R, G, B], target: tuple[R, G, B]) -> float:
    """
    Calculate the distance between base and target colour based on CIEDE2000 method.

    Euclidean distance while is less complex and faster, has a rather large margin of error. This is
    made worse when dealing with UI elements with non-one alpha component (or non-255 in sRGB) and
    JPEG compression artefacts (if any). CIEDE2000 should hopefully be able to tighten this margin.
    """
    lab_base = cv2.cvtColor(np.array([[list(base)]], dtype=np.uint8), cv2.COLOR_RGB2LAB)
    lab_target = cv2.cvtColor(np.array([[list(target)]], dtype=np.uint8), cv2.COLOR_RGB2LAB)

    return float(color.deltaE_ciede2000(lab_base, lab_target, kL=2))
