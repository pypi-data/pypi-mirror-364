import numpy as np
from ..core.tensor import Tensor

def mse_loss(pred: Tensor, target) -> Tensor:
    """Mean Squared Error Loss"""
    if not isinstance(target, Tensor):
        target = Tensor(target)
    return ((pred - target) * (pred - target)).mean()

def cross_entropy_loss(pred: Tensor, target) -> Tensor:
    """Cross Entropy Loss for classification with numerical stability"""
    if not isinstance(target, Tensor):
        target = Tensor(target)
    
    # Add small epsilon for numerical stability
    eps = 1e-7
    pred_clipped = Tensor(np.clip(pred.data, eps, 1.0 - eps))
    
    # Calculate cross entropy
    loss = -((target * pred_clipped.log()).sum(axis=-1)).mean()
    return loss