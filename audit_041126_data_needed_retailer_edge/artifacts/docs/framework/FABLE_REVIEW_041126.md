# FABLE REVIEW 04-11-2026 (independent, read-only, branch report/pull-status-081026)

No box touched. Every number was recomputed from the CSVs or by opening the cited file; mutations ran on scratchpad copies only.

## Verdicts

| # | Artifact | Verdict |
|---|---|---|
| 1 | DATA_NEEDED_INSTRUMENTS_041126.md + CSV | PASS-WITH-FIXES |
| 2 | LIVE_CENSUS_041126.md + CSV | PASS-WITH-FIXES |
| 3 | RETAILER_PULLER_DESIGN_041126.md | PASS-WITH-FIXES |
| 4 | tools/retailer_db_build.py + tests | PASS-WITH-FIXES (14/14 pass; 2 of my 2 code mutants survived) |
| 5 | config/recoverability.json (commit 93f9b296) | PASS-WITH-FIXES (one dangerous row: `global_1m`) |

## What recomputes (confirmed)

- CSV 1: 183 rows; 83/91/9 by class; tier and group tables exact. All 207 `file:line` cites exist; 24 sampled lines say what the row claims.
- Census: Kite 202 (72/72/3/2/53), Dhan 49, Upstox 47, Fyers 5 per box; Kite 82 monthly + 62 weekly = code defaults ±20/±15; 123 / 87 files, 238.9 / 236.0 GB (decimal) and per-broker GB recompute from bytes.
- Census vs code: all 50 CSV constituents present on both boxes; census-only names NIFTY BANK, NIFTY FIN SERVICE, NIFTYBEES are declared TICK_EXTRA rows in the CSV. Code-only: USDINR/CRUDE/GOLD (TICK_EXTRA_MACRO, OFF as declared), GIFT live (no recorder). Dhan 26 weekly + 22 monthly + 1 fut and Upstox 22 + 22 + 1 + 2 equal the code's `weekly6_monthly5` (48+1) and `weekly5_monthly5` (47) pickers: **weekly recording and TICK_EXTRA are ON on both boxes**, resolving CSV-doc UNKNOWN #3.
- recoverability.json: all 36 `dp_families` tables classify (0 UNKNOWN); 25 tests pass; NON patterns tested first; real day-file names classify NON.

## Defects

1. **recoverability.json:102 `global_1m` is RECOVERABLE** under `history_candles`, but the repo's own `pullers/fullpuller/download_engine.py:160` caps Yahoo 1m at a 7-day window. Rows older than 7 days cannot be re-pulled; this class lets them onto SSD. Give it its own class with `recoverable_until: 7 days` or mark NON.
2. recoverability.json:90 pattern `ohlc` makes `opt_ohlc_1m` RECOVERABLE although CLAUDE.md 1.2 SRC_ORDER shows rows built from `upstox_live`/`fyers_live`; recoverability depends on an unprobed expired-contract window. Needs `recoverable_until` or a per-src rule.
3. CSV header misaligned: `file:line` evidence sits in column `count_by_code`, prose in `evidence`, `why_needed_for_regime` empty on 171/183 rows. An auditor reading by header finds no evidence.
4. CSV: 24 WORLD_MARKETS rows cite `dp_instruments.py:MARKER-NOT-FOUND(...)` - a generator failure printed as evidence; 6 NSE_REPORT and 2 GAP rows have no cite.
5. DATA_NEEDED md section 2, dhan row (10/57/4) recomputes under neither exact-token (10/57/1) nor substring (11/58/4) counting; the counting rule is unstated.
6. CSV: 5 rows with store `upstox_YYYYMMDD.db` are classed LIVE_ONLY, but `dp_recoverability.effective()` on that string returns UNKNOWN (`upstox_20` pattern needs a real date). Harmless direction, but not produced the way md line 5 claims.
7. Census md line 20: "distinct instrument names 259 / 269" is actually distinct (broker, name) pairs; true distinct names are 236 per box, 246 union. Line 18 notes the Dhan label collision but not Upstox's (25 names for 47 keys).
8. Design doc 2.1 and 2.2 call weekly recording "PARTIAL (built, OFF)" and section 7 lists it as pending approval; the census proves it ON on both boxes for Dhan and Upstox today. 2.2's "ATM±12 (50 inst.)" is the compose default, not what runs (49).
9. Design doc 2.3: "MINT_POLICY (`dp_quorum.py:14-18`)" is wrong; MINT_POLICY is `pullers/broker_login/login_engine.py:50`; dp_quorum:14-18 is the majority proof.
10. Design doc 2.5: "no collector found for `global_1m`" - `download_engine.py:1012 download_yahoo(..., interval="1m")` fills it (7-day history). Compose cites `:316`, `:358`, `:365-366` point at a service header, `profiles:` and the `/src` mount, not the HDD mount / `DEPTH_WEEKLY_STRIKES`; NSE reports and the event calendar are filed under Fyers Prime (2.4); "09:35 check" is the 09:26 T-1311 note.
11. Design doc finding 3: `MIN_AGE_H`/`MIN_BYTES` are env-overridable (`ssd_to_hdd_move.sh:7`); "skips anything younger than 168 h" is a default. G2 still stands (epoch DB is live-appended).
12. **Builder, resume overclaim** (`retailer_db_build.py:31-32, 419-432`): attack 1 (SIGKILL inside a unit's transaction, the power-cut case) left `.building` + a hot `-journal`; the read-only probe at :422 fails ("attempt to write a readonly database"), so finished units are discarded and everything is rebuilt (BUILT, not RESUMED). Output correct, integrity ok, no half file at the final path. `os.remove(tmp)` at :432 leaves the orphan journal, safe only because SQLite drops a journal for a zero-page DB. Remove `tmp + "-journal"` too and probe read-write, or document "resume only between units".
13. **Builder, SRC_ORDER not applied** (`:300-312`): attack 2, one source holding the same (dt,strike,opt_type,expiry_flag) under two `src` values, stamps whichever row the scan yields first (forward -> fyers, reversed -> upstox) and counts the loser as `rows_dup`, indistinguishable from a true duplicate. Whether the real archive has such collisions is UNKNOWN (no `CREATE TABLE opt_chain_1m` in non-test code; docstring :24 admits the key is inferred).
14. Test gaps (mutants on copies, 14/14 still pass): M3 deleted the post-read stat guard (`:463-466`); M4 made `_map_bars` (`:155`) turn a NULL broker into "kite" - "never invented" is untested on the broker_bars path, which also never checks the carried broker against `VENDORS`.

## Still UNKNOWN

Real `opt_chain_1m` key and duplicate-src collisions; per-broker `recoverable_until`; box `.env` beyond what the census implies; whether `dp_snap` runs; which compose starts recorders on i7; whether any live file sits under `/volume2`; `rows_raw` datasets per box; CLAUDE.md's `event_calendar.yaml` vs the repo's `config/event_calendar.json`.

## Not verifiable from this sandbox

No box, status.json, docker, `.env`, `_state/instruments.db` or live DB was reachable. The census CSV is accepted as reported by agent B; only its arithmetic and its consistency with the code were checked. T-1311 notes are self-reports. Yahoo's 7-day limit is the repo constant, not re-measured. Defect 8 rests on the census; 12-13 on this checkout only.
