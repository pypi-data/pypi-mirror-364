import os
import numpy as np

CUDA_AVAILABLE = False
try:
    import cupy as cp
    CUDA_AVAILABLE = True
except ImportError:
    pass

def get_array_module(x):
    """Get the appropriate array module (numpy or cupy) for the input."""
    return cp if CUDA_AVAILABLE and hasattr(x, '__cuda_array_interface__') else np

def to_cpu(x):
    """Convert array to CPU numpy array."""
    if CUDA_AVAILABLE and hasattr(x, '__cuda_array_interface__'):
        return cp.asnumpy(x)
    return x

def to_gpu(x):
    """Convert array to GPU cupy array."""
    if not CUDA_AVAILABLE:
        raise RuntimeError("CUDA is not available")
    if isinstance(x, np.ndarray):
        return cp.asarray(x)
    return x