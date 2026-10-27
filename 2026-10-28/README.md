# 2026-10-28: PSD + Fluid Biomarker Fusion GVU for Early CI Flag

**Opportunity**: Diagnostics/Biosensors — Speech digital biomarker (PSD) fused with serum p-tau217/GFAP via self-improving multi-agent weights.
Underexploited insight: PSD correlates with fluid biomarkers and cognitive level (two-stage change pattern); a GVU loop can learn personalized fusion weights from verifier critiques instead of static models.

**Base idea**: Minimal pure-Python GVU (no external multi-agent repo needed for 2h slice).
**Verifier criterion**: High-risk (PSD>0.45 AND abnormal blood) must yield flag=elevated AND conf>=0.65; else typical for low-risk.

**Smoke test**: High-risk sample pass1 typical/fail (score 0.416) → pass2 elevated/pass (score 0.711, weights boosted).

Run: `python3 gvu_psd_fusion.py`
