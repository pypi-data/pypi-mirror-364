from openarchx.core.tensor import Tensor
import numpy as np
import time

def benchmark_matmul(size=1000, device='cpu'):
    """Benchmark matrix multiplication on CPU vs GPU"""
    # Create random matrices
    a = np.random.randn(size, size).astype(np.float32)
    b = np.random.randn(size, size).astype(np.float32)
    
    # Convert to tensors
    ta = Tensor(a, device=device)
    tb = Tensor(b, device=device)
    
    # Warmup
    _ = ta @ tb
    
    # Benchmark
    start = time.time()
    for _ in range(10):
        c = ta @ tb
    end = time.time()
    
    return (end - start) / 10

def test_cuda_ops():
    """Test basic CUDA operations"""
    try:
        # Test tensor creation and device movement
        a = Tensor(np.array([[1, 2], [3, 4]]), device='cuda')
        b = Tensor(np.array([[5, 6], [7, 8]]), device='cuda')
        
        print("CUDA Tensor Operations Test:")
        print("----------------------------")
        
        # Test addition
        c = a + b
        print(f"Addition result:\n{c}")
        
        # Test matrix multiplication
        d = a @ b
        print(f"\nMatrix multiplication result:\n{d}")
        
        # Test element-wise multiplication
        e = a * b
        print(f"\nElement-wise multiplication result:\n{e}")
        
        # Benchmark large matrix multiplication
        print("\nBenchmarking matrix multiplication:")
        cpu_time = benchmark_matmul(size=1000, device='cpu')
        gpu_time = benchmark_matmul(size=1000, device='cuda')
        
        print(f"CPU average time: {cpu_time:.4f} seconds")
        print(f"GPU average time: {gpu_time:.4f} seconds")
        print(f"Speedup: {cpu_time/gpu_time:.2f}x")
        
    except Exception as e:
        print(f"Error during CUDA test: {str(e)}")

if __name__ == "__main__":
    test_cuda_ops()