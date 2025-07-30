import numpy as np
from ..core.tensor import Tensor
from ..nn.module import Module

class Linear(Module):
    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # Initialize weights using He initialization
        scale = np.sqrt(2.0 / in_features)
        self.weight = Tensor(
            np.random.normal(0, scale, (in_features, out_features)),  # Changed orientation to (in_features, out_features)
            requires_grad=True
        )
        
        if bias:
            self.bias = Tensor(np.zeros(out_features), requires_grad=True)
        else:
            self.bias = None
    
    def forward(self, x):
        if not isinstance(x, Tensor):
            x = Tensor(x, requires_grad=True)
        
        # Matrix multiplication - (batch_size, in_features) @ (in_features, out_features)
        out = x @ self.weight
        
        # Add bias if it exists
        if self.bias is not None:
            out = out + self.bias
        
        return out
    
    def parameters(self):
        params = [self.weight]
        if self.bias is not None:
            params.append(self.bias)
        return params