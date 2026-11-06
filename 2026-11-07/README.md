# 2026-11-07 — Passive Multi-Modal Speech + Gait Cognitive Reserve Trajectory Flag

**Angle:** Diagnostics/Biosensors  
**Opportunity:** Longitudinal passive fusion of dual-task gait variability and speech pause patterns from consumer sensors into a daily updating "cognitive reserve trajectory" score. Most papers treat modalities separately or in lab; this prototype demonstrates a self-improving GVU loop that re-weights the fusion when the initial draft under-scores a high-risk sample.

## Verifier success criterion
- risk_level == "elevated"
- risk_score >= 0.60
- "pause_ratio" in top_features
- High pause_ratio (>0.4) + high gait_variability (>0.15) must not be flagged typical

## Smoke test result
Pass 1: score 0.591 elevated but <0.60 → fail  
Pass 2: after weight boost + bias, score 0.644 elevated, pause in top → pass

Base inspiration: simple pure-Python multi-agent from scratch (e.g. AIAnytime/Multi-Agents-System-from-Scratch).  
Run: `python3 gvu_dementia_risk.py`
