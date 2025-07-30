import numpy as np
from ..core.tensor import Tensor
from .module import Module

class ReLU(Module):
    def forward(self, x):
        return Tensor(np.maximum(0, x.data), requires_grad=True)

class LeakyReLU(Module):
    def __init__(self, negative_slope=0.01):
        super().__init__()
        self.negative_slope = negative_slope

    def forward(self, x):
        return Tensor(np.where(x.data > 0, x.data, self.negative_slope * x.data), requires_grad=True)

class PReLU(Module):
    def __init__(self, num_parameters=1, init=0.25):
        super().__init__()
        self.weight = Tensor(np.full(num_parameters, init), requires_grad=True)

    def forward(self, x):
        return Tensor(np.where(x.data > 0, x.data, self.weight.data * x.data), requires_grad=True)

class ELU(Module):
    def __init__(self, alpha=1.0):
        super().__init__()
        self.alpha = alpha

    def forward(self, x):
        return Tensor(np.where(x.data > 0, x.data, self.alpha * (np.exp(x.data) - 1)), requires_grad=True)

class GELU(Module):
    def forward(self, x):
        return Tensor(0.5 * x.data * (1 + np.tanh(np.sqrt(2 / np.pi) * (x.data + 0.044715 * x.data**3))), requires_grad=True)

class Sigmoid(Module):
    def forward(self, x):
        return Tensor(1 / (1 + np.exp(-x.data)), requires_grad=True)

class Tanh(Module):
    def forward(self, x):
        return Tensor(np.tanh(x.data), requires_grad=True)

class Softmax(Module):
    def __init__(self, dim=-1):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        exp_x = np.exp(x.data - np.max(x.data, axis=self.dim, keepdims=True))
        return Tensor(exp_x / np.sum(exp_x, axis=self.dim, keepdims=True), requires_grad=True)

class LogSoftmax(Module):
    def __init__(self, dim=-1):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        exp_x = np.exp(x.data - np.max(x.data, axis=self.dim, keepdims=True))
        softmax = exp_x / np.sum(exp_x, axis=self.dim, keepdims=True)
        return Tensor(np.log(softmax), requires_grad=True)

class SELU(Module):
    def __init__(self):
        super().__init__()
        self.alpha = 1.6732632423543772848170429916717
        self.scale = 1.0507009873554804934193349852946

    def forward(self, x):
        return Tensor(self.scale * np.where(x.data > 0, x.data, 
                                          self.alpha * (np.exp(x.data) - 1)), requires_grad=True)

class Hardtanh(Module):
    def __init__(self, min_val=-1.0, max_val=1.0):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val

    def forward(self, x):
        return Tensor(np.clip(x.data, self.min_val, self.max_val), requires_grad=True)

class SiLU(Module):  # Also known as Swish
    def forward(self, x):
        return Tensor(x.data * (1 / (1 + np.exp(-x.data))), requires_grad=True)

class Mish(Module):
    def forward(self, x):
        return Tensor(x.data * np.tanh(np.log(1 + np.exp(x.data))), requires_grad=True)

class ActX(Module):
    """
    Advanced activation function that combines multiple activation types with learnable parameters.
    ActX(x) = α * GELU(x) + β * SiLU(x) + γ * tanh(λx)
    where α, β, γ, and λ are learnable parameters
    """
    def __init__(self, num_parameters=1, init_alpha=0.5, init_beta=0.5, init_gamma=0.25, init_lambda=1.0):
        super().__init__()
        self.num_parameters = num_parameters
        
        # Initialize learnable parameters
        self.alpha = Tensor(np.full(num_parameters, init_alpha), requires_grad=True)
        self.beta = Tensor(np.full(num_parameters, init_beta), requires_grad=True)
        self.gamma = Tensor(np.full(num_parameters, init_gamma), requires_grad=True)
        self.lambda_param = Tensor(np.full(num_parameters, init_lambda), requires_grad=True)

    def forward(self, x):
        # GELU component
        gelu = 0.5 * x.data * (1 + np.tanh(np.sqrt(2 / np.pi) * (x.data + 0.044715 * x.data**3)))
        
        # SiLU (Swish) component
        silu = x.data * (1 / (1 + np.exp(-x.data)))
        
        # Tanh component with learnable frequency
        tanh = np.tanh(self.lambda_param.data.reshape(-1, 1, 1) * x.data)
        
        # Combine components with learnable weights
        alpha = self.alpha.data.reshape(-1, 1, 1)
        beta = self.beta.data.reshape(-1, 1, 1)
        gamma = self.gamma.data.reshape(-1, 1, 1)
        
        result = alpha * gelu + beta * silu + gamma * tanh
        
        return Tensor(result, requires_grad=True)

    def parameters(self):
        return [self.alpha, self.beta, self.gamma, self.lambda_param]