"""
WristGait-GVU: Self-improving multi-agent prototype for dementia risk from wrist-sensor gait features.
Based on UK Biobank watch-walk study insight: max walking speed, running duration, bedtime as independent predictors.
GVU loop: Generator proposes score/flag, Verifier checks against explicit criterion, Updater revises weights.
Smoke-test: high-risk slow-walker sample.
"""

from typing import Dict, Any, List
import json

# Explicit success criterion for Verifier (falsifiable)
# High risk if max_walking_speed < 1.0 m/s (normalized), score must >=0.65 and flag=True, and speed is top feature.
SUCCESS_THRESHOLD = 0.65
SLOW_SPEED_THRESHOLD = 1.0

class Generator:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "max_walking_speed_inv": 0.05,  # weak initial so loop improves
            "step_time_variability": 0.1,
            "running_duration_min": -0.05,
            "bedtime_early": 0.05
        }
    
    def generate(self, features: Dict[str, float]) -> Dict[str, Any]:
        # Prepare inverted features
        feat_used = {
            "max_walking_speed_inv": 2.0 - features.get("max_walking_speed", 1.2),
            "step_time_variability": features.get("step_time_variability", 1.0),
            "running_duration_min": features.get("running_duration_min", 10.0),
            "bedtime_early": 24 - features.get("bedtime_hour", 23.0)
        }
        raw = 0.1
        for feat, w in self.weights.items():
            if feat in feat_used:
                raw += w * feat_used[feat]
        score = max(0.0, min(1.0, raw))
        flag = score >= 0.5
        top_features = sorted(self.weights.keys(), key=lambda k: abs(self.weights[k]), reverse=True)[:2]
        return {
            "risk_score": round(score, 3),
            "elevated_flag": flag,
            "top_features": top_features,
            "weights_used": self.weights.copy()
        }

class Verifier:
    def verify(self, output: Dict[str, Any], features: Dict[str, float]) -> Dict[str, Any]:
        reasons = []
        passed = True
        is_slow = features.get("max_walking_speed", 2.0) < SLOW_SPEED_THRESHOLD
        if is_slow:
            if output["risk_score"] < SUCCESS_THRESHOLD:
                passed = False
                reasons.append(f"Score {output['risk_score']} < {SUCCESS_THRESHOLD} for slow walker")
            if not output["elevated_flag"]:
                passed = False
                reasons.append("Flag not elevated for slow walker")
            if "max_walking_speed_inv" not in output["top_features"]:
                passed = False
                reasons.append("Speed not among top features")
        else:
            if output["risk_score"] > 0.4:
                passed = False
                reasons.append("False positive high score for normal speed")
        if not reasons:
            reasons.append("Meets criterion")
        return {"pass": passed, "reasons": reasons}

class Updater:
    def update(self, generator: Generator, critique: Dict[str, Any], features: Dict[str, float]) -> None:
        if critique["pass"]:
            return
        # Simple rule-based update: boost speed weight if under-detected
        if features.get("max_walking_speed", 2.0) < SLOW_SPEED_THRESHOLD and not critique["pass"]:
            generator.weights["max_walking_speed_inv"] = generator.weights.get("max_walking_speed_inv", 0.2) + 0.25
            # Reduce others slightly
            for k in list(generator.weights.keys()):
                if k != "max_walking_speed_inv":
                    generator.weights[k] *= 0.9

def run_gvu(features: Dict[str, float], max_passes: int = 3) -> List[Dict[str, Any]]:
    gen = Generator()
    ver = Verifier()
    upd = Updater()
    logs = []
    for i in range(max_passes):
        out = gen.generate(features)
        crit = ver.verify(out, features)
        log_entry = {
            "pass": i + 1,
            "output": out,
            "critique": crit
        }
        logs.append(log_entry)
        print(f"Pass {i+1}: score={out['risk_score']}, flag={out['elevated_flag']}, pass={crit['pass']}, reasons={crit['reasons']}")
        if crit["pass"]:
            break
        upd.update(gen, crit, features)
    return logs

if __name__ == "__main__":
    # Sample: slow walker high risk (from study insight)
    sample = {
        "max_walking_speed": 0.75,  # m/s, slow
        "step_time_variability": 1.4,
        "running_duration_min": 0.0,
        "bedtime_hour": 21.5  # early
    }
    print("=== Smoke Test: Slow Walker ===")
    logs = run_gvu(sample)
    print("\nFinal logs:")
    print(json.dumps(logs[-1], indent=2))
    # Save for repo
    with open("smoke_test_output.json", "w") as f:
        json.dump({"sample": sample, "logs": logs}, f, indent=2)
