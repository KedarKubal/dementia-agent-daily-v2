# 2026-10-25: Speech Feature Refiner GVU for MCI Biomarker

Minimal self-improving multi-agent prototype of the next-big opportunity from speech-biomarker papers (e.g., dual dropout ranking for feature selection in dementia detection).

## Opportunity recap
Diagnostics angle: Early MCI detection via speech biomarkers. Underexploited: iterative feature selection/ranking (DDR-style) that can be turned into a self-improving agent loop refining which acoustic/linguistic cues drive the risk flag.

## GVU loop
- Generator: drafts risk_score + flag from weighted features (pause_ratio, lexical_diversity, speech_rate).
- Verifier: explicit criterion — if pause>0.25 AND lex<0.6 then score must >0.7; else <0.4.
- Updater: adjusts weights from critique; loops 2-3 times.

## Run
```bash
python gvu_speech_refiner.py
```
Smoke-test on high-risk sample shows improvement across passes.

Base conceptually forked from simple multi-agent patterns (no heavy deps).
