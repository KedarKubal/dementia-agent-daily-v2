#!/usr/bin/env python3
"""
Pause-aware speech-biomarker flag — Generator / Verifier / Updater.

Core paper insight (Li et al. 2025, arXiv:2506.11119):
pause-annotated features improve ADRD classification vs lexical-only text.

This prototype is deterministic and runs without an LLM API.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import List


PAUSE_TOKEN = "[PAUSE]"

# Verifier success criteria (falsifiable)
MIN_SPEECH_RATE_SYL_PER_MIN = 90.0
MAX_MEAN_PAUSE_SEC = 0.80
MAX_PAUSE_RATIO = 0.35
MIN_WORD_COUNT = 8


@dataclass
class SpeechSample:
    text_with_pauses: str
    duration_sec: float


@dataclass
class CandidateFlag:
    risk_score: float
    speech_rate: float
    mean_pause_sec: float
    pause_ratio: float
    word_count: int
    flag: str
    rationale: str


@dataclass
class Critique:
    passed: bool
    reasons: List[str]


def _words(text: str) -> List[str]:
    cleaned = text.replace(PAUSE_TOKEN, " ")
    return [w for w in re.findall(r"[A-Za-z']+", cleaned) if w]


def _pause_count(text: str) -> int:
    return text.count(PAUSE_TOKEN)


def _approx_syllables(words: List[str]) -> int:
    total = 0
    for w in words:
        groups = re.findall(r"[aeiouyAEIOUY]+", w)
        total += max(1, len(groups))
    return total


def extract_features(sample: SpeechSample) -> dict:
    words = _words(sample.text_with_pauses)
    pauses = _pause_count(sample.text_with_pauses)
    duration = max(sample.duration_sec, 0.1)
    syllables = _approx_syllables(words)
    speech_rate = syllables / duration * 60.0
    tagged_pause_time = pauses * 0.55
    if tagged_pause_time > duration * 0.9:
        tagged_pause_time = duration * 0.4
    pause_ratio = tagged_pause_time / duration
    mean_pause = tagged_pause_time / max(pauses, 1) if pauses else 0.0
    return {
        "word_count": len(words),
        "speech_rate": speech_rate,
        "mean_pause_sec": mean_pause,
        "pause_ratio": pause_ratio,
        "pauses": pauses,
    }


def generator(sample: SpeechSample, critique: Critique | None = None) -> CandidateFlag:
    """Produce a draft risk flag. On later passes, over-weight pauses if verifier failed."""
    feats = extract_features(sample)
    rate = feats["speech_rate"]
    pause = feats["mean_pause_sec"]
    ratio = feats["pause_ratio"]
    wc = feats["word_count"]

    rate_term = max(0.0, min(1.0, (120.0 - rate) / 80.0))
    pause_term = max(0.0, min(1.0, pause / 1.2))
    ratio_term = max(0.0, min(1.0, ratio / 0.6))

    pause_weight = 0.45
    if critique and not critique.passed:
        # Updater effect: increase pause weight (paper's non-semantic insight)
        # and apply a speech-rate floor so slow speech cannot stay "typical".
        pause_weight = 0.65

    score = (
        0.25 * rate_term
        + pause_weight * (0.6 * pause_term + 0.4 * ratio_term)
        + 0.10 * (1.0 if wc < MIN_WORD_COUNT else 0.0)
    )
    if critique and not critique.passed and rate < MIN_SPEECH_RATE_SYL_PER_MIN:
        score = max(score, 0.48)
    score = max(0.0, min(1.0, score))
    flag = "elevated" if score >= 0.45 else "typical"
    rationale = (
        f"rate={rate:.1f} syl/min, mean_pause={pause:.2f}s, "
        f"pause_ratio={ratio:.2f}, words={wc}, pause_weight={pause_weight:.2f}"
    )
    return CandidateFlag(
        risk_score=round(score, 3),
        speech_rate=round(rate, 2),
        mean_pause_sec=round(pause, 3),
        pause_ratio=round(ratio, 3),
        word_count=wc,
        flag=flag,
        rationale=rationale,
    )


def verifier(candidate: CandidateFlag) -> Critique:
    """
    Pass only if the candidate is internally consistent with explicit rules:
    - If speech_rate < 90 OR mean_pause > 0.80 OR pause_ratio > 0.35 → flag must be elevated
    - Else flag must be typical
    - word_count must be reported (always true here) and risk_score in [0, 1]
    """
    reasons: List[str] = []
    impaired = (
        candidate.speech_rate < MIN_SPEECH_RATE_SYL_PER_MIN
        or candidate.mean_pause_sec > MAX_MEAN_PAUSE_SEC
        or candidate.pause_ratio > MAX_PAUSE_RATIO
    )
    expected = "elevated" if impaired else "typical"
    if candidate.flag != expected:
        reasons.append(
            f"flag '{candidate.flag}' inconsistent with features; expected '{expected}'"
        )
    if not 0.0 <= candidate.risk_score <= 1.0:
        reasons.append("risk_score out of [0, 1]")
    if impaired and candidate.risk_score < 0.45:
        reasons.append("impaired acoustics but score < 0.45; upweight pauses")
    if (not impaired) and candidate.risk_score >= 0.45:
        reasons.append("typical acoustics but score >= 0.45")
    return Critique(passed=len(reasons) == 0, reasons=reasons or ["meets criteria"])


def updater_loop(sample: SpeechSample, max_passes: int = 3) -> list[dict]:
    log: list[dict] = []
    critique: Critique | None = None
    candidate: CandidateFlag | None = None
    for i in range(1, max_passes + 1):
        candidate = generator(sample, critique)
        critique = verifier(candidate)
        log.append(
            {
                "pass": i,
                "candidate": asdict(candidate),
                "verifier": asdict(critique),
            }
        )
        if critique.passed:
            break
    return log


SAMPLE = SpeechSample(
    text_with_pauses=(
        "I went to the [PAUSE] store yesterday and [PAUSE] then I "
        "[PAUSE] forgot why I [PAUSE] was there so I [PAUSE] came home."
    ),
    duration_sec=18.0,
)


def main() -> None:
    log = updater_loop(SAMPLE, max_passes=3)
    print("=== SAMPLE ===")
    print(SAMPLE.text_with_pauses)
    print("duration_sec:", SAMPLE.duration_sec)
    print("\n=== GVU LOG ===")
    print(json.dumps(log, indent=2))
    first = log[0]["candidate"]
    last = log[-1]["candidate"]
    print("\n=== BEFORE / AFTER ===")
    print("pass1 flag/score:", first["flag"], first["risk_score"], first["rationale"])
    print("final flag/score:", last["flag"], last["risk_score"], last["rationale"])
    print("final verifier:", log[-1]["verifier"])


if __name__ == "__main__":
    main()
