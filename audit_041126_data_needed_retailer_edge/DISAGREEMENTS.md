# Disagreements and fixes - Fable-model review of 04-11-2026

Source: `artifacts/docs/framework/FABLE_REVIEW_041126.md` (verdict PASS-WITH-FIXES on all five artifacts).
"Fix commit" is where the change landed on branch `report/pull-status-081026`. "Re-verified" says whether
anyone other than the fixer has checked the fix; where it says *not yet*, the second Fable pass and the
external auditor are the ones who must. Nothing here is an approval.

| # | Fable finding (short) | What was changed | Fix commit | Still open? |
|---|---|---|---|---|
| 1 | `global_1m` marked RECOVERABLE, but Yahoo serves only ~7 days per request / ~30 days at all, so older rows could wrongly go to SSD | Moved to new class `window_limited_intraday` (NON_RECOVERABLE) until proven | fa774a41 | Closed. Re-class to RECOVERABLE only after a per-broker window probe (not done). |
| 2 | `ohlc` pattern made `opt_ohlc_1m` RECOVERABLE although some rows are live-built (SRC_ORDER has `upstox_live`) | `opt_ohlc_1m` added to the same protected class | fa774a41 | Closed for placement; the real per-broker window is still UNKNOWN. |
| 3 | CSV header misaligned: evidence in the wrong column, `why_needed_for_regime` empty on 171/183 rows | Generator argument order fixed; 183/183 rows now have a reason and a citation | d546abf9 | Closed. Checked by `tests/test_gen_data_needed_instruments.py`; re-verified by this pack's author only. |
| 4 | 24 WORLD_MARKETS rows cited `MARKER-NOT-FOUND`; 6 NSE-report and 2 GAP rows had no cite | Real cites found or UNKNOWN with query; marker count now 0 | d546abf9 | Closed (test asserts 0 markers). |
| 5 | Dhan broker-count row recomputed under no stated rule | Single counting rule stated in the MD (a token must start with the broker name) | d546abf9 | Closed; not re-verified by Fable yet. |
| 6 | 5 rows with store name `upstox_YYYYMMDD.db` classed LIVE_ONLY although `classify()` on that literal returns UNKNOWN | Not a logic change: MD now explains a sample date is substituted before classifying | d546abf9 | **Open by design.** The literal-name classification is still UNKNOWN; real day files carry a date and classify correctly (`tools/check_recoverability_placement.py`). |
| 7 | Census "259 / 269 distinct names" were (broker,name) pairs; true figure 236 / 246 | Census text corrected with the recompute recipe | d546abf9 | Closed. |
| 8 | Design doc called weekly recording OFF; the census proves it ON on both boxes | Sections 2.1, 2.2, 2.3, 7 corrected (Dhan 49, Upstox 47; compose default noted) | 028baa63 | Closed. |
| 9 | `MINT_POLICY` cited to `dp_quorum.py`; it is `broker_login/login_engine.py:50` | Cite corrected | 028baa63 | Closed. |
| 10 | `global_1m` does have a collector (`download_yahoo`); several compose line cites wrong; NSE reports filed under Fyers; "09:35 check" mis-cited | Corrected; `download_yahoo` at `:1012` cited | 028baa63 | **Partly open.** The fixer says cites it did not change were not re-verified. |
| 11 | "Mover skips anything younger than 168 h" is a default, not a fact | Wording changed to default, env-overridable; G2 still stands | 028baa63 | Closed. |
| 12 | Builder: SIGKILL mid-transaction left a hot journal; "resumes" claim overstated; orphan journal | Resume probe rolls the journal back; scratch removal deletes -journal/-wal/-shm; new real-SIGKILL test | a54e97f8 | Closed in sandbox. Final fsync cannot be tested without a real power cut. |
| 13 | Builder: duplicate key with two different `src` resolved by scan order, not SRC_ORDER | Ranked by SRC_ORDER; losers go to `_build_conflicts` and `rows_conflict`; across sources first source wins (recorded) | a54e97f8 | **Open:** whether the real archive has such collisions is UNKNOWN. The cross-source rule is a choice (question Q8). |
| 14 | Tests missed two mutants (stat-guard removed; NULL broker -> "kite") | Added `test_source_moving_during_the_build_publishes_nothing` and `test_null_or_blank_bars_broker_is_unknown_never_a_vendor` | a54e97f8, efec1757 | Closed per the fixer's mutation report (11 of 12 caught); not re-run independently. |

## Round 3 (Fable, 04-11-2026) - what was found and what was changed (report: docs/framework/FABLE_REVIEW_ROUND3_041126.md)

Round 2's 14 defects: 7 FIXED, 2 NOT FIXED at the time (TRACE gameability: still disclosed, not fixed; the `j1800` alias: now declared in REDACTIONS.txt item 3). Round 3 then attacked the hardened gate and found it still flipped. All below are fixed in the working tree and awaiting a round-4 re-check; none is an approval.

| # | Round-3 finding | What was changed | Still open? |
|---|---|---|---|
| N1 | No path normalisation / duplicate-row refusal: an extra row `./tools/retailer_db_build.py` beside the real one gave "1 of 7 DONE" | Build paths normalised (strip, normpath, casefold); a duplicate row is an ALERT and blocks every DONE; test covers 5 spellings | Closed in tests; Fable re-check pending |
| N2 | Symlinks inside the evidence folder were accepted (a link to a framework doc passed) | Any symlink in the evidence path is refused with its own message; test covers a file link, a directory link and a link outside the repo. The old realpath-containment check is now an equivalent mutant (MUTATION_LOG G18) | Closed |
| N3 | `names the build` was a substring test and `MIN_EVIDENCE_BYTES=40` was satisfied by path+padding; the pack README plus its sha flipped all three flags in two commands | Evidence must live in `docs/approvals_evidence/` only (never a README), contain `APPROVAL <flag> APPROVES <build>` for that flag and build, 20+ prose words, no not-approved/rejected/FAIL line; `--accept-state` takes ONE newly-true flag per call and needs the evidence already in git HEAD, and refuses any true flag when git history is unreadable | Closed in tests. **Residual, stated in README 5: one person with write access can still write the file and approve all three flags in three visible commits.** |
| N4 | Deleting the tail of the chain silently un-revoked an approval | Chain head anchored in the state file, in `guard_report.json` `anchor_history`, and compared with git HEAD's copy; each deletion variant is an ALERT with its own test | Closed in tests; rewriting all of it together passes a local guard (stated) |
| N5 | Builder guards for "output may not be its own source" and "duplicate source labels" had no test (mutants BN1, BN3 survived) | Five tests (output file, scratch file, relative spelling, duplicate labels, empty sources); BN1/BN1b/BN3/BN3b all CAUGHT | Closed |
| N6 | `EVIDENCE_DIRS` allow-listed two folders that do not exist, untested (mutant GN3) | Reduced to the one real folder; test asserts the tuple and refuses six other locations | Closed |
| N7 | Public repo holds LAN addresses and Cloudflare hostname labels in older rounds | Not changed: pre-existing, private range, older rounds; the round-5 pack redacts that prefix and says so | OPEN - owner decision whether to rewrite older rounds |
| N8 | Public LATEST.md lines 1 and 4 stale | Exact replacement lines in PUBLIC_LATEST_REPLACEMENT.md; public repo untouched | OPEN until published |

Mutation totals after round 3: 53 tried, 50 caught, 3 survived (two fsync mutants that need a real power cut, one equivalent mutant). See MUTATION_LOG.txt.


## Round 4 (Fable, 04-11-2026, report FABLE_REVIEW_ROUND4_041126.md) - findings and what was done

| # | Finding | Fix | Status |
|---|---|---|---|
| R4-1 | `--accept-state` checked only that the evidence PATH was in git HEAD, so three accepts in one working tree could be committed together, and a benign draft could be swapped for the real text after being committed | accepts count newly-true flags against the last entry COMMITTED at HEAD; the previous accepted entry must be committed first; HEAD's copy of the evidence must hash to the recorded sha256; the report ALERTs on several uncommitted entries or several flags newly true against HEAD | FIXED (tests t2, t2b, t2c, t3, gn5) |
| R4-2 | an APPROVAL line inside a code fence, or a document saying "withdrawn / draft / do not treat as final", counted | fenced text ignored (an unclosed fence swallows the rest, fenced prose does not count toward the minimum); withdrawn / draft / template / not-final / placeholder / revoked lines refuse the evidence | FIXED (tests t4, t4b, t4c, t4d) |
| R4-3 | CRLF (Windows) responses refused with a misleading reason | text folded (BOM, CRLF, CR) before matching; sha256 still on the raw bytes | FIXED (crlf and bom tests) |
| R4-4 | deleting the chain tail, recomputing the anchor and deleting `guard_report.json` erased a revocation | the chain must extend every earlier COMMITTED version of the state file (git log); a committed `guard_report.json` that vanishes is an ALERT | FIXED against an honest history; a force-push or a full history rewrite still passes (stated in the guard docstring and README section 5) |
| R4-5 | builder read a WAL source with its -wal but hashed and stat-checked without it: false UP_TO_DATE, `source_sha256` missing copied rows, a `-shm` created beside the source, read-only media refused | WAL sources are byte-copied (main + -wal, hashed while copied, source unchanged across the copy or VerifyFailed after 3 tries) into a private snapshot and built from that; `source_sha256` = sha256 of "main:<sha>\|wal:<sha or ->"; nothing is ever opened through SQLite beside the source | FIXED (7 WAL tests with real uncheckpointed -wal fixtures, including a power-cut-style main+wal copy and a moving source) |
| R4-6 | a failed COMMIT (disk full) was masked by "cannot rollback" | ROLLBACK only when a transaction is open, and never allowed to replace the original error | FIXED (test with a connection whose COMMIT fails) |
| R4-7 | size+mtime guard defeated by `utime()` or a coarse-mtime medium; the 8 MB-only hash mutant survived | full content re-hash at the end for journal-mode sources; hash covers the whole file (20 MB test, change beyond 8 MB) | FIXED (B7b and BN7 caught) |
| R4-8 | a kill between the two `os.replace` calls left the final path empty and the rerun discarded the COMPLETE scratch | the old output is kept by hard link (rename-aside only where links are unavailable), the scratch is marked COMPLETE for the plan and the rerun verifies and publishes it (status PUBLISHED_FROM_SCRATCH); kept copies get unique names | FIXED (real SIGKILL tests with and without links) |
| R4-9 | no lock on Windows, directory fsync fails on Windows; `src_rank` unused | directory fsync skipped on Windows and durability explicitly not claimed there; `src_rank` is now cross-checked against the SQL rank in a test | DISCLOSED, not testable here |
| R4-M | 5 of 8 fresh mutants survived (GN5, GN6, GN7, BN5, BN7) | one test each; plus one mutation per new rule; one dominated check deleted instead of keeping an unkillable mutant (G38) | FIXED: 84 mutations, 80 caught, 4 survive (B11, B12 power-cut; B7, G18 equivalent) |

Mutation totals after round 4: 84 tried, 80 caught, 4 survived. See MUTATION_LOG.txt. Tests: 174 passed, 1 skipped (a read-only-directory test that root cannot run).

## Where reviewers have not yet disagreed

* No external auditor has reviewed anything yet, so there are **no external findings to show**. Their reply will be added here beside Fable's.
* The Fable-model reviewer and the author share an operator, so agreement between them is weak evidence. Question list: README section 6.

## Findings Fable listed as UNKNOWN or unverifiable (carried forward unchanged)

Real `opt_chain_1m` key and duplicate-supplier collisions; per-broker `recoverable_until`; box `.env` beyond what the census implies; whether `dp_snap` runs; which compose starts the recorders on i7; whether any live file sits under the i5/i7 SSD volume; `rows_raw` datasets per box; the CLAUDE.md path `data/event_calendar.yaml` versus the repo's `config/event_calendar.json`; every number taken from the live census is an agent's self-report.
