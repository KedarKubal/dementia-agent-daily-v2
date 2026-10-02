"""Dual-task gait-cost flag with a Generator-Verifier-Updater loop.

Prototypes the underexploited insight in Montero-Odasso et al., JAMA Neurol 2017:
high dual-task gait cost (not slow single-task speed alone) marks MCI patients
who progress to dementia. The Verifier rejects a flag that ignores that split.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from typing import Any


SINGLE_TASK_SLOW_MPS = 0.8
HIGH_COST_FRACTION = 0.20


@dataclass
class GaitSample:
    participant_id: str
    single_task_mps: float
    dual_task_mps: float
    probe: str = "count_backward"


@dataclass
class Flag:
    participant_id: str
    gait_cost: float
    single_task_mps: float
    dual_task_mps: float
    progression_flag: bool
    rationale: str
    next_step: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def gait_cost(single_task_mps: float, dual_task_mps: float) -> float:
    if single_task_mps <= 0:
        raise ValueError("single_task_mps must be positive")
    return (single_task_mps - dual_task_mps) / single_task_mps


def generator(sample: GaitSample, critique: str | None = None) -> Flag:
    cost = gait_cost(sample.single_task_mps, sample.dual_task_mps)
    slow_single = sample.single_task_mps < SINGLE_TASK_SLOW_MPS
    high_cost = cost >= HIGH_COST_FRACTION

    if critique is None:
        flag = slow_single or high_cost
        rationale = (
            f"Pass-1 heuristic: flag if single-task < {SINGLE_TASK_SLOW_MPS} m/s "
            f"OR cost >= {HIGH_COST_FRACTION:.0%}. cost={cost:.3f}."
        )
        next_step = "clinic_gait_screen" if flag else "routine_followup"
    else:
        flag = high_cost
        rationale = (
            f"Revised after critique: single-task speed alone does not flag. "
            f"cost={cost:.3f} vs threshold {HIGH_COST_FRACTION:.0%} "
            f"on probe={sample.probe}. single={sample.single_task_mps:.2f} m/s "
            f"(slow_single={slow_single}, ignored)."
        )
        next_step = (
            "order_biomarker_and_prevention_plan"
            if flag
            else "routine_followup_no_dual_task_cost"
        )

    return Flag(
        participant_id=sample.participant_id,
        gait_cost=round(cost, 4),
        single_task_mps=sample.single_task_mps,
        dual_task_mps=sample.dual_task_mps,
        progression_flag=flag,
        rationale=rationale,
        next_step=next_step,
    )


def verifier(sample: GaitSample, flag: Flag) -> dict[str, Any]:
    expected_cost = gait_cost(sample.single_task_mps, sample.dual_task_mps)
    reasons: list[str] = []
    if abs(flag.gait_cost - expected_cost) > 0.01:
        reasons.append("gait_cost arithmetic mismatch")
    should_flag = expected_cost >= HIGH_COST_FRACTION
    if flag.progression_flag != should_flag:
        reasons.append(
            f"flag={flag.progression_flag} but cost {expected_cost:.3f} "
            f"{'meets' if should_flag else 'does not meet'} {HIGH_COST_FRACTION:.0%} rule; "
            "single-task slowness must not decide the flag"
        )
    if should_flag and "biomarker" not in flag.next_step:
        reasons.append("flagged case must recommend biomarker / prevention follow-up")
    if not should_flag and "routine_followup" not in flag.next_step:
        reasons.append("non-flagged case must stay on routine follow-up")
    return {"pass": not reasons, "reasons": reasons or ["ok"]}


def updater(sample: GaitSample, passes: int = 3) -> list[dict[str, Any]]:
    log: list[dict[str, Any]] = []
    critique: str | None = None
    for i in range(1, passes + 1):
        draft = generator(sample, critique)
        verdict = verifier(sample, draft)
        log.append({"pass": i, "output": draft.to_dict(), "verdict": verdict})
        if verdict["pass"]:
            break
        critique = "; ".join(verdict["reasons"])
    return log


def main() -> None:
    sample = GaitSample(
        participant_id="MCI-014",
        single_task_mps=0.72,
        dual_task_mps=0.66,
        probe="count_backward",
    )
    trace = updater(sample, passes=3)
    print(json.dumps({"sample": asdict(sample), "trace": trace}, indent=2))


if __name__ == "__main__":
    main()
