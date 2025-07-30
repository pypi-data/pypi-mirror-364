import numpy as np
from .base import Optimizer

class RAdam(Optimizer):
    """Rectified Adam Optimizer"""
    def __init__(self, parameters, lr=0.001, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.betas = betas
        self.eps = eps
        self.m = [np.zeros_like(param.data) for param in parameters]
        self.v = [np.zeros_like(param.data) for param in parameters]
        self.step_count = 0
        
    def step(self):
        self.step_count += 1
        self.clip_gradients()
        
        beta1, beta2 = self.betas
        bias_correction1 = 1 - beta1 ** self.step_count
        bias_correction2 = 1 - beta2 ** self.step_count
        
        rho_inf = 2 / (1 - beta2) - 1
        rho_t = rho_inf - 2 * self.step_count * beta2 ** self.step_count / bias_correction2
        
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                
                self.m[i] = beta1 * self.m[i] + (1 - beta1) * grad
                self.v[i] = beta2 * self.v[i] + (1 - beta2) * np.square(grad)
                
                m_hat = self.m[i] / bias_correction1
                
                if rho_t > 4:
                    r = np.sqrt(((rho_t - 4) * (rho_t - 2) * rho_inf) / ((rho_inf - 4) * (rho_inf - 2) * rho_t))
                    v_hat = np.sqrt(self.v[i] / bias_correction2)
                    param.data -= self.lr * r * m_hat / (v_hat + self.eps)
                else:
                    param.data -= self.lr * m_hat

class AdaBelief(Optimizer):
    """AdaBelief Optimizer"""
    def __init__(self, parameters, lr=0.001, betas=(0.9, 0.999), eps=1e-16, weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.betas = betas
        self.eps = eps
        self.m = [np.zeros_like(param.data) for param in parameters]
        self.s = [np.zeros_like(param.data) for param in parameters]
        self.step_count = 0

    def step(self):
        self.step_count += 1
        self.clip_gradients()
        
        beta1, beta2 = self.betas
        bias_correction1 = 1 - beta1 ** self.step_count
        bias_correction2 = 1 - beta2 ** self.step_count
        
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                
                self.m[i] = beta1 * self.m[i] + (1 - beta1) * grad
                diff = grad - self.m[i]
                self.s[i] = beta2 * self.s[i] + (1 - beta2) * np.square(diff)
                
                m_hat = self.m[i] / bias_correction1
                s_hat = self.s[i] / bias_correction2
                
                param.data -= self.lr * m_hat / (np.sqrt(s_hat) + self.eps)

class Lion(Optimizer):
    """Lion Optimizer (Learning with Inner Optimization)"""
    def __init__(self, parameters, lr=0.0001, betas=(0.9, 0.99), weight_decay=0.0, clip_grad=None):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.betas = betas
        self.m = [np.zeros_like(param.data) for param in parameters]

    def step(self):
        self.clip_gradients()
        beta1, beta2 = self.betas
        
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                grad = param.grad
                if self.weight_decay > 0:
                    grad = grad + self.weight_decay * param.data
                
                update = beta1 * self.m[i] + (1 - beta1) * grad
                old_m = self.m[i].copy()
                self.m[i] = beta2 * self.m[i] + (1 - beta2) * grad
                
                # Update using sign of momentum
                param.data -= self.lr * np.sign(update)