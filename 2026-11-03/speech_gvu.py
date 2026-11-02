#!/usr/bin/env python3
"""
Minimal GVU prototype for speech-based dementia risk scoring.
Inspired by voiceprint / speech biomarker papers (e.g., high AUC from pause and linguistic features on story recall).
Generator drafts a risk score + flag from features.
Verifier checks against explicit criterion: if pause_ratio > 0.35 and score < 0.6 or flag != 'elevated', fail with critique.
Updater feeds critique back and regenerates.
Runs 3 passes on a sample.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import json

@dataclass
class SpeechFeatures:
    pause_ratio: float
    lexical_diversity: float  # lower = worse
    mean_pause_duration: float
    transcript_length: int

def generator(features: SpeechFeatures, critique: str = "", pass_num: int = 1) -> Dict[str, Any]:
    """Produce candidate risk assessment. Adjusts based on critique."""
    base_score = (features.pause_ratio * 0.7) + ((1 - features.lexical_diversity) * 0.3)
    if "boost pause" in critique.lower() or pass_num > 1:
        base_score = min(1.0, base_score + 0.15 * pass_num)
    if "elevate flag" in critique.lower():
        flag = "elevated"
    else:
        flag = "elevated" if base_score > 0.55 else "typical"
    
    return {
        "pass": pass_num,
        "risk_score": round(base_score, 3),
        "flag": flag,
        "top_feature": "pause_ratio" if features.pause_ratio > 0.3 else "lexical_diversity",
        "rationale": f"Pause ratio {features.pause_ratio:.2f} drives risk; lexical diversity {features.lexical_diversity:.2f}."
    }

def verifier(output: Dict[str, Any], features: SpeechFeatures) -> Dict[str, Any]:
    """Explicit success criterion: for high-pause samples (pause_ratio > 0.35),
    must have score >= 0.6 and flag == 'elevated' and top_feature == 'pause_ratio'.
    """
    high_risk_sample = features.pause_ratio > 0.35
    passes = True
    reasons = []
    
    if high_risk_sample:
        if output["risk_score"] < 0.6:
            passes = False
            reasons.append(f"Score {output['risk_score']} too low for high pause_ratio {features.pause_ratio}")
        if output["flag"] != "elevated":
            passes = False
            reasons.append("Flag must be 'elevated' for high-pause sample")
        if output["top_feature"] != "pause_ratio":
            passes = False
            reasons.append("Top feature must prioritize pause_ratio")
    
    critique = "; ".join(reasons) if reasons else "OK"
    if not passes:
        critique += ". Boost pause weight and elevate flag."
    
    return {"pass": passes, "critique": critique, "reasons": reasons}

def updater(features: SpeechFeatures, max_passes: int = 3) -> List[Dict[str, Any]]:
    """Run GVU loop, logging each pass."""
    logs = []
    critique = ""
    for p in range(1, max_passes + 1):
        candidate = generator(features, critique, p)
        ver = verifier(candidate, features)
        log_entry = {**candidate, "verifier": ver}
        logs.append(log_entry)
        if ver["pass"]:
            break
        critique = ver["critique"]
    return logs

def main():
    # Sample: high pause ratio (typical early AD pattern from papers)
    sample = SpeechFeatures(
        pause_ratio=0.42,
        lexical_diversity=0.55,
        mean_pause_duration=1.8,
        transcript_length=120
    )
    print("=== Smoke Test: High-Pause Speech Sample ===")
    results = updater(sample)
    for r in results:
        print(json.dumps(r, indent=2))
    print("\nFinal output after self-improvement:")
    print(json.dumps(results[-1], indent=2))

if __name__ == "__main__":
    main()
