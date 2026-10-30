#!/usr/bin/env python3
"""
Self-Improving Speech Embedding Risk Flag for Early Dementia Detection
Minimal GVU prototype (Generator-Verifier-Updater) based on foundation speech model insights.
Simulates embedding-derived features; self-improves risk score over 2-3 passes.
"""

import json
from typing import Dict, List, Tuple

# Simulated sample: high-risk (elevated pause, low lexical diversity)
SAMPLE = {
    "pause_ratio": 0.42,
    "speech_rate": 1.1,  # words/sec
    "lexical_diversity": 0.35,
    "embedding_anomaly": 0.68,  # distance from healthy baseline
    "true_risk": "elevated"  # for verifier reference
}

class Generator:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "pause_ratio": 0.15,
            "speech_rate": 0.25,
            "lexical_diversity": 0.3,
            "embedding_anomaly": 0.3
        }
    
    def produce(self, sample: Dict) -> Dict:
        score = sum(self.weights[k] * sample.get(k, 0) for k in self.weights)
        top_feature = max(self.weights, key=self.weights.get)
        return {
            "risk_score": round(score, 3),
            "flag": "elevated" if score > 0.5 else "typical",
            "top_feature": top_feature,
            "weights": self.weights.copy()
        }

class Verifier:
    def __init__(self, criterion: str = "high-risk sample must flag elevated with score >=0.55 and pause_ratio as top or weighted >=0.35"):
        self.criterion = criterion
    
    def check(self, output: Dict, sample: Dict) -> Tuple[bool, str]:
        score = output["risk_score"]
        flag = output["flag"]
        top = output["top_feature"]
        pause_w = output["weights"].get("pause_ratio", 0)
        
        passed = (flag == "elevated" and score >= 0.55 and (top == "pause_ratio" or pause_w >= 0.35))
        reason = "PASS" if passed else f"FAIL: score={score} flag={flag} top={top} pause_w={pause_w} (need elevated >=0.55 with pause emphasis)"
        return passed, reason

class Updater:
    def revise(self, generator: Generator, critique: str, sample: Dict) -> Generator:
        # Simple rule: boost pause weight if critique mentions FAIL and pause not emphasized
        new_w = generator.weights.copy()
        if "FAIL" in critique and "pause" in critique.lower():
            new_w["pause_ratio"] = min(0.5, new_w["pause_ratio"] + 0.15)
            # Normalize others roughly
            total = sum(new_w.values())
            new_w = {k: v / total for k, v in new_w.items()}
        return Generator(new_w)

def run_gvu(sample: Dict, max_passes: int = 3) -> List[Dict]:
    gen = Generator()
    ver = Verifier()
    upd = Updater()
    log = []
    
    for i in range(1, max_passes + 1):
        out = gen.produce(sample)
        passed, reason = ver.check(out, sample)
        entry = {
            "pass": i,
            "output": out,
            "verifier_pass": passed,
            "reason": reason
        }
        log.append(entry)
        print(f"Pass {i}: score={out['risk_score']} flag={out['flag']} top={out['top_feature']} | {reason}")
        if passed or i == max_passes:
            break
        gen = upd.revise(gen, reason, sample)
    
    return log

if __name__ == "__main__":
    print("=== Smoke Test: High-risk Speech Sample ===")
    results = run_gvu(SAMPLE)
    print("\n=== Final Log ===")
    print(json.dumps(results, indent=2))
    print("\nSelf-improvement complete. Core insight: embedding + acoustic features refined via GVU for personalized early dementia risk flag.")
