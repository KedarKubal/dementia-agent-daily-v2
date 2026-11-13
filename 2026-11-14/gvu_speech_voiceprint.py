#!/usr/bin/env python3
"""
Minimal GVU prototype for passive speech-biomarker MCI risk flag.
Based on Voiceprints of cognitive impairment (npj Dementia 2025) insight:
end-to-end deep models achieve high AUC (~0.988) on Craft Story speech for MCI detection.
This simulates feature extraction + self-improving risk scoring via Generator-Verifier-Updater.
Success criterion: risk_score >= 0.7 AND top_feature is 'pause_ratio' or 'linguistic_informativeness' for high-risk samples.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import json

@dataclass
class SpeechFeatures:
    pause_ratio: float
    linguistic_informativeness: float  # lower = worse
    acoustic_stability: float
    # Simulated from end-to-end embedding distance or LLM score

class Generator:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {"pause_ratio": 0.4, "linguistic_informativeness": 0.3, "acoustic_stability": 0.3}
        self.bias = 0.0

    def generate(self, features: SpeechFeatures) -> Dict:
        score = (
            self.weights["pause_ratio"] * features.pause_ratio +
            self.weights["linguistic_informativeness"] * (1 - features.linguistic_informativeness) +
            self.weights["acoustic_stability"] * (1 - features.acoustic_stability) +
            self.bias
        )
        score = max(0.0, min(1.0, score))
        top_feature = max(self.weights, key=self.weights.get)
        flag = "elevated" if score >= 0.65 else "typical"
        return {
            "risk_score": round(score, 3),
            "flag": flag,
            "top_feature": top_feature,
            "weights": self.weights.copy(),
            "bias": self.bias
        }

class Verifier:
    def __init__(self, criterion: str = "risk_score >= 0.7 and top_feature in ['pause_ratio', 'linguistic_informativeness'] for high-risk"):
        self.criterion = criterion

    def verify(self, output: Dict, features: SpeechFeatures, is_high_risk_sample: bool = True) -> Tuple[bool, str]:
        score_ok = output["risk_score"] >= 0.7 if is_high_risk_sample else output["risk_score"] < 0.5
        feature_ok = output["top_feature"] in ["pause_ratio", "linguistic_informativeness"] if is_high_risk_sample else True
        passed = score_ok and feature_ok
        reason = "PASS" if passed else f"FAIL: score={output['risk_score']} (need >=0.7), top={output['top_feature']}"
        return passed, reason

class Updater:
    def update(self, generator: Generator, critique: str, features: SpeechFeatures) -> None:
        # Simple rule-based updater: boost pause if critique mentions score or feature
        if "score" in critique.lower() or "fail" in critique.lower():
            generator.weights["pause_ratio"] = min(0.8, generator.weights["pause_ratio"] + 0.15)
            # Normalize others roughly
            total = sum(generator.weights.values())
            for k in generator.weights:
                generator.weights[k] /= total
            generator.bias = min(0.2, generator.bias + 0.05)
        if "top" in critique.lower() and "pause" not in critique.lower():
            generator.weights["pause_ratio"] = min(0.7, generator.weights.get("pause_ratio", 0.4) + 0.1)

def run_gvu(features: SpeechFeatures, max_passes: int = 3, is_high_risk: bool = True) -> List[Dict]:
    gen = Generator()
    ver = Verifier()
    upd = Updater()
    log = []
    for i in range(max_passes):
        output = gen.generate(features)
        passed, reason = ver.verify(output, features, is_high_risk)
        log.append({
            "pass": i + 1,
            "output": output,
            "passed": passed,
            "reason": reason
        })
        if passed:
            break
        upd.update(gen, reason, features)
    return log

if __name__ == "__main__":
    # High-risk sample: high pause, low informativeness
    high_risk = SpeechFeatures(pause_ratio=0.72, linguistic_informativeness=0.35, acoustic_stability=0.4)
    print("=== Smoke Test: High-risk sample ===")
    results = run_gvu(high_risk, is_high_risk=True)
    for entry in results:
        print(json.dumps(entry, indent=2))
    print("\nBefore (pass 1):", results[0]["output"])
    print("After (final):", results[-1]["output"])
