# FABLE REVIEW ROUND 8, 04-11-2026 (independent, read-only, report/pull-status-081026)

Pack run here: 12 files, **262 passed, 2 FAILED** (`tests/test_edge_universe_coverage.py::test_tick_extra_zero_is_a_gap`, `::test_constituent_beyond_tick_extra_eq_is_a_gap`: fixture rows carry no `store`, so the N10 rule flags them). The branch ships red. 14 mutants + 5 attacks on scratch copies. Line numbers are mine.

## Round-7 defect table

| # | status | opened |
|---|---|---|
| N7 derived_wide index VWAP | FIXED | `derived_wide.py:370` selects `NULL`, `:378-381` `traded_volume.from_connection`, `:596` `v=_f(tv_by_min.get(key))`, `:735-739`; M1 caught |
| N8 timeframe_grid/exit_context | FIXED | `exit_context.py:103-105` drops row volume, `:109-119` futures by minute; `timeframe_grid.py:203-215` weight only measured >0; M2 caught |
| N9 load_futures `vol` | FIXED | `feature_compute_full.py:258-267` `volume`, error logged + `attrs["load_error"]`; M3 caught |
| N10 coverage per dataset | FIXED (test red) | `edge_universe_coverage.py:22-44` WRITER_PROOF per (service, module, token), `:105-108`; real run: 58 covered, 7 gaps incl. U060/U062/U063/U065 (U061 proven by `dp_depthrec.py:232`). M5/M6 caught by `test_edge_coverage_env_source.py`; the two pre-N10 tests were not updated |
| N11 regime_6m partial sum | FIXED | `regime_6m.py:104-116` curve stops at first unmeasured minute; M4 caught |
| N12 DP_SEAL_TMP | **PARTLY** | `dp_seal.py:206-212` required, system temp refused (M7 caught). Residue: `realpath(base)==gettempdir()` only, so `DP_SEAL_TMP=/tmp/anything` is accepted (attack A2). No runner sets it: `EDGE_CUTOVER_RUNBOOK:24` says the seal has no entry point; the only `DP_SEAL_TMP` mentions are the module and its tests |
| N13 compose prefs switch | NOT CHECKED (wording) | runbook only; out of this round's scope |
| N1 residue (FEEDS vs ALL_FEEDS) | FIXED | `edge_cutover_proof.py:472` `ALL_FEEDS`, `:561` PASS_PARTIAL, `:697` exit 5; tests `:684-722,:798`; M8 caught |
| N5 cites | **PARTLY** | pins hand-maintained `gen:306-320` (read only, test `:228-232`); forged `nonexistent.py` rejected `gen:73-85`, test `:100-113`; M14 caught. Residues below (N17, N18) |
| Harness survivors (4) | **2 of 4 STILL SURVIVE** | M9 `retirement_scope` without `not report["corruption"]` and M10 without `PASS>0` (`:457-458`): 64/64 pass either way. No test names `retirement_scope`. quick_check-over-set and snapshot upper bound: P1 `:725` covers quick_check; upper bound not re-mutated |

## New defects

N14 `tests/test_edge_universe_coverage.py:36-51` red on HEAD (above). Test gap, but the pack cannot be called green. Medium (process).
N15 `tools/box_collect.py:256-263,:297,:313` upstox/fyers `last_frame` is `HH:MM:SS` with no date (`dp_upstoxrec.py:181`, `dp_fyerstbt.py:222`); `_hms_today` pins it to today and a negative age passes `<= FRESH_S`. Attack A3a: a recorder dead since yesterday 11:00:30 shows **RECORDING** at 11:00 today; A3b: a future clock time shows RECORDING; A3d: Dhan heartbeat `at` fresh with frames stopped since 09:20 shows RECORDING (`:299-300` uses the writer's heartbeat, not a frame time). Stale shown as fresh on the live board. **High** for the board's purpose.
N16 `box_collect.py:355-370` LIVE_ONLY row state is the worst of the brokers named in the row's STATUS TEXT, not the row's dataset: U060 (upstox master, coverage GAP) reads `(dhan: depth/...)` and shows RECORDING from the Dhan depth feed (attack A4). The board and the coverage tool contradict each other on the same row. Medium.
N17 `tests/test_retailer_edge_universe.py:100-113`, `gen:73-80`: a line-less consumer passes if ANY 4+ letter word of its note occurs anywhere in the file: `domain/services/derived_wide.py (reads it)` and `CLAUDE.md (data)` both pass (A1, A1b). Forgery on an existing file is not rejected. Low-medium, test gap.
N18 `test:83-97` `rule_doc` counts as a read-site: U002, U015, U058, U060, U062, U063 are REQUIRED_ENGINE on CLAUDE.md/definition pins alone (A1d). Wording/evidence-strength, not code.
N19 `box_collect.py:191-202` `live_<box>.json` has no staleness flag; a dead collector leaves `ok:true` files forever and no page in this repo reads `/tmp/board` (nothing found), so freshness is the unseen page's job. Low until the page exists.
N20 CLAUDE.md 2.2 residue in research/CLI tiers: `tools/regime_forecast2.py:86-90,:311-314` VWAP and cumvol from `nifty_1m.vol`; `research/strategy_blocks/features.py:345-359` `session_vwap` weights by `b["vol"]` of nifty_1m; `main.py:135` CVD from `feed.bars()` index volume (startup print only). Live/nightly path clean.

## Box collector: write / lock / mislead
`box_metrics.sh` reads /proc, df, ls, one `docker ps -a`; opens no database, takes no lock, writes nothing on the box (`test_script_never_writes` `:248`). `box_reach.sh` writes only `/tmp/reach_err.$$` on the caller. Rates: reset/wrap -> null (M11 caught), first cycle null, device swap null, ok:false carries no metrics and keeps no counters (M12 caught). It cannot write to a box. It CAN mislead: N15, N16.

## Verdicts / would I sign today
- **CLAUDE.md 2.2 (N7-N9, N11 fixes): PASS** for engines, nightly wide layer, exit context, regime_6m. Sign yes for the live path. Repo-wide: N20 remains (research tier); say "live and nightly paths" not "repo-wide".
- **Universe: PASS-WITH-FIXES.** Sign as a draft list; not as foolproof until N17 (match note words to the dataset name, not any word) and N18 (rule_doc not a read-site) are tightened.
- **Coverage tool: PASS-WITH-FIXES.** The N10 logic is right and the real run finally shows the 7 gaps. Sign once N14's two tests are repaired (add `store` to the fixture) and the pack is green.
- **dp_seal: PASS-WITH-FIXES.** Reject any path under `gettempdir()` (commonpath), and name `DP_SEAL_TMP` in the runner/compose that does not yet exist. ALLOW_REMOVE: no.
- **edge_cutover_proof: PASS-WITH-FIXES.** PASS_PARTIAL correct. Sign as measurement; add two `retirement_scope` tests (M9, M10) before it is a stop-gate.
- **box_collect / box_metrics: FAIL** as a live board until N15 (date-bearing freshness: use `at` + `last_frame`, refuse negative ages) and N16 (row state from the row's dataset/writer, not status text). As a metrics sampler (CPU, disks, net, growth): PASS.

## Not verifiable here
Boxes, the Cloudflare routes, whether `--time-style` works on DSM/busybox `ls` (falls to UNKNOWN if not), box clock skew, the page that will read `/tmp/board`, the seal runner, N13 wording.
