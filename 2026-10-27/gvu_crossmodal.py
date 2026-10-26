#!/usr/bin/env python3
"""
Minimal GVU self-improving multi-agent prototype for cross-modal speech+text AD risk flag.
Based on Ding et al. 2026 cross-attention insight: acoustic + linguistic fusion.
Pure Python, no external deps. Smoke-testable in <2 hours.
"""

import json
from typing import Dict, List, Tuple

class Generator:
    def __init__(self, weights: Dict[str, float] = None, threshold: float = 0.40):
        self.weights = weights or {"pause": 0.55, "lexical": 0.45}
        self.threshold = threshold
    
    def generate(self, features: Dict[str, float]) -> Dict:
        # Cross-modal fusion score: weighted acoustic (pause) + linguistic (1-lexical_div)
        score = (features["pause_ratio"] * self.weights["pause"] + 
                 (1 - features["lexical_div"]) * self.weights["lexical"])
        flag = "elevated" if score > self.threshold else "typical"
        return {
            "risk_score": round(score, 3),
            "flag": flag,
            "weights_used": self.weights.copy(),
            "threshold": self.threshold,
            "features": features
        }

class Verifier:
    def verify(self, output: Dict, features: Dict, true_label: str = None) -> Tuple[bool, str]:
        # Explicit success criterion: flag matches true_label (if given), score in [0,1], weights sum ~1.0
        if true_label and output["flag"] != true_label:
            return False, f"Flag mismatch: predicted {output['flag']} vs true {true_label}. Score={output['risk_score']}"
        if not (0 <= output["risk_score"] <= 1):
            return False, "Score out of [0,1]"
        wsum = sum(output["weights_used"].values())
        if abs(wsum - 1.0) > 0.05:
            return False, f"Weights sum {wsum:.2f} not ~1"
        return True, "Pass: flag matches criterion and constraints held"

class Updater:
    def update(self, generator: Generator, critique: str, features: Dict, true_label: str) -> Generator:
        new_weights = generator.weights.copy()
        new_thresh = generator.threshold
        if "mismatch" in critique.lower() and true_label == "elevated":
            # Lower threshold and boost the stronger elevated-supporting feature
            new_thresh = max(0.30, new_thresh - 0.06)
            if features["pause_ratio"] > 0.25:
                new_weights["pause"] = min(0.75, new_weights["pause"] + 0.10)
                new_weights["lexical"] = max(0.25, new_weights["lexical"] - 0.10)
        elif "mismatch" in critique.lower():
            new_thresh = min(0.50, new_thresh + 0.04)
        # Normalize weights
        s = sum(new_weights.values())
        new_weights = {k: round(v / s, 3) for k, v in new_weights.items()}
        return Generator(new_weights, new_thresh)

def run_gvu(features: Dict, true_label: str, max_passes: int = 3) -> List[Dict]:
    gen = Generator(threshold=0.42)  # start high so first pass may fail
    ver = Verifier()
    upd = Updater()
    log = []
    for pass_num in range(1, max_passes + 1):
        output = gen.generate(features)
        passed, reason = ver.verify(output, features, true_label)
        log_entry = {
            "pass": pass_num,
            "output": output,
            "passed": passed,
            "reason": reason
        }
        log.append(log_entry)
        if passed:
            break
        gen = upd.update(gen, reason, features, true_label)
    return log

if __name__ == "__main__":
    # Smoke test on borderline elevated sample
    sample = {"pause_ratio": 0.32, "lexical_div": 0.50}
    true = "elevated"
    results = run_gvu(sample, true)
    print("=== Smoke Test: Cross-modal AD Risk Flag GVU ===")
    print(json.dumps(results, indent=2))
    print("\nBefore (pass 1 flag):", results[0]["output"]["flag"], "score:", results[0]["output"]["risk_score"])
    print("After (final flag):", results[-1]["output"]["flag"], "score:", results[-1]["output"]["risk_score"])
    print("Passes used:", len(results))
