# Disagreements and fixes - Fable-model review of 04-11-2026

Source: `artifacts/docs/framework/FABLE_REVIEW_041126.md` (verdict PASS-WITH-FIXES on all five artifacts).
"Fix commit" is where the change landed on branch `report/pull-status-081026`. "Re-verified" says whether
anyone other than the fixer has checked the fix; where it says *not yet*, the second Fable pass and the
external auditor are the ones who must. Nothing here is an approval.

| # | Fable finding (short) | What was changed | Fix commit | Still open? |
|---|---|---|---|---|
| 1 | `global_1m` marked RECOVERABLE, but Yahoo serves only ~7 days per request / ~30 days at all, so older rows could wrongly go to SSD | Moved to new class `window_limited_intraday` (NON_RECOVERABLE) until proven | fa774a41 | Closed. Re-class to RECOVERABLE only after a per-broker window probe (not done). |
| 2 | `ohlc` pattern made `opt_ohlc_1m` RECOVERABLE although some rows are live-built (SRC_ORDER has `upstox_live`) | `opt_ohlc_1m` added to the same protected class | fa774a41 | Closed for placement; the real per-broker window is still UNKNOWN. |
| 3 | CSV header misaligned: evidence in the wrong column, `why_needed_for_regime` empty on 171/183 rows | Generator argument order fixed; 183/183 rows now have a reason and a citation | d546abf9 | Closed. Checked by `tests/test_gen_data_needed_instruments.py`; re-verified by this pack's author only. |
| 4 | 24 WORLD_MARKETS rows cited `MARKER-NOT-FOUND`; 6 NSE-report and 2 GAP rows had no cite | Real cites found or UNKNOWN with query; marker count now 0 | d546abf9 | Closed (test asserts 0 markers). |
| 5 | Dhan broker-count row recomputed under no stated rule | Single counting rule stated in the MD (a token must start with the broker name) | d546abf9 | Closed; not re-verified by Fable yet. |
| 6 | 5 rows with store name `upstox_YYYYMMDD.db` classed LIVE_ONLY although `classify()` on that literal returns UNKNOWN | Not a logic change: MD now explains a sample date is substituted before classifying | d546abf9 | **Open by design.** The literal-name classification is still UNKNOWN; real day files carry a date and classify correctly (`tools/check_recoverability_placement.py`). |
| 7 | Census "259 / 269 distinct names" were (broker,name) pairs; true figure 236 / 246 | Census text corrected with the recompute recipe | d546abf9 | Closed. |
| 8 | Design doc called weekly recording OFF; the census proves it ON on both boxes | Sections 2.1, 2.2, 2.3, 7 corrected (Dhan 49, Upstox 47; compose default noted) | 028baa63 | Closed. |
| 9 | `MINT_POLICY` cited to `dp_quorum.py`; it is `broker_login/login_engine.py:50` | Cite corrected | 028baa63 | Closed. |
| 10 | `global_1m` does have a collector (`download_yahoo`); several compose line cites wrong; NSE reports filed under Fyers; "09:35 check" mis-cited | Corrected; `download_yahoo` at `:1012` cited | 028baa63 | **Partly open.** The fixer says cites it did not change were not re-verified. |
| 11 | "Mover skips anything younger than 168 h" is a default, not a fact | Wording changed to default, env-overridable; G2 still stands | 028baa63 | Closed. |
| 12 | Builder: SIGKILL mid-transaction left a hot journal; "resumes" claim overstated; orphan journal | Resume probe rolls the journal back; scratch removal deletes -journal/-wal/-shm; new real-SIGKILL test | a54e97f8 | Closed in sandbox. Final fsync cannot be tested without a real power cut. |
| 13 | Builder: duplicate key with two different `src` resolved by scan order, not SRC_ORDER | Ranked by SRC_ORDER; losers go to `_build_conflicts` and `rows_conflict`; across sources first source wins (recorded) | a54e97f8 | **Open:** whether the real archive has such collisions is UNKNOWN. The cross-source rule is a choice (question Q8). |
| 14 | Tests missed two mutants (stat-guard removed; NULL broker -> "kite") | Added `test_source_moving_during_the_build_publishes_nothing` and `test_null_or_blank_bars_broker_is_unknown_never_a_vendor` | a54e97f8, efec1757 | Closed per the fixer's mutation report (11 of 12 caught); not re-run independently. |

## Where reviewers have not yet disagreed

* No external auditor has reviewed anything yet, so there are **no external findings to show**. Their reply will be added here beside Fable's.
* The Fable-model reviewer and the author share an operator, so agreement between them is weak evidence. Question list: README section 6.

## Findings Fable listed as UNKNOWN or unverifiable (carried forward unchanged)

Real `opt_chain_1m` key and duplicate-supplier collisions; per-broker `recoverable_until`; box `.env` beyond what the census implies; whether `dp_snap` runs; which compose starts the recorders on i7; whether any live file sits under the i5/i7 SSD volume; `rows_raw` datasets per box; the CLAUDE.md path `data/event_calendar.yaml` versus the repo's `config/event_calendar.json`; every number taken from the live census is an agent's self-report.
