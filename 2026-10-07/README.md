# 2026-10-07 — Embedding-discard ADRD speech screen

Fork base (do not vendor): https://github.com/deepgram/examples/tree/main/examples/310-crewai-voice-agents-python

Insight prototyped: Li et al. 2025 (arXiv:2506.11119) found Whisper-medium ASR embeddings beat transcript models for HC/MCI/AD classification. This slice keeps only the embedding distance and refuses any lexical payload.

Verifier success criterion (all must hold):
- no keys in {transcript, tokens, words, lexical_excerpt, keyword_hits}
- discarded_lexical is true and basis is asr_embedding_distance_only
- referral_flag is true iff embedding_cosine_distance_to_hc >= 0.42

Run: `python3 gvu_embedding_screen.py`
