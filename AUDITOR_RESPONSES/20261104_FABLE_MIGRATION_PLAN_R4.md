# Fable review round 4: MIGRATION_PLAN_041126 rev 4 / migration_phases.json (04-11-2026)

Read-only. Suite: 103 passed. 24 new cheats on a temp copy: **24 accepted**. **Governing document: NO.** 0 UNSOUND, 6 FIX, 5 SOUND.

## R1-R9

| # | Status | Opened |
|---|---|---|
| R1 | FIXED as written (json M3/M3a/M6/M7 rollback; rules[11]; runbook :108-111; compose :32; tests :1169-1195); residues S1-S3 |
| R2 | FIXED (runbook :101; json M7 retire order; tests :1204-1217) |
| R3 | PARTLY (tests :280-414; S4) |
| R4 | FIXED for the 24 listed (tests :1310-1452); S5 |
| R5 | FIXED (`edge_snap.py:57-58, :66-67`) |
| R6 | PARTLY (`edge_snap.py:82-105`): `dp_families.py:74-76` is per-unique-request pacing, not an account limit; per box, not per account; old=0, negative and `True` pass as measured |
| R7 | FIXED (PINNED :67-68; tests :1467-1481) |
| R8 | FIXED (json M9 C1; tests :1484-1495) |
| R9 | PARTLY: PINNED hashed (tests :573, :1498); tests :621 and :656 must be deleted at the first real measurement, covered by no hash |

## R1 boundaries (restart=no edge; stop edge; always old; start old)

Docker boots an `always` container even if hand-stopped; `update` is persisted by fsynced atomic write. Cut after step 1: nothing boots (peer covers). After 2: nothing. After 3: old alone. After 4: steady. Daemon restart: identical. **No boundary boots both.** Remaining paths:

**S1.** Forward start after a rollback: edge exists with `no`; `compose up` only `start`s it (config hash unchanged), so a later cut leaves no recorder (03-11 again). Runbook :111 names the re-arm; json M3 step (3) and M7 do not.
**S2 (6th socket without a power cut).** `docker update --restart=no <old>` is invisible to compose. Any `docker compose -p datapullers up -d` (runbook :110 uses it; puller930 was recreated so at 14:08) starts, or on drift recreates with `always`, the retired depthrec beside edge_depth. Retirement must also mark the service in `docker-compose.datapullers.yml` (profile or `replicas: 0`).
**S3.** `docker update --restart=no edge_*` is literal: nothing expands it; a copy-paste rollback fails at step 1.

## Checker cheats (all accepted)

**S4 harness:** `unit` not PINNED (`ratio`->`fraction` lets parity 7.0 pass); `days` "a","b","c" or 2020/Sat/Sun; `old.root == new.root`, same box; one non-required key per feed (universe REQUIRED list never read); `missing_files` contradicting `sessions_compared`; `granularity: connection` with `instrument_level: true`; `summary.keys_*` unchecked; M3 metrics from two reports with different days; M7 takes PASS_PARTIAL; latency, null-exchange, dups (runbook :70-71) never recomputed.
**S5 evidence:** `NOT_MEASURED`, `not yet measured`, Cyrillic `NОT`, `PLACEHOLDER`, `TODO`, `REJECTED`; 4 KB random bytes; the letter `x`; `EVID_20991231_041126.md`; both dates tomorrow; approval file that also says `fable REJECTS`; one file pre-approving M0..M9.
**S6.** `MISSED` needs no evidence (tests :25): M9 can sit MISSED forever with every metric UNKNOWN.

## Ordering M0..M9

**S7.** M3 step 4 swaps both boxes (edge_depth on both); M6 then requires one box old until M7, and M7 "retires" a recorder M3 already stopped. **S8.** M9's hash metric needs M5 segments (not in M9's gate) and E2 ends at M8 DONE: MISSED by construction; the gate should say so. Rules numbered 11, 10, 11 (md :18-20).

## Verdicts

M0 SOUND. M1 SOUND. M2 SOUND. M3 FIX (S1, S3, S7). M3a SOUND. M4 SOUND. M5 SOUND. M6 FIX (R6, S7). M7 FIX (S2, S7). M8 SOUND. M9 FIX (S6, S8).

**Approve as governing document? NO.** Conditions: S2 in M7 and runbook 6; S1 re-arm in M3/M7 steps; S3 explicit names; S7 one Dhan state; PIN `unit`, real trading dates >= plan date, distinct roots and boxes, REQUIRED keys from the universe, one report per phase, PASS only, latency/dups recomputed; MISSED needs a dated evidence file; R6 per account with a sourced limit and old > 0; R9 "nothing measured today" tests in a file the first step may delete; the 24 cheats as mutation tests. Plan only; no deploy approval.

## Not verifiable here
Docker/Synology boot behaviour, live policies, account topology, broker limits, box IO, Drive state, who runs compose.
