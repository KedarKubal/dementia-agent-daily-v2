# dementia-agent-daily-v2 log

2026-09-30 | Pause-aware speech-biomarker flag | GVU loop upweights pause features after verifier fail; smoke-test pass1 typical 0.284 -> pass2 elevated 0.48
2026-10-01 | Dyad proximity caregiver-burden / wandering risk | GVU flips wandering_flag False->True and nudge no_action->night_check_protocol
2026-10-02 | Closed-loop multidomain prevention coach | GVU drops non-adherent physical_activity and cuts 3 modules to 2 (nutrition+cognitive dose 4); pass1 fail -> pass2 ok
2026-10-03 | Dual-task gait-cost progression flag | GVU drops single-task-slow false flag; MCI-014 cost 0.083 flag True->False, next_step routine_followup
2026-10-04 | Sparse Cookie-Theft information-unit biomarker panel | GVU drops pause-only draft; CT-204 panel gains info_units/lexical_diversity, referral_flag false->true, pass2 ok
2026-10-05 | Craft-story delayed-retention differential (EOAD storage-loss pattern) | GVU drops pause-only draft; EOAD-LEADS-017 retention 0.5, missing 4 delayed units, differential storage_loss_pattern, pass2 ok
2026-10-05b | Within-person lexical frequency/familiarity drift flag | GVU drops pause-only draft; MCI-LEX-118 freq delta 0.22 familiarity 0.14 partial-word 0.06, referral true, pass2 ok; nested under 2026-10-05/lexical-drift so craft-story files stay intact
2026-10-06 | Dual-gate speech-slope x plasma p-tau217 progressor desk | GVU drops speech-only higher_risk_progressor; SPEECHDX-044 slope z 1.35 plasma missing, label -> indeterminate_needs_plasma, pass2 ok
2026-10-07 | Embedding-discard ASR speech screen | GVU strips transcript leak; ADRD-EMB-077 distance 0.57 keyword_screen fail -> elevated_embedding pass2 ok
2026-10-08 | Six-axis conversational speech biomarker card | GVU drops anomia-only black-box flag; ROBOT-CONV-088 composite 0.497 elevated_composite, pass2 ok
2026-10-10 | Circadian rest-activity IV/RA fragmentation desk | GVU drops sleep-only flag; WASHU-CIRC-210 IV 0.91 driver total_sleep_hours -> intradaily_variability, next_step sleep_hygiene_leaflet -> circadian_clinic_review, pass2 ok
2026-10-11 | Speech age gap multi-clock screening | GVU multi-feature SAG stable elevated 6.4 on MCI-like sample; pass1 ok (multi-feature range met)
2026-10-12 | Speech pause/DTW similarity risk flag from wearable mic reading task | GVU heuristic matches Cay et al. 2024 features; smoke-test high-pause sample flags HIGH 0.85 pass1 ok
2026-10-13 | Modular speech detectors for CI risk flag (WATCH-SS insight) | GVU self-improves risk assessment from pause/lexical features; smoke-test HIGH 0.85 pass1 ok
2026-10-14 | SpeechDETECT SHAP/cumulative-gains triage ranker for speech screening | GVU boosts score 0.399->0.749 and adds pause_ratio to top_features; pass1 fail -> pass2 ok
2026-10-15 | Passive foundation-model (Whisper-style) ambient speech embedding risk flag | GVU boosts score 0.460->0.540 after verifier under-detection; pass1 fail -> pass2 ok
2026-10-16 | Speech age gap multimodal clock risk screen | GVU boosts pause weight 0.1->0.37 on under-weighted acoustic features; SAG stable elevated ~10, pass1 fail -> pass3 ok
2026-10-18 | Adaptive speed-of-processing training dose GVU (ACTIVE insight) | GVU adjusts dose/modules/boosters on low adherence+progress; smoke pass1 dose3 dual modules -> pass2 dose2 single -> pass3 dose4 with booster
2026-10-19 | Multi-feature speech risk flag (reject single-cue FPs) | GVU rebalances pause/hesitation/lex weights on short sample; pass1 0.308 low -> pass2 0.295 low after short-sample + confidence critique
2026-10-20 | Adaptive multidomain lifestyle coach (Brodaty Nature Med insight) | GVU adjusts module doses on total/adherence/progress critiques; pure-Python loop, smoke shows criteria-driven updates
2026-10-22 | Multimodal contactless Alexa-style speech/video/text MCI screen (Task-Centric Multimodal paper) | GVU multimodal fusion; smoke elevated 0.731 pass1 ok
2026-10-25 | Iterative speech feature refinement for MCI risk flag (DDR/speech biomarker insight) | GVU boosts pause/lex weights on high-risk sample; score low->elevated pass2 ok
2026-10-26 | Wrist-sensor max-speed/running/bedtime incident dementia risk refiner | GVU boosts speed weight on slow sample; score 0.427 fail -> 0.676 pass2 ok
2026-10-27 | Cross-modal acoustic-linguistic fusion weight refiner for AD speech screen (Ding et al. 2026) | GVU lowers threshold and boosts pause weight; borderline flag typical 0.401 -> elevated 0.383 pass2 ok
2026-10-28 | PSD + fluid biomarker (p-tau217/GFAP) fusion weight refiner for early CI speech flag | GVU boosts PSD/blood weights; high-risk sample typical 0.416 fail -> elevated 0.711 pass2 ok
