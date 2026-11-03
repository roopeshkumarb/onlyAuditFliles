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

# LATEST: open for verification (updated 04-11-2026 ~00:55 IST; newest first)
SECOND FABLE REVIEW stored: AUDITOR_RESPONSES/20261103_FABLE_NIGHT_REREVIEW_CONDENSED.md (found and fixed a silent defect: 0 constituents would have been recorded). Please verify fixes N-1..N-4 against it.
OWNER RULE: every outside-auditor verdict is verified with Fable. Fable's audit of tonight's changes: AUDITOR_RESPONSES/20261103_FABLE_NIGHT_AUDIT_CONDENSED.md. README.md inlines the evidence.

## ROUND 4 (night 03-11): weekly expiry + extra live-only instruments + SSD move incident + data-needed list
### N-1 | weekly expiry recording (Dhan d20, Upstox) | DEPLOYED-NOT-YET-SEEN (first live proof 04-11 09:15)
Evidence: NIGHT/05,06,07 code+tests, 08 compose diff, 09 test output, 10 deploy raw. Fable audit fixed: monthly-expiry-week window swap (A1), Upstox 6->5 (A2). Still open: no holiday calendar in depth/upstox in_session; Fyers TBT weekly (B9).
Auditor questions: (a) is splitting the 50 slots (26 weekly + 22 monthly on Dhan) the right trade for an intraday regime/direction edge? (b) what must the 04-11 proof show (instrument counts, expiry_weekly=2026-11-10, no baseline loss)?
### N-2 | Kite extras: indices, NIFTYBEES, BANKNIFTY future, all 50 constituents (macro CDS/MCX OFF) | DEPLOYED-NOT-YET-SEEN
Evidence: NIGHT/02,03. Open: volume growth unmeasured; run_session untested; macro enable plan.
### N-3 | INCIDENT: SSD to HDD move | RESOLVED for data, OPEN for design
Evidence: NIGHT/11 raw + 04 script v3 (copy-only). Two epoch-pointer files were moved and restored (sha256). Fable verdict on the script: NOT SAFE (C1-C4) -> v3 guards; removal disabled by default. Nothing on the i5 SSD is safely movable without changing the old pullers' mounts. Question: is the plan (mount the HDD overflow path into the containers, or replace the old pullers) acceptable, and what must be proven first?
### N-4 | DATA NEEDED FOR EDGE list | AWAITING AUDITOR
Evidence: NIGHT/01 (corrected by Fable D1-D5). Questions: (a) are groups G1-G14 sufficient for an intraday regime/direction engine under the no-GEX/no-signed-flow limits? (b) which of B1-B12 would you build first? (c) any feed of the same kind as the weekly miss that is still not listed?

## ROUND 3: v3.1 dry run (decision: dry run only, no kills)
### V-001 v3.1 | livewatch --dry-run on both boxes | status: RUNNING from 22:16 IST; first in-session cycle 09:00 tomorrow
Evidence (inlined): 02 code v3.1, 03 tests (25), 27 diff v3->v3.1, 28 tests, 29 mutations, 30 preflight on real files, 31 gap-histogram tool. Fable's dry-run spec was adopted: CSV with action/query_ms/restart_count/events_max per recorder per cycle; every DEAD/CONN_DEAD verdict kept every cycle; conn scan bounded; --session-start 09:00.
Auditor decisions requested: (a) is the multi-day histogram taken from the DAY FILES (tool 31; results will be added to this page) acceptable instead of the livewatch log? (b) after 3 sessions, what evidence moves C-005 to PROVEN, per recorder?
Open: -shm readability in session; tickrec uses status last_tick + mtime only; dry-run writes small files under _state/livewatch_dry; dp_watchdog overlap; the daemon dies on reboot until the DSM boot task is installed.
### V-002 | the outside auditor's V-002 verdict was found UNSUPPORTED by Fable (rows 15-17, 21): recoverability of the snapshot tables is unproven; BLK-002 code "not required" is NOT established. Owner rule needed: are the 14-19 Oct chain/quote-depth snapshots live-only (non-recoverable)?
### V-003 | remote access | UPDATED: sshi7 direct route works (34); remaining: independence of the routes from one tunnel (UNKNOWN), DSM boot task (owner), second overlay

## ROUND 2 (after the outside auditor's verdict and the Fable review)
### V-001 v3 | livewatch (code: 02_livewatch.py; history 02a v1, 02b v2) | status: AWAITING AUDITOR (not deployed)
New evidence (inlined): 26 diff v2->v3, 20 tests (22 pass), 25 mutations (7 caught), 18/19 raw d20 gaps, 23 diff v1->v2.
Changes answering the two reviews: fail-closed on missing folders; IST computed from epoch; kill bound per IST day with hourly re-armed ESCALATE; freshness judged by frames.recv_ts for depth (per connection), upstox and tbt; multi-socket death = ALARM ONLY by default; state dir off /tmp; docker-start fallback now tested.
Still OPEN (do not mark verified): tickrec freshness still mtime/last_tick; 09:16 first-pass kill risk; d20 never connecting = UNKNOWN; -shm readability as the daemon user; dp_watchdog vs livewatch overlap; name clash with the compose container livewatch; no dry-run sessions yet; 90 s comes from ONE day of data.
Question to the auditor: is v3 enough to start THREE DRY-RUN sessions (no kills, every DEAD/UNKNOWN line kept), and what must the dry run record?
### V-002 v2 | BLK-002 | status: AWAITING AUDITOR
New: BLK002/05 (negative test of the auditor's path, symlink resolution, src_store group-by, puller-DB table search, TZ/uid, byte-level df). C-020 and C-021 updated; C-021's '~3 days' is RETRACTED.
### V-003 | access | status: NOT VERIFIED; 12 corrected (i5 has 2 independent routes, not 3). Owner steps pending.

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
C-020,03-11-2026,broker_chain_snap (73144 rows) and broker_quote_depth_snap (23037 rows) exist in the live SSD engine DB /volume2/blpro_hot/blpro_working.db,PROVEN (existence+counts),audit_031126_BLK002_raw_proof/04 + 05,rows are COPIES (src_store/copied_at) of puller-DB snapshots dated 14-19 Oct copied 17-19 Oct; /volume1/.../009/app/blpro_working.db is a symlink to the same SSD file; origin tables in the puller DBs UNKNOWN (no chain|depth|quote table name there); H12 relevance UNPROVEN
C-021,03-11-2026,/volume2 on i5 is 216063025152 bytes used of 219529871360 (3466846208 free) at 21:39; /volume2/datapullers is ~173 GB (MB units),PROVEN (figures),audit_031126_BLK002_raw_proof/04_h12_puller_dbs_and_volume2_raw.txt + 05_evidence_batch2_i5_i7.txt,RETRACTED: the '~3 days to full' estimate (df -h 1 GB resolution; no rate derivable). Rate UNMEASURED; 2nd byte reading pending (T-1312)
C-022,03-11-2026,path /volume1/docker/blpro_data/blpro_working.db does not exist,PROVEN,audit_031126_BLK002_raw_proof/05_evidence_batch2_i5_i7.txt,ls: cannot access ... No such file or directory
C-023,03-11-2026,livewatch v3 passes 22 tests; 7 new mutations each caught,PROVEN (synthetic fixtures),audit_031126_BLK001_livewatch/20_unit_tests_v3_output.txt + 25_mutations_v3.txt + 26_livewatch_v2_to_v3.diff,not deployed; not run against production; daemon user -shm readability NOT TESTED
C-024,03-11-2026,v3 refuses to run when a recorder folder is missing for --box (fail closed),PROVEN (tests),audit_031126_BLK001_livewatch/25_mutations_v3.txt,answers Fable defect 1
C-025,03-11-2026,host TZ of both boxes is IST (/etc/TZ IST-5:30; /etc/localtime Asia/Calcutta); daemon uid roopeshkumarb in users administrators docker,PROVEN,audit_031126_BLK002_raw_proof/05_evidence_batch2_i5_i7.txt,i7 has no cloudflared package (only CloudSync)
C-026,03-11-2026,numbers quoted from terminal sessions with NO raw file in repo (4 s max write gap in a 150 s sample; box uptimes 7-9 min; status.json SILENT quotes; file ages 358-378 s at 15:41; load 25-29; cloudflared start 12:45),EVIDENCE NOT IN REPO,,answer CANNOT CHECK; re-run on request
C-027,03-11-2026,'i5 has 3 independent remote routes' (first version of 12_ACCESS_ROUTES),RETRACTED,audit_031126_BLK001_livewatch/12_ACCESS_ROUTES.md,third route passes through i5-cf; independent routes: i5 2, i7 2 (neither its own), Pi 1
C-028,03-11-2026,the outside auditor's round-2 verdict is a reliable independent check,FALSE per Fable verification,AUDITOR_RESPONSES/20261103_FABLE_VERIFICATION_of_QWEN_round2.md,9 of 29 statements incorrect or unsupported; owner rule: every outside audit is verified with Fable
C-029,03-11-2026,broker_chain_snap / broker_quote_depth_snap are recoverable (so SSD placement is fine),UNPROVEN (asserted by the outside auditor only),,owner's H12 table says chain snapshots are non-recoverable/HDD; needs the owner's rule on 14-19 Oct snapshots
C-030,03-11-2026,livewatch v3.1 bounded conn scan runs in 74-310 ms on the real closed depth/upstox/tbt day files of both boxes,PROVEN (closed files; load ~12),audit_031126_BLK001_livewatch/30_preflight_v3.1_real_files.txt,in-session timing and -shm readability NOT TESTED
C-031,03-11-2026,v3.1 dry run logs every verdict every cycle (no suppression) and a CSV with action/query_ms/restart_count/events_max,PROVEN (25 tests; 3 mutations caught),audit_031126_BLK001_livewatch/28_unit_tests_v3.1_output.txt + 29_mutations_v3.1.txt,first real in-session rows tomorrow 09:00
C-032,03-11-2026,dry-run daemons (--dry-run --session-start 09:00 --session-end 15:40 --stale-s 90) are running on i5 and i7 from 22:16 IST,PROVEN at start (/proc ALIVE + log lines),audit_031126_BLK001_livewatch/30_preflight_v3.1_real_files.txt,dies on reboot (boot task not installed); no kills possible in --dry-run
C-033,03-11-2026,multi-day gap histogram from the day files supports a 90 s limit,PARTLY PROVEN (i7 complete; i5 still running),audit_031126_BLK001_livewatch/33_gap_histogram_i7.csv + 32_gap_histogram_i5_PARTIAL.csv,across ~10 normal days the longest gap was ticks 1-11 s; depth d20/d200 2-25 s; upstox 2-7 s; gaps >60 s occur only on days with a known failure (20-10 recorder nearly empty: ticks 33 rows, upstox 282 rows, fyers 52 rows; 29-10, 30-10 (about 1830 s), 02-11, 03-11); tickrec: ticks use the NIFTY token only; fyers_tbt has only 4 days; 15-10..03-11 only, so seasonality/expiry-day behaviour UNKNOWN
C-034,03-11-2026,weekly NIFTY options are recorded on Dhan d20 and Upstox from the 04-11 session,DEPLOYED-NOT-YET-SEEN,audit_031126_NIGHT_weekly_extras_move/10_weekly_deploy_raw.txt + 09_unit_tests_output.txt,env confirmed inside containers; Fable audit fixed the monthly-week bug (A1) and set Upstox to the tested 5/5; first live proof = 04-11 09:15 check
C-035,03-11-2026,Kite socket records indices/ETF/BANKNIFTY future + all 50 constituents (TICK_EXTRA=1 EQ=50; macro CDS/MCX off),DEPLOYED-NOT-YET-SEEN,audit_031126_NIGHT_weekly_extras_move/02_dp_tickrec_extra.py + 03 tests,8 tests; volume growth UNMEASURED; run_session not unit tested
C-036,03-11-2026,inactive SSD files were moved to the HDD,FALSE / INCIDENT,audit_031126_NIGHT_weekly_extras_move/11_incident_ssd_move_raw.txt,v1 script moved two epoch-pointer targets (links dangled minutes; restored sha256-verified); with guards nothing on the i5 SSD is safely movable; script v3 is copy-only by default
C-037,03-11-2026,the 'why weekly expiry was not covered' section is accurate,CORRECTED after Fable,audit_031126_NIGHT_weekly_extras_move/01_DATA_NEEDED_FOR_EDGE_031126.md,weekly was on record as a feature need on 15-10 (ALGOTEST_FEATURES_DATA); four recorders not three; Fyers TBT weekly still missing
C-038,03-11-2026,4 verified HDD copies under /volume1/docker/datapullers_ssd_overflow are trustworthy,UNPROVEN,audit_031126_NIGHT_weekly_extras_move/11_incident_ssd_move_raw.txt,sha256 matched source at copy time; integrity_check and orphan -wal check not run
C-039,04-11-2026,the 50-constituent list reaches the container and is read (50 names; TICK_EXTRA True; macro False) on i5 and i7,PROVEN inside the containers,audit_031126_NIGHT_weekly_extras_move/10_weekly_deploy_raw.txt,found by the 2nd Fable review (entrypoint bug); live recording of the constituents is NOT yet seen
C-040,04-11-2026,weekly windows never exceed the caps and never double-subscribe on any date incl. the monthly-expiry week,PROVEN by simulation (Fable) + tests,AUDITOR_RESPONSES/20261103_FABLE_NIGHT_REREVIEW_CONDENSED.md,Dhan 48 slots / Upstox 47 keys; the November monthly is 23-11; holiday handling (24-11) OPEN
C-041,04-11-2026,tick volume growth from the extras is small (+20-60%),RETRACTED,audit_031126_NIGHT_weekly_extras_move/01_DATA_NEEDED_FOR_EDGE_031126.md,Fable now estimates +70-200% (1.5-5M rows); unmeasured; tickrec has no free-space guard
C-042,04-11-2026,the i7 has a direct Cloudflare SSH route (sshi7),PROVEN,audit_031126_BLK001_livewatch/34_direct_cf_routes_tested.txt,C-015 (i7 Bad Gateway) concerned the old hostname sshj1800 only; sshi5, sshi7 and sshha all answered at 23:59 IST; independence of sshi7 from the i5 tunnel UNKNOWN
C-043,04-11-2026,the Pi restarted about 18:50 IST on 03-11,PROVEN (uptime 5:07 at 23:59 vs 2 d 22 h at 13:40),audit_031126_BLK001_livewatch/34_direct_cf_routes_tested.txt,cause UNKNOWN; relevant to C-008 (the Pi was the proof that the NAS outage was not network-wide)
C-044,04-11-2026,the old hostnames sshj1800 and sshpi no longer exist (no HTTP response); sshha, sshi5, sshi7 answer with the Cloudflare Access login redirect,PROVEN,audit_031126_BLK001_livewatch/34_direct_cf_routes_tested.txt,so the earlier 'Bad Gateway' (C-015) was a stale hostname, not a broken connector; offshore login from a laptop NOT TESTED
C-045,04-11-2026,containers restart after a power cut without a DSM task,CONFIGURED NOT PROVEN,audit_031126_BLK001_livewatch/35_restart_policy_always.txt,'unless-stopped' did not bring recorders back after the 03-11 power losses (they exited with code 0/137/143 and stayed down: consistent with Synology stopping containers at shutdown = a manual stop); 'always' restarts regardless per Docker documentation; applied with docker update on 10 containers per box and in the compose; behaviour on these boxes only provable by a reboot
C-046,04-11-2026,the whole home LAN can be reached through Cloudflare Access with ssh -D / -L from a device with cloudflared,PROVEN from the cloud sandbox (outside the LAN) via the Pi only,audit_031126_BLK001_livewatch/36_home_connect_tested.txt,SOCKS via the Pi reached i5/i7/Pi ssh banners and Home Assistant (HTTP 200); local forwards to DSM i5 and i7 returned HTTP 200; via the i5 and i7 forwarding is REFUSED (Synology sshd: administratively prohibited); from the owner's own laptop on the hotspot NOT TESTED; not usable on a company-managed laptop (policy/XDR)
```

---

# CHANGELOG (newest first; corrections are marked CORRECTION)
- 04-11-2026 01:15 IST: tools/home_connect.sh (SOCKS + forwards to the whole LAN, Pi as jump host) tested from outside the LAN; i5/i7 forbid forwarding. C-046.
- 04-11-2026 00:30 IST: restart policy 'always' on the recording stack (both boxes + compose) as the fix for 'recorders stay down after a power cut' without needing the DSM login; C-045 CONFIGURED NOT PROVEN.
- 04-11-2026 00:12 IST: owner gave the three URLs; HTTPS check: sshha, sshi5, sshi7 live behind Access; sshj1800 and sshpi do not exist (C-015's Bad Gateway was a stale hostname). C-044.
- 04-11-2026 00:05 IST: direct Cloudflare routes tested: sshi5, sshi7 (NEW, fixes the i7 gap), sshha all work. CORRECTION to C-015/V-003: only the old hostname sshj1800 was dead. The Pi restarted ~18:50 IST (C-043). C-042, C-043.
- 04-11-2026 00:50 IST: 2nd Fable review: A/B/C/D verdicts stored; NEW DEFECT found and fixed (tickrec container did not receive nifty50_syms.txt: 0 constituents would have been recorded), proven inside both containers; df-unreadable hole in the move script fixed; corrections: November monthly is 23-11; C-041 volume estimate RETRACTED. C-039..C-041.
- 04-11-2026 00:20 IST: multi-day gap histogram from the day files added (i7 complete, i5 partial): healthy-day max gaps 1-25 s, >60 s only on known-failure days; supports the 90 s limit for file-level freshness (C-033 partly proven).
- 04-11-2026 00:10 IST: owner order 'add weekly expiry and the missing live-only recorders': weekly deployed (Dhan 6/5, Upstox 5/5), Kite extras (indices, ETF, BANKNIFTY fut, 50 constituents; macro off), DATA_NEEDED_FOR_EDGE list; Fable audit found 14 defects, fixed A1,A2,B1,B2,C (script copy-only),D; INCIDENT: SSD move script v1 moved two epoch-pointer files (restored). C-034..C-038. Corrections: weekly was on record on 15-10; four recorders not three.
- 03-11-2026 22:30 IST: outside auditor round 2 stored; Fable verification of it stored (9 of 29 statements incorrect/unsupported); livewatch v3.1 (dry-run keeps every verdict, CSV log, bounded conn scan, never-connected conn = CONN_DEAD); dry-run daemons started on both boxes 22:16; gap-histogram tool added; C-028..C-033.
- 03-11-2026 21:55 IST: independent Fable review + comparison with outside auditor stored (AUDITOR_RESPONSES/). livewatch v3 (22 tests, fail-closed, IST-explicit, per-day bound, frames-based freshness, alarm-only for multi-socket death, state dir off /tmp). CORRECTIONS: C-021 '~3 days' RETRACTED; C-027 'i5 has 3 routes' RETRACTED; C-022 now PROVEN; INDEX md5s were stale (regenerated). New files 02b, 20(v3), 25, 26, BLK002/05.
- 03-11-2026 21:20 IST: auditor 1 response stored; README now inlines all evidence; livewatch v2 (90 s + per-connection) written, NOT deployed; new files 18-24 and BLK002/04; C-005, C-009 updated, C-019..C-022 added; /volume2 99% full registered (T-1312).
- 03-11-2026 16:20 IST: added README (fixed entry point), AUDITOR_PROTOCOL, LATEST, CLAIMS_LEDGER, MANIFEST/SHA256SUMS, AUDITOR_RESPONSES template, 17_access_routes_raw.txt.
- 03-11-2026 16:10 IST: CORRECTION to 13_ADDENDUM: Dhan d20 gaps were hidden because the gap script merged d20 and d200 frames. Claim C-006 RETRACTED. livewatch consequence added.
- 03-11-2026 15:55 IST: added BLK-002 step 1 raw proof (no code written).


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

### FILE audit_031126_BLK002_raw_proof/05_evidence_batch2_i5_i7.txt  sha256=e97f08684dcee011  bytes=2590
```
BLK-002 / V-001 EVIDENCE BATCH 2, 03-11-2026 21:39 IST, read-only, requested by both auditors. Hostnames/aliases only.

ROUTE: i5-cf
### run 03-11-2026 21:39:33 on i5-4590-dsm72; TZ files:
Tue Nov  3 21:39:33 IST 2026
IST-5:30
lrwxrwxrwx 1 root root 33 Nov 19  2025 /etc/localtime -> /usr/share/zoneinfo/Asia/Calcutta
uid=1026(roopeshkumarb) gid=100(users) groups=100(users),101(administrators),65536(docker)
### negative test + symlink
ls: cannot access '/volume1/docker/blpro_data/blpro_working.db': No such file or directory
/volume2/blpro_hot/blpro_working.db
### df -B1 /volume2 (bytes)
/dev/mapper/cachedev_1 219529871360 216063025152 3466846208  99% /volume2
### src_store group-by, LIVE SSD copy
-- broker_chain_snap
puller930_upstox_151026-0033.db|15416|2026-10-19 09:15:00|2026-10-19 15:30:00|2026-10-19 22:12:14|2026-10-19 22:12:14
pullerfull_dhan_151026-0031.db|25666|2026-10-16 09:57:00|2026-10-19 15:30:00|2026-10-17 21:18:35|2026-10-19 22:12:14
pullerfull_upstox_151026-0031.db|24354|2026-10-15 09:15:00|2026-10-16 15:30:00|2026-10-17 21:18:35|2026-10-17 21:18:35
upstox_121026-1533.db|7708|2026-10-14 11:34:00|2026-10-14 15:30:00|2026-10-17 21:18:35|2026-10-17 21:18:35
-- broker_quote_depth_snap
puller930_upstox_151026-0033.db|7896|2026-10-19 09:15:00|2026-10-19 15:30:00|2026-10-19 22:12:14|2026-10-19 22:12:14
pullerfull_upstox_151026-0031.db|11235|2026-10-15 09:15:00|2026-10-16 15:30:00|2026-10-17 21:18:35|2026-10-17 21:18:35
upstox_121026-1533.db|3906|2026-10-14 11:33:00|2026-10-14 15:30:00|2026-10-17 21:18:35|2026-10-17 21:18:35
### HDD copy (symlink target) counts
-- broker_chain_snap
73144|2026-10-14 11:34:00|2026-10-19 15:30:00
-- broker_quote_depth_snap
23037|2026-10-14 11:33:00|2026-10-19 15:30:00
### puller DB tables matching chain|depth|quote
-- /volume2/datapullers/dhan/pullerfull_dhan_151026-0031.db

-- /volume2/datapullers/upstox/pullerfull_upstox_151026-0031.db

-- /volume2/datapullers/fyers/pullerfull_fyers_151026-0030.db

######## i7
route j1800-cf failed (rc=255: Bad Gateway Connection closed by UNKNOWN port 65535 )
ROUTE: i5-cf>i7
### i7 Tue Nov  3 21:39:38 IST 2026 
Tue Nov  3 21:39:38 IST 2026
IST-5:30
lrwxrwxrwx 1 root root 33 Nov 19  2025 /etc/localtime -> /usr/share/zoneinfo/Asia/Calcutta
uid=1026(roopeshkumarb) gid=100(users) groups=100(users),101(administrators),65536(docker)
/dev/mapper/cachedev_0 449394507776 150459916288 298934591488  34% /volume2
CloudSync
pkgs listed above (none = no cloudflared package)
 21:39:38 up  8:55,  0 users,  load average: 12.63, 12.05, 13.86 [IO: 11.08, 10.10, 12.34 CPU: 1.55, 1.95, 1.50]
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

### FILE audit_031126_BLK001_livewatch/12_ACCESS_ROUTES.md  sha256=a5e83763a547211e  bytes=5760
```
> UPDATE 04-11-2026 00:00 IST: the i7 NOW HAS A DIRECT CLOUDFLARE ROUTE: hostname sshi7 (tested, see 34_direct_cf_routes_tested.txt). The statements below that the i7 has no direct route describe the OLD hostname sshj1800, which still returns Bad Gateway. Open: which connector serves sshi7 and whether it survives the i5 tunnel being down (UNKNOWN); the Pi restarted at ~18:50 IST (cause UNKNOWN).

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
CORRECTED 03-11 21:50 (Fable review): the third i5 route in 11_box_reach.sh (i5-cf>i7>i5) starts with i5-cf, the very route that would have failed, so it is not independent. INDEPENDENT routes today: i5 has 2 (own tunnel; via Pi), i7 has 2 (via i5 tunnel; via Pi tunnel; neither is the i7's own), Pi has 1. (First version of this line said i5 has 3 routes.) So today: i5 has 2 independent routes (own tunnel, via Pi); i7 has 2 (via i5, via Pi) and **no direct Cloudflare route**; the Pi has 1 (`pi-cf`). Every route to the i7 passes through a box other than the i7 itself. If the i5 tunnel and the Pi tunnel both drop, the i7 is unreachable from offshore.
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

### FILE AUDITOR_RESPONSES/20261103_COMPARISON_outside_auditor_vs_fable.md  sha256=be1d76442b6ef297  bytes=8320
```
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
```

### FILE audit_031126_BLK001_livewatch/02_livewatch.py  sha256=3cdbee918d8a60a5  bytes=20033
```
#!/usr/bin/env python3
"""livewatch.py - BLK-001 (Kumar, 03-11-2026): the DATA FRESHNESS WATCHDOG that kills a silent recorder.

WHY: on 02-11-2026 the i7 Dhan depth socket closed (1006) at 13:58 and never reopened while `docker ps`
said "Up". Docker status is not data. This daemon judges each live-only recorder by the DATA it last
stored and, when the data stops during the session, issues `docker kill <container>` so the restart
policy (and, if that does not bring it back, a `docker start`) replaces the dead socket.

THE RULE (as ordered): during the session, if now - last_data > STALE_S (default 90 s since v2; the owner ordered 60 s), run
`docker kill <container>`.
  last_data = the newest of (a) status.json "last_tick" when the recorder writes one (Kite ticks) and
              (b) the modification time of today's day file or its -wal (every stored row moves it).
              (b) costs no database read. MEASURED 03-11-2026 on the i5 during the session: the longest
              gap between writes of all four recorders was 4 s (150 s window, 2 s sampling).
DEVIATIONS FROM THE ORDER, each with its reason (Kumar can switch them back with the flags):
  1 SESSION_START default 09:16, not 09:00. Reason: the recorders' own silence guards dropped sockets that
    had been silent 197-210 s at 09:11-09:13 on 03-11-2026 (pre-open is quiet). A 60 s rule from 09:00 would
    kill every recorder every morning. Flag: --session-start 09:00.
  2 MAX_KILLS_PER_HOUR = 3 per container. Reason: a kill loop under a broker's connection cap (Dhan: 5
    sockets, the 6th drops the oldest) or an outage would flap forever and lose more data than it saves.
    After the third kill it writes an ESCALATE file and logs CRITICAL, and stops killing that container.
  3 NO DAY FILE by 09:20 with instruments 0 is also treated as dead (the i7 Fyers TBT wrote no file for
    three days; a rule that only reads file age could never see it).
It NEVER touches cloudflared, portainer, blpro_09 or any name not in RECORDERS.

Stdlib only, python 3.8 compatible, no pip. ADVISORY ONLY: it reads stored data and restarts recorders.
Runs on the host (outside Docker) so a Docker service restart cannot take it down.

    python3 livewatch.py --root /volume1/docker/datapullers --box i5            # live
    python3 livewatch.py --root ... --box i5 --dry-run --once                   # print what it would do
"""
import argparse
import calendar
import json
import os
import subprocess
import sys
import time

RECORDERS = {                     # container -> (folder under root, day-file prefix)
    "tickrec": ("ticks", "ticks_"),
    "depthrec": ("depth", "depth_"),
    "upstoxrec": ("upstox_live", "upstox_"),
    "fyerstbt": ("fyers_tbt", "tbt_"),
}
# v2 (auditor condition, 03-11-2026): a recorder that writes SEVERAL sockets into ONE day file hides a dead socket behind
# the live ones (Dhan: d20 silent ~4 min 12 times on the i5 while d200 kept the file fresh). So judge each connection by
# the newest recv_ts of its own rows. Unreadable DB / no rows for the connection = UNKNOWN (never killed on UNKNOWN).
# v3: upstox/tbt write a heartbeat/open/close row into the SAME day file's `events` table (dp_recguard.log_event), which moves the
# file mtime with zero frames; so judge those by the newest frames.recv_ts too (col None = single series).
CONNS = {"depthrec": ("frames", "conn", ("d20", "d200")),
         "upstoxrec": ("frames", None, ("frames",)),
         "fyerstbt": ("frames", None, ("frames",))}
NEVER_TOUCH = ("cloudflared", "portainer", "blpro_09", "blpro_compute", "blpro_synchub",
               "blpro_vendorwatch", "watchtower")
DEFAULT_DOCKER = "/var/packages/ContainerManager/target/usr/bin/docker"


def ist(now):
    """Struct time in IST (GMT+5:30) computed from the epoch, independent of the host TZ (auditor defect 6)."""
    return time.gmtime(now + 19800)


def hhmm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def in_session(now, start, end):
    """Weekdays only, box-local time, [start, end]. (NSE holidays are not known here: on a holiday the
    recorders see no ticks, so a holiday can cost at most MAX_KILLS_PER_HOUR harmless restarts.)"""
    lt = ist(now)
    return lt.tm_wday < 5 and hhmm(start) <= lt.tm_hour * 60 + lt.tm_min <= hhmm(end)


def file_write_time(path):
    """Newest write evidence of a SQLite day file: the file or its -wal."""
    best = 0.0
    for p in (path, path + "-wal"):
        try:
            best = max(best, os.stat(p).st_mtime)
        except OSError:
            pass
    return best


def status_last_tick(status):
    """Epoch of status.json 'last_tick' ('DD-MM-YYYY HH:MM:SS GMT+5:30') or 0.0 if absent/null."""
    e = status.get("last_tick_epoch")             # TZ-safe field some recorders write
    if isinstance(e, (int, float)) and e > 0:
        return float(e)
    v = status.get("last_tick")
    if not v:
        return 0.0
    try:
        return calendar.timegm(time.strptime(str(v).replace(" GMT+5:30", ""), "%d-%m-%Y %H:%M:%S")) - 19800
    except ValueError:
        return 0.0


def conn_last(path, spec, since=0.0):
    """-> {conn: last recv_ts}; 0.0 = NO row newer than `since` (silent at least that long, or never connected: bounded scan so a dead
    connection cannot make every pass walk the whole index); None = UNKNOWN (db unreadable or locked)."""
    table, col, conns = spec
    out = {c: None for c in conns}
    try:
        import sqlite3
        con = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=3)
        try:
            for c in conns:
                if col is None:
                    r = con.execute("select recv_ts from %s where recv_ts>? order by recv_ts desc limit 1" % table, (since,)).fetchone()
                else:
                    r = con.execute("select recv_ts from %s where %s=? and recv_ts>? order by recv_ts desc limit 1" % (table, col), (c, since)).fetchone()
                out[c] = float(r[0]) if r and r[0] is not None else 0.0
        finally:
            con.close()
    except Exception:
        pass
    return out


def events_max(path, name):
    """Newest row time in the table dp_recguard writes events to (depth/upstox/tbt: events.at_ts; tickrec has session_log, a count only).
    Lets the dry run show whether non-data rows keep the file mtime fresh. '' = unknown."""
    try:
        import sqlite3
        con = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=3)
        try:
            if name == "tickrec":
                return "session_log_rows=%d" % con.execute("select count(*) from session_log").fetchone()[0]
            r = con.execute("select max(at_ts) from events").fetchone()
            return "%.0f" % r[0] if r and r[0] is not None else ""
        finally:
            con.close()
    except Exception:
        return ""


def evaluate(name, root, box, now, stale_s, no_file_after, ex=None):
    """-> dict(verdict, age_s, why). verdict in FRESH, DEAD, NO_FILE_DEAD, NO_FILE_WAITING."""
    folder, prefix = RECORDERS[name]
    day = time.strftime("%Y%m%d", ist(now))
    path = os.path.join(root, folder, box, "%s%s.db" % (prefix, day))
    status = {}
    try:
        with open(os.path.join(root, folder, box, "status.json"), encoding="utf-8") as f:
            status = json.load(f)
    except (OSError, ValueError):
        pass
    fw = file_write_time(path)
    lt = status_last_tick(status)
    if lt > now + 5:                      # future-dated last_tick would give a negative age = FRESH forever: not trusted
        lt = 0.0
    last = max(fw, lt)
    if ex is not None:                    # observation fields for the --csv dry-run log (auditor round 2)
        ex.update({"file_mtime": os.stat(path).st_mtime if os.path.exists(path) else 0.0, "wal_mtime": (os.stat(path + "-wal").st_mtime if os.path.exists(path + "-wal") else 0.0),
                   "last_tick_epoch": lt, "events_max": events_max(path, name)})
    if fw == 0.0:
        lt_now = ist(now)
        if lt_now.tm_hour * 60 + lt_now.tm_min >= hhmm(no_file_after) and not status.get("instruments"):
            return {"verdict": "NO_FILE_DEAD", "age_s": None,
                    "why": "no day file %s and instruments=0 after %s" % (os.path.basename(path), no_file_after)}
        return {"verdict": "NO_FILE_WAITING", "age_s": None, "why": "no day file yet"}
    age = now - last
    if age > stale_s:
        return {"verdict": "DEAD", "age_s": round(age, 1),
                "why": "last data %.0f s ago (limit %.0f s); file_write=%s last_tick=%s" % (
                    age, stale_s, time.strftime("%H:%M:%S", ist(fw)),
                    time.strftime("%H:%M:%S", ist(lt)) if lt else "n/a")}
    why = "last data %.1f s ago" % age
    if name in CONNS:
        t_q = time.time()
        cl = conn_last(path, CONNS[name], now - max(600.0, 4 * stale_s))
        if ex is not None:
            ex["frames"] = ";".join("%s=%s" % (c, ("%.0f" % t) if t else ("none_in_window" if t == 0.0 else "UNKNOWN")) fo
[TRUNCATED at 9000 characters; full file at the raw URL]
```

### FILE audit_031126_BLK001_livewatch/03_test_livewatch.py  sha256=dc41ddc3713cc3b5  bytes=14782
```
"""tests/test_livewatch.py - BLK-001 proof: stale data -> docker kill; fresh -> nothing; bounded; refuses strangers."""
import calendar, json, os, shutil, stat, sys, tempfile, time, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pullers", "shared"))
os.environ["TZ"] = "Asia/Kolkata"
time.tzset()
import livewatch  # noqa: E402

MON_1030 = calendar.timegm((2026, 11, 2, 5, 0, 0))      # Monday 10:30 IST
SAT_1030 = calendar.timegm((2026, 11, 7, 5, 0, 0))


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.root = os.path.join(self.d, "root")
        self.calls = os.path.join(self.d, "calls.txt")
        self.fake = os.path.join(self.d, "docker")
        with open(self.fake, "w") as f:
            f.write("#!/bin/sh\necho \"$@\" >> %s\n[ \"$1\" = inspect ] && echo true\nexit 0\n" % self.calls)
        os.chmod(self.fake, os.stat(self.fake).st_mode | stat.S_IEXEC)
        day = time.strftime("%Y%m%d", time.localtime(MON_1030))
        self.files = {}
        for name, (folder, prefix) in livewatch.RECORDERS.items():
            dd = os.path.join(self.root, folder, "i5")
            os.makedirs(dd)
            p = os.path.join(dd, "%s%s.db" % (prefix, day))
            open(p, "w").write("x")
            self.files[name] = p

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def args(self, *extra):
        return livewatch.argparse.ArgumentParser  # placeholder to keep flake8 quiet

    def watch(self, **kw):
        class A:  # same fields main() builds
            root = self.root; box = "i5"; docker = self.fake; stale_s = 90.0; session_start = "09:16"
            session_end = "15:30"; no_file_after = "09:20"; interval = 1; max_kills = 3; restart_wait = 0; conn_action = "alarm"
            state_dir = os.path.join(self.d, "state"); log = ""; dry_run = False
        for k, v in kw.items():
            setattr(A, k, v)
        return livewatch.Watch(A)

    def touch(self, name, t):
        os.utime(self.files[name], (t, t))

    def kills(self):
        if not os.path.exists(self.calls):
            return []
        return [l.strip() for l in open(self.calls) if l.startswith("kill")]

    def depth_db(self, d20_age, d200_age, now=MON_1030):
        import sqlite3
        p = self.files["depthrec"]; os.remove(p)
        c = sqlite3.connect(p); c.execute("create table frames(recv_ts real, conn text, raw blob)")
        c.execute("insert into frames values(?,?,?)", (now - d20_age, "d20", b"x"))
        c.execute("insert into frames values(?,?,?)", (now - d200_age, "d200", b"x")); c.commit(); c.close()
        self.touch("depthrec", now - 3)          # the FILE is fresh: d200 (or anything) wrote 3 s ago

    def test_dead_d20_is_caught_even_though_the_file_is_fresh_and_only_alarms_by_default(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.depth_db(d20_age=200, d200_age=2)
        w = self.watch(); w.once(MON_1030)
        self.assertEqual(self.kills(), [])                                   # alarm only: a healthy d200 is not dropped
        self.assertTrue(os.path.exists(os.path.join(w.a.state_dir, "ALARM_depthrec.json")))
        r = livewatch.evaluate("depthrec", self.root, "i5", MON_1030, 90.0, "09:20")
        self.assertEqual(r["verdict"], "CONN_DEAD"); self.assertIn("d20", r["why"])

    def test_conn_action_kill_still_kills(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.depth_db(d20_age=200, d200_age=2)
        self.watch(conn_action="kill").once(MON_1030)
        self.assertEqual(self.kills(), ["kill depthrec"])

    def test_refuses_to_run_when_recorder_folders_are_missing(self):
        empty = os.path.join(self.d, "empty"); os.makedirs(empty)
        self.assertEqual(livewatch.main(["--root", empty, "--box", "i7", "--once", "--docker", self.fake]), 2)
        self.assertEqual(self.kills(), [])

    def test_wrong_box_name_is_refused_not_killed(self):
        self.assertEqual(livewatch.main(["--root", self.root, "--box", "i7", "--once", "--docker", self.fake]), 2)
        self.assertEqual(self.kills(), [])

    def test_events_only_writes_do_not_hide_silent_frames(self):
        import sqlite3
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        p = self.files["upstoxrec"]; os.remove(p)
        c = sqlite3.connect(p); c.execute("create table frames(recv_ts real, raw blob)")
        c.execute("insert into frames values(?,?)", (MON_1030 - 300, b"x")); c.commit(); c.close()
        self.touch("upstoxrec", MON_1030 - 3)                                  # a heartbeat/open/close event row just moved mtime
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), ["kill upstoxrec"])

    def test_future_dated_last_tick_is_not_trusted(self):
        self.touch("tickrec", MON_1030 - 500)
        st = os.path.join(self.root, "ticks", "i5", "status.json")
        json.dump({"last_tick": "01-01-2030 10:00:00 GMT+5:30"}, open(st, "w"))
        r = livewatch.evaluate("tickrec", self.root, "i5", MON_1030, 90.0, "09:20")
        self.assertEqual(r["verdict"], "DEAD")

    def test_session_and_day_are_ist_even_when_the_host_is_utc(self):
        os.environ["TZ"] = "UTC"; time.tzset()
        try:
            self.assertTrue(livewatch.in_session(MON_1030, "09:16", "15:30"))     # 10:30 IST, host says 05:00
            self.assertFalse(livewatch.in_session(calendar.timegm((2026, 11, 2, 11, 0, 0)), "09:16", "15:30"))   # 16:30 IST
        finally:
            os.environ["TZ"] = "Asia/Kolkata"; time.tzset()

    def test_kill_bound_is_per_day_and_escalation_rearms(self):
        for n in self.files:
            self.touch(n, MON_1030 - 500)
        w = self.watch()
        for i in range(5):
            w.once(MON_1030 + i * 20)          # all within the same IST day
        self.assertEqual(self.kills().count("kill depthrec"), 3)
        esc = os.path.join(w.a.state_dir, "ESCALATE_depthrec.json"); self.assertTrue(os.path.exists(esc))
        os.remove(esc); w.once(MON_1030 + 200)
        self.assertFalse(os.path.exists(esc))     # not rewritten inside the hour
        w.once(MON_1030 + 3700)  # an hour later, same day: escalation is written again, still no kill
        self.assertTrue(os.path.exists(esc)); self.assertEqual(self.kills().count("kill depthrec"), 3)

    def test_both_connections_fresh_nothing_killed(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.depth_db(d20_age=20, d200_age=2)
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), [])

    def test_unreadable_depth_db_is_unknown_not_dead(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)          # the placeholder "x" file is not a database
        r = livewatch.evaluate("depthrec", self.root, "i5", MON_1030, 90.0, "09:20")
        self.assertEqual(r["verdict"], "FRESH"); self.assertIn("UNKNOWN", r["why"]); self.assertEqual(self.kills(), [])

    def test_default_limit_is_90_and_a_55s_healthy_gap_is_left_alone(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.touch("upstoxrec", MON_1030 - 55)
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), [])
        # the real command-line default, read by running main() with a stub that captures the parsed args
        import subprocess
        out = subprocess.run([sys.executable, livewatch.__file__, "--root", self.root, "--box", "i5", "--once", "--dry-run"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=dict(os.environ, TZ="Asia/Kolkata"))
        self.assertEqual(out.returncode, 0)
        self.assertEqual(livewatch.argparse.ArgumentParser.__name__, "ArgumentParser")
        self.assertIn("default=90.0", open(livewatch.__file__).read().replace(" ", ""))

    def test_csv_log_has_one_row_per_recorder_and_dry_run_never_kills_or_starts(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.depth_db(d20_age=200, d200_age=2)
        csvp = os.path.join(self.d, "dry.csv")
        w = self.watch(dry_run=True, csv=csvp); w.once(MON_1030); w.once(MON_1030 + 20)
        rows = [l.split(",") for l in open(csvp).read().strip().splitlines()]
        self.assertEqual(len(rows), 1 + 2 * 4)                      # header + 2 passes x 4 recorders
        self.assertIn("timestamp_ist", rows[0][1]); depth = [r for r in rows if r[3] == "depthrec"]
        self.assertTrue(all(r[4] == "CONN_DEAD" for r in depth)); self.assertTrue(any("d20=" in x for x in depth[0]))
        self.assertEqual([l for l in open(self.calls)] if os.path.exists(self.calls) else [], [l for l in (open(self.calls) if os.path.exists(self.calls) else []) if l.startswith("inspect")])  # only read-only inspect
        self.assertEqual(self.kills(), [])

    def test_never_connected_d20_is_c
[TRUNCATED at 9000 characters; full file at the raw URL]
```

### FILE audit_031126_BLK001_livewatch/27_livewatch_v3_to_v3.1.diff  sha256=7114ce83e1ba8900  bytes=9716
```
--- audit_031126_BLK001_livewatch/02c_livewatch_v3.py	2026-11-03 16:48:12.853403571 +0000
+++ audit_031126_BLK001_livewatch/02_livewatch.py	2026-11-03 16:48:12.856350272 +0000
@@ -98,8 +98,9 @@
         return 0.0
 
 
-def conn_last(path, spec):
-    """-> {conn: last recv_ts or None}; None = UNKNOWN (db unreadable, locked, or no rows for that conn)."""
+def conn_last(path, spec, since=0.0):
+    """-> {conn: last recv_ts}; 0.0 = NO row newer than `since` (silent at least that long, or never connected: bounded scan so a dead
+    connection cannot make every pass walk the whole index); None = UNKNOWN (db unreadable or locked)."""
     table, col, conns = spec
     out = {c: None for c in conns}
     try:
@@ -108,10 +109,10 @@
         try:
             for c in conns:
                 if col is None:
-                    r = con.execute("select recv_ts from %s order by recv_ts desc limit 1" % table).fetchone()
+                    r = con.execute("select recv_ts from %s where recv_ts>? order by recv_ts desc limit 1" % table, (since,)).fetchone()
                 else:
-                    r = con.execute("select recv_ts from %s where %s=? order by recv_ts desc limit 1" % (table, col), (c,)).fetchone()
-                out[c] = float(r[0]) if r and r[0] is not None else None
+                    r = con.execute("select recv_ts from %s where %s=? and recv_ts>? order by recv_ts desc limit 1" % (table, col), (c, since)).fetchone()
+                out[c] = float(r[0]) if r and r[0] is not None else 0.0
         finally:
             con.close()
     except Exception:
@@ -119,7 +120,24 @@
     return out
 
 
-def evaluate(name, root, box, now, stale_s, no_file_after):
+def events_max(path, name):
+    """Newest row time in the table dp_recguard writes events to (depth/upstox/tbt: events.at_ts; tickrec has session_log, a count only).
+    Lets the dry run show whether non-data rows keep the file mtime fresh. '' = unknown."""
+    try:
+        import sqlite3
+        con = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=3)
+        try:
+            if name == "tickrec":
+                return "session_log_rows=%d" % con.execute("select count(*) from session_log").fetchone()[0]
+            r = con.execute("select max(at_ts) from events").fetchone()
+            return "%.0f" % r[0] if r and r[0] is not None else ""
+        finally:
+            con.close()
+    except Exception:
+        return ""
+
+
+def evaluate(name, root, box, now, stale_s, no_file_after, ex=None):
     """-> dict(verdict, age_s, why). verdict in FRESH, DEAD, NO_FILE_DEAD, NO_FILE_WAITING."""
     folder, prefix = RECORDERS[name]
     day = time.strftime("%Y%m%d", ist(now))
@@ -135,6 +153,9 @@
     if lt > now + 5:                      # future-dated last_tick would give a negative age = FRESH forever: not trusted
         lt = 0.0
     last = max(fw, lt)
+    if ex is not None:                    # observation fields for the --csv dry-run log (auditor round 2)
+        ex.update({"file_mtime": os.stat(path).st_mtime if os.path.exists(path) else 0.0, "wal_mtime": (os.stat(path + "-wal").st_mtime if os.path.exists(path + "-wal") else 0.0),
+                   "last_tick_epoch": lt, "events_max": events_max(path, name)})
     if fw == 0.0:
         lt_now = ist(now)
         if lt_now.tm_hour * 60 + lt_now.tm_min >= hhmm(no_file_after) and not status.get("instruments"):
@@ -149,8 +170,13 @@
                     time.strftime("%H:%M:%S", ist(lt)) if lt else "n/a")}
     why = "last data %.1f s ago" % age
     if name in CONNS:
-        cl = conn_last(path, CONNS[name])
-        dead = ["%s silent %.0f s" % (c, now - t) for c, t in sorted(cl.items()) if t is not None and now - t > stale_s]
+        t_q = time.time()
+        cl = conn_last(path, CONNS[name], now - max(600.0, 4 * stale_s))
+        if ex is not None:
+            ex["frames"] = ";".join("%s=%s" % (c, ("%.0f" % t) if t else ("none_in_window" if t == 0.0 else "UNKNOWN")) for c, t in sorted(cl.items()))
+            ex["query_ms"] = "%.0f" % ((time.time() - t_q) * 1000)
+        dead = [("%s silent >= %.0f s (no row in window)" % (c, max(600.0, 4 * stale_s))) if t == 0.0 else "%s silent %.0f s" % (c, now - t)
+                for c, t in sorted(cl.items()) if t is not None and (t == 0.0 or now - t > stale_s)]
         unk = [c for c, t in sorted(cl.items()) if t is None]
         if dead:
             multi = CONNS[name][1] is not None          # several sockets share one file: killing the container drops the healthy ones
@@ -167,6 +193,7 @@
         self.kills = {}                       # container -> [epoch,...]
         os.makedirs(a.state_dir, exist_ok=True)
         self.escalated = {}
+        self.rc_cache = {}
 
     def log(self, level, msg):
         line = "%s [livewatch %s] %s %s" % (time.strftime("%d-%m-%Y %H:%M:%S GMT+5:30"), self.a.box, level, msg)
@@ -191,6 +218,9 @@
         if name in NEVER_TOUCH or name not in RECORDERS:
             self.log("REFUSE", "%s is not a managed recorder" % name)
             return
+        if self.a.dry_run:                # dry run keeps EVERY verdict of EVERY cycle: no bound, no hourly suppression, no kill counting
+            self.log("WARN", "DRYRUN %s: %s -> WOULD docker kill %s" % (name, why, name))
+            return
         today = time.strftime("%Y%m%d", ist(now))
         recent = [t for t in self.kills.get(name, []) if time.strftime("%Y%m%d", ist(t)) == today]   # per IST DAY, not rolling hour
         if len(recent) >= self.a.max_kills:
@@ -218,10 +248,45 @@
         else:
             self.log("INFO", "%s is running again (restart policy)" % name)
 
+    def docker_ro(self, *args):
+        """READ-ONLY docker query (inspect); runs even under --dry-run because it changes nothing. '' on any failure."""
+        try:
+            p = subprocess.run([self.a.docker] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
+                               universal_newlines=True, timeout=15)
+            return p.stdout.strip() if p.returncode == 0 else ""
+        except Exception:
+            return ""
+
+    def csv_row(self, name, r, ex, now, action="none"):
+        path = getattr(self.a, "csv", "")
+        if not path:
+            return
+        import csv
+        c = self.rc_cache.get(name)
+        if c is None or now - c[0] >= 60:        # docker CLI is slow on these boxes under load: sample the restart counter once a minute
+            c = (now, self.docker_ro("inspect", name, "--format", "{{.RestartCount}}|{{.State.StartedAt}}|{{.State.Running}}") if name in RECORDERS else "")
+            self.rc_cache[name] = c
+        rc = c[1]
+        new = not os.path.exists(path)
+        try:
+            with open(path, "a", newline="") as f:
+                w = csv.writer(f)
+                if new:
+                    w.writerow(["ts_epoch", "timestamp_ist", "box", "recorder", "verdict", "action", "age_s", "last_tick_epoch", "frames_recv_ts", "query_ms",
+                                "file_mtime", "wal_mtime", "events_max", "restart_count|started_at|running", "reason"])
+                w.writerow(["%.0f" % now, time.strftime("%Y-%m-%d %H:%M:%S", ist(now)), self.a.box, name, r["verdict"], action, r["age_s"],
+                            "%.0f" % ex.get("last_tick_epoch", 0), ex.get("frames", ""), ex.get("query_ms", ""), "%.0f" % ex.get("file_mtime", 0),
+                            "%.0f" % ex.get("wal_mtime", 0), ex.get("events_max", ""), rc, r["why"]])
+        except OSError:
+            pass
+
     def alarm(self, name, why, now):
         """Alarm only (owner decision pending, both auditors: do not kill a container for one dead socket): CRITICAL log +
         ALARM file, at most once an hour per container."""
         key = "alarm:" + name
+        if self.a.dry_run:
+            self.log("CRITICAL", "DRYRUN %s: %s -> WOULD ALARM (--conn-action alarm)" % (name, why))
+            return
         if now - self.escalated.get(key, 0) <= 3600:
             return
         self.escalated[key] = now
@@ -239,13 +304,17 @@
             return []
         results = []
         for name in sorted(RECORDERS):
-            r = evaluate(name, self.a.root, self.a.box, now, self.a.stale_s, self.a.no_file_after)
+            ex = {}
+            r = evaluate(name, self.a.root, self.a.box, now, self.a.stale_s, self.a.no_file_after, ex)
             results.append((name, r))
             if r["verdict"] == "CONN_DEAD" and getattr(self.a, "conn_action", "alarm") != "kill":
+                self.csv_row(name, r, ex, now, "would_alarm" if self.a.dry_run else "alarm")
                 self.alarm(name, r["why"], now)
             elif r["verdict"] in ("DEAD", "NO_FILE_DEAD", "CONN_DEAD"):
+                self.csv_row(name, r, ex, now, "would_kill" if self.a.dry_run else "kill_or_suppressed")
                 self.kill(name, r["why"], now)
             else:
+                self.csv_row(name, r, ex, now, "none")
[TRUNCATED at 9000 characters; full file at the raw URL]
```

### FILE audit_031126_BLK001_livewatch/28_unit_tests_v3.1_output.txt  sha256=f89a53200a3f8733  bytes=1427
```
livewatch v3.1 unit tests (25), run 03-11-2026 22:25 IST on the sandbox, TZ=Asia/Kolkata python3 -W ignore -m unittest -v tests.test_livewatch
test_a_stale_file_triggers_exactly_docker_kill_of_that_container
test_both_connections_fresh_nothing_killed
test_conn_action_kill_still_kills
test_csv_log_has_one_row_per_recorder_and_dry_run_never_kills_or_starts
test_dead_d20_is_caught_even_though_the_file_is_fresh_and_only_alarms_by_default
test_default_limit_is_90_and_a_55s_healthy_gap_is_left_alone
test_docker_start_fallback_runs_when_policy_did_not_restart
test_dry_run_logs_every_verdict_every_cycle_without_suppression
test_dry_run_prints_but_runs_nothing
test_events_only_writes_do_not_hide_silent_frames
test_fresh_data_is_left_alone
test_future_dated_last_tick_is_not_trusted
test_it_refuses_strangers
test_kill_bound_is_per_day_and_escalation_rearms
test_kills_are_bounded_per_hour_then_escalate
test_never_connected_d20_is_conn_dead_not_unknown
test_no_day_file_after_0920_with_no_instruments_is_dead
test_outside_the_session_and_on_weekends_nothing_is_killed
test_proof_mode_judges_only_the_disposable_recorder
test_refuses_to_run_when_recorder_folders_are_missing
test_session_and_day_are_ist_even_when_the_host_is_utc
test_state_dir_default_is_not_tmp
test_status_last_tick_counts_when_the_file_is_old
test_unreadable_depth_db_is_unknown_not_dead
test_wrong_box_name_is_refused_not_killed Ran 25 tests in 0.340s OK
```

### FILE audit_031126_BLK001_livewatch/29_mutations_v3.1.txt  sha256=e19b45c12c2dcad5  bytes=806
```
v3.1 mutation checks 03-11-2026 22:15 IST; 25 tests each; file restored. (A first mutation 'never-connected treated as alive' via (now - t > stale_s) was an EQUIVALENT mutant: t=0.0 gives an enormous age; replaced by the next one.)
MUT [never-connected conn becomes UNKNOWN again]: FAIL: test_never_connected_d20_is_conn_dead_not_unknown;
MUT [dry-run suppression back]: FAIL: test_dry_run_logs_every_verdict_every_cycle_without_suppression;
MUT [bounded scan removed]: FAIL: test_conn_action_kill_still_kills;FAIL: test_csv_log_has_one_row_per_recorder_and_dry_run_never_kills_or_starts;FAIL: test_dead_d20_is_caught_even_though_the_file_is_fresh_and_only_alarms_by_default;FAIL: test_never_connected_d20_is_conn_dead_not_unknown;
restored: Ran 25 tests in 0.340s OK  md5 9dba3f38dfdcf49a12eb8530bcdfbe06
```

### FILE audit_031126_BLK001_livewatch/30_preflight_v3.1_real_files.txt  sha256=b2434da55da4a21f  bytes=1102
```
PREFLIGHT of v3.1 on the real day files, both boxes, 03-11-2026 22:16-22:20 IST, --dry-run --once (no kill possible), market closed
A) default limit 90 s: recorders stopped at 15:35 so file-level DEAD (as expected; conn query not reached)
B) --stale-s 100000 so the file-level check passes and the per-connection query runs on the REAL files; columns: recorder,verdict,frames_recv_ts(epoch),query_ms,file_mtime,events_max
i5: depthrec FRESH d20=1793700310;d200=1793700310 query 251 ms | fyerstbt FRESH 277 ms | tickrec FRESH (status/mtime only; events=session_log_rows=3) | upstoxrec FRESH 112 ms
i7: depthrec FRESH d20=1793700313;d200=1793700313 query 74 ms | fyerstbt FRESH 310 ms | tickrec FRESH session_log_rows=3 | upstoxrec FRESH 127 ms
Note: events_max (newest events row) is within ~1 s of the last frame on every recorder: the stop-of-session event. Load average on both boxes ~12 at the time. Query times are on CLOSED files, not during a session.
Dry-run daemons started 22:16 IST on both boxes (pid files in the state dir, /proc check ALIVE); first in-session cycle will be 09:00 tomorrow.
```

### FILE audit_031126_BLK001_livewatch/31_gap_histogram_tool.py  sha256=10836f9c6fc413d9  bytes=2830
```
#!/usr/bin/env python3
"""gap_histogram.py - READ-ONLY. For every day file of the four live recorders on THIS box, count the silent gaps inside the
session window (default 09:15-15:30 IST) above 60/90/120/180 s and print the longest gap. Evidence for the livewatch threshold.
  python3 gap_histogram.py <datapullers root> <box>     ticks = NIFTY 50 token 256265 only; depth split by conn (d20 / d200)
Opens each file with mode=ro and walks the recv_ts index in order; no writes. Gaps that span the window edge are ignored."""
import glob, os, sqlite3, sys, time
LIMITS = (60, 90, 120, 180)
SPECS = (("ticks", "ticks_", "select recv_ts from ticks where token=256265 and recv_ts>=? and recv_ts<=? order by recv_ts", ("NIFTY",)),
         ("depth", "depth_", "select recv_ts from frames where conn=? and recv_ts>=? and recv_ts<=? order by recv_ts", ("d20", "d200")),
         ("upstox_live", "upstox_", "select recv_ts from frames where recv_ts>=? and recv_ts<=? order by recv_ts", ("frames",)),
         ("fyers_tbt", "tbt_", "select recv_ts from frames where recv_ts>=? and recv_ts<=? order by recv_ts", ("frames",)))
def window(day, a="09:15", b="15:30"):
    t = lambda hm: time.mktime(time.strptime(day + " " + hm, "%Y%m%d %H:%M"))      # box TZ is IST (verified /etc/TZ)
    return t(a), t(b)
def main():
    root, box = sys.argv[1], sys.argv[2]
    print("recorder,conn,day,rows,max_gap_s,>60,>90,>120,>180,first,last")
    for folder, prefix, sql, conns in SPECS:
        for p in sorted(glob.glob(os.path.join(root, folder, box, prefix + "20??????.db"))):
            day = os.path.basename(p)[len(prefix):len(prefix) + 8]; t0, t1 = window(day)
            try:
                con = sqlite3.connect("file:%s?mode=ro" % p, uri=True, timeout=10)
            except Exception as e:
                print("%s,-,%s,ERR %s" % (folder, day, e)); continue
            for c in conns:
                args = (t0, t1) if folder in ("ticks", "upstox_live", "fyers_tbt") else (c, t0, t1)
                n = 0; prev = None; mx = 0.0; cnt = [0] * 4; first = last = None
                try:
                    for (t,) in con.execute(sql, args):
                        n += 1; first = first or t; last = t
                        if prev is not None:
                            g = t - prev; mx = max(mx, g)
                            for i, L in enumerate(LIMITS): cnt[i] += g > L
                        prev = t
                    print("%s,%s,%s,%d,%.0f,%d,%d,%d,%d,%s,%s" % (folder, c, day, n, mx, cnt[0], cnt[1], cnt[2], cnt[3],
                          time.strftime("%H:%M:%S", time.localtime(first)) if first else "", time.strftime("%H:%M:%S", time.localtime(last)) if last else ""))
                except Exception as e:
                    print("%s,%s,%s,ERR %s" % (folder, c, day, e))
            con.close()
main()
```

### FILE AUDITOR_RESPONSES/20261103_FABLE_VERIFICATION_of_QWEN_round2.md  sha256=fd5062fea4b404f1  bytes=5823
```
# Fable verification of the outside auditor's (Qwen) ROUND-2 verdict, 03-11-2026 ~22:10 IST (condensed by the author; every row and the bottom line are kept; the verbatim report is in the owner's chat)
Owner's rule (03-11-2026): each external audit with Qwen must be verified with Fable. Fable read the repo only (no box access), reran the v3 tests itself (22 OK, md5 matches INDEX) and drove a synthetic dry run of v3.
## Statement-by-statement (Qwen statement | Fable verdict | evidence)
1 v3 code "not inlined" -> CANNOT CHECK | CORRECT but self-inflicted (files in repo and in INDEX, README inlined only 26/20/25). Author action: 02/03 now inlined.
2 "relying on Fable's confirmation of 22 tests and mutation catches" | INCORRECT: Fable reran 13 tests (v2); files 20/25 are the author's own run.
3 Fable "verified the soundness of the v3 corrections" | INCORRECT: Fable's review predates v3; the COMPARISON status column is the author's text.
4 C-005 unproven (one day) | CORRECT. 5 Defect 1 fixed | CORRECT. 6 alarm default "prevents the Dhan 805 cascade" | UNSUPPORTED (cause C-017 unproven; alarm adds no sockets). 7 tickrec partly resolved | CORRECT. 8 TZ fixed, both IST | CORRECT.
9 missing proof "cat /etc/TZ and date; not in repo" | INCORRECT (BLK002/05). 10 state dir after reboot | CORRECT (absent). 11 dp_recguard 180 s vs livewatch 90 s fight | CORRECT as a concern for upstox/tbt/tick (depth default alarms); the 180 s figure is not in a raw file.
12 BLK002/05 "not inlined" | INCORRECT (README inlines it). 13 src_store proves copies of puller-DB snapshots | PARTLY (provenance label yes; a source copy existing is UNKNOWN, the puller DBs have no chain/depth/quote table).
14 "Fable's discovery that the HDD path is a symlink" | INCORRECT: Fable guessed an older HDD copy; the author's readlink corrected it.
15 "no separate HDD copy means no H12 violation" | INCORRECT reasoning: H12 needs NON-recoverable data on HDD, so absence of an HDD copy makes a violation MORE likely if the data is non-recoverable.
16 "data on SSD is correct for recoverable puller DBs" | UNSUPPORTED: recoverability of broker_chain_snap / broker_quote_depth_snap is proven nowhere; the owner's H12 table lists chain snapshots as non-recoverable. 17 "14-19 Oct snapshots are historical, not live-only" | UNSUPPORTED (age is not recoverability).
18 SQL probe | PARTLY: AND/OR precedence bug (needs parentheses); the table list is already in BLK002/04 and 05. 19 asks readlink | already in 05. 20 "ASSUMPTIONS FOUND: NONE" | INCORRECT (row 16 is one).
21 V-002 "BLK-002 code NOT REQUIRED" | UNSUPPORTED: rests on row 16; puller DBs (173 GB on SSD) were only grepped for 3 name patterns. UNKNOWN is not "not required".
22 11 DOES NOT SUPPORT | CORRECT. 23 12 DOES NOT SUPPORT (count) | STALE (already corrected). 24 502 "points to sshd or the container on i7" | UNSUPPORTED (cause UNKNOWN). 25 "docker ps | grep cloudflared / docker logs on i7" | INCORRECT premise (the i7 has no cloudflared package or container, BLK002/05).
26 tickrec probe "events table row count" | INCORRECT: the ticks day file has instruments_today, session_log, ticks; no events table.
27 "daemon MUST start at 09:00, log 09:00-09:20" | INCOMPLETE: v3 default --session-start is 09:16 and evaluates nothing before it; needs --session-start 09:00 stated.
28 "v3 safe for dry run" | PARTLY: dry-run spawns no docker command, but writes state/pid/ALARM files under /volume1 and opens 3 production SQLite files per cycle.
29 CSV fields "every evaluation cycle" | UNSUPPORTED by v3 code: no CSV existed; DEAD/CONN_DEAD lines were suppressed after 3 cycles/once per hour.
Proofs Qwen asked for that were ALREADY in the repo: TZ/date (05), readlink target (05), chain/depth table list (04/05), file 05 itself.
## Fable's dry-run spec and v3 defects (all acted on in v3.1; see COMPARISON round 3 and ledger C-028..C-033)
Spec: CSV one row per (recorder, conn) per cycle; histogram must come from the DAY FILES (scripts 09/16 extended to upstox/tbt), not the livewatch log (15-20 s sampling cannot give gap lengths); --session-start 09:00; external 60 s docker inspect RestartCount probe; at start: docker ps (dp_watchdog / compose livewatch running?), id, ls -l of day files and -wal/-shm; time one --once --dry-run in session; end of session gap lists + events rows + status.json copies.
Defects: (1) dry run suppressed the lines it must keep (kills counted in dry-run -> bound -> one CRITICAL/hour) [FIXED v3.1: every verdict every cycle, test + mutation]; (2) dry run writes to the production volume (state dir, pid, ALARM files) [OPEN, disclosed: small files under _state/livewatch_dry]; (3) conn_last unbounded backward index walk, worst when d20 never connected [FIXED: scan bounded to max(600 s, 4x limit); none-in-window = silent; query 74-310 ms on closed real files]; (4) WAL/-shm readability as the daemon user [OPEN: first in-session read tomorrow]; (5) log label hard-codes GMT+5:30 [CSV now carries epoch]; (6) counters reset on restart, pid-lock reuse, one exception aborts a pass [OPEN].
## Bottom line (Fable)
Qwen's round-2 verdict is NOT an independent check: it did not read the v3 code/tests although both were in the repo, cited a Fable confirmation that does not exist, misattributed the symlink finding, asked for four proofs already present, prescribed a cloudflared probe on a box with no cloudflared and a tickrec events probe on a file with no events table, and built V-002 ("code NOT REQUIRED") on an unproven recoverability assumption while declaring "ASSUMPTIONS FOUND: NONE". Where it repeats the earlier reviews (dry run only, no kills, no threshold without a multi-session histogram) it is sound but borrowed. Owner decisions still open: alarm vs kill, dp_watchdog vs livewatch, whether the 14-19 Oct chain snapshots are live-only.
```

### FILE audit_031126_NIGHT_weekly_extras_move/01_DATA_NEEDED_FOR_EDGE_031126.md  sha256=fce6590593cd4938  bytes=10623
```
# DATA NEEDED FOR EDGE (retail, API-limited) - one list, live-only vs recoverable, recorder status. 03-11-2026 23:00 IST
Owner order: record the weekly expiry and every missing live-only feed; do not ask. Status words: RECORDING (day-file proof exists), DEPLOYED-NOT-YET-SEEN (code+env on both boxes, first proof = 04-11 09:00 session), MISSING (no recorder), UNKNOWN.

## 0. Why weekly expiry was not covered (facts, not excuses)
- The older need lists (docs/framework/data_need/NEED_BACKTEST/ML/PAPER/LIVE_291026.md and NEW_SYSTEM_NEED_LIST_301026.md) are organised by CONSUMER of the old engine (backtest, ML, paper, live). They mention weekly only as an expiry RULE or a history flag: BT-09, N4, L24, NEED_BACKTEST E2, NEED_PAPER P7, ML-12, ML-05 ("weekly rows exist only from the weekly start dates"), OFFER_VS_HELD row 19. None of them says "record the live ticks/depth/chain of the weekly contracts". CORRECTION after the Fable audit: the weekly WAS on record as a data FEATURE need earlier: docs/research/ALGOTEST_FEATURES_DATA_151026-0808.md line 70 (15-10-2026) "G2 weekly and next-weekly expiries ... add WEEK AFTER monthly". It was never turned into a recorder requirement.
- The live-only work (02-11) was organised BY BROKER. The audit scoreboard listed "weekly options only on Kite; Dhan and Upstox record only the monthly" as ACCEPTED, NEEDS YOUR DECISION (AUDIT_SCOREBOARD_021126.md section 3b) and I left it there instead of promoting it into the need list. That was my miss: a recommendation I had already made ("Yes") needed no decision.
- Consequence: weekly expiry (Tuesday) is the contract family where most intraday option activity sits, and 2 of 3 depth recorders did not have it. Fixed tonight (section 3). Two corrections from the Fable audit: there are FOUR depth/tick recorders (Kite, Dhan, Upstox, Fyers TBT), not three; Fyers TBT is monthly-only by construction (dp_fyerstbt.py:106-111 'a weekly symbol never matches') and is STILL not fixed (B9).

## 1. Feature groups the engine needs (multi-timeframe regime, direction, edge after costs)
| # | Group | What exactly | Live-only? | Source (per CLAUDE.md constraints) | Status |
|---|---|---|---|---|---|
| G1 | Spot and futures | NIFTY 50 index, near + next futures: price, traded volume (futures volume only; index volume is vendor-aggregate), OI | candles recoverable (SSD); live L1+5-depth NOT | Kite ticks; Upstox feed; Dhan | RECORDING (Kite: near+next fut, index). Dhan d200 = one monthly future |
| G2 | Options, monthly | ATM+/- strikes: ticks, depth, OI | live-only | Kite (code defaults +/-20 monthly, +/-15 nearest, dp_tickrec.py:47-48; env override UNKNOWN); Dhan d20; Upstox | RECORDING |
| G3 | Options, WEEKLY (nearest) | ATM+/- strikes: ticks, depth, OI | live-only | Kite (already); Dhan d20 + Upstox via weekly patch | Kite RECORDING; Dhan/Upstox DEPLOYED-NOT-YET-SEEN (final settings: Dhan DEPTH_WEEKLY_STRIKES=6 + monthly 5 = 26 + 22 = 48 of 50 slots; Upstox UPSTOX_WEEKLY_STRIKES=5 + monthly 5 inside 50 keys incl. index, VIX, future; no new socket). Monthly-expiry week (18-24 Nov and every month) fixed after the Fable audit: the expiring monthly gets the wide window |
| G4 | Option chain snapshots with Greeks/IV (dp_snap.py takes the weekly too: DP_SNAP_WEEKLY default 1; whether dp_snap runs on the boxes is UNKNOWN, it is not in the compose file) | per strike: OI, prev OI, IV, delta/gamma/theta/vega, bid/ask | live-only (no history anywhere) | Upstox /v2/option/chain, Dhan /optionchain, Fyers options-chain-v3, NSE | PARTIAL: old pullers (fullpuller/puller930) store snapshots in puller DB table rows_raw on SSD (content and cadence UNMEASURED, see 4) |
| G5 | Volatility | India VIX live; realized vol from futures | VIX live in Kite+Upstox feeds; history only since 2025-08-11 | Kite token 264969; Upstox NSE_INDEX|India VIX | RECORDING |
| G6 | Breadth | all 50 NIFTY constituents live (TICK_EXTRA_EQ=50; the first version took the first 20 alphabetically, a poor sample, changed after the Fable audit); candles recoverable | live L1/depth live-only | Kite websocket | DEPLOYED-NOT-YET-SEEN (TICK_EXTRA=1) |
| G7 | Cross-index / ETF | NIFTY BANK, NIFTY FIN SERVICE, NIFTYBEES (ETF vs futures divergence), BANKNIFTY near future | live-only for ticks | Kite websocket | DEPLOYED-NOT-YET-SEEN |
| G8 | Macro stress | USDINR near future (CDS), MCX CRUDEOIL and GOLD near futures | live ticks live-only | Kite websocket (CDS/MCX entitlement UNKNOWN) | CODE READY, OFF (TICK_EXTRA_MACRO=0): Fable could not exclude that an unentitled token flaps the socket and loses the baseline; enable on one box after a clean session |
| G9 | Pre-market gap | GIFT NIFTY | live-only (history UNKNOWN) | Upstox master (instrument_key NOT found yet) | MISSING (B7) |
| G10 | Microstructure depth | 5/20/30/50/200 level books | live-only | Kite 5; Dhan 20+200; Upstox 30; Fyers TBT 50 | RECORDING (Fyers TBT: 5 symbols; Upstox 30-level request UNVERIFIED) |
| G11 | Auction / quote extras | closing-auction fields, quotes with CAS, option-Greek quote, market status | live-only | Dhan CAS feed; Upstox quote V3/option-greek; Fyers quotes+marketStatus | MISSING (B1-B4) |
| G12 | Flows and positions | FII/DII (EOD only), participant OI (EOD) | EOD reports recoverable | NSE reports | outside the live recorders |
| G13 | Events and news | RBI/FOMC/CPI calendar (manual file), news | news live-only (Upstox 7-day window; Dhan blocked) | manual data/event_calendar.yaml; Upstox /v2/news | calendar MISSING (B6), news NEAR ZERO |
| G14 | Costs | brokerage, STT, exchange charges, slippage | not market data | broker schedules | MISSING: needed before any edge claim |

## 2. Live-only items the old pullers/recorders do NOT cover (build queue, in order; none needs a new broker socket except B8)
| id | item | broker | how | blocker |
|---|---|---|---|---|
| B1 | Option-Greek quote V3 | Upstox | REST snapshot every N s inside the API budget | must go through the pull-lease/budget system; key cap CONFLICT 50 vs 500 (docs) |
| B2 | Closing-auction live feed (CAS) | Dhan | websocket subscribe 23 on the existing feed host | socket cap (4 of 5 used) |
| B3 | Futures chain + market status + quotes with call-auction fields | Fyers | REST | rate budget |
| B4 | Quote snapshots (5-level, OI, circuits) | Kite | REST /quote | quote group 1 req/s |
| B5 | Live indices cadence; live option chain | NSE | REST scripts | NSE says scripted collection not allowed (terms unread) |
| B6 | News + manual event calendar | Upstox/Dhan/manual | puller + yaml | Dhan news blocked (DH-902) |
| B7 | GIFT NIFTY | Upstox | find instrument_key in the Upstox master, add to feed | key unknown; one connection is full at 50 keys |
| B8 | Extra index keys (Bank Nifty, ETF) on Upstox | Upstox | a SECOND websocket connection | connection count on Plus UNVERIFIED (5? contested) |
| B9 | Weekly NIFTY options on Fyers TBT 50-level | Fyers | extend dp_fyerstbt.py symbol picker to the weekly symbol format | weekly symbol format and the TBT symbol cap (5 today) must be read from the Fyers master first |
| B10 | Split the Dhan d200 contract between the boxes (i5 future, i7 nearest weekly ATM) | Dhan | env/plan change | owner's earlier accepted split, not done |
| B11 | NIFTY index + India VIX on Dhan | Dhan | d20 is NSE_FNO only today | slot/segment rules |
| B12 | BANKNIFTY options (none anywhere); Sensex (BSE F&O is offered by Kite BFO / Upstox BSE_FO but not subscribed) | Kite/Upstox | add to Kite socket | decide value; Bank Nifty weekly discontinued by NSE (UNVERIFIED) |
B1-B5 are REST pollers: they must be built behind the lease/budget controller and tested supervised in a session, so they are NOT deployed tonight.

## 3. Done tonight (03-11-2026 22:28-00:10 IST)  [final state after the Fable audit fixes]
- WEEKLY: dp_depthrec.py, dp_upstoxrec.py and the compose file deployed on i5 and i7 (originals kept as *.bak_031126_*), .env DEPTH_WEEKLY_STRIKES=6 and UPSTOX_WEEKLY_STRIKES=5 (first deployed as 6, changed to the tested 5 after the Fable audit), recorders recreated (env confirmed inside the containers). The recorders reuse today's list from today's day file, so the first weekly list is chosen at the 04-11 start. Revert: set both to 0 in .env and recreate.
- TICK_EXTRA: dp_tickrec.py (+ nifty50_syms.txt; the tickrec entrypoint now copies the file into /app, first version did NOT, so it would have recorded 0 constituents: found by the second Fable review) deployed on both boxes, TICK_EXTRA=1 TICK_EXTRA_EQ=50 TICK_EXTRA_MACRO=0 in .env, tickrec recreated (final). Never replaces the baseline list; any failure is logged to status.json errors.
- SSD to HDD: DID NOT HAPPEN, and one attempt caused an incident. The first version of tools/ssd_to_hdd_move.sh moved dhan_121026-1533.db and fyers_121026-1534.db, which dhan_current.db / fyers_current.db point at; the links dangled for several minutes until both files were restored from the sha256-verified HDD copies (T-1313). With the guards added (n
[TRUNCATED at 9000 characters; full file at the raw URL]
```

### FILE audit_031126_NIGHT_weekly_extras_move/10_weekly_deploy_raw.txt  sha256=541c98a76069348f  bytes=3224
```
WEEKLY DEPLOY, raw, 03-11-2026 22:28-22:37 IST (summary of tool output; boxes i5 and i7)
Before: box code md5 dp_depthrec.py b9c85a15304302f169016000ca22eb72, dp_upstoxrec.py 86fc351328bd6d5fce2bd25fc1be95f4; compose = Oct 23 version (no WEEKLY env). Repo versions: dp_depthrec eb9835fe6d75b7cca8b714a3ec57cfd4, dp_upstoxrec 67e5ede15641de448579c003fea55460. Box shared-code diff vs repo = only those two files + livewatch.py.
i5: all three files md5-verified after copy; .env gets DEPTH_WEEKLY_STRIKES=6 UPSTOX_WEEKLY_STRIKES=6; compose up -d depthrec upstoxrec (profiles depth, upstox). In-container env confirmed: DEPTH_WEEKLY_STRIKES=6, DEPTH_MONTHLY_STRIKES_WITH_WEEKLY=5, UPSTOX_WEEKLY_STRIKES=6, UPSTOX_MONTHLY_STRIKES_WITH_WEEKLY=5. NOTE: my first ssh route timed out mid-run and the script re-ran on a second route: two sets of backups exist (.bak_031126_2228 = true originals, md5 b9c8.../86fc...; .bak_031126_2230 = already-new files). status.json after restart: "plan: reused today's list from the day file (restart-safe)", so the weekly list is first chosen at the 04-11 start.
i7: same files/env deployed. The compose recreate was interrupted twice by route timeouts and left the old containers removed and two new containers created-but-not-started with hash-prefixed names (8a5c6d4f245b_depthrec, 9ac0aec13393_upstoxrec). Fixed by starting them with compose up and `docker rename` back to depthrec / upstoxrec; env verified inside both. Recording is not affected tonight (market closed), first live proof is the 04-11 session.
tickrec (extras): files deployed and md5-verified on both boxes; TICK_EXTRA=1, TICK_EXTRA_EQ=20 in .env; i7 recreated cleanly (running 22:43); i5 recreate was cancelled ("context canceled", exit 128) when my ssh route dropped, started again with `docker start` at 22:51; env verified on both.

FIX DEPLOY after the Fable audit, 03-11-2026 ~23:15-23:35 IST (both boxes): dp_depthrec.py, dp_upstoxrec.py, dp_tickrec.py and the compose file re-deployed (md5 verified, backups *.bak_fix_*); .env now UPSTOX_WEEKLY_STRIKES=5, TICK_EXTRA_EQ=50, TICK_EXTRA_MACRO=0 (DEPTH_WEEKLY_STRIKES=6, DEPTH_MONTHLY_STRIKES_WITH_WEEKLY=5, UPSTOX_MONTHLY_STRIKES_WITH_WEEKLY=5, TICK_EXTRA=1 unchanged). upstoxrec and tickrec recreated by a background script (so a dropped ssh route could not cut it), depthrec restarted. Final state seen: i5 upstoxrec/tickrec/depthrec Up healthy (i5 recreate took ~5 min under IO load: 'Removal In Progress' for minutes); i7 all three Up. In-container env confirmed on i5; i7 env set by the same .env.

FIX 2 after the second Fable review, 04-11 ~00:35 IST: the tickrec ENTRYPOINT copied only dp_tickrec.py into /app, so nifty50_syms.txt was not in the container and _eq_syms() returned [] silently (0 constituents). Fixed: entrypoint copies /src/nifty50_syms.txt too, _eq_syms also reads /src, an empty list is written to status.json errors. Proof inside the containers (docker exec tickrec ...): i5 and i7: /app/nifty50_syms.txt 561 bytes present; `import dp_tickrec; len(_eq_syms()), TICK_EXTRA, TICK_EXTRA_EQ, TICK_EXTRA_MACRO` = 50 True 50 False. i5 recreate again hung in 'Starting' and needed a manual `docker start` (running, health starting); i7 Up healthy.
```

### FILE audit_031126_NIGHT_weekly_extras_move/11_incident_ssd_move_raw.txt  sha256=76ee3961d4710d56  bytes=2252
```
INCIDENT 03-11-2026 22:39-22:50 IST (author's error), i5, raw facts
1. tools/ssd_to_hdd_move.sh v1 copied, sha256-verified and removed 'inactive' files older than 168 h from /volume2/datapullers to /volume1/docker/datapullers_ssd_overflow. It did NOT check what pointed at them. MANIFEST.tsv listed 4 moves: dhan/dhan_121026-1533.db, fyers/fyers_121026-1534.db, kite/kite_121026-1533.db, kite/pullerfull_kite_141026-1722.db (the two kite sources could not be removed: /volume2/datapullers/kite is root:root 755, we are user roopeshkumarb).
2. After I stopped the script (pkill) a symlink scan showed: /volume2/datapullers/dhan/dhan_current.db -> dhan_121026-1533.db DANGLING and /volume2/datapullers/fyers/fyers_current.db -> fyers_121026-1534.db DANGLING. (Containers mount /volume2/datapullers/<broker> and cannot follow a link into another volume.)
3. Restore: both files copied back from the HDD copies to .part, sha256 compared with MANIFEST, renamed: dhan 4936bb5242e2495ed26dc982c0f2bf9dbf6f57f4a1777cd2a91695fe0e5bd2b4 RESTORED, fyers 1c9e3099942fc3e9222e0400bec7ec2b96fde95e96a8df9eeb6954bc68a291d4 RESTORED; links OK again. Dangling window about 4-10 minutes, market closed. Who reads these links during that window: UNKNOWN.
4. v2 of the script (file 04): skips any file a symlink points at, any file with a non-empty -wal, any directory not writable, writes the marker/manifest only after the source is really gone; sandbox test proved the symlink, wal and fresh-file guards (the unwritable-directory guard is not proven in the sandbox because it runs as root). Dry run on the i5 with v2: EVERY file over 100 MB on the SSD is either active (written today) or an epoch-pointer target or in a root-owned directory: NOTHING is safely movable now.
5. SSD space after restore: /volume2 99% (3.3 GB free, byte readings: 21:39 used 216063025152 / avail 3466846208). Extra verified HDD copies remain under /volume1/docker/datapullers_ssd_overflow (dhan_121026, fyers_121026, kite_121026, kite 141026): harmless, deletable.
6. Measured: the big active puller DBs did not grow between ~21:00 (72727 MiB upstox pullerfull, 26973 MiB dhan) and 22:50 (same byte sizes), so the SSD fills slowly outside market hours; rate in session UNMEASURED (T-1312).
```

### FILE audit_031126_NIGHT_weekly_extras_move/09_unit_tests_output.txt  sha256=8fa705892ef59484  bytes=1426
```
tests run 04-11-2026 ~00:45 IST on the sandbox (tickrec extras 10 + weekly recorders 18) after the 2nd Fable review
test_compose_entrypoint_copies_the_symbol_file_into_the_container
test_constituent_count_is_capped
test_default_is_off
test_empty_constituent_list_is_reported_not_silent
test_failed_exchange_lists_are_skipped_not_fatal
test_macro_defaults_off_and_constituents_default_to_all_50
test_nifty50_symbols_come_from_the_config
test_no_duplicate_tokens
test_picks_indices_etf_constituents_and_nearest_futures
test_run_session_does_not_ask_for_cds_or_mcx_unless_macro_is_on
test_default_ignores_the_monthly_with_weekly_knob
test_defaults_when_env_unset_in_a_fresh_process
test_dhan_default_list_identical_to_old_code
test_module_defaults
test_upstox_default_list_identical_to_old_code
test_dhan_on_but_no_weekly_in_master_keeps_old_list
test_dhan_on_split_inside_50_and_both_expiries
test_dhan_over_ask_is_capped_at_50_not_exceeded
test_dhan_sockets_unchanged_and_sub_within_limit
test_env_switch_end_to_end_in_a_fresh_process
test_expiry_day_itself_still_included
test_monthly_expiry_week_gives_the_expiring_monthly_the_wide_window
test_nearest_weekly_not_other_index_not_monthly_date
test_upstox_monthly_week_same_rule_and_cap
test_upstox_on_inside_50_keys_all_expiries
test_upstox_on_no_weekly_in_master_keeps_old_list
test_upstox_over_ask_is_capped
test_window_sizes_normal_week_unchanged Ran 28 tests in 0.223s OK
```

### FILE AUDITOR_RESPONSES/20261103_FABLE_NIGHT_AUDIT_CONDENSED.md  sha256=78ee5836cec5bdd2  bytes=4277
```
# Fable audit of the night's changes (weekly, tick extras, SSD move, data-needed doc), 03-11-2026 ~23:00 IST, condensed by the author with every defect and the author's status. Verbatim report is in the owner's chat.
Tests Fable ran: weekly 15/15 OK, tick extras 6/6 OK. No .env in the repo, so every 'deployed with X' value was CANNOT CHECK for Fable (raw evidence: NIGHT/10_weekly_deploy_raw.txt).
## A) WEEKLY  verdict: SAFE WITH CONDITIONS
A1 MEDIUM monthly-expiry week wrong: nifty_weekly skips the date equal to the monthly and returns NEXT week's weekly, so in 18-24 Nov (and every month-end week) 26 of 50 Dhan slots (and 25 of 47 Upstox keys) went to a contract one week out and the EXPIRING monthly got +/-5. The old test hid it. -> FIXED (window_sizes() swaps the windows when wexp > monthly; test test_monthly_expiry_week_gives_the_expiring_monthly_the_wide_window; 18 weekly tests pass; deployed both boxes).
A2 LOW Upstox deployed 6/5 = exactly 50 keys, asymmetric, untested. -> FIXED: UPSTOX_WEEKLY_STRIKES=5 (the tested value).
A3 LOW depth/upstox in_session is weekday-only (no holiday calendar): pre-existing, OPEN.
A4 INFO monthly window shrinks from +/-12 to +/-5 on Dhan 20-level and Upstox 30-level; Kite 5-level still has +/-20: defensible for intraday; accepted.
Restart-safety confirmed: first weekly list is chosen at the 04-11 start (stored_plan reads only TODAY's day file).
## B) TICK EXTRAS  verdict: SAFE WITH CONDITIONS
B1 MEDIUM unentitled MCX/CDS tokens might flap the socket and lose the baseline (not verifiable). -> FIXED by default: TICK_EXTRA_MACRO=0 (no CDS/MCX call, no such tokens); enable on one box after a clean session.
B2 MEDIUM 'first 20 constituents' were the first 20 ALPHABETICALLY. -> FIXED: TICK_EXTRA_EQ=50 (all 50).
B3 LOW volume growth unmeasured (+20-60% plausible on ~845 MB/day per box); writer capacity fine on paper. OPEN: measured at the 09:15 check.
B4 LOW Kite field assumptions (expiry '' vs None, tradingsymbols) guarded; TMPV listing asserted by config only. B5 LOW three extra master downloads at 09:00. B6 INFO run_session not unit tested. All OPEN/accepted.
## C) MOVE SCRIPT  verdict: NOT SAFE as it was
C1 HIGH sidecars (-wal/-shm) ignored; C2 HIGH open handles not checked; C3 MEDIUM DST mount not verified; C4 MEDIUM no lock; C5 LOW df failure/space names; C6 LOW moves recoverable files too (reverses H12 placement). Consumers that lose the path: dp_paths.list_epochs lists *.db in the source dir (moved epochs vanish silently), daily_segsync, puller_coverage (overflow dir is not a root), ssd_backup_gdrive (overflow backed up by nothing).
-> v3: copy-only unless ALLOW_REMOVE=1; skips symlink targets, -wal, -shm (when removing), unwritable dirs; mount check; lock dir. C2 (open-handle check) NOT fixed (fuser not available to a non-root user): removal stays disabled by default. The earlier real run (v1) is NIFTY incident T-1313: dhan_current.db / fyers_current.db dangled for minutes, restored from sha256-verified copies. Fable asks: verify every manifest entry has no orphan -wal and that the HDD copy passes integrity_check before trusting it (the 4 extra HDD copies are NOT to be trusted until that runs).
## D) DOC  (DATA_NEEDED_FOR_EDGE_031126.md)
D1 weekly appears in more need-list rows than listed + ALGOTEST_FEATURES_DATA_151026-0808.md:70 (15-10) -> FIXED in the doc. D2 Kite '25+25 strikes' unsupported (code +/-20 / +/-15) -> FIXED. D3 '26+22' is Dhan only -> FIXED. D4 '2 of 3 depth recorders' wrong: four recorders; Fyers TBT monthly-only and NOT fixed -> FIXED text, B9 added. D5 Sensex is offered but unsubscribed -> FIXED (B12).
Same-kind gaps Fable listed (all now in the doc): Fyers TBT monthly only; Dhan d200 one monthly future (owner's split not done); India VIX/index not on Dhan; next-month future only on Kite; BANKNIFTY options nowhere; breadth only on Kite; chain snapshots in dp_snap DO take the weekly (DP_SNAP_WEEKLY default 1), i.e. the snapshots were ahead of the recorders.
Still missing for the engine: GIFT NIFTY, event calendar, costs, a measured day of the new feeds.
Owner decisions Fable lists: A1 (decided: fixed), Upstox 6 vs 5 (decided: 5), constituent set (decided: all 50), whether to rerun the move script (decided: no), Fyers TBT weekly (queued B9).
```

### FILE audit_031126_NIGHT_weekly_extras_move/04_ssd_to_hdd_move_v3.sh  sha256=2785c6fd6157ac53  bytes=4180
```
#!/bin/sh
# ssd_to_hdd_move.sh - move INACTIVE big files from the SSD share to the HDD RAID volume, with proof. Kumar 03-11-2026.
# Rules (his standing rules): copy -> sha256 of source and copy -> atomic rename on the HDD volume -> only then remove the source.
# Never touches a file modified in the last MIN_AGE_H hours (an active DB), never a file under 100 MB, never overwrites.
# Leaves <name>.MOVED_TO_HDD (dest + sha256) where the file was, and appends every move to MANIFEST (sha256, bytes, src, dest, time).
#   usage: ssd_to_hdd_move.sh [--dry-run]     env: SRC=/volume2/datapullers  DST=/volume1/docker/datapullers_ssd_overflow  MIN_AGE_H=168
SRC=${SRC:-/volume2/datapullers}; DST=${DST:-/volume1/docker/datapullers_ssd_overflow}; MIN_AGE_H=${MIN_AGE_H:-168}; MIN_BYTES=${MIN_BYTES:-104857600}
MAN=$DST/MANIFEST.tsv; LOG=$DST/move.log; DRY=0; [ "$1" = "--dry-run" ] && DRY=1
# v3 (03-11-2026, after Fable audit C1-C4): COPY-ONLY unless ALLOW_REMOVE=1; the HDD volume must really be mounted; one run at a time; -shm too.
case "$DST" in /volume1/*) mountpoint -q /volume1 2>/dev/null || grep -q " /volume1 " /proc/mounts || { echo "REFUSE: /volume1 is not mounted"; exit 1; } ;; esac
mkdir -p "$DST" || exit 1
LOCK=$DST/.move.lock; mkdir "$LOCK" 2>/dev/null || { echo "REFUSE: another run holds $LOCK (rm -r it only if no run is active)"; exit 1; }
trap 'rmdir "$LOCK" 2>/dev/null' EXIT INT TERM
ALLOW_REMOVE=${ALLOW_REMOVE:-0}
log(){ echo "$(date '+%d-%m-%Y %H:%M:%S') $*" | tee -a "$LOG"; }
now=$(date +%s); moved=0; failed=0
find "$SRC" -xdev -type f -size +${MIN_BYTES}c ! -name '*.part' ! -name '*.MOVED_TO_HDD' 2>/dev/null | sort | while read -r f; do
  m=$(stat -c %Y "$f"); s=$(stat -c %s "$f"); age=$(( (now - m) / 3600 ))
  [ "$age" -lt "$MIN_AGE_H" ] && { log "SKIP active/recent (age ${age} h < $MIN_AGE_H): $f"; continue; }
  # v2 (03-11-2026 after the dhan/fyers incident): NEVER move a file that a symlink points at (*_current.db, *_raw_current.db are
  # epoch pointers read by containers that cannot follow a link into another volume), nor one with a live -wal/-shm sidecar, nor from a directory we cannot write.
  base=$(basename "$f"); dir=$(dirname "$f")
  if find "$SRC" -xdev -type l -lname "*$base" 2>/dev/null | grep -q .; then log "SKIP referenced by a symlink (epoch pointer): $f"; continue; fi
  if [ -e "$f-shm" ] && [ "$ALLOW_REMOVE" = 1 ]; then log "SKIP has a -shm sidecar (open or recently open SQLite): $f"; continue; fi
  if [ -s "$f-wal" ]; then log "SKIP has a non-empty -wal (possible unflushed data): $f"; continue; fi
  if [ ! -w "$dir" ]; then log "SKIP directory not writable by $(id -un): $dir"; continue; fi
  rel=${f#$SRC/}; dest="$DST/$rel"; [ -e "$dest" ] && { log "SKIP dest exists: $dest"; continue; }
  free=$(df -B1 "$DST" | tail -1 | awk '{print $4}'); case "$free" in ''|*[!0-9]*) log "STOP cannot read free space of $DST"; break;; esac; [ "$free" -lt $(( s * 2 + 10737418240 )) ] && { log "STOP not enough free space on HDD for $f"; break; }
  [ "$DRY" = 1 ] && { log "DRYRUN would move ${s} bytes: $f -> $dest"; continue; }
  mkdir -p "$(dirname "$dest")"
  log "COPY $f ($((s/1048576)) MB)"
  if ! nice cp -p "$f" "$dest.part"; then log "FAIL copy $f"; rm -f "$dest.part"; continue; fi
  sync
  a=$(nice sha256sum "$f" | cut -d' ' -f1); b=$(nice sha256sum "$dest.part" | cut -d' ' -f1)
  m2=$(stat -c %Y "$f")
  if [ "$a" != "$b" ] || [ "$m2" != "$m" ]; then log "FAIL verify (hash or source changed) $f src=$a copy=$b"; rm -f "$dest.part"; continue; fi
  mv "$dest.part" "$dest" || { log "FAIL rename $dest"; continue; }
  if [ "$ALLOW_REMOVE" != 1 ]; then log "COPIED-ONLY (ALLOW_REMOVE!=1, source left in place; verified copy at $dest sha256=$a)"; continue; fi
  if rm -f "$f" && [ ! -e "$f" ]; then
    printf 'moved to HDD %s\nsha256 %s\nbytes %s\nmoved %s\n' "$dest" "$a" "$s" "$(date '+%d-%m-%Y %H:%M:%S')" > "$f.MOVED_TO_HDD"
    printf '%s\t%s\t%s\t%s\t%s\n' "$a" "$s" "$f" "$dest" "$(date '+%d-%m-%Y %H:%M:%S')" >> "$MAN"
    log "MOVED $f -> $dest sha256=$a"
  else
    log "COPIED-NOT-MOVED (source could not be removed; it is still in place; extra verified copy at $dest sha256=$a)"
  fi
done
log "done"
```

### FILE audit_031126_BLK001_livewatch/33_gap_histogram_i7.csv  sha256=527a08d1fde0f81a  bytes=2947
```
recorder,conn,day,rows,max_gap_s,>60,>90,>120,>180,first,last
ticks,NIFTY,20261015,88794,11,0,0,0,0,09:19:14,15:29:59
ticks,NIFTY,20261016,89767,2,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261019,16619,2,0,0,0,0,09:15:00,10:24:34
ticks,NIFTY,20261020,33,531,32,32,32,32,09:17:41,12:20:25
ticks,NIFTY,20261021,89730,3,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261022,89564,4,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261023,89769,4,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261026,89822,7,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261027,89742,3,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261028,89711,1,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261029,87596,516,1,1,1,1,09:15:00,15:29:59
ticks,NIFTY,20261030,82358,1832,1,1,1,1,09:15:00,15:29:59
ticks,NIFTY,20261102,66477,82,2,0,0,0,09:15:00,13:58:09
ticks,NIFTY,20261103,83050,1295,2,2,2,2,09:15:00,15:29:59
depth,d20,20261019,18177,2,0,0,0,0,09:15:00,10:24:42
depth,d200,20261019,17347,2,0,0,0,0,09:15:00,10:24:42
depth,d20,20261021,93815,20,0,0,0,0,09:15:00,15:29:59
depth,d200,20261021,93586,5,0,0,0,0,09:15:00,15:29:59
depth,d20,20261022,93852,25,0,0,0,0,09:15:00,15:29:59
depth,d200,20261022,93353,9,0,0,0,0,09:15:00,15:29:59
depth,d20,20261023,94263,2,0,0,0,0,09:15:00,15:29:59
depth,d200,20261023,102712,2,0,0,0,0,09:15:00,15:29:59
depth,d20,20261027,52503,3,0,0,0,0,11:29:49,15:29:59
depth,d200,20261027,48716,3,0,0,0,0,11:29:49,15:29:59
depth,d20,20261028,82131,3,0,0,0,0,09:15:00,15:29:59
depth,d200,20261028,76349,6,0,0,0,0,09:15:00,15:29:59
depth,d20,20261029,82853,478,1,1,1,1,09:15:24,15:29:59
depth,d200,20261029,79125,479,1,1,1,1,09:15:00,15:29:59
depth,d20,20261030,75508,1852,1,1,1,1,09:15:00,15:29:59
depth,d200,20261030,70649,1858,1,1,1,1,09:15:00,15:29:59
depth,d20,20261102,61864,26,0,0,0,0,09:15:45,13:57:56
depth,d200,20261102,57395,15,0,0,0,0,09:15:00,13:57:56
depth,d20,20261103,79920,1310,3,3,3,3,09:15:00,15:29:59
depth,d200,20261103,69880,1310,2,2,2,2,09:15:00,15:29:59
upstox_live,frames,20261019,13602,2,0,0,0,0,09:50:49,10:24:49
upstox_live,frames,20261020,282,245,93,93,93,93,09:16:19,15:28:18
upstox_live,frames,20261021,149996,4,0,0,0,0,09:15:00,15:29:59
upstox_live,frames,20261022,149998,2,0,0,0,0,09:15:00,15:29:59
upstox_live,frames,20261023,150014,2,0,0,0,0,09:15:00,15:29:59
upstox_live,frames,20261026,150021,7,0,0,0,0,09:15:00,15:29:59
upstox_live,frames,20261027,150020,3,0,0,0,0,09:15:00,15:29:59
upstox_live,frames,20261028,150012,4,0,0,0,0,09:15:00,15:29:59
upstox_live,frames,20261029,146883,471,1,1,1,1,09:15:00,15:29:59
upstox_live,frames,20261030,137668,1826,1,1,1,1,09:15:00,15:29:59
upstox_live,frames,20261102,113152,4,0,0,0,0,09:15:00,13:57:54
upstox_live,frames,20261103,127376,1348,2,2,2,2,09:15:00,15:29:59
fyers_tbt,frames,20261020,52,246,51,51,51,51,12:03:55,15:27:51
fyers_tbt,frames,20261027,6334,1,0,0,0,0,14:59:27,15:29:59
fyers_tbt,frames,20261028,41761,3,0,0,0,0,12:21:38,15:29:59
fyers_tbt,frames,20261103,71027,1381,2,2,2,2,09:15:00,15:29:59
```

### FILE audit_031126_BLK001_livewatch/32_gap_histogram_i5_PARTIAL.csv  sha256=40dc8a93d4092bcb  bytes=1167
```
recorder,conn,day,rows,max_gap_s,>60,>90,>120,>180,first,last
ticks,NIFTY,20261015,88985,11,0,0,0,0,09:18:06,15:29:59
ticks,NIFTY,20261016,89784,1,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261019,89648,2,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261020,33,382,32,32,32,32,09:16:48,12:15:35
ticks,NIFTY,20261021,89702,2,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261022,89726,4,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261023,89745,3,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261026,89619,7,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261027,87869,1,0,0,0,0,09:22:19,15:29:59
ticks,NIFTY,20261028,89748,4,0,0,0,0,09:15:00,15:29:59
ticks,NIFTY,20261029,86820,709,1,1,1,1,09:15:00,15:29:59
ticks,NIFTY,20261030,82284,1844,1,1,1,1,09:15:00,15:29:59
ticks,NIFTY,20261102,88396,235,1,1,1,1,09:15:00,15:29:59
ticks,NIFTY,20261103,84142,1049,2,2,2,2,09:15:00,15:29:59
depth,d20,20261016,94477,4,0,0,0,0,09:15:00,15:29:59
depth,d200,20261016,96770,2,0,0,0,0,09:15:00,15:29:59
depth,d20,20261019,95504,8,0,0,0,0,09:15:00,15:29:59
depth,d200,20261019,93305,6,0,0,0,0,09:15:00,15:29:59
depth,d20,20261021,94009,3,0,0,0,0,09:15:00,15:29:59
depth,d200,20261021,94592,4,0,0,0,0,09:15:00,15:29:59
```

### FILE AUDITOR_RESPONSES/20261103_FABLE_NIGHT_REREVIEW_CONDENSED.md  sha256=8ab7e0a58809593b  bytes=2191
```
# Fable re-review of the night fixes, 04-11-2026 ~00:30 IST (condensed by the author; every verdict and defect kept)
Tests Fable ran: weekly 18/18, tick extras 8/8. Slot simulation for 03-11, 04-11, 17-11, 18-11, 23-11, 24-11, 25-11, 01-12 (Dhan 6/5, Upstox 5/5, cap 50): Dhan always 48 slots, Upstox always 47 keys, 0 duplicates, never over cap; in 18-23 Nov the EXPIRING monthly gets 26 and next week's weekly 22. Correction: the November monthly is 2026-11-23 (24-11 is a holiday), not 24-11.
A1 FIXED. A2 FIXED (the new Upstox test only asserts <=50 and would not catch a return to 6: weak). A3 (no holiday calendar in depth/upstox) still OPEN: on 24-11 both open sockets on a holiday.
B1 FIXED (macro off, no CDS/MCX call). B2 FIXED BUT NEW DEFECT (medium, silent): the tickrec container copies only /src/dp_tickrec.py to /app, so nifty50_syms.txt was absent and the constituents would have been 0 on 04-11 with no error. -> FIXED by the author (entrypoint copies both files; _eq_syms reads /src; empty list reported; test + container proof, see 10_weekly_deploy_raw.txt).
Volume: Fable now estimates 50 liquid equities add 1.5-5M rows/day, i.e. +70-200% on ~845 MB/day (earlier +20-60% was optimistic). tickrec has NO free-space guard (depth/upstox have MIN_FREE_GB): check /volume1 free GB before 09:15 and queue/dropped at 09:30. OPEN.
C move script v3: default copy-only cannot damage the source (sandbox proof); residuals: df failure let the copy proceed (FIXED by the author: STOP on unreadable free space), copy-only still copies OPEN databases and logs 'verified copy' (not an integrity check; not in MANIFEST), `sync` flushes every filesystem (never run in session), symlink scan only under SRC, C2 open-handle check unfixed -> NOT SAFE with ALLOW_REMOVE=1; SAFE WITH CONDITIONS copy-only, out of session.
D doc: stale lines corrected by the author (UPSTOX 6->5, nifty50_syms deployment wording, 18-23 Nov, dp_snap mention; whether dp_snap runs on the boxes is UNKNOWN, it is not in the compose file).
Verdicts: A SAFE FOR 04-11; B SAFE WITH CONDITIONS (verify count of extra:constituent rows = 50 at 09:16, disk and queue at 09:30); C SAFE WITH CONDITIONS copy-only; D fixed.
```

### FILE audit_031126_BLK001_livewatch/34_direct_cf_routes_tested.txt  sha256=e297206f5821a973  bytes=1061
```
DIRECT CLOUDFLARE ROUTES TESTED 04-11-2026 00:00 IST from the cloud sandbox (hostnames suggested by the owner's other session, owner confirmed); my existing Access service-token proxy and key, nothing from the message executed
sshi5.<domain> as roopeshkumarb -> i5-4590-dsm72 | up 11:16 | load 38
sshi7.<domain> as roopeshkumarb -> I7-3RD-exJ1800 | up 11:16 | load 14  (FIRST direct Cloudflare route to the i7; the old sshj1800 hostname still returns Bad Gateway)
sshha.<domain> as root -> a0d7b954-ssh (Pi) | up 5:07 (it had been up 2 d 22 h at 13:40: the Pi restarted ~18:50 IST, cause UNKNOWN)
Not tested: the jump aliases sshi5via7 / sshhavia7 named in the message (not in this sandbox's ssh config; the setup script path /home/user/Node-Hardware-Home does not exist here). Which connector/tunnel serves sshi7 and whether it survives the i5 tunnel being down: UNKNOWN.

HTTPS check 04-11 00:10 IST: sshha / sshi5 / sshi7 -> HTTP 302 to the Cloudflare Access login; sshj1800 and sshpi -> no HTTP response (hostnames gone). box_reach.sh no longer tries them.
```

### FILE audit_031126_BLK001_livewatch/35_restart_policy_always.txt  sha256=84655d2b9db76895  bytes=1258
```
RESTART POLICY CHANGE, 04-11-2026 00:30 IST, i5 and i7 (read-only inspection before, docker update after)
Before: every recorder/puller container had RestartPolicy 'unless-stopped' (inspect). After the 03-11 12:08 and 12:42 power losses they stayed down until started by hand.
Hypothesis (UNPROVEN): the NAS shutdown stops containers like a manual 'docker stop', and 'unless-stopped' does not restart those after the daemon comes back; 'always' does.
Applied: docker update --restart=always on broker_login, pull_lease_ctl, tickrec, depthrec, upstoxrec, fyerstbt, dp_guard, fullpuller, puller930, dp_voter (all present on both boxes; inspect shows 'always' after; i7 dp_voter was already exited and stays so). NOT touched: cloudflared, portainer, blpro_09, watchtower and every unrelated container.
Compose: restart: always added to broker_login, dp_voter, fullpuller, puller930, tickrec, depthrec, upstoxrec, fyerstbt (pull_lease_ctl and dp_guard are not in this compose: their setting lives only in the container until whatever created them recreates them). Compose deployed to both boxes (md5 checked), no container recreated.
Proof still missing: a real reboot or Docker restart at a quiet time. Not done tonight because the market opens in a few hours.
```

### FILE audit_031126_BLK001_livewatch/36_home_connect_tested.txt  sha256=2e712e581e208ef1  bytes=1119
```
tools/home_connect.sh tested 04-11-2026 ~01:10 IST from the cloud sandbox (outside the LAN) with the existing Access service-token proxy; hostnames are aliases here.
Jump via i5 and via i7: every SOCKS CONNECT refused; ssh log: 'channel N: open failed: administratively prohibited' (Synology default, cannot be changed without root).
Jump via Pi (root, sshha): SOCKS5 CONNECT to 192.168.2.130:8123 -> HTTP/1.0 200 OK; 192.168.2.91:22 and 192.168.2.100:22 -> SSH-2.0-OpenSSH_8.2 banners; 192.168.2.130:22 -> SSH-2.0-OpenSSH_10.3. (Plain HTTP port 5000 on the NAS boxes: no reply; DSM uses https 5001.)
Script 'up' via the Pi: status shows the three ssh banners through the proxy; local forward 127.0.0.1:8123 -> HA HTTP 200; 127.0.0.1:5101 (DSM i5) and :5102 (DSM i7) over TLS -> HTTP/1.1 200 OK; 'down' closes it.
Artifact: an earlier curl test of http://192.168.2.1 returned 403: that came from the sandbox's own egress proxy, NOT from the home router; ignore it.
Defects found and fixed while testing: ssh -f held the terminal's output open (now -E logfile); status used a fragile nc call (now a python SOCKS probe).
```
