"""
Probabilistic Optimization Module for OpenArchX v0.1.3

This module implements probabilistic optimization algorithms that handle uncertainty
in model parameters and hyperparameters, providing robust optimization under uncertainty.
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Callable, Any
from abc import ABC, abstractmethod
from .base import Optimizer


class ProbabilisticOptimizer(Optimizer):
    """
    Base class for probabilistic optimization algorithms that handle uncertainty
    in parameters and provide robust optimization under uncertainty.
    """
    
    def __init__(self, parameters, lr=0.001, weight_decay=0.0, clip_grad=None,
                 uncertainty_threshold=0.1, confidence_level=0.95):
        super().__init__(parameters, lr, weight_decay, clip_grad)
        self.uncertainty_threshold = uncertainty_threshold
        self.confidence_level = confidence_level
        self.parameter_uncertainties = {}
        self.optimization_history = []
        
    @abstractmethod
    def estimate_parameter_uncertainty(self, param_name: str) -> float:
        """Estimate uncertainty for a given parameter"""
        pass
    
    @abstractmethod
    def robust_update(self, param, grad, uncertainty: float) -> np.ndarray:
        """Perform robust parameter update considering uncertainty"""
        pass


class BayesianOptimizer(ProbabilisticOptimizer):
    """
    Bayesian optimization algorithm that maintains probability distributions
    over parameters and performs uncertainty-aware updates.
    """
    
    def __init__(self, parameters, lr=0.001, weight_decay=0.0, clip_grad=None,
                 uncertainty_threshold=0.1, confidence_level=0.95,
                 prior_variance=1.0, likelihood_variance=0.1):
        super().__init__(parameters, lr, weight_decay, clip_grad, 
                        uncertainty_threshold, confidence_level)
        self.prior_variance = prior_variance
        self.likelihood_variance = likelihood_variance
        
        # Initialize parameter statistics
        self.param_means = {}
        self.param_variances = {}
        self.param_samples = {}
        
        for i, param in enumerate(self.parameters):
            param_name = f"param_{i}"
            self.param_means[param_name] = param.data.copy()
            self.param_variances[param_name] = np.full_like(param.data, prior_variance)
            self.param_samples[param_name] = []
    
    def estimate_parameter_uncertainty(self, param_name: str) -> float:
        """Estimate uncertainty using parameter variance"""
        if param_name in self.param_variances:
            return np.mean(np.sqrt(self.param_variances[param_name]))
        return self.uncertainty_threshold
    
    def robust_update(self, param, grad, uncertainty: float) -> np.ndarray:
        """Bayesian parameter update with uncertainty consideration"""
        # Adjust learning rate based on uncertainty
        adaptive_lr = self.lr * (1.0 - min(uncertainty / self.uncertainty_threshold, 0.9))
        
        # Bayesian update with uncertainty weighting
        precision = 1.0 / (uncertainty + 1e-8)
        weighted_grad = grad * precision
        
        return param.data - adaptive_lr * weighted_grad
    
    def update_parameter_statistics(self, param_name: str, param_data: np.ndarray, 
                                  grad: np.ndarray) -> None:
        """Update Bayesian statistics for parameters"""
        # Update mean using exponential moving average
        alpha = 0.1
        self.param_means[param_name] = (1 - alpha) * self.param_means[param_name] + alpha * param_data
        
        # Update variance using gradient information and parameter changes
        param_diff = param_data - self.param_means[param_name]
        grad_variance = np.var(grad) if grad.size > 1 else self.likelihood_variance
        
        # Combine gradient variance with parameter change variance
        combined_variance = grad_variance + np.mean(param_diff ** 2)
        self.param_variances[param_name] = (1 - alpha) * self.param_variances[param_name] + \
                                          alpha * (combined_variance + self.likelihood_variance)
        
        # Store samples for uncertainty estimation
        self.param_samples[param_name].append(param_data.copy())
        if len(self.param_samples[param_name]) > 100:  # Keep last 100 samples
            self.param_samples[param_name].pop(0)
    
    def step(self):
        """Perform one optimization step with Bayesian updates"""
        self.clip_gradients()
        
        for i, param in enumerate(self.parameters):
            if param.grad is not None:
                param_name = f"param_{i}"
                
                # Estimate current uncertainty
                uncertainty = self.estimate_parameter_uncertainty(param_name)
                
                # Perform robust update
                new_data = self.robust_update(param, param.grad, uncertainty)
                
                # Apply weight decay
                if self.weight_decay > 0:
                    new_data -= self.weight_decay * param.data
                
                # Update parameter
                param.data = new_data
                
                # Update Bayesian statistics
                self.update_parameter_statistics(param_name, param.data, param.grad)
                
                # Store uncertainty information
                self.parameter_uncertainties[param_name] = uncertainty
        
        # Record optimization step
        self.optimization_history.append({
            'uncertainties': self.parameter_uncertainties.copy(),
            'step': len(self.optimization_history)
        })


class UncertaintyAwareHyperparameterOptimizer:
    """
    Hyperparameter optimizer that considers uncertainty in hyperparameter selection
    and provides robust hyperparameter optimization.
    """
    
    def __init__(self, hyperparameter_space: Dict[str, Tuple[float, float]],
                 acquisition_function: str = 'expected_improvement',
                 n_initial_samples: int = 10,
                 uncertainty_penalty: float = 0.1):
        self.hyperparameter_space = hyperparameter_space
        self.acquisition_function = acquisition_function
        self.n_initial_samples = n_initial_samples
        self.uncertainty_penalty = uncertainty_penalty
        
        self.evaluated_points = []
        self.performance_history = []
        self.uncertainty_history = []
        self.best_hyperparameters = None
        self.best_performance = float('inf')
    
    def sample_hyperparameters(self, n_samples: int = 1) -> List[Dict[str, float]]:
        """Sample hyperparameters from the search space"""
        samples = []
        for _ in range(n_samples):
            sample = {}
            for param_name, (low, high) in self.hyperparameter_space.items():
                sample[param_name] = np.random.uniform(low, high)
            samples.append(sample)
        return samples
    
    def gaussian_process_surrogate(self, X: np.ndarray, y: np.ndarray, 
                                 X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Simple Gaussian Process surrogate model for hyperparameter optimization"""
        # Simplified GP implementation
        n_train = X.shape[0]
        n_test = X_test.shape[0]
        
        # RBF kernel
        def rbf_kernel(x1, x2, length_scale=1.0):
            return np.exp(-0.5 * np.sum((x1 - x2)**2) / length_scale**2)
        
        # Build kernel matrices
        K = np.zeros((n_train, n_train))
        for i in range(n_train):
            for j in range(n_train):
                K[i, j] = rbf_kernel(X[i], X[j])
        
        K_star = np.zeros((n_test, n_train))
        for i in range(n_test):
            for j in range(n_train):
                K_star[i, j] = rbf_kernel(X_test[i], X[j])
        
        K_star_star = np.zeros((n_test, n_test))
        for i in range(n_test):
            for j in range(n_test):
                K_star_star[i, j] = rbf_kernel(X_test[i], X_test[j])
        
        # Add noise to diagonal
        K += 1e-6 * np.eye(n_train)
        
        # GP predictions
        try:
            K_inv = np.linalg.inv(K)
            mu = K_star @ K_inv @ y
            cov = K_star_star - K_star @ K_inv @ K_star.T
            sigma = np.sqrt(np.diag(cov))
        except np.linalg.LinAlgError:
            # Fallback to simple mean prediction
            mu = np.mean(y) * np.ones(n_test)
            sigma = np.std(y) * np.ones(n_test)
        
        return mu, sigma
    
    def expected_improvement(self, mu: np.ndarray, sigma: np.ndarray, 
                           best_value: float) -> np.ndarray:
        """Expected Improvement acquisition function"""
        improvement = best_value - mu
        Z = improvement / (sigma + 1e-8)
        
        # Standard normal CDF and PDF approximations
        def norm_cdf(x):
            return 0.5 * (1 + np.tanh(x / np.sqrt(2)))
        
        def norm_pdf(x):
            return np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)
        
        ei = improvement * norm_cdf(Z) + sigma * norm_pdf(Z)
        # Ensure non-negative values
        return np.maximum(ei, 0.0)
    
    def uncertainty_penalized_acquisition(self, mu: np.ndarray, sigma: np.ndarray,
                                        best_value: float) -> np.ndarray:
        """Acquisition function with uncertainty penalty"""
        ei = self.expected_improvement(mu, sigma, best_value)
        uncertainty_penalty = self.uncertainty_penalty * sigma
        return ei - uncertainty_penalty
    
    def suggest_hyperparameters(self) -> Dict[str, float]:
        """Suggest next hyperparameters to evaluate"""
        if len(self.evaluated_points) < self.n_initial_samples:
            # Random sampling for initial points
            return self.sample_hyperparameters(1)[0]
        
        # Convert evaluated points to arrays
        X = np.array([[point[param] for param in self.hyperparameter_space.keys()] 
                     for point in self.evaluated_points])
        y = np.array(self.performance_history)
        
        # Generate candidate points
        candidates = self.sample_hyperparameters(100)
        X_candidates = np.array([[candidate[param] for param in self.hyperparameter_space.keys()] 
                               for candidate in candidates])
        
        # Get GP predictions
        mu, sigma = self.gaussian_process_surrogate(X, y, X_candidates)
        
        # Calculate acquisition function
        if self.acquisition_function == 'expected_improvement':
            acquisition_values = self.expected_improvement(mu, sigma, self.best_performance)
        else:  # uncertainty_penalized
            acquisition_values = self.uncertainty_penalized_acquisition(mu, sigma, self.best_performance)
        
        # Select best candidate
        best_idx = np.argmax(acquisition_values)
        best_candidate = candidates[best_idx]
        
        return best_candidate
    
    def update(self, hyperparameters: Dict[str, float], performance: float, 
              uncertainty: float = 0.0) -> None:
        """Update optimizer with evaluation results"""
        self.evaluated_points.append(hyperparameters.copy())
        self.performance_history.append(performance)
        self.uncertainty_history.append(uncertainty)
        
        if performance < self.best_performance:
            self.best_performance = performance
            self.best_hyperparameters = hyperparameters.copy()
    
    def get_best_hyperparameters(self) -> Tuple[Dict[str, float], float]:
        """Get best hyperparameters found so far"""
        return self.best_hyperparameters, self.best_performance


class RobustOptimizationEngine:
    """
    Engine for robust optimization under uncertainty that combines multiple
    probabilistic optimization strategies.
    """
    
    def __init__(self, noise_level: float = 0.1, robustness_factor: float = 0.5):
        self.noise_level = noise_level
        self.robustness_factor = robustness_factor
        self.optimization_strategies = []
        self.performance_tracker = {}
    
    def add_strategy(self, strategy_name: str, optimizer: ProbabilisticOptimizer) -> None:
        """Add a probabilistic optimization strategy"""
        self.optimization_strategies.append((strategy_name, optimizer))
        self.performance_tracker[strategy_name] = []
    
    def robust_loss_function(self, loss_fn: Callable, parameters: List, 
                           n_samples: int = 10) -> Tuple[float, float]:
        """
        Compute robust loss that considers uncertainty in parameters.
        Returns mean loss and uncertainty estimate.
        """
        losses = []
        
        for _ in range(n_samples):
            # Add noise to parameters to simulate uncertainty
            noisy_params = []
            for param in parameters:
                noise = np.random.normal(0, self.noise_level, param.data.shape)
                noisy_param_data = param.data + noise
                
                # Create temporary parameter with noisy data
                class TempParam:
                    def __init__(self, data):
                        self.data = data
                
                noisy_params.append(TempParam(noisy_param_data))
            
            # Evaluate loss with noisy parameters
            loss = loss_fn(noisy_params)
            losses.append(loss)
        
        mean_loss = np.mean(losses)
        uncertainty = np.std(losses)
        
        return mean_loss, uncertainty
    
    def distributionally_robust_loss(self, loss_fn: Callable, parameters: List,
                                   epsilon: float = 0.1) -> float:
        """
        Compute distributionally robust loss using worst-case optimization.
        """
        # Sample from uncertainty set
        worst_case_loss = float('-inf')
        
        for _ in range(20):  # Sample multiple perturbations
            # Generate adversarial perturbation
            perturbed_params = []
            for param in parameters:
                perturbation = np.random.uniform(-epsilon, epsilon, param.data.shape)
                perturbed_data = param.data + perturbation
                
                class TempParam:
                    def __init__(self, data):
                        self.data = data
                
                perturbed_params.append(TempParam(perturbed_data))
            
            # Evaluate loss
            loss = loss_fn(perturbed_params)
            worst_case_loss = max(worst_case_loss, loss)
        
        return worst_case_loss
    
    def adaptive_robustness_control(self, current_uncertainty: float) -> float:
        """Adaptively control robustness based on current uncertainty level"""
        if current_uncertainty > 0.2:
            return min(self.robustness_factor * 1.5, 1.0)
        elif current_uncertainty < 0.05:
            return max(self.robustness_factor * 0.7, 0.1)
        else:
            return self.robustness_factor
    
    def ensemble_optimization_step(self, loss_fn: Callable, parameters: List) -> Dict[str, Any]:
        """
        Perform optimization step using ensemble of probabilistic strategies.
        """
        results = {}
        
        for strategy_name, optimizer in self.optimization_strategies:
            # Compute robust loss for this strategy
            mean_loss, uncertainty = self.robust_loss_function(loss_fn, parameters)
            
            # Adapt robustness based on uncertainty
            adaptive_robustness = self.adaptive_robustness_control(uncertainty)
            
            # Compute distributionally robust loss if high uncertainty
            if uncertainty > 0.15:
                robust_loss = self.distributionally_robust_loss(loss_fn, parameters)
                final_loss = adaptive_robustness * robust_loss + (1 - adaptive_robustness) * mean_loss
            else:
                final_loss = mean_loss
            
            # Store results
            results[strategy_name] = {
                'loss': final_loss,
                'uncertainty': uncertainty,
                'robustness_factor': adaptive_robustness
            }
            
            # Track performance
            self.performance_tracker[strategy_name].append({
                'loss': final_loss,
                'uncertainty': uncertainty,
                'step': len(self.performance_tracker[strategy_name])
            })
        
        return results
    
    def get_best_strategy(self) -> str:
        """Get the best performing strategy based on robust performance"""
        best_strategy = None
        best_score = float('inf')
        
        for strategy_name, history in self.performance_tracker.items():
            if len(history) > 0:
                # Compute robust performance score (lower is better)
                recent_losses = [h['loss'] for h in history[-10:]]  # Last 10 steps
                recent_uncertainties = [h['uncertainty'] for h in history[-10:]]
                
                mean_loss = np.mean(recent_losses)
                mean_uncertainty = np.mean(recent_uncertainties)
                
                # Penalize high uncertainty
                robust_score = mean_loss + 0.5 * mean_uncertainty
                
                if robust_score < best_score:
                    best_score = robust_score
                    best_strategy = strategy_name
        
        return best_strategy


# Factory function for creating probabilistic optimizers
def create_probabilistic_optimizer(optimizer_type: str = 'bayesian', **kwargs) -> ProbabilisticOptimizer:
    """
    Factory function to create probabilistic optimizers.
    
    Args:
        optimizer_type: Type of probabilistic optimizer ('bayesian')
        **kwargs: Additional arguments for the optimizer
    
    Returns:
        ProbabilisticOptimizer instance
    """
    if optimizer_type == 'bayesian':
        return BayesianOptimizer(**kwargs)
    else:
        raise ValueError(f"Unknown probabilistic optimizer type: {optimizer_type}")


# Utility functions for probabilistic optimization
def estimate_model_uncertainty(model_predictions: np.ndarray, n_samples: int = 100) -> float:
    """
    Estimate model uncertainty using prediction variance.
    
    Args:
        model_predictions: Array of model predictions from multiple samples
        n_samples: Number of samples used for uncertainty estimation
    
    Returns:
        Uncertainty estimate (standard deviation of predictions)
    """
    if len(model_predictions.shape) == 1:
        return np.std(model_predictions)
    else:
        return np.mean(np.std(model_predictions, axis=0))


def uncertainty_weighted_loss(predictions: np.ndarray, targets: np.ndarray, 
                            uncertainties: np.ndarray) -> float:
    """
    Compute uncertainty-weighted loss that penalizes uncertain predictions.
    
    Args:
        predictions: Model predictions
        targets: Target values
        uncertainties: Uncertainty estimates for each prediction
    
    Returns:
        Uncertainty-weighted loss value
    """
    mse_loss = np.mean((predictions - targets) ** 2)
    uncertainty_penalty = np.mean(uncertainties)
    
    return mse_loss + 0.1 * uncertainty_penalty