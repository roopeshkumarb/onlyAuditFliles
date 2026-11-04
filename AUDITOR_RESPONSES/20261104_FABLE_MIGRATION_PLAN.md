# Fable review: MIGRATION_PLAN_041126 / migration_phases.json (04-11-2026)

Read-only. `tests/test_migration_phases.py`: 12 passed; they prove the JSON is well-formed, not that the plan is safe. **NOT APPROVED: 3 UNSOUND, 6 FIX, 1 SOUND.**

| Phase | Verdict | Why |
|---|---|---|
| M0 | SOUND | coverage tool fails today (exit 1, 4 gaps): real, fail-able |
| M1 | FIX | D7 |
| M2 | UNSOUND | D1, D2, D3 |
| M3 | UNSOUND | D4 |
| M4 | FIX | D8, D9 |
| M5 | FIX | D5 |
| M6 | UNSOUND | D6 |
| M7 | FIX | D10, D11 |
| M8 | FIX | D12, D13, D14 |
| M9 | FIX | D5; otherwise a re-measure of M2 |

## Defects

**D1 (M2, plan :23,:40; json :218-227). Friday is unreachable under the plan's own rules.** i5 IO avg10 97-99 all day (drain log); copies wait for <= 90 (rule 6). 159.6 GB of i5 SSD is live DBs (manifest class L) that after the redirect must be copied to HDD AND a second place (peer/Drive; SSD never counts) before removal. i7 holds no namesakes; Drive unchecked. No "if missed" branch. Either Kumar waives the IO gate for cold copies, or Friday is missed and the SSD copies stay (nothing lost, rule broken). Say which.

**D2 (M2 rollback, json :240).** Restoring `.env` sends writes to an SSD with 1.3 GB free: impossible on i5. HDD-epoch rows written meanwhile are not merged back.

**D3 (plan :90-91; json :17-18).** "i5 SSD pull data 303.2 GB" on a 205 GB SSD (LIVE_CENSUS :27). 303.4/248.7 are space-gate totals (FABLE_I5_REDIRECT :10), not SSD contents (PLACEMENT_SCAN: 192.8 / 150.1 GB).

**D4 (M3 json :315,:319; M7 json :644).** Upstox and Fyers are INCONCLUSIVE until instrument decoders exist (`edge_cutover_proof.py:19,427`); M3 demands "never INCONCLUSIVE"; M7 retires Fyers and Upstox FIRST. No phase builds the decoders or adopts runbook 8.6 (`broker_consensus`). Missing phase M3a.

**D5 (rule 4; M5 json :495 vs M9 json :807).** "SSD holds today + look-back" contradicts "SSD bytes == 0 after Friday". Make staging HDD-only (compose already demands it until G8) or have Kumar name the exception.

**D6 (M6 json :572,:589,:626).** "New on both boxes, old still running" needs 8 Dhan sockets of 5: old Dhan depth is retired de facto in M6, with no old baseline. Gate "real power-cut observed" has no mechanism: schedule a deliberate mains pull with Kumar at a box whose peer is healthy, or state M6 blocks indefinitely.

**D7 (M1).** No metric forces the refusal test to run against the real malformed i5 `niftybkp.db`.

**D8 (M4 json :410).** "Switch source OFF in old fullpuller" is singular; Kite/Dhan are one account across both boxes, so BOTH old fullpullers must be off.

**D9 (M4).** Kite is planned only on the lease box (`EDGE_LEASE` default `pull_lease_i5`); "start with Kite" names no box; i5 is the box at IO 99 with a full SSD.

**D10 (M7 rollback json :664).** Omits "stop edge first". `--restart=always <old>` while `edge_depth` (restart: always, compose :32) runs means the next power cut boots both: 6th socket, Dhan kicks the oldest.

**D11 (M7 proof json :650).** Option strike bands recentre each session (LIVE_CENSUS :20), so "new alone vs prior-session baseline" is not measurable. Use new-i5 vs new-i7 same session plus coverage and health.

**D12 (M8 plan :75-77; json :714).** Cited read sites are comments: `orchestrator.py:794,:852,:1380` and `judge_engine.py:1065` hold no SQL; the real `options_chain_summary` read is `domain/services/reference_data.py:79`.

**D13 (plan :65-72).** Counts understated ~4x against the stated method. Non-test, non-worktree `.py`, word-boundary: nifty_1m 296, fut_1m 160, vix_1m 142, opt_chain_1m 157, equity_1m 94, options_chain_summary 40, niftybkp 201, blpro_working.db 250. The 77/45/44 figures reproduce only without tools/, research/, attic/ (73/42/44), yet metric "reads remaining: 0" counts everything.

**D14 (M8).** The old engine is itself a puller: `runtime.py:7139 fill_gaps` writes nifty_1m/vix_1m from Fyers (`insert_bars` :2257,:6534,:7275). Nothing in M3/M4 replaces it. "New hot store" is defined nowhere.

**D15 (tests :18-20,:54-57).** A phase can be DONE with every metric UNKNOWN: `approvals_ok` ignores `metrics`. Require every `measured` != UNKNOWN and within target.

**D16.** "0 minutes missing on both boxes" has no tool (runbook G-union: manual cross-read); it can stay UNKNOWN unnoticed.

## Shrink arithmetic
295.4M x 75-173 B = 22.2-51.1 GB: correct. "5-11% of ~475 GB": 475 = 238.9 + 236.0 (files > 20 MB per box, both volumes, incl. `_static_copies`), while the duplicate sits mostly on HDD. Unrelated populations; drop the percentage.

## Power cut mid-phase
M2: cut between `.env` edit and recreate boots old containers on the full SSD (pullers block, no loss). M3: cut between `docker stop old` and `up new` boots a box with no recorder; peer covers; run the swap as one script, verify after boot. M7: D10. Builder/seal: SIGKILL-tested; final-file and directory fsync UNPROVEN (correctly stated).

## Not verifiable from the sandbox
Box IO and free space, lease holder, account topology, Drive bandwidth/state, i7 `.env`, Pi puller status, HDD epoch_meta identity, container restart policies, who stopped i5 fullpuller at 13:37.
