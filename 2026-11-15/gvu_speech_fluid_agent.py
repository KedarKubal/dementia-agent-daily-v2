#!/usr/bin/env python3
"""
Minimal self-improving GVU agent for speech PSD + fluid biomarker fusion risk flag.
Based on insight from speech digital biomarker + fluid biomarkers paper (high AUC multimodal).

Generator produces candidate risk score and feature importance.
Verifier checks explicit criteria.
Updater revises weights based on critique.
Smoke-test on one high-risk sample.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import json

@dataclass
class Sample:
    psd: float  # percentage of silence duration (0-1)
    p_tau217: float  # normalized plasma p-tau217
    gfap: float
    age: float
    label: str  # expected: "elevated" for high-risk

# High-risk sample (high PSD, elevated biomarkers)
HIGH_RISK = Sample(psd=0.62, p_tau217=0.78, gfap=0.65, age=72, label="elevated")

class Generator:
    def __init__(self, weights: Dict[str, float]):
        self.weights = weights

    def generate(self, sample: Sample) -> Dict:
        score = (
            self.weights["psd"] * sample.psd +
            self.weights["p_tau217"] * sample.p_tau217 +
            self.weights["gfap"] * sample.gfap +
            self.weights["age"] * (sample.age - 60) / 40  # normalize age
        )
        score = max(0.0, min(1.0, score))
        # Simple feature ranking
        contribs = {
            "psd": self.weights["psd"] * sample.psd,
            "p_tau217": self.weights["p_tau217"] * sample.p_tau217,
            "gfap": self.weights["gfap"] * sample.gfap,
            "age": self.weights["age"] * (sample.age - 60) / 40,
        }
        top_feature = max(contribs, key=contribs.get)
        risk_flag = "elevated" if score >= 0.55 else "typical"
        return {
            "score": round(score, 3),
            "risk_flag": risk_flag,
            "top_feature": top_feature,
            "contribs": {k: round(v, 3) for k, v in contribs.items()},
            "weights": self.weights.copy(),
        }

class Verifier:
    SUCCESS_CRITERIA = [
        "score >= 0.55 for high-risk sample",
        "risk_flag == 'elevated'",
        "top_feature in ['psd', 'p_tau217'] (multimodal prioritized)",
    ]

    def verify(self, output: Dict, sample: Sample) -> Tuple[bool, str]:
        reasons = []
        passed = True
        if output["score"] < 0.55:
            passed = False
            reasons.append(f"score {output['score']} < 0.55")
        if output["risk_flag"] != "elevated":
            passed = False
            reasons.append(f"risk_flag {output['risk_flag']} != elevated")
        if output["top_feature"] not in ["psd", "p_tau217"]:
            passed = False
            reasons.append(f"top_feature {output['top_feature']} not multimodal priority")
        reason = "; ".join(reasons) if reasons else "all criteria met"
        return passed, reason

class Updater:
    def update(self, weights: Dict[str, float], critique: str) -> Dict[str, float]:
        new_w = weights.copy()
        if "score" in critique and "<" in critique:
            # Boost PSD and biomarkers
            new_w["psd"] = min(0.5, new_w["psd"] + 0.08)
            new_w["p_tau217"] = min(0.4, new_w["p_tau217"] + 0.05)
            new_w["gfap"] = min(0.3, new_w["gfap"] + 0.03)
        if "top_feature" in critique:
            new_w["psd"] = min(0.55, new_w["psd"] + 0.1)
        # Normalize roughly
        total = sum(new_w.values())
        if total > 1.2:
            for k in new_w:
                new_w[k] /= total / 1.0
        return new_w

def run_gvu(sample: Sample, initial_weights: Dict[str, float], max_passes: int = 3) -> List[Dict]:
    weights = initial_weights
    logs = []
    for i in range(1, max_passes + 1):
        gen = Generator(weights)
        output = gen.generate(sample)
        passed, reason = Verifier().verify(output, sample)
        logs.append({
            "pass": i,
            "output": output,
            "passed": passed,
            "critique": reason,
        })
        if passed:
            break
        weights = Updater().update(weights, reason)
    return logs

if __name__ == "__main__":
    initial = {"psd": 0.25, "p_tau217": 0.20, "gfap": 0.15, "age": 0.10}
    results = run_gvu(HIGH_RISK, initial)
    print(json.dumps(results, indent=2))
    print("\n--- Smoke test summary ---")
    for r in results:
        print(f"Pass {r['pass']}: score={r['output']['score']} flag={r['output']['risk_flag']} top={r['output']['top_feature']} passed={r['passed']}")
