# 2026-10-11 Speech Age Gap GVU Prototype
# Minimal self-improving multi-agent for speech-clock style dementia screening insight.
# Based on Hernandez et al. Science Advances 2026 speech clocks paper.
# Generator produces candidate SAG + interpretation from simple features.
# Verifier checks explicit criteria: SAG in plausible range, multi-feature use, no single-feature dominance.
# Updater revises based on critique. 2-3 passes logged.

from dataclasses import dataclass
from typing import Dict, Any, List
import json

@dataclass
class SpeechFeatures:
    pause_rate: float  # pauses per min
    speech_rate: float  # words per min
    lexical_diversity: float  # type-token ratio
    pitch_variability: float  # std of pitch

class Generator:
    def generate(self, features: SpeechFeatures, critique: str = "") -> Dict[str, Any]:
        # Simple rule-based generator simulating speech clock age gap
        base_gap = 0.0
        if features.pause_rate > 0.3:
            base_gap += 2.5
        if features.speech_rate < 110:
            base_gap += 1.8
        if features.lexical_diversity < 0.45:
            base_gap += 1.2
        if features.pitch_variability < 15:
            base_gap += 0.9
        # Apply critique if present
        if "single-feature" in critique.lower() or "pause only" in critique.lower():
            # Diversify
            base_gap = (base_gap * 0.6) + (features.lexical_diversity * -2 + 3)
        sag = round(base_gap, 2)
        interpretation = "elevated_speech_age" if sag > 2.0 else "typical_range"
        return {
            "speech_age_gap": sag,
            "interpretation": interpretation,
            "features_used": ["pause_rate", "speech_rate", "lexical_diversity", "pitch_variability"],
            "pass_note": critique or "initial"
        }

class Verifier:
    def verify(self, output: Dict[str, Any], features: SpeechFeatures) -> Dict[str, Any]:
        sag = output["speech_age_gap"]
        reasons = []
        passed = True
        # Criterion 1: plausible range -5 to 10 years
        if not (-5 <= sag <= 10):
            passed = False
            reasons.append("SAG outside plausible range [-5,10]")
        # Criterion 2: multi-feature (at least 3)
        if len(output.get("features_used", [])) < 3:
            passed = False
            reasons.append("single-feature or insufficient features")
        # Criterion 3: not dominated by pause alone (if pause high but others normal, flag)
        if features.pause_rate > 0.4 and features.speech_rate > 120 and features.lexical_diversity > 0.5:
            if sag > 3.0:
                passed = False
                reasons.append("over-weighted pause only")
        return {
            "passed": passed,
            "reasons": reasons or ["ok"],
            "critique": "; ".join(reasons) if reasons else "meets multi-feature range criteria"
        }

class Updater:
    def run_loop(self, features: SpeechFeatures, max_passes: int = 3) -> List[Dict]:
        gen = Generator()
        ver = Verifier()
        log = []
        critique = ""
        for i in range(1, max_passes + 1):
            out = gen.generate(features, critique)
            v = ver.verify(out, features)
            entry = {
                "pass": i,
                "output": out,
                "verification": v
            }
            log.append(entry)
            if v["passed"]:
                break
            critique = v["critique"]
        return log

def smoke_test():
    # Sample: elevated pause, low diversity (MCI-like)
    sample = SpeechFeatures(pause_rate=0.42, speech_rate=95, lexical_diversity=0.38, pitch_variability=12)
    updater = Updater()
    results = updater.run_loop(sample)
    return results

if __name__ == "__main__":
    results = smoke_test()
    print(json.dumps(results, indent=2))
    print("\n--- Before/After ---")
    if results:
        print("Pass 1:", results[0]["output"])
        print("Final:", results[-1]["output"])
        print("Passes:", len(results))
