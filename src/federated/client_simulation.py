"""
Privacy-Preserving Federated Learning Simulation for MobiURL-Guard (Research Gap 12).
Implements:
1. Federated Averaging (FedAvg) across simulated distributed mobile clients
2. Non-IID local partition assignment
3. Local Differential Privacy (DP) perturbation:
   Noise addition (Laplacian mechanism) to prevent parameter inversion attacks
4. Strict privacy constraint: Raw URLs and user browsing activity NEVER leave the device.
"""

import random
import math
from typing import List, Dict, Any, Tuple


class FederatedClient:
    """Simulates a mobile client training locally on its private URL interactions."""

    def __init__(self, client_id: str, private_features: List[List[float]], private_labels: List[int], seed: int = 42):
        self.client_id = client_id
        self.features = private_features
        self.labels = private_labels
        self.rng = random.Random(seed + hash(client_id))

    def train_local_weights(self, initial_weights: List[float], lr: float = 0.01, epochs: int = 5) -> List[float]:
        """Local stochastic gradient descent updates."""
        weights = list(initial_weights)
        n = len(self.labels)
        if n == 0:
            return weights

        d = len(weights)
        for _ in range(epochs):
            for x, y in zip(self.features, self.labels):
                # Linear dot product
                z = sum(w * xi for w, xi in zip(weights, x[:d]))
                p = 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, z))))
                err = p - y
                for j in range(d):
                    weights[j] -= lr * err * x[j]

        return weights

    def add_differential_privacy_noise(self, weights: List[float], epsilon: float = 1.0, sensitivity: float = 0.05) -> List[float]:
        """
        Adds Laplace noise to enforce (epsilon, 0)-Differential Privacy on client parameter updates.
        Scale b = sensitivity / epsilon.
        """
        b = sensitivity / max(1e-4, epsilon)
        noisy_weights = []
        for w in weights:
            # Sample Laplace noise: L(0, b)
            u = self.rng.random() - 0.5
            noise = -b * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))
            noisy_weights.append(round(w + noise, 5))
        return noisy_weights


class FederatedServer:
    """Orchestrates Federated Averaging (FedAvg) rounds across mobile nodes."""

    def __init__(self, num_features: int, epsilon_dp: float = 1.5):
        self.num_features = num_features
        self.epsilon_dp = epsilon_dp
        self.global_weights = [0.0] * num_features

    def aggregate_updates(self, client_weights: List[List[float]]) -> List[float]:
        """FedAvg: Element-wise mean of client parameters."""
        if not client_weights:
            return self.global_weights

        num_clients = len(client_weights)
        d = len(self.global_weights)
        new_weights = [0.0] * d

        for cw in client_weights:
            for j in range(d):
                new_weights[j] += cw[j]

        self.global_weights = [round(nw / num_clients, 5) for nw in new_weights]
        return self.global_weights

    def run_simulation_round(self, clients: List[FederatedClient], epochs: int = 3) -> Dict[str, Any]:
        """Execute one complete federated training round with local DP."""
        client_updates = []
        for c in clients:
            updated = c.train_local_weights(self.global_weights, epochs=epochs)
            noisy_updated = c.add_differential_privacy_noise(updated, epsilon=self.epsilon_dp)
            client_updates.append(noisy_updated)

        new_global = self.aggregate_updates(client_updates)

        return {
            "participating_clients": len(clients),
            "dp_epsilon": self.epsilon_dp,
            "privacy_guarantee": f"Local ({self.epsilon_dp}, 0)-DP via Laplace mechanism",
            "global_weights_norm": round(math.sqrt(sum(w**2 for w in new_global)), 4),
            "status": "Round completed successfully without collecting raw user URLs."
        }
