#!/usr/bin/env python3
"""
Minimal GVU prototype for passive speech-biomarker early dementia risk flag.
Insight from foundation speech models on spontaneous/ambient speech (e.g. Whisper embeddings): continuous low-burden monitoring can flag risk without structured tasks.
Generator drafts risk; Verifier checks explicit criteria on features/score/flag for labeled-like sample; Updater revises weights.
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, List

@dataclass
class Candidate:
    risk_score: float
    top_features: List[str]
    flag: str
    rationale: str

def generator(sample: Dict[str, float], critique: str = "", boost: float = 0.0) -> Candidate:
    pause = sample.get("pause_ratio", 0.2)
    rate = sample.get("speech_rate", 120)
    lex = sample.get("lexical_diversity", 0.6)
    emb = sample.get("embedding_distance", 0.3)
    
    # Weighted score + adaptive boost from critique
    score = (pause * 0.45) + ((150 - rate) / 200 * 0.25) + ((0.85 - lex) * 0.2) + (emb * 0.1) + boost
    score = max(0.0, min(1.0, score))
    
    if score > 0.65:
        flag = "HIGH"
    elif score > 0.4:
        flag = "ELEVATED"
    else:
        flag = "LOW"
    
    features = []
    if pause > 0.25:
        features.append("pause_ratio")
    if rate < 110:
        features.append("speech_rate")
    if lex < 0.5:
        features.append("lexical_diversity")
    if emb > 0.45:
        features.append("embedding_distance")
    if not features:
        features = ["baseline_features"]
    
    rationale = f"Score {score:.3f} from {', '.join(features)}"
    if boost > 0:
        rationale += f" (boosted +{boost:.2f} after critique)"
    
    return Candidate(score, features[:3], flag, rationale)

def verifier(cand: Candidate, sample: Dict[str, float]) -> Dict[str, Any]:
    """Success criterion (falsifiable): on high-pause (>0.35) or low-lex (<0.4) sample, require score >= 0.48, flag != LOW, and pause_ratio or lexical_diversity in top_features."""
    pause = sample.get("pause_ratio", 0)
    lex = sample.get("lexical_diversity", 1.0)
    risky = pause > 0.35 or lex < 0.40
    
    passed = True
    reasons = []
    if risky:
        if cand.risk_score < 0.48:
            passed = False
            reasons.append(f"score {cand.risk_score:.3f} < 0.48")
        if cand.flag == "LOW":
            passed = False
            reasons.append("flag LOW on risky sample")
        if "pause_ratio" not in cand.top_features and pause > 0.3:
            passed = False
            reasons.append("missing pause_ratio feature")
        if "lexical_diversity" not in cand.top_features and lex < 0.45:
            passed = False
            reasons.append("missing lexical_diversity feature")
    if not reasons:
        reasons.append("criteria satisfied")
    critique = "; ".join(reasons) if not passed else ""
    return {"pass": passed, "reason": "; ".join(reasons), "critique": critique}

def run_gvu(sample: Dict[str, float], passes: int = 3) -> List[Dict]:
    logs = []
    boost = 0.0
    critique = ""
    for i in range(1, passes + 1):
        cand = generator(sample, critique, boost)
        v = verifier(cand, sample)
        logs.append({"pass": i, "candidate": asdict(cand), "verifier": v})
        if v["pass"]:
            break
        # Updater: increase boost for next generator call
        boost += 0.08
        critique = v["critique"]
    return logs

if __name__ == "__main__":
    sample = {"pause_ratio": 0.45, "speech_rate": 78, "lexical_diversity": 0.32, "embedding_distance": 0.62}
    print("=== Smoke-test: high-risk ambient speech sample ===")
    logs = run_gvu(sample)
    for e in logs:
        c = e["candidate"]
        print(f"Pass {e['pass']}: score={c['risk_score']:.3f} flag={c['flag']} features={c['top_features']}")
        print(f"  Verifier pass={e['verifier']['pass']} | {e['verifier']['reason']}")
    print("\n=== Final revised output ===")
    print(json.dumps(logs[-1]["candidate"], indent=2))
