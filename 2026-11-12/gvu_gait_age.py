#!/usr/bin/env python3
"""
Minimal GVU prototype: Age-adjusted gait risk flag for incident dementia
(inspired by age-dependent nonlinear gait-dementia association).
Generator proposes risk score + flag from POMA-like gait features + age.
Verifier checks explicit criterion: score must be elevated (>0.6) for high-risk sample
AND age-weight must be prioritized for younger-old (age <75).
Updater loops up to 3 passes, adjusting weights based on critique.
"""

import json
from typing import Dict, Any

# Sample: high-risk younger-old with poor gait
SAMPLE = {
    "id": "GAIT-AGE-042",
    "age": 68,
    "gait_score": 9.5,  # lower is worse (POMA-like)
    "balance_score": 14,
    "variability": 0.18,
    "expected_risk": "elevated"
}

def generator(features: Dict[str, Any], weights: Dict[str, float], bias: float) -> Dict[str, Any]:
    """Produce candidate risk score and flag."""
    # Invert gait_score (higher bad)
    gait_bad = max(0, (12 - features["gait_score"]) / 12)
    age_factor = max(0, (75 - features["age"]) / 10)  # stronger for younger
    var_bad = min(1.0, features["variability"] / 0.2)
    score = (
        weights["gait"] * gait_bad +
        weights["age"] * age_factor +
        weights["var"] * var_bad +
        bias
    )
    score = min(1.0, max(0.0, score))
    flag = "elevated" if score > 0.6 else "typical"
    top_feature = max(["gait", "age", "var"], key=lambda k: weights[k])
    return {
        "score": round(score, 3),
        "flag": flag,
        "top_feature": top_feature,
        "weights": weights.copy(),
        "bias": bias
    }

def verifier(output: Dict[str, Any], sample: Dict[str, Any]) -> Dict[str, Any]:
    """Explicit success criterion: for this high-risk younger sample,
    flag must be elevated AND top_feature must be age or gait."""
    passed = (
        output["flag"] == "elevated" and
        output["score"] > 0.6 and
        output["top_feature"] in ["age", "gait"]
    )
    reason = ""
    if not passed:
        if output["flag"] != "elevated" or output["score"] <= 0.6:
            reason = "score too low for high-risk sample"
        else:
            reason = "top_feature not age/gait (age-weight not prioritized)"
    return {"pass": passed, "reason": reason, "output": output}

def updater(weights: Dict[str, float], bias: float, critique: str) -> tuple:
    """Adjust based on critique."""
    if "score too low" in critique:
        weights["gait"] = min(0.6, weights["gait"] + 0.15)
        weights["age"] = min(0.5, weights["age"] + 0.1)
        bias = min(0.3, bias + 0.05)
    if "top_feature" in critique:
        weights["age"] = min(0.55, weights["age"] + 0.12)
        weights["var"] = max(0.1, weights["var"] - 0.05)
    # Normalize roughly
    total = sum(weights.values())
    for k in weights:
        weights[k] /= total * 0.9  # leave room for bias
    return weights, bias

def run_gvu(sample: Dict[str, Any], max_passes: int = 3) -> list:
    weights = {"gait": 0.25, "age": 0.25, "var": 0.5}
    bias = 0.1
    logs = []
    for p in range(1, max_passes + 1):
        out = generator(sample, weights, bias)
        ver = verifier(out, sample)
        logs.append({
            "pass": p,
            "output": out,
            "verifier": {"pass": ver["pass"], "reason": ver["reason"]}
        })
        if ver["pass"]:
            break
        weights, bias = updater(weights, bias, ver["reason"])
    return logs

if __name__ == "__main__":
    logs = run_gvu(SAMPLE)
    print(json.dumps(logs, indent=2))
    # Smoke summary
    first = logs[0]["output"]
    last = logs[-1]["output"]
    print(f"\nSMOKE: pass1 score={first['score']} flag={first['flag']} -> pass{len(logs)} score={last['score']} flag={last['flag']} top={last['top_feature']}")
