# 2026-10-26 WristGait-GVU Dementia Risk Refiner

Minimal self-improving GVU prototype for the monitoring opportunity from the UK Biobank wrist-sensor study (max walking speed etc. as independent predictors of incident dementia).

## Run
```bash
python3 wrist_gait_gvu.py
```

Smoke-test shows Generator score 0.427 (fail) -> Updater boosts speed weight -> 0.676 (pass) on slow-walker sample.

## Criterion
Verifier requires score >=0.65, flag=True, and speed among top features for max_speed <1.0 m/s.
