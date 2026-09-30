# 2026-09-30 — Pause-aware speech biomarker flag

**Opportunity:** Diagnostics — pause-annotated ASR features as a phone-call screen for MCI/ADRD.

**Paper seed:** Li et al. 2025 (arXiv:2506.11119) — pause annotation improves foundation-model ADRD detection.

## Run

```bash
python3 gvu_speech_flag.py
```

## GVU pattern

- **Generator** — drafts risk score from `[PAUSE]`-tagged transcript + duration
- **Verifier** — fail-closed rules: rate < 90 syl/min OR mean_pause > 0.80s OR pause_ratio > 0.35 ⇒ flag must be `elevated` and score ≥ 0.45
- **Updater** — raises pause weight and applies rate floor on failed passes

## Smoke test result

| Pass | flag | score | verifier |
|------|------|-------|----------|
| 1 | typical | 0.284 | FAIL |
| 2 | elevated | 0.48 | PASS |
