# 2026-10-29: Pause-prioritized speech biomarker GVU

## Opportunity
Diagnostics/Biosensors: Selective speech biomarkers (pauses strongest) for early dementia detection with lightweight models.

## What runs
`python speech_gvu.py`

## Smoke-test result
Pass 1: score=0.631 elevated but pause not top -> fail
Pass 2: weights updated, pause prioritized, score=0.623 elevated -> pass

## Next step
Add real audio feature extraction (e.g. via librosa or openSMILE) and a small labeled holdout set for the verifier.
