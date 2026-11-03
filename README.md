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

# LATEST: open for verification (updated 03-11-2026 ~21:20 IST; newest first)
Do not rely on a link pasted elsewhere: this file is the source of truth, and README.md inlines every evidence file named below. Answer using the format in AUDITOR_PROTOCOL.md.

## RESUBMISSION after your first response (stored in AUDITOR_RESPONSES/): V-001 v2, V-002, V-003. Author's reply: AUDITOR_RESPONSES/20261103_author_reply_1.md
### V-001 v2 | livewatch with 90 s default and per-connection check | status: AWAITING AUDITOR (code written + tested, NOT deployed)
Evidence (all inlined below): 23 diff v1->v2, 20 tests (13 pass), 21 two mutations caught, 24 query on real files, 18/19 raw per-connection d20 gaps, 13 addendum, 14/15 gaps, 05/06 v1 tests+mutations.
Verify: (a) do 18/19 prove the d20 gaps are real? (b) does the 23 diff implement your conditions 1 and 2 without new assumptions (UNKNOWN never kills; a conn with no rows is UNKNOWN, so a d20 that never connects is only caught by the file-level rule)? (c) design question in the author reply, point 3: detect + bounded kill + ESCALATE, or alarm only for d20? (d) what do the tests still not prove?
### V-002 v2 | BLK-002 scope redefined to puller/engine databases (no code written) | status: AWAITING AUDITOR
Evidence: BLK002 01-03 (recorders, inlined) and 04 (NEW: engine DB tables, SSD volume).
Findings: broker_chain_snap (73,144 rows) and broker_quote_depth_snap (23,037 rows) live in /volume2/blpro_hot/blpro_working.db on the SSD; origin (copy vs only copy) UNKNOWN. /volume2 on i5 is 202G/205G used, driven by /volume2/datapullers (173 GB, puller DBs). T-1312. No deletion done.
Verify: is the evidence in 04 enough to call these tables H12 candidates, and what exact read-only query do you want next (row time range, src_store values, comparison against a recorder file)?
### V-003 | remote access | status: NOT VERIFIED (owner steps pending: Cloudflare dashboard, DSM boot task)
Evidence inlined: 17, 12, 10, 11.

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
C-005,03-11-2026,60 s staleness limit is safe,UNPROVEN - CONTRADICTED (auditor DISAGREE),audit_031126_BLK001_livewatch/14_end_of_session_gaps_i5.txt,healthy 55 s gap i5 upstox; livewatch v2 default is 90 s (code only, not deployed)
C-006,03-11-2026,"the only gaps over 60 s today are the two power windows (first version of addendum 13, point 1)",RETRACTED,audit_031126_BLK001_livewatch/13_ADDENDUM_end_of_session.md,wrong: gap script merged Dhan d20 and d200; see C-009
C-007,03-11-2026,both boxes lost all four recorders ~12:08-12:31 and ~12:42-12:51 (live-only data lost on both),PROVEN,audit_031126_BLK001_livewatch/14_end_of_session_gaps_i5.txt + 15_end_of_session_gaps_i7.txt,gap start/end from recv_ts in the day files
C-008,03-11-2026,cause of C-007 was site power loss,INFERENCE,audit_031126_BLK001_livewatch/01_REPORT_BLK001.md,not proven; both boxes rebooted (uptime) and the Pi did not
C-009,03-11-2026,Dhan d20 socket silent ~4 min 12 times on i5 (13:55-15:17) and once on i7 (13:59:58-14:04:16); d200 no gap outside power windows,PROVEN,audit_031126_BLK001_livewatch/18_d20_conn_gaps_raw_i5.txt + 19_d20_conn_gaps_raw_i7.txt,raw output now saved (re-run 21:01 IST)
C-010,03-11-2026,all four recorders write under /volume1/docker/datapullers on both boxes,PROVEN,audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt + 02_Q2_code_paths.txt,DP_ROOT=/data bound to that path in docker-compose.datapullers.yml (repo copy; running code not read)
C-011,03-11-2026,/volume1 is the RAID1 HDD volume,INFERRED not proven,audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt,md arrays + rotational=1 disks support it; lvs/vgs denied so volume-to-array mapping unproven
C-012,03-11-2026,recorder table names: depth/upstox = events frames instruments; ticks = instruments_today session_log ticks; tbt = events frames instruments texts; none named *chain*,PROVEN,audit_031126_BLK002_raw_proof/03_Q3_tables.txt,newest day file on both boxes
C-013,03-11-2026,H12 violation exists in the live recorder files,UNPROVEN - NOT SUPPORTED,audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt,recorders already on HDD volume; puller DB tables (option_chain/quote_depth) NOT queried
C-014,03-11-2026,LAN SSH works in all 6 directions between i5 i7 and Pi,PROVEN,audit_031126_BLK001_livewatch/17_access_routes_raw.txt,
C-015,03-11-2026,Cloudflare SSH works for i5 and Pi; fails (Bad Gateway) for i7 and for the Pi second hostname,PROVEN,audit_031126_BLK001_livewatch/17_access_routes_raw.txt,cause of the Bad Gateway UNKNOWN (dashboard not visible to the author)
C-016,03-11-2026,boot-start script restores containers after a real reboot,NOT TESTED,audit_031126_BLK001_livewatch/10_boot_start_containers.sh,needs DSM Task Scheduler entry by the owner
C-017,03-11-2026,Dhan d20 gaps are caused by the 5-socket cap shared by both boxes,UNPROVEN,,hypothesis only (T-1311)
C-018,03-11-2026,/volume2 on the i5 is 99% full (3.6G free),PROVEN,audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt,
C-019,03-11-2026,livewatch v2 catches a dead d20 while d200 keeps the file fresh,PROVEN on a synthetic DB only,audit_031126_BLK001_livewatch/20_unit_tests_v2_output.txt + 21_mutations_v2.txt,query runs on the real file (24) but live detection NOT TESTED; v2 not deployed
C-020,03-11-2026,H12 candidate tables broker_chain_snap (73144 rows) and broker_quote_depth_snap (23037 rows) exist in the live SSD engine DB /volume2/blpro_hot/blpro_working.db,PROVEN (existence+counts),audit_031126_BLK002_raw_proof/04_h12_puller_dbs_and_volume2_raw.txt,whether they are the only copy: UNKNOWN
C-021,03-11-2026,/volume2 on i5 is 202G of 205G used (3.3G free); /volume2/datapullers is 173 GB,PROVEN,audit_031126_BLK002_raw_proof/04_h12_puller_dbs_and_volume2_raw.txt,T-1312; time-to-full (~3 days) is a rough estimate from two df readings
C-022,03-11-2026,path /volume1/docker/blpro_data/blpro_working.db exists,FALSE (not present),audit_031126_BLK002_raw_proof/04_h12_puller_dbs_and_volume2_raw.txt,engine DB copies listed in the file
```

---

# CHANGELOG (newest first; corrections are marked CORRECTION)
- 03-11-2026 21:20 IST: auditor 1 response stored; README now inlines all evidence; livewatch v2 (90 s + per-connection) written, NOT deployed; new files 18-24 and BLK002/04; C-005, C-009 updated, C-019..C-022 added; /volume2 99% full registered (T-1312).
- 03-11-2026 16:20 IST: added README (fixed entry point), AUDITOR_PROTOCOL, LATEST, CLAIMS_LEDGER, MANIFEST/SHA256SUMS, AUDITOR_RESPONSES template, 17_access_routes_raw.txt.
- 03-11-2026 16:10 IST: CORRECTION to 13_ADDENDUM: Dhan d20 gaps were hidden because the gap script merged d20 and d200 frames. Claim C-006 RETRACTED. livewatch consequence added.
- 03-11-2026 15:55 IST: added BLK-002 step 1 raw proof (no code written).
- 03-11-2026 15:50 IST: added end-of-session numbers (13-15); found 55 s healthy gap vs 60 s limit.
- 03-11-2026 13:50 IST: BLK-001 report and 12 files.
- 02-11-2026: live-only data per broker and retail data master.


---

## EVIDENCE, INLINE (so one fetch of this page is enough; each block = one repo file, with its sha256)

### FILE audit_031126_BLK001_livewatch/13_ADDENDUM_end_of_session.md  sha256=b4aa952a90ca233a  bytes=2816
```
# ADDENDUM 03-11-2026 15:50 IST: end-of-session numbers (changes one conclusion in 01_REPORT_BLK001.md)
Source: files 14 (i5) and 15 (i7), produced by 09_gapdb_script.py (now listing every gap > 30 s) at 15:4x IST, after the session. Rows counted from 09:15. Ticks use the NIFTY 50 token only.
| Recorder | i5 rows | i7 rows | i5 gaps > 30 s | i7 gaps > 30 s |
|---|---|---|---|---|
| ticks (NIFTY token) | 85,363 | 84,268 | 2 (the outages) | 2 (the outages) |
| depth frames | 135,300 | 152,017 | 2 | 3 (+39 s at 15:08:03) |
| upstox frames | 123,915 | 129,384 | 3 (+55 s at 14:24:57-14:25:52) | 6 (+31, 31, 39, 38 s) |
| fyers tbt frames | 75,760 | 72,297 | 2 | 2 |
All recorders on both boxes last wrote 15:35:00-15:35:21 (they stop themselves after the session; at 15:41 the file ages were 358-378 s, as expected).
## What this changes
1. **CORRECTION (16:10 IST, supersedes my first version of this point).** I wrote that the only gaps over 60 s were the two power windows and that livewatch had nothing to catch. That was WRONG for Dhan depth: my gap script merged the `d20` and `d200` connections of `depth_*.db`. Split by the `conn` column: **i5 d20 has 12 silent gaps of 211-240 s between 13:55 and 15:17 (~46 min of ~82), i7 d20 has one (13:59:58 -> 14:04:16, 257 s); d200 had no gap outside the power windows.** The recorder's own status.json logs 'd20 SILENT 199 s while connected - dropping it' (i5 13:59:10; i7 14:03:13 shows 194 s). Cause UNKNOWN. UNPROVEN hypothesis: both boxes use one Dhan account and the 5-socket cap kicks sockets off.
   **Consequence for BLK-001:** livewatch judges the day FILE; d200 keeps writing, so the file stays fresh while d20 (50 contracts) is dead. livewatch as written would NOT have detected this, and its remedy (`docker kill depthrec`) would drop the healthy d200 as well. Per-connection freshness is needed.
2. **The 60 s threshold is too close to normal behaviour for upstox.** The longest non-outage gap is 55 s (i5 upstox, 14:24:57 -> 14:25:52); the i7 has four upstox gaps of 31-39 s. A strict 60 s rule would have been within 5 s of killing a healthy recorder on the i5, and the i7 (load 25-29) is closer still. Earlier support for 60 s (a 4 s maximum in a 150 s sample) was too short a sample. RECOMMENDATION: 90 s from 09:16, and measure per recorder before locking. This is a deviation from the owner's 60 s order and needs his decision.
3. **Row counts differ between boxes** (e.g. depth: i7 +12%; upstox: i7 +4%; fyers tbt: i5 +5%). Cause UNKNOWN: the boxes subscribe to slightly different strike windows, and the outages differ by minutes. Do not treat either box as the complete record.
4. Unchanged: livewatch has still not run against production recorders; the boot script and access routes are untested across a real reboot / from outside the LAN.
```

### FILE audit_031126_BLK001_livewatch/18_d20_conn_gaps_raw_i5.txt  sha256=1fafbc6c9656ac78  bytes=623
```
route i5-cf failed (rc=124: )
ROUTE: pi-cf>i5
host: i5-4590-dsm72  run at 03-11-2026 21:01:07
d20 gaps>60s: [('12:08:06', '12:27:06', 1140), ('12:42:07', '12:50:49', 521), ('13:55:51', '13:59:41', 230), ('13:59:52', '14:03:44', 231), ('14:06:09', '14:09:41', 211), ('14:10:24', '14:14:12', 228), ('14:17:44', '14:21:41', 236), ('14:22:12', '14:26:11', 239), ('14:28:26', '14:32:11', 225), ('14:37:42', '14:41:41', 238), ('14:46:14', '14:50:11', 236), ('15:01:57', '15:05:41', 224), ('15:08:36', '15:12:11', 215), ('15:13:40', '15:17:41', 240)]
d200 gaps>60s: [('12:08:05', '12:27:06', 1141), ('12:42:07', '12:50:44', 517)]
```

### FILE audit_031126_BLK001_livewatch/19_d20_conn_gaps_raw_i7.txt  sha256=d92ff392874309d8  bytes=339
```
route j1800-cf failed (rc=255: Bad Gateway Connection closed by UNKNOWN port 65535 )
ROUTE: i5-cf>i7
host: I7-3RD-exJ1800  run at 03-11-2026 20:58:42
d20 gaps>60s: [('12:09:31', '12:31:20', 1309), ('12:42:08', '12:48:47', 399), ('13:59:58', '14:04:16', 257)]
d200 gaps>60s: [('12:09:31', '12:31:20', 1309), ('12:42:07', '12:48:45', 398)]
```

### FILE audit_031126_BLK001_livewatch/16_depth_conn_gap_script.py  sha256=e64d9b1ecd993d05  bytes=570
```
import sqlite3,sys,time
box=sys.argv[1]
c=sqlite3.connect("file:/volume1/docker/datapullers/depth/%s/depth_20261103.db?mode=ro"%box,uri=True,timeout=10)
t0=time.mktime(time.strptime("2026-11-03 09:15","%Y-%m-%d %H:%M"))
for conn in ("d20","d200"):
    prev=None;g=[]
    for (t,) in c.execute("select recv_ts from frames where conn=? and recv_ts>=? order by recv_ts",(conn,t0)):
        if prev and t-prev>60: g.append((time.strftime("%H:%M:%S",time.localtime(prev)),time.strftime("%H:%M:%S",time.localtime(t)),int(t-prev)))
        prev=t
    print(conn,"gaps>60s:",g)
```

### FILE audit_031126_BLK001_livewatch/14_end_of_session_gaps_i5.txt  sha256=f381427f1442eef3  bytes=576
```
ticks rows(since 09:15)=85363 last=15:35:05 gaps>30s=2  gaps>30s:
   12:08:36 -> 12:26:05  (1049 s)
   12:42:18 -> 12:48:23  (365 s)
depth rows(since 09:15)=135300 last=15:35:09 gaps>30s=2  gaps>30s:
   12:08:06 -> 12:27:06  (1141 s)
   12:42:07 -> 12:50:44  (517 s)
upstox_live rows(since 09:15)=123915 last=15:35:20 gaps>30s=3  gaps>30s:
   12:08:16 -> 12:27:58  (1182 s)
   12:42:08 -> 12:51:25  (557 s)
   14:24:57 -> 14:25:52  (55 s)
fyers_tbt rows(since 09:15)=75760 last=15:35:19 gaps>30s=2  gaps>30s:
   12:08:20 -> 12:28:47  (1227 s)
   12:42:07 -> 12:48:59  (413 s)
```

### FILE audit_031126_BLK001_livewatch/15_end_of_session_gaps_i7.txt  sha256=30ca23dbfb5cee8f  bytes=704
```
ticks rows(since 09:15)=84268 last=15:35:05 gaps>30s=2  gaps>30s:
   12:09:16 -> 12:30:51  (1295 s)
   12:42:16 -> 12:48:30  (374 s)
depth rows(since 09:15)=152017 last=15:35:13 gaps>30s=3  gaps>30s:
   12:09:31 -> 12:31:20  (1310 s)
   12:42:08 -> 12:48:45  (398 s)
   15:08:03 -> 15:08:42  (39 s)
upstox_live rows(since 09:15)=129384 last=15:35:00 gaps>30s=6  gaps>30s:
   12:08:29 -> 12:30:57  (1348 s)
   12:42:08 -> 12:48:36  (388 s)
   13:52:23 -> 13:52:53  (31 s)
   13:55:11 -> 13:55:43  (31 s)
   14:38:32 -> 14:39:10  (39 s)
   15:20:35 -> 15:21:13  (38 s)
fyers_tbt rows(since 09:15)=72297 last=15:35:21 gaps>30s=2  gaps>30s:
   12:08:46 -> 12:31:48  (1381 s)
   12:42:08 -> 12:48:30  (383 s)
```

### FILE audit_031126_BLK001_livewatch/23_livewatch_v1_to_v2.diff  sha256=80c7f165a37801ea  bytes=4012
```
--- 02a_livewatch_v1.py	2026-11-03 15:33:21.376920875 +0000
+++ 02_livewatch.py	2026-11-03 15:33:21.426122472 +0000
@@ -6,7 +6,7 @@
 stored and, when the data stops during the session, issues `docker kill <container>` so the restart
 policy (and, if that does not bring it back, a `docker start`) replaces the dead socket.
 
-THE RULE (as ordered): during the session, if now - last_data > STALE_S (default 60 s), run
+THE RULE (as ordered): during the session, if now - last_data > STALE_S (default 90 s since v2; the owner ordered 60 s), run
 `docker kill <container>`.
   last_data = the newest of (a) status.json "last_tick" when the recorder writes one (Kite ticks) and
               (b) the modification time of today's day file or its -wal (every stored row moves it).
@@ -42,6 +42,10 @@
     "upstoxrec": ("upstox_live", "upstox_"),
     "fyerstbt": ("fyers_tbt", "tbt_"),
 }
+# v2 (auditor condition, 03-11-2026): a recorder that writes SEVERAL sockets into ONE day file hides a dead socket behind
+# the live ones (Dhan: d20 silent ~4 min 12 times on the i5 while d200 kept the file fresh). So judge each connection by
+# the newest recv_ts of its own rows. Unreadable DB / no rows for the connection = UNKNOWN (never killed on UNKNOWN).
+CONNS = {"depthrec": ("frames", "conn", ("d20", "d200"))}
 NEVER_TOUCH = ("cloudflared", "portainer", "blpro_09", "blpro_compute", "blpro_synchub",
                "blpro_vendorwatch", "watchtower")
 DEFAULT_DOCKER = "/var/packages/ContainerManager/target/usr/bin/docker"
@@ -81,6 +85,24 @@
         return 0.0
 
 
+def conn_last(path, spec):
+    """-> {conn: last recv_ts or None}; None = UNKNOWN (db unreadable, locked, or no rows for that conn)."""
+    table, col, conns = spec
+    out = {c: None for c in conns}
+    try:
+        import sqlite3
+        con = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=3)
+        try:
+            for c in conns:
+                r = con.execute("select recv_ts from %s where %s=? order by recv_ts desc limit 1" % (table, col), (c,)).fetchone()
+                out[c] = float(r[0]) if r and r[0] is not None else None
+        finally:
+            con.close()
+    except Exception:
+        pass
+    return out
+
+
 def evaluate(name, root, box, now, stale_s, no_file_after):
     """-> dict(verdict, age_s, why). verdict in FRESH, DEAD, NO_FILE_DEAD, NO_FILE_WAITING."""
     folder, prefix = RECORDERS[name]
@@ -107,7 +129,17 @@
                 "why": "last data %.0f s ago (limit %.0f s); file_write=%s last_tick=%s" % (
                     age, stale_s, time.strftime("%H:%M:%S", time.localtime(fw)),
                     time.strftime("%H:%M:%S", time.localtime(lt)) if lt else "n/a")}
-    return {"verdict": "FRESH", "age_s": round(age, 1), "why": "last data %.1f s ago" % age}
+    why = "last data %.1f s ago" % age
+    if name in CONNS:
+        cl = conn_last(path, CONNS[name])
+        dead = ["%s silent %.0f s" % (c, now - t) for c, t in sorted(cl.items()) if t is not None and now - t > stale_s]
+        unk = [c for c, t in sorted(cl.items()) if t is None]
+        if dead:
+            return {"verdict": "DEAD", "age_s": round(age, 1),
+                    "why": "file is fresh but connection(s) dead: %s (limit %.0f s)" % (", ".join(dead), stale_s)}
+        if unk:
+            why += "; connection check UNKNOWN for %s (not judged)" % ",".join(unk)
+    return {"verdict": "FRESH", "age_s": round(age, 1), "why": why}
 
 
 class Watch(object):
@@ -187,7 +219,7 @@
     p.add_argument("--root", required=True)
     p.add_argument("--box", required=True)
     p.add_argument("--docker", default=DEFAULT_DOCKER)
-    p.add_argument("--stale-s", type=float, default=60.0)
+    p.add_argument("--stale-s", type=float, default=90.0)   # v2: 60 s was 5 s from a healthy 55 s gap (i5 upstox 14:24:57-14:25:52)
     p.add_argument("--session-start", default="09:16")
     p.add_argument("--session-end", default="15:30")
     p.add_argument("--no-file-after", default="09:20")
```

### FILE audit_031126_BLK001_livewatch/20_unit_tests_v2_output.txt  sha256=7159fa8223c1aec1  bytes=2279
```
livewatch v2 unit tests, run 03-11-2026 21:03 IST on the sandbox (python3 -W ignore -m unittest -v tests.test_livewatch), log lines of the code under test removed
test_a_stale_file_triggers_exactly_docker_kill_of_that_container ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] WARN depthrec: last data 120 s ago (limit 90 s); file_write=10:28:00 last_tick=n/a -> docker kill depthrec
test_both_connections_fresh_nothing_killed ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 3.0 s ago)
test_dead_d20_is_caught_even_though_the_file_is_fresh ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] WARN depthrec: file is fresh but connection(s) dead: d20 silent 200 s (limit 90 s) -> docker kill depthrec
test_default_limit_is_90_and_a_55s_healthy_gap_is_left_alone ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago; connection check UNKNOWN for d20,d200 (not judged))
test_dry_run_prints_but_runs_nothing ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] WARN depthrec: last data 500 s ago (limit 90 s); file_write=10:21:40 last_tick=n/a -> docker kill depthrec
test_fresh_data_is_left_alone ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago; connection check UNKNOWN for d20,d200 (not judged))
test_it_refuses_strangers ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] REFUSE cloudflared is not a managed recorder
test_kills_are_bounded_per_hour_then_escalate ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago; connection check UNKNOWN for d20,d200 (not judged))
test_no_day_file_after_0920_with_no_instruments_is_dead ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago; connection check UNKNOWN for d20,d200 (not judged))
test_outside_the_session_and_on_weekends_nothing_is_killed ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] INFO outside session window 09:16-15:30: nothing to judge
test_proof_mode_judges_only_the_disposable_recorder ... ok
test_status_last_tick_counts_when_the_file_is_old ... 03-11-2026 21:03:21 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago; connection check UNKNOWN for d20,d200 (not judged))
test_unreadable_depth_db_is_unknown_not_dead ... ok
Ran 13 tests in 0.179s
OK
```

### FILE audit_031126_BLK001_livewatch/21_mutations_v2.txt  sha256=434a4356898f5440  bytes=499
```
v2 mutation checks, 03-11-2026 evening, applied to pullers/shared/livewatch.py, then restored (md5 after restore ca711e8c12bca8cb11e4d53b79e0e037, 13 tests OK):
M1 per-connection comparison weakened (now - t > stale_s  ->  now - t > stale_s*100): FAIL test_dead_d20_is_caught_even_though_the_file_is_fresh  (Ran 13, FAILED failures=1)
M2 command-line default changed back (default=90.0 -> default=60.0): FAIL test_default_limit_is_90_and_a_55s_healthy_gap_is_left_alone  (Ran 13, FAILED failures=1)
```

### FILE audit_031126_BLK001_livewatch/24_conn_last_on_real_db.txt  sha256=4487d60ca2f260ff  bytes=425
```
livewatch v2 function conn_last() run READ-ONLY on the real 03-11 depth files (copy of the v2 file in /tmp, deleted after; NOT deployed):
i5: {'d20': '15:35:09', 'd200': '15:35:09'} took 0.00 s
i7: {'d20': '15:35:13', 'd200': '15:35:12'} took 0.85 s
LIMIT: the market was closed, so this proves the query runs on the real file and is fast; it does NOT prove detection on a live dead socket (only the synthetic-DB test does).
```

### FILE audit_031126_BLK001_livewatch/05_mutation_log.txt  sha256=8d46373608f34d41  bytes=2088
```
MUTATION TESTING of pullers/shared/livewatch.py, 03-11-2026 06:42:49 box-clock; each mutation is applied to the real file, the 9 tests are run, then the file is restored from a copy.
== BASELINE
Ran 9 tests in 0.125s
OK
== MUTATION 1: threshold comparison reversed (age > stale_s -> age < stale_s)
FAIL: test_a_stale_file_triggers_exactly_docker_kill_of_that_container (__main__.T.test_a_stale_file_triggers_exactly_docker_kill_of_that_container)
FAIL: test_fresh_data_is_left_alone (__main__.T.test_fresh_data_is_left_alone)
FAIL: test_kills_are_bounded_per_hour_then_escalate (__main__.T.test_kills_are_bounded_per_hour_then_escalate)
FAIL: test_no_day_file_after_0920_with_no_instruments_is_dead (__main__.T.test_no_day_file_after_0920_with_no_instruments_is_dead)
FAIL: test_status_last_tick_counts_when_the_file_is_old (__main__.T.test_status_last_tick_counts_when_the_file_is_old)
Ran 9 tests in 0.192s
FAILED (failures=5)
== MUTATION 2: kill action replaced (docker kill -> docker version)
FAIL: test_a_stale_file_triggers_exactly_docker_kill_of_that_container (__main__.T.test_a_stale_file_triggers_exactly_docker_kill_of_that_container)
FAIL: test_kills_are_bounded_per_hour_then_escalate (__main__.T.test_kills_are_bounded_per_hour_then_escalate)
FAIL: test_no_day_file_after_0920_with_no_instruments_is_dead (__main__.T.test_no_day_file_after_0920_with_no_instruments_is_dead)
Ran 9 tests in 0.131s
FAILED (failures=3)
== MUTATION 3: guard against non-recorder names removed
FAIL: test_it_refuses_strangers (__main__.T.test_it_refuses_strangers)
Ran 9 tests in 0.116s
FAILED (failures=1)
== MUTATION 4: per-hour kill bound removed
FAIL: test_kills_are_bounded_per_hour_then_escalate (__main__.T.test_kills_are_bounded_per_hour_then_escalate)
Ran 9 tests in 0.108s
FAILED (failures=1)
== MUTATION 5: out-of-session guard removed
FAIL: test_outside_the_session_and_on_weekends_nothing_is_killed (__main__.T.test_outside_the_session_and_on_weekends_nothing_is_killed)
Ran 9 tests in 0.135s
FAILED (failures=1)
== RESTORED
797db99be487259491a35dd5afd2751c
Ran 9 tests in 0.113s
OK
```

### FILE audit_031126_BLK001_livewatch/06_unit_tests_output.txt  sha256=d8cc21a9892b855f  bytes=1373
```
test_a_stale_file_triggers_exactly_docker_kill_of_that_container ... 03-11-2026 13:41:32 GMT+5:30 [livewatch i5] WARN depthrec: last data 120 s ago (limit 60 s); file_write=10:28:00 last_tick=n/a -> docker kill depthrec
test_dry_run_prints_but_runs_nothing ... 03-11-2026 13:41:32 GMT+5:30 [livewatch i5] WARN depthrec: last data 500 s ago (limit 60 s); file_write=10:21:40 last_tick=n/a -> docker kill depthrec
test_fresh_data_is_left_alone ... 03-11-2026 13:41:32 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago)
test_it_refuses_strangers ... 03-11-2026 13:41:32 GMT+5:30 [livewatch i5] REFUSE cloudflared is not a managed recorder
test_kills_are_bounded_per_hour_then_escalate ... 03-11-2026 13:41:32 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago)
test_no_day_file_after_0920_with_no_instruments_is_dead ... 03-11-2026 13:41:32 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago)
test_outside_the_session_and_on_weekends_nothing_is_killed ... 03-11-2026 13:41:32 GMT+5:30 [livewatch i5] INFO outside session window 09:16-15:30: nothing to judge
test_proof_mode_judges_only_the_disposable_recorder ... ok
test_status_last_tick_counts_when_the_file_is_old ... 03-11-2026 13:41:32 GMT+5:30 [livewatch i5] OK depthrec FRESH (last data 5.0 s ago)
Ran 9 tests in 0.101s
OK
(run 03-11-2026 13:41 IST on the sandbox, TZ=Asia/Kolkata)
```

### FILE audit_031126_BLK002_raw_proof/01_Q1_mounts_i5_i7.txt  sha256=3ba1d4c8a1442a6f  bytes=6364
```
BLK-002 STEP 1 RAW PROOF, 03-11-2026 ~16:00 IST. Commands run read-only via ssh. Nothing edited except that long outputs are in separate sections.

######## i5: Q1 (df, lsblk, mount, mdstat, ls)
### hostname
i5-4590-dsm72
### df -h
Filesystem              Size  Used Avail Use% Mounted on
/dev/md0                7.9G  1.7G  6.1G  22% /
devtmpfs                7.7G     0  7.7G   0% /dev
tmpfs                   7.7G  260K  7.7G   1% /dev/shm
tmpfs                   7.7G   20M  7.7G   1% /run
tmpfs                   7.7G     0  7.7G   0% /sys/fs/cgroup
tmpfs                   7.7G   28M  7.7G   1% /tmp
tmpfs                   1.6G     0  1.6G   0% /run/user/108668
tmpfs                   1.6G     0  1.6G   0% /run/user/196791
/dev/loop0               27M  767K   24M   4% /tmp/SynologyAuthService
/dev/mapper/cachedev_1  205G  201G  3.6G  99% /volume2
/dev/mapper/cachedev_0  3.5T  1.5T  2.1T  41% /volume1
/dev/mapper/cachedev_1  205G  201G  3.6G  99% /volume1/@appdata/ContainerManager/all_shares/ssd_backup_gdrive
### lsblk
sh: line 1: lsblk: command not found
lsblk: exit 127
### mount | grep volume
/dev/mapper/cachedev_1 on /volume2 type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=256,subvol=/@syno)
/dev/mapper/cachedev_0 on /volume1 type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=256,subvol=/@syno)
/dev/mapper/cachedev_0 on /volume1/@docker type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=256,subvol=/@syno)
/dev/mapper/cachedev_0 on /volume1/@docker/btrfs type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=256,subvol=/@syno)
/dev/mapper/cachedev_1 on /volume1/@appdata/ContainerManager/all_shares/ssd_backup_gdrive type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=257,subvol=/@syno/ssd_backup_gdrive)
### cat /proc/mdstat
Personalities : [raid1] 
md4 : active raid1 sata2p6[0] sata3p6[1]
      2930246912 blocks super 1.2 [2/2] [UU]
      
md2 : active raid1 sata2p5[2] sata3p5[3]
      966035584 blocks super 1.2 [2/2] [UU]
      
md3 : active raid1 sata1p5[0]
      223704064 blocks super 1.2 [1/1] [U]
      
md1 : active raid1 sata2p2[26](W) sata1p2[28] sata3p2[27](W)
      2096128 blocks super 1.2 [26/3] [UUU_______________________]
      
md0 : active raid1 sata2p1[26](W) sata1p1[28] sata3p1[27](W)
      8387584 blocks super 1.2 [26/3] [UUU_______________________]
      
unused devices: <none>
### ls -ld datapullers dirs
ls: cannot access '/volume2/docker/datapullers': No such file or directory
drwxrwxrwx+ 1 roopeshkumarb users 1058 Nov  3 13:09 /volume1/docker/datapullers
### df of recorder dirs
Filesystem      Size  Used Avail Use% Mounted on
-               3.5T  1.5T  2.1T  41% /volume1/docker
-               3.5T  1.5T  2.1T  41% /volume1/docker
-               3.5T  1.5T  2.1T  41% /volume1/docker
-               3.5T  1.5T  2.1T  41% /volume1/docker

######## i7: Q1
### hostname
I7-3RD-exJ1800
### df -h
Filesystem              Size  Used Avail Use% Mounted on
/dev/md0                7.9G  1.7G  6.1G  21% /
devtmpfs                7.7G     0  7.7G   0% /dev
tmpfs                   7.7G  244K  7.7G   1% /dev/shm
tmpfs                   7.7G   19M  7.7G   1% /run
tmpfs                   7.7G     0  7.7G   0% /sys/fs/cgroup
tmpfs                   7.7G   28M  7.7G   1% /tmp
tmpfs                   1.6G     0  1.6G   0% /run/user/196791
tmpfs                   1.6G     0  1.6G   0% /run/user/108668
/dev/loop0               27M  767K   24M   4% /tmp/SynologyAuthService
/dev/mapper/cachedev_0  419G  141G  279G  34% /volume2
/dev/mapper/cachedev_1  3.5T  2.5T  1.1T  71% /volume1
/dev/mapper/cachedev_0  419G  141G  279G  34% /volume1/@appdata/ContainerManager/all_shares/docker2
### lsblk
sh: line 1: lsblk: command not found
lsblk: exit 127
### mount | grep volume
/dev/mapper/cachedev_0 on /volume2 type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=256,subvol=/@syno)
/dev/mapper/cachedev_1 on /volume1 type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=256,subvol=/@syno)
/dev/mapper/cachedev_1 on /volume1/@docker type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=256,subvol=/@syno)
/dev/mapper/cachedev_1 on /volume1/@docker/btrfs type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=256,subvol=/@syno)
/dev/mapper/cachedev_0 on /volume1/@appdata/ContainerManager/all_shares/docker2 type btrfs (rw,nodev,relatime,ssd,noacl,synoacl,space_cache=v2,metadata_ratio=50,auto_reclaim_space,block_group_cache_tree,syno_allocator,subvolid=257,subvol=/@syno/docker2)
### cat /proc/mdstat
Personalities : [raid1] 
md4 : active raid1 sata3p5[0]
      458124544 blocks super 1.2 [1/1] [U]
      
md3 : active raid1 sata2p6[0] sata1p6[1]
      2930246912 blocks super 1.2 [2/2] [UU]
      
md2 : active raid1 sata2p5[2] sata1p5[3]
      966035584 blocks super 1.2 [2/2] [UU]
      
md1 : active raid1 sata2p2[26](W) sata3p2[28] sata1p2[27](W)
      2096128 blocks super 1.2 [26/3] [UUU_______________________]
      
md0 : active raid1 sata2p1[26](W) sata3p1[28] sata1p1[27](W)
      8387584 blocks super 1.2 [26/3] [UUU_______________________]
      
unused devices: <none>
### ls -ld datapullers dirs
ls: cannot access '/volume2/docker/datapullers': No such file or directory
drwxrwxrwx+ 1 roopeshkumarb users 746 Nov  3 13:09 /volume1/docker/datapullers
### df of recorder dirs
Filesystem      Size  Used Avail Use% Mounted on
-               3.5T  2.5T  1.1T  71% /volume1/docker
-               3.5T  2.5T  1.1T  71% /volume1/docker
-               3.5T  2.5T  1.1T  71% /volume1/docker
-               3.5T  2.5T  1.1T  71% /volume1/docker
```

### FILE audit_031126_BLK002_raw_proof/02_Q2_code_paths.txt  sha256=5a00f367ac1cb56e  bytes=1707
```
pullers/shared/dp_tickrec.py:42:DP_ROOT = os.environ.get("DP_ROOT", "/data")
pullers/shared/dp_tickrec.py:43:BOX = (os.environ.get("BOX_NAME") or "unknown").lower()
pullers/shared/dp_tickrec.py:44:OUT_DIR = os.path.join(DP_ROOT, "ticks", BOX)
pullers/shared/dp_tickrec.py:154:def day_file(d: date | None = None) -> str:
pullers/shared/dp_tickrec.py:161:    return os.path.join(OUT_DIR, "ticks_%s.db" % (d or now().date()).strftime("%Y%m%d"))
pullers/shared/dp_depthrec.py:55:DP_ROOT = os.environ.get("DP_ROOT", "/data")
pullers/shared/dp_depthrec.py:56:BOX = (os.environ.get("BOX_NAME") or "unknown").lower()
pullers/shared/dp_depthrec.py:57:OUT_DIR = os.path.join(DP_ROOT, "depth", BOX)
pullers/shared/dp_depthrec.py:293:    def day_file(self):
pullers/shared/dp_depthrec.py:294:        return os.path.join(OUT_DIR, "depth_%s.db" % now().strftime("%Y%m%d"))
pullers/shared/dp_upstoxrec.py:45:DP_ROOT = os.environ.get("DP_ROOT", "/data")
pullers/shared/dp_upstoxrec.py:46:BOX = (os.environ.get("BOX_NAME") or "unknown").lower()
pullers/shared/dp_upstoxrec.py:47:OUT_DIR = os.path.join(DP_ROOT, "upstox_live", BOX)
pullers/shared/dp_upstoxrec.py:165:    def day_file(self):
pullers/shared/dp_upstoxrec.py:166:        return os.path.join(OUT_DIR, "upstox_%s.db" % now().strftime("%Y%m%d"))
pullers/shared/dp_fyerstbt.py:49:DP_ROOT = os.environ.get("DP_ROOT", "/data")
pullers/shared/dp_fyerstbt.py:50:BOX = (os.environ.get("BOX_NAME") or "unknown").lower()
pullers/shared/dp_fyerstbt.py:51:OUT_DIR = os.path.join(DP_ROOT, "fyers_tbt", BOX)
pullers/shared/dp_fyerstbt.py:214:    def day_file(self):
pullers/shared/dp_fyerstbt.py:215:        return os.path.join(OUT_DIR, "tbt_%s.db" % now().strftime("%Y%m%d"))
```

### FILE audit_031126_BLK002_raw_proof/03_Q3_tables.txt  sha256=781ae7d7f5ae53e6  bytes=833
```
$ sqlite3 -readonly /volume1/docker/datapullers/depth/i5/depth_20261103.db .tables     -> events frames instruments
$ sqlite3 -readonly /volume1/docker/datapullers/upstox_live/i5/upstox_20261103.db .tables -> events frames instruments
$ sqlite3 -readonly /volume1/docker/datapullers/depth/j1800/depth_20261103.db .tables  -> events frames instruments
$ sqlite3 -readonly /volume1/docker/datapullers/upstox_live/j1800/upstox_20261103.db .tables -> events frames instruments
python3 sqlite_master (read-only):  ticks_20261103.db -> instruments_today session_log ticks   (both boxes)
                                    tbt_20261103.db   -> events frames instruments texts       (both boxes)
Rotational flags: i5 sata1 SSD(CT240BX500SSD1) rot=0; sata2,sata3 ST4000NM000B rot=1.  i7 sata1,sata2 ST4000NM000B rot=1; sata3 SATA SSD rot=0.
```

### FILE audit_031126_BLK002_raw_proof/04_h12_puller_dbs_and_volume2_raw.txt  sha256=e0867df1b182a10c  bytes=3018
```
H12 CHECK ON PULLER/ENGINE DATABASES, i5, 03-11-2026 ~21:00 IST (read-only). Requested by the auditor (V-002).

ROUTE: i5-cf
### /volume1/docker/blpro009/data/blpro_working.db
249856 03-11-2026 21:00 
$ sqlite3 -readonly /volume1/docker/blpro009/data/blpro_working.db ".tables" | grep -iE 'chain|depth|tick|tbt|quote'

total tables: 1
### /volume1/docker/blpro_data/009/app/blpro_working.db
35 20-10-2026 02:33 ->
8662638592 20-10-2026 02:00 
32768 20-10-2026 02:32 
8816832 20-10-2026 02:32 
2339078144 11-09-2026 17:48 
32768 16-09-2026 22:01 
0 16-09-2026 21:45 
$ sqlite3 -readonly /volume1/docker/blpro_data/009/app/blpro_working.db ".tables" | grep -iE 'chain|depth|tick|tbt|quote'
broker_chain_snap broker_quote_depth_snap depth_1m depth_top_1m equity_depth_1m opt_chain_1m opt_chain_1m_replaced opt_depth_1m options_chain_summary quarantine__options_chain_summary tick_minute_1m 
total tables: 124
### /volume2/blpro_hot/blpro_working.db
9181708288 03-11-2026 19:08 
32768 03-11-2026 21:01 
6089392 03-11-2026 21:01 
$ sqlite3 -readonly /volume2/blpro_hot/blpro_working.db ".tables" | grep -iE 'chain|depth|tick|tbt|quote'
broker_chain_snap broker_quote_depth_snap depth_1m depth_top_1m equity_depth_1m opt_chain_1m opt_chain_1m_replaced opt_depth_1m options_chain_summary quarantine__options_chain_summary tick_minute_1m 
total tables: 124
### df -h /volume1 /volume2
Filesystem              Size  Used Avail Use% Mounted on
/dev/mapper/cachedev_0  3.5T  1.5T  2.1T  41% /volume1
/dev/mapper/cachedev_1  205G  202G  3.3G  99% /volume2

### columns, size, rows of the two H12 candidates in /volume2/blpro_hot/blpro_working.db
ROUTE: i5-cf
### broker_chain_snap columns:
ts,src,expiry,strike,spot,ce_ltp,ce_oi,ce_prev_oi,ce_vol,ce_iv,ce_delta,ce_gamma,ce_theta,ce_vega,ce_bid,ce_ask,pe_ltp,pe_oi,pe_prev_oi,pe_vol,pe_iv,pe_delta,pe_gamma,pe_theta,pe_vega,pe_bid,pe_ask,src_store,copied_at
### broker_chain_snap approx size (dbstat bytes):
20172800
### broker_chain_snap count(*):
73144
### broker_quote_depth_snap columns:
ts,src,instrument_key,symbol,ltp,volume,oi,total_buy_qty,total_sell_qty,bid1,bid1_qty,ask1,ask1_qty,bid_qty5,ask_qty5,exch_ts,src_store,copied_at
### broker_quote_depth_snap approx size (dbstat bytes):
4464640
### broker_quote_depth_snap count(*):
23037

### du of /volume2 (i5)
ROUTE: i5-cf
173324	datapullers
8763	blpro_hot
1	ssd_backup_gdrive
1	@eaDir
0	@tmp
---
root /volume2/@eaDir
root /volume2/@tmp
root /volume2/blpro_hot
root /volume2/datapullers
root /volume2/ssd_backup_gdrive
--- docker root
ROUTE: i5-cf
81379	upstox
49228	fyers
29708	dhan
10251	nse
2760	kite
--- big files
71.021 GB 03-11 21:01 ./upstox/pullerfull_upstox_151026-0031.db
41.6305 GB 03-11 21:00 ./fyers/pullerfull_fyers_151026-0030.db
26.3393 GB 03-11 21:01 ./dhan/pullerfull_dhan_151026-0031.db
9.15853 GB 15-10 00:42 ./nse/nse_121026-1534.db
7.13031 GB 03-11 21:01 ./upstox/puller930_upstox_151026-0033.db
5.63263 GB 15-10 03:26 ./fyers/fyers_121026-1534.db
2.6683 GB 14-10 16:51 ./dhan/dhan_121026-1533.db
```

### FILE audit_031126_BLK001_livewatch/17_access_routes_raw.txt  sha256=766c0a94e0f6fd5d  bytes=728
```
ACCESS ROUTE RAW TESTS, 03-11-2026 16:07 IST, from the cloud sandbox via tools/box_reach.sh (file 11). Hostnames are aliases.

### box_reach.sh i5 'hostname'
ROUTE: i5-cf
i5-4590-dsm72

### box_reach.sh i7 'hostname'
route j1800-cf failed (rc=255: Bad Gateway Connection closed by UNKNOWN port 65535 )
ROUTE: i5-cf>i7
I7-3RD-exJ1800

### box_reach.sh pi 'hostname'
ROUTE: pi-cf
a0d7b954-ssh

### LAN hops (each line: from -> to : result)
pi -> 192.168.2.91 (user roopeshkumarb): i5-4590-dsm72
pi -> 192.168.2.100 (user roopeshkumarb): I7-3RD-exJ1800
i5 -> i7: I7-3RD-exJ1800
i5 -> pi (root): a0d7b954-ssh
i7 -> i5: i5-4590-dsm72
i7 -> pi (root): a0d7b954-ssh

### direct alias tests
j1800-cf: Bad Gateway
sshpi-cf: Bad Gateway
```

### FILE audit_031126_BLK001_livewatch/12_ACCESS_ROUTES.md  sha256=c85428932fd19ffa  bytes=4998
```
# ACCESS ROUTES: reach every box with no single point of failure (prepared 03-11-2026 ~13:55 IST; owner leaves for offshore on 05-11)
Hostnames are shown as aliases only (i5-cf, j1800-cf, pi-cf, sshpi-cf). No tokens or keys are in this file.

## 1. MEASURED today (not assumed)
| Route | Result 03-11 ~13:40 | Evidence |
|---|---|---|
| Cloudflare SSH to i5 (`i5-cf`) | WORKS | `box_reach.sh i5` -> `ROUTE: i5-cf`, host i5-4590-dsm72 |
| Cloudflare SSH to Pi (`pi-cf`) | WORKS | host a0d7b954-ssh, up 2 d 22 h |
| Cloudflare SSH to i7 (`j1800-cf`) | **FAILS: Bad Gateway** | every attempt today (also earlier in the session) |
| Cloudflare SSH to Pi, 2nd name (`sshpi-cf`) | **FAILS: Bad Gateway** | same |
| LAN hop i5 -> i7 and i7 -> i5 | WORKS | both directions tested |
| LAN hop Pi -> i5 and Pi -> i7 (user roopeshkumarb) | WORKS | tested |
| LAN hop i5 -> Pi and i7 -> Pi (user root) | WORKS | tested |
| Direct from the cloud sandbox to a LAN address (192.168.2.x) | impossible | timed out |
So today: i5 has 3 routes (own tunnel, via Pi, via i7); i7 has 2 (via i5, via Pi) and **no direct Cloudflare route**; the Pi has 1 (`pi-cf`). Every route to the i7 passes through a box other than the i7 itself. If the i5 tunnel and the Pi tunnel both drop, the i7 is unreachable from offshore.
Facts about the connector: the i5 runs cloudflared as a DSM package (process started 12:45, i.e. it came back by itself after the reboot); it uses a remotely-managed tunnel token, so the hostname -> service mapping lives in the Cloudflare dashboard, which this session cannot read. The i7 has no cloudflared package or container (`/var/packages` shows only CloudSync; its `docker ps` has no cloudflared). Which connector serves `pi-cf`: UNKNOWN. Why `j1800-cf` and `sshpi-cf` return Bad Gateway: UNKNOWN (needs the dashboard).

## 2. WHICH DIRECTION WE ARE GOING (recommendation)
1. **Primary: Cloudflare Tunnel with THREE connectors** (i5 existing, i7 new, Pi new), all running the same tunnel, each hostname routed to its box's LAN address. Any one connector alive serves every hostname.
2. **Secondary: LAN hop** through any live box (already works; `tools/box_reach.sh` tries every route in order and prints which answered).
3. **Third, independent of Cloudflare: a second overlay (Tailscale) on the Pi only** (optional, needs the owner's account). Protects against a Cloudflare outage or an Access-policy mistake.
4. **Power, the real single point of failure:** both NAS boxes lost power together twice today; a UPS (NAS x2 + router + modem) and the DSM boot-up task are the first fixes. The boxes DID power back on by themselves (evidence: two unattended reboots), so "restart after power failure" is already effective. The router/modem on the same circuit is not yet verified.
Do not touch the existing cloudflared on the i5 or portainer: it is the owner's only way in.

## 3. SEQUENCE (do in this order; each step has a test)
| # | Step | Who | Test (pass = ...) |
|---|---|---|---|
| 1 | Verify LAN mesh in all 6 directions | Claude | DONE 03-11: 6/6 |
| 2 | `box_reach.sh` tries every route; keep ~/.ssh/config aliases in the repo template | Claude | DONE: i5, pi answer direct; i7 answers via `i5-cf>i7` |
| 3 | Show what `sshj1800` and `sshpi` point at in Zero Trust > Networks > Tunnels > (the tunnel of `sshi5`) > Public hostnames. Fix: `sshj1800` -> `ssh://192.168.2.100:22`, `sshpi` -> `ssh://192.168.2.130:22` | Owner in the dashboard (~5 min), OR owner authorises the Cloudflare connector in claude.ai settings and Claude does it | `box_reach.sh i7` prints `ROUTE: j1800-cf` |
| 4 | Add replica connectors: cloudflared on the i7 (Docker container, `restart: unless-stopped`) and on the Pi, using the same tunnel token. Claude reads the token on the box and never prints it | Claude, after step 3 and the owner's OK | dashboard shows 3 connectors healthy; `box_reach.sh i7` still passes |
| 5 | Put `boot_start_containers.sh` in DSM Task Scheduler (Triggered Task, Boot-up, root) on both boxes; add the cloudflared replica container to its start list | Owner (DSM admin login) | pull the box's network or reboot at a quiet time; recorders return without a human |
| 6 | Offshore rehearsal from a phone hotspot (NOT the home LAN) on the owner's laptop: install the cloudflared client, log in through Access, `ssh` to each alias | Owner, with Claude watching `box_reach.sh` | all three aliases answer from outside the LAN |
| 7 | Failure drill: stop the replica on ONE box (never the i5 package) and confirm the others still serve | Claude, at a quiet time | hostname still answers |
| 8 | UPS for NAS x2 + router + modem; second internet (4G failover) for the router | Owner | box rides through a 5-minute mains cut |
Target date: steps 3-6 before 05-11.

## 4. What this does NOT protect against
Total site power or internet loss with no UPS/4G; loss of the owner's Cloudflare account; an Access-policy change that locks everyone out. NOT TESTED: any offshore login from outside the LAN.
```

### FILE audit_031126_BLK001_livewatch/10_boot_start_containers.sh  sha256=d5cc181f41426e31  bytes=1413
```
#!/bin/sh
# boot_start_containers.sh - start the live recorders and the stack after a NAS reboot/power loss.
# WHY: on 03-11-2026 ~12:08 IST a power event took both boxes down; "restart: unless-stopped" did NOT bring
# the containers back, and live-only data was lost until a human started them. No UPS.
# INSTALL (Kumar, DSM admin, once per box): Control Panel > Task Scheduler > Create > Triggered Task >
#   User-defined script > User: root > Event: Boot-up > Task settings > Run command:
#   sh /volume1/docker/datapullers/boot_start_containers.sh >> /volume1/docker/datapullers/_state/boot_start.log 2>&1
# Safe: `docker start` on a running container is a no-op. Never touches cloudflared/portainer.
D=/var/packages/ContainerManager/target/usr/bin/docker
log(){ echo "$(date '+%d-%m-%Y %H:%M:%S') [boot_start] $*"; }
# wait for Docker (up to 10 min)
i=0; until $D info >/dev/null 2>&1; do i=$((i+1)); [ $i -gt 60 ] && { log "docker not ready after 10 min"; exit 1; }; sleep 10; done
sleep 30   # let network/mounts settle
# order matters: logins/lease first, then live-only recorders (non-recoverable), then pullers and helpers
for c in broker_login pull_lease_ctl tickrec depthrec upstoxrec fyerstbt dp_guard fullpuller puller930 dp_voter dbtools; do
  if $D inspect "$c" >/dev/null 2>&1; then
    $D start "$c" >/dev/null 2>&1 && log "started/ok $c" || log "FAILED $c"
  else
    log "absent $c"
  fi
done
```

### FILE audit_031126_BLK001_livewatch/11_box_reach.sh  sha256=5bc4701599218490  bytes=2086
```
#!/bin/bash
# box_reach.sh - run a command on a box, trying EVERY route in order so no single path is a single point of failure.
#   usage: box_reach.sh <i5|i7|pi> '<shell command>'
# Routes (Cloudflare SSH aliases come from ~/.ssh/config; LAN hops use the key already on the hop box):
#   i5: 1 i5-cf (direct)            2 pi-cf -> roopeshkumarb@192.168.2.91   3 i7 route -> i5
#   i7: 1 j1800-cf (direct, needs its own connector - see ACCESS_ROUTES) 2 i5-cf -> i7  3 pi-cf -> i7
#   pi: 1 pi-cf (direct sshha)      2 sshpi-cf (alias)                      3 i5-cf -> pi
# Prints "ROUTE: <name>" on stderr for the route that answered. Exit 99 if all fail. Read the command's own exit code otherwise.
BOX="$1"; CMD="$2"; [ -n "$BOX" ] && [ -n "$CMD" ] || { echo "usage: $0 <i5|i7|pi> '<cmd>'" >&2; exit 2; }
RUN="sh -s"   # the command travels on stdin, so nested hops need no quoting
O="-o BatchMode=yes -o ConnectTimeout=25 -o ServerAliveInterval=10"
LAN="ssh -o BatchMode=yes -o ConnectTimeout=10"
T=${REACH_TIMEOUT:-150}
try(){ name="$1"; shift; out=$(printf '%s\n' "$CMD" | timeout $T "$@" 2>/tmp/reach_err.$$); rc=$?
  if [ $rc -ne 255 ] && [ $rc -ne 124 ] && ! grep -qE "Bad Gateway|bad handshake|Connection closed by UNKNOWN|Permission denied" /tmp/reach_err.$$; then
     echo "ROUTE: $name" >&2; printf '%s\n' "$out"; rm -f /tmp/reach_err.$$; exit $rc; fi
  echo "route $name failed (rc=$rc: $(head -c 100 /tmp/reach_err.$$ | tr '\n' ' '))" >&2; }
case "$BOX" in
 i5) try i5-cf        ssh $O i5-cf "$RUN"
     try "pi-cf>i5"     ssh $O pi-cf "$LAN roopeshkumarb@192.168.2.91 '$RUN'"
     try "i5-cf>i7>i5"  ssh $O i5-cf "$LAN 192.168.2.100 \"$LAN 192.168.2.91 '$RUN'\"" ;;
 i7) try j1800-cf     ssh $O j1800-cf "$RUN"
     try "i5-cf>i7"     ssh $O i5-cf "$LAN 192.168.2.100 '$RUN'"
     try "pi-cf>i7"     ssh $O pi-cf "$LAN roopeshkumarb@192.168.2.100 '$RUN'" ;;
 pi) try pi-cf        ssh $O pi-cf "$RUN"
     try sshpi-cf     ssh $O sshpi-cf "$RUN"
     try "i5-cf>pi"     ssh $O i5-cf "$LAN root@192.168.2.130 '$RUN'" ;;
esac
echo "ALL ROUTES FAILED for $BOX" >&2; exit 99
```
