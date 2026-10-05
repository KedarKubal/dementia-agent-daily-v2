"""GVU loop: Generator -> Verifier -> Updater, 3 passes max."""

from __future__ import annotations

import json
from pathlib import Path

from generator import generate
from verifier import verify

SAMPLE = {
    "case_id": "SPEECHDX-044",
    "speech_slope_z": 1.35,
    "plasma_ptau217_status": None,
    "linguistic_features": {
        "idea_density": 0.31,
        "pronoun_ratio": 0.22,
        "content_word_ratio": 0.41,
    },
    "note": "Home picture-description, 90s, 6-month slope vs own baseline.",
}


def run(case: dict | None = None, max_passes: int = 3) -> list[dict]:
    case = case or SAMPLE
    critique: str | None = None
    log: list[dict] = []
    for i in range(1, max_passes + 1):
        draft = generate(case, critique)
        verdict = verify(case, draft)
        log.append({"pass": i, "draft": draft, "verdict": verdict})
        if verdict["pass"]:
            break
        critique = "; ".join(verdict["reasons"])
    return log


def main() -> None:
    log = run()
    out = Path(__file__).resolve().parent / "smoke_log.json"
    out.write_text(json.dumps(log, indent=2), encoding="utf-8")
    for entry in log:
        d = entry["draft"]
        v = entry["verdict"]
        print(
            f"pass {entry['pass']}: label={d['label']} "
            f"features={list(d['features_cited'])} "
            f"next={d['next_step']} pass={v['pass']} reason={v['reasons'][0]}"
        )


if __name__ == "__main__":
    main()
