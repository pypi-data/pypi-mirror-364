import numpy as np
from openarchx.core.tensor import Tensor
from openarchx.layers.transformer import TransformerEncoderLayer
from openarchx.layers.base import Linear
from openarchx.quantum.circuit import QuantumLayer, QuantumCircuit
from openarchx.nn.module import Module
from openarchx.optimizers.sgd import SGD

class QuantumTransformerLayer(QuantumLayer):
    def __init__(self, num_qubits=4):
        super().__init__(num_qubits, num_params=num_qubits * 3)
        
    def build_circuit(self):
        # Apply Hadamard gates to create superposition
        for i in range(self.circuit.num_qubits):
            self.circuit.h(i)
        
        # Apply parameterized rotations
        param_idx = 0
        for i in range(self.circuit.num_qubits):
            self.circuit.rx(param_idx, i)
            param_idx += 1
            self.circuit.ry(param_idx, i)
            param_idx += 1
            self.circuit.rz(param_idx, i)
            param_idx += 1
        
        # Apply entangling CNOT gates
        for i in range(self.circuit.num_qubits - 1):
            self.circuit.cnot(i, i + 1)

class HybridModel(Module):
    def __init__(self, seq_length, d_model, nhead):
        super().__init__()
        self.d_model = d_model
        
        # Classical transformer layer
        self.transformer = TransformerEncoderLayer(d_model, nhead)
        
        # Quantum layer
        self.quantum = QuantumTransformerLayer(num_qubits=4)
        
        # Final classical layer to combine quantum and classical results
        self.final_layer = Linear(d_model + 16, d_model)  # 16 = 2^4 (quantum state size)
        
    def forward(self, x):
        # Process with transformer
        classical_out = self.transformer.forward(x)
        
        # Process with quantum circuit
        quantum_out = self.quantum.forward(None)
        
        # Combine classical and quantum outputs
        batch_size = x.data.shape[0]
        quantum_out_expanded = Tensor(np.tile(quantum_out.data, (batch_size, 1)))
        combined = Tensor(np.concatenate([classical_out.data, quantum_out_expanded.data], axis=-1))
        
        return self.final_layer.forward(combined)

def generate_dummy_data(batch_size=32, seq_length=10, d_model=64):
    # Generate random sequence data
    X = np.random.randn(batch_size, seq_length, d_model) * 0.1
    y = np.random.randn(batch_size, seq_length, d_model) * 0.1
    return X, y

def main():
    # Model parameters
    batch_size = 32
    seq_length = 10
    d_model = 64
    nhead = 4
    
    # Create model
    model = HybridModel(seq_length, d_model, nhead)
    
    # Generate dummy data
    X_train, y_train = generate_dummy_data(batch_size, seq_length, d_model)
    
    # Training parameters
    optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9)
    num_epochs = 10
    
    # Training loop
    for epoch in range(num_epochs):
        # Convert to tensors
        x_tensor = Tensor(X_train)
        y_tensor = Tensor(y_train)
        
        # Forward pass
        pred = model(x_tensor)
        
        # Calculate MSE loss
        loss = ((pred - y_tensor) ** 2).mean()
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Update weights
        optimizer.step()
        
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {loss.data:.4f}")

if __name__ == "__main__":
    main()