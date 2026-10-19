#!/usr/bin/env python3
"""
GVU Loop Prototype: Adaptive Multidomain Lifestyle Coach for Dementia Prevention
Based on Brodaty et al. 2025 Nature Medicine online intervention insight:
Personalize modules (physical, nutrition, cognitive, mental health) by adherence & progress.
Self-improving via Generator-Verifier-Updater loop.
"""

import json
from typing import Dict, Any, List

class Generator:
    def generate(self, user_profile: Dict[str, Any], critique: str = None) -> Dict[str, Any]:
        base = {
            "modules": ["physical_activity", "nutrition", "cognitive_training", "mental_health"],
            "doses": {"physical_activity": 3, "nutrition": 2, "cognitive_training": 4, "mental_health": 1},
            "adherence_weights": {"physical_activity": 0.5, "nutrition": 0.75, "cognitive_training": 0.45, "mental_health": 0.85},
            "next_nudge": "Continue all modules at current doses."
        }
        if critique:
            if "total dose" in critique.lower():
                for m in list(base["doses"]):
                    base["doses"][m] = max(1, base["doses"][m] - 1)
                base["next_nudge"] = "Reduced doses to meet total budget."
            if "weighted adherence" in critique.lower() or "low adherence" in critique.lower():
                base["doses"]["physical_activity"] = max(1, base["doses"]["physical_activity"] - 1)
                base["next_nudge"] = "Cut low-adherence physical dose."
            if "low progress" in critique.lower() or "boost cognitive" in critique.lower():
                base["doses"]["cognitive_training"] = min(5, base["doses"]["cognitive_training"] + 1)
                base["next_nudge"] = "Boosted cognitive training on low progress."
        return base

class Verifier:
    def verify(self, output: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        total_dose = sum(output["doses"].values())
        num_modules = len(output["modules"])
        weighted = sum(output["adherence_weights"].get(m, 0.5) * output["doses"].get(m, 0) for m in output["modules"]) / max(1, total_dose)
        reasons = []
        passed = True
        if total_dose > 10:
            passed = False
            reasons.append(f"Total dose {total_dose} exceeds 10.")
        if num_modules < 2:
            passed = False
            reasons.append("Fewer than 2 modules.")
        if weighted < 0.5:
            passed = False
            reasons.append(f"Weighted adherence {weighted:.2f} < 0.5.")
        if user_profile.get("recent_progress", 0.5) < 0.3 and output["doses"].get("cognitive_training", 0) < 3:
            passed = False
            reasons.append("Low progress; boost cognitive.")
        critique = "; ".join(reasons) if reasons else "Meets all criteria (dose<=10, >=2 modules, weighted>=0.5)."
        return {"passed": passed, "reasons": reasons, "critique": critique}

class Updater:
    def run_loop(self, generator: Generator, verifier: Verifier, user_profile: Dict[str, Any], max_passes: int = 3) -> List[Dict]:
        logs = []
        critique = None
        for i in range(1, max_passes + 1):
            out = generator.generate(user_profile, critique)
            ver = verifier.verify(out, user_profile)
            logs.append({"pass": i, "output": out, "verification": ver})
            if ver["passed"]:
                break
            critique = ver["critique"]
        return logs

def smoke_test():
    profile = {"recent_progress": 0.22, "adherence": "mixed"}
    g = Generator()
    v = Verifier()
    u = Updater()
    logs = u.run_loop(g, v, profile)
    print("Smoke test results:")
    for entry in logs:
        print(f"Pass {entry['pass']}: passed={entry['verification']['passed']} | {entry['verification']['critique']}")
        print(f"  Doses: {entry['output']['doses']} | Nudge: {entry['output']['next_nudge']}")
    return logs

if __name__ == "__main__":
    smoke_test()
