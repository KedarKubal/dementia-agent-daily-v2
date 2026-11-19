# 2026-11-20: PSD Speech Biomarker GVU Risk Flag

**Opportunity:** Diagnostics angle — continuous passive monitoring of percentage of silence duration (PSD) from everyday speech (phone/calls) as early CI digital biomarker, optionally fused with fluid markers (p-tau217/GFAP).

**Core insight prototyped:** From 2025 paper (speech digital biomarker + fluid biomarkers ML model, AUC 0.928 for CI). Underexploited: PSD as a simple, phone-native acoustic feature that tracks with pathology; self-improving agent can learn individual baselines and prioritize it over generic lexical cues.

**GVU:**
- Generator: weighted score from PSD, pause, lexical, rate, optional fluid.
- Verifier: for high-PSD (>=0.35) sample, must output elevated/high label AND top feature PSD or pause.
- Updater: boosts PSD/pause weights + bias on fail.

Pure Python. Run: `python gvu_psd_speech.py`
