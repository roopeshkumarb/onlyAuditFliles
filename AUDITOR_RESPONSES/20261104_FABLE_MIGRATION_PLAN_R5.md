# Fable review round 5: MIGRATION_PLAN_041126 rev 5 / migration_phases.json / FRIDAY_RUNBOOK (04-11-2026)

Read-only. Suite 148 passed. Author's mutation runner re-run: BASELINE PASSES, 106 CAUGHT, 2 SURVIVED (both EQUIVALENT), identical to the committed log. 25 new cheats on temp copies: **25 accepted**. **Governing document: NO.**

## R4 items (file:line opened)

- S1 FIXED as written (json M3 step 6, M6 step 6, M7 step 4, rule 10; EDGE_CUTOVER_RUNBOOK :111; tests :2074); residue T1.
- S2 PARTLY (json M3 step 2, M7 step 0; runbook :101, :110; tests :2087): T2, T3.
- S3 FIXED in plan and cutover runbook (tests :2062); NOT FIXED in FRIDAY_RUNBOOK :160 (`edge_*` glob, pinned by test_friday_runbook :165).
- S4 FIXED as listed (tests :491-608); residue C3-C10. S5 FIXED as listed (tests :305-327); residue C12, C13, C16. S6 FIXED (tests :388); residue C14.
- S7 FIXED (json `dhan_depth_state_by_phase`; tests :2106). S8 FIXED (json M9 gates 3-4; tests :2120).
- R3 PARTLY: tests :506-608 recompute what the report says about itself, not what the boxes hold (C6-C10).
- R6 FIXED in `edge_snap.py:84-107`; M6 step 5 still asserts "ONE account" while M3 gate 3 says UNVERIFIED.
- R9 PARTLY: TODAY_TESTS pinned (tests :687); :2056 `assertFalse(first_step_taken())` is an unpinned repo-state line that must be edited at the first real marker.

## Power-cut boundaries

Docker `always` starts a hand-stopped container at daemon start; `no` never does; compose auto-enables the profile of a service named on the command line.

Forward (1) old `no`, (2) stop, (S2) compose mark, (3) start edge: cut after (1)/(2): box X without recorder, peer covers (stated). Cut during the S2 swap: half-written compose file unless swapped by rename (plan never says `mv`). After (3), or daemon restart: steady. Rollback: cut mid `no`-loop: part of the edge set boots, old stays down, never two. Cut after the stop loop, before `update --restart=always old`: box X has NO recorder after boot (unstated).

**T1 (new).** Re-arm is "before ANY forward start after a rollback" (M3 step 6, runbook :111) but not ordered AFTER the old recorder's (1)(2). Re-arm first, cut before (2): old (`always`, running) and all edge containers (`always`, hand-stopped) boot together: the 6th socket S1 meant to close. Re-arm must be step 2.5.
**T2.** `profiles: [retired_041126]` does not stop `compose up -d <service>`: naming auto-enables the profile. FRIDAY_RUNBOOK :108 is that form (`up -d fullpuller puller930`, both M7 targets); runbook :110 "the marker, not the command" is false for a named service.
**T3.** A retired service is a compose orphan: `up -d --remove-orphans` or `down` on project datapullers deletes the rollback container. Forbidden nowhere.

## Checker cheats (temp copies, all accepted)

C1 no phase ordering: M9 DONE, M0..M8 NOT_STARTED, E1-E5 unapproved: 89 passed. C2 approval dated 04-11, metrics 30-11. C3 report named 041126 holding sessions 25..27-11. C4 session on 24-11-2026 (NSE holiday; `dp_holidays.py` unused). C5 box `i5` vs `i5 `, root `/x` vs `//x`. C6 `old_minutes=1` per key. C7 row_ratio 1.0 beside old_rows 500 / new_rows 50000. C8 latency None both sides. C9 null_exch 1.0 both sides. C10 required keys `NOT_AN_INSTRUMENT_n`. C11 one file in M3 and M7; approval sheet bytes as evidence. C12 "UNKNOWN", "unverified", "assumed". C13 ZWSP `NOT​MEASURED`, Lisu lookalikes. C14 M7 MISSED saying "finished early". C15 "drill observed" = "mains never pulled". C16 FABLE_I5_REDIRECT + one newline.

## FRIDAY_RUNBOOK

:3 cites rev 4. :159 forward order correct. :160 rollback row: glob, no compose restore, no re-arm. Copies rule, P4 gate, restart=no-before-stop: consistent. :108: T2.

## Verdicts

M0, M1, M4, M5, M8 SOUND. M2 SOUND (:108 wording). M3 FIX (T1, T2). M3a FIX (T1). M6 FIX (T1, C15). M7 FIX (T1-T3). M9 FIX (C1).

**Approve as governing document? NO.** Remaining defects are test-gap or wording level EXCEPT T1, an ordering hole in the plan text. Minimum for YES: (a) T1 fixed in rule 10, M3/M3a/M6/M7 steps, runbook :111, with a mutation test; (b) wording: never name a retired service on an `up` line, never `down`/`--remove-orphans` on datapullers, compose swap by `mv`, rollback no-recorder window stated; (c) FRIDAY_RUNBOOK :3, :160 and test :165 aligned with S1-S3; (d) checker: M(n) DONE needs M(n-1) DONE and the M9 exceptions approved, approval and report dates >= last measurement, holiday table, minutes floor, row_ratio recomputed, key names from the universe, no cross-phase reuse, :2056 guarded; (e) C1-C16 as mutation tests. Plan only; no deploy approval.

## Not verifiable here
Docker/Synology boot behaviour, compose version, account topology, broker limits, box IO, Drive state, NSE 2026 holidays.
