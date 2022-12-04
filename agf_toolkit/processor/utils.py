import numpy as np
from loguru import logger

from agf_toolkit import templates
from agf_toolkit.processor.gear import Gear, Stat
from agf_toolkit.processor.image import (
    extract_gear_star,
    extract_info_box,
    extract_sub_stat_rarity,
)
from agf_toolkit.processor.text import (
    extract_gear_set,
    extract_gear_type,
    extract_stats,
    extract_text,
)


def parse_screenshot(screenshot: np.ndarray[int, np.dtype[np.generic]]) -> Gear:
    """Parse the screenshot into instance's attributes."""
    if screenshot is None:
        logger.error("No screenshot found! Returning!")
        return Gear()

    img = extract_info_box(screenshot, templates.INFO_BOX)
    txt = extract_text(img)

    # As much as I hate it, I have to do this. Currently, there's no concrete data on rarity threshold except for 6-star
    # equipments. Any half-arsed attempt to accommodate 6-star with generic detection will result in code bloat without
    # actually reconciling sub stats' rarity detection and sub stats' stat_value detection. Until then, we make do.
    rarity, _sub_stat_rarity = extract_sub_stat_rarity(img)
    _stat_rarity = (None, *_sub_stat_rarity.values())
    _stat_data = extract_stats(txt)
    main_stat, *sub_stats = tuple(Stat(*data, rarity) for data, rarity in zip(_stat_data, _stat_rarity))

    star = extract_gear_star(img, templates.STARS)
    gear_set = extract_gear_set(txt)
    gear_type = extract_gear_type(txt)

    return Gear(
        gear_set=gear_set,
        gear_type=gear_type,
        gear_rarity=rarity,
        gear_star=star,
        main_stat=main_stat,
        sub_stats=sub_stats,
    )
