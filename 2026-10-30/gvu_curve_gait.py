#!/usr/bin/env python3
"""
Minimal GVU prototype for curve-walking gait digital biomarker
(Monitoring/Care angle: Seifallahi et al. 2024 insight on curve > straight sensitivity).
Generator proposes risk flag from gait features.
Verifier checks against explicit criterion.
Updater loops 3 times.
"""

import json
from typing import Dict, Any

# Sample input: gait features from Kinect-like curve vs straight
SAMPLE = {
    "id": "MCI-CURVE-045",
    "straight_velocity": 1.05,  # m/s
    "curve_velocity": 0.72,     # m/s
    "straight_variability": 0.08,
    "curve_variability": 0.22,
    "cadence_curve": 95,
}

def generator(features: Dict[str, Any], critique: str = "") -> Dict[str, Any]:
    """Produce candidate risk assessment. Incorporates critique if given."""
    vel_drop = (features["straight_velocity"] - features["curve_velocity"]) / features["straight_velocity"]
    var_increase = features["curve_variability"] - features["straight_variability"]
    
    base_score = 0.3 * vel_drop + 0.4 * var_increase * 2 + 0.1  # rough
    if "boost curve weight" in critique.lower() or "under-detect" in critique.lower():
        base_score = min(1.0, base_score + 0.25)
    
    flag = "elevated" if base_score > 0.45 else "typical"
    reason = f"vel_drop={vel_drop:.2f}, var_inc={var_increase:.2f}"
    if critique:
        reason += f" | after critique: {critique[:50]}"
    
    return {
        "risk_flag": flag,
        "score": round(base_score, 3),
        "reason": reason,
        "top_feature": "curve_variability" if var_increase > 0.1 else "velocity_drop"
    }

def verifier(output: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """Explicit success criterion: for MCI-like, must flag elevated if vel_drop >0.25 AND var_inc >0.1."""
    vel_drop = (features["straight_velocity"] - features["curve_velocity"]) / features["straight_velocity"]
    var_inc = features["curve_variability"] - features["straight_variability"]
    expected_elevated = vel_drop > 0.25 and var_inc > 0.1
    
    passed = (output["risk_flag"] == "elevated") == expected_elevated
    # Additional: top feature should be curve-related for high var
    if expected_elevated and output["top_feature"] != "curve_variability":
        passed = False
        reason = "Top feature not prioritizing curve variability as expected for this sample."
    else:
        reason = "Matches expected elevated flag based on >25% velocity drop and >0.1 variability increase on curve." if passed else "Flag mismatch with criterion."
    
    return {"pass": passed, "reason": reason, "expected_elevated": expected_elevated}

def updater(features: Dict[str, Any], max_passes: int = 3) -> list:
    """Loop Generator-Verifier-Updater, log each pass."""
    logs = []
    critique = ""
    for i in range(1, max_passes + 1):
        out = generator(features, critique)
        ver = verifier(out, features)
        log_entry = {
            "pass": i,
            "output": out,
            "verifier": ver,
            "critique_used": critique
        }
        logs.append(log_entry)
        if ver["pass"]:
            break
        # Updater: generate critique for next
        critique = f"under-detect; boost curve weight. Previous: {ver['reason']}"
    return logs

if __name__ == "__main__":
    results = updater(SAMPLE)
    print(json.dumps(results, indent=2))
    # Smoke test summary
    first = results[0]
    last = results[-1]
    print("\n=== Smoke Test ===")
    print(f"Before (pass 1): flag={first['output']['risk_flag']} score={first['output']['score']} pass={first['verifier']['pass']}")
    print(f"After (pass {last['pass']}): flag={last['output']['risk_flag']} score={last['output']['score']} pass={last['verifier']['pass']}")
