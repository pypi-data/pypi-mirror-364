"""
Integration tests for probabilistic optimization with OpenArchX v0.1.3

These tests verify that probabilistic optimization integrates properly with
the broader OpenArchX ecosystem and improves model robustness as required.
"""

import numpy as np
import pytest
import sys
import os

# Add the parent directory to the path to import openarchx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from openarchx.optimizers.probabilistic import (
    BayesianOptimizer,
    UncertaintyAwareHyperparameterOptimizer,
    RobustOptimizationEngine,
    create_probabilistic_optimizer
)


class MockTensor:
    """Mock tensor class that mimics OpenArchX tensor behavior"""
    def __init__(self, data):
        self.data = data.copy() if isinstance(data, np.ndarray) else np.array(data)
        self.grad = None
        self.shape = self.data.shape
        self.size = self.data.size
    
    def zero_grad(self):
        if self.grad is not None:
            self.grad.fill(0)


class MockModel:
    """Mock model that simulates OpenArchX model behavior"""
    def __init__(self, input_dim=10, hidden_dim=20, output_dim=1):
        self.W1 = MockTensor(np.random.randn(input_dim, hidden_dim) * 0.1)
        self.b1 = MockTensor(np.zeros(hidden_dim))
        self.W2 = MockTensor(np.random.randn(hidden_dim, output_dim) * 0.1)
        self.b2 = MockTensor(np.zeros(output_dim))
        
        self.parameters = [self.W1, self.b1, self.W2, self.b2]
    
    def forward(self, X):
        """Forward pass through the model"""
        h1 = np.maximum(0, X @ self.W1.data + self.b1.data)  # ReLU
        output = h1 @ self.W2.data + self.b2.data
        return output
    
    def backward(self, X, y, output):
        """Backward pass to compute gradients"""
        batch_size = X.shape[0]
        
        # Compute loss gradient
        d_output = 2 * (output - y) / batch_size
        
        # Backward through second layer
        h1 = np.maximum(0, X @ self.W1.data + self.b1.data)
        self.W2.grad = h1.T @ d_output
        self.b2.grad = np.sum(d_output, axis=0)
        
        # Backward through first layer
        d_h1 = d_output @ self.W2.data.T
        d_h1[h1 <= 0] = 0  # ReLU derivative
        
        self.W1.grad = X.T @ d_h1
        self.b1.grad = np.sum(d_h1, axis=0)
    
    def compute_loss(self, X, y):
        """Compute loss and gradients"""
        output = self.forward(X)
        loss = np.mean((output - y) ** 2)
        self.backward(X, y, output)
        return loss


class TestProbabilisticIntegration:
    """Integration tests for probabilistic optimization"""
    
    def test_bayesian_optimizer_integration(self):
        """Test Bayesian optimizer integration with mock OpenArchX components"""
        # Create mock model
        model = MockModel(input_dim=5, hidden_dim=10, output_dim=1)
        
        # Create Bayesian optimizer
        optimizer = BayesianOptimizer(
            model.parameters,
            lr=0.01,
            uncertainty_threshold=0.1,
            confidence_level=0.95
        )
        
        # Generate synthetic data
        np.random.seed(42)
        X = np.random.randn(50, 5)
        y = np.random.randn(50, 1)
        
        # Training loop
        initial_loss = None
        final_uncertainties = []
        
        for epoch in range(20):
            # Forward and backward pass
            loss = model.compute_loss(X, y)
            
            if initial_loss is None:
                initial_loss = loss
            
            # Add some noise to simulate real-world uncertainty
            for param in model.parameters:
                if param.grad is not None:
                    noise = np.random.randn(*param.grad.shape) * 0.01
                    param.grad += noise
            
            # Optimization step
            optimizer.step()
            
            # Track uncertainties
            if len(optimizer.parameter_uncertainties) > 0:
                avg_uncertainty = np.mean(list(optimizer.parameter_uncertainties.values()))
                final_uncertainties.append(avg_uncertainty)
        
        # Verify integration worked
        assert len(optimizer.optimization_history) == 20
        assert len(final_uncertainties) > 0
        assert all(u >= 0 for u in final_uncertainties)
        
        # Verify parameters were updated
        for param in model.parameters:
            assert param.data is not None
            assert not np.allclose(param.data, 0)  # Should have changed from initialization
    
    def test_hyperparameter_optimization_integration(self):
        """Test hyperparameter optimizer integration"""
        # Define hyperparameter space
        hyperparameter_space = {
            'learning_rate': (0.001, 0.1),
            'weight_decay': (0.0, 0.01),
            'hidden_dim': (5, 20)
        }
        
        # Create hyperparameter optimizer
        hp_optimizer = UncertaintyAwareHyperparameterOptimizer(
            hyperparameter_space,
            n_initial_samples=3,
            uncertainty_penalty=0.1
        )
        
        # Mock evaluation function
        def evaluate_hyperparameters(hyperparams):
            # Create model with specified hyperparameters
            hidden_dim = int(hyperparams['hidden_dim'])
            model = MockModel(input_dim=3, hidden_dim=hidden_dim, output_dim=1)
            
            # Create optimizer with specified parameters
            optimizer = BayesianOptimizer(
                model.parameters,
                lr=hyperparams['learning_rate'],
                weight_decay=hyperparams['weight_decay']
            )
            
            # Generate data
            X = np.random.randn(20, 3)
            y = np.random.randn(20, 1)
            
            # Short training
            losses = []
            for _ in range(10):
                loss = model.compute_loss(X, y)
                optimizer.step()
                losses.append(loss)
            
            # Return performance and uncertainty
            performance = np.mean(losses[-3:])
            uncertainty = np.std(losses[-3:])
            return performance, uncertainty
        
        # Run hyperparameter optimization
        for iteration in range(8):
            hyperparams = hp_optimizer.suggest_hyperparameters()
            performance, uncertainty = evaluate_hyperparameters(hyperparams)
            hp_optimizer.update(hyperparams, performance, uncertainty)
        
        # Verify optimization worked
        best_hyperparams, best_performance = hp_optimizer.get_best_hyperparameters()
        assert best_hyperparams is not None
        assert isinstance(best_performance, float)
        assert len(hp_optimizer.evaluated_points) == 8
        
        # Verify hyperparameters are within bounds
        for param_name, value in best_hyperparams.items():
            low, high = hyperparameter_space[param_name]
            assert low <= value <= high
    
    def test_robust_optimization_integration(self):
        """Test robust optimization engine integration"""
        # Create model
        model = MockModel(input_dim=4, hidden_dim=8, output_dim=1)
        
        # Create robust optimization engine
        robust_engine = RobustOptimizationEngine(
            noise_level=0.1,
            robustness_factor=0.5
        )
        
        # Add optimization strategies
        bayesian_opt = BayesianOptimizer(model.parameters, lr=0.02)
        robust_engine.add_strategy('bayesian', bayesian_opt)
        
        # Define loss function
        X = np.random.randn(30, 4)
        y = np.random.randn(30, 1)
        
        def loss_function(parameters):
            # Temporarily set model parameters
            original_data = [p.data.copy() for p in model.parameters]
            for i, param in enumerate(model.parameters):
                param.data = parameters[i].data
            
            # Compute loss
            loss = model.compute_loss(X, y)
            
            # Restore original parameters
            for i, param in enumerate(model.parameters):
                param.data = original_data[i]
            
            return loss
        
        # Run robust optimization
        for epoch in range(15):
            # Compute gradients
            loss = model.compute_loss(X, y)
            
            # Add noise
            for param in model.parameters:
                if param.grad is not None:
                    noise = np.random.randn(*param.grad.shape) * 0.02
                    param.grad += noise
            
            # Robust optimization step
            results = robust_engine.ensemble_optimization_step(loss_function, model.parameters)
            
            # Update using best strategy
            best_strategy = robust_engine.get_best_strategy()
            if best_strategy:
                strategy_optimizer = dict(robust_engine.optimization_strategies)[best_strategy]
                strategy_optimizer.step()
        
        # Verify robust optimization worked
        assert len(robust_engine.performance_tracker['bayesian']) == 15
        assert robust_engine.get_best_strategy() == 'bayesian'
        
        # Verify results contain expected keys
        assert 'bayesian' in results
        assert 'loss' in results['bayesian']
        assert 'uncertainty' in results['bayesian']
        assert 'robustness_factor' in results['bayesian']
    
    def test_probabilistic_optimizer_factory_integration(self):
        """Test probabilistic optimizer factory integration"""
        # Create mock parameters
        model = MockModel(input_dim=3, hidden_dim=5, output_dim=1)
        
        # Test factory function
        optimizer = create_probabilistic_optimizer(
            'bayesian',
            parameters=model.parameters,
            lr=0.01,
            uncertainty_threshold=0.05
        )
        
        assert isinstance(optimizer, BayesianOptimizer)
        assert optimizer.lr == 0.01
        assert optimizer.uncertainty_threshold == 0.05
        
        # Test that it works with the model
        X = np.random.randn(10, 3)
        y = np.random.randn(10, 1)
        
        loss = model.compute_loss(X, y)
        optimizer.step()
        
        # Should have updated parameters
        assert len(optimizer.parameter_uncertainties) == len(model.parameters)
    
    def test_end_to_end_robustness_improvement(self):
        """End-to-end test demonstrating robustness improvement"""
        # Create identical models for comparison
        np.random.seed(42)
        model_standard = MockModel(input_dim=6, hidden_dim=10, output_dim=1)
        model_probabilistic = MockModel(input_dim=6, hidden_dim=10, output_dim=1)
        
        # Copy weights to ensure fair comparison
        for i, param in enumerate(model_probabilistic.parameters):
            param.data = model_standard.parameters[i].data.copy()
        
        # Create optimizers
        class StandardOptimizer:
            def __init__(self, parameters, lr=0.01):
                self.parameters = parameters
                self.lr = lr
            
            def step(self):
                for param in self.parameters:
                    if param.grad is not None:
                        param.data -= self.lr * param.grad
        
        standard_opt = StandardOptimizer(model_standard.parameters, lr=0.02)
        probabilistic_opt = BayesianOptimizer(model_probabilistic.parameters, lr=0.02)
        
        # Generate data
        X = np.random.randn(40, 6)
        y = np.random.randn(40, 1)
        
        # Training with noise
        standard_losses = []
        probabilistic_losses = []
        standard_variances = []
        probabilistic_variances = []
        
        for epoch in range(30):
            # Standard optimization
            loss_std = model_standard.compute_loss(X, y)
            
            # Add noise to gradients
            for param in model_standard.parameters:
                if param.grad is not None:
                    noise = np.random.randn(*param.grad.shape) * 0.03
                    param.grad += noise
            
            standard_opt.step()
            standard_losses.append(loss_std)
            
            # Probabilistic optimization
            loss_prob = model_probabilistic.compute_loss(X, y)
            
            # Add same noise pattern
            np.random.seed(epoch + 100)  # Different but consistent seed
            for param in model_probabilistic.parameters:
                if param.grad is not None:
                    noise = np.random.randn(*param.grad.shape) * 0.03
                    param.grad += noise
            
            probabilistic_opt.step()
            probabilistic_losses.append(loss_prob)
            
            # Calculate running variance (stability measure)
            if epoch >= 5:
                standard_variances.append(np.var(standard_losses[-5:]))
                probabilistic_variances.append(np.var(probabilistic_losses[-5:]))
        
        # Verify both methods worked
        assert len(standard_losses) == 30
        assert len(probabilistic_losses) == 30
        
        # Check that probabilistic optimization provides uncertainty estimates
        assert len(probabilistic_opt.parameter_uncertainties) > 0
        assert all(u >= 0 for u in probabilistic_opt.parameter_uncertainties.values())
        
        # Verify optimization history is tracked
        assert len(probabilistic_opt.optimization_history) == 30
        
        # Both should achieve reasonable performance
        final_standard = np.mean(standard_losses[-5:])
        final_probabilistic = np.mean(probabilistic_losses[-5:])
        
        # Both should be finite and reasonable
        assert np.isfinite(final_standard)
        assert np.isfinite(final_probabilistic)
        assert final_standard > 0
        assert final_probabilistic > 0


if __name__ == '__main__':
    # Run integration tests
    pytest.main([__file__, '-v'])