#!/usr/bin/env python3
"""
Minimal GVU prototype: Speech PSD (percentage of silence duration) risk flag
for early cognitive impairment detection.

Based on insight from 2025 paper combining speech digital biomarkers (PSD)
with fluid markers. Generator produces candidate risk score/flag from sample
speech features. Verifier checks against explicit criterion (elevated risk
when high PSD and multi-feature alignment). Updater refines weights/bias
over 2-3 passes.

Pure Python, no external deps. Smoke-test on one high-PSD sample.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import json


@dataclass
class SpeechSample:
    pause_ratio: float  # approx PSD proxy
    silence_duration_pct: float  # PSD
    lexical_diversity: float
    speech_rate: float
    has_fluid_marker: bool = False
    p_tau217: float = 0.0


@dataclass
class RiskOutput:
    score: float
    label: str  # typical / elevated / high
    top_feature: str
    weights: Dict[str, float]
    notes: str = ""


def generator(sample: SpeechSample, weights: Dict[str, float], bias: float = 0.0) -> RiskOutput:
    """Generate candidate risk score from features."""
    features = {
        "psd": sample.silence_duration_pct,
        "pause": sample.pause_ratio,
        "lex": 1.0 - sample.lexical_diversity,  # lower diversity = higher risk
        "rate": max(0, 1.0 - sample.speech_rate / 150),  # slower rate higher risk
        "fluid": 0.3 if sample.has_fluid_marker and sample.p_tau217 > 0.2 else 0.0,
    }
    score = bias
    for k, v in features.items():
        score += weights.get(k, 0.2) * v
    score = max(0.0, min(1.0, score))
    top = max(features, key=features.get)
    if score >= 0.7:
        label = "high"
    elif score >= 0.5:
        label = "elevated"
    else:
        label = "typical"
    return RiskOutput(score=score, label=label, top_feature=top, weights=weights.copy())


def verifier(output: RiskOutput, sample: SpeechSample) -> Tuple[bool, str]:
    """Explicit success criterion: for high-PSD sample (>=0.35), label must be
    elevated or high AND top_feature must be 'psd' or 'pause'. Otherwise fail.
    """
    high_psd = sample.silence_duration_pct >= 0.35 or sample.pause_ratio >= 0.4
    if not high_psd:
        return True, "Low-PSD sample; any reasonable label ok"
    passed = output.label in ("elevated", "high") and output.top_feature in ("psd", "pause")
    reason = (
        f"High-PSD sample requires elevated+ and PSD/pause top. "
        f"Got label={output.label}, top={output.top_feature}, score={output.score:.3f}"
    )
    return passed, reason


def updater(output: RiskOutput, critique: str, weights: Dict[str, float], bias: float) -> Tuple[Dict[str, float], float]:
    """Simple weight update: boost PSD/pause if not prioritized on high-risk."""
    new_weights = weights.copy()
    if "PSD/pause" in critique or "top=" in critique and "psd" not in critique:
        new_weights["psd"] = min(0.5, new_weights.get("psd", 0.25) + 0.08)
        new_weights["pause"] = min(0.5, new_weights.get("pause", 0.25) + 0.05)
        bias += 0.05
    return new_weights, bias


def run_gvu(sample: SpeechSample, max_passes: int = 3) -> List[Dict]:
    weights = {"psd": 0.25, "pause": 0.20, "lex": 0.20, "rate": 0.15, "fluid": 0.20}
    bias = 0.05
    logs = []
    for i in range(1, max_passes + 1):
        out = generator(sample, weights, bias)
        ok, reason = verifier(out, sample)
        logs.append({
            "pass": i,
            "score": round(out.score, 3),
            "label": out.label,
            "top_feature": out.top_feature,
            "passed": ok,
            "reason": reason,
            "weights": {k: round(v, 3) for k, v in weights.items()},
            "bias": round(bias, 3),
        })
        if ok:
            break
        weights, bias = updater(out, reason, weights, bias)
    return logs


if __name__ == "__main__":
    # High-PSD sample simulating early CI
    sample = SpeechSample(
        pause_ratio=0.45,
        silence_duration_pct=0.42,
        lexical_diversity=0.55,
        speech_rate=95.0,
        has_fluid_marker=True,
        p_tau217=0.28,
    )
    print("=== Smoke Test: High-PSD Sample ===")
    results = run_gvu(sample)
    for r in results:
        print(json.dumps(r, indent=2))
    print("\nFinal:", results[-1])
    # Write sample output
    with open("smoke_test.json", "w") as f:
        json.dump({"sample": sample.__dict__, "logs": results}, f, indent=2)
    print("Wrote smoke_test.json")
