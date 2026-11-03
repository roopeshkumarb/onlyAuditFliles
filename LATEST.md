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
