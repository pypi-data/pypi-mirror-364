from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
import typing
__all__ = ['cp', 'reconstruct_optimized_kernel', 'reconstruct_optimized_kernel_code', 'subsample_image', 'subsample_image_back']
def subsample_image(image: cp.ndarray, dim: int) -> list[cp.ndarray]:
    """
    Perform interleaved subsampling of an image without for loops.
    
        Args:
            image: Input image (cp.ndarray) with shape (height, width) or (height, width, channels).
            dim: Block size for subsampling.
    
        Returns:
            List of interleaved subsampled images.
        
    """
def subsample_image_back(subsampled_images: cp.ndarray | list[cp.ndarray], dim: int) -> cp.ndarray:
    """
    Ultra-optimized reconstruction using single-pass kernel.
    
        Args:
            subsampled_images: Batch tensor with shape (N, C, H, W) where N = dim*dim or a list of images[H, W, C].
            dim: Block size used in the original subsampling
    
        Returns:
            Reconstructed image with shape (H*dim, W*dim, C)
        
    """
__test__: dict = {}
reconstruct_optimized_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
reconstruct_optimized_kernel_code: str = '\nextern "C" __global__ void reconstruct_optimized_kernel(\n    const float* __restrict__ input,  // NCHW format\n    float* __restrict__ output,       // HWC format\n    const int batch_size,\n    const int channels,\n    const int input_height,\n    const int input_width,\n    const int output_height,\n    const int output_width,\n    const int dim\n) {\n    // Use 1D indexing for better performance\n    const int tid = blockIdx.x * blockDim.x + threadIdx.x;\n    const int total_elements = output_height * output_width * channels;\n    \n    if (tid >= total_elements) return;\n    \n    // Decode output position\n    const int c = tid % channels;\n    const int xy = tid / channels;\n    const int x = xy % output_width;\n    const int y = xy / output_width;\n    \n    // Calculate which subsample and position\n    const int dy = y % dim;\n    const int dx = x % dim;\n    const int subsample_idx = dy * dim + dx;\n    const int y_in = y / dim;\n    const int x_in = x / dim;\n    \n    // Read from NCHW input\n    const int idx_in = subsample_idx * channels * input_height * input_width +\n                      c * input_height * input_width +\n                      y_in * input_width + x_in;\n    \n    // Write to output\n    output[tid] = input[idx_in];\n}\n'
