import numpy as np
from ..core.tensor import Tensor
from .module import Module

class _ConstantPadNd(Module):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def _pad_array(self, x, pad_width):
        return np.pad(x.data, pad_width, mode='constant', constant_values=self.value)

class ConstantPad1d(_ConstantPadNd):
    def __init__(self, padding, value=0):
        super().__init__(value)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)

    def forward(self, x):
        pad_width = ((0, 0),) * (len(x.data.shape) - 1) + (self.padding,)
        return Tensor(self._pad_array(x, pad_width), requires_grad=True)

class ConstantPad2d(_ConstantPadNd):
    def __init__(self, padding, value=0):
        super().__init__(value)
        if isinstance(padding, int):
            self.padding = ((padding, padding), (padding, padding))
        elif len(padding) == 2:
            self.padding = ((padding[0], padding[0]), (padding[1], padding[1]))
        else:
            self.padding = ((padding[0], padding[1]), (padding[2], padding[3]))

    def forward(self, x):
        pad_width = ((0, 0), (0, 0)) + self.padding
        return Tensor(self._pad_array(x, pad_width), requires_grad=True)

class ConstantPad3d(_ConstantPadNd):
    def __init__(self, padding, value=0):
        super().__init__(value)
        if isinstance(padding, int):
            self.padding = ((padding, padding), (padding, padding), (padding, padding))
        elif len(padding) == 3:
            self.padding = ((padding[0], padding[0]), 
                          (padding[1], padding[1]),
                          (padding[2], padding[2]))
        else:
            self.padding = ((padding[0], padding[1]),
                          (padding[2], padding[3]),
                          (padding[4], padding[5]))

    def forward(self, x):
        pad_width = ((0, 0), (0, 0)) + self.padding
        return Tensor(self._pad_array(x, pad_width), requires_grad=True)

class ReflectionPad1d(Module):
    def __init__(self, padding):
        super().__init__()
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)

    def forward(self, x):
        pad_width = ((0, 0),) * (len(x.data.shape) - 1) + (self.padding,)
        return Tensor(np.pad(x.data, pad_width, mode='reflect'), requires_grad=True)

class ReflectionPad2d(Module):
    def __init__(self, padding):
        super().__init__()
        if isinstance(padding, int):
            self.padding = ((padding, padding), (padding, padding))
        elif len(padding) == 2:
            self.padding = ((padding[0], padding[0]), (padding[1], padding[1]))
        else:
            self.padding = ((padding[0], padding[1]), (padding[2], padding[3]))

    def forward(self, x):
        pad_width = ((0, 0), (0, 0)) + self.padding
        return Tensor(np.pad(x.data, pad_width, mode='reflect'), requires_grad=True)

class ReplicationPad1d(Module):
    def __init__(self, padding):
        super().__init__()
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)

    def forward(self, x):
        pad_width = ((0, 0),) * (len(x.data.shape) - 1) + (self.padding,)
        return Tensor(np.pad(x.data, pad_width, mode='edge'), requires_grad=True)

class ReplicationPad2d(Module):
    def __init__(self, padding):
        super().__init__()
        if isinstance(padding, int):
            self.padding = ((padding, padding), (padding, padding))
        elif len(padding) == 2:
            self.padding = ((padding[0], padding[0]), (padding[1], padding[1]))
        else:
            self.padding = ((padding[0], padding[1]), (padding[2], padding[3]))

    def forward(self, x):
        pad_width = ((0, 0), (0, 0)) + self.padding
        return Tensor(np.pad(x.data, pad_width, mode='edge'), requires_grad=True)

class ReplicationPad3d(Module):
    def __init__(self, padding):
        super().__init__()
        if isinstance(padding, int):
            self.padding = ((padding, padding), (padding, padding), (padding, padding))
        elif len(padding) == 3:
            self.padding = ((padding[0], padding[0]), 
                          (padding[1], padding[1]),
                          (padding[2], padding[2]))
        else:
            self.padding = ((padding[0], padding[1]),
                          (padding[2], padding[3]),
                          (padding[4], padding[5]))

    def forward(self, x):
        pad_width = ((0, 0), (0, 0)) + self.padding
        return Tensor(np.pad(x.data, pad_width, mode='edge'), requires_grad=True)

class ZeroPad2d(ConstantPad2d):
    def __init__(self, padding):
        super().__init__(padding, value=0)