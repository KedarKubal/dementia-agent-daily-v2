# 2026-10-02 — Closed-loop module coach (Maintain Your Brain seed)

Prevention/digital-therapeutics slice of Brodaty et al., Nature Medicine 2025.
The trial assigned 2-4 online modules but did not close the loop on adherence
and a cognitive proxy. This folder is a 3-pass Generator-Verifier-Updater
that drops overloaded or non-adherent modules and raises cognitive dose when
the proxy declines.

## Run

```bash
python gvu_module_coach.py
```

Success criterion (verifier, all must hold):

- at most 2 active modules
- top risk factor covered unless its adherence is below 0.60
- no active module with adherence below 0.60
- doses in [2, 5]
- if cognitive proxy delta < -0.05 and cognitive_activity is active, dose >= 4
