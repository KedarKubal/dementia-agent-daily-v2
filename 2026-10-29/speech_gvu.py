#!/usr/bin/env python3
"""
Minimal GVU self-improving agent for speech-biomarker early dementia risk flag.
Based on insight: selective pause / lexical features outperform broad feature sets (e.g. pauses as strongest biomarker).
Generator produces candidate risk score + features.
Verifier checks against explicit criterion: high-pause sample must score >= 0.55, flag elevated, and pause prioritized.
Updater feeds critique and revises weights.
"""

import json
from typing import Dict, Any

# Sample input: speech features from a high-risk MCI-like recording
SAMPLE = {
    "pause_ratio": 0.28,          # elevated
    "lexical_diversity": 0.41,    # reduced
    "disfluency_rate": 0.12,
    "word_count": 85,
    "avg_sentence_length": 6.2
}

def generator(features: Dict[str, float], weights: Dict[str, float], threshold: float = 0.50) -> Dict[str, Any]:
    """Produce candidate risk score and flag."""
    score = (
        weights.get("pause", 0.35) * features["pause_ratio"] * 2.0 +
        weights.get("lex", 0.25) * (1 - features["lexical_diversity"]) +
        weights.get("disfluency", 0.20) * features["disfluency_rate"] * 3.0 +
        weights.get("verbosity", 0.20) * (1 if features["word_count"] < 100 else 0.3)
    )
    score = min(max(score, 0.0), 1.0)
    flag = "elevated" if score >= threshold else "typical"
    return {
        "score": round(score, 3),
        "flag": flag,
        "weights_used": weights,
        "threshold": threshold,
        "top_features": sorted(weights.items(), key=lambda x: -x[1])[:2]
    }

def verifier(output: Dict[str, Any], features: Dict[str, float]) -> Dict[str, Any]:
    """Check against explicit success criterion."""
    # Criterion: for this high-pause / low-diversity sample, must be elevated and score >= 0.55
    # and pause among top features
    success = output["flag"] == "elevated" and output["score"] >= 0.55
    reasons = []
    if output["score"] < 0.55:
        reasons.append(f"score {output['score']} below 0.55 required for high-pause sample")
    if output["flag"] != "elevated":
        reasons.append("flag not elevated")
    # Extra: pause should be among top features
    top_names = [n for n, _ in output["top_features"]]
    if "pause" not in top_names:
        reasons.append("pause not prioritized in top features")
        success = False
    return {
        "pass": success,
        "reason": "; ".join(reasons) if reasons else "meets criterion",
        "critique": "Increase pause weight and/or lower threshold if under-detecting high-pause risk." if not success else "ok"
    }

def updater(weights: Dict[str, float], critique: str) -> Dict[str, float]:
    """Revise weights based on critique."""
    new_w = weights.copy()
    if "pause" in critique.lower() or "under-detecting" in critique.lower():
        new_w["pause"] = min(new_w.get("pause", 0.35) + 0.15, 0.60)
        new_w["lex"] = max(new_w.get("lex", 0.25) - 0.05, 0.10)
    # renormalize roughly
    total = sum(new_w.values())
    for k in new_w:
        new_w[k] = round(new_w[k] / total, 3)
    return new_w

def run_gvu(max_passes: int = 3) -> list:
    weights = {"pause": 0.15, "lex": 0.35, "disfluency": 0.25, "verbosity": 0.25}
    log = []
    for i in range(1, max_passes + 1):
        out = generator(SAMPLE, weights)
        ver = verifier(out, SAMPLE)
        entry = {
            "pass": i,
            "output": out,
            "verifier": ver,
            "weights": weights
        }
        log.append(entry)
        print(f"Pass {i}: score={out['score']} flag={out['flag']} | {ver['pass']} | {ver['reason']}")
        if ver["pass"]:
            break
        weights = updater(weights, ver["critique"])
    return log

if __name__ == "__main__":
    print("=== Speech Biomarker GVU Smoke Test ===")
    print(f"Sample features: {SAMPLE}\n")
    results = run_gvu()
    print("\n=== Final log ===")
    print(json.dumps(results[-1], indent=2))
