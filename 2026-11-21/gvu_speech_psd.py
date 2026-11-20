#!/usr/bin/env python3
"""
Minimal GVU prototype: Speech PSD (percentage of silence duration) digital biomarker risk flag.
Inspired by speech + fluid biomarker fusion papers for early CI detection (e.g. 2025 Alzheimer's Research & Therapy).
Generator produces candidate risk score/flag from speech features.
Verifier checks against explicit criterion (elevated risk if PSD high AND pause/PSD prioritized).
Updater loops critique feedback 2-3 times.
"""

import json
from typing import Dict, Any

# Sample input: high PSD / pause-heavy speech sample
SAMPLE = {
    "psd": 0.72,          # percentage silence duration
    "pause_ratio": 0.65,
    "mean_pause_duration": 1.8,
    "lexical_diversity": 0.42,
    "speech_rate": 1.1,
    "optional_ptau217": None  # missing
}

def generator(features: Dict[str, Any], weights: Dict[str, float] = None, bias: float = 0.0) -> Dict[str, Any]:
    """Produce candidate risk score and flag. Default weights under-weight acoustic features to demo improvement."""
    if weights is None:
        weights = {"psd": 0.25, "pause_ratio": 0.2, "lexical": 0.35, "rate": 0.2}
    score = (
        weights["psd"] * features["psd"]
        + weights["pause_ratio"] * features["pause_ratio"]
        + weights["lexical"] * (1.0 - features["lexical_diversity"])
        + weights["rate"] * (1.0 / max(features["speech_rate"], 0.5)) * 0.5
        + bias
    )
    score = min(max(score, 0.0), 1.0)
    flag = "elevated" if score >= 0.55 else "typical"
    top_feature = max(weights, key=weights.get)
    return {
        "risk_score": round(score, 3),
        "flag": flag,
        "top_feature": top_feature,
        "weights_used": weights.copy(),
        "bias": bias
    }

def verifier(output: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """Explicit success criterion: for high-PSD sample, flag must be elevated AND top_feature must be psd or pause_ratio."""
    high_psd = features["psd"] >= 0.6 and features["pause_ratio"] >= 0.5
    pass_flag = output["flag"] == "elevated"
    pass_top = output["top_feature"] in ("psd", "pause_ratio")
    success = (not high_psd) or (pass_flag and pass_top)
    reason = []
    if high_psd and not pass_flag:
        reason.append("High PSD/pause sample should flag elevated")
    if high_psd and not pass_top:
        reason.append("Top feature should prioritize PSD or pause_ratio")
    return {
        "pass": success,
        "reason": "; ".join(reason) if reason else "Criteria met",
        "critique": "Boost PSD/pause weights and bias if under-flagging high-pause samples" if not success else "OK"
    }

def updater(prev_output: Dict[str, Any], critique: Dict[str, Any]):
    """Simple weight update from critique."""
    weights = prev_output.get("weights_used", {"psd": 0.25, "pause_ratio": 0.2, "lexical": 0.35, "rate": 0.2}).copy()
    bias = prev_output.get("bias", 0.0)
    if not critique["pass"]:
        weights["psd"] = min(weights.get("psd", 0.25) + 0.18, 0.65)
        weights["pause_ratio"] = min(weights.get("pause_ratio", 0.2) + 0.12, 0.45)
        total = sum(weights.values())
        for k in weights:
            weights[k] /= total
        bias = min(bias + 0.06, 0.15)
    return weights, bias

def run_gvu(sample: Dict[str, Any], max_passes: int = 3) -> list:
    log = []
    weights = None
    bias = 0.0
    for i in range(1, max_passes + 1):
        out = generator(sample, weights, bias)
        ver = verifier(out, sample)
        entry = {
            "pass": i,
            "output": out,
            "verifier": ver
        }
        log.append(entry)
        print(f"Pass {i}: score={out['risk_score']} flag={out['flag']} top={out['top_feature']} | pass={ver['pass']} - {ver['reason']}")
        if ver["pass"]:
            break
        weights, bias = updater(out, ver)
    return log

if __name__ == "__main__":
    print("=== Smoke test: High-PSD speech sample ===")
    log = run_gvu(SAMPLE)
    with open("smoke_test.json", "w") as f:
        json.dump({"sample": SAMPLE, "log": log}, f, indent=2)
    print("\nLog written to smoke_test.json")
