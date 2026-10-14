# 2026-10-15 — Passive Foundation Speech Model Ambient Risk Flag (GVU)

**Opportunity angle**: Diagnostics/Biosensors — early detection via speech.

**Underexploited insight prototyped**: Foundation speech models (Whisper-style embeddings) on continuous/ambient spontaneous speech can provide low-burden, scalable digital biomarkers that update risk without requiring structured reading tasks. The GVU loop self-improves the draft risk score by boosting feature weights when the verifier flags an under-detection on a high-pause/low-lexical sample.

## Files
- `speech_gvu.py` — Generator / Verifier / Updater loop
- Run: `python3 speech_gvu.py`

## Smoke-test result
Pass 1: score≈0.460 ELEVATED (verifier fail: score < 0.48)
Pass 2: score≈0.540 ELEVATED (verifier pass after +0.08 boost)

**Verifier success criterion** (falsifiable): On a sample with pause_ratio > 0.35 or lexical_diversity < 0.40, the candidate must have risk_score ≥ 0.48, flag ≠ LOW, and surface pause_ratio or lexical_diversity in top_features.

Base repo inspiration: lightweight pure-Python multi-agent scaffolds (e.g. planner-executor-critic patterns). This is a minimal slice demonstrating the core paper insight + self-improvement pass.
