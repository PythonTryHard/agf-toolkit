import cv2
import numpy as np
from skimage import color

# Type hints for dealing with OpenCV's BGR magic
R = G = B = int


def get_rgb(bgr_image: cv2.Mat, x: int, y: int) -> tuple[R, G, B]:
    """Get RGB color at coordinate (x,y) of a BGR image."""
    return tuple(bgr_image[y, x])[::-1]  # Coordinate is flipped when dealing with numpy array


def color_distance(base: tuple[R, G, B], target: tuple[R, G, B]):
    """
    Calculate the distance between base and target colour based on CIEDE2000 method.

    Euclidean distance while is less complex and faster, has a rather large margin of error. This is
    made worse when dealing with UI elements with non-one alpha component (or non-255 in sRGB) and
    JPEG compression artefacts (if any). CIEDE2000 should hopefully be able to tighten this margin.
    """
    lab_base = cv2.cvtColor(np.array([[list(base)]], dtype=np.uint8), cv2.COLOR_RGB2LAB)
    lab_target = cv2.cvtColor(np.array([[list(target)]], dtype=np.uint8), cv2.COLOR_RGB2LAB)

    return float(color.deltaE_ciede2000(lab_base, lab_target, kL=2))
