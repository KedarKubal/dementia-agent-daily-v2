#!/usr/bin/env python3
"""
Minimal GVU prototype for adaptive multidomain lifestyle intervention dose adjustment.
Based on Brodaty et al. Nature Medicine 2025 insight: personalized online modules.
Pure-Python, no external deps. Smoke-test included.
"""

import json
from typing import Dict, List, Any

# Sample: high-risk older adult with low adherence on physical activity
SAMPLE = {
    "id": "PREV-2026-042",
    "baseline_risk_score": 0.72,  # high
    "adherence": {
        "physical_activity": 0.35,
        "nutrition": 0.68,
        "cognitive_training": 0.55,
        "mood_depression": 0.42
    },
    "progress": {
        "physical_activity": 0.2,  # low progress
        "nutrition": 0.6,
        "cognitive_training": 0.4,
        "mood_depression": 0.3
    }
}

def generator(sample: Dict, critique: str = "") -> Dict:
    """Generator: produces candidate module plan with doses (1-5)."""
    modules = ["physical_activity", "nutrition", "cognitive_training", "mood_depression"]
    plan = {"modules": {}, "total_active": 0, "rationale": "Initial draft based on risk"}
    for m in modules:
        adh = sample["adherence"].get(m, 0.5)
        prog = sample["progress"].get(m, 0.5)
        dose = 3  # default
        if critique and "reduce low adherence" in critique:
            if adh < 0.5:
                dose = 1
            elif adh < 0.6:
                dose = 2
        if critique and "drop non-progress" in critique and prog < 0.3:
            dose = 0
        if dose > 0:
            plan["modules"][m] = dose
            plan["total_active"] += 1
    if not plan["modules"]:
        plan["modules"]["nutrition"] = 2  # fallback
        plan["total_active"] = 1
    plan["rationale"] += f" | critique applied: {critique[:50]}" if critique else ""
    return plan

def verifier(plan: Dict, sample: Dict) -> Dict:
    """Verifier: checks against explicit criteria.
    Success: total_active <= 3 AND all modules with adh<0.5 have dose<=2 AND no module with prog<0.3 has dose>0.
    """
    issues = []
    total = plan.get("total_active", 0)
    if total > 3:
        issues.append("too many active modules (>3)")
    for m, dose in plan.get("modules", {}).items():
        adh = sample["adherence"].get(m, 1.0)
        prog = sample["progress"].get(m, 1.0)
        if adh < 0.5 and dose > 2:
            issues.append(f"{m} low adherence but high dose {dose}")
        if prog < 0.3 and dose > 0:
            issues.append(f"{m} low progress but still active")
    passed = len(issues) == 0
    return {
        "pass": passed,
        "reason": "; ".join(issues) if issues else "meets criteria: <=3 modules, low-adh dose<=2, no low-prog active",
        "critique": "reduce low adherence doses and drop non-progress modules" if not passed else ""
    }

def updater_loop(sample: Dict, max_passes: int = 3) -> List[Dict]:
    """Updater: feeds critique back, loops."""
    logs = []
    critique = ""
    for i in range(1, max_passes + 1):
        plan = generator(sample, critique)
        v = verifier(plan, sample)
        logs.append({
            "pass": i,
            "plan": plan,
            "verifier": v
        })
        if v["pass"]:
            break
        critique = v["critique"]
    return logs

def main():
    print("=== Smoke Test: Adaptive Lifestyle GVU ===")
    logs = updater_loop(SAMPLE)
    for entry in logs:
        print(f"\n--- Pass {entry['pass']} ---")
        print(json.dumps(entry["plan"], indent=2))
        print(f"Verifier: {'PASS' if entry['verifier']['pass'] else 'FAIL'} - {entry['verifier']['reason']}")
    final = logs[-1]
    print("\n=== Final Output ===")
    print(json.dumps(final["plan"], indent=2))
    print(f"Passes needed: {len(logs)}")
    # Save log
    with open("smoke_test_output.json", "w") as f:
        json.dump({"sample": SAMPLE, "logs": logs}, f, indent=2)
    print("Saved smoke_test_output.json")

if __name__ == "__main__":
    main()
