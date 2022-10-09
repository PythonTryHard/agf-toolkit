import os

import cv2
import numpy as np
import skimage
from loguru import logger

from agf_toolkit.utils import color

AMBIGUITY_THRESHOLD = 0.05
PURPLE_RARITY_STAR = (241, 142, 255)
RARITY_COLORS = {
    "Yellow": (254, 205, 51),
    "Purple": (217, 169, 249),
    "Blue": (138, 199, 252),
    "Green": (141, 223, 186),
    "White": (246, 247, 247),
}
CIEDE_PIXEL_THRESHOLD = 10


def template_match(img, template):
    """Template matching barebones."""
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return min_val, max_val, min_loc, max_loc


def crop(img, top_left, bottom_right):
    """Crop an image"""
    cropped = img[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]
    return cropped


def extract_info_box(
    img: np.ndarray[int, np.dtype[np.generic]], template: np.ndarray[int, np.dtype[np.generic]]
) -> np.ndarray[int, np.dtype[np.generic]]:
    """
    Get the info box from the screenshot.

    This approach does not scale, however, due to the stiff nature of template matching. While
    multiscale template matching is a thing, it is much more expensive, especially when dealing
    with typical 1080p phone screenshots. Feature matching while works more generally (i.e. the
    template does not need to be regenerated), it's ignored since this is a utility script to aid
    data collection, not for gear importing. It *is* a possibility in the future. But, it is a
    possibility *in the future*, not now.

    Algorithm is definitely slow due to usage of `python-opencv` which is CPU-only. It could be sped
    up more if GPU-enabled from manually-compiled OpenCV but again, not needed.
    """
    # Template matching
    logger.info("Searching for info box.")
    template_h, template_y = template.shape[:2]  # Allow use of RGB template
    _, _, _, max_loc = template_match(img, template)

    top_left = max_loc
    bottom_right = (top_left[0] + template_y, top_left[1] + template_h)
    logger.debug(f"Match found with bounding box {top_left} -> {bottom_right}.")

    # Cropping out the info box to reduce noise
    info_box = crop(img, top_left, bottom_right)

    return info_box


def extract_gear_star(
    info_box: np.ndarray[int, np.dtype[np.generic]], star_templates: dict[int, np.ndarray[int, np.dtype[np.generic]]]
) -> int:
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
    _, t_info_box = cv2.threshold(
        cv2.cvtColor(info_box, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )

    # Match against the 6-star templates and store the score and matching region
    match = {}
    for star_count, template in star_templates.items():
        template_h, template_w = template.shape[:2]

        _, thresh_template = cv2.threshold(
            cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )

        _, max_val, _, max_loc = template_match(t_info_box, thresh_template)
        logger.debug(f"Template for {star_count}* scored {max_val * 100 :05.4f}%.")

        match_region = crop(info_box, max_loc, (max_loc[0] + template_w, max_loc[1] + template_h))
        match[star_count] = {"score": max_val, "region": match_region}

    # Sort max first
    star_order = list(sorted(match, key=lambda x: x[0], reverse=True))  # type: ignore

    # Resolve ambiguity between 5* and 6* should that arise
    if set(star_order[:2]) == {5, 6} and (delta := abs(match[5]["score"] - match[6]["score"])) < AMBIGUITY_THRESHOLD:
        logger.debug(f"Gear star is ambiguous between 5* and 6* with delta {delta * 100 :05.4f}%. Resolving.")
        return resolve_5_6_ambiguity(match_region_6_star=match[6]["region"])

    detected_star = star_order[0]
    logger.info(f"Gear star detect as {detected_star}* (confidence {match[detected_star]['score'] * 100 :05.4f}%)")
    return detected_star


def resolve_5_6_ambiguity(match_region_6_star: np.ndarray[int, np.dtype[np.generic]]) -> int:
    """Resolve 5-star 6-star ambiguity"""
    lab_match_region_6 = cv2.cvtColor(match_region_6_star, cv2.COLOR_BGR2LAB)
    lab_known_6 = cv2.cvtColor(np.full_like(lab_match_region_6, PURPLE_RARITY_STAR), cv2.COLOR_BGR2LAB)

    logger.debug(f"Calculating delta between match region and known 6* color {PURPLE_RARITY_STAR}.")
    match_x, match_y = np.where(skimage.color.deltaE_ciede2000(lab_match_region_6, lab_known_6, kL=2) < 5)

    match_pixel_count = len(tuple(zip(match_x, match_y)))
    logger.debug(f"Match region has {match_pixel_count}/{CIEDE_PIXEL_THRESHOLD} pixels matching known 6* color.")

    if match_pixel_count > CIEDE_PIXEL_THRESHOLD:  # Arbitrary threshold, but should be enough to have confidence
        logger.info("Gear star detect as 6*")
        return 6

    logger.info("Gear star detect as 5*")
    return 5


def extract_sub_stat_rarity(info_box: np.ndarray[int, np.dtype[np.generic]]) -> tuple[str, dict[int, str]]:
    """
    Extract sub stats' rarity via pixel-checking.

    This also extract gear's rarity thanks to the sub stat count-gear rarity correlation.
    """
    logger.info("Extracting sub stat rarity.")

    result = {}
    for i, sub_stat in enumerate(("SUB_STAT_1", "SUB_STAT_2", "SUB_STAT_3", "SUB_STAT_4")):
        # Extract color of pixel, type-check ignored since we verified in toolkit's __init__.py already
        coord_x, coord_y = map(int, os.environ.get(sub_stat).split(","))  # type: ignore
        base_rgb = color.get_rgb(info_box, coord_x, coord_y)
        logger.debug(f"Color of {sub_stat} is {base_rgb}.")

        # Loop over rarity color and calculate distance
        scores = {}
        for rarity, target_rgb in RARITY_COLORS.items():
            distance = color.color_distance(base_rgb, target_rgb)
            scores[rarity] = distance
            logger.debug(f"Delta-E to {rarity}-rarity {target_rgb} is {distance :05.4f}.")

        # Get rarity. CIEDE2000 should guarantee the closest color is the correct one.
        rarity = min(scores, key=scores.get)  # type: ignore

        if rarity == "White":
            logger.debug("White sub stat detected. Discarding")
        else:
            logger.info(f"Sub stat {i + 1} rarity detected as {rarity}")
            result[i] = rarity

    gear_rarity = list(RARITY_COLORS)[len(RARITY_COLORS) - len(result) - 1]
    logger.info(f"Gear rarity detected to be {gear_rarity}")

    return gear_rarity, result
