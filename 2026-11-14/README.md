# 2026-11-14: Passive Speech Voiceprint MCI Risk Flag (GVU)

**Opportunity:** Diagnostics angle from "Voiceprints of cognitive impairment" (npj Dementia, 2025). Underexploited insight: end-to-end deep learning (AUC 0.988) on spontaneous speech (Craft Story) enables high-accuracy passive MCI detection that can seed a phone-call or ambient screening agent.

**Prototype:** Minimal Generator-Verifier-Updater loop that scores speech features and self-improves weights/bias until success criterion is met (risk_score >= 0.7 and pause/linguistic prioritized for high-risk samples).

**Success criterion (Verifier):** For high-risk sample, risk_score >= 0.7 AND top_feature in ['pause_ratio', 'linguistic_informativeness'].

**Smoke test:** High-pause sample: pass1 score 0.663 (fail) → pass2 0.720 (pass, pause prioritized).

Base inspiration: simple multi-agent healthcare patterns (e.g. ElderCareAI). Files: gvu_speech_voiceprint.py + this README.
