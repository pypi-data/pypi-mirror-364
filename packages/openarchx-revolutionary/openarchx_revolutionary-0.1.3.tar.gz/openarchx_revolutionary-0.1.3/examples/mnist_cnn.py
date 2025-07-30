import numpy as np
import sys
import argparse
from openarchx.core.tensor import Tensor
from openarchx.nn.module import Module
from openarchx.layers.cnn import Conv2d, MaxPool2d
from openarchx.layers.base import Linear
from openarchx.optimizers.adam import Adam
from openarchx.layers.activations import relu

# Global variable for CUDA usage
use_cuda = True
cuda_available = True

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='MNIST CNN Example with OpenArchX')
    parser.add_argument('--cuda', action='store_true', help='Enable CUDA (if available)')
    parser.add_argument('--cpu', action='store_true', help='Disable CUDA and use CPU only')
    parser.add_argument('--epochs', type=int, default=3, help='Number of epochs to train')
    parser.add_argument('--batch-size', type=int, default=64, help='Batch size for training')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    return parser.parse_args()

# Check if CUDA is available
def check_cuda_availability():
    global cuda_available
    # Use PyTorch to check for CUDA availability
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"PyTorch CUDA detection: {cuda_available}")
            print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("PyTorch not installed, cannot check for CUDA")
        cuda_available = False
    return cuda_available

class SmallCNN(Module):
    def __init__(self):
        super().__init__()
        # Smaller CNN for faster training
        self.conv1 = Conv2d(1, 8, kernel_size=3, padding=1)     # 28x28 -> 28x28
        self.conv2 = Conv2d(8, 16, kernel_size=3, padding=1)    # 14x14 -> 14x14
        self.pool = MaxPool2d(kernel_size=2)                     # Halves spatial dimensions
        self.fc1 = Linear(16 * 7 * 7, 32)                       # Smaller hidden layer
        self.fc2 = Linear(32, 10)
    
    def forward(self, x):
        x = relu(self.conv1(x))           # First conv + ReLU
        x = self.pool(x)                  # 28x28 -> 14x14
        x = relu(self.conv2(x))           # Second conv + ReLU
        x = self.pool(x)                  # 14x14 -> 7x7
        batch_size = x.data.shape[0]
        x = Tensor(x.data.reshape(batch_size, -1))     # Flatten: -1 = 16 * 7 * 7
        x = relu(self.fc1(x))            # First fully connected + ReLU
        x = self.fc2(x)                  # Output layer
        return x

    def cuda(self):
        """Move tensor to GPU"""
        return self.to('cuda')

class AverageMeter:
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

def load_mnist(path='mnist.npz'):
    """Load MNIST data from NumPy format."""
    try:
        with np.load(path) as f:
            x_train, y_train = f['x_train'], f['y_train']
            x_test, y_test = f['x_test'], f['y_test']
            return (x_train, y_train), (x_test, y_test)
    except Exception as e:
        print(f"Error loading MNIST dataset: {e}")
        print("Downloading MNIST dataset...")
        try:
            from urllib import request
            url = "https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz"
            request.urlretrieve(url, path)
            return load_mnist(path)
        except Exception as e:
            print(f"Failed to download MNIST dataset: {e}")
            sys.exit(1)

def preprocess_data(x, y, num_classes=10):
    """Preprocess MNIST data."""
    # Normalize images to [0, 1] and reshape to (batch_size, channels, height, width)
    x = x.astype('float32') / 255.0
    x = x.reshape(x.shape[0], 1, 28, 28)
    
    # One-hot encode labels
    y_one_hot = np.zeros((y.size, num_classes))
    y_one_hot[np.arange(y.size), y] = 1
    return x, y_one_hot

# Helper function to safely move tensors to GPU
def to_device(tensor):
    global use_cuda
    if use_cuda:
        try:
            return tensor.cuda()
        except Exception as e:
            print(f"Warning: Failed to move tensor to GPU: {e}")
            # Disable CUDA for future operations if we encounter an error
            use_cuda = False
            print("Disabled CUDA due to errors")
    return tensor

def evaluate(model, x, y, batch_size=100):
    """Evaluate model on given data."""
    correct = 0
    total = 0
    num_batches = len(x) // batch_size
    global use_cuda
    
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = start_idx + batch_size
        
        batch_x = x[start_idx:end_idx]
        batch_y = y[start_idx:end_idx]
        
        # Forward pass
        x_tensor = to_device(Tensor(batch_x))
        pred = model(x_tensor)
        
        # Calculate accuracy
        predictions = np.argmax(pred.data, axis=1)
        true_labels = np.argmax(batch_y, axis=1)
        correct += np.sum(predictions == true_labels)
        total += batch_size
    
    return correct / total

def train_epoch(model, optimizer, x_train, y_train, batch_size):
    """Train for one epoch."""
    losses = AverageMeter()
    accuracy = AverageMeter()
    num_batches = len(x_train) // batch_size
    global use_cuda
    
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = start_idx + batch_size
        
        # Get batch
        batch_x = x_train[start_idx:end_idx]
        batch_y = y_train[start_idx:end_idx]
        
        # Convert to tensors and move to device
        x = to_device(Tensor(batch_x))
        y = to_device(Tensor(batch_y))
        
        # Forward pass
        pred = model(x)
        
        # Calculate cross-entropy loss with numerical stability
        epsilon = 1e-10
        # Clip prediction values to avoid numerical issues
        pred_clipped = np.clip(pred.data, epsilon, 1.0 - epsilon)
        log_pred = to_device(Tensor(np.log(pred_clipped)))
        cross_entropy = (y * log_pred).sum(axis=-1)
        loss = Tensor(np.negative(cross_entropy.data)).mean()
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Update metrics
        predictions = np.argmax(pred.data, axis=1)
        true_labels = np.argmax(batch_y, axis=1)
        acc = np.mean(predictions == true_labels)
        
        losses.update(loss.data, batch_size)
        accuracy.update(acc, batch_size)
        
        # Print progress
        if (i + 1) % 20 == 0:
            print(f"Step [{i+1}/{num_batches}] "
                  f"Loss: {losses.avg:.4f} "
                  f"Accuracy: {accuracy.avg:.4f}")
    
    return losses.avg, accuracy.avg

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Determine whether to use CUDA
    global use_cuda
    cuda_available = check_cuda_availability()
    
    # Respect command line arguments for CUDA usage
    if args.cpu:
        use_cuda = False
    elif args.cuda:
        use_cuda = cuda_available
    else:
        # Default: use CUDA if available
        use_cuda = cuda_available
    
    print(f"CUDA available: {cuda_available}, Using CUDA: {use_cuda}")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    print("Loading MNIST dataset...")
    (x_train, y_train), (x_test, y_test) = load_mnist()
    
    print("Preprocessing data...")
    # Use subset of data for faster training
    train_size = 10000
    test_size = 1000
    x_train, y_train = preprocess_data(x_train[:train_size], y_train[:train_size])
    x_test, y_test = preprocess_data(x_test[:test_size], y_test[:test_size])
    print(f"Training samples: {len(x_train)}, Test samples: {len(x_test)}")
    
    # Create model and optimizer
    print("Creating model...")
    model = SmallCNN()
    
    # Move model to GPU if available and requested
    if use_cuda:
        print("Moving model to GPU...")
        try:
            for param in model.parameters():
                param.cuda()  # Use the cuda() method directly
            print("Model successfully moved to GPU")
        except Exception as e:
            print(f"Error moving model to GPU: {e}")
            use_cuda = False
            print("Falling back to CPU")
    
    optimizer = Adam(model.parameters(), lr=args.lr)
    
    # Training parameters
    batch_size = args.batch_size
    num_epochs = args.epochs
    best_accuracy = 0.0
    
    print("\nStarting training...")
    try:
        for epoch in range(num_epochs):
            print(f"\nEpoch [{epoch+1}/{num_epochs}]")
            
            # Shuffle training data
            indices = np.random.permutation(len(x_train))
            x_train_shuffled = x_train[indices]
            y_train_shuffled = y_train[indices]
            
            # Train one epoch
            train_loss, train_acc = train_epoch(
                model, optimizer, x_train_shuffled, y_train_shuffled, batch_size
            )
            
            # Evaluate on test set
            test_acc = evaluate(model, x_test, y_test)
            
            print(f"\nEpoch Summary:")
            print(f"Train Loss: {train_loss:.4f}")
            print(f"Train Accuracy: {train_acc:.4f}")
            print(f"Test Accuracy: {test_acc:.4f}")
            
            # Save best model (in practice, you'd save to disk here)
            if test_acc > best_accuracy:
                best_accuracy = test_acc
                print(f"New best test accuracy: {best_accuracy:.4f}")
        
        print("\nTraining completed!")
        print(f"Best test accuracy: {best_accuracy:.4f}")
        
    except KeyboardInterrupt:
        print("\nTraining interrupted by user!")
    except Exception as e:
        print(f"\nAn error occurred during training: {e}")
        raise

if __name__ == "__main__":
    main()