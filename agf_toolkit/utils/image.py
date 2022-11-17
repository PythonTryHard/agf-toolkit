from typing import Union

import cv2
import numpy as np


def rescale(
    img: Union[cv2.UMat, np.ndarray[int, np.dtype[np.generic]]], factor: float
) -> Union[cv2.UMat, np.ndarray[int, np.dtype[np.generic]]]:
    """Rescale an image by a given factor."""
    if isinstance(img, cv2.UMat):
        img_array = img.get()
    else:
        img_array = img

    img_h, img_w = img_array.shape[:2]

    scaled_h, scaled_w = int(img_h / factor), int(img_w / factor)
    resized = cv2.resize(img, (scaled_w, scaled_h))
    return resized
