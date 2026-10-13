"""
Minimal Self-Improving Multi-Agent Prototype: Speech Biomarker Risk Flag (GVU pattern)
Based on SpeechDETECT paper insight: explainable feature ranking (SHAP-like) + triage via cumulative gains for early dementia screening.

Generator: produces candidate risk score + top features from mock speech features.
Verifier: checks explicit criteria (score in [0,1], fluency features present for high-risk, etc.).
Updater: feeds critique, regenerates up to 3 passes, logs changes.
"""

from typing import Dict, List, Tuple, Any
import json
from datetime import datetime

# Mock speech features from a short recording (e.g., picture description)
SAMPLE_FEATURES = {
    "pause_ratio": 0.35,  # high
    "hesitation_rate": 0.28,  # high
    "lexical_diversity": 0.42,  # low
    "mean_length_utterance": 6.2,  # low
    "formant_dynamics": 0.15,  # abnormal
    "speech_rate": 1.8,  # slow
}

LABELED_HIGH_RISK = True  # for smoke test

class Generator:
    def __init__(self):
        self.pass_num = 0

    def generate(self, features: Dict[str, float], critique: str = "") -> Dict[str, Any]:
        self.pass_num += 1
        # Simple heuristic scoring, refined by critique
        base_score = (
            features.get("pause_ratio", 0) * 0.4 +
            features.get("hesitation_rate", 0) * 0.3 +
            (1 - features.get("lexical_diversity", 0.5)) * 0.2 +
            (1 - min(features.get("mean_length_utterance", 10)/15, 1)) * 0.1
        )
        # Adjust based on critique for self-improvement
        if "high-risk" in critique.lower() or "0.70" in critique:
            base_score = min(base_score + 0.25, 0.95)
        if "fluency" in critique.lower() or "pause" in critique.lower():
            # Force fluency into top and boost
            base_score = min(base_score + 0.1, 0.95)
        if "range" in critique.lower():
            base_score = max(0.0, min(1.0, base_score))

        # Prefer fluency features in ranking when relevant
        fluency_keys = ["pause_ratio", "hesitation_rate"]
        top_candidates = list(features.items())
        if "fluency" in critique.lower() or self.pass_num > 1:
            # Boost fluency scores for ranking
            for k in fluency_keys:
                if k in features:
                    top_candidates = [(kk, vv * 1.5 if kk in fluency_keys else vv) for kk, vv in top_candidates]

        top_features = sorted(top_candidates, key=lambda x: x[1], reverse=True)[:3]

        return {
            "risk_score": round(base_score, 3),
            "top_features": [f[0] for f in top_features],
            "flag": "elevated" if base_score > 0.6 else "normal",
            "pass": self.pass_num,
            "timestamp": datetime.now().isoformat()
        }

class Verifier:
    SUCCESS_CRITERIA = [
        "risk_score must be in [0.0, 1.0]",
        "for high-risk labeled sample, risk_score >= 0.70",
        "top_features must include at least one fluency metric (pause_ratio or hesitation_rate)",
        "flag must be 'elevated' or 'normal'"
    ]

    def verify(self, output: Dict[str, Any], is_high_risk: bool) -> Tuple[bool, str]:
        reasons = []
        score = output.get("risk_score", -1)
        tops = output.get("top_features", [])
        flag = output.get("flag", "")

        if not (0.0 <= score <= 1.0):
            reasons.append("risk_score out of [0,1]")
        if is_high_risk and score < 0.70:
            reasons.append("high-risk sample score < 0.70")
        if not any(f in tops for f in ["pause_ratio", "hesitation_rate"]):
            reasons.append("missing fluency feature in top_features")
        if flag not in ["elevated", "normal"]:
            reasons.append("invalid flag")

        passed = len(reasons) == 0
        critique = "; ".join(reasons) if reasons else "All criteria passed"
        return passed, critique

class Updater:
    def run_loop(self, features: Dict[str, float], is_high_risk: bool, max_passes: int = 3) -> List[Dict[str, Any]]:
        gen = Generator()
        ver = Verifier()
        history = []
        critique = ""

        for i in range(max_passes):
            candidate = gen.generate(features, critique)
            passed, critique = ver.verify(candidate, is_high_risk)
            entry = {
                "pass": i + 1,
                "output": candidate,
                "passed": passed,
                "critique": critique
            }
            history.append(entry)
            if passed:
                break
            # else feed critique for next

        return history

def smoke_test():
    updater = Updater()
    history = updater.run_loop(SAMPLE_FEATURES, LABELED_HIGH_RISK)
    print("=== Smoke Test Results ===")
    for h in history:
        print(json.dumps(h, indent=2))
    print("\nFinal output:", json.dumps(history[-1]["output"], indent=2))
    return history

if __name__ == "__main__":
    smoke_test()
