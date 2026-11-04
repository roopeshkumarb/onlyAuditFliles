# approvals_evidence - the only folder the approvals guard accepts as evidence

A flag in `docs/framework/APPROVALS_LEDGER.json` (`fable`, `external_auditor`, `kumar`) may be `true` only when
its `<flag>_evidence` is a file in THIS folder. This README is never accepted as evidence itself.

An evidence file is a real response document from the reviewer: the Fable report, the external auditor's reply
copied here unchanged, or Kumar's own written sign-off. It must contain, on its own line, exactly:

    APPROVAL <flag> APPROVES <build path as written in the ledger>

for example `APPROVAL fable APPROVES tools/retailer_db_build.py`, plus at least 20 words of prose (what was
reviewed, what remains unproven). It must NOT contain a line saying "not approved", "rejected" or a FAIL verdict.
No symlinks. Commit the file FIRST; then flip ONE flag in the ledger, record the file's sha256 in
`<flag>_evidence_sha256`, run `python3 tools/requirements_guard.py --accept-state`, and commit again. The guard
refuses to accept more than one newly-true flag per call, or a flag whose evidence is not yet in git HEAD.

Limit, stated plainly: the guard cannot tell who wrote the file. Anyone with write access to this repo can still
write one, commit it, flip a flag and accept it - one flag per commit, visibly. The real gate is Kumar and the
external auditor reading the response documents themselves. Nothing in this folder exists yet: all approvals are
still false.
