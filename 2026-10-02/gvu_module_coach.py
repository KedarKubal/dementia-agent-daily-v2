"""GVU coach for a closed-loop multidomain dementia-prevention plan.

Prototype of the underexploited insight in Brodaty et al., Nature Medicine 2025
(Maintain Your Brain): participants were eligible for 2-4 modules, but the
coaching schedule was not a closed loop. This agent drafts a weekly module
plan, verifies it against explicit rules, and revises for 3 passes.

Not a medical device. Synthetic inputs only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MODULES = ("physical_activity", "nutrition", "cognitive_activity", "mood")
MAX_ACTIVE = 2
ADHERENCE_FLOOR = 0.60
DOSE_MIN = 2
DOSE_MAX = 5


@dataclass
class PersonWeek:
    """One synthetic week of risk factors, adherence, and a cheap cognitive proxy."""

    person_id: str
    risk_factors: dict[str, float]  # module -> 0..1 risk
    adherence: dict[str, float]  # module -> 0..1 last-week completion
    cognitive_proxy_delta: float  # negative means decline on a z-like proxy


@dataclass
class Plan:
    active: dict[str, int]  # module -> sessions/week
    dropped: list[str] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"active": dict(self.active), "dropped": list(self.dropped), "rationale": self.rationale}


def generator(person: PersonWeek, critique: str | None = None) -> Plan:
    """Draft a weekly plan. Critique from the verifier tightens the next draft."""
    ranked = sorted(person.risk_factors.items(), key=lambda kv: kv[1], reverse=True)
    critique_l = (critique or "").lower()
    active: dict[str, int] = {}
    dropped: list[str] = []

    # Pass 1 tends to overload: top 3 risks, dose scaled by risk, ignore adherence.
    take = 3
    if "overloaded" in critique_l or "max_active" in critique_l:
        take = MAX_ACTIVE
    if "adherence" in critique_l:
        take = MAX_ACTIVE

    for name, risk in ranked:
        if person.adherence.get(name, 1.0) < ADHERENCE_FLOOR and (
            "adherence" in critique_l or "drop" in critique_l
        ):
            dropped.append(name)
            continue
        if len(active) >= take:
            continue
        dose = DOSE_MIN + round(risk * (DOSE_MAX - DOSE_MIN))
        if "dose" in critique_l and person.adherence.get(name, 1.0) < 0.75:
            dose = max(DOSE_MIN, dose - 1)
        if person.cognitive_proxy_delta < 0 and name == "cognitive_activity" and "proxy" in critique_l:
            dose = min(DOSE_MAX, dose + 1)
        active[name] = int(dose)

    top = ranked[0][0]
    if "uncovered_top_risk" in critique_l and top not in active:
        active[top] = DOSE_MIN
        if top in dropped:
            dropped.remove(top)

    rationale = "risk-ranked draft" if not critique else f"revised after: {critique}"
    return Plan(active=active, dropped=dropped, rationale=rationale)


def verifier(person: PersonWeek, plan: Plan) -> dict[str, Any]:
    """Falsifiable checks. Fail closed with a single primary reason code."""
    reasons: list[str] = []
    if len(plan.active) > MAX_ACTIVE:
        reasons.append("overloaded:max_active")
    if len(plan.active) == 0:
        reasons.append("empty_plan")
    top = max(person.risk_factors, key=person.risk_factors.get)
    if top not in plan.active and person.adherence.get(top, 1.0) >= ADHERENCE_FLOOR:
        reasons.append("uncovered_top_risk")
    for name, dose in plan.active.items():
        if not DOSE_MIN <= dose <= DOSE_MAX:
            reasons.append("dose_out_of_range")
        if person.adherence.get(name, 1.0) < ADHERENCE_FLOOR:
            reasons.append(f"adherence_drop:{name}")
    if person.cognitive_proxy_delta < -0.05 and "cognitive_activity" in plan.active:
        if plan.active["cognitive_activity"] < 4:
            reasons.append("proxy_needs_more_cognitive_dose")
    passed = len(reasons) == 0
    return {"pass": passed, "reasons": reasons, "primary": reasons[0] if reasons else "ok"}


def updater(person: PersonWeek, passes: int = 3) -> list[dict[str, Any]]:
    """Run generator -> verifier -> critique feedback for `passes` iterations."""
    log: list[dict[str, Any]] = []
    critique: str | None = None
    for i in range(1, passes + 1):
        plan = generator(person, critique)
        verdict = verifier(person, plan)
        log.append({"pass": i, "plan": plan.to_dict(), "verdict": verdict})
        if verdict["pass"]:
            break
        critique = ";".join(verdict["reasons"])
    return log


def smoke() -> list[dict[str, Any]]:
    sample = PersonWeek(
        person_id="synth-001",
        risk_factors={
            "physical_activity": 0.82,
            "nutrition": 0.71,
            "cognitive_activity": 0.64,
            "mood": 0.40,
        },
        adherence={
            "physical_activity": 0.45,
            "nutrition": 0.80,
            "cognitive_activity": 0.70,
            "mood": 0.90,
        },
        cognitive_proxy_delta=-0.12,
    )
    return updater(sample, passes=3)


if __name__ == "__main__":
    import json

    print(json.dumps(smoke(), indent=2))
