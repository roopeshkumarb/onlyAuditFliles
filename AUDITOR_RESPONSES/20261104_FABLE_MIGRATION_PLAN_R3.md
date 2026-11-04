# Fable review round 3: MIGRATION_PLAN_041126 rev 3 / migration_phases.json (04-11-2026)

Read-only. Suite: 64 passed. 27 new cheats on a temp copy of the checker: 24 accepted. **Governing document: NO.** 0 UNSOUND, 7 FIX, 4 SOUND.

## N1-N8, D5

| # | Status | Opened |
|---|---|---|
| N1 | PARTLY | checker typed (tests :166-193); cheatable, R4 |
| N2 | PARTLY | feed real (`edge_cutover_proof.py:77,:448-460`); M6/M7 gates; R3, R5, R6 |
| N3 | FIXED forward (json rules[9], M3 :437, M7 :1035; runbook :50; md :18); R1 |
| N4 | FIXED (M2 PRIORITY 1-3); R7 |
| N5 | FIXED (md :134; tests :724-746) |
| N6 | FIXED (M3 gate[0]; md :63) |
| N7 | FIXED (M4 gate; md :65) |
| N8 | FIXED (M9 E1-E5; md :70); R8 |
| D5 | FIXED (json rules[3]; md :12; tests :666-685) |

## New defects

**R1 (M3, M3a, M6, M7 rollbacks; runbook :108-109).** Each rollback is `docker stop edge_*`, then `update --restart=always <old>`. `edge_*` runs `restart: always` (compose :32), and Docker restarts an *always* container after a daemon restart even when stopped by hand. So after any rollback the next power cut boots edge beside old: the 6th Dhan socket. N3 was fixed forward only. Rollback must be `docker update --restart=no edge_*`, `docker stop edge_*`, then old. The repo's old recorders are `unless-stopped` (`docker-compose.datapullers.yml:60`), so this hole is the real one.

**R2 (runbook :101 vs M7 steps).** Runbook section 6 stops "Fyers TBT, Upstox, Kite ticks, Dhan" and proves by "new-vs-previous-days baseline": the INCONCLUSIVE feeds first, by the method D11 rejected. The test checks the JSON only (tests :501-503).

**R3 (M3, M3a, M6, M7 metrics).** Every harness number (parity, sessions, `retirement_scope` as "1") is typed by hand beside any dated file (tests :104, :112). `--min-sessions 1 --min-parity 0.5` also yield a real PASS report; the plan never reads its `thresholds`. Make the harness `--json` report the evidence; recompute verdict, thresholds and `retirement_scope` in the test. Until then 930/full retirement rests on three humans reading a file.

**R4 (checker, tests :27-28, :141, :144-156, :172-177). Accepted:** `measured_at` 99-99-9999, 31-12-2099, 01-01-2020, Arabic-Indic digits (`\d` is Unicode); evidence named with Arabic-Indic digits, dated 00000000 or 2019, or older than `measured_at`; whitespace-only file; file saying "NOT MEASURED"; approval file saying "NOT APPROVED"; one file for all 11 metrics; `FABLE_*_041126.md`, a copy or hard link of the plan under a dated name; a file behind a symlinked directory; `.claude/worktrees` path; `-0.0`; `1e308`; parity 7.0. `10**400` crashes (OverflowError). Status `DONE\xa0` or Cyrillic `DОNE` claims done, then fails (harmless). Rejected: bool target or measured. Fix: ASCII digits, real date in [plan date, today], evidence date >= plan date, `realpath` under ROOT, inode and sha unequal to any plan or `FABLE_*` file, parity in [0,1].

**R5 (`edge_snap.py:59`).** `plan()` without `ssd_roots` checks nothing: `plan("/volume2/retailer_edge", "i5", day)` returned 8 SSD paths. Fail closed.

**R6 (M6 gate: G8 recording beside old 930/full).** `edge_snap.py:20-21` counts websockets only; G8 doubles REST snapshot calls on one shared account (runbook :56), no rate arithmetic. A rate-limit during the proof degrades the OLD baseline and loses live-only minutes.

**R7 (M2 metric "snapshot minutes lost == 0", tests :59).** The if-missed branch records a loss honestly; a loss > 0 then keeps M2 un-DONE forever. Split: "loss window recorded" (evidence), "lost after the redirect == 0".

**R8 (M9).** i7 `/volume2/docker2` (PLACEMENT_SCAN :42) looks like a Docker root on the SSD; if images, layers and logs live there, "bytes on any SSD == 0" is MISSED by construction; E1-E5 do not name it.

**R9 (tests :311-316).** The first real step must edit the test file holding PINNED; no hash of PINNED is recorded.

## Plan as written

Executable in order; dependencies consistent. Power-cut holes left: R1; M2 cut between `.env` edit and recreate (stated). E2 must hold on Friday; R8 unnamed. 930/full: the harness can prove it (R3 aside); the stub cannot fake it.

## Verdicts

M0 SOUND. M1 SOUND. M2 FIX (R7, R4). M3 FIX (R1, R3). M3a FIX (R1). M4 SOUND. M5 SOUND. M6 FIX (R1, R5, R6). M7 FIX (R1, R2, R3). M8 SOUND. M9 FIX (R8).

**Approve as governing document? NO.** Conditions, one pass: R1 in all four rollbacks and runbook section 7; R2 rewritten to the JSON order and D11 method; R3 harness JSON as evidence; R4 tightened, the 24 cheats as mutation tests; R5-R9 recorded. Plan only; no deploy approval.

## Not verifiable here
Live restart policies, box IO and free space, i7 Docker data-root, lease holder, account topology, broker REST limits, Drive state.
