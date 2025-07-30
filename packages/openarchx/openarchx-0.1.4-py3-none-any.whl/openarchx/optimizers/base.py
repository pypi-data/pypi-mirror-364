import numpy as np
from abc import ABC, abstractmethod

class Optimizer(ABC):
    def __init__(self, parameters, lr=0.001, weight_decay=0.0, clip_grad=None):
        self.parameters = parameters
        self.lr = lr
        self.weight_decay = weight_decay
        self.clip_grad = clip_grad

    def clip_gradients(self):
        if self.clip_grad is not None:
            for param in self.parameters:
                if param.grad is not None:
                    np.clip(param.grad, -self.clip_grad, self.clip_grad, out=param.grad)

    @abstractmethod
    def step(self):
        pass

    def zero_grad(self):
        for param in self.parameters:
            if param.grad is not None:
                param.grad.fill(0)