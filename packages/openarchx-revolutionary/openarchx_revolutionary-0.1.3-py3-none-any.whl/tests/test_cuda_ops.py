import unittest
import numpy as np
import torch
import cupy as cp
from openarchx.cuda import cuda_ops
import time

class TestCUDAOps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize random seed for reproducibility
        np.random.seed(42)
        torch.manual_seed(42)
        cp.random.seed(42)
        
    def setUp(self):
        cuda_ops.clear_gpu_memory()
        
    def tearDown(self):
        cuda_ops.clear_gpu_memory()
        
    def test_matmul(self):
        # Test various matrix sizes
        sizes = [(32, 32, 32), (128, 64, 256), (512, 512, 512)]
        
        for m, k, n in sizes:
            a = np.random.randn(m, k).astype(np.float32)
            b = np.random.randn(k, n).astype(np.float32)
            
            # NumPy result
            expected = np.matmul(a, b)
            
            # CUDA result
            result, time_taken = cuda_ops.benchmark_operation(
                cuda_ops.matmul, a, b
            )
            
            np.testing.assert_allclose(result, expected, rtol=1e-5)
            print(f"MatMul {m}x{k} @ {k}x{n} - Time: {time_taken:.4f}s")
            
    def test_conv2d(self):
        batch_size = 32
        in_channels = 3
        out_channels = 16
        input_size = 32
        kernel_size = 3
        
        input_data = np.random.randn(
            batch_size, in_channels, input_size, input_size
        ).astype(np.float32)
        
        weights = np.random.randn(
            out_channels, in_channels, kernel_size, kernel_size
        ).astype(np.float32)
        
        # PyTorch result for validation
        torch_input = torch.from_numpy(input_data)
        torch_weights = torch.from_numpy(weights)
        expected = torch.nn.functional.conv2d(
            torch_input, torch_weights, padding=1
        ).numpy()
        
        # CUDA result
        result, time_taken = cuda_ops.benchmark_operation(
            cuda_ops.conv2d, input_data, weights, padding=1
        )
        
        np.testing.assert_allclose(result, expected, rtol=1e-4)
        print(f"Conv2D - Time: {time_taken:.4f}s")
        
    def test_batch_norm(self):
        batch_size = 32
        channels = 64
        height = 32
        width = 32
        
        input_data = np.random.randn(
            batch_size, channels, height, width
        ).astype(np.float32)
        
        gamma = np.random.randn(channels).astype(np.float32)
        beta = np.random.randn(channels).astype(np.float32)
        running_mean = np.zeros(channels, dtype=np.float32)
        running_var = np.ones(channels, dtype=np.float32)
        
        # PyTorch result for validation
        torch_input = torch.from_numpy(input_data)
        torch_gamma = torch.from_numpy(gamma)
        torch_beta = torch.from_numpy(beta)
        
        expected = torch.nn.functional.batch_norm(
            torch_input,
            torch.from_numpy(running_mean),
            torch.from_numpy(running_var),
            torch_gamma,
            torch_beta,
            training=True
        ).numpy()
        
        # CUDA result
        result, time_taken = cuda_ops.benchmark_operation(
            cuda_ops.batch_norm,
            input_data, gamma, beta,
            running_mean, running_var
        )
        
        np.testing.assert_allclose(result, expected, rtol=1e-4)
        print(f"BatchNorm - Time: {time_taken:.4f}s")
        
    def test_dropout(self):
        shape = (32, 1024)
        input_data = np.random.randn(*shape).astype(np.float32)
        p = 0.5
        
        # Test training mode
        result, time_taken = cuda_ops.benchmark_operation(
            cuda_ops.dropout, input_data, p, True
        )
        
        # Verify dropout mask properties
        mask = (result != 0).astype(np.float32)
        dropout_ratio = 1 - (mask.sum() / mask.size)
        self.assertAlmostEqual(dropout_ratio, p, delta=0.1)
        
        # Test eval mode (should return input unchanged)
        result = cuda_ops.dropout(input_data, p, training=False)
        np.testing.assert_array_equal(result, input_data)
        
        print(f"Dropout - Time: {time_taken:.4f}s")
        
    def test_elementwise_ops(self):
        shape = (1024, 1024)
        a = np.random.randn(*shape).astype(np.float32)
        b = np.random.randn(*shape).astype(np.float32)
        
        # Test ReLU
        expected = np.maximum(a, 0)
        result, time_taken = cuda_ops.benchmark_operation(
            cuda_ops.elementwise_op, a, op_type='relu'
        )
        np.testing.assert_allclose(result, expected)
        print(f"ReLU - Time: {time_taken:.4f}s")
        
        # Test Add
        expected = a + b
        result, time_taken = cuda_ops.benchmark_operation(
            cuda_ops.elementwise_op, a, b, op_type='add'
        )
        np.testing.assert_allclose(result, expected)
        print(f"Add - Time: {time_taken:.4f}s")
        
    def test_maxpool2d(self):
        batch_size = 32
        channels = 16
        height = 32
        width = 32
        kernel_size = 2
        stride = 2
        
        input_data = np.random.randn(
            batch_size, channels, height, width
        ).astype(np.float32)
        
        # PyTorch result for validation
        torch_input = torch.from_numpy(input_data)
        expected, indices = torch.nn.functional.max_pool2d(
            torch_input,
            kernel_size,
            stride=stride,
            return_indices=True
        )
        expected = expected.numpy()
        
        # CUDA result
        result, time_taken = cuda_ops.benchmark_operation(
            cuda_ops.maxpool2d,
            input_data,
            kernel_size,
            stride
        )
        
        np.testing.assert_allclose(result[0], expected, rtol=1e-5)
        print(f"MaxPool2D - Time: {time_taken:.4f}s")
        
    def test_memory_management(self):
        # Test memory info
        initial_mem = cuda_ops.get_memory_info()
        
        # Allocate some memory
        shape = (1024, 1024)
        data = np.random.randn(*shape).astype(np.float32)
        _ = cuda_ops.to_gpu(data)
        
        mid_mem = cuda_ops.get_memory_info()
        self.assertGreater(mid_mem['used'], initial_mem['used'])
        
        # Clear memory
        cuda_ops.clear_gpu_memory()
        final_mem = cuda_ops.get_memory_info()
        
        # Memory should be freed
        self.assertLessEqual(final_mem['used'], initial_mem['used'])

if __name__ == '__main__':
    unittest.main()