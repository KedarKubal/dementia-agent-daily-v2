# 2026-10-03 — Dual-task gait-cost flag

Opportunity: phone/IMU dual-task gait cost (not single-task speed) as the MCI-to-dementia progression flag, from Montero-Odasso et al., JAMA Neurology 2017.

Base to fork for a larger UI: https://github.com/saboonikhil/Gait-Assessment

Run: `python3 gvu_dual_task.py`

Verifier rule: progression_flag is true iff (single - dual) / single >= 0.20. Slow single-task gait alone must not flag.
