#!/usr/bin/env python3
"""Sparse spoken-language biomarker panel — Generator / Verifier / Updater.

Prototypes the underexploited insight in Ke, Mak, Meng (Neural Networks, 2024):
under small-N dementia speech data, a two-step selector should emit a short,
interpretable biomarker list rather than a black-box score. Distinct from the
2026-09-30 pause-only flag: pause_rate alone cannot pass the verifier.
"""

from __future__ import annotations

import json
from typing import Any

ALLOWED = {
    "info_units",
    "lexical_diversity",
    "pronoun_ratio",
    "semantic_idea_density",
    "pause_rate",
    "filled_pause_ratio",
}
CONTENT_FEATURES = {"info_units", "lexical_diversity", "pronoun_ratio", "semantic_idea_density"}
MAX_PANEL = 5
INFO_UNIT_FLOOR = 8  # Cookie-Theft content units; below this, content feature required


def generator(sample: dict[str, Any], critique: str | None = None) -> dict[str, Any]:
    """Draft a ranked biomarker panel and a referral flag."""
    features = sample["features"]
    ranked: list[dict[str, Any]] = []

    if features["info_units"] < INFO_UNIT_FLOOR:
        ranked.append({"name": "info_units", "value": features["info_units"], "direction": "low"})
    if features["lexical_diversity"] < 0.45:
        ranked.append({"name": "lexical_diversity", "value": features["lexical_diversity"], "direction": "low"})
    if features["pronoun_ratio"] > 0.18:
        ranked.append({"name": "pronoun_ratio", "value": features["pronoun_ratio"], "direction": "high"})
    if features["semantic_idea_density"] < 0.40:
        ranked.append({"name": "semantic_idea_density", "value": features["semantic_idea_density"], "direction": "low"})
    if features["pause_rate"] > 0.25:
        ranked.append({"name": "pause_rate", "value": features["pause_rate"], "direction": "high"})
    if features["filled_pause_ratio"] > 0.08:
        ranked.append({"name": "filled_pause_ratio", "value": features["filled_pause_ratio"], "direction": "high"})

    # First pass intentionally overweights acoustics if no critique yet (the failure mode).
    if critique is None:
        ranked = [item for item in ranked if item["name"] in {"pause_rate", "filled_pause_ratio"}]
        if not ranked:
            ranked = [{"name": "pause_rate", "value": features["pause_rate"], "direction": "high"}]

    if critique:
        content = [item for item in ranked if item["name"] in CONTENT_FEATURES]
        acoustic = [item for item in ranked if item["name"] not in CONTENT_FEATURES]
        ranked = content + acoustic

    panel = ranked[:MAX_PANEL]
    content_hits = [item["name"] for item in panel if item["name"] in CONTENT_FEATURES]
    referral = bool(content_hits) and features["info_units"] < INFO_UNIT_FLOOR
    return {
        "sample_id": sample["sample_id"],
        "task": "cookie_theft",
        "panel": panel,
        "referral_flag": referral,
        "rationale": (
            "content-unit deficit" if referral else "acoustic-only draft; not sufficient for referral"
        ),
    }


def verifier(candidate: dict[str, Any], sample: dict[str, Any]) -> dict[str, Any]:
    """Falsifiable success criterion.

    Pass iff all of:
      1. panel size is 1..5 and every name is in ALLOWED
      2. if info_units < 8, panel includes at least one CONTENT feature
      3. referral_flag is True iff (info_units < 8 and a content feature is on the panel)
      4. panel is not pause-only when info_units < 8
    """
    reasons: list[str] = []
    panel = candidate.get("panel") or []
    names = [item.get("name") for item in panel]
    if not (1 <= len(panel) <= MAX_PANEL):
        reasons.append(f"panel size {len(panel)} not in 1..{MAX_PANEL}")
    unknown = [name for name in names if name not in ALLOWED]
    if unknown:
        reasons.append(f"unknown biomarkers: {unknown}")
    info_units = sample["features"]["info_units"]
    has_content = any(name in CONTENT_FEATURES for name in names)
    if info_units < INFO_UNIT_FLOOR and not has_content:
        reasons.append("info_units below floor but panel has no content-unit biomarker")
    expected_flag = info_units < INFO_UNIT_FLOOR and has_content
    if bool(candidate.get("referral_flag")) != expected_flag:
        reasons.append(
            f"referral_flag={candidate.get('referral_flag')} expected {expected_flag}"
        )
    passed = not reasons
    return {"pass": passed, "reasons": reasons or ["ok"]}


def updater(sample: dict[str, Any], passes: int = 3) -> list[dict[str, Any]]:
    log: list[dict[str, Any]] = []
    critique: str | None = None
    for i in range(1, passes + 1):
        draft = generator(sample, critique)
        verdict = verifier(draft, sample)
        log.append({"pass": i, "output": draft, "verdict": verdict})
        if verdict["pass"]:
            break
        critique = "; ".join(verdict["reasons"])
    return log


def main() -> None:
    sample = {
        "sample_id": "CT-204",
        "features": {
            "info_units": 5,
            "lexical_diversity": 0.38,
            "pronoun_ratio": 0.22,
            "semantic_idea_density": 0.31,
            "pause_rate": 0.33,
            "filled_pause_ratio": 0.11,
        },
    }
    log = updater(sample, passes=3)
    print(json.dumps({"sample": sample, "gvu_log": log}, indent=2))


if __name__ == "__main__":
    main()
