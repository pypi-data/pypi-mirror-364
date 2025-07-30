import numpy as np
from ..core.tensor import Tensor


class Transform:
    """Base class for all transforms."""
    
    def __call__(self, x):
        """Apply the transform to input x."""
        raise NotImplementedError("Transform must implement __call__ method")
    

class Compose:
    """Composes several transforms together."""
    
    def __init__(self, transforms):
        """
        Args:
            transforms (list): List of transforms to compose.
        """
        self.transforms = transforms
        
    def __call__(self, x):
        """Apply all transforms sequentially."""
        for t in self.transforms:
            x = t(x)
        return x


class ToTensor:
    """Convert a numpy.ndarray to OpenArchX Tensor."""
    
    def __call__(self, x):
        """
        Args:
            x: NumPy array or list to be converted to tensor.
        Returns:
            OpenArchX Tensor.
        """
        if isinstance(x, Tensor):
            return x
        if not isinstance(x, np.ndarray):
            x = np.array(x, dtype=np.float32)
        return Tensor(x)


class Normalize:
    """Normalize a tensor with mean and standard deviation."""
    
    def __init__(self, mean, std):
        """
        Args:
            mean: Mean value for each channel/feature.
            std: Standard deviation for each channel/feature.
        """
        self.mean = np.array(mean, dtype=np.float32)
        self.std = np.array(std, dtype=np.float32)
        
    def __call__(self, x):
        """
        Args:
            x: Tensor to be normalized.
        Returns:
            Normalized Tensor.
        """
        if isinstance(x, Tensor):
            return Tensor((x.data - self.mean) / self.std)
        return (x - self.mean) / self.std


class RandomCrop:
    """Crop randomly the image in a sample."""
    
    def __init__(self, output_size):
        """
        Args:
            output_size (tuple or int): Desired output size. If int, square crop is made.
        """
        if isinstance(output_size, int):
            self.output_size = (output_size, output_size)
        else:
            self.output_size = output_size
        
    def __call__(self, x):
        """
        Args:
            x: Image to be cropped.
        Returns:
            Cropped image.
        """
        h, w = x.shape[-2:]
        new_h, new_w = self.output_size
        
        top = np.random.randint(0, h - new_h + 1)
        left = np.random.randint(0, w - new_w + 1)
        
        if isinstance(x, Tensor):
            x_data = x.data
            if len(x_data.shape) == 2:
                x_data = x_data[top:top + new_h, left:left + new_w]
            elif len(x_data.shape) == 3:
                x_data = x_data[:, top:top + new_h, left:left + new_w]
            else:
                x_data = x_data[..., top:top + new_h, left:left + new_w]
            return Tensor(x_data)
        else:
            if len(x.shape) == 2:
                return x[top:top + new_h, left:left + new_w]
            elif len(x.shape) == 3:
                return x[:, top:top + new_h, left:left + new_w]
            else:
                return x[..., top:top + new_h, left:left + new_w]


class RandomHorizontalFlip:
    """Randomly flip the image horizontally."""
    
    def __init__(self, p=0.5):
        """
        Args:
            p (float): Probability of flipping.
        """
        self.p = p
        
    def __call__(self, x):
        """
        Args:
            x: Image to be flipped.
        Returns:
            Flipped image with probability p.
        """
        if np.random.random() < self.p:
            if isinstance(x, Tensor):
                # Handle the last dimension for channels first or last
                if len(x.data.shape) == 3:  # Assume channels-first (C, H, W)
                    return Tensor(x.data[:, :, ::-1])
                elif len(x.data.shape) == 2:  # No channels
                    return Tensor(x.data[:, ::-1])
                else:  # Batch images or other dimensions
                    return Tensor(np.flip(x.data, axis=-1))
            else:
                # Handle the last dimension for channels first or last
                if len(x.shape) == 3:  # Assume channels-first (C, H, W)
                    return x[:, :, ::-1]
                elif len(x.shape) == 2:  # No channels
                    return x[:, ::-1]
                else:  # Batch images or other dimensions
                    return np.flip(x, axis=-1)
        return x


class Resize:
    """Resize the image to a given size."""
    
    def __init__(self, output_size):
        """
        Args:
            output_size (tuple or int): Desired output size. If int, square resize is made.
        """
        if isinstance(output_size, int):
            self.output_size = (output_size, output_size)
        else:
            self.output_size = output_size
            
    def __call__(self, x):
        """
        Args:
            x: Image to be resized.
        Returns:
            Resized image.
        """
        # Check if scipy is available for resize
        try:
            from scipy.ndimage import zoom
        except ImportError:
            raise ImportError("SciPy is required for resize. Please install it with 'pip install scipy'")
            
        new_h, new_w = self.output_size
        
        if isinstance(x, Tensor):
            x_data = x.data
            if len(x_data.shape) == 2:  # (H, W)
                h, w = x_data.shape
                zoom_h, zoom_w = new_h / h, new_w / w
                return Tensor(zoom(x_data, (zoom_h, zoom_w)))
            elif len(x_data.shape) == 3:  # (C, H, W)
                c, h, w = x_data.shape
                zoom_h, zoom_w = new_h / h, new_w / w
                return Tensor(zoom(x_data, (1, zoom_h, zoom_w)))
            else:  # Batch or other dimensions
                raise ValueError("Unsupported tensor shape for resize")
        else:
            if len(x.shape) == 2:  # (H, W)
                h, w = x.shape
                zoom_h, zoom_w = new_h / h, new_w / w
                return zoom(x, (zoom_h, zoom_w))
            elif len(x.shape) == 3:  # (C, H, W)
                c, h, w = x.shape
                zoom_h, zoom_w = new_h / h, new_w / w
                return zoom(x, (1, zoom_h, zoom_w))
            else:  # Batch or other dimensions
                raise ValueError("Unsupported array shape for resize")


class TorchTransformAdapter:
    """Adapter for using PyTorch transforms with OpenArchX."""
    
    def __init__(self, torch_transform):
        """
        Args:
            torch_transform: A PyTorch transform or composition of transforms.
        """
        import importlib.util
        if importlib.util.find_spec("torch") is None:
            raise ImportError("PyTorch is required for this adapter. Please install it with 'pip install torch'")
            
        import torch
        self.torch_transform = torch_transform
        
    def __call__(self, x):
        """
        Args:
            x: Input data to transform.
        Returns:
            Transformed data as OpenArchX Tensor.
        """
        import torch
        import numpy as np
        
        # Convert to torch tensor if needed
        if isinstance(x, np.ndarray):
            x_torch = torch.from_numpy(x)
        elif isinstance(x, Tensor):
            x_torch = torch.from_numpy(x.data)
        else:
            x_torch = x
            
        # Apply torch transform
        result = self.torch_transform(x_torch)
        
        # Convert back to numpy/Tensor
        if isinstance(result, torch.Tensor):
            result = result.numpy()
            
        return Tensor(result) if not isinstance(x, Tensor) else result


class TransformFactory:
    """Factory for creating transforms from various sources."""
    
    @staticmethod
    def from_torch(torch_transform):
        """Create a transform from a PyTorch transform."""
        return TorchTransformAdapter(torch_transform)
    
    @staticmethod
    def compose(transforms):
        """Create a composition of transforms."""
        return Compose(transforms) 