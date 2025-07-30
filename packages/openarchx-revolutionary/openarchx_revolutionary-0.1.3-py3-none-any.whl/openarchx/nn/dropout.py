import numpy as np
from ..core.tensor import Tensor
from .module import Module

class Dropout(Module):
    def __init__(self, p=0.5, inplace=False):
        super().__init__()
        self.p = p
        self.inplace = inplace
        self.training = True

    def forward(self, x):
        if not self.training or self.p == 0:
            return x
        
        mask = np.random.random(x.data.shape) > self.p
        if self.inplace:
            x.data = x.data * mask / (1 - self.p)
            return x
        return Tensor(x.data * mask / (1 - self.p), requires_grad=True)

class Dropout2d(Module):
    def __init__(self, p=0.5, inplace=False):
        super().__init__()
        self.p = p
        self.inplace = inplace
        self.training = True

    def forward(self, x):
        if not self.training or self.p == 0:
            return x
        
        # Create mask for entire channels
        mask = np.random.random((x.data.shape[0], x.data.shape[1], 1, 1)) > self.p
        mask = np.broadcast_to(mask, x.data.shape)
        
        if self.inplace:
            x.data = x.data * mask / (1 - self.p)
            return x
        return Tensor(x.data * mask / (1 - self.p), requires_grad=True)

class Dropout3d(Module):
    def __init__(self, p=0.5, inplace=False):
        super().__init__()
        self.p = p
        self.inplace = inplace
        self.training = True

    def forward(self, x):
        if not self.training or self.p == 0:
            return x
        
        # Create mask for entire 3D feature maps
        mask = np.random.random((x.data.shape[0], x.data.shape[1], 1, 1, 1)) > self.p
        mask = np.broadcast_to(mask, x.data.shape)
        
        if self.inplace:
            x.data = x.data * mask / (1 - self.p)
            return x
        return Tensor(x.data * mask / (1 - self.p), requires_grad=True)

class AlphaDropout(Module):
    def __init__(self, p=0.5, inplace=False):
        super().__init__()
        self.p = p
        self.inplace = inplace
        self.training = True
        # SELU parameters
        self.alpha = 1.6732632423543772848170429916717
        self.scale = 1.0507009873554804934193349852946
        
        self.alpha_p = -self.alpha * self.scale

    def forward(self, x):
        if not self.training or self.p == 0:
            return x
        
        # Keep mean and variance the same during training and evaluation
        mask = np.random.random(x.data.shape) > self.p
        
        # Calculate the affine transformation parameters
        a = ((1 - self.p) + self.p * self.alpha_p ** 2) ** (-0.5)
        b = -a * self.p * self.alpha_p
        
        if self.inplace:
            x.data = mask * x.data + (1 - mask) * self.alpha_p
            x.data = a * x.data + b
            return x
        return Tensor(a * (mask * x.data + (1 - mask) * self.alpha_p) + b, requires_grad=True)

class FeatureAlphaDropout(Module):
    def __init__(self, p=0.5, inplace=False):
        super().__init__()
        self.p = p
        self.inplace = inplace
        self.training = True
        # SELU parameters
        self.alpha = 1.6732632423543772848170429916717
        self.scale = 1.0507009873554804934193349852946
        
        self.alpha_p = -self.alpha * self.scale

    def forward(self, x):
        if not self.training or self.p == 0:
            return x
        
        # Create mask for entire features
        shape = list(x.data.shape)
        shape[1:] = [1] * (len(shape) - 1)
        mask = np.random.random(shape) > self.p
        mask = np.broadcast_to(mask, x.data.shape)
        
        # Calculate the affine transformation parameters
        a = ((1 - self.p) + self.p * self.alpha_p ** 2) ** (-0.5)
        b = -a * self.p * self.alpha_p
        
        if self.inplace:
            x.data = mask * x.data + (1 - mask) * self.alpha_p
            x.data = a * x.data + b
            return x
        return Tensor(a * (mask * x.data + (1 - mask) * self.alpha_p) + b, requires_grad=True)