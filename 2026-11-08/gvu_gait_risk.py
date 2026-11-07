#!/usr/bin/env python3
"""
Minimal GVU prototype for continuous gait monitoring dementia risk flag.
Based on wearable sensor gait analysis papers for progression/fall risk.
Generator: draft risk score from gait features.
Verifier: checks against explicit criteria (variability > threshold implies elevated).
Updater: revises weights/score based on critique, loops 2-3 times.
"""

import json
from typing import Dict, Any

# Sample input: gait features from wearable (e.g., from Varma et al. continuous monitoring)
SAMPLE_GAIT = {
    "step_velocity_mean": 0.85,  # m/s, lower = worse
    "step_velocity_variability": 0.22,  # high variability = risk
    "cadence": 95,  # steps/min
    "cadence_variability": 0.15,
    "patient_id": "GAIT-MCI-042"
}

def generator(features: Dict[str, float], weights: Dict[str, float] = None) -> Dict[str, Any]:
    """Produce candidate risk score and flag."""
    if weights is None:
        weights = {"velocity": 0.4, "variability": 0.3, "cadence": 0.3}
    # Simple weighted score: higher variability and lower velocity increase risk
    risk = 0.3 + (
        (1 - features["step_velocity_mean"]) * weights["velocity"] +
        features["step_velocity_variability"] * weights["variability"] +
        (1 - features["cadence"] / 120) * weights["cadence"]
    )
    flag = "elevated" if risk > 0.4 else "typical"
    return {
        "risk_score": round(risk, 3),
        "flag": flag,
        "weights_used": weights,
        "features": features
    }

def verifier(output: Dict[str, Any]) -> Dict[str, Any]:
    """Explicit success criterion: high variability (>0.18) must yield elevated flag and score >0.45.
    Also, variability must be the top weighted feature if elevated."""
    features = output["features"]
    score = output["risk_score"]
    flag = output["flag"]
    weights = output["weights_used"]
    pass_ = True
    reason = "OK"
    if features["step_velocity_variability"] > 0.18:
        if flag != "elevated" or score <= 0.45:
            pass_ = False
            reason = "High variability but flag/score not elevated enough"
        if max(weights, key=weights.get) != "variability":
            pass_ = False
            reason += "; variability not prioritized in weights"
    else:
        if flag == "elevated":
            pass_ = False
            reason = "Low variability but elevated flag"
    return {"pass": pass_, "reason": reason, "critique": reason if not pass_ else "Meets criterion"}

def updater(output: Dict[str, Any], critique: Dict[str, Any]) -> Dict[str, float]:
    """Revise weights based on critique to self-improve."""
    weights = output["weights_used"].copy()
    if not critique["pass"]:
        if "variability" in critique["reason"]:
            weights["variability"] = min(0.7, weights["variability"] + 0.15)
            weights["velocity"] = max(0.1, weights["velocity"] - 0.05)
            weights["cadence"] = max(0.1, weights["cadence"] - 0.05)
        # Normalize roughly
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}
    return weights

def run_gvu(features: Dict[str, float], max_passes: int = 3) -> list:
    """Run GVU loop, log each pass."""
    logs = []
    weights = None
    for i in range(1, max_passes + 1):
        out = generator(features, weights)
        ver = verifier(out)
        logs.append({"pass": i, "output": out, "verifier": ver})
        if ver["pass"]:
            break
        weights = updater(out, ver)
    return logs

if __name__ == "__main__":
    logs = run_gvu(SAMPLE_GAIT)
    print(json.dumps(logs, indent=2))
    # Smoke test before/after
    print("\n--- Smoke test summary ---")
    print(f"Pass 1: score={logs[0]['output']['risk_score']} flag={logs[0]['output']['flag']} pass={logs[0]['verifier']['pass']}")
    if len(logs) > 1:
        print(f"Pass {len(logs)}: score={logs[-1]['output']['risk_score']} flag={logs[-1]['output']['flag']} pass={logs[-1]['verifier']['pass']}")
