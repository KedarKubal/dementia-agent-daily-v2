# 2026-10-05 — Craft-story delayed-retention differential

Fork-style slice of a multi-agent loop (base pattern: https://github.com/fetchai/innovation-lab-examples). No network, no model calls.

Opportunity: Rezaii et al., npj Dementia 2025, feature-engineered Craft Story units. Prototype the immediate-vs-delayed proposition ledger (storage-loss pattern), not a pause score and not a Cookie-Theft panel.

Verifier rule: not pause-only; retention_ratio present; at least two missing delayed units cited; if ratio < 0.60 and delayed hits <= 4 then differential is storage_loss_pattern and referral_flag is true.

Run: `python3 gvu_craft_differential.py`
