#!/usr/bin/env python3
"""
Minimal GVU prototype for speech-based dementia risk scoring.
Self-improving loop: Generator → Verifier → Updater (2-3 passes).
Based on speech digital biomarkers insight (timing/prosody features from papers like Cay et al. and foundation model work).
"""

from typing import Dict, Any, List
import json

# Sample speech features (from reading task or spontaneous speech)
SAMPLE_FEATURES = {
    "pause_ratio": 0.35,          # high → risk
    "speech_rate_wpm": 95,        # low → risk
    "articulation_rate": 3.2,
    "filled_pauses_per_min": 8.5, # high → risk
    "lexical_diversity": 0.42,    # low → risk
    "age": 72,
    "education_years": 14
}

def generator(features: Dict[str, Any], critique: str = "") -> Dict[str, Any]:
    """Produce candidate risk score and explanation."""
    # Simple heuristic baseline (in real system: LLM or model inference)
    risk = 0.0
    reasons = []
    
    if features["pause_ratio"] > 0.25:
        risk += 0.3
        reasons.append("Elevated pause ratio suggests reduced fluency")
    if features["speech_rate_wpm"] < 110:
        risk += 0.25
        reasons.append("Slowed speech rate")
    if features["filled_pauses_per_min"] > 5:
        risk += 0.2
        reasons.append("Increased filled pauses")
    if features["lexical_diversity"] < 0.5:
        risk += 0.15
        reasons.append("Reduced lexical diversity")
    
    risk = min(1.0, max(0.0, risk))
    
    explanation = "; ".join(reasons) if reasons else "Features within typical range"
    
    if critique:
        # Apply simple revision based on critique
        if "overestimate" in critique.lower() or "too high" in critique.lower():
            risk *= 0.85
            explanation += " [revised down after critique]"
        elif "underestimate" in critique.lower() or "too low" in critique.lower():
            risk = min(1.0, risk * 1.15)
            explanation += " [revised up after critique]"
        else:
            explanation += f" [noted: {critique[:50]}]"
    
    return {
        "risk_score": round(risk, 3),
        "confidence": 0.7,
        "explanation": explanation,
        "features_used": list(features.keys())
    }

def verifier(output: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """Check against explicit success criteria."""
    score = output["risk_score"]
    reasons = []
    passed = True
    
    # Criterion 1: score in [0, 1]
    if not (0 <= score <= 1):
        passed = False
        reasons.append(f"Score {score} outside [0,1]")
    
    # Criterion 2: high pause_ratio (>0.25) should yield score >= 0.25
    if features["pause_ratio"] > 0.25 and score < 0.25:
        passed = False
        reasons.append("High pause_ratio but risk score too low (<0.25)")
    
    # Criterion 3: explanation must reference at least one feature
    if not any(f in output["explanation"].lower() for f in ["pause", "speech", "lexical", "rate"]):
        passed = False
        reasons.append("Explanation does not reference key features")
    
    critique = "; ".join(reasons) if reasons else "All criteria met"
    return {"pass": passed, "critique": critique, "score": score}

def run_gvu(features: Dict[str, Any], max_passes: int = 3) -> List[Dict[str, Any]]:
    """Run Generator-Verifier-Updater loop, logging each pass."""
    logs = []
    critique = ""
    
    for i in range(1, max_passes + 1):
        candidate = generator(features, critique)
        verification = verifier(candidate, features)
        
        log_entry = {
            "pass": i,
            "candidate": candidate,
            "verification": verification
        }
        logs.append(log_entry)
        
        if verification["pass"]:
            log_entry["status"] = "PASSED — stopping early"
            break
        else:
            critique = verification["critique"]
            log_entry["status"] = "FAILED — feeding critique to next Generator"
    
    return logs

if __name__ == "__main__":
    print("=== Speech Biomarker Risk Scorer — GVU Prototype ===\n")
    print(f"Sample features: {json.dumps(SAMPLE_FEATURES, indent=2)}\n")
    
    results = run_gvu(SAMPLE_FEATURES)
    
    for entry in results:
        print(f"--- Pass {entry['pass']} ---")
        print(f"Risk Score: {entry['candidate']['risk_score']}")
        print(f"Explanation: {entry['candidate']['explanation']}")
        print(f"Verifier: {'PASS' if entry['verification']['pass'] else 'FAIL'} — {entry['verification']['critique']}")
        print(f"Status: {entry['status']}\n")
    
    print("=== Final Output ===")
    final = results[-1]["candidate"]
    print(json.dumps(final, indent=2))
