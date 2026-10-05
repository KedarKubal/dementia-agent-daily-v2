# 2026-10-05 lexical-drift (second slice; craft-story files left intact)

Opportunity: within-person lexical frequency / familiarity / partial-word drift (Cho et al. 2022), not pause rate and not Cookie-Theft information units.

Base pattern to fork: https://github.com/cpgrant/multiagent (Planner-Executor-Critic). This folder is a zero-dependency GVU slice.

Run: `python3 gvu_lexical_drift.py`

Verifier rule: referral_flag is true only if baseline_n >= 3 and lexical_frequency_delta >= 0.15 and familiarity_delta >= 0.10 and partial_word_delta > 0, with those three features as the drivers. Pause-only drafts fail.
