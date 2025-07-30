import numpy as np

class Adam:
    def __init__(self, parameters, lr=0.001, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0, clip_grad=None):
        self.parameters = parameters
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.clip_grad = clip_grad
        
        # Initialize momentum and velocity
        self.m = [np.zeros_like(param.data) for param in parameters]
        self.v = [np.zeros_like(param.data) for param in parameters]
        self.t = 0

    def clip_gradients(self):
        if self.clip_grad is not None:
            for param in self.parameters:
                if param.grad is not None:
                    np.clip(param.grad, -self.clip_grad, self.clip_grad, out=param.grad)

    def step(self):
        self.t += 1
        self.clip_gradients()
        
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                
                # Update momentum
                self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
                
                # Update velocity
                self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (grad ** 2)
                
                # Bias correction
                m_hat = self.m[i] / (1 - self.beta1 ** self.t)
                v_hat = self.v[i] / (1 - self.beta2 ** self.t)
                
                # Update parameters
                param.data -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
    
    def zero_grad(self):
        for param in self.parameters:
            if param.grad is not None:
                param.grad.fill(0)