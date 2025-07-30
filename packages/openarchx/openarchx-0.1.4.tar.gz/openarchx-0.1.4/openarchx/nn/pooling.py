import numpy as np
from ..core.tensor import Tensor
from .module import Module

class MaxPool1d(Module):
    def __init__(self, kernel_size, stride=None, padding=0):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride if stride is not None else kernel_size
        self.padding = padding

    def forward(self, x):
        # TODO: Implement MaxPool1d forward pass
        pass

class MaxPool2d(Module):
    def __init__(self, kernel_size, stride=None, padding=0):
        super().__init__()
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if stride is not None else self.kernel_size
        self.stride = self.stride if isinstance(self.stride, tuple) else (self.stride, self.stride)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)

    def forward(self, x):
        batch_size, channels, height, width = x.data.shape
        pad_h, pad_w = self.padding
        stride_h, stride_w = self.stride
        kernel_h, kernel_w = self.kernel_size
        
        # Add padding if needed
        if pad_h > 0 or pad_w > 0:
            x_padded = np.pad(x.data, ((0, 0), (0, 0), (pad_h, pad_h), (pad_w, pad_w)), mode='constant')
        else:
            x_padded = x.data
        
        # Calculate output dimensions
        out_height = (height + 2 * pad_h - kernel_h) // stride_h + 1
        out_width = (width + 2 * pad_w - kernel_w) // stride_w + 1
        
        # Prepare output array
        out = np.zeros((batch_size, channels, out_height, out_width))
        
        # Perform max pooling
        for b in range(batch_size):
            for c in range(channels):
                for h in range(out_height):
                    for w in range(out_width):
                        h_start = h * stride_h
                        w_start = w * stride_w
                        h_end = h_start + kernel_h
                        w_end = w_start + kernel_w
                        
                        pool_region = x_padded[b, c, h_start:h_end, w_start:w_end]
                        out[b, c, h, w] = np.max(pool_region)
        
        return Tensor(out, requires_grad=True)

class AvgPool1d(Module):
    def __init__(self, kernel_size, stride=None, padding=0):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride if stride is not None else kernel_size
        self.padding = padding

    def forward(self, x):
        # TODO: Implement AvgPool1d forward pass
        pass

class AvgPool2d(Module):
    def __init__(self, kernel_size, stride=None, padding=0):
        super().__init__()
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if stride is not None else self.kernel_size
        self.stride = self.stride if isinstance(self.stride, tuple) else (self.stride, self.stride)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)

    def forward(self, x):
        batch_size, channels, height, width = x.data.shape
        pad_h, pad_w = self.padding
        stride_h, stride_w = self.stride
        kernel_h, kernel_w = self.kernel_size
        
        # Add padding if needed
        if pad_h > 0 or pad_w > 0:
            x_padded = np.pad(x.data, ((0, 0), (0, 0), (pad_h, pad_h), (pad_w, pad_w)), mode='constant')
        else:
            x_padded = x.data
        
        # Calculate output dimensions
        out_height = (height + 2 * pad_h - kernel_h) // stride_h + 1
        out_width = (width + 2 * pad_w - kernel_w) // stride_w + 1
        
        # Prepare output array
        out = np.zeros((batch_size, channels, out_height, out_width))
        
        # Perform average pooling
        for b in range(batch_size):
            for c in range(channels):
                for h in range(out_height):
                    for w in range(out_width):
                        h_start = h * stride_h
                        w_start = w * stride_w
                        h_end = h_start + kernel_h
                        w_end = w_start + kernel_w
                        
                        pool_region = x_padded[b, c, h_start:h_end, w_start:w_end]
                        out[b, c, h, w] = np.mean(pool_region)
        
        return Tensor(out, requires_grad=True)

class AdaptiveAvgPool2d(Module):
    def __init__(self, output_size):
        super().__init__()
        self.output_size = output_size if isinstance(output_size, tuple) else (output_size, output_size)

    def forward(self, x):
        batch_size, channels, height, width = x.data.shape
        out_h, out_w = self.output_size
        
        # Calculate the kernel and stride sizes
        stride_h = height // out_h
        stride_w = width // out_w
        kernel_h = height - (out_h - 1) * stride_h
        kernel_w = width - (out_w - 1) * stride_w
        
        # Prepare output array
        out = np.zeros((batch_size, channels, out_h, out_w))
        
        # Perform adaptive average pooling
        for b in range(batch_size):
            for c in range(channels):
                for h in range(out_h):
                    for w in range(out_w):
                        h_start = h * stride_h
                        w_start = w * stride_w
                        h_end = min(h_start + kernel_h, height)
                        w_end = min(w_start + kernel_w, width)
                        
                        pool_region = x.data[b, c, h_start:h_end, w_start:w_end]
                        out[b, c, h, w] = np.mean(pool_region)
        
        return Tensor(out, requires_grad=True)

class AdaptiveMaxPool2d(Module):
    def __init__(self, output_size):
        super().__init__()
        self.output_size = output_size if isinstance(output_size, tuple) else (output_size, output_size)

    def forward(self, x):
        batch_size, channels, height, width = x.data.shape
        out_h, out_w = self.output_size
        
        # Calculate the kernel and stride sizes
        stride_h = height // out_h
        stride_w = width // out_w
        kernel_h = height - (out_h - 1) * stride_h
        kernel_w = width - (out_w - 1) * stride_w
        
        # Prepare output array
        out = np.zeros((batch_size, channels, out_h, out_w))
        
        # Perform adaptive max pooling
        for b in range(batch_size):
            for c in range(channels):
                for h in range(out_h):
                    for w in range(out_w):
                        h_start = h * stride_h
                        w_start = w * stride_w
                        h_end = min(h_start + kernel_h, height)
                        w_end = min(w_start + kernel_w, width)
                        
                        pool_region = x.data[b, c, h_start:h_end, w_start:w_end]
                        out[b, c, h, w] = np.max(pool_region)
        
        return Tensor(out, requires_grad=True)

class FractionalMaxPool2d(Module):
    def __init__(self, kernel_size, output_size=None, output_ratio=None, return_indices=False):
        super().__init__()
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.output_size = output_size
        self.output_ratio = output_ratio
        self.return_indices = return_indices

    def forward(self, x):
        batch_size, channels, height, width = x.data.shape
        
        if self.output_size is not None:
            out_h, out_w = self.output_size
        else:
            out_h = int(height * self.output_ratio[0])
            out_w = int(width * self.output_ratio[1])
        
        # Generate random pooling regions
        h_indices = np.linspace(0, height - self.kernel_size[0], out_h, dtype=int)
        w_indices = np.linspace(0, width - self.kernel_size[1], out_w, dtype=int)
        
        out = np.zeros((batch_size, channels, out_h, out_w))
        indices = np.zeros((batch_size, channels, out_h, out_w, 2), dtype=int) if self.return_indices else None
        
        for b in range(batch_size):
            for c in range(channels):
                for i, h_idx in enumerate(h_indices):
                    for j, w_idx in enumerate(w_indices):
                        region = x.data[b, c,
                                h_idx:h_idx + self.kernel_size[0],
                                w_idx:w_idx + self.kernel_size[1]]
                        out[b, c, i, j] = np.max(region)
                        if self.return_indices:
                            max_idx = np.unravel_index(np.argmax(region), region.shape)
                            indices[b, c, i, j] = [h_idx + max_idx[0], w_idx + max_idx[1]]
        
        if self.return_indices:
            return Tensor(out, requires_grad=True), indices
        return Tensor(out, requires_grad=True)

class FractionalMaxPool3d(Module):
    def __init__(self, kernel_size, output_size=None, output_ratio=None, return_indices=False):
        super().__init__()
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size, kernel_size)
        self.output_size = output_size
        self.output_ratio = output_ratio
        self.return_indices = return_indices

    def forward(self, x):
        batch_size, channels, depth, height, width = x.data.shape
        
        if self.output_size is not None:
            out_d, out_h, out_w = self.output_size
        else:
            out_d = int(depth * self.output_ratio[0])
            out_h = int(height * self.output_ratio[1])
            out_w = int(width * self.output_ratio[2])
        
        # Generate random pooling regions
        d_indices = np.linspace(0, depth - self.kernel_size[0], out_d, dtype=int)
        h_indices = np.linspace(0, height - self.kernel_size[1], out_h, dtype=int)
        w_indices = np.linspace(0, width - self.kernel_size[2], out_w, dtype=int)
        
        out = np.zeros((batch_size, channels, out_d, out_h, out_w))
        indices = np.zeros((batch_size, channels, out_d, out_h, out_w, 3), dtype=int) if self.return_indices else None
        
        for b in range(batch_size):
            for c in range(channels):
                for i, d_idx in enumerate(d_indices):
                    for j, h_idx in enumerate(h_indices):
                        for k, w_idx in enumerate(w_indices):
                            region = x.data[b, c,
                                    d_idx:d_idx + self.kernel_size[0],
                                    h_idx:h_idx + self.kernel_size[1],
                                    w_idx:w_idx + self.kernel_size[2]]
                            out[b, c, i, j, k] = np.max(region)
                            if self.return_indices:
                                max_idx = np.unravel_index(np.argmax(region), region.shape)
                                indices[b, c, i, j, k] = [d_idx + max_idx[0],
                                                        h_idx + max_idx[1],
                                                        w_idx + max_idx[2]]
        
        if self.return_indices:
            return Tensor(out, requires_grad=True), indices
        return Tensor(out, requires_grad=True)

class LPPool1d(Module):
    def __init__(self, norm_type, kernel_size, stride=None):
        super().__init__()
        self.norm_type = norm_type
        self.kernel_size = kernel_size
        self.stride = stride if stride is not None else kernel_size

    def forward(self, x):
        batch_size, channels, length = x.data.shape
        out_length = (length - self.kernel_size) // self.stride + 1
        
        out = np.zeros((batch_size, channels, out_length))
        
        for b in range(batch_size):
            for c in range(channels):
                for i in range(out_length):
                    start_idx = i * self.stride
                    end_idx = start_idx + self.kernel_size
                    region = x.data[b, c, start_idx:end_idx]
                    out[b, c, i] = np.power(np.sum(np.power(np.abs(region), self.norm_type)),
                                          1.0 / self.norm_type)
        
        return Tensor(out, requires_grad=True)

class LPPool2d(Module):
    def __init__(self, norm_type, kernel_size, stride=None):
        super().__init__()
        self.norm_type = norm_type
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if stride is not None else self.kernel_size

    def forward(self, x):
        batch_size, channels, height, width = x.data.shape
        stride_h, stride_w = self.stride if isinstance(self.stride, tuple) else (self.stride, self.stride)
        kernel_h, kernel_w = self.kernel_size
        
        out_height = (height - kernel_h) // stride_h + 1
        out_width = (width - kernel_w) // stride_w + 1
        
        out = np.zeros((batch_size, channels, out_height, out_width))
        
        for b in range(batch_size):
            for c in range(channels):
                for i in range(out_height):
                    for j in range(out_width):
                        start_h = i * stride_h
                        start_w = j * stride_w
                        region = x.data[b, c,
                                start_h:start_h + kernel_h,
                                start_w:start_w + kernel_w]
                        out[b, c, i, j] = np.power(
                            np.sum(np.power(np.abs(region), self.norm_type)),
                            1.0 / self.norm_type
                        )
        
        return Tensor(out, requires_grad=True)