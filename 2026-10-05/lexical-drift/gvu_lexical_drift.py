#!/usr/bin/env python3
"""Within-person lexical-drift flag — Generator / Verifier / Updater.

Prototypes the underexploited slice of Cho et al. 2022 (Alzheimer's & Dementia,
DOI 10.1002/alz.061835): MCI/mild-AD picture descriptions drift toward higher
word frequency, higher familiarity, more partial words, and slower articulation
*within the same speaker*. Cross-sectional pause rate is not the signal.

No third-party dependencies. Not a clinical device.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


SUCCESS = {
    "min_baseline_n": 3,
    "freq_delta_min": 0.15,
    "familiarity_delta_min": 0.10,
    "required_features": (
        "lexical_frequency_delta",
        "familiarity_delta",
        "partial_word_delta",
    ),
    "banned_sole_drivers": ("pause_rate", "info_unit_count"),
}


@dataclass
class Candidate:
    speaker_id: str
    baseline_n: int
    features_used: list[str]
    lexical_frequency_delta: float
    familiarity_delta: float
    partial_word_delta: float
    pause_rate: float
    referral_flag: bool
    rationale: str
    next_step: str
    pass_index: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Critique:
    passed: bool
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _should_flag(sample: dict[str, Any]) -> bool:
    return (
        sample["baseline_n"] >= SUCCESS["min_baseline_n"]
        and sample["lexical_frequency_delta"] >= SUCCESS["freq_delta_min"]
        and sample["familiarity_delta"] >= SUCCESS["familiarity_delta_min"]
        and sample["partial_word_delta"] > 0
    )


def generate(sample: dict[str, Any], critique: Critique | None = None, pass_index: int = 1) -> Candidate:
    """Generator. Pass 1 deliberately emits the weak pause-only draft."""
    flag = _should_flag(sample)
    if critique is None:
        return Candidate(
            speaker_id=sample["speaker_id"],
            baseline_n=sample["baseline_n"],
            features_used=["pause_rate"],
            lexical_frequency_delta=0.0,
            familiarity_delta=0.0,
            partial_word_delta=0.0,
            pause_rate=sample["pause_rate"],
            referral_flag=sample["pause_rate"] > 0.25,
            rationale="Elevated pause rate versus a population cutoff.",
            next_step="clinician_review" if sample["pause_rate"] > 0.25 else "continue_baseline",
            pass_index=pass_index,
        )

    rationale = (
        "Within-person lexical drift: higher-frequency and more familiar words "
        "plus more partial words versus this speaker's own baseline."
        if flag
        else "Lexical frequency, familiarity, and partial-word deltas remain inside this speaker's personal baseline."
    )
    return Candidate(
        speaker_id=sample["speaker_id"],
        baseline_n=sample["baseline_n"],
        features_used=list(SUCCESS["required_features"]),
        lexical_frequency_delta=sample["lexical_frequency_delta"],
        familiarity_delta=sample["familiarity_delta"],
        partial_word_delta=sample["partial_word_delta"],
        pause_rate=sample["pause_rate"],
        referral_flag=flag,
        rationale=rationale,
        next_step="clinician_review" if flag else "continue_baseline",
        pass_index=pass_index,
    )


def verify(candidate: Candidate, sample: dict[str, Any]) -> Critique:
    """Verifier. Returns pass/fail plus every violated rule."""
    reasons: list[str] = []
    expected = _should_flag(sample)
    used = set(candidate.features_used)

    if candidate.baseline_n < SUCCESS["min_baseline_n"]:
        reasons.append(f"baseline_n {candidate.baseline_n} < {SUCCESS['min_baseline_n']}")
    missing = [f for f in SUCCESS["required_features"] if f not in used]
    if missing:
        reasons.append(f"missing deciding features: {missing}")
    if used <= set(SUCCESS["banned_sole_drivers"]):
        reasons.append("sole driver is a banned prior-day feature (pause_rate or info_unit_count)")
    if candidate.referral_flag != expected:
        reasons.append(f"referral_flag {candidate.referral_flag} != expected {expected}")
    if expected and "within-person lexical drift" not in candidate.rationale.lower():
        reasons.append("flagged rationale must name 'within-person lexical drift'")
    if not expected and "personal baseline" not in candidate.rationale.lower():
        reasons.append("negative rationale must name 'personal baseline'")
    expected_step = "clinician_review" if expected else "continue_baseline"
    if candidate.next_step != expected_step:
        reasons.append(f"next_step {candidate.next_step} != {expected_step}")
    if not missing:
        if abs(candidate.lexical_frequency_delta - sample["lexical_frequency_delta"]) > 1e-6:
            reasons.append("lexical_frequency_delta does not match sample")
        if abs(candidate.familiarity_delta - sample["familiarity_delta"]) > 1e-6:
            reasons.append("familiarity_delta does not match sample")
        if abs(candidate.partial_word_delta - sample["partial_word_delta"]) > 1e-6:
            reasons.append("partial_word_delta does not match sample")
    return Critique(passed=not reasons, reasons=reasons)


def update_loop(sample: dict[str, Any], max_passes: int = 3) -> list[dict[str, Any]]:
    """Updater. Feeds critique back; stops early on pass. Logs every pass."""
    log: list[dict[str, Any]] = []
    critique: Critique | None = None
    for i in range(1, max_passes + 1):
        candidate = generate(sample, critique, pass_index=i)
        critique = verify(candidate, sample)
        log.append({"candidate": candidate.to_dict(), "critique": critique.to_dict()})
        if critique.passed:
            break
    return log


SAMPLE = {
    "speaker_id": "MCI-LEX-118",
    "baseline_n": 4,
    "lexical_frequency_delta": 0.22,
    "familiarity_delta": 0.14,
    "partial_word_delta": 0.06,
    "pause_rate": 0.31,
    "info_unit_count": 11,
}


def main() -> None:
    log = update_loop(SAMPLE)
    print(json.dumps({"sample": SAMPLE, "passes": log}, indent=2))
    assert log[0]["critique"]["passed"] is False
    assert log[-1]["critique"]["passed"] is True
    assert log[-1]["candidate"]["referral_flag"] is True
    assert "lexical_frequency_delta" in log[-1]["candidate"]["features_used"]


if __name__ == "__main__":
    main()
