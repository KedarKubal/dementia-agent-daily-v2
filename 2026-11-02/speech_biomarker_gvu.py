"""
Speech Biomarker Risk Scorer - Self-Improving GVU Agent
Prototype for early dementia detection from speech features.
Based on spoken language biomarkers research (Ke et al., 2024).

Generator produces candidate risk score + flag from features.
Verifier checks against explicit criterion (pause ratio > 0.25 or lexical diversity < 0.4 implies elevated risk).
Updater loops 2-3 times with critique.
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class SpeechFeatures:
    pause_ratio: float  # fraction of time in pauses
    lexical_diversity: float  # type-token ratio
    speech_rate: float  # words per minute
    transcript: str

class GeneratorAgent:
    def generate(self, features: SpeechFeatures, critique: str = "") -> Dict[str, Any]:
        # Simple heuristic generator, adjusted by critique
        base_score = (features.pause_ratio * 0.6 + (1 - features.lexical_diversity) * 0.4) * 100
        if "overestimate" in critique.lower():
            base_score *= 0.85
        elif "underestimate" in critique.lower():
            base_score *= 1.15
        score = min(100, max(0, base_score))
        flag = "elevated" if score > 40 else "low"
        return {
            "risk_score": round(score, 1),
            "flag": flag,
            "reasoning": f"Score derived from pause_ratio={features.pause_ratio:.2f}, lexical_div={features.lexical_diversity:.2f}. {critique}"
        }

class VerifierAgent:
    def verify(self, output: Dict[str, Any], features: SpeechFeatures) -> Dict[str, Any]:
        # Explicit success criterion: if pause_ratio > 0.25 or lexical_diversity < 0.4, flag should be elevated and score > 35
        high_risk_indicators = features.pause_ratio > 0.25 or features.lexical_diversity < 0.4
        score_ok = output["risk_score"] > 35 if high_risk_indicators else output["risk_score"] <= 40
        flag_ok = (output["flag"] == "elevated") == high_risk_indicators or abs(output["risk_score"] - 40) < 10
        passed = score_ok and (output["flag"] == "elevated" if high_risk_indicators else output["flag"] == "low")
        reason = "Pass: consistent with biomarker thresholds" if passed else \
                 f"Fail: high_risk_indicators={high_risk_indicators} but got flag={output['flag']}, score={output['risk_score']}"
        return {"passed": passed, "reason": reason, "critique": reason if not passed else "Good match."}

class Updater:
    def __init__(self):
        self.generator = GeneratorAgent()
        self.verifier = VerifierAgent()
        self.logs: List[Dict] = []

    def run_loop(self, features: SpeechFeatures, max_passes: int = 3) -> List[Dict]:
        critique = ""
        for i in range(max_passes):
            candidate = self.generator.generate(features, critique)
            verification = self.verifier.verify(candidate, features)
            entry = {
                "pass": i + 1,
                "candidate": candidate,
                "verification": verification
            }
            self.logs.append(entry)
            if verification["passed"]:
                break
            critique = verification["critique"]
        return self.logs

def main():
    # Sample: elevated risk speech (high pauses, low diversity)
    sample = SpeechFeatures(
        pause_ratio=0.32,
        lexical_diversity=0.35,
        speech_rate=95.0,
        transcript="I... went to the... store and... bought some... things."
    )
    updater = Updater()
    results = updater.run_loop(sample)
    print(json.dumps([asdict(r) if hasattr(r, '__dataclass_fields__') else r for r in results], indent=2))
    # For demo, print summary
    print("\n=== Smoke Test Summary ===")
    for entry in results:
        print(f"Pass {entry['pass']}: score={entry['candidate']['risk_score']}, flag={entry['candidate']['flag']}, passed={entry['verification']['passed']}")

if __name__ == "__main__":
    main()
