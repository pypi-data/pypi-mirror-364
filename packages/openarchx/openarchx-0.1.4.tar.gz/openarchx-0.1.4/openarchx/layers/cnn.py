import numpy as np
from ..core.tensor import Tensor
from ..nn.module import Module

class Conv2d(Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if isinstance(stride, tuple) else (stride, stride)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)
        
        # Initialize weights using He initialization
        scale = np.sqrt(2.0 / (in_channels * self.kernel_size[0] * self.kernel_size[1]))
        self.weight = Tensor(
            np.random.normal(0, scale, 
                           (out_channels, in_channels, *self.kernel_size)),
            requires_grad=True
        )
        self.bias = Tensor(np.zeros(out_channels), requires_grad=True)
    
    def _extract_patches(self, x, k_h, k_w, stride_h, stride_w):
        """Extract patches from input tensor efficiently"""
        batch_size, channels, height, width = x.shape
        
        # Calculate output dimensions
        out_h = (height - k_h) // stride_h + 1
        out_w = (width - k_w) // stride_w + 1
        
        # Initialize patches array
        patches = np.zeros((batch_size, out_h * out_w, channels * k_h * k_w))
        
        # Extract patches
        patch_idx = 0
        for i in range(0, height - k_h + 1, stride_h):
            for j in range(0, width - k_w + 1, stride_w):
                # Extract patch for all batches and channels
                patch = x[:, :, i:i+k_h, j:j+k_w]
                # Reshape patch to (batch_size, channels * k_h * k_w)
                patches[:, patch_idx, :] = patch.reshape(batch_size, -1)
                patch_idx += 1
        
        return patches, out_h, out_w
    
    def forward(self, x):
        batch_size, C, H, W = x.data.shape
        pad_h, pad_w = self.padding
        stride_h, stride_w = self.stride
        k_h, k_w = self.kernel_size
        
        # Add padding if needed
        if pad_h > 0 or pad_w > 0:
            x_padded = np.pad(x.data, ((0,0), (0,0), (pad_h,pad_h), (pad_w,pad_w)), mode='constant')
        else:
            x_padded = x.data
        
        # Extract patches
        patches, H_out, W_out = self._extract_patches(x_padded, k_h, k_w, stride_h, stride_w)
        
        # Reshape weights to [out_channels, in_channels * k_h * k_w]
        w_reshaped = self.weight.data.reshape(self.out_channels, -1)
        
        # Compute convolution using matrix multiplication
        out = patches @ w_reshaped.T  # [batch_size, H_out * W_out, out_channels]
        out = out.transpose(0, 2, 1).reshape(batch_size, self.out_channels, H_out, W_out)
        
        # Add bias
        out += self.bias.data.reshape(1, -1, 1, 1)
        
        return Tensor(out, requires_grad=True)

class MaxPool2d(Module):
    def __init__(self, kernel_size, stride=None):
        super().__init__()
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = self.kernel_size if stride is None else (stride if isinstance(stride, tuple) else (stride, stride))
    
    def forward(self, x):
        batch_size, C, H, W = x.data.shape
        k_h, k_w = self.kernel_size
        stride_h, stride_w = self.stride
        
        # Calculate output dimensions
        H_out = (H - k_h) // stride_h + 1
        W_out = (W - k_w) // stride_w + 1
        
        # Initialize output array
        out = np.zeros((batch_size, C, H_out, W_out))
        
        # Perform max pooling
        for b in range(batch_size):
            for c in range(C):
                for h in range(H_out):
                    for w in range(W_out):
                        h_start = h * stride_h
                        w_start = w * stride_w
                        h_end = h_start + k_h
                        w_end = w_start + k_w
                        
                        pool_region = x.data[b, c, h_start:h_end, w_start:w_end]
                        out[b, c, h, w] = np.max(pool_region)
        
        return Tensor(out, requires_grad=True)

class BatchNorm2d(Module):
    def __init__(self, num_features, eps=1e-5, momentum=0.1):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        
        # Parameters
        self.gamma = Tensor(np.ones(num_features), requires_grad=True)
        self.beta = Tensor(np.zeros(num_features), requires_grad=True)
        
        # Running estimates
        self.running_mean = np.zeros(num_features)
        self.running_var = np.ones(num_features)
        
        # Training mode flag
        self.training = True
    
    def forward(self, x):
        if self.training:
            # Calculate batch statistics
            batch_mean = x.data.mean(axis=(0,2,3), keepdims=True)
            batch_var = x.data.var(axis=(0,2,3), keepdims=True)
            
            # Update running statistics
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * batch_mean.squeeze()
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * batch_var.squeeze()
            
            # Normalize
            x_normalized = (x.data - batch_mean) / np.sqrt(batch_var + self.eps)
        else:
            # Use running statistics
            x_normalized = (x.data - self.running_mean.reshape(1,-1,1,1)) / \
                         np.sqrt(self.running_var.reshape(1,-1,1,1) + self.eps)
        
        # Apply scale and shift
        out = self.gamma.data.reshape(1,-1,1,1) * x_normalized + \
              self.beta.data.reshape(1,-1,1,1)
        
        return Tensor(out, requires_grad=True)