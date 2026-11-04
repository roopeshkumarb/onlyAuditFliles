# External audit pack - retailer_db_edge data-needed list (04-11-2026)

Prepared by Claude Code for Kumar, who will hand it to an outside auditor. Built on top of commit `2ba212fe`
on branch `report/pull-status-081026` (repo `roopeshkumarb/blpro`); the commit that adds this pack is the branch tip to audit. The pack is a copy; nothing was moved.

## 1. What this is, in plain words

Kumar is a retail trader building a database ("retailer_db_edge") to look for an intraday NIFTY 50 edge.
Before building new data pullers he wants one list: every instrument the engine needs, which of the four
paid brokers (Upstox Plus, DhanHQ, Kite Connect, Fyers Prime) can supply it, and whether it is
**live-only** (gone forever if not recorded -> must be written to the RAID hard disks) or **pullable
later** (a broker or NSE serves it again -> may sit on SSD for the day, then moves to the hard disks).
No institutional data (dealer gamma, signed option flow, intraday FII positions) is in scope.

## 2. What is claimed (each item names the file that carries the evidence)

| # | Claim | Evidence |
|---|---|---|
| C1 | 183 rows, one per instrument per data product: 85 LIVE_ONLY_NON_RECOVERABLE, 94 PULLABLE_RECOVERABLE, 4 UNKNOWN. Every row's `evidence` column carries a `path:line` cite and its `why_needed_for_regime` is filled (both checked mechanically: 183/183 contain `:<digits>`, 0 blank; the two GAP rows cite `docs/framework/DATA_NEEDED_FOR_EDGE_031126.md:41`). That the cited line says what the row claims was re-opened by Fable only for a sample (round 2 re-opened 237 cites); the rest is for you (Q1). | `artifacts/docs/framework/data_needed_instruments_041126.csv`, `DATA_NEEDED_INSTRUMENTS_041126.md` |
| C2 | All 36 store tables the pullers declare (`dp_families.py`) are classified; 0 left UNKNOWN. A partly re-pullable table (`global_1m`, `opt_ohlc_1m`) is treated as live-only until its window is probed. | `artifacts/config/recoverability.json`, `artifacts/pullers/shared/dp_recoverability.py` |
| C3 | On 04-11-2026 both i5 and i7 were recording the same live-only instruments: Kite 202, Dhan 49, Upstox 47, Fyers 5; weekly-expiry recording is ON. 236 distinct names per box (259 broker+name pairs). 123 / 87 files over 20 MB on i5 / i7. | `artifacts/docs/framework/LIVE_CENSUS_041126.csv` / `.md` |
| C4 | The retailer database can be filled from existing databases with a supplier stamp on every row; rows with no known supplier get `UNKNOWN_HISTORICAL`, never a guessed broker; sources are never modified; a power cut leaves no half-built file. (Tested on synthetic data only.) | `artifacts/tools/retailer_db_build.py`, `tests/test_retailer_db_build.py` |
| C5 | Nearly all recorders needed already exist; six small gaps (G1-G6) remain, and the same-day SSD-to-HDD mover does not exist yet. | `artifacts/docs/framework/RETAILER_PULLER_DESIGN_041126.md` |
| C6 | Kumar's 31 requirements are encoded as machine-checkable rules; the guard refuses to call any build DONE without Fable, external-auditor and Kumar approval. | `artifacts/docs/framework/REQUIREMENTS_REGISTER.json`, `APPROVALS_LEDGER.json`, `tools/requirements_guard.py` |

## 3. What is NOT proven (read this before trusting anything above)

1. **The live census is one read-only snapshot, taken by an AI agent during market hours.** No second source confirms it. Per-token tick row counts timed out and are UNKNOWN, not 0.
2. **Upstox and Dhan identifiers for the 50 NIFTY constituents are not in the repo**; 127 of 183 rows have those cells as UNKNOWN. The resolving read-only queries are listed in the MD, section "UNKNOWN".
3. **Four instruments have no recorder anywhere**: GIFT NIFTY live, USDINR daily, BANKNIFTY options, Sensex F&O. The GIFT NIFTY instrument key is contradicted between two repo documents.
4. **"Pullable" is not probed.** `recoverable_until` per broker (how far back each broker serves 1m/options history) has not been measured; the config says UNKNOWN. CLAUDE.md 1.1 gives start dates only.
5. **The real `opt_chain_1m` primary key and any duplicate-supplier collisions in the real archive are unknown.** The builder infers the key.
6. **The builder has never touched a real database.** The final-fsync step cannot be tested without a real power cut (one mutation survives for that reason).
7. **i5's master archive `niftybkp.db` is corrupt** ("database disk image is malformed", task T-1317). i7's copy was read healthy (1,782,139 rows in `nifty_1m`). Not repaired.
8. **i5's SSD is 100% full** (1.8G free of 205G, measured in the read-only census, `artifacts/docs/framework/LIVE_CENSUS_041126.md` line 27, one snapshot at market hours; there is no TASKS.jsonl entry for this exact figure, only the older C-021 reading of 3.47 GB at 21:39 on 03-11) and its space gate fails open; i7's `.env` / `DP_SSD_ROOT` and the Pi5 were not checked.
9. **The same-day SSD-to-HDD mover is not built** (design gaps G2 daily seal, G3 `rows_raw` split).
10. **Independence limits:** the "Fable" review was a Fable-model agent started by the same operator that wrote the artifacts; its findings are in `FABLE_REVIEW_041126.md`. It is not an external audit, and **no approval below is ticked**.
11. **The requirements guard is itself a new, unapproved build**, and its traceability rule can be satisfied by merely citing an R-id (see question Q10).

## 4. How to verify (exact commands; need Python 3.11+ and pytest, no network, no broker access)

```bash
git clone -b report/pull-status-081026 https://github.com/roopeshkumarb/blpro && cd blpro   # tip of the branch contains this pack
# 1. the copied files are what is described (run inside this pack)
cd docs/audit_pack_041126/artifacts && sha256sum -c ../MANIFEST.sha256 && cd -
# 2. the tests (expected: 141 passed = 75 guard + 6 generator + 32 builder + 25 recoverability + 3 placement;
#    the placement file used to contribute 0 under pytest)
python3 -m pytest -q tests/test_dp_recoverability.py tests/test_recoverability_placement.py \
    tests/test_gen_data_needed_instruments.py tests/test_retailer_db_build.py tests/test_requirements_guard.py
# 2b. the mutation runner (patches copies only; expected 31 CAUGHT, 2 SURVIVED = the two fsync mutants, see MUTATION_LOG.txt)
python3 docs/audit_pack_041126/mutation_runner.py
# 3. regenerate the list and confirm it equals the committed one (the test above does this in a sandbox)
python3 tools/gen_data_needed_instruments_041126.py && git status --short docs/framework
# 4. classify any name yourself
python3 -c "import sys; sys.path.insert(0,'pullers/shared'); import dp_recoverability as R; print(R.classify('opt_ohlc_1m'), R.classify('nifty_1m'))"
# 5. rerun the guard (read-only)
python3 tools/requirements_guard.py
```
Pack copies of files containing a LAN address prefix were redacted; see `REDACTIONS.txt`. No tokens, passwords or `.env` content are in the pack (`make_manifest.py` scans for them; the word "token" in the files means a public exchange instrument token).

## 5. Approvals ledger (copied from `APPROVALS_LEDGER.json`)

| Build | Fable | External auditor | Kumar | May be called DONE |
|---|---|---|---|---|
| tools/retailer_db_build.py | no (PASS-WITH-FIXES, not an approval) | no | no | no |
| tools/retailer_db_inventory.py | no | no | no | no |
| tools/gen_data_needed_instruments_041126.py | no | no | no | no |
| tools/requirements_guard.py | no | no | no | no |
| config/recoverability.json | no (re-review pending) | no | no | no |
| pullers/shared/dp_recoverability.py | no | no | no | no |

**How an approval is recorded, and what the guard can and cannot stop (hardened after Fable rounds 2 and 3).** A flag in `APPROVALS_LEDGER.json` may be `true` only when its `<flag>_evidence` is a regular file (no symlink in its path, canonical spelling) in `docs/approvals_evidence/` - the only folder accepted; never the pack, never a README, never code, `CLAUDE.md` or the ledger - that contains the line `APPROVAL <flag> APPROVES <build path>` for exactly that flag and build plus at least 20 words of prose, contains no "not approved" / "rejected" / FAIL line, and whose sha256 is recorded in `<flag>_evidence_sha256` and recomputes. Build paths in the ledger are normalised and a duplicate row for the same build is an ALERT. The approval then has to be appended to `docs/framework/APPROVALS_STATE.json` (an append-only hash chain, written only by `tools/requirements_guard.py --accept-state`), and `--accept-state` takes at most ONE newly-true flag per call, only when that flag's evidence file is already committed in git HEAD, and refuses any true flag when git history cannot be read. The chain head is anchored in three places (the state file, the `anchor_history` carried in `guard_report.json`, and git HEAD's copy), so deleting the tail of the chain - which would silently un-revoke an approval - is an ALERT. A removed build row, a broken chain, evidence edited after approval, or a `DONE` claim without all three accepted approvals is an ALERT, and such a build is never "allowed to be called DONE".

**Limit, stated plainly - one person with write access to this repo can still approve any build.** The guard cannot tell who wrote an evidence file or whether Fable, the auditor or Kumar really said it. A person who writes a file containing the APPROVAL line, commits it, flips one flag, runs `--accept-state`, commits, and repeats for the other two flags gets three approvals; and a person who rewrites the whole chain, the state file, `guard_report.json` and git history together passes a local guard. What the guard forces is that this is done in separate, visible commits, one flag at a time, with the response document committed first. It is an accident-and-sloppiness check, not a security control, and its traceability rule (TRACE) is still gameable: any cited R-id passes. The real gate is Kumar and the external auditor reading the evidence themselves. Mutation results, including the ones that survive, are in `MUTATION_LOG.txt`; the corrected wording of ledger claims C-054 and C-055 is in `LEDGER_CORRECTIONS.md`.

## 6. Ten things the external auditor is asked to try to break

1. **Citations.** Pick 20 random CSV rows. Open each `evidence` file:line. Does the code really say what the row claims (symbol, expiry rule, broker)?
2. **Recoverable that is not.** Find any table `classify()` calls RECOVERABLE whose past cannot be bought back (suspects: `vix_1m` which only exists from Aug 2025, `fut_1m`, `sector_1m`, `equity_1m`, `nifty_1m` before 2022, the NSE reports).
3. **Pattern collisions.** The classifier matches substrings (`tick`, `quote`, `depth`, `instruments`, `ohlc`, `news`). Invent a real file or table name that is classified the wrong way, in either direction. Is "UNKNOWN is protected" a safe default for placement?
4. **Missing live-only data.** Is anything a retailer needs for multi-timeframe regime detection and intraday direction absent from the 183 rows, using only data a retail broker or NSE can supply? (Institutional data is out of scope by design.)
5. **Census trust.** The census is a single agent snapshot. What second, independent source would you demand? Dhan weekly and monthly contracts share one label string - how should the retailer DB key them so they can never merge?
6. **Builder: corrupt or invent.** Hand `retailer_db_build.py` a source that makes it modify the source, invent a broker stamp, or publish a half-built file. Include a corrupt source, a locked source and a source that changes mid-run.
7. **Builder: power cut.** Is the sequence temp file -> fsync -> verify -> rename -> directory fsync correct on ext4 and Btrfs (Synology)? Is there any instant where the final path exists but is incomplete?
8. **Supplier precedence.** Duplicate rows with different `src` are ranked by the order upstox_live, upstox_expired, fyers_backfill, dhan, fyers_live, fyers_live+upstox_oi, fyers_live+dhan_oi; across different source databases the first source wins. Defend or reject both rules.
9. **Move safety design.** Read the "Same-day SSD to HDD" section of the puller design. Does the 8-point contract survive a power cut at every step, a full destination disk, and a network drop mid-copy? What is missing?
10. **Guard gaming.** Find a way to make `requirements_guard.py` report no ALERT or allow a DONE claim while a requirement is violated (for example citing an R-id in a note without doing the work). Propose the tightest rule that closes it.

Disagreements already found by the Fable-model review, and what was done about each, are in `DISAGREEMENTS.md`.
