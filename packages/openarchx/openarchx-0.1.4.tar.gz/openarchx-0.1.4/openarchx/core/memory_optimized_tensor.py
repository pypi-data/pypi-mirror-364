import numpy as np
import weakref
import threading
from typing import Optional, Dict, Any, Tuple
from .tensor import Tensor

class GlobalMemoryPool:
    """Advanced memory pool with automatic optimization and defragmentation"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self.pools: Dict[Tuple[int, np.dtype], list] = {}
        self.allocated_tensors = weakref.WeakSet()
        self.fragmentation_threshold = 0.3
        self.auto_defrag = True
        self.total_allocated = 0
        self.peak_allocated = 0
        self.allocation_history = []
        self._lock = threading.Lock()
    
    def allocate(self, shape: Tuple[int, ...], dtype: np.dtype) -> np.ndarray:
        """Smart allocation with defragmentation and reuse"""
        size = np.prod(shape)
        key = (size, dtype)
        
        with self._lock:
            # Try to reuse existing allocation
            if key in self.pools and self.pools[key]:
                array = self.pools[key].pop()
                return array.reshape(shape)
            
            # Create new allocation
            array = np.empty(shape, dtype=dtype)
            self.total_allocated += array.nbytes
            self.peak_allocated = max(self.peak_allocated, self.total_allocated)
            self.allocation_history.append(('alloc', array.nbytes))
            
            # Trigger defragmentation if needed
            if self.auto_defrag and self._should_defragment():
                self._defragment()
            
            return array
    
    def deallocate(self, array: np.ndarray):
        """Return array to pool for reuse"""
        if array is None:
            return
            
        size = array.size
        dtype = array.dtype
        key = (size, dtype)
        
        with self._lock:
            if key not in self.pools:
                self.pools[key] = []
            
            # Store flattened array for reuse
            self.pools[key].append(array.flatten())
            self.allocation_history.append(('dealloc', array.nbytes))
    
    def _should_defragment(self) -> bool:
        """Check if defragmentation is needed"""
        if len(self.allocation_history) < 100:
            return False
        
        recent_allocs = sum(1 for op, _ in self.allocation_history[-50:] if op == 'alloc')
        recent_deallocs = sum(1 for op, _ in self.allocation_history[-50:] if op == 'dealloc')
        
        fragmentation_ratio = recent_allocs / max(recent_deallocs, 1)
        return fragmentation_ratio > self.fragmentation_threshold
    
    def _defragment(self):
        """Perform memory defragmentation"""
        # Clear small pools to reduce fragmentation
        keys_to_remove = []
        for key, pool in self.pools.items():
            if len(pool) > 10:  # Keep only large pools
                pool.clear()
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.pools[key]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get detailed memory usage statistics"""
        with self._lock:
            pool_sizes = {str(key): len(pool) for key, pool in self.pools.items()}
            return {
                'total_allocated': self.total_allocated,
                'peak_allocated': self.peak_allocated,
                'active_tensors': len(self.allocated_tensors),
                'pool_sizes': pool_sizes,
                'fragmentation_ratio': self._calculate_fragmentation_ratio()
            }
    
    def _calculate_fragmentation_ratio(self) -> float:
        """Calculate current fragmentation ratio"""
        if not self.allocation_history:
            return 0.0
        
        recent_ops = self.allocation_history[-100:]
        allocs = sum(1 for op, _ in recent_ops if op == 'alloc')
        deallocs = sum(1 for op, _ in recent_ops if op == 'dealloc')
        
        return allocs / max(deallocs, 1) if deallocs > 0 else 1.0
    
    def optimize(self):
        """Manual memory optimization"""
        with self._lock:
            self._defragment()
            # Clear allocation history to free memory
            if len(self.allocation_history) > 1000:
                self.allocation_history = self.allocation_history[-500:]


class MemoryOptimizedTensor(Tensor):
    """Memory-optimized tensor with lazy allocation, compression, and smart memory management"""
    
    def __init__(self, data, requires_grad=False, device='cpu', memory_pool=None, 
                 lazy_allocation=True, compression_enabled=True):
        self.memory_pool = memory_pool or GlobalMemoryPool()
        self.lazy_allocation = lazy_allocation
        self.compression_enabled = compression_enabled
        self._compressed_data = None
        self._is_compressed = False
        self._access_count = 0
        self._last_access_time = 0
        
        # Initialize with lazy allocation if enabled
        if lazy_allocation and isinstance(data, (list, tuple)):
            self._lazy_shape = np.array(data).shape
            self._lazy_dtype = np.float32
            self._data = None
        else:
            self._data = self._allocate_array(data)
        
        # Initialize parent class attributes manually to avoid double allocation
        self.requires_grad = requires_grad
        self.grad = None if requires_grad else None
        self._backward = lambda: None
        self._prev = set()
        self.device = device
        
        # Register with memory pool
        self.memory_pool.allocated_tensors.add(self)
    
    @property
    def data(self):
        """Lazy data access with automatic decompression"""
        self._access_count += 1
        import time
        self._last_access_time = time.time()
        
        if self._data is None and hasattr(self, '_lazy_shape'):
            # Lazy allocation
            self._data = self.memory_pool.allocate(self._lazy_shape, self._lazy_dtype)
            
        if self._is_compressed:
            self._decompress()
        
        return self._data
    
    @data.setter
    def data(self, value):
        """Set data with automatic memory management"""
        if self._data is not None:
            self.memory_pool.deallocate(self._data)
        
        self._data = self._allocate_array(value)
        self._is_compressed = False
        self._compressed_data = None
    
    def _allocate_array(self, data):
        """Allocate array using memory pool"""
        if isinstance(data, np.ndarray):
            shape = data.shape
            dtype = data.dtype
            array = self.memory_pool.allocate(shape, dtype)
            array[:] = data
            return array
        else:
            data_array = np.asarray(data, dtype=np.float32)
            array = self.memory_pool.allocate(data_array.shape, data_array.dtype)
            array[:] = data_array
            return array
    
    def _compress(self):
        """Compress tensor data to save memory"""
        if not self.compression_enabled or self._is_compressed or self._data is None:
            return
        
        # Advanced compression strategies
        if self._data.dtype == np.float32:
            # Strategy 1: Use float16 for suitable data
            if np.all(np.abs(self._data) < 65504):  # float16 max value
                self._compressed_data = self._data.astype(np.float16)
                self.memory_pool.deallocate(self._data)
                self._data = None
                self._is_compressed = True
            # Strategy 2: Sparse representation for mostly zero tensors
            elif np.count_nonzero(self._data) / self._data.size < 0.1:  # Less than 10% non-zero
                # Store as sparse format (indices + values)
                nonzero_indices = np.nonzero(self._data)
                nonzero_values = self._data[nonzero_indices]
                self._compressed_data = {
                    'type': 'sparse',
                    'shape': self._data.shape,
                    'indices': nonzero_indices,
                    'values': nonzero_values.astype(np.float16) if np.all(np.abs(nonzero_values) < 65504) else nonzero_values
                }
                self.memory_pool.deallocate(self._data)
                self._data = None
                self._is_compressed = True
    
    def _decompress(self):
        """Decompress tensor data"""
        if not self._is_compressed or self._compressed_data is None:
            return
        
        if isinstance(self._compressed_data, dict) and self._compressed_data.get('type') == 'sparse':
            # Decompress sparse format
            shape = self._compressed_data['shape']
            indices = self._compressed_data['indices']
            values = self._compressed_data['values']
            
            self._data = self.memory_pool.allocate(shape, np.float32)
            self._data.fill(0)  # Initialize with zeros
            self._data[indices] = values.astype(np.float32) if values.dtype != np.float32 else values
        else:
            # Decompress from float16 back to float32
            self._data = self.memory_pool.allocate(self._compressed_data.shape, np.float32)
            self._data[:] = self._compressed_data.astype(np.float32)
        
        self._compressed_data = None
        self._is_compressed = False
    
    def optimize_memory(self):
        """Optimize memory usage for this tensor"""
        import time
        current_time = time.time()
        
        # Compress if not accessed recently
        if (current_time - self._last_access_time > 10.0 and 
            self._access_count < 5 and 
            not self._is_compressed):
            self._compress()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this tensor"""
        stats = {
            'shape': getattr(self, '_lazy_shape', self._data.shape if self._data is not None else None),
            'dtype': getattr(self, '_lazy_dtype', self._data.dtype if self._data is not None else None),
            'is_compressed': self._is_compressed,
            'access_count': self._access_count,
            'last_access_time': self._last_access_time,
            'lazy_allocation': self.lazy_allocation,
            'compression_enabled': self.compression_enabled
        }
        
        if self._data is not None:
            stats['memory_usage'] = self._data.nbytes
        elif self._compressed_data is not None:
            stats['memory_usage'] = self._compressed_data.nbytes
            stats['compression_ratio'] = self._compressed_data.nbytes / (np.prod(self._compressed_data.shape) * 4)  # vs float32
        else:
            stats['memory_usage'] = 0
        
        return stats
    
    def __del__(self):
        """Clean up memory when tensor is destroyed"""
        if hasattr(self, '_data') and self._data is not None:
            self.memory_pool.deallocate(self._data)
        if hasattr(self, '_compressed_data') and self._compressed_data is not None:
            del self._compressed_data


class MemoryAnalyzer:
    """Analyze and optimize memory usage patterns"""
    
    def __init__(self):
        self.memory_pool = GlobalMemoryPool()
    
    def analyze_usage(self) -> Dict[str, Any]:
        """Analyze current memory usage patterns"""
        stats = self.memory_pool.get_memory_stats()
        
        # Analyze tensor access patterns
        active_tensors = list(self.memory_pool.allocated_tensors)
        if active_tensors and hasattr(active_tensors[0], 'get_memory_stats'):
            tensor_stats = [t.get_memory_stats() for t in active_tensors 
                          if hasattr(t, 'get_memory_stats')]
            
            stats['tensor_analysis'] = {
                'total_tensors': len(tensor_stats),
                'compressed_tensors': sum(1 for t in tensor_stats if t.get('is_compressed', False)),
                'avg_access_count': np.mean([t.get('access_count', 0) for t in tensor_stats]),
                'total_tensor_memory': sum(t.get('memory_usage', 0) for t in tensor_stats)
            }
        
        return stats
    
    def suggest_optimizations(self) -> list:
        """Suggest memory optimizations"""
        stats = self.analyze_usage()
        suggestions = []
        
        if stats['fragmentation_ratio'] > 0.5:
            suggestions.append("High memory fragmentation detected. Consider calling memory_pool.optimize()")
        
        if 'tensor_analysis' in stats:
            tensor_analysis = stats['tensor_analysis']
            compression_ratio = tensor_analysis['compressed_tensors'] / max(tensor_analysis['total_tensors'], 1)
            
            if compression_ratio < 0.3:
                suggestions.append("Low compression ratio. Consider enabling compression for more tensors")
            
            if tensor_analysis['avg_access_count'] < 2:
                suggestions.append("Many tensors have low access counts. Consider lazy allocation")
        
        return suggestions
    
    def optimize_all_tensors(self):
        """Optimize all active tensors"""
        active_tensors = list(self.memory_pool.allocated_tensors)
        for tensor in active_tensors:
            if hasattr(tensor, 'optimize_memory'):
                tensor.optimize_memory()
        
        self.memory_pool.optimize()


# Convenience function to create memory-optimized tensors
def tensor(data, requires_grad=False, device='cpu', optimize_memory=True):
    """Create a memory-optimized tensor"""
    if optimize_memory:
        return MemoryOptimizedTensor(data, requires_grad=requires_grad, device=device)
    else:
        return Tensor(data, requires_grad=requires_grad, device=device)