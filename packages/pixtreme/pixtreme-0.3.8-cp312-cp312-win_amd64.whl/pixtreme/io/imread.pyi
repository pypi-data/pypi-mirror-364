import Imath as Imath
import OpenEXR as OpenEXR
from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cv2 as cv2
import numpy as np
from nvidia import nvimgcodec
import os as os
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.utils.dtypes import to_float16
from pixtreme.utils.dtypes import to_float32
from pixtreme.utils.dtypes import to_uint16
from pixtreme.utils.dtypes import to_uint8
__all__ = ['Imath', 'OpenEXR', 'bgr_to_rgb', 'cp', 'cv2', 'imread', 'np', 'nvimgcodec', 'os', 'rgb_to_bgr', 'to_float16', 'to_float32', 'to_uint16', 'to_uint8']
def imread(input_path: str, dtype: str = 'fp32', swap_rb = False, is_nvimgcodec = False) -> cp.ndarray:
    """
    
        Read an image from a file into a CuPy array.
    
        Args:
            input_path (str): Path to the image file.
            swap_rb (bool): If True, the image will be read with red and blue channels swapped. Default is False.
            is_nvimgcodec (bool): If True, use NVIDIA's nvimgcodec for reading the image. Default is False.
        Returns:
            cp.ndarray: The image as a CuPy array.
        Raises:
            FileNotFoundError: If the image file does not exist.
        
    """
__test__: dict = {}
