"""Generator: draft a progression desk note from speech slope + optional plasma.

Core insight (Lee et al. 2026 SpeechDx; Lima et al. 2025 linguistic features):
amyloid/plasma positivity alone does not predict who declines, and a speech
slope is not a progressor label until both gates close.
"""

from __future__ import annotations

REQUIRED_FEATURES = ("idea_density", "pronoun_ratio", "content_word_ratio")


def generate(case: dict, critique: str | None = None) -> dict:
    speech_z = float(case["speech_slope_z"])
    plasma = case.get("plasma_ptau217_status")  # positive | negative | None
    features = case.get("linguistic_features") or {}

    # Pass 1 (no critique): the common product mistake — speech slope alone.
    if not critique:
        label = "higher_risk_progressor" if speech_z >= 1.0 else "stable"
        return {
            "case_id": case["case_id"],
            "label": label,
            "speech_slope_z": speech_z,
            "plasma_ptau217_status": plasma if plasma else "not_collected",
            "features_cited": {},
            "rationale": (
                f"Speech slope z={speech_z:.2f} alone "
                f"{'crosses' if speech_z >= 1.0 else 'does not cross'} 1.0; "
                "emitted a risk band without a plasma gate."
            ),
            "next_step": "memory_clinic_referral" if speech_z >= 1.0 else "routine_followup",
        }

    cited = {k: features[k] for k in REQUIRED_FEATURES if k in features}
    missing_plasma = plasma not in ("positive", "negative")
    if missing_plasma:
        label = "indeterminate_needs_plasma"
        next_step = "collect_plasma_ptau217_then_rescore"
        rationale = (
            "Speech slope is informative but plasma p-tau217 is missing; "
            "refusing a progressor band until the second gate closes."
        )
    elif speech_z >= 1.0 and plasma == "positive":
        label = "higher_risk_progressor"
        next_step = "memory_clinic_referral"
        rationale = (
            "Both gates closed: speech_slope_z>=1.0 and plasma p-tau217 positive."
        )
    else:
        label = "stable"
        next_step = "routine_followup"
        rationale = "Dual gate did not meet progressor rule."

    return {
        "case_id": case["case_id"],
        "label": label,
        "speech_slope_z": speech_z,
        "plasma_ptau217_status": plasma if plasma else "not_collected",
        "features_cited": cited,
        "rationale": rationale,
        "next_step": next_step,
    }
