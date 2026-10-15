# 2026-10-16: Speech Age Gap (SAG) Dementia Risk Screening GVU

Minimal self-improving multi-agent prototype of the Hernandez et al. (2026) Speech Clocks insight from Science Advances.

**Opportunity**: Passive multimodal speech features (acoustic pauses + linguistic) to compute speech-age gap as scalable early dementia risk flag, culturally adaptable, low-cost, correlating with p-tau217 and brain clocks.

**GVU Loop**:
- Generator: computes SAG and risk score from features with learnable weights
- Verifier: explicit criteria — SAG >5 and risk >=0.4 for elevated sample; pause weight >=0.25 (key acoustic insight)
- Updater: boosts pause weight on fail, normalizes

Smoke-test on high-pause MCI-like sample shows self-improvement: pause weight 0.1 → 0.37, still elevated, pass3 OK.

Run: `python speech_clock_gvu.py`
