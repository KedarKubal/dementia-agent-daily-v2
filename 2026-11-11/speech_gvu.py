#!/usr/bin/env python3
"""
Minimal GVU prototype for speech-biomarker early dementia risk flag.
Insight from papers: percentage of silence duration (PSD/pause_ratio) as key underexploited digital biomarker correlating with cognitive decline and fluid markers.
Verifier success criterion: for samples with pause_ratio > 0.4, output must have top_feature == 'pause_ratio' AND score >= 0.7 (elevated flag).
"""
import json
from typing import Dict, List, Tuple

class Generator:
    def __init__(self):
        self.weights = {"pause_ratio": 0.35, "lexical_diversity": 0.35, "speaking_rate": 0.30}
        self.bias = 0.15

    def generate(self, features: Dict[str, float]) -> Dict:
        score = self.bias + sum(self.weights[k] * features.get(k, 0.0) for k in self.weights)
        score = max(0.0, min(1.0, score))
        top_feature = max(self.weights.items(), key=lambda x: x[1])[0]
        flag = "elevated" if score >= 0.6 else "typical"
        return {
            "score": round(score, 3),
            "flag": flag,
            "top_feature": top_feature,
            "weights": {k: round(v, 3) for k, v in self.weights.items()}
        }

class Verifier:
    def verify(self, output: Dict, features: Dict[str, float]) -> Tuple[bool, str]:
        pr = features.get("pause_ratio", 0)
        if pr > 0.4:
            if output["top_feature"] != "pause_ratio" or output["score"] < 0.7:
                return False, f"High pause_ratio={pr:.2f} requires top_feature=pause_ratio and score>=0.7; got top={output['top_feature']}, score={output['score']}"
        return True, "Pass: explicit success criterion met"

class Updater:
    def update(self, generator: Generator, critique: str, features: Dict) -> Generator:
        if "pause_ratio" in critique and "score" in critique:
            # Boost pause weight and bias to raise score
            generator.weights["pause_ratio"] = min(0.75, generator.weights["pause_ratio"] + 0.15)
            generator.bias = min(0.4, generator.bias + 0.1)
            # Soft normalize
            total_w = sum(generator.weights.values())
            if total_w > 1.0:
                for k in generator.weights:
                    generator.weights[k] /= total_w
        return generator

def run_gvu(features: Dict[str, float], max_passes: int = 3) -> List[Dict]:
    gen = Generator()
    ver = Verifier()
    upd = Updater()
    log = []
    for i in range(1, max_passes + 1):
        out = gen.generate(features)
        passed, reason = ver.verify(out, features)
        log.append({"pass": i, "output": out, "passed": passed, "reason": reason})
        if passed:
            break
        gen = upd.update(gen, reason, features)
    return log

if __name__ == "__main__":
    sample_high = {"pause_ratio": 0.62, "lexical_diversity": 0.35, "speaking_rate": 0.28}
    results = run_gvu(sample_high)
    print(json.dumps(results, indent=2))
    with open("smoke_test_output.json", "w") as f:
        json.dump({"sample": sample_high, "gvu_log": results}, f, indent=2)
