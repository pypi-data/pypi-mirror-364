import numpy as np

class OptX:
    def __init__(self, parameters, lr=0.001, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0.0, clip_grad=None, rectify=True,
                 lookahead_steps=5, lookahead_alpha=0.5):
        self.parameters = parameters
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.clip_grad = clip_grad
        self.rectify = rectify
        self.lookahead_steps = lookahead_steps
        self.lookahead_alpha = lookahead_alpha
        
        # Initialize momentum and velocity
        self.m = [np.zeros_like(param.data) for param in parameters]
        self.v = [np.zeros_like(param.data) for param in parameters]
        self.slow_weights = [param.data.copy() for param in parameters]
        self.t = 0
        self.step_counter = 0
        
        # Gradient variance tracking
        self.grad_var = [np.zeros_like(param.data) for param in parameters]
        
    def clip_gradients(self):
        if self.clip_grad is not None:
            for param in self.parameters:
                if param.grad is not None:
                    np.clip(param.grad, -self.clip_grad, self.clip_grad, out=param.grad)
                    
    def update_grad_variance(self, i, grad):
        # Update running variance of gradients
        if self.t > 1:
            self.grad_var[i] = 0.9 * self.grad_var[i] + 0.1 * (grad - self.m[i])**2

    def compute_adaptive_lr(self, i, v_hat):
        # Compute adaptive learning rate based on gradient variance
        if self.t > 1:
            variance_scaling = 1.0 / (1.0 + np.sqrt(self.grad_var[i]) + self.eps)
            return self.lr * variance_scaling
        return self.lr

    def step(self):
        self.t += 1
        self.step_counter += 1
        self.clip_gradients()
        
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                
                # Update momentum with bias correction
                self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
                m_hat = self.m[i] / (1 - self.beta1 ** self.t)
                
                # Update velocity with bias correction
                self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (grad ** 2)
                v_hat = self.v[i] / (1 - self.beta2 ** self.t)
                
                # Update gradient variance for adaptive scaling
                self.update_grad_variance(i, grad)
                
                # Compute adaptive learning rate
                adaptive_lr = self.compute_adaptive_lr(i, v_hat)
                
                # Compute update
                update = adaptive_lr * m_hat / (np.sqrt(v_hat) + self.eps)
                
                if self.rectify:
                    # Apply rectification to prevent overshooting
                    variance_ratio = np.sqrt(self.grad_var[i]) / (np.sqrt(v_hat) + self.eps)
                    update *= np.minimum(1.0, np.maximum(0.1, variance_ratio))
                
                # Apply update
                param.data -= update
                
                # Lookahead update
                if self.step_counter % self.lookahead_steps == 0:
                    # Move slow weights toward current parameters
                    self.slow_weights[i] += self.lookahead_alpha * (param.data - self.slow_weights[i])
                    # Update parameters to interpolated position
                    param.data = self.slow_weights[i].copy()
    
    def zero_grad(self):
        for param in self.parameters:
            if param.grad is not None:
                param.grad.fill(0)