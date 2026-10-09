"""GVU prototype: circadian rest-activity fragmentation desk.

Prototypes the underexploited insight in Musiek et al., JAMA Neurol 2018:
preclinical AD shows rest-activity fragmentation (higher IV, lower RA)
independent of age/sex, and total sleep time is a confounder, not the signal.

Generator drafts a progression card. Verifier rejects sleep-only flags.
Updater feeds the critique back for 3 passes.
"""

from __future__ import annotations

import json
from typing import Any


# Explicit, falsifiable success criterion (not vibes):
# PASS iff
#   1. referral_flag == True exactly when IV >= 0.75 or RA <= 0.65
#   2. primary_driver is "intradaily_variability" or "relative_amplitude"
#      (never "total_sleep_hours") when flagged; "none" when not flagged
#   3. rationale names the failing metric and its threshold
# FAIL otherwise, with a reason the updater can apply.
IV_THRESHOLD = 0.75
RA_THRESHOLD = 0.65


def generator(sample: dict[str, Any], critique: str | None = None) -> dict[str, Any]:
    """Draft a circadian progression card. First pass is intentionally naive."""
    iv = float(sample["intradaily_variability"])
    ra = float(sample["relative_amplitude"])
    sleep_h = float(sample["total_sleep_hours"])
    pid = sample["participant_id"]

    if critique is None:
        # Naive draft: flags short sleep, ignores fragmentation metrics.
        flag = sleep_h < 6.0
        return {
            "participant_id": pid,
            "referral_flag": flag,
            "primary_driver": "total_sleep_hours",
            "metrics": {
                "intradaily_variability": iv,
                "relative_amplitude": ra,
                "total_sleep_hours": sleep_h,
            },
            "rationale": (
                f"{pid} slept {sleep_h:.1f}h; flag set from total sleep alone."
            ),
            "next_step": "sleep_hygiene_leaflet" if flag else "routine_followup",
        }

    # Revised draft: apply verifier rule. Sleep is recorded, not used to flag.
    fragmented = iv >= IV_THRESHOLD or ra <= RA_THRESHOLD
    if iv >= IV_THRESHOLD:
        driver = "intradaily_variability"
        rationale = (
            f"{pid} IV {iv:.2f} >= {IV_THRESHOLD} (rest-activity fragmentation); "
            f"RA {ra:.2f} recorded; total sleep {sleep_h:.1f}h is not the driver."
        )
    elif ra <= RA_THRESHOLD:
        driver = "relative_amplitude"
        rationale = (
            f"{pid} RA {ra:.2f} <= {RA_THRESHOLD} (blunted day-night amplitude); "
            f"IV {iv:.2f} recorded; total sleep {sleep_h:.1f}h is not the driver."
        )
    else:
        driver = "none"
        rationale = (
            f"{pid} IV {iv:.2f} < {IV_THRESHOLD} and RA {ra:.2f} > {RA_THRESHOLD}; "
            f"no fragmentation flag. Sleep {sleep_h:.1f}h ignored as driver."
        )
    return {
        "participant_id": pid,
        "referral_flag": fragmented,
        "primary_driver": driver,
        "metrics": {
            "intradaily_variability": iv,
            "relative_amplitude": ra,
            "total_sleep_hours": sleep_h,
        },
        "rationale": rationale,
        "next_step": "circadian_clinic_review" if fragmented else "routine_followup",
    }


def verifier(card: dict[str, Any]) -> dict[str, Any]:
    """Check the card against the fragmentation rule. Returns pass/fail + reason."""
    metrics = card.get("metrics") or {}
    try:
        iv = float(metrics["intradaily_variability"])
        ra = float(metrics["relative_amplitude"])
    except (KeyError, TypeError, ValueError) as exc:
        return {"pass": False, "reason": f"missing metrics: {exc}"}

    expected_flag = iv >= IV_THRESHOLD or ra <= RA_THRESHOLD
    reasons: list[str] = []
    if bool(card.get("referral_flag")) != expected_flag:
        reasons.append(
            f"referral_flag {card.get('referral_flag')} != expected {expected_flag} "
            f"for IV {iv:.2f} / RA {ra:.2f}"
        )
    driver = str(card.get("primary_driver", ""))
    if driver == "total_sleep_hours":
        reasons.append(
            "primary_driver is total_sleep_hours; fragmentation rule forbids sleep-only flags"
        )
    if expected_flag and driver not in {"intradaily_variability", "relative_amplitude"}:
        reasons.append(
            "flagged card must name intradaily_variability or relative_amplitude as driver"
        )
    rationale = str(card.get("rationale", "")).lower()
    if expected_flag and "iv" not in rationale and "ra" not in rationale and "fragment" not in rationale:
        reasons.append("rationale does not name IV, RA, or fragmentation")

    if reasons:
        return {"pass": False, "reason": "; ".join(reasons)}
    return {
        "pass": True,
        "reason": "flag matches IV/RA thresholds and driver is not total sleep",
    }


def updater(sample: dict[str, Any], passes: int = 3) -> list[dict[str, Any]]:
    """Run generator -> verifier -> critique feedback for `passes` iterations."""
    if passes < 1:
        raise ValueError("passes must be >= 1")
    log: list[dict[str, Any]] = []
    critique: str | None = None
    for i in range(1, passes + 1):
        card = generator(sample, critique)
        verdict = verifier(card)
        log.append({"pass": i, "card": card, "verdict": verdict})
        if verdict["pass"]:
            critique = None
            if i >= 2:
                break
        else:
            critique = verdict["reason"]
    return log


SAMPLE = {
    "participant_id": "WASHU-CIRC-210",
    "intradaily_variability": 0.91,  # fragmented (Musiek-style preclinical pattern)
    "relative_amplitude": 0.72,  # amplitude still above threshold
    "total_sleep_hours": 5.4,  # short sleep — confounder the naive draft latches onto
}


def main() -> None:
    log = updater(SAMPLE, passes=3)
    print(json.dumps(log, indent=2))
    assert log[0]["verdict"]["pass"] is False
    assert log[-1]["verdict"]["pass"] is True
    assert log[-1]["card"]["primary_driver"] == "intradaily_variability"
    assert log[-1]["card"]["referral_flag"] is True


if __name__ == "__main__":
    main()
