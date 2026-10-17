# 2026-10-18: Adaptive Cognitive Training Dose GVU Agent

**Opportunity:** Prevention/Digital Therapeutics — self-improving adaptive dosing of speed-of-processing cognitive training (from ACTIVE 20-year follow-up showing ~25% dementia risk reduction with boosters).

**Underexploited insight:** Long-term benefit of specific training + boosters is known, but closed-loop personalization based on real-time adherence and progress metrics is missing in most platforms.

**Verifier success criterion:** Plan must include "speed_of_processing" module; if adherence <0.6 reduce dose/modules; if progress_score <0.5 add booster.

**Base:** Standalone Python (minimal slice demonstrating GVU; prior days used similar patterns).

**Files:** gvu_cognitive_dose.py (Generator/Verifier/Updater + smoke test)
