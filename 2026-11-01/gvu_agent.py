"""Minimal GVU loop for SVF + imaging proxy risk flag."""

import json
from typing import Dict, Any

def generator(features: Dict[str, float], weights: Dict[str, float]) -> Dict[str, Any]:
    score = sum(features.get(k, 0) * weights.get(k, 0.2) for k in features)
    risk = "elevated" if score > 0.5 else "typical"
    return {"score": round(score, 3), "risk_flag": risk, "top_feature": max(features, key=features.get)}

def verifier(output: Dict[str, Any], features: Dict[str, float]) -> Dict[str, Any]:
    # Explicit criterion: if SVF_correct low (<15) and imaging_atrophy high (>0.3), must flag elevated and top_feature prioritizes SVF or atrophy
    low_svf = features.get("svf_correct", 20) < 15
    high_atrophy = features.get("imaging_atrophy_proxy", 0) > 0.3
    if low_svf and high_atrophy and (output["risk_flag"] != "elevated" or output["top_feature"] not in ["svf_correct", "imaging_atrophy_proxy"]):
        return {"pass": False, "critique": "Must elevate risk and prioritize SVF/atrophy when both signals present"}
    return {"pass": True, "critique": "Meets criterion"}

def updater(weights: Dict[str, float], critique: str) -> Dict[str, float]:
    if "elevate" in critique.lower() or "prioritize" in critique.lower():
        weights["svf_correct"] = weights.get("svf_correct", 0.2) + 0.15
        weights["imaging_atrophy_proxy"] = weights.get("imaging_atrophy_proxy", 0.2) + 0.15
    return weights

def run_gvu(sample: Dict[str, float], max_passes: int = 3):
    weights = {"svf_correct": 0.25, "imaging_atrophy_proxy": 0.25, "pause_ratio": 0.2, "lexical_div": 0.3}
    logs = []
    for i in range(max_passes):
        out = generator(sample, weights)
        ver = verifier(out, sample)
        logs.append({"pass": i+1, "output": out, "verification": ver})
        if ver["pass"]:
            break
        weights = updater(weights, ver["critique"])
    return logs

if __name__ == "__main__":
    sample = {"svf_correct": 12, "imaging_atrophy_proxy": 0.42, "pause_ratio": 0.35, "lexical_div": 0.6}
    results = run_gvu(sample)
    print(json.dumps(results, indent=2))
