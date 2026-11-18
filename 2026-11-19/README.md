# 2026-11-19 — Speech Biomarker GVU Risk Scorer

**Opportunity (Diagnostics angle):** Passive foundation-model / timing-feature speech biomarkers for early dementia risk flagging from short reading or spontaneous speech.

**Core insight prototyped:** Timing and prosodic features (pause ratio, speech rate, filled pauses, lexical diversity) from papers such as Cay et al. (2024) and foundation speech model evaluations can serve as scalable digital biomarkers. The GVU loop demonstrates a self-improving heuristic that ensures the risk score is consistent with high-risk feature thresholds.

**Verifier success criteria (explicit & falsifiable):**
1. Risk score ∈ [0, 1]
2. If pause_ratio > 0.25 then risk_score ≥ 0.25
3. Explanation references at least one key feature (pause/speech/lexical/rate)

**Smoke test:** High-pause sample (pause_ratio=0.35, speech_rate=95) → risk 0.9, passes on first iteration.

**Run:**
```bash
python speech_gvu.py
```

This is a pure-Python minimal prototype (no external LLM required) that can be extended by replacing the heuristic Generator with an actual model inference or LLM call.
