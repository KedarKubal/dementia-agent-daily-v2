#!/usr/bin/env python3
"""
Minimal Generator-Verifier-Updater (GVU) loop for self-improving speech biomarker refinement
for early MCI/dementia detection. Based on insight from dual dropout ranking / speech feature selection papers.
"""

import json
from typing import Dict, List, Tuple

# Explicit success criterion for Verifier: risk_score should be high (>0.7) if pause_ratio > 0.25 and lexical_diversity < 0.6
# else low (<0.4). Must match labeled heuristic. Falsifiable.

def generator(features: Dict, weights: Dict, pass_num: int) -> Dict:
    """Produce candidate risk score and flag from speech features."""
    pause_ratio = features.get("pause_ratio", 0.1)
    lexical_div = features.get("lexical_diversity", 0.7)
    speech_rate = features.get("speech_rate", 150)
    
    score = (
        weights.get("pause", 0.4) * min(pause_ratio * 2, 1.0) +
        weights.get("lex", 0.3) * max(0, 1 - lexical_div) +
        weights.get("rate", 0.3) * max(0, (180 - speech_rate) / 100)
    )
    score = max(0.0, min(1.0, score))
    flag = "elevated" if score > 0.6 else "low"
    return {
        "pass": pass_num,
        "risk_score": round(score, 3),
        "flag": flag,
        "weights_used": weights.copy(),
        "features": features
    }

def verifier(output: Dict, features: Dict) -> Tuple[bool, str]:
    """Check against explicit criterion."""
    score = output["risk_score"]
    pause = features["pause_ratio"]
    lex = features["lexical_diversity"]
    high_risk_expected = pause > 0.25 and lex < 0.6
    if high_risk_expected:
        ok = score > 0.7
        reason = f"High-risk features (pause={pause:.2f}, lex={lex:.2f}) but score={score:.3f} {'>=0.7' if ok else '<0.7'}"
    else:
        ok = score < 0.4
        reason = f"Low-risk features but score={score:.3f} {'<0.4' if ok else '>=0.4'}"
    return ok, reason

def updater(weights: Dict, critique: str, features: Dict) -> Dict:
    """Adjust weights based on critique."""
    new_w = weights.copy()
    if "score=" in critique and "<0.7" in critique:
        # Boost pause and lex weights
        new_w["pause"] = min(0.6, new_w.get("pause", 0.4) + 0.1)
        new_w["lex"] = min(0.5, new_w.get("lex", 0.3) + 0.1)
        new_w["rate"] = max(0.1, new_w.get("rate", 0.3) - 0.1)
    elif ">=0.4" in critique:
        new_w["pause"] = max(0.2, new_w.get("pause", 0.4) - 0.1)
    return new_w

def run_gvu(features: Dict, max_passes: int = 3) -> List[Dict]:
    weights = {"pause": 0.4, "lex": 0.3, "rate": 0.3}
    history = []
    for p in range(1, max_passes + 1):
        out = generator(features, weights, p)
        ok, reason = verifier(out, features)
        out["verifier_pass"] = ok
        out["critique"] = reason
        history.append(out)
        if ok:
            break
        weights = updater(weights, reason, features)
    return history

if __name__ == "__main__":
    # Smoke-test sample: high-risk speech features (elevated pauses, low lexical diversity)
    sample = {
        "pause_ratio": 0.32,
        "lexical_diversity": 0.48,
        "speech_rate": 120
    }
    print("=== Smoke-test: high-risk sample ===")
    results = run_gvu(sample)
    for r in results:
        print(json.dumps(r, indent=2))
    print("\nBefore/after:")
    print(f"Pass1 score: {results[0]['risk_score']} flag={results[0]['flag']} pass={results[0]['verifier_pass']}")
    if len(results) > 1:
        print(f"Final score: {results[-1]['risk_score']} flag={results[-1]['flag']} pass={results[-1]['verifier_pass']}")
