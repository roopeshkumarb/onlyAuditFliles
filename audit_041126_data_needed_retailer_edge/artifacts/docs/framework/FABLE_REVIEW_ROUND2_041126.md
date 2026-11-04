# FABLE REVIEW ROUND 2, 04-11-2026 (independent, read-only, branch report/pull-status-081026 @ 553da2a8)

Every verdict re-derived from the checkout; DISAGREEMENTS.md not trusted. Mutations ran on `git archive` copies in the scratchpad. No box touched. Disclosure: `make_manifest.py --help` (no argparse) re-ran the pack copy, touching `MANIFEST.sha256` + `guard_report.json` (timestamp); both restored via `git checkout`, tree clean.

## Verdicts

| Artifact | Verdict |
|---|---|
| DATA_NEEDED_INSTRUMENTS md+csv | PASS-WITH-FIXES (2 GAP rows lack file:line; MD:5 "6 INDEX_SPOT rows" is ~70 rows) |
| LIVE_CENSUS md+csv | PASS (236/259/246, 25/27 names, 123/87 files, 238.9/236.0 GB recompute) |
| RETAILER_PULLER_DESIGN | PASS (every re-checked cite lands) |
| retailer_db_build.py + tests | PASS-WITH-FIXES (84/84 pass; 2 of 3 fresh mutants survived) |
| recoverability.json | PASS (36/36 classified, 0 UNKNOWN, no live-only table RECOVERABLE) |
| requirements_guard.py + ledger | **FAIL as a gate** (3 of 3 mutants survived; ledger flips with zero evidence) |
| Audit pack README / C-051..055 | PASS-WITH-FIXES (3 unsupported statements) |

## Round-1 findings re-opened

| # | Status | Evidence |
|---|---|---|
| 1 | FIXED | `recoverability.json:146-152`; `classify('global_1m')` -> NON_RECOVERABLE |
| 2 | FIXED (placement) | same class; `opt_ohlc_1m` -> NON; per-src window still UNKNOWN |
| 3 | FIXED | CSV: `why_needed_for_regime` empty 0/183, `evidence` empty 0, `count_by_code` holds counts |
| 4 | PARTLY | MARKER 0; 237 cites exist; 2 GAP rows cite "…031126.md section 2", no line |
| 5 | FIXED | MD:44 rule; recompute dhan 10/61/0, upstox 14/59/0, kite 68/58/0, fyers 10/58/0 = MD:48-51 |
| 6 | PARTLY (by design) | MD:5 documents the substitution; literal name still UNKNOWN |
| 7 | FIXED | census md:20; recompute 236/236/246, Upstox 47 keys/25 names |
| 8 | FIXED | design :51, :64, :66, :176 say ON; :64 gives 50 default vs 49 running |
| 9 | FIXED | :83 -> `login_engine.py:50`; `dp_quorum.py:12-18` is the proof text |
| 10 | FIXED | :110 `download_engine.py:1012`, `:160`, `:166-170`; compose `:316/:324/:333/:355/:363/:370/:388/:403/:422` all land; NSE reports in 2.5 (:93-100); 09:15/09:26 = T-1311 |
| 11 | FIXED | :24 "by DEFAULT… env-overridable, `:7`" = `ssd_to_hdd_move.sh:7` |
| 12 | FIXED (sandbox) | `_probe_tmp` :441-451 rw; `_rm_tmp` :432-438; test :387 asserts hot journal, RESUMED, integrity ok |
| 13 | FIXED (code) | `_rank_sql` :70-72 in ORDER BY :330-331; conflicts :343-350; tests :311, :330 |
| 14 | FIXED | tests :344, :355; `_map_bars` :179-182 still carries any broker string (documented) |

## New defects

1. **Guard mutants all survive** (32/32 tests pass each): G1 delete the evidence-file branch `requirements_guard.py:305-308`; G2 cut `PROBLEM_STATUS` :49 to DONE/COMPLETE; G3 `main()` :559 returns 0 always.
2. **Ledger flips without evidence** (`r_approvals` :298-321), run on the real repo: (A) all flags true, `fable_evidence:"approved in chat"`, `kumar_evidence:"ok"`, status DONE -> 0 ALERT, `done_allowed` True; (B) evidence = `CLAUDE.md` -> 0 ALERT; (C) delete the build's row -> 0 ALERT, 5 builds. Only existence of a "/"-containing path is checked; never content, author or relation to the build; ledger unsigned.
3. **TRACE satisfied by appended notes** (`r_trace` :392-428): all 7 touched task ids were unmapped until a "REQUIREMENT MAPPING" note was added to each at 12:07 (TASKS.jsonl :2950-2954), 3 min before `guard_report.json` (12:10). Any entry of the id, even pre-cutoff, counts (:412-418). Q10 confirmed in practice.
4. **Builder mutants** (21/21 pass): B1 delete row-count check `_verify` :378-379 -> survives; B2 `any`->`all` in NOT NULL reject :335 -> survives (no test feeds a NULL key); B3 ignore `quick_check` :248 -> caught.
5. **No lock on `.building`**: two builds to one `--out` both pass `_probe_tmp` :482 (meta autocommits :490-493); the loser dies with an uncaught `OperationalError` masked by ROLLBACK :360, not REFUSED. Reasoned from code, not executed.
6. `tests/test_recoverability_placement.py` collects **0 tests under pytest** (a `main()` script, :20); "expected 84 passed" = 25+21+32+6 silently excludes it; TOOL_TESTS :293 accepts it via `check\(`.
7. Pack CSVs are LF-normalised by `make_manifest.py` (text-mode read); repo files hold 817/184 CR bytes, so pack sha != repo sha; REDACTIONS.txt names only the Friday plan.
8. Leak scan: no tokens, RFC1918, emails or Cloudflare hostnames; old hostname `j1800` appears 393 times in census paths. Acceptable; declare it.

## README / ledger statements

Unsupported: README C1 "every row has a file:line citation" (2 rows); README 3.8 "i5 SSD 100% full (1.8 GB free)" has no TASKS.jsonl entry (C-021: 3.47 GB at 21:39 on 03-11); C-054 "11 of 12 mutations caught" has no mutation log in repo or pack. Supported: C2, C3, C4, C5 (G1-G6 at design :134-139), C6 (17 rules, 31+5), 3.7 (T-1317; 1,782,139 in TASKS), C-051, C-052, C-053 (25 tests), C-055 (0 ALERT, 0 of 6 reproduced).

## Unverifiable from this sandbox

Boxes, `.env`, live DBs, `/volume2` state, whether the 12:07 notes reflect real work, real `opt_chain_1m` key, per-broker `recoverable_until`, final fsync under power loss, C-052 beyond its arithmetic.
