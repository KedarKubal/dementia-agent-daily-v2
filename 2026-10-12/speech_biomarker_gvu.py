#!/usr/bin/env python3
"""
Minimal Generator-Verifier-Updater (GVU) prototype for speech-biomarker dementia risk flag.
Based on insights from Cay et al. 2024 (speech pause/similarity features).

Sample input: simulated speech features from a reading task.
"""

from typing import Dict, Any, List
import json

# Simulated sample features (from paper-like: pause time, speech-to-pause ratio, etc.)
SAMPLE_FEATURES = {
    "total_pause_time": 12.5,  # seconds, high = concern
    "speech_to_pause_ratio": 1.8,  # low = concern
    "dtw_similarity": 0.65,  # low similarity to reference = concern
    "intelligibility_dtw": 0.70,
    "moCA_proxy": None  # unknown
}

SUCCESS_CRITERION = "Risk score must be high (>0.7) if total_pause_time > 10s AND speech_to_pause_ratio < 2.0; otherwise moderate or low. Must cite at least one feature."

def generator(features: Dict[str, Any], critique: str = "") -> Dict[str, Any]:
    """Produces candidate risk assessment."""
    pause = features["total_pause_time"]
    ratio = features["speech_to_pause_ratio"]
    sim = features["dtw_similarity"]
    
    # Simple heuristic inspired by paper
    if pause > 10 and ratio < 2.0:
        risk = 0.85
        flag = "HIGH"
        reason = f"Elevated pause time ({pause}s) and low speech-to-pause ratio ({ratio}) indicate potential cognitive slowing."
    elif pause > 8 or sim < 0.7:
        risk = 0.55
        flag = "MODERATE"
        reason = f"Borderline features: pause={pause}, similarity={sim}."
    else:
        risk = 0.25
        flag = "LOW"
        reason = "Features within typical range for intact cognition."
    
    if critique:
        reason += f" Revised based on: {critique}"
        if "increase" in critique.lower() or "high" in critique.lower():
            risk = min(1.0, risk + 0.15)
            flag = "HIGH" if risk > 0.7 else flag
    
    return {
        "risk_score": round(risk, 2),
        "flag": flag,
        "reason": reason,
        "features_used": ["total_pause_time", "speech_to_pause_ratio", "dtw_similarity"]
    }

def verifier(output: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """Checks against explicit success criterion."""
    pause = features["total_pause_time"]
    ratio = features["speech_to_pause_ratio"]
    expected_high = pause > 10 and ratio < 2.0
    
    passes = True
    reasons = []
    
    if expected_high and output["risk_score"] <= 0.7:
        passes = False
        reasons.append("Expected HIGH risk (>0.7) given pause >10 and ratio <2, but score is lower.")
    if not expected_high and output["risk_score"] > 0.7:
        passes = False
        reasons.append("Score too high for features that do not meet high-risk threshold.")
    if not any(f in output["reason"].lower() for f in ["pause", "ratio", "similarity", "dtw"]):
        passes = False
        reasons.append("Must cite at least one feature in the reason.")
    
    critique = "PASS" if passes else "FAIL: " + "; ".join(reasons)
    return {"pass": passes, "critique": critique, "expected_high": expected_high}

def updater_loop(features: Dict[str, Any], max_passes: int = 3) -> List[Dict[str, Any]]:
    """Runs GVU 2-3 times, logging changes."""
    logs = []
    critique = ""
    for i in range(max_passes):
        output = generator(features, critique)
        ver = verifier(output, features)
        entry = {
            "pass": i + 1,
            "output": output,
            "verifier": ver
        }
        logs.append(entry)
        if ver["pass"]:
            break
        critique = ver["critique"]
    return logs

if __name__ == "__main__":
    print("=== Speech Biomarker GVU Smoke Test ===")
    print(f"Sample features: {json.dumps(SAMPLE_FEATURES, indent=2)}")
    print(f"Success criterion: {SUCCESS_CRITERION}\n")
    
    logs = updater_loop(SAMPLE_FEATURES)
    for entry in logs:
        print(f"--- Pass {entry['pass']} ---")
        print(f"Output: {json.dumps(entry['output'], indent=2)}")
        print(f"Verifier: {entry['verifier']['critique']}")
        print()
    
    final = logs[-1]["output"]
    print("Final output:", json.dumps(final, indent=2))
