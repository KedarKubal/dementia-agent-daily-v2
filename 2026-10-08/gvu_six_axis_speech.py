#!/usr/bin/env python3
"""GVU loop: six-axis conversational speech biomarker card.

Opportunity (2026-10-08): Addlesee et al. arXiv:2502.10896 scored six
named speech biomarkers (grammar, pragmatics, anomia, turn-taking,
pronunciation, prosody) plus a composite that beat any single axis vs MMSE.
This prototype refuses a single black-box flag until at least four axes
are populated and the composite is the mean of measured axes only.

Not a clinical device. Heuristic demo only.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

AXES = (
    "altered_grammar",
    "pragmatic_impairment",
    "anomia",
    "disrupted_turn_taking",
    "slurred_pronunciation",
    "prosody_change",
)
MIN_AXES = 4
COMPOSITE_ELEVATED = 0.45


def generator(sample: dict[str, Any], critique: str | None = None) -> dict[str, Any]:
    """Draft a speech-biomarker card. First pass is intentionally incomplete."""
    axes_in = sample.get("axes", {})
    if critique is None:
        loudest = max(axes_in, key=axes_in.get) if axes_in else "anomia"
        return {
            "session_id": sample["session_id"],
            "axes_reported": {loudest: round(float(axes_in.get(loudest, 0.0)), 3)},
            "n_axes": 1,
            "composite": None,
            "label": "black_box_impaired" if axes_in.get(loudest, 0) >= 0.5 else "black_box_ok",
            "clinician_note": "Single-axis flag only; other conversational markers ignored.",
        }

    reported = {name: round(float(axes_in[name]), 3) for name in AXES if name in axes_in}
    n = len(reported)
    composite = round(sum(reported.values()) / n, 3) if n else None
    if n < MIN_AXES or composite is None:
        label = "insufficient_axes"
        note = f"Need >= {MIN_AXES} named axes before a composite referral."
    elif composite >= COMPOSITE_ELEVATED:
        label = "elevated_composite"
        note = "Composite of measured axes exceeds 0.45; review individual axes, do not collapse to one score."
    else:
        label = "composite_within_range"
        note = "Composite within range; keep the six-axis card for longitudinal comparison."
    return {
        "session_id": sample["session_id"],
        "axes_reported": reported,
        "n_axes": n,
        "composite": composite,
        "label": label,
        "clinician_note": note,
    }


def verifier(card: dict[str, Any]) -> dict[str, Any]:
    """Falsifiable success criterion from the paper's panel design."""
    reasons: list[str] = []
    axes = card.get("axes_reported") or {}
    unknown = [k for k in axes if k not in AXES]
    if unknown:
        reasons.append(f"unknown axes: {unknown}")
    if card.get("n_axes", 0) < MIN_AXES:
        reasons.append(f"n_axes {card.get('n_axes')} < {MIN_AXES}")
    if card.get("composite") is None:
        reasons.append("composite missing")
    if str(card.get("label", "")).startswith("black_box"):
        reasons.append("black-box label not allowed; panel must stay axis-visible")
    expected = None
    if axes and card.get("composite") is not None:
        expected = round(sum(axes.values()) / len(axes), 3)
        if abs(expected - float(card["composite"])) > 0.001:
            reasons.append(f"composite {card['composite']} != mean {expected}")
    ok = not reasons
    return {"pass": ok, "reasons": reasons or ["six-axis card meets criterion"], "expected_composite": expected}


def updater(sample: dict[str, Any], passes: int = 3) -> list[dict[str, Any]]:
    log: list[dict[str, Any]] = []
    critique: str | None = None
    card: dict[str, Any] = {}
    for i in range(1, passes + 1):
        card = generator(sample, critique)
        verdict = verifier(card)
        log.append({"pass": i, "card": deepcopy(card), "verdict": verdict})
        if verdict["pass"]:
            break
        critique = "; ".join(verdict["reasons"])
    return log


SAMPLE = {
    "session_id": "ROBOT-CONV-088",
    "axes": {
        "altered_grammar": 0.62,
        "pragmatic_impairment": 0.41,
        "anomia": 0.70,
        "disrupted_turn_taking": 0.55,
        "slurred_pronunciation": 0.22,
        "prosody_change": 0.48,
    },
}


def main() -> None:
    log = updater(SAMPLE)
    print(json.dumps({"sample": SAMPLE["session_id"], "log": log}, indent=2))


if __name__ == "__main__":
    main()
