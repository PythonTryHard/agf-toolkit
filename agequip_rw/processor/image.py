import os

import cv2
from loguru import logger

from agequip_rw.utils import color
from agequip_rw.processor import constants

RARITY_COLORS = {
    0: (254, 205, 51),
    1: (217, 169, 249),
    2: (138, 199, 252),
    3: (141, 223, 186),
    4: (246, 247, 247),
}


def template_match(img, template):
    """Template matching barebones."""
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return min_val, max_val, min_loc, max_loc


def extract_info_box(img: cv2.Mat, template: cv2.Mat) -> ...:
    """
    Get the info box from the screenshot.

    This approach does not scale, however, due to the stiff nature of template matching. While
    multi-scale template matching is a thing, it is much more expensive, especially when dealing
    with typical 1080p phone screenshots. Feature matching while works more generally (i.e. the
    template does not need to be regenerated), it's ignored since this is a utility script to aid
    data collection, not for gear importing. It *is* a possibility in the future. But, it is a
    possibility *in the future*, not now.

    Algorithm is definitely slow due to usage of `python-opencv` which is CPU-only. It could be sped
    up more if GPU-enabled from manually-compiled OpenCV but again, not needed.
    """
    # Template matching
    logger.info("Searching for info box.")
    template_height, template_width = template.shape[:2]  # Allow use of RGB template
    _, _, _, max_loc = template_match(img, template)

    top_left = max_loc
    bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
    logger.debug(f"Match found with bounding box {top_left} -> {bottom_right}.")

    # Cropping out the info box to reduce noise
    info_box = img[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]

    return info_box


def extract_gear_star(info_box: cv2.Mat, star_templates: dict[int, cv2.Mat]) -> int:
    """
    Get the gear star from the screenshot.

    This works by template matching the known states of gear star to the screenshot. Despite having
    to deal with 6 templates, it's faster than get_info_box() due to the smaller sizes of the
    template and the info box. To improve accuracy, thresholding is applied to both images to
    improve contrast since the gear star is a single color (save for the 6* star which is purple).
    The highest score of the each template is returned as that indicates confidence in the result.

    However, this approach can misidentify 5* and 6* gear, mainly due to the very similar colours
    of the "indicator star" after thresholding. Test runs had given as low as 0.00098 difference in
    final score between the two options, but usually this difference will hover around 0.03 to 0.05.
    In other cases, the difference is 0.1+ with the correct identification giving score on average
    0.93.

    Any improvement/rewrite to this is welcome.
    """
    logger.info("Extracting gear star.")

    scores = {}
    for star_count, template in star_templates.items():
        _, max_val, _, _ = template_match(info_box, template)
        scores[star_count] = max_val
        logger.debug(f"Template for {star_count}* scored {max_val}.")

    star = max(scores.keys(), key=scores.get)
    logger.info(
        f"Gear star detect as {star}* (confidence {scores[star] * 100 :05.4f}%)"
    )

    return star


def extract_substat_rarity(info_box: cv2.Mat) -> list[int]:
    """Extract substats' rarity via pixel-checking."""
    logger.info("Extracting substat rarity.")

    result = {}
    for i, substat in enumerate(("SUBSTAT_1", "SUBSTAT_2", "SUBSTAT_3", "SUBSTAT_4")):
        # Extract color of pixel
        x, y = map(int, os.environ.get(substat).split(","))
        base_rgb = color.get_rgb(info_box, x, y)
        logger.debug(f"Color of {substat} is {base_rgb}.")

        # Loop over rarity color and calculate distance
        scores = {}
        for rarity, target_rgb in RARITY_COLORS.items():
            distance = color.color_distance(base_rgb, target_rgb)
            scores[rarity] = distance
            logger.debug(
                f"Color distance from base to target {target_rgb} is {distance}."
            )

        # Get rarity. CIEDE2000 should guarantee the closest color is the correct one.
        rarity = min(scores.keys(), key=scores.get)
        logger.info(
            f"Substat {i + 1} rarity detected as {constants.RARITY_GRADE_MAPPING[rarity]}"
        )

        if rarity == 4:
            logger.debug("White substat detected. Discarding")
        else:
            result[i] = rarity

    return result
