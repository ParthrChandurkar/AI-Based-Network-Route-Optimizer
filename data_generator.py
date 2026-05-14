"""
data_generator.py — Synthetic dataset generator for link failure prediction.
Failure probability is driven by: low bandwidth, high latency,
high packet_loss, and high traffic_load.
"""
import numpy as np
import pandas as pd
import os

FEATURES = ["bandwidth", "latency", "packet_loss", "traffic_load"]

def generate_network_dataset(n_samples: int = 800, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    bandwidth    = rng.uniform(10,  1000, n_samples)
    latency      = rng.uniform(1,   300,  n_samples)
    packet_loss  = rng.uniform(0,   20,   n_samples)
    traffic_load = rng.uniform(0,   100,  n_samples)
    stress = (
        (1 - bandwidth / 1000) * 0.30 +
        (latency / 300)        * 0.25 +
        (packet_loss / 20)     * 0.30 +
        (traffic_load / 100)   * 0.15
    )
    noise   = rng.normal(0, 0.08, n_samples)
    failure = (np.clip(stress + noise, 0, 1) > 0.55).astype(int)
    return pd.DataFrame({
        "bandwidth":    np.round(bandwidth,    2),
        "latency":      np.round(latency,      2),
        "packet_loss":  np.round(packet_loss,  2),
        "traffic_load": np.round(traffic_load, 2),
        "failure":      failure,
    })

def save_dataset(path: str = "network_data.csv", n_samples: int = 800) -> pd.DataFrame:
    df = generate_network_dataset(n_samples=n_samples)
    df.to_csv(path, index=False)
    return df

if __name__ == "__main__":
    df = save_dataset("network_data.csv")
    print(f"Saved {len(df)} rows. Failure rate: {df.failure.mean():.2%}")
