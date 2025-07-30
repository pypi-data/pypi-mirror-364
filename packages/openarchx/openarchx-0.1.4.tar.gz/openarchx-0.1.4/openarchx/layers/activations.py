import numpy as np
from ..core.tensor import Tensor

class ReLU:
    def forward(self, x):
        return Tensor(np.maximum(0, x.data), requires_grad=x.requires_grad)
    
    def parameters(self):
        return []

class Sigmoid:
    def forward(self, x):
        out = 1 / (1 + np.exp(-x.data))
        return Tensor(out, requires_grad=x.requires_grad)
    
    def parameters(self):
        return []

class Tanh:
    def forward(self, x):
        out = np.tanh(x.data)
        return Tensor(out, requires_grad=x.requires_grad)
    
    def parameters(self):
        return []

class Softmax:
    def forward(self, x):
        exp_x = np.exp(x.data - np.max(x.data))
        out = exp_x / exp_x.sum(axis=-1, keepdims=True)
        return Tensor(out, requires_grad=x.requires_grad)
    
    def parameters(self):
        return []

def relu(x):
    """ReLU activation function"""
    return Tensor(np.maximum(0, x.data), requires_grad=True)

def sigmoid(x):
    """Sigmoid activation function"""
    return Tensor(1 / (1 + np.exp(-x.data)), requires_grad=True)

def tanh(x):
    """Tanh activation function"""
    return Tensor(np.tanh(x.data), requires_grad=True)

def softmax(x, axis=-1):
    """Softmax activation function"""
    exp_x = np.exp(x.data - np.max(x.data, axis=axis, keepdims=True))
    return Tensor(exp_x / exp_x.sum(axis=axis, keepdims=True), requires_grad=True)

def leaky_relu(x, alpha=0.01):
    """Leaky ReLU activation function"""
    return Tensor(np.where(x.data > 0, x.data, alpha * x.data), requires_grad=True)

def elu(x, alpha=1.0):
    """ELU activation function"""
    return Tensor(np.where(x.data > 0, x.data, alpha * (np.exp(x.data) - 1)), requires_grad=True)

def gelu(x):
    """GELU activation function"""
    return Tensor(0.5 * x.data * (1 + np.tanh(np.sqrt(2 / np.pi) * (x.data + 0.044715 * x.data**3))), requires_grad=True)