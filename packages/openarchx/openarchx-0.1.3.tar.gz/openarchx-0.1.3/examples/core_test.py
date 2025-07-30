import numpy as np
import traceback
import sys
from openarchx.core.tensor import Tensor
from openarchx.nn.module import Module
from openarchx.layers.cnn import Conv2d, MaxPool2d
from openarchx.layers.base import Linear
from openarchx.optimizers.adam import Adam
from openarchx.layers.activations import relu

def print_separator():
    print("\n" + "="*50 + "\n")

def softmax(x):
    """Stable softmax implementation"""
    if isinstance(x, Tensor):
        x = x.data
    x = x - np.max(x, axis=1, keepdims=True)  # For numerical stability
    exp_x = np.exp(x)
    return exp_x / exp_x.sum(axis=1, keepdims=True)

def cross_entropy_loss(pred, target):
    """Stable cross entropy loss calculation"""
    if isinstance(pred, Tensor):
        pred = pred.data
    if isinstance(target, Tensor):
        target = target.data
    
    epsilon = 1e-7
    pred_clipped = np.clip(pred, epsilon, 1 - epsilon)
    return -np.mean(np.sum(target * np.log(pred_clipped), axis=1))

def test_tensor_ops():
    print_separator()
    print("Testing basic tensor operations...")
    
    try:
        # Test creation and basic ops
        a = Tensor(np.array([[1, 2], [3, 4]]), requires_grad=True)
        b = Tensor(np.array([[5, 6], [7, 8]]), requires_grad=True)
        
        print("Addition:")
        c = a + b
        print(c.data)
        
        print("\nMatrix multiplication:")
        d = a @ b
        print(d.data)
        
        print("\nReshape and transpose:")
        e = a.reshape(4)
        print(f"Reshaped: {e.data}")
        f = a.transpose(1, 0)
        print(f"Transposed: {f.data}")
        
        print("\nTensor operations test passed!")
    except Exception as e:
        print(f"Tensor operations error: {e}")
        traceback.print_exc()

def test_conv_layer():
    print_separator()
    print("Testing convolution layer...")
    
    try:
        # Create small input
        x = np.random.randn(2, 3, 4, 4)  # [batch_size, channels, height, width]
        x_tensor = Tensor(x)
        
        # Create conv layer
        conv = Conv2d(in_channels=3, out_channels=2, kernel_size=3, padding=1)
        
        # Forward pass
        out = conv(x_tensor)
        print(f"Conv2d input shape: {x.shape}")
        print(f"Conv2d output shape: {out.data.shape}")
        print("\nConvolution layer test passed!")
        
    except Exception as e:
        print(f"Conv2d error: {e}")
        traceback.print_exc()

class SimpleNet(Module):
    def __init__(self):
        super().__init__()
        self.conv1 = Conv2d(1, 4, kernel_size=3, padding=1)
        self.fc1 = Linear(64, 10)  # Fixed: 4 * 4 * 4 = 64 input features
    
    def forward(self, x):
        x = relu(self.conv1(x))
        batch_size = x.data.shape[0]
        x = x.reshape(batch_size, -1)  # Flatten conv output
        x = self.fc1(x)
        probs = softmax(x)  # Apply softmax to logits
        return Tensor(probs, requires_grad=True)

def test_small_network():
    print_separator()
    print("Testing small network...")
    
    try:
        # Create small input
        np.random.seed(42)  # For reproducibility
        x = np.random.randn(2, 1, 4, 4)  # [batch_size, channels, height, width]
        y = np.zeros((2, 10))  # One-hot encoded targets
        y[:, 0] = 1  # Set first class as target
        
        # Create model and optimizer
        model = SimpleNet()
        optimizer = Adam(model.parameters(), lr=0.01)
        
        # Training step
        x_tensor = Tensor(x)
        y_tensor = Tensor(y)
        
        print(f"Input shape: {x.shape}")
        
        # Forward pass
        pred = model(x_tensor)
        print(f"Output shape: {pred.data.shape}")
        
        # Calculate loss
        loss = cross_entropy_loss(pred, y_tensor)
        print(f"Initial loss: {loss:.4f}")
        
        # Backward pass
        loss_tensor = Tensor(np.array(loss), requires_grad=True)
        optimizer.zero_grad()
        loss_tensor.backward()
        optimizer.step()
        
        # Another forward pass to check if loss decreased
        pred = model(x_tensor)
        new_loss = cross_entropy_loss(pred, y_tensor)
        print(f"Loss after one step: {new_loss:.4f}")
        print("\nNetwork training test passed!")
        
    except Exception as e:
        print(f"Training error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting core functionality tests...")
    test_tensor_ops()
    test_conv_layer()
    test_small_network()
    print("\nTests completed!")