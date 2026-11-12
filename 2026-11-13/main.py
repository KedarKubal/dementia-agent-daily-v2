#!/usr/bin/env python3
"""
Minimal GVU prototype for speech-biomarker early dementia risk flag.
Based on linguistic features insight from spoken language biomarker papers.
Generator produces risk score from pause_ratio and lexical_diversity.
Verifier checks against criterion: for high-pause samples, pause must be top feature and score >0.6.
Updater loops 3 times adjusting weights.
"""
import json
from typing import Dict, List, Tuple

class Generator:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {"pause_ratio": 0.2, "lexical_diversity": 0.3, "hesitation": 0.3}
        self.bias = 0.1

    def produce(self, sample: Dict[str, float]) -> Dict:
        score = self.bias
        for feat, w in self.weights.items():
            score += w * sample.get(feat, 0)
        score = max(0, min(1, score))
        top_feature = max(self.weights, key=self.weights.get)
        flag = "elevated" if score > 0.6 else "typical"
        return {
            "score": round(score, 3),
            "flag": flag,
            "top_feature": top_feature,
            "weights": self.weights.copy(),
            "rationale": f"Weighted sum with bias {self.bias}"
        }

class Verifier:
    def __init__(self, criterion: str = "high_pause_prioritized_elevated"):
        self.criterion = criterion

    def check(self, output: Dict, sample: Dict) -> Tuple[bool, str]:
        # Explicit criterion: if pause_ratio > 0.5, top_feature must be pause_ratio and score > 0.6
        if sample.get("pause_ratio", 0) > 0.5:
            if output["top_feature"] != "pause_ratio" or output["score"] <= 0.6:
                return False, f"Failed: high pause sample but top={output['top_feature']}, score={output['score']} (need pause top and >0.6)"
            return True, "Pass: pause prioritized and elevated on high-pause sample"
        return True, "Pass: non-high-pause sample, no strict requirement"

class Updater:
    def __init__(self, generator: Generator):
        self.generator = generator

    def update(self, critique: str, sample: Dict) -> None:
        # Simple rule: if critique mentions pause not top, boost pause weight
        if "pause" in critique.lower() and ("not" in critique.lower() or "top=" in critique):
            self.generator.weights["pause_ratio"] = min(0.8, self.generator.weights["pause_ratio"] + 0.15)
            # Normalize others roughly
            total = sum(self.generator.weights.values())
            for k in self.generator.weights:
                self.generator.weights[k] /= total
            self.generator.bias = min(0.3, self.generator.bias + 0.05)
        print(f"Updater adjusted weights to {self.generator.weights}")

def run_gvu(sample: Dict, max_passes: int = 3) -> List[Dict]:
    gen = Generator()
    ver = Verifier()
    upd = Updater(gen)
    logs = []
    for i in range(1, max_passes + 1):
        out = gen.produce(sample)
        passed, reason = ver.check(out, sample)
        logs.append({"pass": i, "output": out, "passed": passed, "reason": reason})
        print(f"Pass {i}: score={out['score']} flag={out['flag']} top={out['top_feature']} | {reason}")
        if passed:
            break
        upd.update(reason, sample)
    return logs

if __name__ == "__main__":
    # Sample high-pause speech features (simulated from DementiaBank-style)
    sample = {"pause_ratio": 0.72, "lexical_diversity": 0.45, "hesitation": 0.55}
    print("=== Smoke test high-pause sample ===")
    logs = run_gvu(sample)
    with open("smoke_test.json", "w") as f:
        json.dump({"sample": sample, "logs": logs}, f, indent=2)
    print("\nFinal output after loop:")
    print(json.dumps(logs[-1], indent=2))
