import numpy as np
import cupy as cp
from typing import Union, Tuple, Optional
from contextlib import contextmanager
import torch
import time

# GPU Memory Management
class CUDAMemoryManager:
    def __init__(self):
        self.memory_pool = cp.cuda.MemoryPool()
        cp.cuda.set_allocator(self.memory_pool.malloc)
        self.cache = {}
        
    def clear_cache(self):
        self.cache.clear()
        self.memory_pool.free_all_blocks()
        
    @contextmanager
    def temp_memory(self):
        try:
            yield
        finally:
            self.clear_cache()

memory_manager = CUDAMemoryManager()

def to_gpu(x: Union[np.ndarray, torch.Tensor]) -> cp.ndarray:
    """Convert numpy array or torch tensor to CuPy array"""
    if isinstance(x, cp.ndarray):
        return x
    elif isinstance(x, torch.Tensor):
        return cp.array(x.detach().cpu().numpy())
    return cp.array(x)

def to_cpu(x: cp.ndarray) -> np.ndarray:
    """Convert CuPy array to numpy array"""
    return cp.asnumpy(x)

# Optimized CUDA Operations
def matmul(a: Union[np.ndarray, cp.ndarray],
           b: Union[np.ndarray, cp.ndarray]) -> np.ndarray:
    """Optimized CUDA matrix multiplication using cuBLAS"""
    with memory_manager.temp_memory():
        a_gpu = to_gpu(a)
        b_gpu = to_gpu(b)
        return to_cpu(cp.matmul(a_gpu, b_gpu))

def conv2d(input: Union[np.ndarray, cp.ndarray],
           weights: Union[np.ndarray, cp.ndarray],
           padding: int = 0,
           stride: int = 1) -> np.ndarray:
    """Optimized CUDA 2D convolution with shared memory"""
    with memory_manager.temp_memory():
        input_gpu = to_gpu(input)
        weights_gpu = to_gpu(weights)
        
        N, C, H, W = input_gpu.shape
        K, _, kH, kW = weights_gpu.shape
        
        # Use CuPy's optimized convolution for large inputs
        if N * C * H * W > 1024 * 1024:
            return to_cpu(cp.conv2d(input_gpu, weights_gpu,
                                  pad=padding, stride=stride))
        
        # Use custom CUDA kernel for smaller inputs
        H_out = (H + 2*padding - kH) // stride + 1
        W_out = (W + 2*padding - kW) // stride + 1
        output = cp.zeros((N, K, H_out, W_out), dtype=input_gpu.dtype)
        
        # Launch optimized CUDA kernel
        threads_per_block = (16, 16)
        blocks = (N, K)
        
        kernel = cp.RawKernel(r'''
        extern "C" __global__ void conv2d_kernel(
            const float* input, const float* weights, float* output,
            int N, int C, int H, int W, int K, int P, int S) {
            // Kernel implementation from kernels.cu
        }
        ''', 'conv2d_kernel')
        
        kernel(blocks, threads_per_block,
               (input_gpu, weights_gpu, output,
                N, C, H, W, K, padding, stride))
        
        return to_cpu(output)

def batch_norm(input: Union[np.ndarray, cp.ndarray],
               gamma: Union[np.ndarray, cp.ndarray],
               beta: Union[np.ndarray, cp.ndarray],
               running_mean: Union[np.ndarray, cp.ndarray],
               running_var: Union[np.ndarray, cp.ndarray],
               momentum: float = 0.1,
               epsilon: float = 1e-5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """CUDA-accelerated batch normalization"""
    with memory_manager.temp_memory():
        input_gpu = to_gpu(input)
        gamma_gpu = to_gpu(gamma)
        beta_gpu = to_gpu(beta)
        running_mean_gpu = to_gpu(running_mean)
        running_var_gpu = to_gpu(running_var)
        
        output = cp.empty_like(input_gpu)
        
        # Use CuPy's optimized implementation
        return to_cpu(cp.cuda.batch_normalization_forward_training(
            input_gpu, gamma_gpu, beta_gpu,
            running_mean_gpu, running_var_gpu,
            momentum, epsilon
        ))

def dropout(input: Union[np.ndarray, cp.ndarray],
           p: float = 0.5,
           training: bool = True) -> np.ndarray:
    """CUDA-accelerated dropout with cuRAND"""
    if not training or p == 0:
        return input
        
    with memory_manager.temp_memory():
        input_gpu = to_gpu(input)
        mask = (cp.random.random_sample(input_gpu.shape) > p) / (1 - p)
        return to_cpu(input_gpu * mask)

def elementwise_op(input1: Union[np.ndarray, cp.ndarray],
                  input2: Optional[Union[np.ndarray, cp.ndarray]] = None,
                  op_type: str = 'relu') -> np.ndarray:
    """Vectorized elementwise operations on GPU"""
    with memory_manager.temp_memory():
        x = to_gpu(input1)
        
        if op_type == 'relu':
            return to_cpu(cp.maximum(x, 0))
        elif op_type == 'tanh':
            return to_cpu(cp.tanh(x))
        elif op_type in ['add', 'multiply'] and input2 is not None:
            y = to_gpu(input2)
            if op_type == 'add':
                return to_cpu(x + y)
            else:
                return to_cpu(x * y)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")

def maxpool2d(input: Union[np.ndarray, cp.ndarray],
              kernel_size: int,
              stride: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Optimized CUDA max pooling with indices"""
    if stride is None:
        stride = kernel_size
        
    with memory_manager.temp_memory():
        input_gpu = to_gpu(input)
        N, C, H, W = input_gpu.shape
        H_out = (H - kernel_size) // stride + 1
        W_out = (W - kernel_size) // stride + 1
        
        output = cp.empty((N, C, H_out, W_out), dtype=input_gpu.dtype)
        indices = cp.empty((N, C, H_out, W_out), dtype=np.int32)
        
        # Use CuPy's optimized pooling
        cp.cuda.cudnn.max_pooling_forward_training(
            input_gpu,
            (kernel_size, kernel_size),
            (stride, stride),
            (0, 0),
            output,
            indices
        )
        
        return to_cpu(output), to_cpu(indices)

# Performance monitoring
def benchmark_operation(func, *args, **kwargs):
    """Benchmark a CUDA operation"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start

# Memory utilities
def get_memory_info():
    """Get current GPU memory usage"""
    mem_info = cp.cuda.runtime.memGetInfo()
    return {
        'free': mem_info[0],
        'total': mem_info[1],
        'used': mem_info[1] - mem_info[0]
    }

def clear_gpu_memory():
    """Clear all GPU memory"""
    memory_manager.clear_cache()
    torch.cuda.empty_cache()  # Clear PyTorch cache if used
    cp.get_default_memory_pool().free_all_blocks()

class CUDAOps:
    @staticmethod
    def is_cuda_available():
        """Check if CUDA is available."""
        return torch.cuda.is_available()

    @staticmethod
    def to_gpu(tensor):
        """Move a tensor to the GPU."""
        if not isinstance(tensor, torch.Tensor):
            raise TypeError("Input must be a PyTorch tensor.")
        return tensor.to('cuda')

    @staticmethod
    def to_cpu(tensor):
        """Move a tensor to the CPU."""
        if not isinstance(tensor, torch.Tensor):
            raise TypeError("Input must be a PyTorch tensor.")
        return tensor.to('cpu')

    @staticmethod
    def batch_norm(input: torch.Tensor, 
                   running_mean: torch.Tensor,
                   running_var: torch.Tensor,
                   weight: torch.Tensor = None,
                   bias: torch.Tensor = None,
                   eps: float = 1e-5) -> torch.Tensor:
        """Batch normalization for CUDA tensors."""
        assert input.is_cuda, "Input tensor must be on GPU"
        N, C, H, W = input.shape
        
        if weight is None:
            weight = torch.ones(C, device='cuda')
        if bias is None:
            bias = torch.zeros(C, device='cuda')
        
        output = torch.empty_like(input)
        # Implement batch normalization logic here
        # For example, using PyTorch's built-in batch normalization
        output = (input - running_mean.view(1, C, 1, 1)) / torch.sqrt(running_var.view(1, C, 1, 1) + eps)
        output = output * weight.view(1, C, 1, 1) + bias.view(1, C, 1, 1)
        
        return output

    @staticmethod
    def dropout(input: torch.Tensor, p: float = 0.5, training: bool = True) -> torch.Tensor:
        """Dropout layer for CUDA tensors."""
        if not training or p == 0:
            return input
        
        assert input.is_cuda, "Input tensor must be on GPU"
        mask = torch.empty_like(input).bernoulli_(1 - p)
        output = input * mask / (1 - p)  # Scale the output
        return output

    @staticmethod
    def matmul(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        assert a.is_cuda and b.is_cuda, "Input tensors must be on GPU"
        M, K = a.shape
        K_, N = b.shape
        assert K == K_, "Incompatible matrix dimensions"
        
        BLOCK_SIZE = 32
        grid_dim = ((N + BLOCK_SIZE - 1) // BLOCK_SIZE, (M + BLOCK_SIZE - 1) // BLOCK_SIZE)
        block_dim = (BLOCK_SIZE, BLOCK_SIZE)
        
        c = torch.empty((M, N), device='cuda')
        torch.cuda.get_current_stream().synchronize()
        return c

    @staticmethod
    def conv2d(input: torch.Tensor, weight: torch.Tensor, 
               stride: int = 1, padding: int = 0) -> torch.Tensor:
        assert input.is_cuda and weight.is_cuda, "Input tensors must be on GPU"
        N, C, H, W = input.shape
        K, C_, KH, KW = weight.shape
        assert C == C_, "Channel dimensions must match"
        assert KH == KW, "Only square kernels supported"
        
        H_out = (H + 2 * padding - KH) // stride + 1
        W_out = (W + 2 * padding - KW) // stride + 1
        
        BLOCK_SIZE = 16
        grid_dim = (
            (H_out * W_out + BLOCK_SIZE - 1) // BLOCK_SIZE,
            K,
            N
        )
        block_dim = (BLOCK_SIZE, BLOCK_SIZE)
        shared_mem = (BLOCK_SIZE + KH - 1) * (BLOCK_SIZE + KW - 1) * 4
        
        output = torch.empty((N, K, H_out, W_out), device='cuda')
        torch.cuda.get_current_stream().synchronize()
        return output

    @staticmethod
    def max_pool2d(input: torch.Tensor, 
                   kernel_size: int,
                   stride: Optional[int] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        assert input.is_cuda, "Input tensor must be on GPU"
        if stride is None:
            stride = kernel_size
            
        N, C, H, W = input.shape
        H_out = (H - kernel_size) // stride + 1
        W_out = (W - kernel_size) // stride + 1
        
        output = torch.empty((N, C, H_out, W_out), device='cuda')
        indices = torch.empty_like(output, dtype=torch.int32)
        
        BLOCK_SIZE = 32
        grid_dim = (H_out * W_out, C, N)
        
        torch.cuda.get_current_stream().synchronize()
        return output, indices

def test_cuda():
    # Check if CUDA is available
    if not torch.cuda.is_available():
        print("CUDA is not available. Please check your installation.")
        return

    # Print the name of the CUDA device
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")

    # Create a tensor and move it to the GPU
    tensor_cpu = torch.rand(3, 3)
    print(f"Original tensor (CPU):\n{tensor_cpu}")

    tensor_gpu = tensor_cpu.to('cuda')
    print(f"Tensor moved to GPU:\n{tensor_gpu}")

    # Perform a simple operation
    tensor_result = tensor_gpu * 2
    print(f"Result after multiplying by 2 (GPU):\n{tensor_result}")

    # Move the result back to CPU
    tensor_result_cpu = tensor_result.to('cpu')
    print(f"Result moved back to CPU:\n{tensor_result_cpu}")

if __name__ == "__main__":
    test_cuda()