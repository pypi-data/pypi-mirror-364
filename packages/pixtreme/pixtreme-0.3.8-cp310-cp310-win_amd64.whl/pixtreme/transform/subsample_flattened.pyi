from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
import numpy as np
import typing
__all__ = ['cp', 'create_output_order_indices', 'gather_kernel', 'gather_kernel_code', 'np', 'simple_copy_kernel', 'simple_copy_kernel_code', 'subsample_image_back_flattened', 'subsample_image_back_gather']
def create_output_order_indices(batch_shape, dim):
    """
    出力順序に合わせたインデックスマップを作成
    """
def subsample_image_back_flattened(subsampled_images: cp.ndarray | list[cp.ndarray], dim: int) -> cp.ndarray:
    """
    1次元化による最適化版のsubsample_image_back
    
        Args:
            subsampled_images: Batch tensor with shape (N, C, H, W) where N = dim*dim or a list of images[H, W, C].
            dim: Block size used in the original subsampling
    
        Returns:
            Reconstructed image with shape (H*dim, W*dim, C)
        
    """
def subsample_image_back_gather(subsampled_images: cp.ndarray | list[cp.ndarray], dim: int) -> cp.ndarray:
    """
    Gather操作を使用した最適化版
    
        インデックスの並べ替えをせず、直接gather操作でデータを収集
        
    """
__test__: dict = {}
_index_cache: dict = {}
gather_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
gather_kernel_code: str = '\nextern "C" __global__ void gather_kernel(\n    const float* __restrict__ input,\n    float* __restrict__ output,\n    const long long* __restrict__ indices,\n    const int total_elements\n) {\n    const int tid = blockIdx.x * blockDim.x + threadIdx.x;\n    if (tid >= total_elements) return;\n    \n    // インデックスを使用してgather操作\n    output[tid] = input[indices[tid]];\n}\n'
simple_copy_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
simple_copy_kernel_code: str = '\nextern "C" __global__ void simple_copy_kernel(\n    const float* __restrict__ input,\n    float* __restrict__ output,\n    const int total_elements\n) {\n    const int tid = blockIdx.x * blockDim.x + threadIdx.x;\n    if (tid >= total_elements) return;\n    \n    // 単純なメモリコピー\n    output[tid] = input[tid];\n}\n'
