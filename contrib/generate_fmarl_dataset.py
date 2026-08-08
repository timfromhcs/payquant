#!/usr/bin/env python3
"""
Generates the PayQuant AI Training Dataset (payquant_dataset.json)
Contains federated telemetry and network optimization traces.
"""

import json
import random

def generate_dataset(num_samples=500):
    samples = []
    
    for i in range(num_samples):
        tps = random.randint(10, 5000)
        mempool_bytes = random.randint(100000, 50000000)
        avg_fee = round(random.uniform(1.0, 150.0), 2)
        active_peers = random.randint(32, 256)
        
        # Reward / Target actions
        opt_block_size = 4000000 if mempool_bytes > 10000000 else 2000000
        opt_min_fee = round(max(1.0, avg_fee * 0.9), 2)
        
        samples.append({
            "step": i,
            "state": {
                "tps": tps,
                "mempool_bytes": mempool_bytes,
                "avg_fee_rate_sat_vb": avg_fee,
                "active_peers": active_peers
            },
            "optimal_action": {
                "target_block_bytes": opt_block_size,
                "target_min_fee": opt_min_fee,
                "recommended_peers": min(256, active_peers + 16)
            },
            "reward_score": round(random.uniform(0.85, 0.99), 4)
        })
        
    dataset = {
        "metadata": {
            "project": "PayQuant FMARL Dataset",
            "version": "1.0.0",
            "samples": len(samples),
            "created_by": "PayQuant Autonomous AI Engine"
        },
        "data": samples
    }
    
    with open("payquant_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Generated payquant_dataset.json with {len(samples)} telemetry traces.")

if __name__ == '__main__':
    generate_dataset()
