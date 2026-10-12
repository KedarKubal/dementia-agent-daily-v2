"""
Minimal GVU Multi-Agent Prototype for Speech Biomarker Dementia Risk Flag
Based on modular detectors insight from WATCH-SS paper.
Generator produces draft risk assessment from speech features.
Verifier critiques against explicit criteria (pause_ratio > 0.25 and lexical_diversity < 0.5 → high risk).
Updater loops 2-3 times incorporating critique.
"""

import json
from datetime import datetime

# Sample speech features (from typical DementiaBank-like data)
SAMPLE_FEATURES = {
    "pause_ratio": 0.35,  # high pauses
    "lexical_diversity": 0.28,  # low diversity
    "speech_rate": 90,  # syllables/min, low
    "intelligibility": 0.65
}

EXPECTED_HIGH_RISK = True  # based on criteria

class Generator:
    def generate(self, features, critique=None):
        pause = features["pause_ratio"]
        lex = features["lexical_diversity"]
        rate = features["speech_rate"]
        
        # Base draft
        if pause > 0.25 and lex < 0.5:
            risk = "HIGH"
            score = 0.85
            reason = f"Elevated pause_ratio ({pause}) and low lexical_diversity ({lex}) indicate cognitive impairment markers."
        else:
            risk = "LOW"
            score = 0.2
            reason = "Features within normal ranges."
        
        # Incorporate critique if present
        if critique and "too aggressive" in critique.lower():
            risk = "MODERATE"
            score = 0.6
            reason += " Adjusted for potential over-sensitivity as per verifier."
        elif critique and "missing rate" in critique.lower():
            if rate < 100:
                reason += f" Confirmed by low speech_rate ({rate})."
                score = min(0.95, score + 0.05)
        
        return {
            "risk_flag": risk,
            "risk_score": round(score, 2),
            "explanation": reason,
            "features_used": list(features.keys())
        }

class Verifier:
    def verify(self, output, features):
        pause = features["pause_ratio"]
        lex = features["lexical_diversity"]
        expected_high = pause > 0.25 and lex < 0.5
        
        actual_high = output["risk_flag"] in ["HIGH", "MODERATE"]
        
        if expected_high and not actual_high:
            return False, "Failed: Expected high risk based on pause_ratio > 0.25 and lexical_diversity < 0.5, but got low."
        if not expected_high and actual_high:
            return False, "Failed: Flagged high risk but features do not meet criteria. Too aggressive."
        if "speech_rate" not in output.get("features_used", []) and features["speech_rate"] < 100:
            return False, "Partial: Missing consideration of low speech_rate which supports impairment."
        
        return True, "Passed: Risk flag aligns with modular feature thresholds (pause + lexical)."

class Updater:
    def update(self, generator, features, max_passes=3):
        logs = []
        critique = None
        for i in range(1, max_passes + 1):
            output = generator.generate(features, critique)
            passed, reason = Verifier().verify(output, features)
            log_entry = {
                "pass": i,
                "output": output,
                "verified": passed,
                "critique": reason,
                "timestamp": datetime.now().isoformat()
            }
            logs.append(log_entry)
            if passed:
                break
            critique = reason
        return logs

def smoke_test():
    print("=== Smoke Test: Speech Biomarker GVU Agent ===")
    gen = Generator()
    updater = Updater()
    logs = updater.update(gen, SAMPLE_FEATURES)
    
    print("\nBefore/After (passes):")
    for log in logs:
        print(f"\nPass {log['pass']}:")
        print(f"  Output: {json.dumps(log['output'], indent=2)}")
        print(f"  Verified: {log['verified']}")
        print(f"  Critique: {log['critique']}")
    
    final = logs[-1]
    print(f"\nFinal improved output: {final['output']['risk_flag']} (score: {final['output']['risk_score']})")
    return logs

if __name__ == "__main__":
    smoke_test()
