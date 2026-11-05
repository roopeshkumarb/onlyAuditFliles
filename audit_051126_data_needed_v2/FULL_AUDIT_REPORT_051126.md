# FULL AUDIT REPORT, 05-11-2026: Fable, Opus, Kimi, Qwen, ChatGPT. Findings, what was fixed, proof.
Rule: nothing here is approved by anyone. FIXED means a change is committed AND a test or measurement shows it; "tests pass" is not proof the design is right. Commits are in the repo branch `report/pull-status-081026`; public audit repo: github.com/roopeshkumarb/onlyAuditFliles (Round 6).

## 0. Scoreboard
| Audited thing | Auditor | Verdict | State |
|---|---|---|---|
| Data-needed list (what to pull) | Fable | NO more data needed, ~75% confidence; no edge demonstrated | Not an approval |
| Data-needed list | Opus R1 | FAIL as written | 9 rows added, 3 corrected |
| Data-needed list + policy gate | Opus R2 | PASS-WITH-FIXES (list may govern a policy; draft deployable outside market hours after fixes) | Fixes F1/F2 done by implementer, NOT re-audited |
| Data-needed list | Kimi (owner says; model not stated in the pasted text) | NO: not full/safe for ML/backtest | G1-G5 recorded; 1 claim disproved |
| Data-needed list | Qwen | NO: full for retail, not safe for ML/backtest as built | G8 added; 1 claim already fixed |
| Tool stack | ChatGPT | generic tool list | No new data requirement; DuckDB not usable on boxes |
| dbclean merge tool | Opus R1 | FAIL (11 defects) | Fixed D1-D11 |
| dbclean | Opus R2 | PASS-WITH-FIXES (1 new high defect) | Fixed; NOT re-audited |
| Weekend DB plan | Opus | FAIL as governing doc (v1) | v2/v3 written; plan not re-audited |
| Live-only gate / old pullers | Fable R1 (04-11) | code PASS-WITH-FIXES, deploy plan FAIL | D1-D9 fixed by implementer; deploy plan NOT re-audited |
| External auditors' formal approval | | none received | PENDING |
| Owner approval | Kumar | | PENDING |

## 1. FABLE (05-11) on the data-needed list  (docs/framework/FABLE_DATA_COMPLETENESS_051126.md)
| Finding | Status | Proof |
|---|---|---|
| Engine reads are covered by the list; preopen_snap, bulk/block deals, news not read by any decision path | Stated, not re-verified by author | Report file:line cites |
| Chain snapshots already captured; USDINR/crude intraday ADD LATER; pre-open auction ADD LATER; GIFT intraday SKIP (t=1.02); depth already recorded; IV term = missing writer | Recorded | no change made |
| equity_1m "ETFs not constituents" conflicts with list | PARTLY RESOLVED | Read-only query on i5 blpro_working.db 05-11: equity_1m holds 52 symbols (constituent names) from dhan since 2025-09-15 (4.39M rows), fyers_backfill 50 symbols 75,000 rows for 4 days (=50x375x4), kite 23. Not measured before 2025-09-15; 52 vs 50 unexplained; code block feature_compute_full.py:50 looks stale (gap G6, untouched). |
| No intraday edge demonstrated (AUC 0.52, momentum/gap/ORB/straddle/GIFT null) | Accepted, nothing to fix | data collection is not the bottleneck |
## 1b. FABLE R1 (04-11) on live-only mode: D1-D9
Fixed by the implementer (commits d6f10f1d, ea093e20, 0fbece24, 760ddf70): compose default `${DP_LIVE_ONLY:-}`, FIFO hang, indexed policy, NEEDED override beats not_needed, class from symbol, deploy plan split, mutants killed. Proof: tests 212 pass (dp_liveonly 57, old_pullers 29, fixes 51, generator 25, universe 28+9, needed_vs_pulled), hand mutation 48/48 killed. NOT deployed; deploy plan not re-audited.

## 2. OPUS on the data-needed list
### R1 (docs/framework/OPUS_AUDIT_DATA_NEEDED_051126.md) FAIL as written
| Defect | Status | Proof |
|---|---|---|
| D1 sector/MIDCAP100/NEXT50 1m read by code, classed NOT_NEEDED | Fixed in list and gate; classifier updated in R2 round | rows U168/U169 (ae721f43); classifier fix 760ddf70 |
| D2 class_name_for makes every non-NSE job RECOVERABLE | PARTLY: options and Yahoo/GLOBAL intraday now protected; plain candles still RECOVERABLE with no window probe | 760ddf70, tests |
| D3 GIFT 1m / Yahoo 1m DXY, US10Y, GOLD missing or DROP | Fixed in list | U170, U171, U051 corrected (ae721f43) |
| D4 NSE F&O bhavcopy, participant_vol, delivery, india_macro missing | Fixed in list | U172-U175 |
| D5 MCX / BANKNIFTY futures contradiction | Fixed in list (U024, U176); classifier fixed R2 | ae721f43, 760ddf70 |
| D6 wrong citations | PARTLY: 25 Yahoo rows fixed; U013/U014/U015/U064 claims narrowed; residual U013/U014 cite, U064, U022, U168 line, U170 docstring lines | f25096ed; residual = gap G7 OPEN |
### R2 (docs/framework/OPUS_AUDIT_DATA_NEEDED_R2_051126.md) PASS-WITH-FIXES
| Finding | Status | Proof |
|---|---|---|
| F1 bare Dhan/Kite numeric ids judged only at generation; no policy expiry | Fixed: policy v3 with master_date + valid_until inside the checksum; expired/undated/v2 policy fails OPEN; generator lists a bare number only if the master proves a cash-equity id | 760ddf70; tests; mutation 48/48 |
| F2 classifier not updated for U168-U176 | Fixed | needed_vs_pulled tests |
| G6 "resolved" was overstated | Downgraded to PARTLY RESOLVED | 95fc79ba |
| Retraction right in direction; "oldest held" is not what a broker serves today; Kite/Dhan do not serve expired F&O | Accepted | BROKER_WINDOW_DAYS renamed BROKER_REQUEST_LIMIT_DAYS, status text only (760ddf70) |
| "~0.02 GB/day" is not an upper bound | Corrected in plan and generated report | 760ddf70 |
| Unproven: id reuse by Kite/Dhan; per-symbol serving depth today; masters behind the draft | OPEN |

## 3. KIMI (owner says; model not stated) and QWEN, external
| Claim | Check by author | Result |
|---|---|---|
| Static NIFTY 50 constituents = survivorship bias; need point-in-time history | agree (also Opus item 6) | OPEN, gap G1: needs NSE circulars, example names unverified |
| Rule history (lot size, expiry day, costs by date) missing | agree; no config/rule_history exists | OPEN, gap G2: quoted 75 to 65 unverified |
| News: ~7 days at Upstox; keep out of ML/backtest | agree in principle | News marked LIVE/PAPER ONLY (U065 note); archive OPEN, gap G3; 7 d unverified |
| Futures roll gaps need adjustment | unverified whether engine adjusts | OPEN, gap G4 |
| Index volume zero pre-2025; use futures traded volume | ALREADY IMPLEMENTED | feature_compute_full.py ~167, 226-229 (futures traded volume, NaN where unmeasured); other consumers not all re-checked |
| Reclassify ALL 1m as NON_RECOVERABLE (Fyers 100 d, Upstox 28 d) | NOT SUPPORTED. Those windows were my own wrong figures given to the auditors. | RETRACTION published (onlyAuditFliles 9bc8b73). Measured oldest 1m HELD (coverage.db i5 and i7, 05-11): Kite 2015-01-13, Dhan 2017-04-03, Fyers 2017-07-17, Upstox 2022-01-03; NIFTY spot 1m held: Upstox from 2022-01-03 (574,776 rows i5). Gap G5. |
| backtester.py:81 uses bars_held/375.0 | LINE VERIFIED | option time-decay term with fixed session; impact on real data unmeasured; gap G8 OPEN |
| PP-12 execution record needed for paper slippage calibration | plausible, not verified live | OPEN |
| Live sessions SAFE | not independently verified | n/a |
Note: both external texts were pasted by the owner; condensed versions with these checks are in the public repo (AUDITOR_RESPONSES, 4733b93 and 66d9ae8). Kimi and Qwen could not fetch GitHub links; they audited from pasted text.

## 4. CHATGPT (tool stack): no data finding; DuckDB/Parquet not available on the boxes (measured: sqlite extension not fetchable, Alpine Pi no wheel). Sensible ideas (release manifest, Prometheus/Grafana, resource-aware dispatcher) are NOT built.

## 5. OPUS on dbclean (docs/framework/OPUS_AUDIT_DBCLEAN_051126.md and _R2_)
R1 FAIL: D1 rows silently lost when >24 weekly files open (critical), D2 false EXCESS-CANDIDATE, D3 distinct rows merged, D4 provenance dropped, D5 one bad row stops run, D6 crash after a source is moved, D7 NULL keys, D8 conflicts not idempotent, D9 read-only open writes -shm, D10 source changing mid-merge, D11 foreign canonical file.
Fixed in 1cd279a0 + da54a3cc; proof: 18 tests then 32 tests pass (regression per defect), Opus R2 re-ran 310 random trials with 0 mismatches (80 span 40-60 weeks) and 20 kill -9 runs identical.
R2 PASS-WITH-FIXES: new high defect (corrected source value lost; conflicts keyed without the incoming row), verify crash on new -wal, box label, hot journal. Fixed in 0284382f (+65319108 bound verify cache after an out-of-memory kill at 1 GB on i7). 32 tests pass. NOT re-audited after these fixes. Still open: D10 mid-merge change, ~8 full reads per source, no directory fsync.
Run evidence on i7 (cold copies only): 9 files merged (dhan 13.4M, fyers 23.1M, kite 6.1M, nse 10.7M raw rows, upstox 3.78M candles + 173k raw), verify finished with ok=True for 9 sources, excess.tsv produced (19:28). That run used the code BEFORE 0284382f; it is not evidence for the final code. Do not act on excess.tsv.
Cross-check: sqlmerge.sh (plain SQL via official sqlite3), dbclean and an independent Python model agreed exactly on one random fixture (weeks 21/41/38 rows, conflicts 3/9/5). One fixture, not a proof.

## 6. OPUS on the weekend DB plan v1: FAIL (merge key did not exist, source ranks, immutable/WAL, copy-by-name, delete weaker than policy, IO gate, power-loss, DuckDB casts, Drive gaps, week zones, consumers). v2/v3 amendments written (2113fe21, adafb53d). Not re-audited; nothing moved or deleted.

## 7. WHAT IS STILL OPEN (ranked)
1. Approvals: external audit formal answer, Opus re-audit of implementer's R2 fixes and of the deploy plan, owner yes.
2. G1 point-in-time constituents, G2 rule history, G4 roll adjustment, G3 news archive, G7 residual citations, G8 375-bar assumption.
3. Policy draft is built from 04-11 exports and expires after 2026-11-05: must be rebuilt from fresh exports before any deploy.
4. Disk load: the policy removes little new write load; old-puller reads/backfills need a separate throttle.
5. Space: i7 gate still closed on the 40% free-space rule; i5 gate opened by Kumar's written authorization (D12).
