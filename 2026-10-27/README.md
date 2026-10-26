# 2026-10-27: Cross-modal Speech+Text AD Risk Flag GVU

**Opportunity**: Diagnostics/Biosensors — Iterative refinement of acoustic-linguistic fusion weights for early AD speech screening (Ding et al. Neural Computing and Applications 2026 cross-attention seed).

**Base insight prototyped**: Bidirectional cross-modal attention between Whisper-style acoustic features (pause ratio) and BERT-style linguistic features (lexical diversity) can be self-improved via GVU critique against labeled examples.

**Verifier criterion**: Predicted flag must match true label; score in [0,1]; weights sum ≈1.0.

**Smoke result**: Borderline sample flag typical → elevated after 2 passes (threshold/weight update).

Run: `python3 gvu_crossmodal.py`
