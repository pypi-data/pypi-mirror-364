import numpy as np
from openarchx.core.tensor import Tensor
from openarchx.layers.base import Linear
from openarchx.layers.activations import ReLU, Softmax
from openarchx.nn.module import Module
from openarchx.optimizers.sgd import SGD
from openarchx.utils.losses import cross_entropy_loss

class MNISTClassifier(Module):
    def __init__(self):
        super().__init__()
        # Smaller network with better initialization
        self.fc1 = Linear(784, 64)
        self.relu1 = ReLU()
        self.fc2 = Linear(64, 32)
        self.relu2 = ReLU()
        self.fc3 = Linear(32, 10)
        self.softmax = Softmax()
        
    def forward(self, x):
        x = self.fc1.forward(x)
        x = self.relu1.forward(x)
        x = self.fc2.forward(x)
        x = self.relu2.forward(x)
        x = self.fc3.forward(x)
        x = self.softmax.forward(x)
        return x

def create_dummy_data(num_samples=1000):
    # Create random MNIST-like dataset with appropriate scaling
    X = np.random.randn(num_samples, 784) * 0.1
    X = (X - X.mean()) / X.std()  # Normalize the input
    y = np.random.randint(0, 10, size=(num_samples,))
    
    # Convert to one-hot encoded labels
    y_one_hot = np.zeros((num_samples, 10))
    y_one_hot[np.arange(num_samples), y] = 1
    return X, y_one_hot

def train(model, X, y, num_epochs=20, batch_size=64, learning_rate=0.01, momentum=0.9):
    optimizer = SGD(model.parameters(), lr=learning_rate, momentum=momentum)
    num_samples = len(X)
    num_batches = num_samples // batch_size
    
    for epoch in range(num_epochs):
        total_loss = 0
        correct_predictions = 0
        
        # Shuffle the data
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
            
            # Calculate loss
            loss = cross_entropy_loss(pred, y_tensor)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            
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
        print(f"Epoch {epoch + 1}/{num_epochs}")
        print(f"Average Loss: {avg_loss:.4f}")
        print(f"Accuracy: {accuracy:.4f}")
        print("-" * 30)

def main():
    # Create model
    model = MNISTClassifier()
    
    # Generate dummy data
    X_train, y_train = create_dummy_data(num_samples=2000)
    
    # Train the model with momentum and adjusted parameters
    train(model, X_train, y_train, 
          num_epochs=20, 
          batch_size=64, 
          learning_rate=0.01,
          momentum=0.9)

if __name__ == "__main__":
    main()