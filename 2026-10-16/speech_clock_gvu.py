#!/usr/bin/env python3
"""
Minimal GVU prototype for speech-age-gap dementia risk screening.
Based on Hernandez et al. 2026 Speech Clocks insight: multimodal acoustic/linguistic features
estimate speech age, gap flags elevated risk. Self-improving via critique on feature weighting.
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

@dataclass
class SpeechFeatures:
    pause_ratio: float  # 0-1, higher = more pauses
    speech_rate_wpm: float  # words per minute
    lexical_diversity: float  # type-token ratio 0-1
    pitch_variability: float  # std of pitch
    age_years: int

class Generator:
    """Produces candidate risk score and speech age gap from features."""
    def generate(self, features: SpeechFeatures, weights: Dict[str, float] = None) -> Dict:
        if weights is None:
            weights = {"pause": 0.4, "rate": 0.3, "lex": 0.2, "pitch": 0.1}
        
        # Mock speech age prediction: base + weighted deviations from norms
        norm_pause = 0.15
        norm_rate = 150
        norm_lex = 0.65
        norm_pitch = 25
        
        age_offset = (
            weights["pause"] * max(0, features.pause_ratio - norm_pause) * 40 +
            weights["rate"] * max(0, (norm_rate - features.speech_rate_wpm) / 50) * 15 +
            weights["lex"] * max(0, (norm_lex - features.lexical_diversity)) * 25 +
            weights["pitch"] * max(0, (norm_pitch - features.pitch_variability) / 10) * 10
        )
        speech_age = features.age_years + age_offset
        sag = speech_age - features.age_years
        risk_score = min(1.0, max(0.0, sag / 12.0))  # normalize ~0-1, elevated if >5-6y gap
        return {
            "speech_age": round(speech_age, 1),
            "speech_age_gap": round(sag, 1),
            "risk_score": round(risk_score, 3),
            "flag": "elevated" if sag > 5 else "typical",
            "weights_used": weights
        }

class Verifier:
    """Checks against explicit criterion: for known high-risk sample, SAG should be >5 and risk>0.4; 
    weights should not ignore pause (paper insight on acoustic features)."""
    def verify(self, output: Dict, features: SpeechFeatures, expected_elevated: bool = True) -> Tuple[bool, str]:
        sag = output["speech_age_gap"]
        risk = output["risk_score"]
        weights = output["weights_used"]
        
        issues = []
        if expected_elevated and sag < 5.0:
            issues.append(f"SAG {sag} too low for elevated sample (need >5)")
        if expected_elevated and risk < 0.4:
            issues.append(f"risk {risk} under-detects (need >=0.4)")
        if weights.get("pause", 0) < 0.25:
            issues.append("pause weight too low; acoustic pauses are key in speech clocks")
        
        if not issues:
            return True, "PASS: SAG and risk meet elevated threshold; pause weighted adequately"
        return False, "FAIL: " + "; ".join(issues)

class Updater:
    """Feeds critique back: boosts pause weight if under-detecting, adjusts others."""
    def update(self, current_weights: Dict[str, float], critique: str) -> Dict[str, float]:
        new_w = current_weights.copy()
        if "SAG" in critique or "under-detects" in critique or "pause" in critique:
            new_w["pause"] = min(0.55, new_w.get("pause", 0.4) + 0.15)
            new_w["rate"] = max(0.15, new_w.get("rate", 0.3) - 0.05)
            new_w["lex"] = max(0.1, new_w.get("lex", 0.2) - 0.05)
        # normalize
        total = sum(new_w.values())
        return {k: round(v / total, 3) for k, v in new_w.items()}

def run_gvu(features: SpeechFeatures, max_passes: int = 3) -> List[Dict]:
    gen = Generator()
    ver = Verifier()
    upd = Updater()
    weights = {"pause": 0.1, "rate": 0.4, "lex": 0.3, "pitch": 0.2}  # start suboptimal
    logs = []
    
    for pass_num in range(1, max_passes + 1):
        out = gen.generate(features, weights)
        passed, reason = ver.verify(out, features)
        log_entry = {
            "pass": pass_num,
            "output": out,
            "passed": passed,
            "reason": reason,
            "weights_in": weights
        }
        logs.append(log_entry)
        if passed:
            break
        weights = upd.update(weights, reason)
    
    return logs

if __name__ == "__main__":
    # Sample: high-pause, slow rate MCI-like (elevated expected)
    sample = SpeechFeatures(
        pause_ratio=0.32,
        speech_rate_wpm=98,
        lexical_diversity=0.48,
        pitch_variability=12,
        age_years=72
    )
    results = run_gvu(sample)
    print(json.dumps(results, indent=2))
    # Before/after summary
    print("\n--- SMOKE TEST SUMMARY ---")
    print(f"Pass 1 risk: {results[0]['output']['risk_score']} flag: {results[0]['output']['flag']} | {results[0]['reason']}")
    if len(results) > 1:
        print(f"Pass {results[-1]['pass']} risk: {results[-1]['output']['risk_score']} flag: {results[-1]['output']['flag']} | {results[-1]['reason']}")
