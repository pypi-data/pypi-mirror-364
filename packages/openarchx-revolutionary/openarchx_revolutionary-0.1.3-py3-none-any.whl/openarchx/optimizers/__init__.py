"""
OpenArchX Optimizers Module

This module contains various optimization algorithms including:
- Standard optimizers (SGD, Adam)
- Adaptive optimizers
- Modern optimizers
- Probabilistic optimizers with uncertainty quantification
"""

from .base import Optimizer
from .sgd import SGD
from .adam import Adam
from .adaptive import Adagrad, Adadelta, RMSprop
from .modern import RAdam, AdaBelief, Lion
from .optx import OptX
from .probabilistic import (
    BayesianOptimizer,
    UncertaintyAwareHyperparameterOptimizer,
    RobustOptimizationEngine,
    create_probabilistic_optimizer,
    estimate_model_uncertainty,
    uncertainty_weighted_loss
)

__all__ = [
    'Optimizer',
    'SGD',
    'Adam',
    'Adagrad',
    'Adadelta',
    'RMSprop',
    'RAdam',
    'AdaBelief',
    'Lion',
    'OptX',
    'BayesianOptimizer',
    'UncertaintyAwareHyperparameterOptimizer',
    'RobustOptimizationEngine',
    'create_probabilistic_optimizer',
    'estimate_model_uncertainty',
    'uncertainty_weighted_loss'
]