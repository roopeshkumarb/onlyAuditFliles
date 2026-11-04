# FABLE REVIEW ROUND 6, 04-11-2026 (independent, read-only, report/pull-status-081026)

Pack tests: **151 passed** (8 files). Mutants/faults ran on a scratch copy; `docker compose config` (v5.6.0, no daemon) parsed the real compose with the example env. Line numbers are mine.

## Round-5 defect table

| # | status | opened |
|---|---|---|
| 1 regime_6m index volume | **FIXED** | `regime_6m_build.py:31-47,61` (traded_volume, None when unmeasured); `regime_6m.py:50-58,276`; `test_regime_6m_volume.py` |
| 2 dead/wrong cites | **PARTLY** | token on the cited line, gen `:34-57,:72-82`, test `:100-122`. Wrong line numbers fail (3 of 4 cite mutants caught), but tokens are generic (`close` on 6 lines of mtf_regime_engine, `adx` on 29 of regime_stabiliser): `:132` moved to `:90` passed. `cite_tokens` live inside the JSON, so the test has no independent registry |
| 3 event calendar | **FIXED** | `:257-260,:287`, owner conflict stated |
| 4 USDINR | **FIXED** | `:210-215` UNKNOWN; `dp_tickrec.py:138-162` subscribes CDS USDINR |
| 5 constituent ids | **FIXED** | `:266-269` from `resolved_symbols_fyers_kite_041126.csv`; test `:165-179`. The fetch itself is unverifiable here |
| 6 breadth_1d / sector_1m | **FIXED** | `:238`, `:244` |
| 7 TICK_EXTRA coverage | **PARTLY** | `edge_universe_coverage.py:26-36,63-80`: `TICK_EXTRA=0` gives 56 gaps, `TICK_EXTRA_EQ=20` 33 (verified). But `:22,:85-86` expand against the **sandbox `os.environ`**, never the box's `.env.retailer_edge`: on a laptop it certifies compose defaults, not the box |
| 8 COMPOSE_PROFILES | **FIXED** | `.env:4`; `compose:8-21`; `config --services` = `edge_hist`; `--profile live_dhan` = `edge_depth` only; `_auth`/`/src`/`/lease` all `read_only: true`; no old root mounted |
| 9 /lease, history proof | **PARTLY** | `compose:134,:139-141`; `compare_history :436-498`. Snap clock is gated by prefs (`planner.py:1067`) but `:1071-1072` swallows a prefs read error and runs the pass (Dhan /optionchain on the shared account). Topology unmeasured |
| 10 harness C1-C6/A1/A2/A4 | **FIXED** | `:414`, `:315`, `:321-327`, `:354,:555-556` |
| 11 health /tmp, H2/H3 | **FIXED** | `edge_health.py:31-32,80-87` |
| 12 candles place/removable | **FIXED** | `dp_seal.py:368,:386,:439-441,:452-475` |
| 13 ALREADY_SEALED by name | **FIXED** | `:302-329` |
| 14 mode=ro leftover | **PARTLY** | snapshot only with **no** -shm `:206-209`. A SIGKILLed writer leaves main+-wal+-shm (the usual power-cut picture): the seal opened in place and **rewrote the -shm bytes** (measured; 60/60 rows). Data-safe, but contract 1 `:11-12` "never written" is false for the common case |
| 15 rows==nsrc, '/' dataset | **FIXED** | `:248-254`, `:273-282,:376` |

## New defects

N1 `edge_cutover_proof.py:350-433` `--feeds depth` alone returns **PASS** (exit 0) with no note that ticks/upstox/fyers were never compared; a subset PASS reads as a full PASS in the audit pack. Medium.
N2 `dp_seal.py:171-217` a garbage `-wal` beside a clean main (no -shm) is **not refused**: SQLite drops the frames; the seal returned zero segments, no error (contract 6 `:27` false). On a real DB it seals the main-file rows as SEALED. Medium.
N3 `dp_seal.py:395-396` late rows report growth only; a source that lost rows after sealing (25 to 15) is ALREADY_SEALED, `late_rows={}`. Low.
N4 coverage env source (row 7). Medium. N5 cite tokens (row 2). Medium.
N6 CLAUDE.md 2.2 repo-wide: `domain/services/feature_compute_full.py:206-207` selects nifty_1m `vol` as `volume`; `:162-171` and `:551` weight **VWAP f080 and OBV f078 with the index aggregate**; `:533-556` f071-f079; `:920` volume percentile; live via `derived_compute.py:841`. **Violation.** `derived_features.py:138` feature 144 from nifty_1m.vol: violation in spirit. `exit_context.py:104,:168-170` named index fallback: borderline. `indicator_engine.py:326-333,372` compliant. `market_memory.py:173`, `regime_spine.py:232,:306` fill missing volume with 0: low, no percentile reader found. `flow_engine.cvd_from_bars` has no caller. `regime_6m.py:106,:186` partial sums over partly-measured sessions bias the volume percentile: low.

## Mutants (14 new) and faults

Harness/health: P1 quick_check skips the old side, P2 zero-session feed ignored, P3 latency delta doubled, P5 NULL tolerance 50 %, P6 new-side read error swallowed, P7 no day file but fresh status.json = healthy, P8 state written before the backwards compare: **7 SURVIVED**; P4 (history start slack) caught. The real code is right in each case (probed: P2 scenario INSUFFICIENT, 40 % NULL FAIL): test gaps a future edit walks through.
Seal: S1 `.BAD` deleted by the next run, S3 `known` without `here` = ALREADY_SEALED, S4 unverified HDD copy row counts as done, S6 adopted rows=0: **4 SURVIVED** (test gaps); S2 caught; S5 caught only because `_lock` mkdirs.
Faults: SIGKILL at chunk 1, fsync, read-back, after rename, before ledger commit, second segment: all rerun to SEALED/ADOPTED, 60/60 rows, no `.part`, every segment has a copy row, move_to_hdd PROVEN. Disk full: nothing final, rerun clean. Corrupt ledger: DatabaseError before any file. Stale -shm, corrupt -wal, lost rows: above.

## INCONCLUSIVE treatment
No path turns a feed- or connection-level feed into PASS (`:341-347,:426-432`; decode share `:345`; corruption and FAIL win). Holes: N1, and thresholds are free CLI choices (printed). Upstox/Fyers stay INCONCLUSIVE by design, so the old Upstox/Fyers recorders cannot be retired on this harness (runbook 8.1 says so).

## Verdicts / would I sign today
- Universe: **PASS-WITH-FIXES** as a draft list (N4, N5). Sign as draft list: yes. "Foolproof": no; N6 means engines beside it still read the forbidden volume.
- Compose + .env: **PASS**. Kite-only box-swap shadow: yes. Dhan swap only after runbook 2 and C-keys measured.
- Harness: **PASS-WITH-FIXES** as measurement (N1, 5 test gaps); **FAIL as stop-gate** for Upstox/Fyers and undecoded depth, by its own admission. Sign as measurement after N1: yes.
- edge_health, coverage tool, runbook 8: **PASS-WITH-FIXES** (P7/P8 tests, N4). Sign after N4: yes.
- dp_seal: **PASS-WITH-FIXES** (row 14 wording, N2, N3, S1/S3/S4/S6 tests). Copy-only SSD to HDD on ext4 after N2: yes. ALLOW_REMOVE: no.
- regime_6m volume: **PASS**, sign yes. N6 goes to Kumar: the round-5 defect, one directory over.

## Not verifiable here
Boxes, Dhan socket count and account topology, edge_hist lease behaviour beside the old fullpuller, whether `derived_compute` runs nightly, the fyers/kite CSV fetch, fsync under a real power cut, `nobody`-user tests (skipped in scratch).
