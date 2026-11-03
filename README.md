# onlyAuditFliles: THE ONE LINK (auto-built from LATEST.md, AUDITOR_PROTOCOL.md, CLAIMS_LEDGER.csv, CHANGELOG.md; do not edit by hand)
Page URL (never changes): https://github.com/roopeshkumarb/onlyAuditFliles   Raw text: https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/README.md
Retail NIFTY 50 data-capture system, advisory only (no orders). Evidence files are linked below as <folder>/<file>: prefix them with https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/
Every file's sha256 is in MANIFEST.json / SHA256SUMS. Raw cache can lag a few minutes after a push.

# AUDITOR PROTOCOL: ZERO ASSUMPTION
Rules the author (Claude Code, on the owner's behalf) holds itself to, and asks you to hold the work to:
1. **No claim without a file.** Each claim in CLAIMS_LEDGER.csv names an evidence file. If the evidence is not in this repo, the ledger says `EVIDENCE NOT IN REPO` and you must answer CANNOT CHECK, not SUPPORTS.
2. **UNKNOWN is never zero.** Absence of data is not proof of absence. Mark UNKNOWN.
3. **Do not assume paths, mounts, table names, thresholds or code structure.** Re-derive them from the raw outputs. If a raw output does not show it, it is unproven.
4. **Corrections are public.** A wrong earlier claim is marked RETRACTED in the ledger and listed in CHANGELOG.md; it is never silently edited.
5. **Reproduce when you can.** Each LATEST.md item lists read-only commands the owner (or the author) can run on request. Ask for an output; do not infer it.
6. **Gated build.** The author does not start block N+1 until the owner has verified block N. Your verdict is an input to that decision, not the decision.
## Required answer format (per open item in LATEST.md)
```
ITEM: <id>
FILE-BY-FILE: <path> -> SUPPORTS | DOES NOT SUPPORT | CANNOT CHECK  (one line of reason each)
CLAIMS: <claim id> -> AGREE | DISAGREE | UNPROVEN  (reason)
MISSING PROOF YOU WANT RUN: <exact read-only command, which box>
ASSUMPTIONS YOU FOUND IN THE WORK: <list, or NONE FOUND>
VERDICT: VERIFIED | NOT VERIFIED | VERIFIED WITH CONDITIONS: <conditions>
```
## Limits you should know
The author and any AI agent it spawns share one model family; you are the independent check. The boxes are reachable only by the author, the owner is the gatekeeper for all changes.

---

# LATEST: open for verification (updated 03-11-2026 ~16:20 IST; newest first)
Do not rely on a link pasted elsewhere: this file is the source of truth. Answer using the format in AUDITOR_PROTOCOL.md.

## V-003 | Remote access resilience (no single point of failure) | status: PARTLY PROVEN, FIX PENDING
Files: audit_031126_BLK001_livewatch/12_ACCESS_ROUTES.md, 11_box_reach.sh, 17_access_routes_raw.txt, 10_boot_start_containers.sh
Verify: (a) do the raw tests in 17 support the route table in 12? (b) is the recommended design (one tunnel, three connectors; LAN hops; independent second overlay; UPS) sound, what is missing? (c) any assumption about Cloudflare configuration (which is NOT visible to the author)?
Known unproven: why two Cloudflare hostnames return Bad Gateway; any login from outside the home network; the boot script across a real reboot.

## V-002 | BLK-002 step 1: H12 recoverability routing, RAW PROOF ONLY (no code exists) | status: AWAITING AUDITOR
Files: audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt, 02_Q2_code_paths.txt, 03_Q3_tables.txt
Verify: (a) does 01 prove which mount is the HDD RAID1 on each box? The author claims only: recorders write under /volume1/docker/datapullers on both boxes (proven); /volume1 = RAID1 on rotational disks (INFERRED from md sizes and rotational flags; lvs was denied, so the volume-to-array mapping is NOT proven). (b) does 02 show every place a recorder database path is built? (c) do the table lists in 03 match your reading, and is the author right that no listed table is named *chain*? (d) is the proposed dictionary (in the owner's chat; summarised in CLAIMS_LEDGER C-010..C-012) justified by the raw proof alone?
Author's finding to challenge: the four recorders already write to the HDD volume, so BLK-002's premise (recorder tables violate H12) is not supported by this evidence. Any H12 violation would be in the puller databases (option_chain / quote_depth), which have NOT been queried.
Reproduce on request: `df -h; mount | grep volume; cat /proc/mdstat` on i5 and i7; `sqlite3 -readonly <file> .tables`.

## V-001 | BLK-001: data-freshness watchdog (livewatch) | status: AWAITING AUDITOR, owner verification pending
Files: audit_031126_BLK001_livewatch/INDEX.md (start with 00 and 01, then 13 ADDENDUM which CORRECTS 01 in one respect).
Verify: the 7 questions in 01_REPORT_BLK001.md section 6, plus: (a) 13 says livewatch, judging the day file, would NOT detect a dead Dhan d20 socket while d200 keeps writing (i5: 12 silent gaps of ~4 min, 13:55-15:17). Confirm from files 09/16 and 14/15 and the d20 gap numbers quoted in 13. (b) 13 says the 60 s limit is within 5 s of a healthy gap (55 s, i5 upstox 14:24:57-14:25:52). Is 90 s defensible? (c) the 5 mutation tests (05) and the disposable-container proof (04): what do they NOT prove?
Retracted: the first version of 13 point 1 ("only gaps over 60 s are the power windows"). See CLAIMS_LEDGER C-006 and CHANGELOG.
Known unproven: livewatch against production recorders; as a daemon across a reboot; per-connection checks (not built).

## Older, already published
audit_031126_live_only_and_data_master/INDEX.md (live-only data per broker and the retail data master; three earlier outside audits scored it PARTLY).

---

## CLAIMS LEDGER (CSV)
```
id,date,claim,status,evidence_file,note
C-001,03-11-2026,livewatch unit tests: 9 pass,PROVEN,audit_031126_BLK001_livewatch/06_unit_tests_output.txt,tests use a fake docker so they prove decision logic only
C-002,03-11-2026,5 deliberate code breaks (mutations) are each caught by the tests,PROVEN,audit_031126_BLK001_livewatch/05_mutation_log.txt,file restored after each
C-003,03-11-2026,livewatch kills then starts a stale disposable container on the i5 and leaves a fresh one alone,PROVEN,audit_031126_BLK001_livewatch/04_proof_i5_raw.txt,disposable container only; section G (production untouched) is empty
C-004,03-11-2026,livewatch works on the four production recorders,NOT TESTED,,never run against production
C-005,03-11-2026,60 s staleness limit is safe,UNPROVEN - CONTRADICTED,audit_031126_BLK001_livewatch/14_end_of_session_gaps_i5.txt,healthy 55 s gap on i5 upstox 14:24:57-14:25:52; recommend 90 s (owner decision)
C-006,03-11-2026,"the only gaps over 60 s today are the two power windows (first version of addendum 13, point 1)",RETRACTED,audit_031126_BLK001_livewatch/13_ADDENDUM_end_of_session.md,wrong: gap script merged Dhan d20 and d200; see C-009
C-007,03-11-2026,both boxes lost all four recorders ~12:08-12:31 and ~12:42-12:51 (live-only data lost on both),PROVEN,audit_031126_BLK001_livewatch/14_end_of_session_gaps_i5.txt + 15_end_of_session_gaps_i7.txt,gap start/end from recv_ts in the day files
C-008,03-11-2026,cause of C-007 was site power loss,INFERENCE,audit_031126_BLK001_livewatch/01_REPORT_BLK001.md,not proven; both boxes rebooted (uptime) and the Pi did not
C-009,03-11-2026,Dhan d20 socket was silent ~4 min 12 times on i5 (13:55-15:17) and once on i7 (13:59:58-14:04:16); d200 had no gap outside power windows,PROVEN (numbers in text),audit_031126_BLK001_livewatch/13_ADDENDUM_end_of_session.md + 16_depth_conn_gap_script.py,raw per-connection output not saved as a file - ask for a re-run
C-010,03-11-2026,all four recorders write under /volume1/docker/datapullers on both boxes,PROVEN,audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt + 02_Q2_code_paths.txt,DP_ROOT=/data bound to that path in docker-compose.datapullers.yml (repo copy; running code not read)
C-011,03-11-2026,/volume1 is the RAID1 HDD volume,INFERRED not proven,audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt,md arrays + rotational=1 disks support it; lvs/vgs denied so volume-to-array mapping unproven
C-012,03-11-2026,recorder table names: depth/upstox = events frames instruments; ticks = instruments_today session_log ticks; tbt = events frames instruments texts; none named *chain*,PROVEN,audit_031126_BLK002_raw_proof/03_Q3_tables.txt,newest day file on both boxes
C-013,03-11-2026,H12 violation exists in the live recorder files,UNPROVEN - NOT SUPPORTED,audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt,recorders already on HDD volume; puller DB tables (option_chain/quote_depth) NOT queried
C-014,03-11-2026,LAN SSH works in all 6 directions between i5 i7 and Pi,PROVEN,audit_031126_BLK001_livewatch/17_access_routes_raw.txt,
C-015,03-11-2026,Cloudflare SSH works for i5 and Pi; fails (Bad Gateway) for i7 and for the Pi second hostname,PROVEN,audit_031126_BLK001_livewatch/17_access_routes_raw.txt,cause of the Bad Gateway UNKNOWN (dashboard not visible to the author)
C-016,03-11-2026,boot-start script restores containers after a real reboot,NOT TESTED,audit_031126_BLK001_livewatch/10_boot_start_containers.sh,needs DSM Task Scheduler entry by the owner
C-017,03-11-2026,Dhan d20 gaps are caused by the 5-socket cap shared by both boxes,UNPROVEN,,hypothesis only (T-1311)
C-018,03-11-2026,/volume2 on the i5 is 99% full (3.6G free),PROVEN,audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt,
```

---

# CHANGELOG (newest first; corrections are marked CORRECTION)
- 03-11-2026 16:20 IST: added README (fixed entry point), AUDITOR_PROTOCOL, LATEST, CLAIMS_LEDGER, MANIFEST/SHA256SUMS, AUDITOR_RESPONSES template, 17_access_routes_raw.txt.
- 03-11-2026 16:10 IST: CORRECTION to 13_ADDENDUM: Dhan d20 gaps were hidden because the gap script merged d20 and d200 frames. Claim C-006 RETRACTED. livewatch consequence added.
- 03-11-2026 15:55 IST: added BLK-002 step 1 raw proof (no code written).
- 03-11-2026 15:50 IST: added end-of-session numbers (13-15); found 55 s healthy gap vs 60 s limit.
- 03-11-2026 13:50 IST: BLK-001 report and 12 files.
- 02-11-2026: live-only data per broker and retail data master.
