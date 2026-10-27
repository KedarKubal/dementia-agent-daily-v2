#!/usr/bin/env python3
"""Minimal GVU for PSD+biomarker fusion dementia flag (prototypes speech+fluid paper insight)."""
import json
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Sample:
    psd: float
    p_tau217: float
    gfap: float

class Generator:
    def __init__(self):
        self.psd_w = 0.2  # start low so under-detects
        self.blood_w = 0.3
    
    def generate(self, sample: Sample, critique: str = "") -> Dict[str, Any]:
        if "boost_psd" in critique:
            self.psd_w = min(0.6, self.psd_w + 0.25)
        if "boost_blood" in critique:
            self.blood_w = min(0.6, self.blood_w + 0.15)
        blood = 1.0 if (sample.p_tau217 > 0.4 or sample.gfap > 100) else 0.0
        score = sample.psd * self.psd_w + blood * self.blood_w
        score = min(1.0, score)
        flag = "elevated" if score >= 0.5 else "typical"
        conf = 0.4 + score * 0.5
        return {
            "flag": flag,
            "score": round(score, 3),
            "confidence": round(conf, 3),
            "psd_weight": round(self.psd_w, 2),
            "blood_weight": round(self.blood_w, 2),
            "rationale": f"score=PSD*{self.psd_w:.2f}+blood*{self.blood_w:.2f}"
        }

class Verifier:
    def verify(self, out: Dict[str, Any], sample: Sample) -> Dict[str, Any]:
        high = sample.psd > 0.45 and (sample.p_tau217 > 0.4 or sample.gfap > 100)
        if high and out["flag"] == "elevated" and out["confidence"] >= 0.65:
            return {"pass": True, "reason": "OK: elevated high-risk with conf>=0.65", "critique": ""}
        if not high and out["flag"] == "typical" and out["confidence"] >= 0.5:
            return {"pass": True, "reason": "OK: typical low-risk", "critique": ""}
        crit = "boost_psd boost_blood" if high else ""
        return {"pass": False, "reason": "Failed criterion (under/over detection)", "critique": crit}

def run_gvu(sample: Sample, max_p: int = 3) -> List:
    g = Generator()
    v = Verifier()
    logs = []
    crit = ""
    for i in range(max_p):
        o = g.generate(sample, crit)
        vr = v.verify(o, sample)
        logs.append({"pass": i+1, "output": o, "verifier": vr})
        if vr["pass"]:
            break
        crit = vr["critique"]
    return logs

if __name__ == "__main__":
    sample = Sample(psd=0.58, p_tau217=0.51, gfap=70)
    logs = run_gvu(sample)
    print(json.dumps(logs, indent=2))
    open("smoke_test_output.json", "w").write(json.dumps(logs, indent=2))
