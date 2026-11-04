# Ledger corrections for the public claims ledger (04-11-2026, after Fable round 2)

These are the exact replacement texts for claims C-054 and C-055 in `onlyAuditFliles/CLAIMS_LEDGER.csv`. Nothing has been written to the public repo; the corrections are staged here so the owner can see them first. A superseded claim is marked RETRACTED in the public ledger, never silently edited (AUDITOR_PROTOCOL rule 4).

## C-054 (builder)

**Old text (as published):** `retailer_db_build.py (initial retailer DB from existing DBs with supplier stamps): 21 tests pass and 11 of 12 mutations caught` | status `PROVEN (sandbox only)`

**Why it is replaced:** Fable round 2 found (a) "11 of 12 mutations caught" had no mutation log anywhere in the repo or the pack, so it could not be checked; (b) two of three fresh mutants Fable tried survived the 21-test suite (row-count check in `_verify`, `any`->`all` in the NOT NULL reject); (c) no lock stopped two concurrent builds to one output (reasoned, not executed).

**New status of the old claim:** `RETRACTED` (unsupported as written).

**New claim C-054b:** `retailer_db_build.py: 27 tests in tests/test_retailer_db_build.py pass. 33 deliberate breaks were tried across the builder and the requirements guard (docs/audit_pack_041126/MUTATION_LOG.txt); of the 17 aimed at the builder, 15 are CAUGHT and 2 SURVIVE (removal of the scratch-file fsync and of the directory fsync - not testable without a real power cut). A directory flock now refuses a second concurrent build.` | status `PROVEN (sandbox only; never run on a real database; durability under power loss UNPROVEN)` | evidence `docs/audit_pack_041126/MUTATION_LOG.txt`, `tests/test_retailer_db_build.py`

(Counting rule: the builder mutations are B1, B1b, B2-B16 = 17 of the 33; the other 16 are guard mutations G1-G16.)

## C-055 (guard)

**Old text (as published):** `requirements guard (R01-R31) reports 0 ALERT and refuses to call any build DONE: 0 of 6 builds have all three approvals` | status `PROVEN (sandbox)`

**Why it is replaced:** the numbers were reproduced by Fable, but Fable round 2 judged the guard a FAIL as an approvals gate: a ledger flag could be flipped with the evidence text `ok`, `CLAUDE.md` was accepted as evidence, and a build row could be deleted, all with 0 ALERT. Its traceability rule was also satisfied by notes appended three minutes before the report (confirmed gameable, audit question Q10). "Refuses to call any build DONE" was therefore too strong.

**New status of the old claim:** `RETRACTED` (overstated).

**New claim C-055b:** `requirements_guard.py (hardened 04-11 after Fable round 2): an approval flag counts only with evidence that is a file under docs/audit_pack_041126/ (not artifacts/) or an AUDITOR_RESPONSES-style folder, that is not code or CLAUDE.md or the ledger, that names the build, and whose recorded sha256 recomputes; accepted approvals live in an append-only hash chain (docs/framework/APPROVALS_STATE.json). 56 tests; 16 deliberate breaks of the gate, all CAUGHT. Today 0 ALERT and 0 of 6 builds may be called DONE. The traceability rule (TRACE) is still gameable: any cited R-id passes, so it proves a mapping was written, not that the work serves the requirement.` | status `SANDBOX-TESTED; AN ACCIDENT-AND-SLOPPINESS CHECK, NOT A SECURITY CONTROL` | evidence `tools/requirements_guard.py`, `tests/test_requirements_guard.py`, `docs/audit_pack_041126/MUTATION_LOG.txt`

**Stated limit:** someone who edits the ledger, the evidence file, its recorded hash and the state chain together, or deletes the tail of the chain, passes a local guard. The real gate is Kumar and the external auditor.


## Addendum after Fable round 3 (04-11-2026) - replacement wording for C-054b and C-055b

**C-054c (supersedes C-054b):** `retailer_db_build.py: 32 tests in tests/test_retailer_db_build.py pass. 53 deliberate breaks were tried across the builder and the requirements guard (docs/audit_pack_041126/MUTATION_LOG.txt); of the 21 aimed at the builder, 19 are CAUGHT and 2 SURVIVE (removal of the scratch-file fsync and of the directory fsync - not testable without a real power cut). The guards "output may not be a source" and "source labels must be unique" are now tested (round-3 mutants BN1/BN3). A directory flock refuses a second concurrent build.` | status `PROVEN (sandbox only; never run on a real database; power-loss durability UNPROVEN)` | evidence `docs/audit_pack_041126/MUTATION_LOG.txt`, `tests/test_retailer_db_build.py`

**C-055c (supersedes C-055b):** `requirements_guard.py (hardened twice, after Fable rounds 2 and 3): an approval flag counts only with a regular, non-symlink evidence file in docs/approvals_evidence/ that carries the line 'APPROVAL <flag> APPROVES <build>', has 20+ prose words and no not-approved/rejected/FAIL line, whose sha256 recomputes; ledger build paths are normalised and duplicate rows are an ALERT; --accept-state takes one newly-true flag per call and only when the evidence is in git HEAD; the chain head is anchored in the state file, guard_report.json and git HEAD, so tail deletion ALERTs. 75 tests; 32 guard mutants, 31 caught, 1 equivalent survivor (G18). Today 0 ALERT and 0 of 6 builds may be called DONE.` | status `SANDBOX-TESTED; AN ACCIDENT-AND-SLOPPINESS CHECK, NOT A SECURITY CONTROL` | stated limit: one person with write access can still write the evidence file and approve all three flags in three visible commits; the TRACE rule is still gameable (any cited R-id passes); the real gate is Kumar plus the external auditor.
