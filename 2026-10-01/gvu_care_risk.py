#!/usr/bin/env python3
"""
Day 2026-10-01 — Generator–Verifier–Updater prototype.

Opportunity: wearable dyad proximity + caregiver movement as a
calibrated caregiver-burden / wandering-risk score (Chen 2023;
Kim 2025 location-tracking review).

Generator drafts a risk packet.
Verifier checks an explicit, falsifiable criterion.
Updater feeds the critique back for 3 passes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


SAMPLE = {
    "patient_id": "demo-dyad-01",
    "delta_proximity_hours_per_day": 1.8,
    "delta_cg_movement_steps_pct": 22.0,
    "delta_pwd_movement_steps_pct": -8.0,
    "night_exits": 3,
    "geo_fence_breaches_7d": 2,
    "adl_decline_points": 2,
}

ALLOWED_NUDGES = {
    "schedule_respite",
    "tighten_geo_fence",
    "night_check_protocol",
    "ot_adl_review",
    "no_action_monitor",
}


@dataclass
class RiskPacket:
    burden_risk: float
    wandering_flag: bool
    primary_driver: str
    nudge: str
    rationale: str
    pass_index: int


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def generate(features: dict[str, Any], critique: str | None, pass_index: int) -> RiskPacket:
    prox = float(features["delta_proximity_hours_per_day"])
    cg_move = float(features["delta_cg_movement_steps_pct"])
    pwd_move = float(features["delta_pwd_movement_steps_pct"])
    night = int(features["night_exits"])
    breaches = int(features["geo_fence_breaches_7d"])
    adl = int(features["adl_decline_points"])

    if pass_index == 1 and not critique:
        burden = 0.20 * prox + 0.005 * cg_move + 0.05 * adl
        wandering = breaches >= 4
        driver = "adl"
        nudge = "no_action_monitor"
        rationale = "first-pass equal-weight draft; proximity underweighted"
    else:
        burden = 0.22 * prox + 0.012 * cg_move + 0.04 * max(0, -pwd_move) + 0.08 * adl
        if critique and "burden_risk too low" in critique:
            burden += 0.18
        wandering = (night + breaches) >= 3
        driver = "proximity" if prox >= 1.0 else ("movement" if cg_move >= 15 else "adl")
        if wandering:
            nudge = "night_check_protocol" if night >= 2 else "tighten_geo_fence"
        elif burden >= 0.55:
            nudge = "schedule_respite"
        elif adl >= 2:
            nudge = "ot_adl_review"
        else:
            nudge = "no_action_monitor"
        rationale = f"revised after critique: {critique or 'none'}"

    return RiskPacket(
        burden_risk=round(clamp(burden), 3),
        wandering_flag=bool(wandering),
        primary_driver=driver,
        nudge=nudge,
        rationale=rationale,
        pass_index=pass_index,
    )


def verify(packet: RiskPacket, features: dict[str, Any]) -> tuple[bool, str]:
    reasons: list[str] = []
    if not (0.0 <= packet.burden_risk <= 1.0):
        reasons.append("burden_risk out of [0,1]")
    prox = float(features["delta_proximity_hours_per_day"])
    cg_move = float(features["delta_cg_movement_steps_pct"])
    if prox >= 1.0 and cg_move >= 15.0 and packet.burden_risk < 0.55:
        reasons.append(
            f"burden_risk too low ({packet.burden_risk}) given proximity {prox}h "
            f"and CG movement +{cg_move}% (Chen 2023 heuristic requires >=0.55)"
        )
    night = int(features["night_exits"])
    breaches = int(features["geo_fence_breaches_7d"])
    if night + breaches >= 3 and not packet.wandering_flag:
        reasons.append(
            f"wandering_flag must be True when night_exits+breaches="
            f"{night + breaches} >= 3"
        )
    if packet.nudge not in ALLOWED_NUDGES:
        reasons.append(f"nudge '{packet.nudge}' not in allowed set")
    if packet.wandering_flag and packet.nudge not in {
        "tighten_geo_fence",
        "night_check_protocol",
    }:
        reasons.append("wandering_flag True but nudge is not a safety action")
    if reasons:
        return False, "; ".join(reasons)
    return True, "all success criteria met"


def run_gvu(features: dict[str, Any], max_passes: int = 3) -> list[dict[str, Any]]:
    log: list[dict[str, Any]] = []
    critique: str | None = None
    for i in range(1, max_passes + 1):
        packet = generate(features, critique, i)
        ok, reason = verify(packet, features)
        log.append({"pass": i, "packet": asdict(packet), "verified": ok, "critique": reason})
        if ok:
            break
        critique = reason
    return log


def main() -> None:
    log = run_gvu(SAMPLE, max_passes=3)
    print("=== SAMPLE FEATURES ===")
    print(json.dumps(SAMPLE, indent=2))
    print("\n=== GVU PASSES ===")
    print(json.dumps(log, indent=2))
    first = log[0]["packet"]
    last = log[-1]["packet"]
    print("\n=== BEFORE / AFTER ===")
    print(
        f"pass1 burden_risk={first['burden_risk']} "
        f"wandering={first['wandering_flag']} nudge={first['nudge']}"
    )
    print(
        f"pass{last['pass_index']} burden_risk={last['burden_risk']} "
        f"wandering={last['wandering_flag']} nudge={last['nudge']} "
        f"verified={log[-1]['verified']}"
    )


if __name__ == "__main__":
    main()
