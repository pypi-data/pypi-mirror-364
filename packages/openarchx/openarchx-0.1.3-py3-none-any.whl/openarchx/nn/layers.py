import numpy as np
from ..core.tensor import Tensor
from .module import Module

class Linear(Module):
    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        scale = np.sqrt(2.0 / in_features)
        self.weight = Tensor(np.random.normal(0, scale, (in_features, out_features)), requires_grad=True)
        self.bias = Tensor(np.zeros(out_features), requires_grad=True) if bias else None

    def forward(self, x):
        if not isinstance(x, Tensor):
            x = Tensor(x, requires_grad=True)
        out = x @ self.weight
        if self.bias is not None:
            out = out + self.bias
        return out

class Conv1d(Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, bias=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size,)
        self.stride = stride if isinstance(stride, tuple) else (stride,)
        self.padding = padding if isinstance(padding, tuple) else (padding,)
        
        scale = np.sqrt(2.0 / (in_channels * kernel_size))
        self.weight = Tensor(
            np.random.normal(0, scale, (out_channels, in_channels, kernel_size)),
            requires_grad=True
        )
        self.bias = Tensor(np.zeros(out_channels), requires_grad=True) if bias else None

    def forward(self, x):
        # Implementation for 1D convolution
        pass  # TODO: Implement actual convolution

class Conv2d(Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, bias=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if isinstance(stride, tuple) else (stride, stride)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)
        
        scale = np.sqrt(2.0 / (in_channels * kernel_size * kernel_size))
        self.weight = Tensor(
            np.random.normal(0, scale, (out_channels, in_channels, *self.kernel_size)),
            requires_grad=True
        )
        self.bias = Tensor(np.zeros(out_channels), requires_grad=True) if bias else None

    def forward(self, x):
        # Implementation for 2D convolution
        pass  # TODO: Implement actual convolution

class BatchNorm1d(Module):
    def __init__(self, num_features, eps=1e-5, momentum=0.1):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        
        self.gamma = Tensor(np.ones(num_features), requires_grad=True)
        self.beta = Tensor(np.zeros(num_features), requires_grad=True)
        self.running_mean = Tensor(np.zeros(num_features), requires_grad=False)
        self.running_var = Tensor(np.ones(num_features), requires_grad=False)

    def forward(self, x):
        if self.training:
            mean = x.mean(axis=0)
            var = x.var(axis=0)
            
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var
        else:
            mean = self.running_mean
            var = self.running_var
        
        x_norm = (x - mean) / np.sqrt(var + self.eps)
        return self.gamma * x_norm + self.beta

class LayerNorm(Module):
    def __init__(self, normalized_shape, eps=1e-5):
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.gamma = Tensor(np.ones(normalized_shape), requires_grad=True)
        self.beta = Tensor(np.zeros(normalized_shape), requires_grad=True)

    def forward(self, x):
        mean = x.mean(axis=-1, keepdims=True)
        var = x.var(axis=-1, keepdims=True)
        return self.gamma * (x - mean) / np.sqrt(var + self.eps) + self.beta

class Embedding(Module):
    def __init__(self, num_embeddings, embedding_dim):
        super().__init__()
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.weight = Tensor(
            np.random.normal(0, 0.02, (num_embeddings, embedding_dim)),
            requires_grad=True
        )

    def forward(self, x):
        return self.weight[x]

class ConvTranspose1d(Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, output_padding=0, bias=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size,)
        self.stride = stride if isinstance(stride, tuple) else (stride,)
        self.padding = padding if isinstance(padding, tuple) else (padding,)
        self.output_padding = output_padding if isinstance(output_padding, tuple) else (output_padding,)
        
        scale = np.sqrt(2.0 / (in_channels * kernel_size))
        self.weight = Tensor(
            np.random.normal(0, scale, (in_channels, out_channels, *self.kernel_size)),
            requires_grad=True
        )
        if bias:
            self.bias = Tensor(np.zeros(out_channels), requires_grad=True)
        else:
            self.bias = None

    def forward(self, x):
        # TODO: Implement actual transposed convolution
        pass

class ConvTranspose2d(Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, output_padding=0, bias=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if isinstance(stride, tuple) else (stride, stride)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)
        self.output_padding = output_padding if isinstance(output_padding, tuple) else (output_padding, output_padding)
        
        scale = np.sqrt(2.0 / (in_channels * kernel_size * kernel_size))
        self.weight = Tensor(
            np.random.normal(0, scale, (in_channels, out_channels, *self.kernel_size)),
            requires_grad=True
        )
        if bias:
            self.bias = Tensor(np.zeros(out_channels), requires_grad=True)
        else:
            self.bias = None

    def forward(self, x):
        # TODO: Implement actual transposed convolution
        pass

class ConvTranspose3d(Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, output_padding=0, bias=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size, kernel_size)
        self.stride = stride if isinstance(stride, tuple) else (stride, stride, stride)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding, padding)
        self.output_padding = output_padding if isinstance(output_padding, tuple) else (output_padding, output_padding, output_padding)
        
        scale = np.sqrt(2.0 / (in_channels * kernel_size * kernel_size * kernel_size))
        self.weight = Tensor(
            np.random.normal(0, scale, (in_channels, out_channels, *self.kernel_size)),
            requires_grad=True
        )
        if bias:
            self.bias = Tensor(np.zeros(out_channels), requires_grad=True)
        else:
            self.bias = None

    def forward(self, x):
        # TODO: Implement actual transposed convolution
        pass

class InstanceNorm1d(Module):
    def __init__(self, num_features, eps=1e-5, momentum=0.1, affine=True):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        self.affine = affine
        
        if affine:
            self.weight = Tensor(np.ones(num_features), requires_grad=True)
            self.bias = Tensor(np.zeros(num_features), requires_grad=True)

    def forward(self, x):
        mean = np.mean(x.data, axis=(2,), keepdims=True)
        var = np.var(x.data, axis=(2,), keepdims=True)
        
        x_norm = (x.data - mean) / np.sqrt(var + self.eps)
        
        if self.affine:
            x_norm = self.weight.data.reshape(-1, 1) * x_norm + self.bias.data.reshape(-1, 1)
        
        return Tensor(x_norm, requires_grad=True)

class InstanceNorm2d(Module):
    def __init__(self, num_features, eps=1e-5, momentum=0.1, affine=True):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        self.affine = affine
        
        if affine:
            self.weight = Tensor(np.ones(num_features), requires_grad=True)
            self.bias = Tensor(np.zeros(num_features), requires_grad=True)

    def forward(self, x):
        mean = np.mean(x.data, axis=(2, 3), keepdims=True)
        var = np.var(x.data, axis=(2, 3), keepdims=True)
        
        x_norm = (x.data - mean) / np.sqrt(var + self.eps)
        
        if self.affine:
            x_norm = self.weight.data.reshape(-1, 1, 1) * x_norm + self.bias.data.reshape(-1, 1, 1)
        
        return Tensor(x_norm, requires_grad=True)

class InstanceNorm3d(Module):
    def __init__(self, num_features, eps=1e-5, momentum=0.1, affine=True):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        self.affine = affine
        
        if affine:
            self.weight = Tensor(np.ones(num_features), requires_grad=True)
            self.bias = Tensor(np.zeros(num_features), requires_grad=True)

    def forward(self, x):
        mean = np.mean(x.data, axis=(2, 3, 4), keepdims=True)
        var = np.var(x.data, axis=(2, 3, 4), keepdims=True)
        
        x_norm = (x.data - mean) / np.sqrt(var + self.eps)
        
        if self.affine:
            x_norm = self.weight.data.reshape(-1, 1, 1, 1) * x_norm + self.bias.data.reshape(-1, 1, 1, 1)
        
        return Tensor(x_norm, requires_grad=True)

class GroupNorm(Module):
    def __init__(self, num_groups, num_channels, eps=1e-5, affine=True):
        super().__init__()
        self.num_groups = num_groups
        self.num_channels = num_channels
        self.eps = eps
        self.affine = affine
        
        if affine:
            self.weight = Tensor(np.ones(num_channels), requires_grad=True)
            self.bias = Tensor(np.zeros(num_channels), requires_grad=True)

    def forward(self, x):
        N, C, *spatial = x.data.shape
        x_reshaped = x.data.reshape(N, self.num_groups, -1)
        
        mean = np.mean(x_reshaped, axis=2, keepdims=True)
        var = np.var(x_reshaped, axis=2, keepdims=True)
        
        x_norm = (x_reshaped - mean) / np.sqrt(var + self.eps)
        x_norm = x_norm.reshape(N, C, *spatial)
        
        if self.affine:
            shape = (1, -1) + (1,) * len(spatial)
            x_norm = self.weight.data.reshape(shape) * x_norm + self.bias.data.reshape(shape)
        
        return Tensor(x_norm, requires_grad=True)

class LocalResponseNorm(Module):
    def __init__(self, size, alpha=1e-4, beta=0.75, k=1.0):
        super().__init__()
        self.size = size
        self.alpha = alpha
        self.beta = beta
        self.k = k

    def forward(self, x):
        N, C, *spatial = x.data.shape
        half_size = self.size // 2
        
        square = x.data ** 2
        for i in range(C):
            start = max(0, i - half_size)
            end = min(C, i + half_size + 1)
            scale = self.k + self.alpha * np.sum(square[:, start:end], axis=1, keepdims=True)
            x.data[:, i] /= scale ** self.beta
        
        return Tensor(x.data, requires_grad=True)

class EmbeddingBag(Module):
    def __init__(self, num_embeddings, embedding_dim, mode='mean'):
        super().__init__()
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.mode = mode
        self.weight = Tensor(
            np.random.normal(0, 0.02, (num_embeddings, embedding_dim)),
            requires_grad=True
        )

    def forward(self, x, offsets=None):
        embeddings = self.weight.data[x.data]
        if offsets is None:
            # Treat entire input as a single bag
            if self.mode == 'mean':
                return Tensor(np.mean(embeddings, axis=1), requires_grad=True)
            elif self.mode == 'sum':
                return Tensor(np.sum(embeddings, axis=1), requires_grad=True)
            else:  # max
                return Tensor(np.max(embeddings, axis=1), requires_grad=True)
        
        # Handle multiple bags using offsets
        result = []
        for i in range(len(offsets) - 1):
            start, end = offsets[i:i+2]
            if self.mode == 'mean':
                bag = np.mean(embeddings[start:end], axis=0)
            elif self.mode == 'sum':
                bag = np.sum(embeddings[start:end], axis=0)
            else:  # max
                bag = np.max(embeddings[start:end], axis=0)
            result.append(bag)
        
        return Tensor(np.stack(result), requires_grad=True)