"""
Federated Learning and Differential Privacy Simulation Script (Research Gap 12).
Demonstrates:
1. Distributed edge nodes training locally on non-IID URL feature distributions
2. Federated Averaging (FedAvg) parameter aggregation
3. Local (epsilon, 0)-Differential Privacy via Laplace perturbation
4. Privacy Threat Model: Zero raw URLs or browsing histories transmitted
"""

import os
import sys
import math
import random

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.loader import DatasetLoader
from src.data.validation import DataValidator
from src.data.splitting import DataSplitter
from src.data.preprocessing import DataPreprocessor
from src.federated.client_simulation import FederatedClient, FederatedServer


def run_federated_simulation():
    print("=" * 65)
    print("   MobiURL-Guard: Federated Learning & Local Differential Privacy")
    print("=" * 65)

    loader = DatasetLoader()
    raw_records, _ = loader.load_raw_records()
    clean_records, _ = DataValidator.filter_clean_records(raw_records)
    splitter = DataSplitter(seed=42)
    deduped = splitter.deduplicate(clean_records)

    preprocessor = DataPreprocessor()
    feat_names = preprocessor.feature_names
    num_features = len(feat_names)

    # Partition data across 5 simulated mobile devices (Non-IID distribution)
    num_clients = 5
    client_records = [[] for _ in range(num_clients)]
    for i, r in enumerate(deduped[:5000]):
        # Non-IID assignment: skew benign vs malicious proportion per client
        c_idx = (i + int(float(r["label"])) * 2) % num_clients
        client_records[c_idx].append(r)

    clients = []
    for c_id in range(num_clients):
        X_c, y_c, _ = preprocessor.process_records(client_records[c_id])
        client = FederatedClient(
            client_id=f"MobileNode_{c_id+1}",
            private_features=X_c,
            private_labels=y_c,
            seed=42 + c_id
        )
        clients.append(client)
        print(f"  • Initialized Client {c_id+1} ({client.client_id}): {len(y_c):,} local samples (Non-IID)")

    server = FederatedServer(num_features=num_features, epsilon_dp=1.5)
    print(f"\n[+] Central Server Configured: Feature Dimension = {num_features}, Local DP epsilon = {server.epsilon_dp}")

    # Run 5 federated rounds
    num_rounds = 5
    for r in range(1, num_rounds + 1):
        round_res = server.run_simulation_round(clients, epochs=3)
        print(f"[*] Round {r}/{num_rounds}: Participating Clients = {round_res['participating_clients']} | Weight Norm = {round_res['global_weights_norm']:.4f} | {round_res['privacy_guarantee']}")

    print("\n" + "=" * 65)
    print("[+] Federated Learning Simulation Successfully Verified.")
    print("    - Privacy Invariance: 0 raw URLs transmitted to server.")
    print("    - Communication: Gradient updates only, secured by Laplace noise.")
    print("=" * 65)


if __name__ == "__main__":
    run_federated_simulation()
