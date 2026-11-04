# FABLE REVIEW ROUND 5, 04-11-2026 (independent, read-only, report/pull-status-081026)

Six pack test files: **118 passed, 1 skipped**. Mutants and attacks ran on a scratch copy; repo untouched except this file. Line numbers are mine.

## 1. Universe (json, generator, tests, doc) - PASS-WITH-FIXES as a list; FAIL as "foolproof"

Opened 30+ rows' cites. The three engines' inputs all have REQUIRED_ENGINE rows and every LIVE_ONLY store classes NON_RECOVERABLE. Defects:

1. `gen_retailer_edge_universe.py:107` U010 cites `regime_6m.py:177` as a fut_1m consumer. False: `tools/regime_6m_build.py:42` feeds regime_6m `nifty_1m.vol`, the index vendor aggregate CLAUDE.md 2.2 forbids. Wrong cite, **and the engine uses the proscribed series as its volume evidence** - escalate to Kumar.
2. Dead/wrong cites: `:193,:197` "CLAUDE.md:21" is a blank line (Tuesday rule is :16); `:138` CLAUDE.md:15 is fut_1m, not opt_ohlc_1m; `:77` meta_label.py:57 is atr_pct; `:192` corporate_actions.py:16 is a docstring - that module reads equity_1m/nifty_1m (`:94-121`), never the NSE `corporate_actions` store, so U056's engine consumer is false. `tests/test_retailer_edge_universe.py:76-85` checks only that the line number fits the file: a non-check.
3. `:205-207` U065 event calendar LIVE_ONLY "RAID HDD directly (all brokers in parallel)" contradicts CLAUDE.md section 3 (SSD + cloud sync, Pi5).
4. `:167-169` U023 NOT_AVAILABLE_AT_RETAIL rests on the Dhan master alone; `dp_tickrec.py:138-162` subscribes a Kite CDS USDINR future. Must be UNKNOWN.
5. `:214` fyers/kite constituent ids are string-formatted, not read from a master; `tests:41-43` accepts them as suppliers (100 cells).
6. No decision row at all for `breadth_1d` (in data_needed csv) and `sector_1m`.
7. `test_no_live_only_row_is_recoverable` tests the universe's own `store` labels, not recorder file names; `edge_universe_coverage.py:16-28` checks service names only: `TICK_EXTRA=0` would uncover U006/U012/U021 and 50 tick rows with exit 0.

Sign today: **No.** After 1-4 and 6, plus a cite test that checks a token on the cited line: yes as a draft list, never as "foolproof".

## 2. Compose / edge_health / cutover proof / coverage / runbook

Compose touches nothing old (own project, network, root; `_auth`/code `:ro`; no cloudflared/portainer/blpro_09/login); live-only data reaches an SSD only if EDGE_ROOT names one. Defects:

8. `.env.retailer_edge.example:4` `COMPOSE_PROFILES=live,hist` and the header command (`compose:8 --profile live`) start `edge_depth`: +2 Dhan sockets = 6, Dhan kicks the OLD recorder - exactly what `compose:14-16` and runbook section 2 forbid. Default must be `hist`.
9. `compose:118-139` edge_hist has no `/lease` mount (old compose `:195`); `planner.py:832-842` plans Kite work only on the lease box. The new puller either queues dead or double-pulls on the same account beside the old fullpuller (shared REST limit). The history side has no shadow protocol and no parity harness (section 6.3 hand-waves `coverage.db`).
10. `edge_cutover_proof.py`: six new mutants, **six survived**: C1 `:320` sessions = max over feeds (a 1-session feed passes beside a 3-session one); C2 `:327`; C3 `:325` old-side corruption; C4 `:227`; C5 `:246`; C6 `:51`. Attacks: A1 new writes 3x rows (reconnect storm, distinct recv_ts) PASS, ratio 2.996 - no ceiling; A2 new stores NULL exch_ts PASS, empty why (`:256-259`); A4 `required_keys` not reachable from the CLI (`:360-389`), so "0 instruments missing" cannot be asserted for keys old never had.
11. `edge_health.py:65-76` backwards-count state sits in container `/tmp` (lost on the restart it should catch); H3 (`n < prev//2`) and H2 (low impact) survived.

Acceptance bar: sound in shape (box-swap for Dhan, cross-box compare, declared thresholds, no PASS without baseline). **Not sufficient to stop the old pullers**: depth/Upstox/Fyers - the OI/IV/depth the regime needs - are proved per feed, never per instrument (G-raw); no history-side proof; no row ceiling; silent latency; C-keys, G7, G2-run open. Verdicts: compose PASS-WITH-FIXES (8, 9); proof PASS as measurement, **FAIL as a stop-gate** (10); health, coverage, runbook PASS-WITH-FIXES. Sign today: No. After 8 and 10 (A1, A2, A4, C1) are fixed with tests I would sign the compose for a Kite-only box-swap shadow, not for stopping anything.

## 3. dp_seal.py + tests + SEAL_MUTATION_LOG - FAIL today

12. `:205` the candles plan item is tagged `"candles"`, so `:241` records the SSD-resident candles segment as `place='box_hdd'` (F1). `move_to_hdd` `:272-274` never copies candles to HDD, and with ALLOW_REMOVE one real off-SSD copy makes `removable()` list it: the largest recoverable class never reaches HDD and the delete gate is fooled. Mutant D4 survived: untested.
13. `:222-228` ALREADY_SEALED trusts the file name: a kill between `:171` rename and `:242` ledger insert, or a lost ledger (F2), leaves a segment the ledger never sees. Contract 5 false there.
14. `:122` mode=ro on a power-cut leftover (main + -wal, no -shm): writable dir creates an -shm beside the source (F3; `tests:149-163` checks only the URI); read-only medium -> SourceRefused (F3 as `nobody`). Contract 1 half-true.
15. `:141-173` nothing checks rows written == nsrc (D3 "first chunk only" survived); `:210` a dataset name with "/" aborts with a raw OperationalError (F5).


Fault injection: disk full (RLIMIT_FSIZE) left nothing final, rerun SEALED; corrupt source refused; rows_raw split sends mixed-case and unknown datasets to HDD - no SSD leak. D1, D2 CAUGHT. Log honest; add D3/D4/F1-F3. Sign: after 12-14 fixed with tests, PASS-WITH-FIXES.

## 4. retailer_db_build.py WAL (round-4 defects)

5 **FIXED** `:260-269,:296-313,:588-599`, tests `:559-702`. 6 **FIXED** `:441-447`. 7 **FIXED** `:694`. 8 **FIXED** `:620-639,:653-657,:698`. 9 disclosed, not fixed `:342,:557`; `src_rank:82` dead. **PARTLY**: `:309` hold-still check is size + mtime_ns; on exFAT/SMB (2 s granularity) a torn main/-wal copy passes, SQLite drops mismatched-salt frames silently, quick_check ok. PASS-WITH-FIXES; would sign for Linux, ext4/btrfs sources, journal or WAL, medium stated in the ledger note.

## Not verifiable here
Boxes, Dhan socket count and account topology, edge_hist lease behaviour live, real `niftybkp.db`, Kite CDS entitlement, fsync under a real power cut.
