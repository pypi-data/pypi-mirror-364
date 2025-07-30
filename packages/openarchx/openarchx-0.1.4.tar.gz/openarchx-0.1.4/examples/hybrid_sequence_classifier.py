import numpy as np
from openarchx.core.tensor import Tensor
from openarchx.layers.transformer import TransformerEncoderLayer
from openarchx.layers.base import Linear
from openarchx.quantum.circuit import QuantumLayer
from openarchx.nn.module import Module
from openarchx.optimizers.adam import Adam

class QuantumFeatureExtractor(QuantumLayer):
    def __init__(self, num_qubits=4):
        super().__init__(num_qubits, num_params=num_qubits * 3)
        # Initialize parameters with smaller values for better stability
        self.params = Tensor(np.random.randn(num_qubits * 3) * 0.01, requires_grad=True)
        
    def build_circuit(self):
        # Create a variational quantum circuit for feature extraction
        for i in range(self.circuit.num_qubits):
            self.circuit.h(i)  # Initialize with Hadamard gates
        
        # Apply parameterized rotation gates with controlled scaling
        param_idx = 0
        for i in range(self.circuit.num_qubits):
            self.circuit.rx(self.params[param_idx] * np.pi, i)  # Scale to [-π, π]
            param_idx += 1
            self.circuit.ry(self.params[param_idx] * np.pi, i)
            param_idx += 1
            self.circuit.rz(self.params[param_idx] * np.pi, i)
            param_idx += 1
        
        # Create entanglement between qubits
        for i in range(self.circuit.num_qubits - 1):
            self.circuit.cnot(i, i + 1)

class HybridSequenceClassifier(Module):
    def __init__(self, seq_length, d_model, nhead, num_classes):
        super().__init__()
        self.d_model = d_model
        
        # Initialize transformer with smaller dimension for better convergence
        self.transformer = TransformerEncoderLayer(d_model, nhead, dim_feedforward=d_model * 2)
        
        # Quantum circuit for feature extraction
        self.quantum = QuantumFeatureExtractor(num_qubits=4)
        
        # Classical layers with careful initialization
        self.pooling = Linear(seq_length * d_model, d_model)
        self.quantum_proj = Linear(16, d_model)  # 16 = 2^4 (quantum state size)
        self.classifier = Linear(d_model, num_classes)
        
        # Initialize the projection layers with smaller weights
        self.quantum_proj.weights.data *= 0.01
        self.classifier.weights.data *= 0.01
    
    def forward(self, x):
        # Process sequence with transformer
        trans_out = self.transformer.forward(x)
        
        # Flatten sequence for pooling
        batch_size = x.data.shape[0]
        trans_flat = trans_out.reshape(batch_size, -1)
        trans_features = self.pooling.forward(trans_flat)
        
        # Extract quantum features
        quantum_state = self.quantum.forward(None)
        # Expand quantum features for batch dimension
        quantum_state = Tensor(np.tile(quantum_state.data, (batch_size, 1)))
        quantum_features = self.quantum_proj.forward(quantum_state)
        
        # Combine classical and quantum features with scaling
        combined_features = trans_features + 0.1 * quantum_features
        
        # Classify
        return self.classifier.forward(combined_features)

def generate_dummy_sequence_data(num_samples=100, seq_length=10, d_model=64, num_classes=2):
    """Generate dummy sequence classification data"""
    # Generate more structured data for better training
    X = np.random.randn(num_samples, seq_length, d_model) * 0.1
    # Add some patterns based on class
    y = np.random.randint(0, num_classes, size=(num_samples,))
    for i in range(num_samples):
        pattern = np.random.randn(d_model) * 0.1
        X[i] += pattern * (y[i] + 1)  # Add class-dependent patterns
    
    # Normalize input
    X = (X - X.mean(axis=0, keepdims=True)) / (X.std(axis=0, keepdims=True) + 1e-8)
    
    # Convert to one-hot encoded labels
    y_one_hot = np.zeros((num_samples, num_classes))
    y_one_hot[np.arange(num_samples), y] = 1
    
    return X, y_one_hot

def cosine_decay_schedule(initial_lr, epoch, total_epochs):
    """Cosine learning rate decay schedule"""
    return initial_lr * 0.5 * (1 + np.cos(np.pi * epoch / total_epochs))

def train_hybrid_model(model, X, y, num_epochs=20, batch_size=16, initial_lr=0.001):
    # Use Adam optimizer instead of SGD for better convergence
    optimizer = Adam(
        model.parameters(),
        lr=initial_lr,
        betas=(0.9, 0.999),
        eps=1e-8
    )
    
    num_samples = len(X)
    num_batches = num_samples // batch_size
    best_accuracy = 0
    
    for epoch in range(num_epochs):
        total_loss = 0
        correct_predictions = 0
        
        # Shuffle data
        indices = np.random.permutation(num_samples)
        X = X[indices]
        y = y[indices]
        
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = start_idx + batch_size
            
            # Get batch
            batch_X = X[start_idx:end_idx]
            batch_y = y[start_idx:end_idx]
            
            # Convert to tensors
            x_tensor = Tensor(batch_X)
            y_tensor = Tensor(batch_y)
            
            # Forward pass
            pred = model(x_tensor)
            
            # Calculate cross-entropy loss with label smoothing
            smooth_y = y_tensor * 0.9 + 0.1 / y_tensor.data.shape[1]
            loss = -((smooth_y * pred.log()).sum(axis=-1)).mean()
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            for param in model.parameters():
                if param.grad is not None:
                    np.clip(param.grad, -1.0, 1.0, out=param.grad)
            
            # Update weights
            optimizer.step()
            
            # Calculate accuracy
            predictions = np.argmax(pred.data, axis=1)
            true_labels = np.argmax(batch_y, axis=1)
            correct_predictions += np.sum(predictions == true_labels)
            
            total_loss += loss.data
        
        # Calculate epoch metrics
        avg_loss = total_loss / num_batches
        accuracy = correct_predictions / num_samples
        
        # Track best accuracy
        if accuracy > best_accuracy:
            best_accuracy = accuracy
        
        print(f"Epoch {epoch + 1}/{num_epochs}")
        print(f"Average Loss: {avg_loss:.4f}")
        print(f"Accuracy: {accuracy:.4f} (Best: {best_accuracy:.4f})")
        print("-" * 30)

def main():
    # Model parameters - using smaller network for faster convergence
    seq_length = 10
    d_model = 32
    nhead = 4
    num_classes = 2
    
    # Create model
    model = HybridSequenceClassifier(seq_length, d_model, nhead, num_classes)
    
    # Generate dummy data with more structured patterns
    X_train, y_train = generate_dummy_sequence_data(
        num_samples=1000,
        seq_length=seq_length,
        d_model=d_model,
        num_classes=num_classes
    )
    
    # Train model with Adam optimizer
    train_hybrid_model(
        model, 
        X_train, 
        y_train,
        num_epochs=30,  # Increased epochs since Adam can handle longer training
        batch_size=32,
        initial_lr=0.001  # Typical Adam learning rate
    )

if __name__ == "__main__":
    main()