"""
GVU Self-Improving Agent for Adaptive Cognitive Training Dose Adjustment
Based on ACTIVE study insight: speed-of-processing training + boosters reduced dementia risk 25% over 20 years.
Minimal prototype: Generator proposes training plan, Verifier checks against adherence/progress criteria, Updater revises.
"""

from typing import Dict, Any, List
import json

class Generator:
    def __init__(self):
        self.pass_count = 0

    def generate(self, sample: Dict[str, Any], critique: str = "") -> Dict[str, Any]:
        self.pass_count += 1
        # Base plan from ACTIVE-like: speed training modules
        base_dose = 3  # sessions/week
        modules = ["speed_of_processing", "memory_strategy"]
        adherence_target = 0.8
        
        if critique:
            # Respond to critique: increase dose or drop non-adherent
            if "low adherence" in critique.lower():
                base_dose = max(2, base_dose - 1)
                modules = ["speed_of_processing"]  # focus on high-impact
            if "low progress" in critique.lower():
                base_dose += 1
                adherence_target = 0.7
        
        plan = {
            "patient_id": sample.get("patient_id", "UNKNOWN"),
            "modules": modules,
            "weekly_dose": base_dose,
            "adherence_target": adherence_target,
            "booster_sessions": 1 if base_dose >= 3 else 0,
            "pass": self.pass_count,
            "rationale": f"Adapted from critique: {critique}" if critique else "Initial ACTIVE-inspired plan"
        }
        return plan

class Verifier:
    def verify(self, plan: Dict[str, Any], sample: Dict[str, Any]) -> Dict[str, Any]:
        # Explicit success criterion: plan must address observed adherence <0.6 by reducing modules or dose, 
        # and if progress_score <0.5, increase dose or add booster. Must include speed_of_processing.
        adherence = sample.get("adherence", 1.0)
        progress = sample.get("progress_score", 1.0)
        
        issues = []
        if "speed_of_processing" not in plan["modules"]:
            issues.append("missing core speed_of_processing module")
        if adherence < 0.6 and plan["weekly_dose"] > 2:
            issues.append("low adherence not addressed by dose reduction")
        if progress < 0.5 and plan["booster_sessions"] == 0:
            issues.append("low progress not addressed by booster")
        
        passed = len(issues) == 0
        reason = "; ".join(issues) if issues else "meets criteria: speed module present, adherence/progress handled"
        return {"pass": passed, "reason": reason, "critique": reason if not passed else ""}

class Updater:
    def __init__(self, generator: Generator, verifier: Verifier):
        self.generator = generator
        self.verifier = verifier
        self.logs = []

    def run_loop(self, sample: Dict[str, Any], max_passes: int = 3) -> List[Dict[str, Any]]:
        critique = ""
        for i in range(max_passes):
            plan = self.generator.generate(sample, critique)
            result = self.verifier.verify(plan, sample)
            log_entry = {
                "pass": i + 1,
                "plan": plan,
                "verify": result
            }
            self.logs.append(log_entry)
            if result["pass"]:
                break
            critique = result["critique"]
        return self.logs

# Smoke test
if __name__ == "__main__":
    sample = {
        "patient_id": "ACTIVE-SPEED-042",
        "adherence": 0.45,
        "progress_score": 0.3,
        "age": 72
    }
    gen = Generator()
    ver = Verifier()
    upd = Updater(gen, ver)
    logs = upd.run_loop(sample)
    
    print("=== BEFORE/AFTER SMOKE TEST ===")
    for entry in logs:
        print(f"\nPass {entry['pass']}:")
        print(json.dumps(entry['plan'], indent=2))
        print(f"Verify: {entry['verify']}")
    
    # Write logs
    with open("smoke_test.txt", "w") as f:
        f.write(json.dumps(logs, indent=2))
    print("\nLogs written to smoke_test.txt")
