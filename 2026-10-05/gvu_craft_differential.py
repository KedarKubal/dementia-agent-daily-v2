"""Craft-story delayed-retention differential (GVU).

Prototypes the underexploited slice of Rezaii et al., npj Dementia 2025:
feature-engineered linguistic units on Craft Story recall, especially the
immediate-vs-delayed gap that separates a storage-loss pattern from a
retrieval-intact recall. Not a pause-only or Cookie-Theft panel.

No model calls. Deterministic so the loop is falsifiable.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


# Short public-domain-style stand-in narrative. Not the copyrighted Craft story.
CANONICAL_UNITS: dict[str, str] = {
    "u1_boy": "a boy",
    "u2_dog": "his dog",
    "u3_park": "went to the park",
    "u4_red_ball": "a red ball",
    "u5_lake": "near the lake",
    "u6_ducks": "ducks on the water",
    "u7_mother_calls": "his mother called him",
    "u8_ice_cream": "they got ice cream",
}

RETENTION_FAIL = 0.60
DELAYED_HIT_CEILING = 4
MIN_MISSING_CITED = 2


@dataclass
class RecallSample:
    sample_id: str
    immediate_text: str
    delayed_text: str


@dataclass
class DraftFlag:
    sample_id: str
    features_used: list[str]
    immediate_hits: list[str] = field(default_factory=list)
    delayed_hits: list[str] = field(default_factory=list)
    missing_delayed: list[str] = field(default_factory=list)
    retention_ratio: float | None = None
    differential: str = "unspecified"
    referral_flag: bool = False
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hits(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for unit_id, phrase in CANONICAL_UNITS.items():
        if phrase in lowered:
            found.append(unit_id)
    return found


def generator(sample: RecallSample, critique: str | None = None) -> DraftFlag:
    """Pass 1 emits a pause-only draft (the failure mode prior days already shipped).

    After a verifier critique, the generator switches to proposition units and
    the delayed/immediate retention ratio.
    """
    if critique is None:
        return DraftFlag(
            sample_id=sample.sample_id,
            features_used=["pause_rate"],
            differential="impairment_unspecified",
            referral_flag=True,
            rationale="Pause rate 0.31 treated as a binary impairment flag. No story units.",
        )

    immediate = _hits(sample.immediate_text)
    delayed = _hits(sample.delayed_text)
    missing = [unit for unit in immediate if unit not in delayed]
    ratio = (len(delayed) / len(immediate)) if immediate else 0.0
    storage_loss = ratio < RETENTION_FAIL and len(delayed) <= DELAYED_HIT_CEILING
    differential = "storage_loss_pattern" if storage_loss else "retrieval_intact"
    return DraftFlag(
        sample_id=sample.sample_id,
        features_used=["immediate_idea_units", "delayed_idea_units", "retention_ratio"],
        immediate_hits=immediate,
        delayed_hits=delayed,
        missing_delayed=missing,
        retention_ratio=round(ratio, 3),
        differential=differential,
        referral_flag=storage_loss,
        rationale=(
            f"Revised after critique. Delayed/immediate retention={ratio:.3f}; "
            f"missing delayed units={missing}. "
            + (
                "Storage-loss pattern: refer for EOAD-leaning workup, not a pause score."
                if storage_loss
                else "Retention above rule; no storage-loss referral."
            )
        ),
    )


def verifier(draft: DraftFlag) -> dict[str, Any]:
    """Explicit success criterion.

    Pass only if all hold:
    1. features_used is not pause-only.
    2. retention_ratio is present.
    3. at least two missing delayed proposition ids are cited when immediate > delayed.
    4. if retention_ratio < 0.60 and delayed hits <= 4, differential is
       storage_loss_pattern and referral_flag is true.
    """
    reasons: list[str] = []
    if draft.features_used == ["pause_rate"] or "immediate_idea_units" not in draft.features_used:
        reasons.append("pause-only or missing idea-unit features; prior-day failure mode")
    if draft.retention_ratio is None:
        reasons.append("retention_ratio missing")
    if draft.immediate_hits and len(draft.missing_delayed) < MIN_MISSING_CITED:
        reasons.append(
            f"need >= {MIN_MISSING_CITED} cited missing delayed units, got {draft.missing_delayed}"
        )
    storage_rule = (
        draft.retention_ratio is not None
        and draft.retention_ratio < RETENTION_FAIL
        and len(draft.delayed_hits) <= DELAYED_HIT_CEILING
    )
    if storage_rule and (
        draft.differential != "storage_loss_pattern" or not draft.referral_flag
    ):
        reasons.append(
            "storage-loss rule fired but differential/referral_flag not set"
        )
    if not storage_rule and draft.differential == "storage_loss_pattern":
        reasons.append("storage_loss_pattern set without the retention rule firing")

    return {
        "pass": not reasons,
        "reasons": reasons or ["retention ledger matches the storage-loss rule"],
        "criterion": (
            "not pause-only; retention_ratio present; >=2 missing delayed units cited; "
            "if ratio<0.60 and delayed hits<=4 then differential=storage_loss_pattern "
            "and referral_flag=true"
        ),
    }


def updater(sample: RecallSample, passes: int = 3) -> list[dict[str, Any]]:
    log: list[dict[str, Any]] = []
    critique: str | None = None
    draft = generator(sample, critique)
    for index in range(1, passes + 1):
        report = verifier(draft)
        log.append(
            {
                "pass": index,
                "draft": draft.to_dict(),
                "verifier": report,
            }
        )
        if report["pass"]:
            break
        critique = "; ".join(report["reasons"])
        draft = generator(sample, critique)
    return log


SAMPLE = RecallSample(
    sample_id="EOAD-LEADS-017",
    immediate_text=(
        "A boy and his dog went to the park with a red ball near the lake. "
        "There were ducks on the water. His mother called him and they got ice cream."
    ),
    delayed_text="A boy and his dog went to the park with a red ball.",
)


def main() -> None:
    log = updater(SAMPLE, passes=3)
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
