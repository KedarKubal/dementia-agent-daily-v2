# 2026-10-01 — Dyad proximity / caregiver-burden GVU

Monitoring/care opportunity from Chen et al. 2023 (wearable proximity + movement vs Zarit burden) plus location-tracking reviews.

- Generator: drafts `burden_risk`, `wandering_flag`, care `nudge`
- Verifier: Chen-style threshold (proximity≥1h and CG movement≥15% ⇒ risk≥0.55) plus wandering rule (night exits + fence breaches ≥ 3 ⇒ flag)
- Updater: 2–3 passes

Run: `python3 gvu_care_risk.py`
