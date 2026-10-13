# Day 2026-10-14: SpeechDETECT Explainable Triage Ranker

## Opportunity
Diagnostics/Biosensors: SpeechDETECT (2026) – explainable pipeline with SHAP on PCA features from short multi-task speech; underexploited insight is cumulative-gains triage (top 40% captures ~70% of cases) + automatic biomarker ranking for scalable screening.

## Prototype
Minimal GVU loop in pure Python (no external LLM) demonstrating self-improving risk score + feature ranking from mock speech features.

- Generator: heuristic score + top features
- Verifier: explicit criteria (score range, high-risk threshold >=0.70, fluency feature present)
- Updater: 2-3 passes, logs changes

## Run
```bash
python speech_biomarker_gvu.py
```

## Base idea
Inspired by simple multi-agent patterns; this is the one feature slice of the paper insight.
