# 2026-10-08 — Six-axis conversational speech biomarker card

Base idea to fork: https://github.com/srinjoydutta03/MindGuardAI (local speech capture for dementia care; no biomarker panel).

Insight from Addlesee et al., arXiv:2502.10896: six named conversational biomarkers plus a composite that beat any single axis against MMSE.

Verifier criterion: at least 4 of the 6 named axes present, composite equals the mean of measured axes, and the label is not a black-box single flag.

Run: `python3 gvu_six_axis_speech.py`
