"""
PyTorch Integration Utilities for OpenArchX.

This module provides conversion and adapter utilities for using PyTorch models
and datasets with OpenArchX. These utilities are completely optional and do not 
affect OpenArchX's core functionality, which remains independent from external libraries.
"""

import numpy as np
import importlib.util
from ..core.tensor import Tensor


class PyTorchModelAdapter:
    """Adapter for using PyTorch models with OpenArchX."""
    
    def __init__(self, torch_model, device=None):
        """
        Initialize a PyTorch model adapter.
        
        Args:
            torch_model: A PyTorch nn.Module model.
            device: The device to run the model on ('cpu', 'cuda', etc.).
        """
        # Check if torch is installed
        if importlib.util.find_spec("torch") is None:
            raise ImportError("PyTorch is required. Install with 'pip install torch'")
            
        import torch
        
        self.model = torch_model
        
        # Handle device placement
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
    def __call__(self, inputs, **kwargs):
        """
        Process inputs through the PyTorch model.
        
        Args:
            inputs: Input data, can be numpy arrays, lists, or OpenArchX Tensors.
            **kwargs: Additional arguments to pass to the model.
            
        Returns:
            OpenArchX Tensor containing the model output.
        """
        import torch
        
        # Convert inputs to torch tensors
        if isinstance(inputs, Tensor):
            inputs = inputs.data
            
        if isinstance(inputs, np.ndarray):
            inputs = torch.tensor(inputs, dtype=torch.float32, device=self.device)
        elif isinstance(inputs, list):
            inputs = torch.tensor(np.array(inputs), dtype=torch.float32, device=self.device)
        elif not isinstance(inputs, torch.Tensor):
            raise TypeError(f"Unsupported input type: {type(inputs)}")
            
        # If inputs is already a torch tensor, ensure it's on the right device
        if isinstance(inputs, torch.Tensor) and inputs.device != self.device:
            inputs = inputs.to(self.device)
            
        # Forward pass with gradient tracking disabled
        with torch.no_grad():
            outputs = self.model(inputs, **kwargs)
            
        # Convert output to numpy and then to Tensor
        if isinstance(outputs, torch.Tensor):
            return Tensor(outputs.detach().cpu().numpy())
        elif isinstance(outputs, (tuple, list)):
            return tuple(Tensor(output.detach().cpu().numpy()) for output in outputs 
                         if isinstance(output, torch.Tensor))
        elif isinstance(outputs, dict):
            return {k: Tensor(v.detach().cpu().numpy()) if isinstance(v, torch.Tensor) else v 
                    for k, v in outputs.items()}
        else:
            return outputs


class PyTorchDatasetConverter:
    """Utility for converting between PyTorch and OpenArchX datasets."""
    
    @staticmethod
    def to_openarchx_dataset(torch_dataset, transform=None):
        """
        Convert a PyTorch Dataset to an OpenArchX Dataset.
        
        Args:
            torch_dataset: A PyTorch Dataset instance.
            transform: Optional transform to apply to the data.
            
        Returns:
            An OpenArchX Dataset.
        """
        from .data import Dataset
        
        # Check if torch is installed
        if importlib.util.find_spec("torch") is None:
            raise ImportError("PyTorch is required. Install with 'pip install torch'")
            
        class OpenArchXDatasetFromPyTorch(Dataset):
            def __init__(self, torch_dataset, transform=None):
                self.torch_dataset = torch_dataset
                self.transform = transform
                
            def __len__(self):
                return len(self.torch_dataset)
                
            def __getitem__(self, idx):
                data = self.torch_dataset[idx]
                
                # Handle different return types from PyTorch dataset
                if isinstance(data, tuple) and len(data) == 2:
                    # Standard (input, target) format
                    features, target = data
                    
                    # Convert PyTorch tensors to numpy arrays
                    if hasattr(features, 'numpy'):
                        features = features.numpy()
                    if hasattr(target, 'numpy'):
                        target = target.numpy()
                        
                    # Apply transform if provided
                    if self.transform:
                        features = self.transform(features)
                        
                    return features, target
                else:
                    # Generic handling for other formats
                    if hasattr(data, 'numpy'):
                        data = data.numpy()
                    return data
        
        return OpenArchXDatasetFromPyTorch(torch_dataset, transform)
    
    @staticmethod
    def from_openarchx_dataset(ox_dataset, tensor_dtype=None):
        """
        Convert an OpenArchX Dataset to a PyTorch Dataset.
        
        Args:
            ox_dataset: An OpenArchX Dataset instance.
            tensor_dtype: Optional dtype for the PyTorch tensors.
            
        Returns:
            A PyTorch Dataset.
        """
        # Check if torch is installed
        if importlib.util.find_spec("torch") is None:
            raise ImportError("PyTorch is required. Install with 'pip install torch'")
            
        import torch
        from torch.utils.data import Dataset as TorchDataset
        
        class PyTorchDatasetFromOpenArchX(TorchDataset):
            def __init__(self, ox_dataset, tensor_dtype=None):
                self.ox_dataset = ox_dataset
                self.tensor_dtype = tensor_dtype or torch.float32
                
            def __len__(self):
                return len(self.ox_dataset)
                
            def __getitem__(self, idx):
                data = self.ox_dataset[idx]
                
                # Handle different return types from OpenArchX dataset
                if isinstance(data, tuple) and len(data) == 2:
                    # Standard (input, target) format
                    features, target = data
                    
                    # Convert to PyTorch tensors
                    if isinstance(features, Tensor):
                        features = torch.tensor(features.data, dtype=self.tensor_dtype)
                    elif isinstance(features, np.ndarray):
                        features = torch.tensor(features, dtype=self.tensor_dtype)
                        
                    if isinstance(target, Tensor):
                        target = torch.tensor(target.data, dtype=self.tensor_dtype)
                    elif isinstance(target, np.ndarray):
                        target = torch.tensor(target, dtype=self.tensor_dtype)
                        
                    return features, target
                else:
                    # Generic handling for other formats
                    if isinstance(data, Tensor):
                        return torch.tensor(data.data, dtype=self.tensor_dtype)
                    elif isinstance(data, np.ndarray):
                        return torch.tensor(data, dtype=self.tensor_dtype)
                    return data
        
        return PyTorchDatasetFromOpenArchX(ox_dataset, tensor_dtype)


class PyTorchModelConverter:
    """Utility for converting PyTorch models to OpenArchX architecture."""
    
    @staticmethod
    def convert_model(torch_model, input_shape=None, framework_dependence=False):
        """
        Convert a PyTorch model to an OpenArchX model.
        
        Args:
            torch_model: A PyTorch nn.Module model.
            input_shape: The shape of the input tensor (excluding batch dimension).
            framework_dependence: If True, the resulting model will still rely on PyTorch
                                  for forward passes. If False, it will be converted to
                                  pure OpenArchX layers.
                                  
        Returns:
            An OpenArchX model.
        """
        # Check if torch is installed
        if importlib.util.find_spec("torch") is None:
            raise ImportError("PyTorch is required. Install with 'pip install torch'")
            
        import torch
        import torch.nn as nn
        from ..nn.base import Layer, Model
        from ..nn.layers import Dense, Conv2D, MaxPool2D, Flatten, Dropout
        
        if framework_dependence:
            # Create a wrapper around the PyTorch model
            class PyTorchWrappedModel(Model):
                def __init__(self, torch_model):
                    super().__init__()
                    self.torch_model = torch_model
                    self.torch_model.eval()  # Set to evaluation mode
                    
                def forward(self, x):
                    # Convert OpenArchX Tensor to PyTorch tensor
                    if isinstance(x, Tensor):
                        x_torch = torch.tensor(x.data, dtype=torch.float32)
                    else:
                        x_torch = torch.tensor(x, dtype=torch.float32)
                        
                    # Forward pass with gradient tracking disabled
                    with torch.no_grad():
                        output = self.torch_model(x_torch)
                        
                    # Convert back to OpenArchX Tensor
                    if isinstance(output, torch.Tensor):
                        return Tensor(output.numpy())
                    else:
                        return output
            
            return PyTorchWrappedModel(torch_model)
            
        else:
            # Convert to pure OpenArchX model by translating each layer
            class OpenArchXModelFromPyTorch(Model):
                def __init__(self, torch_model, input_shape):
                    super().__init__()
                    self.layers = []
                    
                    # We need sample input to trace through the PyTorch model
                    if input_shape is None:
                        raise ValueError("input_shape must be provided for full conversion")
                    
                    # Create a sample input tensor to trace the model
                    sample_input = torch.zeros((1,) + input_shape)
                    
                    # Collect layer information
                    layer_info = []
                    
                    def hook_fn(module, input, output):
                        layer_info.append({
                            'module': module,
                            'input_shape': [tuple(t.shape) for t in input if isinstance(t, torch.Tensor)],
                            'output_shape': output.shape if isinstance(output, torch.Tensor) 
                                            else [t.shape for t in output if isinstance(t, torch.Tensor)]
                        })
                    
                    # Register hooks
                    hooks = []
                    for name, module in torch_model.named_modules():
                        if isinstance(module, (nn.Linear, nn.Conv2d, nn.MaxPool2d, nn.Flatten, nn.Dropout)):
                            hooks.append(module.register_forward_hook(hook_fn))
                    
                    # Forward pass to activate hooks
                    with torch.no_grad():
                        torch_model(sample_input)
                    
                    # Remove hooks
                    for hook in hooks:
                        hook.remove()
                    
                    # Convert each layer
                    for info in layer_info:
                        module = info['module']
                        if isinstance(module, nn.Linear):
                            layer = Dense(module.out_features)
                            # Set weights and biases
                            layer.weights = Tensor(module.weight.detach().numpy().T)
                            if module.bias is not None:
                                layer.bias = Tensor(module.bias.detach().numpy())
                            self.layers.append(layer)
                            
                        elif isinstance(module, nn.Conv2d):
                            layer = Conv2D(
                                filters=module.out_channels,
                                kernel_size=module.kernel_size,
                                strides=module.stride,
                                padding=module.padding
                            )
                            # Set weights and biases
                            layer.kernels = Tensor(module.weight.detach().numpy())
                            if module.bias is not None:
                                layer.bias = Tensor(module.bias.detach().numpy())
                            self.layers.append(layer)
                            
                        elif isinstance(module, nn.MaxPool2d):
                            layer = MaxPool2D(
                                pool_size=module.kernel_size,
                                strides=module.stride,
                                padding=module.padding
                            )
                            self.layers.append(layer)
                            
                        elif isinstance(module, nn.Flatten):
                            layer = Flatten()
                            self.layers.append(layer)
                            
                        elif isinstance(module, nn.Dropout):
                            layer = Dropout(rate=module.p)
                            self.layers.append(layer)
                    
                def forward(self, x):
                    for layer in self.layers:
                        x = layer(x)
                    return x
            
            return OpenArchXModelFromPyTorch(torch_model, input_shape)


# Convenience functions

def get_pytorch_model_adapter(torch_model, device=None):
    """
    Helper function to get a PyTorch model adapter.
    
    Args:
        torch_model: A PyTorch nn.Module model.
        device: The device to run the model on.
        
    Returns:
        A PyTorchModelAdapter instance.
    """
    return PyTorchModelAdapter(torch_model, device)


def convert_to_pytorch_dataset(ox_dataset, tensor_dtype=None):
    """
    Convert an OpenArchX Dataset to a PyTorch Dataset.
    
    Args:
        ox_dataset: An OpenArchX Dataset instance.
        tensor_dtype: Optional dtype for the PyTorch tensors.
        
    Returns:
        A PyTorch Dataset.
    """
    return PyTorchDatasetConverter.from_openarchx_dataset(ox_dataset, tensor_dtype)


def convert_from_pytorch_dataset(torch_dataset, transform=None):
    """
    Convert a PyTorch Dataset to an OpenArchX Dataset.
    
    Args:
        torch_dataset: A PyTorch Dataset instance.
        transform: Optional transform to apply to the data.
        
    Returns:
        An OpenArchX Dataset.
    """
    return PyTorchDatasetConverter.to_openarchx_dataset(torch_dataset, transform)


def convert_pytorch_model(torch_model, input_shape=None, framework_dependence=False):
    """
    Convert a PyTorch model to an OpenArchX model.
    
    Args:
        torch_model: A PyTorch nn.Module model.
        input_shape: The shape of the input tensor (excluding batch dimension).
        framework_dependence: If True, the resulting model will still rely on PyTorch.
                             If False, it will be converted to pure OpenArchX layers.
                             
    Returns:
        An OpenArchX model.
    """
    return PyTorchModelConverter.convert_model(torch_model, input_shape, framework_dependence)


def extract_pytorch_weights(torch_model):
    """
    Extract weights from a PyTorch model.
    
    Args:
        torch_model: A PyTorch nn.Module model.
        
    Returns:
        Dictionary mapping parameter names to OpenArchX Tensors.
    """
    # Check if torch is installed
    if importlib.util.find_spec("torch") is None:
        raise ImportError("PyTorch is required. Install with 'pip install torch'")
        
    weights_dict = {}
    
    # Iterate through named parameters
    for name, param in torch_model.named_parameters():
        weights_dict[name] = Tensor(param.detach().cpu().numpy())
        
    return weights_dict 