# 2026-10-30: Curve-Walking Gait Digital Biomarker GVU

Monitoring/Care angle prototype of Seifallahi et al. (2024) insight: curve walking reveals more gait impairments than straight for MCI detection.

GVU loop: Generator produces risk flag from velocity drop + variability; Verifier enforces explicit criterion (elevated if vel_drop>0.25 AND var_inc>0.1, with curve_variability prioritized); Updater feeds critique and re-runs.

Smoke test: pass1 typical (fail) -> pass2 elevated (pass).
