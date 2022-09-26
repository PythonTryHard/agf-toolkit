import cv2
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from loguru import logger

# Type hints for dealing with OpenCV's BGR magic
R = G = B = int


def get_rgb(bgr_image: cv2.Mat, x: int, y: int) -> tuple[R, G, B]:
    """Get RGB color at coordinate (x,y) of a BGR image."""
    rgb = tuple(bgr_image[y, x])[
        ::-1
    ]  # Coordinate is flipped when dealing with numpy array
    logger.debug(f"Color at ({x}, {y}) captured = {rgb}")

    return rgb


def color_distance(base: tuple[R, G, B], target: tuple[R, G, B]):
    """
    Calculate the distance between base and target colour based on CIEDE2000 method.

    Euclidean distance while is less complex and faster, has a rather large margin of error. This is
    made worse when dealing with UI elements with non-one alpha component (or non-255 in sRGB) and
    JPEG compression artefacts (if any). CIEDE2000 should hopefully be able to tighten this margin.
    """
    logger.debug(f"Calculating distance between base {base} and target {target}.")
    base_converted = convert_color(sRGBColor(*base, is_upscaled=True), LabColor)
    target_converted = convert_color(sRGBColor(*target, is_upscaled=True), LabColor)

    delta_e = delta_e_cie2000(base_converted, target_converted)
    logger.debug(f"Delta-E calculated to be {delta_e}.")

    return delta_e
