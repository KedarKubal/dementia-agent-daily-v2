#!/usr/bin/env python3
"""
Minimal GVU prototype for gait foundation model insight:
Self-improving risk flag from skeletal motion embeddings / gait features
for continuous dementia progression monitoring.
"""

import json
from typing import Dict, Any

# Sample: high gait variability indicating risk
SAMPLE = {
    "id": "GAIT-FOUND-042",
    "stride_variability": 0.28,  # high
    "speed": 0.72,  # m/s slow
    "embedding_distance": 0.65,  # from healthy foundation embedding
    "age": 72,
    "torso_stability": 0.45
}

class Generator:
    def __init__(self):
        self.weights = {"variability": 0.3, "speed": 0.2, "embedding": 0.3, "age": 0.1, "torso": 0.1}
        self.bias = 0.0

    def generate(self, sample: Dict) -> Dict[str, Any]:
        score = (
            self.weights["variability"] * sample["stride_variability"] * 3 +
            self.weights["speed"] * (1.0 - sample["speed"]) +
            self.weights["embedding"] * sample["embedding_distance"] +
            self.weights["age"] * (sample["age"] - 60) / 30 +
            self.weights["torso"] * (1 - sample["torso_stability"]) +
            self.bias
        )
        score = min(max(score, 0.0), 1.0)
        flag = "elevated" if score > 0.6 else "typical"
        top = max(self.weights, key=self.weights.get)
        return {
            "score": round(score, 3),
            "flag": flag,
            "top_feature": top,
            "weights": self.weights.copy(),
            "bias": self.bias
        }

class Verifier:
    def verify(self, output: Dict, sample: Dict) -> Dict[str, Any]:
        # Success criterion: for high-var sample, flag elevated AND top_feature in ['variability', 'embedding'] AND score > 0.6
        high_risk = sample["stride_variability"] > 0.2 or sample["embedding_distance"] > 0.5
        criteria_met = (
            high_risk and
            output["flag"] == "elevated" and
            output["score"] > 0.6 and
            output["top_feature"] in ["variability", "embedding"]
        )
        reason = "ok" if criteria_met else f"Fail: flag={output['flag']}, score={output['score']}, top={output['top_feature']}"
        return {"pass": criteria_met, "reason": reason}

class Updater:
    def update(self, generator: Generator, critique: str, sample: Dict):
        # Simple rule-based updater from critique
        if "top=" in critique and "variability" not in critique:
            generator.weights["variability"] += 0.15
            generator.weights["embedding"] += 0.1
            # normalize
            total = sum(generator.weights.values())
            for k in generator.weights:
                generator.weights[k] /= total
        if "score=" in critique and float(critique.split("score=")[1].split(",")[0]) < 0.6:
            generator.bias += 0.1

def run_gvu(sample: Dict, passes: int = 3) -> list:
    gen = Generator()
    ver = Verifier()
    upd = Updater()
    log = []
    for i in range(passes):
        out = gen.generate(sample)
        v = ver.verify(out, sample)
        entry = {"pass": i+1, "output": out, "verifier": v}
        log.append(entry)
        if v["pass"]:
            break
        upd.update(gen, v["reason"], sample)
    return log

if __name__ == "__main__":
    results = run_gvu(SAMPLE)
    print(json.dumps(results, indent=2))
    with open("smoke_test_output.json", "w") as f:
        json.dump(results, f, indent=2)
