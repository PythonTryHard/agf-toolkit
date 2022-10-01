import os

import cv2
import numpy as np
import skimage
from loguru import logger

from agequip_rw.utils import color


RARITY_COLORS = {
    "Yellow": (254, 205, 51),
    "Purple": (217, 169, 249),
    "Blue"  : (138, 199, 252),
    "Green" : (141, 223, 186),
    "White" : (246, 247, 247),
}


def template_match(img, template):
    """Template matching barebones."""
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return min_val, max_val, min_loc, max_loc


def crop(img, top_left, bottom_right):
    """Crop an image"""
    cropped = img[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]
    return cropped


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
    h, w = template.shape[:2]  # Allow use of RGB template
    _, _, _, max_loc = template_match(img, template)

    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    logger.debug(f"Match found with bounding box {top_left} -> {bottom_right}.")

    # Cropping out the info box to reduce noise
    info_box = crop(img, top_left, bottom_right)

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

    # Thresholding to (hopefully) improve contrast
    t_info_box = cv2.cvtColor(info_box, cv2.COLOR_BGR2GRAY)
    _, t_info_box = cv2.threshold(t_info_box, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Match against the 6 star templates and store the score and matching region
    scores = {}
    matches = {}
    for star_count, template in star_templates.items():
        h, w = template.shape[:2]
        t_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        _, t_template = cv2.threshold(t_template, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        _, max_val, _, max_loc = template_match(t_info_box, t_template)
        scores[star_count] = max_val
        logger.debug(f"Template for {star_count}* scored {max_val}.")

        match_region = crop(info_box, max_loc, (max_loc[0] + w, max_loc[1] + h))
        matches[star_count] = match_region

    star_order = list(sorted(scores.keys(), key=scores.get, reverse=True))  # Max first

    # Resolve ambiguity between 5* and 6* should that arise
    if star_order[:2] in ([5, 6], [6, 5]) and abs(scores[5] - scores[6]) < 0.035:
        logger.debug(f"Gear star is ambiguous between 5* and 6* with scores {scores[5]} and {scores[6]}. Resolving.")

        lab_match_region_6 = cv2.cvtColor(matches[6], cv2.COLOR_BGR2LAB)
        lab_known_6 = cv2.cvtColor(np.full_like(lab_match_region_6, (241, 142, 255)), cv2.COLOR_BGR2LAB)

        match_x, match_y = np.where(skimage.color.deltaE_ciede2000(lab_match_region_6, lab_known_6, kL=2) < 5)

        if len(tuple(zip(match_x, match_y))) > 10:  # Arbitrary threshold, but should be enough to have confidence
            star = 6
            logger.info(f"Gear star detect as {star}*")
        else:
            star = 5
            logger.info(f"Gear star detect as {star}*")

    else:
        star = star_order[0]
        logger.info(f"Gear star detect as {star}* (confidence {scores[star] * 100 :05.4f}%)")

    return star


def extract_sub_stat_rarity(info_box: cv2.Mat) -> tuple[str, dict[int, str]]:
    """
    Extract sub stats' rarity via pixel-checking.
    
    This also extract gear's rarity thanks to the sub stat count-gear rarity correlation.
    """
    logger.info("Extracting substat rarity.")

    result = {}
    for i, sub_stat in enumerate(("SUBSTAT_1", "SUBSTAT_2", "SUBSTAT_3", "SUBSTAT_4")):
        # Extract color of pixel
        x, y = map(int, os.environ.get(sub_stat).split(","))
        base_rgb = color.get_rgb(info_box, x, y)
        logger.debug(f"Color of {sub_stat} is {base_rgb}.")

        # Loop over rarity color and calculate distance
        scores = {}
        for rarity, target_rgb in RARITY_COLORS.items():
            distance = color.color_distance(base_rgb, target_rgb)
            scores[rarity] = distance
            logger.debug(f"Color distance from base to target {target_rgb} is {distance}.")

        # Get rarity. CIEDE2000 should guarantee the closest color is the correct one.
        rarity = min(scores.keys(), key=scores.get)

        if rarity == "White":
            logger.debug("White sub stat detected. Discarding")
        else:
            logger.info(f"Sub stat {i + 1} rarity detected as {rarity}")
            result[i] = rarity

    gear_rarity = list(RARITY_COLORS)[len(RARITY_COLORS) - len(result) - 1]
    logger.info(f"Gear rarity detected to be {gear_rarity}")

    return gear_rarity, result
