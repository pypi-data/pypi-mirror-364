"""
OpenArchX Model Saving and Loading Example

This example demonstrates how to:
1. Create and train a simple model
2. Save the model in the native .oaxm format
3. Load the model from the .oaxm file
4. Convert models between PyTorch, TensorFlow, and OpenArchX
"""

import os
import numpy as np

# Import OpenArchX
import openarchx as ox
from openarchx.nn import Dense, Sequential, ReLU
from openarchx.core import Tensor
from openarchx.utils import save_model, load_model


def create_simple_model():
    """Create a simple sequential model for demonstration."""
    model = Sequential([
        Dense(10, input_dim=5),
        ReLU(),
        Dense(5),
        ReLU(),
        Dense(1)
    ])
    return model


def generate_dummy_data(num_samples=100):
    """Generate dummy data for training."""
    X = np.random.randn(num_samples, 5).astype(np.float32)
    y = np.sum(X * np.array([0.2, 0.5, -0.3, 0.7, -0.1]), axis=1, keepdims=True)
    y += np.random.randn(num_samples, 1) * 0.1  # Add some noise
    return Tensor(X), Tensor(y)


def train_simple_model(model, X, y, epochs=10, learning_rate=0.01):
    """Train the model on dummy data."""
    optimizer = ox.optim.SGD(model.parameters(), learning_rate=learning_rate)
    loss_fn = ox.losses.MSELoss()
    
    for epoch in range(epochs):
        # Forward pass
        y_pred = model(X)
        loss = loss_fn(y_pred, y)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if epoch % 2 == 0:
            print(f"Epoch {epoch}: Loss = {loss.data}")
    
    return model


def save_and_load_example():
    """Example of saving and loading a model in .oaxm format."""
    # Create and train a model
    model = create_simple_model()
    X, y = generate_dummy_data()
    trained_model = train_simple_model(model, X, y)
    
    # Create directory for saving models
    os.makedirs("saved_models", exist_ok=True)
    
    # Save the model
    save_path = save_model(trained_model, "saved_models/simple_model.oaxm")
    print(f"Model saved to {save_path}")
    
    # Load the model
    loaded_model = load_model(save_path, model_class=Sequential)
    
    # Verify it works the same
    y_pred_original = trained_model(X)
    y_pred_loaded = loaded_model(X)
    
    # Check if predictions are the same
    diff = np.abs(y_pred_original.data - y_pred_loaded.data).mean()
    print(f"Difference between original and loaded model predictions: {diff}")
    assert diff < 1e-6, "Loaded model produces different results!"
    
    # Save with compression and metadata
    metadata = {
        "description": "Simple regression model",
        "epochs_trained": 10,
        "author": "OpenArchX"
    }
    
    compressed_path = save_model(
        trained_model, 
        "saved_models/simple_model_compressed.oaxm", 
        metadata=metadata,
        compress=True
    )
    print(f"Model saved with compression to {compressed_path}")
    
    return trained_model, loaded_model


def pytorch_conversion_example(trained_model):
    """Example of converting between PyTorch and OpenArchX models."""
    try:
        import torch
        import torch.nn as nn
        from openarchx.utils import convert_from_pytorch, convert_to_pytorch
        
        # Create an equivalent PyTorch model
        class PyTorchEquivalent(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(5, 10)
                self.relu1 = nn.ReLU()
                self.fc2 = nn.Linear(10, 5)
                self.relu2 = nn.ReLU()
                self.fc3 = nn.Linear(5, 1)
                
            def forward(self, x):
                x = self.relu1(self.fc1(x))
                x = self.relu2(self.fc2(x))
                x = self.fc3(x)
                return x
        
        # Instantiate the PyTorch model
        pt_model = PyTorchEquivalent()
        
        # Set some weights
        with torch.no_grad():
            pt_model.fc1.weight.fill_(0.1)
            pt_model.fc2.weight.fill_(0.2)
            pt_model.fc3.weight.fill_(0.3)
        
        # Convert PyTorch model to .oaxm
        oaxm_path = convert_from_pytorch(pt_model, "saved_models/from_pytorch.oaxm")
        print(f"PyTorch model converted and saved to {oaxm_path}")
        
        # Convert OpenArchX model to PyTorch
        X, _ = generate_dummy_data(1)  # Get a sample input
        pt_equivalent = PyTorchEquivalent()  # Create empty PyTorch model
        
        # Load the weights from OpenArchX model into PyTorch model
        pt_loaded = convert_to_pytorch("saved_models/simple_model.oaxm", pt_equivalent)
        
        # Check if the conversion worked
        with torch.no_grad():
            pt_input = torch.tensor(X.data)
            pt_output = pt_loaded(pt_input)
            
        ox_output = trained_model(X)
        pt_np_output = pt_output.detach().numpy()
        
        diff = np.abs(ox_output.data - pt_np_output).mean()
        print(f"Difference between OpenArchX and PyTorch model predictions: {diff}")
        
        return True
    except ImportError:
        print("PyTorch is not installed, skipping conversion example.")
        return False


def tensorflow_conversion_example(trained_model):
    """Example of converting between TensorFlow and OpenArchX models."""
    try:
        import tensorflow as tf
        from openarchx.utils import convert_from_tensorflow, convert_to_tensorflow
        
        # Create an equivalent TensorFlow model
        tf_model = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dense(5, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        
        # Set some weights (just for demonstration)
        weights = []
        biases = []
        
        # For the first layer
        weights.append(np.ones((5, 10)) * 0.1)
        biases.append(np.zeros(10))
        
        # For the second layer
        weights.append(np.ones((10, 5)) * 0.2)
        biases.append(np.zeros(5))
        
        # For the third layer
        weights.append(np.ones((5, 1)) * 0.3)
        biases.append(np.zeros(1))
        
        # Set the weights
        tf_model_weights = []
        for w, b in zip(weights, biases):
            tf_model_weights.append(w)
            tf_model_weights.append(b)
            
        tf_model.set_weights(tf_model_weights)
        
        # Convert TensorFlow model to .oaxm
        oaxm_path = convert_from_tensorflow(tf_model, "saved_models/from_tensorflow.oaxm")
        print(f"TensorFlow model converted and saved to {oaxm_path}")
        
        # Convert OpenArchX model to TensorFlow
        tf_equivalent = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dense(5, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        
        # Initialize the model to create the weights
        X, _ = generate_dummy_data(1)
        _ = tf_equivalent(X.data)
        
        # Load the weights from OpenArchX model into TensorFlow model
        tf_loaded = convert_to_tensorflow("saved_models/simple_model.oaxm", tf_equivalent)
        
        # Check if the conversion worked
        tf_input = X.data
        tf_output = tf_loaded(tf_input).numpy()
            
        ox_output = trained_model(X)
        
        diff = np.abs(ox_output.data - tf_output).mean()
        print(f"Difference between OpenArchX and TensorFlow model predictions: {diff}")
        
        return True
    except ImportError:
        print("TensorFlow is not installed, skipping conversion example.")
        return False


if __name__ == "__main__":
    print("=== OpenArchX Model Saving and Loading Example ===")
    
    # Basic save and load
    trained_model, loaded_model = save_and_load_example()
    
    # Framework conversions
    print("\n=== PyTorch Conversion Example ===")
    pytorch_success = pytorch_conversion_example(trained_model)
    
    print("\n=== TensorFlow Conversion Example ===")
    tensorflow_success = tensorflow_conversion_example(trained_model)
    
    print("\nAll examples completed successfully!") 