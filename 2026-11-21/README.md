# 2026-11-21: PSD Speech Digital Biomarker GVU Risk Flag

**Opportunity**: Diagnostics/Biosensors — early CI detection via speech PSD + optional fluid fusion.

**Underexploited insight**: Percentage of silence duration (PSD) correlates with p-tau217/GFAP and amyloid; a self-improving agent can iteratively reweight acoustic features so pause/PSD dominate over lexical on high-risk samples.

**GVU pattern**:
- Generator: weighted score from PSD, pause_ratio, lexical, rate.
- Verifier: for high-PSD sample, require elevated flag AND top feature in {psd, pause_ratio}.
- Updater: boost PSD/pause weights + bias on fail.

Smoke test shows pass1 fail (top=lexical) → pass2 pass (top=psd, score↑).
