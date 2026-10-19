#!/usr/bin/env python3
"""
Minimal Generator-Verifier-Updater (GVU) loop for speech-biomarker risk scoring.
Prototypes the underexploited insight from continuous multimodal speech/gait monitoring papers:
passive, privacy-aware, short-sample risk flags that improve via critique loops.
Smoke-testable offline (no external LLM required).
"""

from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

# Simulated short speech features (pause ratio, hesitation rate, lexical diversity proxy)
# Drawn from the kinds of features highlighted in SpeechDETECT / mobile ASR papers.
SAMPLE_FEATURES = {
    "pause_ratio": 0.28,          # higher = more impairment risk
    "hesitation_rate": 0.19,      # higher = risk
    "lexical_diversity": 0.42,    # lower = risk
    "mean_pause_ms": 820,
    "word_count": 48,
    "task": "picture_description_30s",
}

@dataclass
class RiskCandidate:
    risk_score: float          # 0-1
    flag: str                  # "low" | "elevated" | "high"
    rationale: str
    features_used: Dict[str, float]

def generator(features: Dict[str, Any], critique: str | None = None, pass_num: int = 1) -> RiskCandidate:
    """
    Generator: produces a candidate risk score from speech features.
    On later passes it incorporates the Verifier's critique to refine.
    """
    pause = features["pause_ratio"]
    hes = features["hesitation_rate"]
    lex = features["lexical_diversity"]

    # Base heuristic (intentionally imperfect so the loop has room to improve)
    raw = 0.45 * pause + 0.35 * hes + 0.20 * (1.0 - lex)

    if critique and "over-weight pause" in critique.lower():
        # Verifier said we over-weighted pause; rebalance
        raw = 0.30 * pause + 0.40 * hes + 0.30 * (1.0 - lex)
    if critique and "ignore task length" in critique.lower():
        # Adjust for short sample
        if features.get("word_count", 100) < 60:
            raw *= 0.92  # slightly conservative on short samples
    if critique and "add confidence" in critique.lower():
        # Tighten band
        raw = max(0.0, min(1.0, raw * 0.97 + 0.02))

    raw = max(0.0, min(1.0, raw))
    if raw < 0.35:
        flag = "low"
    elif raw < 0.55:
        flag = "elevated"
    else:
        flag = "high"

    rationale = (
        f"Pass {pass_num}: weighted combination of pause_ratio={pause:.2f}, "
        f"hesitation={hes:.2f}, (1-lex_div)={1-lex:.2f}."
    )
    if critique:
        rationale += f" Adjusted after critique: {critique[:80]}..."

    return RiskCandidate(
        risk_score=round(raw, 3),
        flag=flag,
        rationale=rationale,
        features_used={"pause_ratio": pause, "hesitation_rate": hes, "lexical_diversity": lex},
    )


def verifier(candidate: RiskCandidate, features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifier: explicit, falsifiable success criterion.
    PASS only if:
      1. risk_score is in [0,1]
      2. flag matches the score thresholds
      3. for elevated/high flags, both pause_ratio > 0.22 AND hesitation_rate > 0.12
         (avoids single-feature false positives – the core insight we want to enforce)
      4. rationale mentions at least two feature names
    """
    reasons = []
    score = candidate.risk_score
    flag = candidate.flag

    if not (0.0 <= score <= 1.0):
        reasons.append("score out of [0,1]")
    expected_flag = "low" if score < 0.35 else ("elevated" if score < 0.55 else "high")
    if flag != expected_flag:
        reasons.append(f"flag '{flag}' does not match score {score} (expected {expected_flag})")

    # Multi-feature requirement (the paper insight: single acoustic cue is noisy)
    if flag in ("elevated", "high"):
        if features["pause_ratio"] <= 0.22 or features["hesitation_rate"] <= 0.12:
            reasons.append("elevated/high flag without both pause>0.22 and hesitation>0.12 – single-feature risk")

    feat_mentions = sum(1 for k in ("pause", "hesitation", "lex") if k in candidate.rationale.lower())
    if feat_mentions < 2:
        reasons.append("rationale must mention at least two feature families")

    # Soft suggestions that drive the Updater (even on pass we can still improve)
    suggestions = []
    if features["pause_ratio"] > 0.25 and "over-weight pause" not in candidate.rationale.lower():
        suggestions.append("consider reducing over-weight on pause for short samples")
    if features.get("word_count", 100) < 60:
        suggestions.append("ignore task length / short-sample bias")
    if "confidence" not in candidate.rationale.lower():
        suggestions.append("add confidence note for clinical triage")

    passed = len(reasons) == 0
    critique = "; ".join(reasons) if reasons else "; ".join(suggestions) or "clean"
    return {
        "pass": passed,
        "reasons": reasons,
        "critique": critique,
        "suggestions": suggestions,
    }


def updater_loop(features: Dict[str, Any], max_passes: int = 3) -> List[Dict[str, Any]]:
    """Run Generator → Verifier → feedback for up to max_passes. Log every pass."""
    log = []
    critique = None
    candidate = None

    for p in range(1, max_passes + 1):
        candidate = generator(features, critique=critique, pass_num=p)
        v = verifier(candidate, features)
        entry = {
            "pass": p,
            "candidate": asdict(candidate),
            "verifier": v,
        }
        log.append(entry)
        if v["pass"] and p >= 2:  # require at least one improvement cycle
            break
        critique = v["critique"]
    return log


def main() -> None:
    print("=== GVU Speech-Biomarker Risk Prototype (Day 2026-10-19) ===\n")
    print("Sample features:", json.dumps(SAMPLE_FEATURES, indent=2))
    print()

    history = updater_loop(SAMPLE_FEATURES, max_passes=3)

    for entry in history:
        c = entry["candidate"]
        v = entry["verifier"]
        print(f"--- Pass {entry['pass']} ---")
        print(f"  Risk score : {c['risk_score']}  flag={c['flag']}")
        print(f"  Rationale  : {c['rationale']}")
        print(f"  Verifier   : {'PASS' if v['pass'] else 'FAIL'} | {v['critique']}")
        print()

    final = history[-1]["candidate"]
    print("=== Final output after self-improvement ===")
    print(json.dumps(final, indent=2))
    print("\nSmoke-test complete. Before (pass 1) vs after (final) scores logged above.")


if __name__ == "__main__":
    main()
