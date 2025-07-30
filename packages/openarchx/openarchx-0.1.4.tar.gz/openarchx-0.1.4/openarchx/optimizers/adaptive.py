import numpy as np
from .base import Optimizer

class Adagrad(Optimizer):
    """Adaptive Gradient Algorithm"""
    def __init__(self, parameters, lr=0.01, eps=1e-8, weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.eps = eps
        self.G = [np.zeros_like(param.data) for param in parameters]

    def step(self):
        self.clip_gradients()
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                self.G[i] += np.square(grad)
                param.data -= self.lr * grad / (np.sqrt(self.G[i]) + self.eps)

class Adadelta(Optimizer):
    """Adaptive Delta Algorithm"""
    def __init__(self, parameters, rho=0.95, eps=1e-6, weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, 1.0, weight_decay, clip_grad)  # lr=1.0 as it's not used
        self.rho = rho
        self.eps = eps
        self.G = [np.zeros_like(param.data) for param in parameters]
        self.delta = [np.zeros_like(param.data) for param in parameters]

    def step(self):
        self.clip_gradients()
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                
                self.G[i] = self.rho * self.G[i] + (1 - self.rho) * np.square(grad)
                rms_g = np.sqrt(self.G[i] + self.eps)
                rms_delta = np.sqrt(self.delta[i] + self.eps)
                
                update = -rms_delta / rms_g * grad
                param.data += update
                
                self.delta[i] = self.rho * self.delta[i] + (1 - self.rho) * np.square(update)

class RMSprop(Optimizer):
    """Root Mean Square Propagation"""
    def __init__(self, parameters, lr=0.01, alpha=0.99, eps=1e-8, weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.alpha = alpha
        self.eps = eps
        self.G = [np.zeros_like(param.data) for param in parameters]

    def step(self):
        self.clip_gradients()
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                self.G[i] = self.alpha * self.G[i] + (1 - self.alpha) * np.square(grad)
                param.data -= self.lr * grad / (np.sqrt(self.G[i]) + self.eps)