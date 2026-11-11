# 2026-11-12: Age-adjusted gait risk flag GVU

**Opportunity:** Diagnostics/Monitoring angle — age-dependent nonlinear gait impairment as predictor of incident dementia (stronger in younger-old adults).

**Paper:** Age-Dependent Nonlinear Association Between Gait Impairment and Incident Dementia (Neurology, 2026).

**Prototype:** Minimal self-improving multi-agent (GVU) that scores gait + age features. Generator produces score/flag; Verifier enforces elevated flag + age/gait prioritization for younger-old high-risk sample; Updater reweights across passes.

**Verifier criterion:** For SAMPLE (age 68, gait_score 9.5), output flag must be "elevated" (score > 0.6) AND top_feature in ["age", "gait"].

**Smoke:** pass1 (var-prioritized, fail) → pass3 (age-prioritized, ok). Score 0.777 → 0.836.

Run: `python3 gvu_gait_age.py`
