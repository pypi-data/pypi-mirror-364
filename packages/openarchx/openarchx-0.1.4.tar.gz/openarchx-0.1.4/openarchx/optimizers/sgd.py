import numpy as np
from .base import Optimizer

class BGD(Optimizer):
    """Batch Gradient Descent"""
    def step(self):
        self.clip_gradients()
        for param in self.parameters:
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                param.data -= self.lr * grad

class MBGD(Optimizer):
    """Mini-Batch Gradient Descent"""
    def __init__(self, parameters, lr=0.001, batch_size=32, weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.batch_size = batch_size

    def step(self):
        self.clip_gradients()
        for param in self.parameters:
            if param.grad is not None:
                grad = param.grad / self.batch_size
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                param.data -= self.lr * grad

class SGD(Optimizer):
    """SGD with Momentum"""
    def __init__(self, parameters, lr=0.001, momentum=0.9, weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.momentum = momentum
        self.v = [np.zeros_like(param.data) for param in parameters]

    def step(self):
        self.clip_gradients()
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                self.v[i] = self.momentum * self.v[i] - self.lr * grad
                param.data += self.v[i]

class NAG(Optimizer):
    """Nesterov Accelerated Gradient"""
    def __init__(self, parameters, lr=0.001, momentum=0.9, weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.momentum = momentum
        self.v = [np.zeros_like(param.data) for param in parameters]

    def step(self):
        self.clip_gradients()
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                v_prev = self.v[i].copy()
                self.v[i] = self.momentum * self.v[i] - self.lr * grad
                param.data += -self.momentum * v_prev + (1 + self.momentum) * self.v[i]