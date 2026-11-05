# Adversarial audit: is the DATA-NEEDED list safe to govern a live-only pull policy? (05-11-2026)
Auditor: Claude Opus 5.5 (claude-opus-5-5), independent. Read-only; scripts in /tmp/audit (fwd.py, rev.py, sim.py).

## Verdict: FAIL as written; PASS-WITH-FIXES once the 6 ADD rows below and fixes D1-D4 are in.
The live-only gate itself is built safely (`pullers/dhan/dp_liveonly.py:244-266`: it refuses only a key that is listed NOT_NEEDED **and** RECOVERABLE, and UNKNOWN or unlisted keys are allowed). But the list misses inputs the code reads, and the gate's recoverability test is wrong for window-limited intraday data (D2).

## 1. Forward proof
The file has 167 rows, not 165, and 215 citations. All 215 file:line citations exist. 197 contain their cite token at that line. 10 cite CLAUDE.md only, with no code reader. 18 rows have no consumer. Six citations exist but do not read what the row claims:
* U022-U050 (Yahoo daily) cite `global_cues.py:84`. That line reads `global_cues_1m`, which is built from **1m** Upstox GLOBAL_* and Yahoo bars (`tools/global_wire.py:144-161`). Only 16 series feed it. ASX200, BTC, COPPER, EURUSD, KOSPI, NASDAQ, RUT, SSE, SILVER, US2Y, USDJPY and VIX_US daily feed nothing there.
* U022 cites `global_cues.py:38`, which is a label tuple, not a read.
* U024 (MCX) cites `global_cues.py:84`. The real reader is `global_context.py:231` (`macro_1d`).
* U064 cites `constituents_top20.py:216` (`_prior_session`). That code reads no membership: the list is the static `config/nifty50.py`.
* U013/U014 cite `regime_6m_build.py:69` (`options_chain_summary`). That table's history comes from the **NSE F&O bhavcopy** (`daily_recorder.py:90`); only today's row comes from live snapshots (`daily_writers.py:235`).

## 2. Reverse proof: inputs the code reads that no row covers
| Input | Read at | Classifier today | Recoverable? |
|---|---|---|---|
| Sector indices + NIFTY MIDCAP 100 + NIFTY NEXT 50, 1m (`index_1m`) | `derived_wide.py:452-489` (datasets 109/110/112/115); `feature_compute_full.py:890` | NOT_NEEDED (bulk reason 1) | Only inside the broker window (Fyers 100 d); older minutes are lost |
| GIFT NIFTY **1m** (Upstox `GLOBAL_INDEX\|SGX NIFTY`) + Upstox GLOBAL_INDEX/INDICATOR 1m (DJI, SPX, BRENT, WTI, USDINR...) | `global_wire.py:89-103,144` -> `global_cues.py:84`, `regime_forecast2_export.py:38` | UNKNOWN or NOT_NEEDED, depending on the master (sim.py: master name "SGX NIFTY" gives NOT_NEEDED) | Unproven |
| Yahoo 1m DXY / US10Y / GOLD (U051 = DROP) | `global_wire.py:147-150` | outside the coverage ledger | **No**: Yahoo serves ~30 d, then lost |
| NSE F&O bhavcopy (NIFTY contracts) | `eod_pit.py:156`, `options_context.py` (judge gate 18, `judge_engine.py:106`), `options_chain_summary` | NOT_NEEDED ("duplicates broker candles", which is false: broker candles have no EOD OI of expired strikes); `fo_bhavcopy` snap = UNKNOWN | Yes (NSE archive) |
| participant_vol | `eod_pit.py:130` | NOT_NEEDED (`needed_vs_pulled.py:49`) | Yes (NSE archive, 2012+) |
| CM bhavcopy / MTO delivery, `india_macro` | `eod_pit.py:218,229,242` | no row | Yes / manual |
| BANKNIFTY future daily | `global_context.py:55,224` | NOT_NEEDED | Yes, within the window |
| MCX crude/gold daily (U024 = OPTIONAL_KEEP) | `global_context.py:231` | NOT_NEEDED: the classifier treats every non-NIFTY future as unneeded, which contradicts U024 | Expired months: no (Dhan serves only active contracts) |

These are covered: VIX pre-2025 fallback (U010 futures realized vol), `fut_1m traded_volume` (U010), all 50 constituents (they match `config/nifty50.py` exactly), holidays (U058), event calendar (U067), masters (U060-063), and the NIFTY option chain (U014). Native 5m/15m is never read: `mtf_regime_engine.py:136`, `regime_spine.py:235,311` and `multi_timeframe.py:170` all resample 1m or daily data. U054/U055 say "nothing reads it", but `eod_pit.py:280` reads `derivative_activity`.

## 3. The five NOT_NEEDED bulk reasons
1. Unnamed indices: **NOT SAFE**. Sector indices, MIDCAP 100 and NEXT 50 are read (table above). Recoverable only inside the broker window.
2. NSE contract-level daily: **NOT SAFE** unless `tools/nse_reports.py` (the lake) keeps fetching the FO UDiFF files, because the engine's copy is built from the lake (`nse_eod_copy.py`). Recoverable from the NSE archive.
3. Equities outside the NIFTY 50: **SAFE today**, but the list is static. At the next NIFTY 50 rebalance an entering stock's ticks are lost for good and its 1m is recoverable only within the window. Needs a rule that follows `index_membership`.
4. Fyers 5s-45s: **SAFE** (no reader). But the gate calls them RECOVERABLE without any probe, so stopping them is an owner decision to lose them for good.
5. Stock F&O / MCX: **SAFE for stock F&O. NOT SAFE for MCX crude/gold and BANKNIFTY futures**, which `global_context` reads.

## 4. Ranked defects
* **D1 (high).** Sector, MIDCAP 100 and NEXT 50 1m will be refused. Loss: all derived_wide 109/110/112/115 history older than ~100 days.
* **D2 (high).** `dp_liveonly.class_name_for` (`:229-241`) maps every non-NSE, non-expired job to `history_candles_<src>_<iv>`, so it always returns RECOVERABLE. That bypasses `recoverability.json`'s `window_limited_intraday` rule (global_1m, opt_ohlc_1m) and probes no window. Loss: any window-limited key listed NOT_NEEDED (Yahoo/Upstox global 1m, Fyers seconds) is gone for good.
* **D3 (high).** No GIFT 1m row (U018 is 1D only, U019 is ticks), and U051 is DROP. Loss: the GIFT/DXY/US10Y/brent inputs of the gap cue. `global_cues_1m` has been stale since 16-10 (`lc_families.py:466`), so this loss has already started.
* **D4 (medium).** No rows for the F&O bhavcopy, participant_vol, delivery/MTO or `india_macro`, which feed the edge-research reader (`eod_pit` -> `edge_ladder.py:157`) and judge gate 18.
* **D5 (medium).** The classifier contradicts its own rows: MCX (U024), and GIFT detection depends on the master's name text, not on the U018 key.
* **D6 (low).** Wrong citations (section 1). U015 names no strike band, so a puller that follows the list cannot know which strikes to pull.

## 5. Rows to ADD
1. NSE sector indices + NIFTY MIDCAP 100 + NIFTY NEXT 50, 1m (`index_1m`), REQUIRED_ENGINE.
2. GIFT NIFTY 1m + Upstox GLOBAL_INDEX/INDICATOR 1m, REQUIRED_ENGINE, window-limited.
3. Yahoo 1m DXY / ^TNX / GC=F (change U051 from DROP to REQUIRED_ENGINE), NON_RECOVERABLE.
4. NSE F&O UDiFF bhavcopy (NIFTY contracts) + participant_vol + CM bhavcopy/MTO delivery + `india_macro`.
5. BANKNIFTY near-month future 1d; MCX crude/gold daily (make the classifier honour U024).
6. A membership-follow rule: the constituent rows equal `index_membership` of the prior session, not a static 50.

## 6. Unproven
* The Upstox master names for the GLOBAL_* keys. The masters were not in /tmp/board, and the upstox DBs on i5 have no `instruments` table.
* Per-broker windows for index 1m, Fyers seconds and Upstox global 1m.
* Whether `tools/nse_reports.py` falls under the stop policy.
* No `pull_policy.json` is deployed yet (the i5 `_state` directory holds none), so nothing has been refused so far.
* GB/day of live data, which the coverage ledger does not see.
