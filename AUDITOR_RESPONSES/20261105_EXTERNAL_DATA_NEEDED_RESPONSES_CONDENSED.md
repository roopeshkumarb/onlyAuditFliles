# External responses to Round 6 (05-11-2026), CONDENSED BY THE AUTHOR (not verbatim; the owner holds the full texts)
Two outside responses were pasted by the owner. Neither is recorded as an approval. The author's check of each claim follows.

## Response 1 (model not stated): verdict NO, "neither full nor safe for ML, backtest, paper"
| Claim | Author's check |
|---|---|
| 1m series marked RECOVERABLE will be lost (Fyers 100 d, Upstox 28 d); reclassify ALL 1m to NON_RECOVERABLE | PARTLY WRONG / UNPROVEN. The 28/100-day figures were given to the auditor by the author for specific datasets; CLAUDE.md shows Nifty 1m held from 2022-01-03, so at least one source serves years of index 1m. Window-limited sector/Fyers series are real (Opus audit D1). Per-broker depth must be MEASURED (task T-0832) before any reclassification. Gap G5. |
| Index volume is zero pre-2025; features must use fut_1m traded volume | ALREADY A RULE (CLAUDE.md 2.2) and applied in regime_6m, feature_compute_full, derived_wide, timeframe_grid, exit_context. Fable: the ML path reads OHLC only. Not re-verified on every consumer. |
| Static constituents = survivorship bias; need point-in-time membership | AGREE. Same as Opus item 6. Gap G1. The example history in the response is UNVERIFIED and must not be copied. |
| Add rule_change_history (lot size, expiry day, costs by date) | AGREE as a backtest requirement. Gap G2. The quoted lot sizes (75 to 65) are UNVERIFIED. |
| News: Upstox ~7 days; no historical archive; quarantine news from ML/backtest | AGREE in principle (window UNVERIFIED). Decision recorded in U065 and gap G3. |
| Continuous futures roll adjustment needed for backtests | UNVERIFIED whether the engine does it. Gap G4. |
| Live sessions SAFE | Not independently checked by the author. |

## Response 2 (ChatGPT): generic tool stack (Codex CLI review, GitHub Actions, Ansible, Prometheus/Grafana, DuckDB/Parquet/Polars, Semgrep/Ruff, VectorBT, news tools)
It states it inspected only the audit pack. Author's notes: DuckDB's SQLite extension could not be fetched through the sandbox proxy and DuckDB has no wheel for the Alpine Pi (measured 05-11), so DuckDB is not available on the boxes today. A resource-aware dispatcher and release manifest are sensible but are not built. It repeats open items already listed (D1-D6, U059 vs U168, U064 static membership, the equity_1m ETF-vs-constituent conflict). No new data requirement beyond G1-G4.

## Also on record
Fable (05-11): NO more data needed for the intraday directional engine (confidence ~75%) and no edge demonstrated. Verdicts differ because the questions differed: Fable judged "more data for direction"; Response 1 judged "safe for ML/backtest/paper".
