import numpy as np
from openarchx.core.tensor import Tensor
import cupy as cp

def is_cuda_available():
    """Check if CUDA is available."""
    return cp.cuda.is_available()

def test_cuda():
    # Check if CUDA is available
    if not is_cuda_available():
        print("CUDA is not available. Please check your installation.")
        return

    # Print the name of the CUDA device
    print(f"CUDA device: {cp.cuda.get_device_name(0)}")

    # Create a tensor and move it to the GPU
    tensor_cpu = np.random.rand(3, 3)
    print(f"Original tensor (CPU):\n{tensor_cpu}")

    tensor_gpu = Tensor(tensor_cpu, device='cuda')
    print(f"Tensor moved to GPU:\n{tensor_gpu.data}")

    # Perform a simple operation
    tensor_result = tensor_gpu.data * 2
    print(f"Result after multiplying by 2 (GPU):\n{tensor_result}")

    # Move the result back to CPU
    tensor_result_cpu = tensor_gpu.cpu()
    print(f"Result moved back to CPU:\n{tensor_result_cpu.data}")

def test_cuda_operations():
    if is_cuda_available():
        print("CUDA is available.")
        # Create a tensor and perform operations
        tensor = Tensor(np.random.rand(3, 3), device='cuda')
        print("Tensor on GPU:", tensor.data)
        # Perform some operations
        result = tensor.data * 2
        print("Result after operation:", result)
    else:
        print("CUDA is not available.")

if __name__ == "__main__":
    test_cuda()
    test_cuda_operations()

if cp.cuda.is_available():
    print("CUDA is available.")
    a = cp.array([1, 2, 3])
    print("Array on GPU:", a)
else:
    print("CUDA is not available.")