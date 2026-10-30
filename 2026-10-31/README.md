# 2026-10-31: Self-Improving Speech Embedding Risk Flag

Based on foundation speech/language models for early ADRD detection from spontaneous speech (e.g., Whisper-style embeddings capturing acoustic + semantic cues).

**Opportunity**: Personalized, self-improving multi-agent risk flag that adapts feature weights (pause, embedding anomaly, etc.) to individual baselines via GVU loop.

**Verifier criterion**: High-risk sample must produce elevated flag with score >=0.55 and pause_ratio emphasized (top feature or weight >=0.35).

**Smoke test**: Pass 1 (initial low pause weight) -> elevated but top=lexical (FAIL) -> Pass 2 (boosted pause) -> elevated with pause top (PASS).

Run: `python3 gvu_speech_risk.py`
