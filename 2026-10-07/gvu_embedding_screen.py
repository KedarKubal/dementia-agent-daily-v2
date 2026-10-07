#!/usr/bin/env python3
"""GVU speech-embedding screen (2026-10-07).

Prototypes the underexploited insight in Li et al. 2025 (arXiv:2506.11119):
ASR-encoder embeddings beat transcript classifiers for ADRD. The product
slice never retains lexical content. Generator may leak a transcript on
pass 1; Verifier rejects it; Updater strips words and rescores from the
embedding distance only.

No network, no model weights. Embedding stats are precomputed stand-ins
so the loop is runnable in a 2-hour fork.
"""

from __future__ import annotations

import json
from typing import Any

LEXICAL_KEYS = {"transcript", "tokens", "words", "lexical_excerpt", "keyword_hits"}
DISTANCE_CUTOFF = 0.42  # cosine distance to healthy-control centroid


def generator(sample: dict[str, Any], critique: str | None = None) -> dict[str, Any]:
    """Draft a screening payload. First pass leaks words; later passes do not."""
    distance = float(sample["embedding_cosine_distance_to_hc"])
    pause_ratio = float(sample.get("pause_ratio", 0.0))
    if critique is None:
        hits = [w for w in sample.get("tokens", []) if w.lower() in {"forgot", "um", "thing", "yesterday"}]
        score = min(1.0, 0.15 * len(hits) + 0.4 * pause_ratio)
        return {
            "subject_id": sample["subject_id"],
            "transcript": " ".join(sample.get("tokens", [])),
            "tokens": list(sample.get("tokens", [])),
            "keyword_hits": hits,
            "embedding_cosine_distance_to_hc": distance,
            "risk_score": round(score, 3),
            "referral_flag": score >= 0.35,
            "label": "keyword_screen",
            "discarded_lexical": False,
            "basis": "transcript_keywords",
        }
    flag = distance >= DISTANCE_CUTOFF
    return {
        "subject_id": sample["subject_id"],
        "embedding_cosine_distance_to_hc": round(distance, 3),
        "risk_score": round(min(1.0, distance), 3),
        "referral_flag": flag,
        "label": "elevated_embedding" if flag else "typical_embedding",
        "discarded_lexical": True,
        "basis": "asr_embedding_distance_only",
        "note": "lexical payload stripped after verifier critique",
    }


def verifier(output: dict[str, Any]) -> dict[str, Any]:
    """Falsifiable checks. Pass only if every rule holds."""
    reasons: list[str] = []
    leaked = sorted(LEXICAL_KEYS.intersection(output.keys()))
    if leaked:
        reasons.append(f"lexical keys present: {leaked}")
    if output.get("discarded_lexical") is not True:
        reasons.append("discarded_lexical is not true")
    if output.get("basis") != "asr_embedding_distance_only":
        reasons.append("basis is not asr_embedding_distance_only")
    distance = output.get("embedding_cosine_distance_to_hc")
    if not isinstance(distance, (int, float)):
        reasons.append("missing embedding_cosine_distance_to_hc")
    else:
        expected_flag = float(distance) >= DISTANCE_CUTOFF
        if output.get("referral_flag") is not expected_flag:
            reasons.append(
                f"referral_flag {output.get('referral_flag')} != expected {expected_flag} "
                f"at cutoff {DISTANCE_CUTOFF}"
            )
    passed = not reasons
    return {"pass": passed, "reasons": reasons or ["ok"]}


def updater(sample: dict[str, Any], rounds: int = 3) -> list[dict[str, Any]]:
    """Run generator -> verifier -> critique feedback, up to `rounds` passes."""
    log: list[dict[str, Any]] = []
    critique: str | None = None
    for i in range(1, rounds + 1):
        draft = generator(sample, critique)
        verdict = verifier(draft)
        log.append({"pass": i, "output": draft, "verdict": verdict})
        if verdict["pass"]:
            break
        critique = "; ".join(verdict["reasons"])
    return log


SAMPLE = {
    "subject_id": "ADRD-EMB-077",
    "tokens": ["I", "um", "forgot", "the", "thing", "from", "yesterday"],
    "pause_ratio": 0.31,
    "embedding_cosine_distance_to_hc": 0.57,
}


def main() -> None:
    trace = updater(SAMPLE)
    print(json.dumps({"sample": SAMPLE["subject_id"], "trace": trace}, indent=2))
    assert trace[0]["verdict"]["pass"] is False, "pass 1 should fail lexical leak"
    assert trace[-1]["verdict"]["pass"] is True, "final pass should meet criterion"
    assert "transcript" not in trace[-1]["output"]


if __name__ == "__main__":
    main()
