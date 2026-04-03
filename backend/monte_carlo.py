import numpy as np
import pandas as pd

class MonteCarloSimulator:
    def __init__(self, model, iterations=1000, confidence_interval=0.95):
        self.model = model
        self.iterations = iterations
        self.confidence_interval = confidence_interval

    def simulate_risk(self, input_data, std_dev=2.5):
        """
        Simulates risk scores using a normal distribution of noise
        around the predicted value.
        """
        base_prediction = self.model.predict(input_data)[0]
        
        # Simulate noise using normal distribution
        # std_dev represents the model's uncertainty or historical volatility
        simulated_scores = np.random.normal(base_prediction, std_dev, self.iterations)
        
        lower_bound = np.percentile(simulated_scores, (1 - self.confidence_interval) / 2 * 100)
        upper_bound = np.percentile(simulated_scores, (1 + self.confidence_interval) / 2 * 100)
        
        return {
            'base_score': base_prediction,
            'mean_simulated': np.mean(simulated_scores),
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'all_simulations': simulated_scores
        }
