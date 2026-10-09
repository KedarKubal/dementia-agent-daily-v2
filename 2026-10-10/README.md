# 2026-10-10 — Circadian rest-activity fragmentation desk

Opportunity: Musiek et al., JAMA Neurol 2018 showed preclinical AD rest-activity fragmentation (higher intradaily variability, lower relative amplitude) independent of age and sex. Consumer wearables already log activity counts, but products still flag short total sleep.

GVU slice: Generator drafts a progression card. Verifier passes only if `referral_flag` matches IV >= 0.75 or RA <= 0.65 and the driver is not `total_sleep_hours`. Updater revises.

Run: `python3 gvu_circadian.py`

Smoke test WASHU-CIRC-210: pass 1 fail (sleep-only flag, sleep_hygiene_leaflet) -> pass 2 ok (IV 0.91 driver, circadian_clinic_review).
