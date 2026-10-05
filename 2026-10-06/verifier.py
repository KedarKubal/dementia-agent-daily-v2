"""Verifier: falsifiable dual-gate success criterion.

PASS iff all of:
1. label in {stable, indeterminate_needs_plasma, higher_risk_progressor}
2. higher_risk_progressor only if speech_slope_z >= 1.0 AND plasma == positive
3. at least 2 of {idea_density, pronoun_ratio, content_word_ratio} cited with numbers
4. if plasma is missing/not_collected, label must be indeterminate_needs_plasma
"""

from __future__ import annotations

ALLOWED = {"stable", "indeterminate_needs_plasma", "higher_risk_progressor"}
FEATURE_KEYS = ("idea_density", "pronoun_ratio", "content_word_ratio")


def verify(case: dict, draft: dict) -> dict:
    reasons: list[str] = []
    label = draft.get("label")
    plasma = case.get("plasma_ptau217_status")
    speech_z = float(case["speech_slope_z"])
    cited = draft.get("features_cited") or {}

    if label not in ALLOWED:
        reasons.append(f"label {label!r} not in allowed set")

    numeric_cited = [
        k for k in FEATURE_KEYS if isinstance(cited.get(k), (int, float))
    ]
    if len(numeric_cited) < 2:
        reasons.append(
            "need >=2 numeric linguistic features "
            f"(idea_density, pronoun_ratio, content_word_ratio); got {numeric_cited}"
        )

    plasma_missing = plasma not in ("positive", "negative")
    if plasma_missing and label != "indeterminate_needs_plasma":
        reasons.append(
            "plasma p-tau217 missing; label must be indeterminate_needs_plasma, "
            f"not {label}"
        )

    if label == "higher_risk_progressor":
        if speech_z < 1.0 or plasma != "positive":
            reasons.append(
                "higher_risk_progressor requires speech_slope_z>=1.0 AND "
                "plasma_ptau217_status==positive"
            )

    if label == "stable" and plasma_missing:
        reasons.append("stable is not allowed while plasma status is unknown")

    ok = not reasons
    return {
        "pass": ok,
        "reasons": reasons or ["dual gate and feature citations satisfied"],
    }
