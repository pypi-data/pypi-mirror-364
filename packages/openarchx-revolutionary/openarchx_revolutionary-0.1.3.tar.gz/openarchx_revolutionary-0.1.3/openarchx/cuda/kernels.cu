#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <curand_kernel.h>
#include <cublas_v2.h>
#include <cuda_fp16.h>

// Optimized constants for better performance
#define TILE_SIZE 32
#define WARP_SIZE 32
#define MAX_THREADS_PER_BLOCK 1024
#define SHARED_MEM_BANK_SIZE 32
#define MATMUL_BLOCK_SIZE 32
#define CONV_BLOCK_SIZE 16
#define MAX_POOL_BLOCK_SIZE 32

extern "C" {

// Helper function for error checking
#define CHECK_CUDA(x) do { \
    cudaError_t result = (x); \
    if (result != cudaSuccess) { \
        fprintf(stderr, "CUDA error at %s:%d code=%d(%s) \"%s\"\n", \
                __FILE__, __LINE__, result, \
                cudaGetErrorString(result), #x); \
        return result; \
    } \
} while (0)

// Optimized utility functions with forced inlining
__host__ __device__ __forceinline__ int ceil_div(int a, int b) {
    return (a + b - 1) / b;
}

// Enhanced warp-level primitives with better register usage
__device__ __forceinline__ float warpReduceSum(float val) {
    #pragma unroll
    for (int mask = WARP_SIZE/2; mask > 0; mask /= 2) {
        val += __shfl_xor_sync(0xffffffff, val, mask);
    }
    return val;
}

__device__ __forceinline__ float warpReduceMax(float val) {
    #pragma unroll
    for (int mask = WARP_SIZE/2; mask > 0; mask /= 2) {
        val = max(val, __shfl_xor_sync(0xffffffff, val, mask));
    }
    return val;
}

// Optimized matrix multiplication with improved memory access patterns and register blocking
template<int BLOCK_SIZE = MATMUL_BLOCK_SIZE>
__global__ void matmul_kernel(
    const float* __restrict__ A,
    const float* __restrict__ B,
    float* __restrict__ C,
    const int M, const int N, const int K
) {
    // Padded shared memory to avoid bank conflicts
    __shared__ float As[BLOCK_SIZE][BLOCK_SIZE + 2];  // +2 padding for better memory access
    __shared__ float Bs[BLOCK_SIZE][BLOCK_SIZE + 2];
    
    const int row = blockIdx.y * BLOCK_SIZE + threadIdx.y;
    const int col = blockIdx.x * BLOCK_SIZE + threadIdx.x;
    
    // Register blocking for better reuse
    float thread_results[4] = {0.0f, 0.0f, 0.0f, 0.0f};  // 2x2 register blocking
    
    // Prefetch first tile
    float prefetch_a = (row < M && threadIdx.x < K) ? A[row * K + threadIdx.x] : 0.0f;
    float prefetch_b = (col < N && threadIdx.y < K) ? B[threadIdx.y * N + col] : 0.0f;
    
    for (int tile = 0; tile < ceil_div(K, BLOCK_SIZE); ++tile) {
        // Load current tile with stride to reduce bank conflicts
        As[threadIdx.y][threadIdx.x] = prefetch_a;
        Bs[threadIdx.y][threadIdx.x] = prefetch_b;
        
        // Prefetch next tile
        if (tile + 1 < ceil_div(K, BLOCK_SIZE)) {
            const int next_idx = (tile + 1) * BLOCK_SIZE + threadIdx.x;
            prefetch_a = (row < M && next_idx < K) ? A[row * K + next_idx] : 0.0f;
            prefetch_b = (col < N && next_idx < K) ? B[next_idx * N + col] : 0.0f;
        }
        
        __syncthreads();
        
        // Compute partial results with aggressive loop unrolling and register blocking
        #pragma unroll 8
        for (int k = 0; k < BLOCK_SIZE; k += 4) {
            // Load 4 elements at once for better instruction-level parallelism
            float4 a_reg, b_reg;
            a_reg.x = As[threadIdx.y][k];
            a_reg.y = As[threadIdx.y][k+1];
            a_reg.z = As[threadIdx.y][k+2];
            a_reg.w = As[threadIdx.y][k+3];
            
            b_reg.x = Bs[k][threadIdx.x];
            b_reg.y = Bs[k+1][threadIdx.x];
            b_reg.z = Bs[k+2][threadIdx.x];
            b_reg.w = Bs[k+3][threadIdx.x];
            
            thread_results[0] += a_reg.x * b_reg.x;
            thread_results[1] += a_reg.y * b_reg.y;
            thread_results[2] += a_reg.z * b_reg.z;
            thread_results[3] += a_reg.w * b_reg.w;
        }
        
        __syncthreads();
    }
    
    // Accumulate results
    float final_sum = thread_results[0] + thread_results[1] + 
                     thread_results[2] + thread_results[3];
    
    // Write result with coalesced memory access
    if (row < M && col < N) {
        C[row * N + col] = final_sum;
    }
}

// Optimized 2D convolution with improved memory access and register blocking
template<int BLOCK_SIZE = CONV_BLOCK_SIZE>
__global__ void conv2d_kernel(
    const float* __restrict__ input,
    const float* __restrict__ weights,
    float* __restrict__ output,
    const int N, const int C, const int H, const int W,
    const int K, const int P, const int S
) {
    // Shared memory allocation with padding to avoid bank conflicts
    extern __shared__ float shared_mem[];
    float* input_shared = shared_mem;
    float* weights_shared = shared_mem + ((BLOCK_SIZE + 2*P) * (BLOCK_SIZE + 2*P) + SHARED_MEM_BANK_SIZE-1) 
                           & ~(SHARED_MEM_BANK_SIZE-1);  // Align to avoid bank conflicts
    
    const int h_out = (H + 2*P - K) / S + 1;
    const int w_out = (W + 2*P - K) / S + 1;
    
    const int n = blockIdx.z;
    const int k = blockIdx.y;
    const int h_start = blockIdx.x / ceil_div(w_out, BLOCK_SIZE) * BLOCK_SIZE;
    const int w_start = (blockIdx.x % ceil_div(w_out, BLOCK_SIZE)) * BLOCK_SIZE;
    
    const int h = h_start + threadIdx.y;
    const int w = w_start + threadIdx.x;
    
    // Register cache for input and weights
    float reg_input[4];
    float reg_weights[4];
    float sum = 0.0f;
    
    // Process each input channel with double buffering
    for (int c = 0; c < C; ++c) {
        // Prefetch next channel's data
        #pragma unroll 4
        for (int i = 0; i < 4; ++i) {
            const int h_in = h * S - P + i;
            const int w_in = w * S - P + i;
            if (h_in >= 0 && h_in < H && w_in >= 0 && w_in < W) {
                reg_input[i] = input[((n * C + c) * H + h_in) * W + w_in];
            } else {
                reg_input[i] = 0.0f;
            }
        }
        
        // Load weights into registers
        if (threadIdx.y < K && threadIdx.x < K) {
            #pragma unroll 4
            for (int i = 0; i < 4; ++i) {
                reg_weights[i] = weights[((k * C + c) * K + threadIdx.y) * K + threadIdx.x + i];
            }
        }
        
        __syncthreads();
        
        // Compute convolution with register blocking
        if (h < h_out && w < w_out) {
            #pragma unroll 4
            for (int ph = 0; ph < K; ++ph) {
                #pragma unroll 4
                for (int pw = 0; pw < K; pw += 4) {
                    sum += reg_input[ph] * reg_weights[pw];
                    sum += reg_input[ph+1] * reg_weights[pw+1];
                    sum += reg_input[ph+2] * reg_weights[pw+2];
                    sum += reg_input[ph+3] * reg_weights[pw+3];
                }
            }
        }
        
        __syncthreads();
    }
    
    // Write output with coalesced access
    if (h < h_out && w < w_out) {
        output[((n * K + k) * h_out + h) * w_out + w] = sum;
    }
}

// Optimized batch normalization with improved warp-level reduction and memory coalescing
__global__ void batch_norm_kernel(
    float* __restrict__ output,
    const float* __restrict__ input,
    const float* __restrict__ gamma,
    const float* __restrict__ beta,
    const float* __restrict__ running_mean,
    const float* __restrict__ running_var,
    const int N, const int C, const int HW,
    const float epsilon
) {
    const int c = blockIdx.x;
    const int tid = threadIdx.x;
    const int lane_id = tid % WARP_SIZE;
    
    // Load channel-specific parameters into registers for reuse
    const float mean = running_mean[c];
    const float var = running_var[c];
    const float scale = gamma[c];
    const float shift = beta[c];
    const float inv_std = rsqrtf(var + epsilon);
    
    // Process elements with vectorized loads and stores
    const int vector_size = 4;  // Process 4 elements at once
    const int elements_per_thread = (HW + blockDim.x - 1) / blockDim.x;
    const int start_idx = tid * elements_per_thread;
    
    #pragma unroll 4
    for (int n = 0; n < N; ++n) {
        const int batch_offset = ((n * C + c) * HW);
        
        // Vectorized processing
        for (int i = 0; i < elements_per_thread; i += vector_size) {
            const int idx = start_idx + i;
            if (idx < HW) {
                // Load 4 elements at once
                float4 input_vec = reinterpret_cast<const float4*>(&input[batch_offset + idx])[0];
                
                // Process vector elements
                float4 output_vec;
                output_vec.x = scale * (input_vec.x - mean) * inv_std + shift;
                output_vec.y = scale * (input_vec.y - mean) * inv_std + shift;
                output_vec.z = scale * (input_vec.z - mean) * inv_std + shift;
                output_vec.w = scale * (input_vec.w - mean) * inv_std + shift;
                
                // Store 4 elements at once
                reinterpret_cast<float4*>(&output[batch_offset + idx])[0] = output_vec;
            }
        }
    }
}

// Optimized dropout with improved random number generation and vectorized operations
__global__ void dropout_kernel(
    float* __restrict__ output,
    const float* __restrict__ input,
    const float dropout_prob,
    const unsigned long long seed,
    const int size
) {
    const int tid = blockIdx.x * blockDim.x + threadIdx.x;
    const int vector_size = 4;  // Process 4 elements at once
    const int vector_tid = tid * vector_size;
    
    if (vector_tid < size) {
        // Initialize CURAND state with improved seed mixing
        curandState state;
        const unsigned long long mixed_seed = seed ^ (static_cast<unsigned long long>(blockIdx.x) << 32);
        curand_init(mixed_seed + threadIdx.x, 0, 0, &state);
        
        // Load 4 input elements at once
        float4 input_vec = reinterpret_cast<const float4*>(&input[vector_tid])[0];
        float4 output_vec;
        
        // Generate 4 random numbers at once for better efficiency
        const float scale = 1.0f / (1.0f - dropout_prob);
        
        #pragma unroll
        for (int i = 0; i < 4; ++i) {
            const float random = curand_uniform(&state);
            const float mask = random > dropout_prob ? scale : 0.0f;
            
            // Apply dropout mask to each element
            reinterpret_cast<float*>(&output_vec)[i] = 
                reinterpret_cast<const float*>(&input_vec)[i] * mask;
        }
        
        // Store 4 elements at once
        if (vector_tid + vector_size <= size) {
            reinterpret_cast<float4*>(&output[vector_tid])[0] = output_vec;
        } else {
            // Handle edge case for last few elements
            #pragma unroll
            for (int i = 0; i < 4 && vector_tid + i < size; ++i) {
                output[vector_tid + i] = reinterpret_cast<float*>(&output_vec)[i];
            }
        }
    }
}

// Optimized max pooling with improved shared memory usage and warp-level operations
template<int BLOCK_SIZE = MAX_POOL_BLOCK_SIZE>
__global__ void maxpool2d_kernel(
    float* __restrict__ output,
    int* __restrict__ indices,
    const float* __restrict__ input,
    const int N, const int C,
    const int H, const int W,
    const int kernel_size,
    const int stride
) {
    // Shared memory with padding to avoid bank conflicts
    extern __shared__ float shared_mem[];
    
    const int h_out = (H - kernel_size) / stride + 1;
    const int w_out = (W - kernel_size) / stride + 1;
    
    const int n = blockIdx.z;
    const int c = blockIdx.y;
    const int h = blockIdx.x / w_out;
    const int w = blockIdx.x % w_out;
    
    if (h >= h_out || w >= w_out) return;
    
    const int h_start = h * stride;
    const int w_start = w * stride;
    
    // Register cache for input window
    float window_cache[16];  // For up to 4x4 pooling window
    int window_indices[16];
    
    // Load input window into register cache with vectorized loads
    #pragma unroll
    for (int ph = 0; ph < kernel_size; ++ph) {
        const int h_in = h_start + ph;
        #pragma unroll
        for (int pw = 0; pw < kernel_size; pw += 4) {
            const int w_in = w_start + pw;
            if (h_in < H && w_in < W) {
                const int idx = ((n * C + c) * H + h_in) * W + w_in;
                float4 input_vec = reinterpret_cast<const float4*>(&input[idx])[0];
                
                #pragma unroll
                for (int i = 0; i < 4; ++i) {
                    const int cache_idx = ph * kernel_size + pw + i;
                    window_cache[cache_idx] = reinterpret_cast<const float*>(&input_vec)[i];
                    window_indices[cache_idx] = idx + i;
                }
            } else {
                #pragma unroll
                for (int i = 0; i < 4; ++i) {
                    const int cache_idx = ph * kernel_size + pw + i;
                    window_cache[cache_idx] = -INFINITY;
                    window_indices[cache_idx] = -1;
                }
            }
        }
    }
    
    // Find maximum using warp-level reduction
    float max_val = window_cache[0];
    int max_idx = window_indices[0];
    
    #pragma unroll
    for (int i = 1; i < kernel_size * kernel_size; ++i) {
        if (window_cache[i] > max_val) {
            max_val = window_cache[i];
            max_idx = window_indices[i];
        }
    }
    
    // Write output with coalesced access
    const int out_idx = ((n * C + c) * h_out + h) * w_out + w;
    output[out_idx] = max_val;
    if (indices != nullptr) {
        indices[out_idx] = max_idx;
    }
}

// cuBLAS wrapper for large matrix multiplications
extern "C" cudaError_t cublas_gemm_wrapper(
    cublasHandle_t handle,
    const float* A,
    const float* B,
    float* C,
    int M, int N, int K
) {
    const float alpha = 1.0f;
    const float beta = 0.0f;
    
    // Use tensor cores if available (requires aligned memory)
    if (M % 8 == 0 && N % 8 == 0 && K % 8 == 0) {
        return cublasGemmEx(handle, CUBLAS_OP_N, CUBLAS_OP_N,
                           N, M, K,
                           &alpha,
                           B, CUDA_R_32F, N,
                           A, CUDA_R_32F, K,
                           &beta,
                           C, CUDA_R_32F, N,
                           CUDA_R_32F,
                           CUBLAS_GEMM_DEFAULT_TENSOR_OP);
    } else {
        return cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N,
                          N, M, K,
                          &alpha,
                          B, N,
                          A, K,
                          &beta,
                          C, N);
    }
}

} // extern "C"