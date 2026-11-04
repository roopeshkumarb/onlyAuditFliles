# FABLE REVIEW ROUND 3, 04-11-2026 (independent, read-only, branch report/pull-status-081026 @ 280fc8ce)

Re-derived from the checkout. Tests ran in place with `-p no:cacheprovider`; every mutation and gate attack ran on `git archive`/`copytree` copies in the scratchpad. Repo untouched apart from this file. No box, `.env` or live DB.

## Round-2 defects

| # | Status | Evidence opened |
|---|---|---|
| 1 G1-G3 survive | FIXED | re-ran G1, G3: CAUGHT (`test_attack_evidence_file_missing`, `ExitCode::test_alert_gives_exit_1`) |
| 2 flips with "ok"/CLAUDE.md/deleted row | FIXED for those (`requirements_guard.py:361-391`, `:425-427`; G6, G9, G11 CAUGHT); gate still flips, see new 1-4 |
| 3 TRACE gameable | NOT FIXED, disclosed (`:568-604` unchanged; C-055b, README 3.11) |
| 4 B1/B2 survive | FIXED (`tests/test_retailer_db_build.py:446-479`; B1, B2 CAUGHT) |
| 5 no build lock | FIXED (`retailer_db_build.py:461-469`; test `:481-494`; B16 CAUGHT) |
| 6 placement collects 0 | FIXED (3 collected; 117 passed = 56+6+27+25+3) |
| 7 CSV LF-normalised | FIXED (`REDACTIONS.txt` item 2) |
| 8 `j1800` undeclared | NOT FIXED (343 hits in pack census); trivial |
| README C1 / 3.8 / C-054 | FIXED (`:19` GAP rows cite `DATA_NEEDED_FOR_EDGE_031126.md:41` = the B12 line; `:35`; C-054 RETRACTED) |

## Mutations

Re-ran 12 of 33 logged: G1, G3, G6, G9, G11, G14, G15, B1, B2, B16 CAUGHT; B11, B12 SURVIVED, as logged. Eight of mine:

| ID | Mutation | Result |
|---|---|---|
| GN1 | drop realpath containment `:379` | SURVIVED |
| GN2 | DONE without chain acceptance `:457` | CAUGHT |
| GN3 | `EVIDENCE_DIRS = ("docs/",)` `:64` | SURVIVED |
| GN4 | removed-row loop skipped `:424` | CAUGHT |
| BN1 | output may be its own source `:483` | SURVIVED |
| BN2 | resume any scratch, ignore plan `:501` | CAUGHT |
| BN3 | duplicate source labels `:477` | SURVIVED |
| BN4 | conflict reason swapped `:350` | CAUGHT |

## Gate attacks (scratch copy of the real repo)

| Trick | Result |
|---|---|
| A. all three `_evidence = docs/audit_pack_041126/README.md` + sha, then `--accept-state` | **PASSES**: 0 ALERT, 1 of 6 DONE. No new file needed |
| B. symlink in pack dir -> `../framework/FABLE_REVIEW_041126.md` | **PASSES** |
| B2. symlink outside repo; C. `artifacts/`; D. empty file | refused |
| D2. 40-byte file = path + 14 spaces | **PASSES** |
| E. approve+accept, revoke+accept, delete last entry, re-flip | **PASSES**: revocation erased |
| F1-F3. trailing space / `./` / `//` in path | refused |
| F4. extra row `./tools/retailer_db_build.py` beside the real one | **PASSES**: 1 of 7 DONE |
| G. new `docs/audit_responses/` file saying "NOT approved" | **PASSES** |

## New defects

1. `:423-428` no path normalisation or duplicate-row refusal (F4). Fix: `normpath` + uniqueness.
2. `:379` accepts symlinks to anything inside the repo (B, GN1). Fix: refuse `islink`, add a test.
3. `:389` substring "names the build" and `MIN_EVIDENCE_BYTES = 40` `:69` are satisfied by any pack doc, a "NOT approved" note, or path+padding (A, D2, G). README 5 must say plainly: one person with repo write approves any build in two commands.
4. `_verify_chain` `:352-358` has no external anchor; tail deletion un-revokes (E). LEDGER_CORRECTIONS names tail deletion, not this consequence.
5. Builder guards `:483` and `:477` untested (BN1, BN3).
6. `:64` allow-lists two folders absent from the repo; list untested (GN3).
7. Public repo: LAN addresses `<LAN>.2.1/.91/.100/.130` in `README.md:614,1669`, `12_ACCESS_ROUTES.md:32`, `17_access_routes_raw.txt:17-18`, `36_home_connect_tested.txt:3-5`, plus labels `sshi5/sshi7/sshha/sshpi/sshj1800`; the round-5 pack redacts that prefix and `12_ACCESS_ROUTES.md:2` says "aliases only". Pre-existing, private range. No tokens, emails, public hostnames; `api_key` hits are variable names.
8. `LATEST.md:1` "~12:30" and `:4` "Fable round 2 PENDING" stale against `:2`.

## Numbers checked

C-054b: 27 tests, 33 tried, 17 builder (B1, B1b, B2-B16), 15/2, flock: supported. C-055b: 56 tests (the 57th `def test_` grep is a fixture string), 16 mutants, 0 ALERT, 0 of 6: supported (G2/G3 are not strictly gate breaks). CHANGELOG 31/2 and LATEST 12/2 match my round-2 table. Public `SHA256SUMS` 124/124, pack `MANIFEST.sha256` 27/27, public pack byte-identical to repo pack, artifacts identical to repo files. CSV 183 = 85/94/4, 0 rows without `:digits`. Join: 36 tables, 19 REC / 17 NON, 0 UNKNOWN, every chain/quote/marker table NON; `vix_1m`, `equity_1m`, `sector_1m` REC remain pack Q2.

## Verdicts and signature

| Artifact | Verdict | Sign Fable approval today? |
|---|---|---|
| DATA_NEEDED_INSTRUMENTS md+csv | PASS | yes |
| LIVE_CENSUS, RETAILER_PULLER_DESIGN | PASS (unchanged) | yes, census as one snapshot |
| recoverability.json + dp_recoverability.py | PASS | yes |
| retailer_db_build.py + tests | PASS-WITH-FIXES | after BN1/BN3 tests; evidence must say "sandbox only, power-cut durability unproven" |
| requirements_guard.py + ledger + chain | PASS-WITH-FIXES as accident check; **FAIL if called a gate** | no, until 1 and 2 are fixed with tests and README 5 states the two-command limit |
| Pack README, C-054b/C-055b, LATEST/CHANGELOG | PASS-WITH-FIXES | after 7, 8 and a `j1800` line |

Not verifiable here: boxes, `.env`, real `niftybkp.db`, whether the 12:07 TRACE notes reflect work, fsync under power loss, C-052 beyond arithmetic, the Cloudflare side of the hostnames.
