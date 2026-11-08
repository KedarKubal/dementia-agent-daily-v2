#!/usr/bin/env python3
"""
Minimal GVU self-improving multi-agent prototype for speech-biomarker early CI risk flag.
Based on insight: speech digital biomarkers (e.g. percentage of silence duration / PSD) fused with simple heuristics can flag elevated risk; verifier enforces multi-feature prioritization.
"""

import json
from typing import Dict, Any

# Sample input: speech features from a high-pause / high-risk sample
SAMPLE = {
    "pause_ratio": 0.42,      # high silence / PSD proxy
    "lexical_diversity": 0.38, # low
    "articulation_rate": 3.1,  # slow
    "age": 72,
    "education_years": 12
}

def generator(features: Dict[str, float], weights: Dict[str, float], bias: float = 0.0) -> Dict[str, Any]:
    """Generator: produces candidate risk score and top features."""
    score = bias
    for k, w in weights.items():
        if k in features:
            score += w * features[k]
    # Normalize roughly to 0-1
    score = max(0.0, min(1.0, score))
    top_features = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:2]
    risk_level = "elevated" if score >= 0.55 else "typical"
    return {
        "risk_score": round(score, 3),
        "risk_level": risk_level,
        "top_features": [f[0] for f in top_features],
        "weights_used": weights.copy()
    }

def verifier(output: Dict[str, Any], features: Dict[str, float]) -> Dict[str, Any]:
    """Verifier: explicit success criterion — for high-pause samples, pause_ratio must be top feature and score elevated if pause_ratio > 0.35."""
    pass_ = True
    reason = "ok"
    if features.get("pause_ratio", 0) > 0.35:
        if "pause_ratio" not in output.get("top_features", []):
            pass_ = False
            reason = "high-pause sample but pause_ratio not prioritized in top_features"
        elif output.get("risk_level") != "elevated":
            pass_ = False
            reason = "high-pause sample but risk_level not elevated"
    return {"pass": pass_, "reason": reason, "critique": reason if not pass_ else "criteria met"}

def updater(weights: Dict[str, float], critique: str) -> Dict[str, float]:
    """Updater: feeds critique back — boost pause weight if not prioritized."""
    new_weights = weights.copy()
    if "pause_ratio" in critique or "not prioritized" in critique:
        new_weights["pause_ratio"] = min(0.8, new_weights.get("pause_ratio", 0.3) + 0.25)
        # re-normalize roughly
        total = sum(new_weights.values())
        if total > 0:
            for k in new_weights:
                new_weights[k] /= total
    return new_weights

def run_gvu(sample: Dict[str, float], max_passes: int = 3) -> list:
    """Run Generator-Verifier-Updater loop 2-3 times, log each pass."""
    weights = {"pause_ratio": 0.25, "lexical_diversity": 0.5, "articulation_rate": 0.3}
    logs = []
    for i in range(1, max_passes + 1):
        gen_out = generator(sample, weights)
        ver = verifier(gen_out, sample)
        logs.append({
            "pass": i,
            "generator_output": gen_out,
            "verifier": ver,
            "weights": weights.copy()
        })
        if ver["pass"]:
            break
        weights = updater(weights, ver["critique"])
    return logs

if __name__ == "__main__":
    results = run_gvu(SAMPLE)
    print(json.dumps(results, indent=2))
    # Smoke-test before/after
    print("\n=== Smoke-test summary ===")
    print(f"Pass 1 score: {results[0]['generator_output']['risk_score']} level: {results[0]['generator_output']['risk_level']} top: {results[0]['generator_output']['top_features']}")
    if len(results) > 1:
        print(f"Pass {len(results)} score: {results[-1]['generator_output']['risk_score']} level: {results[-1]['generator_output']['risk_level']} top: {results[-1]['generator_output']['top_features']}")
