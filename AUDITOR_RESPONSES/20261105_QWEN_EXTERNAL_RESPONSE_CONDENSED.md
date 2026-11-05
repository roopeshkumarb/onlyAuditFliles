# External auditor response: Qwen (05-11-2026 night) - CONDENSED BY THE AUTHOR; the owner holds the full text. No approval recorded.
Qwen's first line: NO. The list is as full as retail constraints allow but NOT SAFE for ML or backtesting as built (survivorship, volume, rule changes). It rates Live SAFE and Paper PARTLY SAFE, conditional on deployment.

| Qwen claim | Author's check (05-11) |
|---|---|
| Institutional gaps (signed flow, GEX, historical depth) are acceptable and correctly excluded | Consistent with CLAUDE.md. Not independently verified by the author. |
| Momentum E1 contradicted on NIFTY (slope -0.0149, NW-t -0.73) | Matches the repo's null edge results as reported by the Fable audit (no edge demonstrated). Figures not re-run. |
| Static 50 constituents = survivorship bias; need point-in-time history | AGREE (gap G1). The example names in Qwen's text (BSE, JioFin, Wipro) are UNVERIFIED and not used. |
| nifty_1m volume is 0/missing before mid-2025; features must use futures traded volume | ALREADY IMPLEMENTED in feature_compute_full.py (lines ~167, 226-229: futures traded volume, NaN where unmeasured, per CLAUDE.md 2.2). Qwen's 'expanding mean fabrication' description refers to older code (T-0206). Other consumers not re-verified. |
| News: Upstox ~7 days, cannot train NLP; quarantine from ML | AGREE in principle (gap G3). The 7-day window is UNVERIFIED. |
| Rule history (lot size 75->65, expiry shifts) missing | AGREE as a requirement (gap G2); no config/rule_history file exists. The quoted lot sizes are UNVERIFIED. |
| Continuous futures roll adjustment missing | UNVERIFIED whether the engine adjusts (gap G4). |
| backtester.py:81 uses bars_held/375.0 | LINE VERIFIED exactly as quoted. It is an option time-decay term, so the harm is a fixed-session assumption; impact on real data unmeasured (new gap G8). |
| PP-12 execution record needed to calibrate slippage in paper trading | Plausible requirement; the author did not verify PP-12 capture is live. |
| Live safe only if H12 routing and livewatch are deployed | Not independently verified here. |
