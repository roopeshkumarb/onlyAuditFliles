# COMPARISON: outside auditor (OA) vs independent Fable review, same repo state (03-11-2026 ~21:50 IST)
Basis. OA = the verdict pasted by the owner (twice; identical text). OA could only read files 01-04 of BLK-001 (marked everything else CANNOT CHECK because raw text was not fetched). Fable read EVERY file (all inlined), recomputed numbers, ran the tests locally and read the code line by line; it had no box access (box items = CANNOT CHECK unless a raw file shows them). Fable was told nothing of the author's conclusions and did not read AUDITOR_RESPONSES/. Fable and the author are the same model family: treat Fable as a deeper check, not as independence.

## 1. Verdicts
| Item | OA | Fable | Same? | Author's resulting action |
|---|---|---|---|---|
| V-001 livewatch | NOT VERIFIED (3 conditions) | NOT VERIFIED (6 conditions + 13 defects) | YES | v3 written (see 3), not deployed |
| V-002 BLK-002 | VERIFIED WITH CONDITIONS | VERIFIED WITH CONDITIONS for the recorder part; NOT VERIFIED for "H12 candidate tables" | PARTLY | evidence batch 2 (BLK002/05); candidate status downgraded |
| V-003 access | NOT VERIFIED (diagnose i7 502; test boot script by reboot) | NOT VERIFIED (plan unexecuted; i5 route count wrong; no off-LAN test) | YES | doc corrected; owner steps pending |

## 2. Claim by claim (ledger ids)
| Claim | OA | Fable | Note |
|---|---|---|---|
| C-001 9 tests pass | CANNOT CHECK | AGREE (reran) | |
| C-002 5 mutations | CANNOT CHECK | AGREE | |
| C-003 disposable-container proof | AGREE | AGREE (only exercise of the docker-start fallback anywhere) | |
| C-004 production run | AGREE (NOT TESTED) | AGREE | |
| C-005 60 s safe | DISAGREE, wants >=90/120 | AGREE 60 unsafe; 90 ALSO unproven (one day, 4 recorders) | both: do not trust 90 until a multi-day gap histogram exists |
| C-006 retraction | AGREE | AGREE (proven by 18) | |
| C-007 both boxes lost 12:08-12:31, 12:42-12:51 | CANNOT CHECK | AGREE (recomputed +-1 s) | |
| C-008 power cause | AGREE (inference) | AGREE (inference; uptimes not in a raw file) | uptimes still not saved as files |
| C-009 d20 silent 12x i5, 1x i7 | CANNOT CHECK | AGREE: 12 gaps 13:55:51-15:17:41, sum 2753 s = 45.9 min | |
| C-010 recorders under /volume1/docker/datapullers | CANNOT CHECK | AGREE (stronger: rows read from there) | |
| C-011 /volume1 = HDD RAID1 | AGREE (inferred) | AGREE (inferred; size arithmetic fits; the `ssd` mount flag is on every volume incl. /volume1; any SSD cache in front is UNKNOWN) | needs root: mdadm/lvs |
| C-012 table names | CANNOT CHECK | AGREE | |
| C-013 H12 violation in recorder files | AGREE (not supported) | AGREE | |
| C-014/C-015 routes | CANNOT CHECK | AGREE (17), LAN-hop lines are a summary not verbatim ssh output | |
| C-016 boot script | AGREE (NOT TESTED) | AGREE | |
| C-017 5-socket cap cause | UNPROVEN | UNPROVEN; the 211-240 s gap LENGTH is explained by the recorder's own stall guard (dp_recguard STALL_S=180 s + reopen), not by the cause | |
| C-018/C-021 /volume2 full | CANNOT CHECK | AGREE 202G/205G/3.3G/173 GB; DISAGREE with "~3 days": df -h has 1 GB resolution, no rate can be derived | author agrees: downgraded; byte readings started (21:39) |
| C-020 candidate tables | (not yet seen) | AGREE existence+counts; "only copy" UNKNOWN; src_store/copied_at columns point the other way | evidence batch 2 below |
| C-022 path absent | (asked for it) | UNPROVEN (no negative test in the file) | now PROVEN by BLK002/05: `ls: cannot access ... No such file or directory` |

## 3. Defects only Fable found in 02_livewatch.py / 03_test (author's status)
1. False kill of ALL 4 production recorders on wrong --box / --root / unmounted volume (empty root -> NO_FILE_DEAD x4). Real; verified by reading the code. FIXED in v3 (refuses to run, exit 2) + 2 tests; mutation caught.
2. Kill bound was per ROLLING hour; escalation fired once per daemon life. FIXED v3: per IST day, ESCALATE re-armed hourly; mutation caught. Counters are still in memory (a daemon restart resets them): OPEN.
3. Kill of depthrec for one dead d20 drops the healthy d200 and opens two new Dhan sockets while the old may still be counted (805 kicks the oldest, possibly the OTHER box's). FIXED in v3 by default: multi-socket death = ALARM ONLY (--conn-action alarm). Whether alarm-only is right: OWNER DECISION (both auditors' direction agrees).
4. Overlap with three existing remedies (dp_recguard 180 s per-socket reopen, tickrec self-exit, dp_watchdog docker restart). OPEN: owner must choose dp_watchdog OR livewatch; not resolved.
5. File mtime is moved by non-data rows (events table written by dp_recguard) so a connect/close loop looks FRESH. FIXED for depth (per conn), upstox, tbt (judge by frames.recv_ts, v3). NOT fixed for tickrec (ticks table has no index on recv_ts alone; a scan on a ~1 GB table is not acceptable); tickrec still uses status last_tick + mtime. OPEN.
6. Host-TZ dependence (UTC host -> window 14:46-21:00 IST, false kills after 15:36) and future-dated last_tick -> negative age. FIXED v3: IST computed from epoch; last_tick_epoch preferred; future last_tick ignored; tests + mutations. Evidence batch 2: both boxes' /etc/TZ = IST-5:30, so the risk was latent, not live.
7. First pass at 09:16 may kill at the open if the reopened socket has no frame yet. OPEN; needs dry-run sessions.
8. d20 that never connects = UNKNOWN = FRESH; holidays cost up to 3 kills each. OPEN (documented).
9. SQLite mode=ro on a WAL file needs a readable -shm; daemon user unknown. PARTLY: uid is roopeshkumarb (users, administrators, docker) on both boxes (BLK002/05); -shm readability live: NOT TESTED.
10. docker start fallback had NO unit test. FIXED v3: test added; removing the fallback is caught (22 tests).
11. Vacuous test assertions (string match on source, ArgumentParser name). Partly OPEN: the default is still checked by source text; behavioural check at wall-clock time is not meaningful outside session.
12. State dir default /tmp (tmpfs: ESCALATE files vanish on reboot); pid-lock reuse. state dir FIXED v3 (/volume1/docker/datapullers/_state/livewatch_host); pid-lock OPEN.
13. Name clash: compose container `livewatch` (dp_livewatch.py, alert-only) vs host livewatch.py (kills). OPEN: recommend renaming the host program (e.g. recwatch).
Also Fable: INDEX.md md5s for 02/03 stale (TRUE, regenerated); 07/08 made by an older script version (TRUE: they list >60 s gaps, 09 prints >30 s); 20's header said log lines removed but they are not (TRUE, rewritten); i5 "3 routes" is circular (TRUE, corrected in 12).

## 4. Things only OA asked for
- `mdadm --detail`/`lvs` proof of the volume-to-array mapping: needs root, which the author lacks. STILL UNPROVEN.
- Tailscale as a second independent route: kept as recommendation (owner account needed).
- Controlled reboot test of the i5 for the boot script: owner step.
- OA's path /volume1/docker/blpro_data/blpro_working.db: does not exist (BLK002/05 proves it).

## 5. Where Fable's guesses were corrected by new evidence (BLK002/05)
- Fable guessed /volume1/docker/blpro_data/009/app/blpro_working.db was an older HDD copy up to 20-10. `readlink -f` resolves that path to /volume2/blpro_hot/blpro_working.db, the live SSD file (same row counts 73,144 / 23,037). So there is no separate HDD copy: the "HDD path" is a link to the SSD file.
- Fable asked what src_store holds. broker_chain_snap rows: 4 source files (puller930_upstox_151026-0033, pullerfull_dhan_151026-0031, pullerfull_upstox_151026-0031, upstox_121026-1533), ts 14-19 Oct 2026, copied_at 17-19 Oct. broker_quote_depth_snap: 3 source files, same dates. So these are copies of puller-DB snapshots from 14-19 Oct, not today's live capture. The puller DBs on the SSD (dhan/upstox/fyers pullerfull 15-10) contain NO table whose name matches chain|depth|quote, so where the rows originated is UNKNOWN.
- Net: H12 relevance (are these non-recoverable live snapshots stored on SSD?) is UNPROVEN, not a violation. Needs the owner's rule on whether 14-19 Oct chain snapshots are live-only data.

## 6. What neither auditor could resolve (owner or root needed)
Cloudflare dashboard (i7 502 cause), DSM boot task + controlled reboot, mdadm/lvs, owner's decision alarm-only vs kill and dp_watchdog vs livewatch, SSD space plan (T-1312), multi-day gap histogram before fixing a threshold.
