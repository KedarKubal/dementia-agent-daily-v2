# 2026-11-03: Speech Voiceprint Risk Flag GVU

Prototype of the diagnostics opportunity from voiceprint / speech biomarker papers (e.g., high-AUC end-to-end models on Craft Story Recall showing pauses and linguistic informativeness as key).

## Opportunity
Passive continuous screening: turn everyday voice (calls, messages) into early dementia risk flags by prioritizing pause patterns and lexical features, deployable on edge.

## GVU Loop
- Generator: drafts risk_score + flag from pause_ratio / lexical_diversity.
- Verifier: explicit criterion — for pause_ratio > 0.35, score >= 0.6, flag == "elevated", top_feature == "pause_ratio".
- Updater: feeds critique, boosts pause weight, re-runs.

## Smoke Test
High-pause sample: pass1 score 0.429 / typical (fail) → pass2 score 0.729 / elevated (pass).

Run: `python3 speech_gvu.py`
