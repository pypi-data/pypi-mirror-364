#include <Python.h>
#include <numpy/arrayobject.h>
#include <cuda_runtime.h>
#include <cublas_v2.h>
#include "kernels.cu"
#include <unordered_map>

// CUDA Memory Manager
class CUDAMemoryManager {
private:
    static CUDAMemoryManager* instance;
    std::unordered_map<void*, size_t> allocations;
    
public:
    static CUDAMemoryManager* getInstance() {
        if (!instance) instance = new CUDAMemoryManager();
        return instance;
    }
    
    void* allocate(size_t size) {
        void* ptr;
        cudaError_t error = cudaMalloc(&ptr, size);
        if (error != cudaSuccess) {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate CUDA memory");
            return nullptr;
        }
        allocations[ptr] = size;
        return ptr;
    }
    
    void free(void* ptr) {
        if (ptr && allocations.count(ptr)) {
            cudaFree(ptr);
            allocations.erase(ptr);
        }
    }
    
    void freeAll() {
        for (auto& alloc : allocations) {
            cudaFree(alloc.first);
        }
        allocations.clear();
    }
    
    ~CUDAMemoryManager() {
        freeAll();
    }
};

CUDAMemoryManager* CUDAMemoryManager::instance = nullptr;

static cublasHandle_t cublas_handle;

// Initialize cuBLAS handle with error checking
static bool init_cublas() {
    cublasStatus_t status = cublasCreate(&cublas_handle);
    if (status != CUBLAS_STATUS_SUCCESS) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to initialize cuBLAS");
        return false;
    }
    return true;
}

// Enhanced error checking function
static bool check_cuda_error(cudaError_t error, const char* operation) {
    if (error != cudaSuccess) {
        PyErr_Format(PyExc_RuntimeError, "CUDA error during %s: %s", 
                    operation, cudaGetErrorString(error));
        return false;
    }
    return true;
}

// Cleanup resources
static void cleanup_resources() {
    cublasDestroy(cublas_handle);
    CUDAMemoryManager::getInstance()->freeAll();
}

// Matrix multiplication wrapper
static PyObject* cuda_matmul(PyObject* self, PyObject* args) {
    PyArrayObject *A, *B;
    if (!PyArg_ParseTuple(args, "OO", &A, &B)) return NULL;
    
    int M = PyArray_DIM(A, 0);
    int K = PyArray_DIM(A, 1);
    int N = PyArray_DIM(B, 1);
    
    // Create output array
    npy_intp dims[2] = {M, N};
    PyObject* C = PyArray_SimpleNew(2, dims, NPY_FLOAT32);
    
    // Allocate device memory
    CUDAMemoryManager* memManager = CUDAMemoryManager::getInstance();
    float *d_A = (float*)memManager->allocate(M * K * sizeof(float));
    float *d_B = (float*)memManager->allocate(K * N * sizeof(float));
    float *d_C = (float*)memManager->allocate(M * N * sizeof(float));
    if (!d_A || !d_B || !d_C) return NULL;
    
    // Copy data to device
    if (!check_cuda_error(cudaMemcpy(d_A, PyArray_DATA(A), M * K * sizeof(float), cudaMemcpyHostToDevice), "cudaMemcpy A") ||
        !check_cuda_error(cudaMemcpy(d_B, PyArray_DATA(B), K * N * sizeof(float), cudaMemcpyHostToDevice), "cudaMemcpy B")) {
        return NULL;
    }
    
    // Use cuBLAS for large matrices, custom kernel for small ones
    if (M * N * K > 1024 * 1024) {
        cublas_gemm_wrapper(cublas_handle, d_A, d_B, d_C, M, N, K);
    } else {
        dim3 threadsPerBlock(TILE_SIZE, TILE_SIZE);
        dim3 numBlocks((N + TILE_SIZE - 1) / TILE_SIZE,
                      (M + TILE_SIZE - 1) / TILE_SIZE);
        matmul_kernel<<<numBlocks, threadsPerBlock>>>(d_A, d_B, d_C, M, N, K);
    }
    
    // Copy result back to host
    if (!check_cuda_error(cudaMemcpy(PyArray_DATA((PyArrayObject*)C), d_C, M * N * sizeof(float), cudaMemcpyDeviceToHost), "cudaMemcpy C")) {
        return NULL;
    }
    
    // Free device memory
    memManager->free(d_A);
    memManager->free(d_B);
    memManager->free(d_C);
    
    return C;
}

// Batch normalization wrapper
static PyObject* cuda_batchnorm(PyObject* self, PyObject* args) {
    PyArrayObject *input, *gamma, *beta, *running_mean, *running_var;
    float momentum, epsilon;
    
    if (!PyArg_ParseTuple(args, "OOOOOff", &input, &gamma, &beta,
                         &running_mean, &running_var, &momentum, &epsilon))
        return NULL;
    
    int N = PyArray_DIM(input, 0);
    int C = PyArray_DIM(input, 1);
    int H = PyArray_DIM(input, 2);
    int W = PyArray_DIM(input, 3);
    int HW = H * W;
    
    // Create output array
    npy_intp dims[4] = {N, C, H, W};
    PyObject* output = PyArray_SimpleNew(4, dims, NPY_FLOAT32);
    
    // Allocate device memory
    CUDAMemoryManager* memManager = CUDAMemoryManager::getInstance();
    float *d_input = (float*)memManager->allocate(N * C * HW * sizeof(float));
    float *d_output = (float*)memManager->allocate(N * C * HW * sizeof(float));
    float *d_gamma = (float*)memManager->allocate(C * sizeof(float));
    float *d_beta = (float*)memManager->allocate(C * sizeof(float));
    float *d_running_mean = (float*)memManager->allocate(C * sizeof(float));
    float *d_running_var = (float*)memManager->allocate(C * sizeof(float));
    if (!d_input || !d_output || !d_gamma || !d_beta || !d_running_mean || !d_running_var) return NULL;
    
    // Copy data to device
    if (!check_cuda_error(cudaMemcpy(d_input, PyArray_DATA(input), N * C * HW * sizeof(float), cudaMemcpyHostToDevice), "cudaMemcpy input") ||
        !check_cuda_error(cudaMemcpy(d_gamma, PyArray_DATA(gamma), C * sizeof(float), cudaMemcpyHostToDevice), "cudaMemcpy gamma") ||
        !check_cuda_error(cudaMemcpy(d_beta, PyArray_DATA(beta), C * sizeof(float), cudaMemcpyHostToDevice), "cudaMemcpy beta") ||
        !check_cuda_error(cudaMemcpy(d_running_mean, PyArray_DATA(running_mean), C * sizeof(float), cudaMemcpyHostToDevice), "cudaMemcpy running_mean") ||
        !check_cuda_error(cudaMemcpy(d_running_var, PyArray_DATA(running_var), C * sizeof(float), cudaMemcpyHostToDevice), "cudaMemcpy running_var")) {
        return NULL;
    }
    
    // Launch kernel
    int threadsPerBlock = min(MAX_THREADS_PER_BLOCK, N * HW);
    batchnorm_forward_kernel<<<C, threadsPerBlock>>>(
        d_input, d_gamma, d_beta, d_output,
        d_running_mean, d_running_var,
        momentum, epsilon, N, C, HW
    );
    
    // Copy results back to host
    if (!check_cuda_error(cudaMemcpy(PyArray_DATA((PyArrayObject*)output), d_output, N * C * HW * sizeof(float), cudaMemcpyDeviceToHost), "cudaMemcpy output") ||
        !check_cuda_error(cudaMemcpy(PyArray_DATA(running_mean), d_running_mean, C * sizeof(float), cudaMemcpyDeviceToHost), "cudaMemcpy running_mean") ||
        !check_cuda_error(cudaMemcpy(PyArray_DATA(running_var), d_running_var, C * sizeof(float), cudaMemcpyDeviceToHost), "cudaMemcpy running_var")) {
        return NULL;
    }
    
    // Free device memory
    memManager->free(d_input);
    memManager->free(d_output);
    memManager->free(d_gamma);
    memManager->free(d_beta);
    memManager->free(d_running_mean);
    memManager->free(d_running_var);
    
    return output;
}

// Dropout wrapper
static PyObject* cuda_dropout(PyObject* self, PyObject* args) {
    PyArrayObject* input;
    float dropout_prob;
    unsigned long long seed;
    
    if (!PyArg_ParseTuple(args, "OfK", &input, &dropout_prob, &seed))
        return NULL;
    
    int size = PyArray_SIZE(input);
    
    // Create output array
    PyObject* output = PyArray_SimpleNew(PyArray_NDIM(input),
                                       PyArray_DIMS(input),
                                       NPY_FLOAT32);
    
    // Allocate device memory
    CUDAMemoryManager* memManager = CUDAMemoryManager::getInstance();
    float *d_input = (float*)memManager->allocate(size * sizeof(float));
    float *d_output = (float*)memManager->allocate(size * sizeof(float));
    if (!d_input || !d_output) return NULL;
    
    // Copy input to device
    if (!check_cuda_error(cudaMemcpy(d_input, PyArray_DATA(input), size * sizeof(float), cudaMemcpyHostToDevice), "cudaMemcpy input")) {
        return NULL;
    }
    
    // Launch kernel
    int threadsPerBlock = 256;
    int numBlocks = (size + threadsPerBlock - 1) / threadsPerBlock;
    dropout_kernel<<<numBlocks, threadsPerBlock>>>(
        d_output, d_input, dropout_prob, seed, size
    );
    
    // Copy result back to host
    if (!check_cuda_error(cudaMemcpy(PyArray_DATA((PyArrayObject*)output), d_output, size * sizeof(float), cudaMemcpyDeviceToHost), "cudaMemcpy output")) {
        return NULL;
    }
    
    // Free device memory
    memManager->free(d_input);
    memManager->free(d_output);
    
    return output;
}

// 2D Convolution wrapper
static PyObject* cuda_conv2d(PyObject* self, PyObject* args) {
    PyArrayObject *input, *weights;
    int padding, stride;
    if (!PyArg_ParseTuple(args, "OOii", &input, &weights, &padding, &stride)) 
        return NULL;
    
    int N = PyArray_DIM(input, 0);  // batch size
    int C = PyArray_DIM(input, 1);  // channels
    int H = PyArray_DIM(input, 2);  // height
    int W = PyArray_DIM(input, 3);  // width
    int K = PyArray_DIM(weights, 0); // output channels
    int kernel_size = PyArray_DIM(weights, 2);
    
    int H_out = (H + 2*padding - kernel_size) / stride + 1;
    int W_out = (W + 2*padding - kernel_size) / stride + 1;
    
    // Create output array
    npy_intp dims[4] = {N, K, H_out, W_out};
    PyObject* output = PyArray_SimpleNew(4, dims, NPY_FLOAT32);
    
    // Launch kernel
    dim3 threadsPerBlock(16, 16);
    dim3 numBlocks(N, K);
    
    conv2d_kernel<<<numBlocks, threadsPerBlock>>>(
        (float*)PyArray_DATA(input),
        (float*)PyArray_DATA(weights),
        (float*)PyArray_DATA((PyArrayObject*)output),
        N, C, H, W, kernel_size, padding, stride);
    
    return output;
}

// Elementwise operations wrapper
static PyObject* cuda_elementwise(PyObject* self, PyObject* args) {
    PyArrayObject *input1, *input2;
    int op_type;
    if (!PyArg_ParseTuple(args, "OOi", &input1, &input2, &op_type)) return NULL;
    
    int size = PyArray_SIZE(input1);
    
    // Create output array
    PyObject* output = PyArray_SimpleNew(PyArray_NDIM(input1), 
                                       PyArray_DIMS(input1), 
                                       NPY_FLOAT32);
    
    // Launch kernel
    int threadsPerBlock = 256;
    int numBlocks = (size + threadsPerBlock - 1) / threadsPerBlock;
    
    elementwise_kernel<<<numBlocks, threadsPerBlock>>>(
        (float*)PyArray_DATA((PyArrayObject*)output),
        (float*)PyArray_DATA(input1),
        (float*)PyArray_DATA(input2),
        size, op_type);
    
    return output;
}

// Max pooling 2D wrapper
static PyObject* cuda_maxpool2d(PyObject* self, PyObject* args) {
    PyArrayObject* input;
    int kernel_size, stride;
    if (!PyArg_ParseTuple(args, "Oii", &input, &kernel_size, &stride)) 
        return NULL;
    
    int N = PyArray_DIM(input, 0);
    int C = PyArray_DIM(input, 1);
    int H = PyArray_DIM(input, 2);
    int W = PyArray_DIM(input, 3);
    
    int H_out = (H - kernel_size) / stride + 1;
    int W_out = (W - kernel_size) / stride + 1;
    
    // Create output array
    npy_intp dims[4] = {N, C, H_out, W_out};
    PyObject* output = PyArray_SimpleNew(4, dims, NPY_FLOAT32);
    
    // Launch kernel
    dim3 threadsPerBlock(16, 16);
    dim3 numBlocks(N, C);
    
    maxpool2d_kernel<<<numBlocks, threadsPerBlock>>>(
        (float*)PyArray_DATA(input),
        (float*)PyArray_DATA((PyArrayObject*)output),
        N, C, H, W, kernel_size, stride);
    
    return output;
}

// Method definitions
static PyMethodDef cuda_methods[] = {
    {"matmul", cuda_matmul, METH_VARARGS,
     "Optimized CUDA matrix multiplication with cuBLAS integration"},
    {"batchnorm", cuda_batchnorm, METH_VARARGS,
     "CUDA-accelerated batch normalization"},
    {"dropout", cuda_dropout, METH_VARARGS,
     "CUDA-accelerated dropout with cuRAND"},
    {"conv2d", cuda_conv2d, METH_VARARGS,
     "CUDA 2D convolution with shared memory optimization"},
    {"elementwise", cuda_elementwise, METH_VARARGS,
     "Vectorized elementwise operations"},
    {"maxpool2d", cuda_maxpool2d, METH_VARARGS,
     "Optimized max pooling 2D with indices"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cuda_module = {
    PyModuleDef_HEAD_INIT,
    "cuda_ops",
    "Optimized CUDA operations for OpenArchX",
    -1,
    cuda_methods
};

PyMODINIT_FUNC PyInit_cuda_ops(void) {
    import_array();
    if (!init_cublas()) return NULL;
    PyObject* m = PyModule_Create(&cuda_module);
    if (m == NULL) return NULL;
    
    // Register cleanup
    Py_AtExit(cleanup_resources);
    return m;
}