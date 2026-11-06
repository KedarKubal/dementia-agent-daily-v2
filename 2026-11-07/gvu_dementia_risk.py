#!/usr/bin/env python3
"""
Minimal GVU self-improving agent for passive multi-modal dementia risk flag.
Diagnostics/Biosensors angle: fuses speech pause_ratio + gait_variability
into a daily cognitive-reserve trajectory score from consumer sensors.
Underexploited insight: longitudinal passive fusion of dual-task gait cost
and speech pause patterns (not lab single-modality or episodic testing).
"""

from typing import Dict, List, Tuple
import json

SAMPLE_FEATURES = {
    "pause_ratio": 0.48,
    "lexical_diversity": 0.32,
    "gait_variability": 0.22,
    "sleep_fragmentation": 0.35
}

SUCCESS_CRITERIA = {
    "expected_level": "elevated",
    "min_score": 0.60,
    "must_include_feature": "pause_ratio"
}

class Generator:
    def __init__(self):
        self.bias = 0.0
        self.weights = {
            "pause_ratio": 0.25,
            "lexical_diversity": 0.20,
            "gait_variability": 0.30,
            "sleep_fragmentation": 0.25
        }
    
    def produce(self, features: Dict[str, float], critique: str = "") -> Dict:
        raw = sum(self.weights[k] * features.get(k, 0) for k in self.weights)
        score = min(1.0, raw * 1.75 + self.bias)
        
        top_features = sorted(
            self.weights.keys(),
            key=lambda k: self.weights[k] * features.get(k, 0),
            reverse=True
        )[:2]
        level = "elevated" if score >= 0.55 else "typical"
        
        return {
            "risk_score": round(score, 3),
            "risk_level": level,
            "top_features": top_features,
            "weights_used": {k: round(v, 3) for k, v in self.weights.items()},
            "rationale": (
                f"Fused passive speech/gait proxies. Critique: {critique[:60]}..."
                if critique else "Initial fixed-weight fusion draft."
            )
        }

class Verifier:
    def check(self, output: Dict, features: Dict) -> Tuple[bool, str]:
        score = output["risk_score"]
        level = output["risk_level"]
        tops = output["top_features"]
        
        reasons = []
        passed = True
        
        if level != SUCCESS_CRITERIA["expected_level"]:
            passed = False
            reasons.append(f"Level '{level}' != expected 'elevated'")
        if score < SUCCESS_CRITERIA["min_score"]:
            passed = False
            reasons.append(f"Score {score} < min {SUCCESS_CRITERIA['min_score']}")
        if SUCCESS_CRITERIA["must_include_feature"] not in tops:
            passed = False
            reasons.append(f"Required feature '{SUCCESS_CRITERIA['must_include_feature']}' not in top_features")
        
        if (features["pause_ratio"] > 0.4 and features["gait_variability"] > 0.15
                and level == "typical"):
            passed = False
            reasons.append("High pause + gait variability but flagged typical")
        
        critique = (
            "; ".join(reasons)
            if reasons
            else "Criteria met: elevated level, score>=0.60, pause_ratio in top features."
        )
        return passed, critique

class Updater:
    def __init__(self, generator: Generator):
        self.gen = generator
        self.history: List[Dict] = []
    
    def run_loop(self, features: Dict, max_passes: int = 3) -> List[Dict]:
        critique = ""
        results = []
        for pass_num in range(1, max_passes + 1):
            output = self.gen.produce(features, critique)
            passed, new_critique = Verifier().check(output, features)
            
            entry = {
                "pass": pass_num,
                "output": output,
                "passed": passed,
                "critique": new_critique
            }
            results.append(entry)
            self.history.append(entry)
            
            if passed:
                break
            
            if "score" in new_critique.lower() or "elevated" in new_critique.lower():
                self.gen.weights["pause_ratio"] = min(0.60, self.gen.weights["pause_ratio"] + 0.10)
                self.gen.weights["gait_variability"] = min(0.55, self.gen.weights["gait_variability"] + 0.10)
                total = sum(self.gen.weights.values())
                self.gen.weights = {k: v / total for k, v in self.gen.weights.items()}
                self.gen.bias += 0.05
            critique = new_critique
        
        return results

def smoke_test():
    print("=== Smoke Test: High-risk passive multi-modal sample ===")
    gen = Generator()
    updater = Updater(gen)
    results = updater.run_loop(SAMPLE_FEATURES, max_passes=3)
    
    for r in results:
        print(f"\n--- Pass {r['pass']} ---")
        print(json.dumps(r["output"], indent=2))
        print(f"Passed: {r['passed']}")
        print(f"Critique: {r['critique']}")
    
    print("\n=== Final weights ===")
    print(json.dumps({k: round(v, 3) for k, v in gen.weights.items()}, indent=2))
    return results

if __name__ == "__main__":
    smoke_test()
