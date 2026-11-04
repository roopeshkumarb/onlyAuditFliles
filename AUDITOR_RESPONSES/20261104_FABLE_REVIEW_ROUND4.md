# FABLE REVIEW ROUND 4, 04-11-2026 (independent, read-only, report/pull-status-081026 @ bca7446f)

Scope: guard and builder with tests. Five pack test files: **141 passed**. Attacks ran on a `git archive` copy with its own git; repo untouched apart from this file. Line numbers are mine.

## Round-3 defects

| # | Status | Opened |
|---|---|---|
| 1 normalisation/duplicates | FIXED | `:384-386`, `:529-534`; G19/G20 re-run CAUGHT |
| 2 symlinks | FIXED | `:402-408`, `:428-430`; tests `:461-500`; G17 CAUGHT |
| 3 substring, 40 bytes | PARTLY | `:73,:75-80`; README `:74` states the limit; but new 2 |
| 4 no external anchor | PARTLY, disclosed | `:472-497` three local anchors; T8 |
| 5 BN1/BN3 untested | FIXED | tests `:502-541`; BN1/BN3 re-run CAUGHT |
| 6 absent folders | FIXED | `:73`; test `:391` |
| 7, 8 | out of scope this round |

## New mutants (not in MUTATION_LOG)

| ID | Mutation | Result |
|---|---|---|
| GN5 | `:611` two new flags per accept | SURVIVED |
| GN6 | `:485` report anchor by length only | SURVIVED |
| GN7 | `:494` HEAD chain by length only | SURVIVED |
| GN8 | `:79` prose minimum 1 | CAUGHT |
| BN5 | `:72` SRC_ORDER rank case-sensitive | SURVIVED |
| BN6 | `:536` stat guard size only | CAUGHT |
| BN7 | `:231` sha256 of first 8 MB only | SURVIVED |
| BN8 | `:566` REFUSED exits 0 | CAUGHT |

## Gate attacks (scratch copy, real git)

| Trick | Result |
|---|---|
| T2 evidence in one commit, three accepts, **one** commit | **PASSES**, 1 of 6 DONE |
| T3 commit a benign draft, write the APPROVAL text uncommitted, flip, accept | **PASSES** |
| T4 APPROVAL line inside a ``` fence in a "not final" draft | **PASSES** |
| T4 lowercase, tabs, `./`, backslash / quote, comment, NBSP, BOM, trailing text, homoglyph | pass / refused |
| T4 CRLF (Notepad) | refused with a misleading message |
| T4 "I withdraw this approval" appended | PASSES (`:82`) |
| T5 Cyrillic-i ledger row + copied file | PASSES: 1 of 7, real row untouched |
| T6 amend after accept / T7 evidence replaced after accept | passes (disclosed) / CAUGHT |
| T8 revoke, drop tail, recompute `anchor`, delete `guard_report.json`, commit | **PASSES**: revocation erased |

## Builder fault injection

12 random SIGKILLs (mid-row, between units, double): converged with a clean build, sources byte-identical. Corrupt source refused. Disk full (RLIMIT_FSIZE): nothing published, clean resume. Read-only output dir as `nobody`: nothing left. No invented broker: BLOB/INTEGER `src`, `upstox+` give `UNKNOWN_HISTORICAL`.

## New defects

1. `requirements_guard.py:614-622`: accept checks only that the evidence *path* exists in HEAD, not its content, and not that the previous chain entry is committed. T2/T3 falsify `:35-36` and README `:74`. Fix: compare HEAD's evidence sha with the recorded one; refuse when HEAD's state file differs from disk.
2. `:80, :447-448`: a fenced template line is an approval (T4). Ignore fenced lines or require it first.
3. `:443`: CR not stripped; Windows sign-offs refused with the wrong reason.
4. `:468-469`: missing `guard_report.json` silently drops an anchor (T8).
5. `retailer_db_build.py:228-233, :256-258, :536`: a WAL source (niftybkp.db is WAL) is read *with* its `-wal` but hashed and stat-checked *without*: WAL-only appends give `UP_TO_DATE` with stale rows, `source_sha256` excludes copied rows, `:223` creates `-shm` beside the source, a read-only medium is refused. Refuse non-empty `-wal`; hash main+wal.
6. `:359-361`: a failed COMMIT raises "cannot rollback", masking disk-full.
7. `:536`: size+mtime defeated by `utime` or coarse-mtime media (exFAT, SMB); published `source_sha256` then mismatches disk. Re-hash at the end.
8. `:541-546`: kill between the two `os.replace` leaves the final path empty; the rerun discards the COMPLETE scratch (`:447`).
9. By inspection: `:464-467` no lock on Windows; `:262` directory `os.open` fails on Windows, stranding `--replace`. `src_rank` `:65` dead.

## Verdicts

| Tool | Verdict | Sign today? |
|---|---|---|
| `retailer_db_build.py` + tests | PASS-WITH-FIXES | Yes for Linux, synthetic data, journal-mode sources, with the ledger note's wording. **No** for WAL sources until 5 is fixed and tested. Power-cut durability unproven. |
| `requirements_guard.py` + ledger + chain | PASS as accident check; **FAIL as a gate** | No: its central claim (commits in sequence, evidence first) is false (1). After 1-3 are fixed with tests for T2, T3, fence, CRLF, I would sign it as an accident check only. |

Residual: all anchors are local; one writer editing ledger, chain, report and history together passes (T8). Unicode paths unnormalised (T5). Not verifiable here: boxes, Windows, real `niftybkp.db`, fsync under power loss.
