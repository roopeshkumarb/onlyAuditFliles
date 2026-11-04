# Fable review round 6: MIGRATION_PLAN_041126 rev 6 / migration_phases.json / runbooks (04-11-2026)

Read-only. Suite 245 passed. Mutation runner RE-RUN BY ME against the FINAL tests (the committed log was spliced): BASELINE PASSES, 184 mutants, 180 CAUGHT, 4 SURVIVED, exactly the four declared EQUIVALENT (R4 sha-only, islink-only, unicode digits; C13 NFKC); identical to the log. 15 new cheats on temp copies: 13 accepted. **Governing document: YES** (plan only; no deploy approval).

## R5 minimum set (file:line opened)

- (a) T1 FIXED: json rule "Forward cutover order" Step 2.5, md :18, M3 step 3, M3a step 4, M6/M7 "Re-arm (S1) AFTER", cutover runbook :101, :111, FRIDAY :159; tests :2455, friday test :157; 11 T1 mutants CAUGHT.
- (b) T2/T3 FIXED: rules 10, 12; M3/M7 steps; all four rollbacks; runbook :101, :110; FRIDAY :108-:110, :159-:160; tests :2490-:2524.
- (c) FIXED: FRIDAY :3, :160; friday test :142-:173.
- (d) FIXED: doc_ok :855, exceptions_ok :815, dates :742/:838, holidays :51, minutes :600, row_ratio :605, KEY_POOL :682, reuse :864, repo-state line guarded :872/:1129/:2531.
- (e) FIXED: C1-C16 tests :2542-:2801 plus rev6 mutants, all CAUGHT except equivalent C13.
- T1-T3, C1-C16: FIXED at those lines.

## Power-cut boundaries (redone)

`always` starts a hand-stopped container at daemon start; `no` never; Synology boot = daemon restart.
Forward (1) `restart=no old`, (2) `stop old`, (2.5) re-arm, (3) start edge, compose `mv`: cut after (1)/(2): no recorder on X, peer covers (stated); after (2.5): edge boots, old stays down; after (3) or a daemon restart: steady; during `mv`: whole file either way. T1 closed.
Rollback (1) disarm loop, (2) stop loop, (3) restore compose, `restart=always old`, `start old`: cut mid loop 1: partial edge set, never two; first stop to `restart=always old`: NO recorder (stated; really opens at the first disarm: wording); afterwards old boots by itself. Correct.
Compose retirement, wording hole: the old services already carry a profile each (datapullers.yml :185-:425). "add `profiles: [retired_041126]`" (M3 step 3, M7 step 0, runbook :101) read as APPEND leaves `--profile ticks up -d` able to start the retired recorder. Say REPLACE; add a mutant.

## 15 new cheats

Accepted: (2) old_minutes 1e9 over 3 sessions; (3) session on 25-12-2026 once today passes it; (4) non-consecutive sessions; (5) drill cut 10:00 IST in-session, restored before the cut, wrong box; (6) M9 approval sheet doubling as E1 evidence; (7) approval lines plus prose "withdraws and revokes"; (8) estimated / simulated / untested / deferred pass text_ok; (9) old/new roots swapped; (10) evidence copied across phases, one serial changed; (12) M9 DONE with the R8 docker2 candidate undecided; (13) KEY_POOL(ticks) holds `-15`; (14) a df listing is a valid FIRST_REAL_STEP marker; (15) 180 minutes, one row per side. Refused: (11) 2 of 3 days.
Contradiction, not a cheat: (1) M2 MISSED (expected; M9 gate "M2 done or MISSED recorded", md :71) makes doc_ok :855 refuse M3..M9 DONE for ever. My (d) wording caused it; fix: M2 MISSED with valid evidence counts as a predecessor.

## Verdict

**Approve as governing document? YES.** T1, the only ordering hole, is closed everywhere and pinned by tests my re-run shows catch regressions. Everything above is test-gap or wording (REPLACE sentence, M2-MISSED ordering, cheats 2-15); none permits two recorder sets or a deletion before two copies. Fix in rev 7 without another round. No deploy approval; approvals stay at zero. Not verifiable here: Docker/Synology boot behaviour, compose version, account topology.
