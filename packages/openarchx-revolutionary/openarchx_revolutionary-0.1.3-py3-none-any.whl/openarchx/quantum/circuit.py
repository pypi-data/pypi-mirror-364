import numpy as np
from ..core.tensor import Tensor
from ..nn.module import Module
from .gates import QuantumGates, QuantumRegister

class QuantumCircuit(Module):
    def __init__(self, num_qubits):
        super().__init__()
        self.num_qubits = num_qubits
        self.register = None
        self.gates = []
    
    def reset(self):
        """Initialize a new quantum register"""
        self.register = QuantumRegister(self.num_qubits)
        self.gates = []
    
    def h(self, qubit):
        """Apply Hadamard gate"""
        self.gates.append(('H', qubit))
        return self
    
    def x(self, qubit):
        """Apply Pauli-X gate"""
        self.gates.append(('X', qubit))
        return self
    
    def y(self, qubit):
        """Apply Pauli-Y gate"""
        self.gates.append(('Y', qubit))
        return self
    
    def z(self, qubit):
        """Apply Pauli-Z gate"""
        self.gates.append(('Z', qubit))
        return self
    
    def rx(self, theta, qubit):
        """Apply parameterized rotation around X axis"""
        self.gates.append(('RX', theta, qubit))
        return self
    
    def ry(self, theta, qubit):
        """Apply parameterized rotation around Y axis"""
        self.gates.append(('RY', theta, qubit))
        return self
    
    def rz(self, theta, qubit):
        """Apply parameterized rotation around Z axis"""
        self.gates.append(('RZ', theta, qubit))
        return self
    
    def cnot(self, control, target):
        """Apply CNOT gate"""
        self.gates.append(('CNOT', control, target))
        return self
    
    def forward(self, input_params=None):
        """Execute quantum circuit and return measurement results"""
        self.reset()
        
        # Apply gates with batch support
        for gate in self.gates:
            if gate[0] in ['RX', 'RY', 'RZ']:
                theta = gate[1] if input_params is None else input_params[gate[1]]
                # Scale parameters to prevent gradient explosion
                theta = np.clip(theta, -np.pi, np.pi)
                self.register.apply_gate(getattr(QuantumGates, gate[0])(theta), gate[2])
            else:
                gate_op = getattr(QuantumGates, gate[0])()
                if gate[0] == 'CNOT':
                    self.register.apply_controlled_gate(gate_op, gate[1], gate[2])
                else:
                    self.register.apply_gate(gate_op, gate[1])
        
        # Return the final state with gradient tracking
        return Tensor(self.register.state, requires_grad=True)

class QuantumLayer(Module):
    def __init__(self, num_qubits, num_params):
        super().__init__()
        self.circuit = QuantumCircuit(num_qubits)
        self.params = Tensor(np.random.randn(num_params) * 0.1, requires_grad=True)
    
    def build_circuit(self):
        """Override this method to define the quantum circuit architecture"""
        raise NotImplementedError
    
    def forward(self, x):
        """Execute quantum circuit with current parameters"""
        self.build_circuit()
        return self.circuit.forward(self.params)