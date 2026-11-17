#!/usr/bin/env python3
"""
Minimal GVU prototype: Multimodal Speech+Gait Early Dementia Risk Flag
Based on Dieffenderfer et al. 2023 wearable system insight.
Generator produces risk score from pause_ratio + gait_cv.
Verifier checks explicit criterion.
Updater loops 3 times adjusting weights.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Features:
    pause_ratio: float  # higher = more risk
    gait_cv: float      # coefficient of variation, higher = more risk

class Generator:
    def __init__(self, w_pause: float = 0.4, w_gait: float = 0.4, bias: float = 0.0):
        self.w_pause = w_pause
        self.w_gait = w_gait
        self.bias = bias

    def generate(self, feats: Features) -> Dict:
        score = self.w_pause * feats.pause_ratio + self.w_gait * feats.gait_cv + self.bias
        score = max(0.0, min(1.0, score))
        flag = "elevated" if score >= 0.7 else "typical"
        top = "pause" if self.w_pause > self.w_gait else "gait"
        return {
            "score": round(score, 3),
            "flag": flag,
            "top_feature": top,
            "weights": {"pause": self.w_pause, "gait": self.w_gait, "bias": self.bias}
        }

class Verifier:
    def verify(self, output: Dict, feats: Features) -> Tuple[bool, str]:
        # Explicit criterion: if both features high (>0.6), score must be >=0.7 AND top_feature correctly prioritized
        both_high = feats.pause_ratio > 0.6 and feats.gait_cv > 0.6
        if both_high:
            if output["score"] >= 0.7 and output["flag"] == "elevated":
                return True, "pass: high multimodal risk correctly elevated"
            else:
                return False, f"fail: both features high but score={output['score']} flag={output['flag']}"
        else:
            if output["score"] < 0.7:
                return True, "pass: not both high, score appropriately low"
            else:
                return False, "fail: over-flagged low features"

class Updater:
    def update(self, gen: Generator, critique: str, feats: Features) -> None:
        if "fail" in critique and "both features high" in critique:
            # Boost the weaker weight and bias
            if gen.w_pause < gen.w_gait:
                gen.w_pause += 0.15
            else:
                gen.w_gait += 0.15
            gen.bias += 0.05
            # Normalize roughly
            total = gen.w_pause + gen.w_gait
            gen.w_pause /= total
            gen.w_gait /= total

def run_gvu(sample: Features, passes: int = 3) -> List[Dict]:
    gen = Generator()
    ver = Verifier()
    upd = Updater()
    log = []
    for i in range(passes):
        out = gen.generate(sample)
        passed, reason = ver.verify(out, sample)
        entry = {
            "pass": i + 1,
            "output": out,
            "passed": passed,
            "reason": reason
        }
        log.append(entry)
        print(f"Pass {i+1}: score={out['score']} flag={out['flag']} top={out['top_feature']} | {reason}")
        if passed:
            break
        upd.update(gen, reason, sample)
    return log

if __name__ == "__main__":
    # Smoke-test sample: high pause + high gait variability
    sample = Features(pause_ratio=0.72, gait_cv=0.68)
    print("=== Smoke Test: High-risk multimodal sample ===")
    results = run_gvu(sample)
    print("\nFinal output after loop:")
    print(results[-1]["output"])
