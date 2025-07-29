from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cv2 as cv2
import numpy as np
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.utils.dtypes import to_uint16
from pixtreme.utils.dtypes import to_uint8
__all__ = ['cp', 'cv2', 'imencode', 'np', 'rgb_to_bgr', 'to_uint16', 'to_uint8']
def imencode(image: cp.ndarray, ext: str = '.png', param: int = -1, swap_rb: bool = False) -> bytes:
    """
    
        Encode an image to a bytes object from a CuPy array.
    
        Args:
            image (cp.ndarray): The input image as a CuPy array.
            format (str): The image format to encode. Default is "png".
            param (int): Optional parameter for image encoding.
            swap_rb (bool): If True, the image will be encoded with red and blue channels swapped. Default is False.
        Returns:
            bytes: The encoded image as bytes.
        
    """
__test__: dict = {}
