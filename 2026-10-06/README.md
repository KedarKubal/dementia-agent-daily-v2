# 2026-10-06 — Dual-gate speech × plasma progressor desk

Minimal Generator–Verifier–Updater prototype of today's opportunity.

Not a diagnostic device. Toy rules on a single synthetic case.

## Run

```bash
python gvu.py
```

## Success criterion

A draft passes only if the label is in `{stable, indeterminate_needs_plasma, higher_risk_progressor}`, at least two numeric linguistic features are cited, and `higher_risk_progressor` is emitted only when `speech_slope_z >= 1.0` and `plasma_ptau217_status == positive`. Missing plasma must yield `indeterminate_needs_plasma`.

Base pattern to fork for a longer build: https://github.com/alicelee1/ad_care
