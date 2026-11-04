# Fable review round 2: MIGRATION_PLAN_041126 rev 2 / migration_phases.json (04-11-2026)

Read-only. `tests/test_migration_phases.py`: 30 passed. Grep counts reproduced exactly (250/296/160/142/157/94/40/200; niftybkp 201 -> 200 as the repo moved). **PLAN NOT APPROVED as governing document: 2 UNSOUND, 6 FIX, 3 SOUND.** Big improvement; the remaining holes are mechanical and fixable in one more pass.

## D1-D16, M3a

| D | Status | Where opened |
|---|---|---|
| D1 | FIXED | md :19-49; json :1106-1172 |
| D2 | FIXED | json :273 |
| D3 | FIXED | json :31-40, :253 |
| D4 | FIXED | json :354-367 (M3), :465-548 (M3a), :833 |
| D5 | PARTLY | md rule 4 says staging HDD; json rule 4 (:10) still says "lands on SSD then moves to HDD", M5 step :661 "SSD -> HDD". Twin contradicts twin; test only checks `load_moved` :666 |
| D6 | FIXED | json :364, :755, :757, :820-822, :751 |
| D7 | FIXED | json :145, :150, :220 |
| D8 | FIXED | json :562, :587 |
| D9 | FIXED | json :563; `pullers/fullpuller/planner.py:1072` fail-closed verified |
| D10 | FIXED for rollbacks (:393, :499, :776, :860); see N3 for the forward step |
| D11 | FIXED | json :845-847 |
| D12 | FIXED | json :1217-1316; `reference_data.py:79`, `orchestrator.py:669/:709` hold real SQL |
| D13 | FIXED | json :1175-1215; script reproduces |
| D14 | PARTLY | puller role documented (:1318-1329); hot store "defined" (:1331-1337) but see N5 |
| D15 | PARTLY | checker exists (tests :31-39) but is a string blacklist; see N1 |
| D16 | FIXED | json :439-444, :901-906 |
| M3a | FIXED (exists, gated, M7 waits on it) |

## New defects

**N1 (D15 residue, tests :17-18, :31-35). The DONE checker is trivially cheatable.** I mutated a temp copy of M0 and ran `phase_done_ok`: all of these pass as DONE: `measured` = "unknown", "UNKNOWN " (trailing space), "TBD", "n/a", "not measured (UNPROVABLE)" (the check is whole-string equality, so any sentence passes), numeric 0, `False`; `measured` "7" against target "0" with `pass: true`; the metrics list replaced by one dummy; one metric deleted. Also status "FINISHED"/"CLOSED" is outside `DONE_WORDS` so the checker is never invoked. Fix: case-fold and strip; whitelist (a number or a dated evidence path), not blacklist; pin the metric names per phase in the test; treat any status other than NOT_STARTED/IN_PROGRESS as done-claiming.

**N2 (UNSOUND M7; M6 gate :748-751, M7 :839). The old 930/full pullers' live-only chain snapshots have no successor and no proof.** `fullpuller_server.py:95` `planner.snap_clock()` writes option-chain snapshots (U014, G8); the harness `FEEDS` (`tools/edge_cutover_proof.py:60-65`) has ticks, depth, upstox_live, fyers_tbt only. G8's HDD-only snap service is "not started" (runbook :132). M7 step :839 retires "930 puller, full puller" with no per-instrument PASS possible, breaking rule 9 (:15). G8 must be an M6 entry gate and a harness feed.

**N3 (M3 :365, M7 :838). Forward order is "docker stop; docker update --restart=no".** A power cut between the two boots the old recorder (restart=always) beside `edge_depth` (compose :32): 6th Dhan socket, 805 kick. Order must be `update --restart=no` FIRST, then stop. The rollbacks got this right; the forward steps did not.

**N4 (M2 ordering vs data safety, :246-247). Class A (recoverable, 22 GB) is copied first "for space"; class L (159.6 GB) holds i5's ONLY copy of live-only chain snapshots since 23-10** (FABLE_I5_REDIRECT :14; manifest rows :15-19 "i7 has no file of this name"). Until the `.env` edit is permitted, puller930 (recreated 14:08) keeps writing live-only rows to an SSD with 1.3 GB free: when it fills, SQLite writes fail and those minutes are gone, and the if-missed branch (:1166-1172) says nothing about it. Priority must be: redirect first (zero copy), then class L cold copy to HDD, then class A.

**N5 (M8 :1331-1337). Hot store: no writer path is named.** "Fed by the new live-only puller path" means minute bars built from Kite ticks / raw frames; no bar builder, no `SRC_ORDER` position (CLAUDE.md 1.2), no VIX source (VIX is not a tick feed). RAM read is fine for latency; the HDD journal competes with recorders on a RAID at IO 97-99 and that cost is unmeasured. Define G9's input and SRC_ORDER before M8 is gated on it.

**N6 (M3 gate :357, M4 :563). "M2 free-space gate green on the box" can block forever** (f = 0). The new recorders write only to `EDGE_ROOT` on /volume1 (compose :23); the dependency is unnecessary. Let M3 start on i7 regardless of M2.

**N7 (M4 gate :555).** Fyers/Upstox history handover needs M3a green, not M3; the gate names only M3.

**N8 (M9 :1029).** `blpro_working.db` (9.2 GB live, written by the engine until M8) and CLAUDE.md 3 SSD items (sim_state, event calendar) are not named exceptions, so M9 is MISSED by construction.

## Verdicts

M0 SOUND. M1 SOUND. M2 FIX (N4). M3 FIX (N3, N6). M3a SOUND. M4 FIX (N7). M5 FIX (D5 twin). M6 UNSOUND (N2 gate). M7 UNSOUND (N2, N3). M8 FIX (N5). M9 FIX (N8).

## Retirement, per broker (attack 4)

Kite ticks: retirable after per-instrument PASS (token key). Dhan depth: retirable only with `--decode-depth` >= 99% frames decoded and one-old-one-new baseline. Upstox/Fyers: M3a only. 930/full pullers: NOT retirable until G8 exists and a snapshot feed is added to the harness (N2). Minimum extra proof for all: G-union run, plus the second-connection capability read (dp_coverage_report.py:104 says Kite 3 per key; Dhan 5; Upstox/Fyers unread).

## Power cut per boundary (attack 5)

M1 safe. M2: cut before `.env` recreate boots old on the full SSD, snapshot minutes lost (N4). M3/M7: N3. M4: OFF on one box only -> double pull, no loss. M5: seal SIGKILL-tested, fsync UNPROVEN (stated). M6: the drill. M8: switch flip, safe. M9: none.

## Not verifiable here

Box IO, free space, lease holder, account topology, Drive state, whether puller930 is writing to SSD now, container restart policies live, G8 behaviour on the box.
