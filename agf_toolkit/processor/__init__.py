import numpy as _np
from loguru import logger as _logger

from agf_toolkit import templates
from agf_toolkit.processor.constant import (
    GEAR_TYPE_MAPPING,
    RARITY_GRADE_MAPPING,
    SET_NAME_MAPPING,
    STAT_TYPE_MAPPING,
    STAT_TYPE_REGEX_MAPPING,
)
from agf_toolkit.processor.gear import Gear, Stat
from agf_toolkit.processor.image import (
    extract_gear_star,
    extract_info_box,
    extract_sub_stat_rarity,
)
from agf_toolkit.processor.text import (
    extract_gear_set,
    extract_gear_type,
    extract_main_stat,
    extract_sub_stats,
    extract_text,
)


def parse_screenshot(screenshot: _np.ndarray[int, _np.dtype[_np.generic]]) -> Gear:
    """Parse the screenshot into instance's attributes."""
    if screenshot is None:
        _logger.error("No screenshot found! Returning!")
        return Gear()

    img = extract_info_box(screenshot, templates.INFO_BOX)
    txt = extract_text(img)

    main_stat = extract_main_stat(txt)

    rarity, _sub_stat_rarity = extract_sub_stat_rarity(img)
    _sub_stat_data = extract_sub_stats(txt)
    sub_stats = tuple(Stat(*data, rarity) for data, rarity in zip(_sub_stat_data, _sub_stat_rarity.values()))

    star = extract_gear_star(img, templates.STARS)
    gear_set = extract_gear_set(txt)
    gear_type = extract_gear_type(txt)

    return Gear(
        gear_set=gear_set,
        gear_type=gear_type,
        rarity=rarity,
        star=star,
        main_stat=main_stat,
        sub_stats=sub_stats,
    )
