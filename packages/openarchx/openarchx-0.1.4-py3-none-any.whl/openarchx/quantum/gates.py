import numpy as np
from ..core.tensor import Tensor

# Basic quantum gates as numpy arrays
class QuantumGates:
    @staticmethod
    def I():
        return np.array([[1, 0], [0, 1]], dtype=complex)
    
    @staticmethod
    def X():
        return np.array([[0, 1], [1, 0]], dtype=complex)
    
    @staticmethod
    def Y():
        return np.array([[0, -1j], [1j, 0]], dtype=complex)
    
    @staticmethod
    def Z():
        return np.array([[1, 0], [0, -1]], dtype=complex)
    
    @staticmethod
    def H():
        return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    
    @staticmethod
    def CNOT():
        return np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 1],
                        [0, 0, 1, 0]], dtype=complex)
    
    @staticmethod
    def RX(theta):
        return np.array([[np.cos(theta/2), -1j*np.sin(theta/2)],
                        [-1j*np.sin(theta/2), np.cos(theta/2)]], dtype=complex)
    
    @staticmethod
    def RY(theta):
        return np.array([[np.cos(theta/2), -np.sin(theta/2)],
                        [np.sin(theta/2), np.cos(theta/2)]], dtype=complex)
    
    @staticmethod
    def RZ(theta):
        return np.array([[np.exp(-1j*theta/2), 0],
                        [0, np.exp(1j*theta/2)]], dtype=complex)

class QuantumRegister:
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        # Initialize to |0>^⊗n state
        self.state = np.zeros(2**num_qubits, dtype=complex)
        self.state[0] = 1.0
    
    def apply_gate(self, gate, target_qubit):
        """Apply a single-qubit gate to the specified target qubit"""
        n = self.num_qubits
        
        # Create the full operator using tensor products
        op = np.array([[1]])
        for i in range(n):
            if i == target_qubit:
                op = np.kron(op, gate)
            else:
                op = np.kron(op, QuantumGates.I())
        
        self.state = op @ self.state
    
    def apply_controlled_gate(self, gate, control_qubit, target_qubit):
        """Apply a controlled gate with specified control and target qubits"""
        if abs(control_qubit - target_qubit) == 1:
            # Adjacent qubits can use the gate directly
            n = self.num_qubits
            op = np.array([[1]])
            for i in range(n):
                if i == min(control_qubit, target_qubit):
                    op = np.kron(op, gate)
                    i += 1  # Skip next qubit as it's part of the controlled operation
                else:
                    op = np.kron(op, QuantumGates.I())
        else:
            # Non-adjacent qubits need swap operations
            # This is a simplified implementation
            op = self._create_non_adjacent_controlled_op(gate, control_qubit, target_qubit)
        
        self.state = op @ self.state
    
    def measure(self, qubit=None):
        """Measure the specified qubit or the whole register"""
        if qubit is None:
            # Measure all qubits
            probs = np.abs(self.state) ** 2
            result = np.random.choice(len(self.state), p=probs)
            self.state = np.zeros_like(self.state)
            self.state[result] = 1.0
            return bin(result)[2:].zfill(self.num_qubits)
        else:
            # Measure single qubit
            # Project and renormalize the state
            raise NotImplementedError("Single qubit measurement not implemented yet")
    
    def _create_non_adjacent_controlled_op(self, gate, control, target):
        """Helper method to create controlled operations between non-adjacent qubits"""
        # This is a simplified implementation
        n = self.num_qubits
        dim = 2**n
        op = np.eye(dim, dtype=complex)
        
        # Create the controlled operation
        ctrl_mask = 1 << control
        target_mask = 1 << target
        
        for i in range(dim):
            if i & ctrl_mask:  # If control qubit is 1
                # Apply gate to target qubit
                i_target_0 = i & ~target_mask  # Target bit set to 0
                i_target_1 = i | target_mask   # Target bit set to 1
                
                if i & target_mask == 0:  # Target is 0
                    op[i, i] = gate[0, 0]
                    op[i, i_target_1] = gate[0, 1]
                else:  # Target is 1
                    op[i, i_target_0] = gate[1, 0]
                    op[i, i] = gate[1, 1]
        
        return op