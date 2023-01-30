from typing import Generator

import cv2
import numpy as np
from loguru import logger
from tqdm import tqdm

from agf_toolkit import templates
from agf_toolkit.processor.image import rescale, template_match


def _generate_scaling_factors(lower_bound: float, upper_bound: float, max_step: int) -> Generator[float, None, None]:
    """Return a scaling factor from the upper bound to the lower bound at a given step."""
    yield from list(np.linspace(lower_bound, upper_bound, max_step))[::-1]


def auto_calibrate_scale(
    screenshot: np.ndarray[int, np.dtype[np.generic]],
    rounds: int = 3,
    scaling_lower_bound: float = 0.8,
    scaling_upper_bound: float = 1.2,
    scaling_step: int = 20,
    _current_scale: float = None,
) -> float:
    """
    Recursively calibrate the screenshot to maximise template fit.

    Note:
        Argument `_first_step` and `_current_scale` are for internal use only:
            - `_first_step` is for determining whether the screenshot should be rescaled to 1080-pixel wide.
            - `_current_scale` is for keeping track of the current best scaling factor at each recursive level.
    """
    screenshot_umat = cv2.UMat(screenshot)
    template_umat = cv2.UMat(templates.INFO_BOX)

    # Set up scaling factors
    if _current_scale is None:  # First step detection
        initial_scale = screenshot.shape[0] / 1080
        logger.debug(f"Screenshot normalised to 1080-pixel height (initial scale: {initial_scale:.2f})")
        factors = _generate_scaling_factors(
            scaling_lower_bound * initial_scale, scaling_upper_bound * initial_scale, scaling_step
        )
    else:
        factors = _generate_scaling_factors(
            scaling_lower_bound * _current_scale, scaling_upper_bound * _current_scale, scaling_step
        )

    # Iterate through scaling factors
    logger.info(f"Calibrating scale... {rounds} round(s) left.")
    scores = {}
    for scaling_factor in tqdm(factors):
        rescaled_screenshot_umat: cv2.UMat = rescale(screenshot_umat, scaling_factor)
        scaled_h, scaled_w = rescaled_screenshot_umat.get().shape[:2]

        if not (
            scaled_h < templates.INFO_BOX.shape[0] or scaled_w < templates.INFO_BOX.shape[1]
        ):  # Skip if scaled image is smaller than template
            _, scores[scaling_factor], _, _ = template_match(rescaled_screenshot_umat, template_umat)

    best_scaling_factor = max(scores, key=scores.get)  # type: ignore
    logger.debug(
        f"Best scaling factor as of current round: {best_scaling_factor:05.4f} "
        f"at {scores[best_scaling_factor] * 100:05.4f}%"
    )

    if rounds == 1:
        return best_scaling_factor

    return auto_calibrate_scale(
        screenshot=screenshot,
        rounds=rounds - 1,
        scaling_lower_bound=scaling_lower_bound,
        scaling_upper_bound=scaling_upper_bound,
        _current_scale=best_scaling_factor,
    )
