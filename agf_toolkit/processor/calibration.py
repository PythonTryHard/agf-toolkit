import cv2
import numpy as np
from loguru import logger
from tqdm import tqdm

from agf_toolkit import templates
from agf_toolkit.processor.image import calculate_rescaled_size, rescale, template_match


def _generate_scaling_factors(lower_bound: float, upper_bound: float, max_step: int) -> list[float]:
    """Return a scaling factor from the upper bound to the lower bound at a given step."""
    return list(np.linspace(lower_bound, upper_bound, max_step))[::-1]


# pylint: disable=too-many-locals
def calibrate_scale(
    screenshot: np.ndarray[int, np.dtype[np.generic]],
    rounds: int = 3,
    initial_bound_coefficient: float = 1.3,
    bound_constriction_coefficient: float = 0.5,
    sweep_steps: int | list[int] = 50,
    _current_state: tuple[float, float, float] = None,
):
    """
    Recursively calibrate the screenshot to maximise template fit.

    Note:
        Argument `_first_step` and `_current_scale` are for internal use only:
            - `_first_step` is for determining whether the screenshot should be rescaled to 1080-pixel wide.
            - `_current_scale` is for keeping track of the current best scaling factor at each recursive level.
    """
    if initial_bound_coefficient < 1:
        raise ValueError("Initial bound coefficient must be greater than 1.")
    if not 0 < bound_constriction_coefficient < 1:
        raise ValueError("Bound constriction coefficient must be between 0 and 1.")

    if isinstance(sweep_steps, list):
        if len(sweep_steps) != rounds:
            raise ValueError("Length of sweep step list must match number of rounds.")
        recursive_sweep_steps = sweep_steps.copy()  # Copy to prevent potential issues with mutating original arg.
        steps = recursive_sweep_steps.pop(0)
    else:
        steps = recursive_sweep_steps = sweep_steps  # type: ignore  # We can handle both int and list[int].

    # Preparation for the first calibration round
    if _current_state is None:
        initial_scale = 1080 / screenshot.shape[0]
        logger.debug(f"Screenshot normalised to 1080-pixel height (initial scale: {initial_scale:.2f})")

        scale_expansion_value = initial_scale * abs(1 - initial_bound_coefficient)

        scale_upper_bound = initial_scale + scale_expansion_value
        scale_lower_bound = max(0.01, initial_scale - scale_expansion_value)
        logger.debug(f"Initial scale expanded by {scale_expansion_value} to [{scale_upper_bound}, {scale_lower_bound}]")

    # Constrict sweep bounds for 2nd round and onwards
    else:
        previous_lower_bound, previous_best_scaling_factor, previous_upper_bound = _current_state
        bound_constriction_value = abs(previous_upper_bound - previous_lower_bound) * bound_constriction_coefficient / 2

        scale_upper_bound = previous_best_scaling_factor + bound_constriction_value
        scale_lower_bound = max(0.01, previous_best_scaling_factor - bound_constriction_value)
        logger.debug(
            f"Scale constricted by {bound_constriction_value} "
            f"from [{previous_lower_bound}, {previous_upper_bound}] "
            f"to [{scale_lower_bound}, {scale_upper_bound}]"
        )

    logger.info(f"Calibrating scale... {rounds} round(s) left.")
    screenshot_umat = cv2.UMat(screenshot)
    template_umat = cv2.UMat(templates.INFO_BOX)
    scores = {}
    for scaling_factor in tqdm(_generate_scaling_factors(scale_lower_bound, scale_upper_bound, steps)):
        resized_w, resized_h = calculate_rescaled_size(screenshot_umat, scaling_factor)

        if (resized_h, resized_w) < templates.INFO_BOX.shape[:2]:
            logger.debug(f"Factor {scaling_factor} results in screenshot smaller than template. Skipped.")
            continue  #  Skip if scaled image is smaller than template

        rescaled_screenshot_umat: cv2.UMat = rescale(screenshot_umat, target_w=resized_w, target_h=resized_h)
        _, score, _, _ = template_match(rescaled_screenshot_umat, template_umat)

        scores[scaling_factor] = score
        logger.debug(f"Resized with factor {scaling_factor} to size {resized_w}x{resized_h} for score of {score}")

    best_scaling_factor = max(scores, key=scores.get)  # type: ignore
    logger.debug(
        f"Best scaling factor as of current round: {best_scaling_factor:05.4f} "
        f"at {scores[best_scaling_factor] * 100:05.4f}%"
    )

    if rounds == 1:
        return best_scaling_factor

    return calibrate_scale(
        screenshot=screenshot,
        rounds=rounds - 1,
        initial_bound_coefficient=initial_bound_coefficient,
        bound_constriction_coefficient=bound_constriction_coefficient,
        sweep_steps=recursive_sweep_steps,
        _current_state=(scale_lower_bound, best_scaling_factor, scale_upper_bound),
    )
