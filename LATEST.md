# LATEST: open for verification (updated 05-11-2026 night IST; newest first)
## ROUND 6 FINAL PACK (05-11 night): audit_051126_data_needed_v2/FINAL_AUDIT_PACK_ONE_FILE_051126.md = list + Opus R1 + Opus R2 + Fable in ONE file. The older AUDIT_PACK_ONE_FILE_051126.txt is SUPERSEDED (it predates the R2 audit and the gaps G1-G7).
## ROUND 6 (05-11 night): is the data-needed list COMPLETE for the intraday directional engine? | AWAITING AUDITORS
Start with audit_051126_data_needed_v2/README.md. Opus audit found the list incomplete (6 groups of inputs missing); 9 rows added, fix not re-audited. Questions inside. Nothing is deployed on any puller because of this list; a stop-pulling policy waits for audit + external audit + owner.
## ROUND 5 UPDATE 4 (04-11 night): Fable rounds 4-8 and plan rounds 1-6 published (AUDITOR_RESPONSES/20261104_FABLE_*). Plan approved by Fable round 6 AS A GOVERNING DOCUMENT ONLY (C-058); CLAUDE.md 2.2 live+nightly PASS (C-057); the live-board collector could mislead and was fixed (C-056, C-059). NO build is approved for deploy: Fable would sign scoped items (builder Linux ext4/btrfs, seal copy-only, compose Kite-only shadow), external auditor PENDING, owner PENDING.

## ROUND 5 (04-11 day) - UPDATED after Fable round 2 (report: AUDITOR_RESPONSES/20261104_FABLE_DATA_NEEDED_REVIEW_ROUND2.md): 12 of 14 round-1 findings FIXED, 2 partly; the guard FAILED as an approvals gate and was hardened; C-054 and C-055 RETRACTED and replaced by C-054b / C-055b. Fable round 3 PENDING. Fable round 3 done (AUDITOR_RESPONSES/20261104_FABLE_DATA_NEEDED_REVIEW_ROUND3.md): PASS for instrument list, census, puller design, recoverability config; builder and guard PASS-WITH-FIXES - fixed since, need a round 4 re-check.
## ROUND 5 (04-11 day): data-needed list per instrument, live census, retailer DB builder, guard
Start with audit_041126_data_needed_retailer_edge/README.md (what is claimed, what is NOT proven, 10 questions) and DISAGREEMENTS.md (all 14 Fable round-1 findings and their fixes). Fable round-1 report: AUDITOR_RESPONSES/20261104_FABLE_DATA_NEEDED_REVIEW_ROUND1.md. Claims C-051..C-055. Approvals: Fable has reviewed three times (r1 PASS-WITH-FIXES 14 findings; r2 guard FAIL as a gate; r3 PASS for list/census/design/config, PASS-WITH-FIXES for builder and guard) - NONE of that is an approval in the ledger. External auditor PENDING. Owner PENDING. Nothing is called done.
### R5-1 | which instruments are live-only vs pullable, per broker | NOT PROVEN
Evidence: artifacts/docs/framework/data_needed_instruments_041126.csv + LIVE_CENSUS_041126.csv. Open: broker symbol cells UNKNOWN; GIFT NIFTY live is recorded nowhere; USDINR daily, BANKNIFTY options, Sensex F&O unrecorded. Auditor: is the live-only/pullable split right for an intraday regime+direction edge? Which table is misclassified?
### R5-2 | N-1 first live proof | census shows weekly expiry recording ON on both boxes (Dhan 49, Upstox 47)
### R5-3 | retailer_db_build.py | sandbox-tested, never run on real data. Try to corrupt a source or invent a broker stamp.
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
