# FABLE REVIEW ROUND 7, 04-11-2026 (independent, read-only, report/pull-status-081026)

Pack: **297 passed, 1 skipped** (12 files). 37 mutants and 3 faults ran on scratch copies; `docker compose config` (v5.6.0) parsed the real compose with the example env: default = `edge_hist`, `--profile live_dhan` = `edge_depth` only, `_auth`/`/src` `read_only: true`. Line numbers are mine.

## Round-6 defect table

| # | status | opened |
|---|---|---|
| 1 regime_6m volume | FIXED | unchanged, `regime_6m.py:50-58,:276` |
| 2 / N5 cites | **PARTLY** | registry pins exact text, `gen:298-305`, `test:61-77,:144-186`; my `:132`->`:90` attack now fails. But the registry is **written by the same generator** (`gen:302-305`), so it pins whatever `add()` accepted; and a consumer string with no `:line` is skipped by both (`gen:73-74`, `test:132-134`): `U013` "derived_wide.py (call/put wall...)" is unchecked, and a forged REQUIRED_ENGINE row citing `nonexistent.py (reads it)` passes every test (ran it). 9 of 33 pins are doc/import lines (`CLAUDE.md` x6, `constituents_top20.py:118` an import, two docstrings) |
| 3-6, 8, 10-13, 15 | FIXED | unchanged from round 6 |
| 7 / N4 coverage env | FIXED | `edge_universe_coverage.py:25-29` empty env by default, `:107-130` `--env-file`, exit 2 without it; `TICK_EXTRA=0` in a box file = gap (verified) |
| 9 snap prefs swallow | FIXED | `planner.py:1067-1081` fail closed; `test_planner_snap_failclosed.py` 3/3. Lease/topology still unmeasured |
| 14 mode=ro -shm rewrite | FIXED | `dp_seal.py:180-195` F_GETLK probe, `:264-271` snapshot unless a live holder; `:154-177` header check; fault F2 below: SIGKILL picture, source bytes identical, 26/26 rows |
| N1 subset PASS | FIXED | `:46-50,:472,:545-547,:560`, exit 5 `:696`; 7 tests. Residue: `:472` uses `FEEDS` not `ALL_FEEDS`, so a 4-recorder run without `--with-snapshots` is still PASS/exit 0 (NOTE `:543` + `retirement_scope` carry the limit; runbook `:117` agrees) |
| N2 garbage -wal | FIXED | `:154-177,:242-245`; 6 tests. In-place live path `:272-275` skips the header check (the holder wrote that -wal: low) |
| N3 lost rows | FIXED | `:455-458`, test `:826` |
| N6 CLAUDE.md 2.2 | **PARTLY** | `feature_compute_full.py:216-236` volume = futures traded volume, NaN unmeasured; OBV/VWAP `:166-189`; percentile `:946`; `derived_features.py:144-148,:276-279`; `exit_context.py:173` no index fallback: all FIXED. **Not fixed: see N7-N9** |

Round-6 survivors P1-P3, P5-P8, S1, S3, S4, S6 now have tests (`test_edge_cutover_proof.py:667-785`, `test_edge_health.py:173-200`, `test_dp_seal.py:856-936`).

## Not verifiable here
Boxes, Dhan socket count and account topology, the lease beside the old fullpuller, whether `derived_compute`/`derived_wide` run nightly, fsync under a real power cut, `nobody`-user seal tests (skipped), what `edge_upstox` really writes (N10).

## New defects

N7 `domain/services/derived_wide.py:370` reads `nifty_1m.vol`, `:593` `v = _f(vol)`, `:731-735` **feature 153 VWAP weighted by the index aggregate**. A direct CLAUDE.md 2.2 violation in the nightly wide layer, missed in round 6. Medium-high.
N8 `domain/services/timeframe_grid.py:205-213` `_entry` VWAP weighted by `bars["volume"]`, which `exit_context.py:104` fills from the index bars (0 when absent). Same rule. Medium.
N9 `feature_compute_full.py:254` `load_futures` selects `vol` from `fut_1m`; the schema (`infrastructure/database/data_layer.py:136`) and every other reader (`traded_volume.py:138`) say `volume`. `OperationalError` is swallowed `:256-257` -> f091-f100 **always NaN on a real DB** (reproduced). `tests/test_features_full.py:56` builds `fut_1m` with `vol`, so the test passes. Medium.
N10 `tools/edge_universe_coverage.py:18,:61-62` covers by broker->service only: with the example env `U065` news_items is "covered" by `edge_upstox` (a tick recorder that fetches no news) and `U060-U063` instrument masters by recorders never checked to write a master (62 covered, 3 gaps). A REQUIRED row can be certified by the wrong container. Medium.
N11 `regime_6m.py:106,:112` partial-session cumulative volume (round-6 low) unchanged. Low.
N12 `dp_seal.py:205,:233` the private snapshot (up to 20 GB of NON_RECOVERABLE rows_raw) lands in `DP_SEAL_TMP` or `/tmp`: on a box that is the overlay or the SSD. Transient, invisible to the placement guard. Set `DP_SEAL_TMP` to the HDD in the runner. Low.
N13 compose `:134`: one prefs switch per source gates both history pulls and the snap clock; switching Kite history on also starts Kite quote snaps on the shared account. Runbook 2b should say so. Low.

## Mutants and faults (scratch copies)

Harness: 12 mutants, **4 SURVIVED**: `retirement_scope` without the corruption guard and without `PASS>0` (`:457-458`), `quick_check` over a snapshot set always ok (`:336-341`), snapshot session upper bound dropped (`:218`). Code right; test gaps. Health 7/7 caught. Coverage 6/6 caught. Seal 12: 10 caught, 1 equivalent (no-shm branch, `:269` catches it anyway), 1 low (`:351` `hash_ok=0` on the sealer's own copy row changes nothing).
Faults: F1 SIGKILL during the snapshot copy (-wal), F2 SIGKILL at chunk 1 on a main+wal+shm source, F3 ENOSPC at fsync: nothing final, no ledger row, source bytes identical, leaked snapshot dir and `.part` removed on rerun, rerun SEALED 26/26.
retailer_db_build WAL `:296-313`: hashed copy, sig before/after, 3 tries, -wal in the fingerprint; residual is a same-size page rewrite inside one mtime tick (quick_check then decides). Fine.

## Verdicts / would I sign today

- Universe: **PASS-WITH-FIXES** (N10 for the coverage claim, line-less consumers, generator-written registry). As a draft list: yes. As "foolproof": no (N7-N9).
- Compose + .env + edge_health: **PASS**. Kite-only shadow on one box: yes. Dhan swap only after runbook 2 socket count is measured.
- Harness: **PASS-WITH-FIXES** (4 test gaps). As measurement: yes. As stop-gate for Upstox/Fyers/930/full: no, by its own text.
- Coverage tool: **PASS-WITH-FIXES**: sign only after N10 (map store -> service, or require a recorder's own evidence per row).
- dp_seal + runner: **PASS** copy-only SSD->HDD, with `DP_SEAL_TMP` on the HDD (N12). ALLOW_REMOVE: no.
- retailer_db_build: **PASS**, sign yes.
- regime_6m volume: **PASS**; planner fail-closed: **PASS**, sign yes.
- CLAUDE.md 2.2 repo-wide: **FAIL** until N7, N8, N9 are patched; the live indicator path is clean.
