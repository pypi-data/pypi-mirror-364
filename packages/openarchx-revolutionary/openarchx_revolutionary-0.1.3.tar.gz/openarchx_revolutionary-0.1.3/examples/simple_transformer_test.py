import numpy as np
from openarchx.core.tensor import Tensor
from openarchx.layers.transformer import TransformerEncoderLayer
from openarchx.optimizers.adam import Adam

def generate_simple_sequence_data(batch_size=4, seq_length=8, d_model=16):
    """Generate simple sequence data with a clear pattern"""
    # Create sequences where each position is related to its index
    X = np.zeros((batch_size, seq_length, d_model))
    y = np.zeros((batch_size, seq_length, d_model))
    
    for b in range(batch_size):
        for s in range(seq_length):
            # Input: position-based pattern
            X[b, s] = np.sin(np.arange(d_model) * (s + 1) / d_model)
            # Target: shifted pattern
            y[b, s] = np.sin(np.arange(d_model) * (s + 2) / d_model)
    
    print(f"Input shape: {X.shape}")
    return X, y

def main():
    # Small model parameters for testing
    batch_size = 4
    seq_length = 8
    d_model = 16
    nhead = 4
    
    print("Model parameters:")
    print(f"batch_size={batch_size}, seq_length={seq_length}")
    print(f"d_model={d_model}, nhead={nhead}")
    print("-" * 30)
    
    # Create transformer layer
    model = TransformerEncoderLayer(d_model, nhead, dim_feedforward=32)
    
    # Generate simple data
    X, y = generate_simple_sequence_data(batch_size, seq_length, d_model)
    
    # Convert to tensors
    x_tensor = Tensor(X)
    y_tensor = Tensor(y)
    
    # Create optimizer
    optimizer = Adam(model.parameters(), lr=0.01)
    
    # Simple training loop
    print("\nStarting training...")
    for epoch in range(10):
        # Forward pass
        print(f"\nEpoch {epoch + 1}")
        print(f"Input tensor shape: {x_tensor.data.shape}")
        
        pred = model(x_tensor)
        print(f"Output tensor shape: {pred.data.shape}")
        
        # Calculate MSE loss
        loss = ((pred - y_tensor) ** 2).mean()
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        print(f"Loss: {loss.data:.6f}")

if __name__ == "__main__":
    main()