from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cv2 as cv2
import numpy as np
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.utils.dtypes import to_float16
from pixtreme.utils.dtypes import to_float32
from pixtreme.utils.dtypes import to_uint16
from pixtreme.utils.dtypes import to_uint8
__all__ = ['bgr_to_rgb', 'cp', 'cv2', 'imdecode', 'np', 'to_float16', 'to_float32', 'to_uint16', 'to_uint8']
def imdecode(src: bytes, dtype: str = 'fp32', swap_rb: bool = False) -> cp.ndarray:
    """
    
        Decode an image from a bytes object into a CuPy array.
    
        Args:
            src (bytes): The input image data as bytes.
            dtype (str): The desired data type for the output array. Default is "fp32".
            swap_rb (bool): If True, the image will be converted from BGR to RGB after decoding. Default is False (BGR).
        Returns:
            cp.ndarray: The image as a CuPy array.
        
    """
__test__: dict = {}
