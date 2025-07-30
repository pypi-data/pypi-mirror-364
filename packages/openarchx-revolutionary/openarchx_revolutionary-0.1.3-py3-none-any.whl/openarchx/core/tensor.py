import numpy as np

class Tensor:
    def __init__(self, data, requires_grad=False, device='cpu'):
        self.data = np.asarray(data, dtype=np.float32)
        self.requires_grad = requires_grad
        self.grad = None if requires_grad else None
        self._backward = lambda: None
        self._prev = set()
        self.device = device
        
        if device == 'cuda':
            # Late import to avoid circular dependency
            from ..cuda import CUDA_AVAILABLE, to_gpu
            if not CUDA_AVAILABLE:
                raise RuntimeError("CUDA is not available")
            self.data = to_gpu(self.data)

    def to(self, device):
        """Move tensor to specified device (cpu/cuda)"""
        if device == self.device:
            return self
        
        # Late imports to avoid circular dependency
        from ..cuda import CUDA_AVAILABLE, to_gpu, to_cpu
        
        if device == 'cuda' and not CUDA_AVAILABLE:
            raise RuntimeError("CUDA is not available")
        
        new_tensor = Tensor(
            to_gpu(self.data) if device == 'cuda' else to_cpu(self.data),
            requires_grad=self.requires_grad,
            device=device
        )
        new_tensor.grad = self.grad
        new_tensor._backward = self._backward
        new_tensor._prev = self._prev
        return new_tensor

    def cuda(self):
        """Move tensor to GPU"""
        return self.to('cuda')

    def cpu(self):
        """Move tensor to CPU"""
        return self.to('cpu')

    def is_cuda(self):
        """Check if tensor is on GPU"""
        return self.device == 'cuda'

    def _get_array_module(self):
        """Get the appropriate array module (numpy or cupy) for the tensor"""
        from ..cuda import get_array_module
        return get_array_module(self.data)

    # Basic arithmetic operations
    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, device=self.device)
        xp = self._get_array_module()
        out = Tensor(xp.add(self.data, other.data), 
                    requires_grad=self.requires_grad or other.requires_grad,
                    device=self.device)
        
        def _backward():
            if self.requires_grad:
                self.grad = xp.add(self.grad if self.grad is not None else 0, out.grad)
            if other.requires_grad:
                other.grad = xp.add(other.grad if other.grad is not None else 0, out.grad)
        
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, device=self.device)
        xp = self._get_array_module()
        out = Tensor(xp.multiply(self.data, other.data), 
                    requires_grad=self.requires_grad or other.requires_grad,
                    device=self.device)
        
        def _backward():
            if self.requires_grad:
                self.grad = xp.add(self.grad if self.grad is not None else 0,
                                 xp.multiply(other.data, out.grad))
            if other.requires_grad:
                other.grad = xp.add(other.grad if other.grad is not None else 0,
                                  xp.multiply(self.data, out.grad))
        
        out._backward = _backward
        out._prev = {self, other}
        return out

    def __matmul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, device=self.device)
        if self.device == 'cuda' and other.device == 'cuda':
            from ..cuda.cuda_ops import matmul
            out_data = matmul(self.data, other.data)
        else:
            xp = self._get_array_module()
            out_data = xp.matmul(self.data, other.data)
        
        out = Tensor(out_data,
                    requires_grad=self.requires_grad or other.requires_grad,
                    device=self.device)
        
        def _backward():
            if self.requires_grad:
                xp = self._get_array_module()
                self.grad = xp.add(self.grad if self.grad is not None else 0,
                                 xp.matmul(out.grad, other.data.T))
            if other.requires_grad:
                xp = other._get_array_module()
                other.grad = xp.add(other.grad if other.grad is not None else 0,
                                  xp.matmul(self.data.T, out.grad))
        
        out._backward = _backward
        out._prev = {self, other}
        return out

    def sum(self, axis=None, keepdims=False):
        xp = self._get_array_module()
        out = Tensor(xp.sum(self.data, axis=axis, keepdims=keepdims),
                    requires_grad=self.requires_grad,
                    device=self.device)
        
        def _backward():
            if self.requires_grad:
                grad_shape = list(self.data.shape)
                if axis is not None and not keepdims:
                    grad_shape[axis] = 1
                self.grad = xp.add(self.grad if self.grad is not None else 0,
                                 xp.broadcast_to(out.grad.reshape(grad_shape), self.data.shape))
        
        out._backward = _backward
        out._prev = {self}
        return out

    def mean(self, axis=None, keepdims=False):
        xp = self._get_array_module()
        out = Tensor(xp.mean(self.data, axis=axis, keepdims=keepdims),
                    requires_grad=self.requires_grad,
                    device=self.device)
        
        def _backward():
            if self.requires_grad:
                size = self.data.size if axis is None else self.data.shape[axis]
                grad_shape = list(self.data.shape)
                if axis is not None and not keepdims:
                    grad_shape[axis] = 1
                self.grad = xp.add(self.grad if self.grad is not None else 0,
                                 xp.broadcast_to(out.grad.reshape(grad_shape), self.data.shape) / size)
        
        out._backward = _backward
        out._prev = {self}
        return out

    def backward(self, grad=None):
        if not self.requires_grad:
            return

        if grad is None:
            xp = self._get_array_module()
            grad = xp.ones_like(self.data)
        
        self.grad = grad
        self._backward()
        
        for prev in self._prev:
            if prev.requires_grad:
                prev.backward()

    def zero_grad(self):
        if self.grad is not None:
            xp = self._get_array_module()
            self.grad = xp.zeros_like(self.grad)

    def __repr__(self):
        return f"Tensor({self.data}, requires_grad={self.requires_grad}, device='{self.device}')"