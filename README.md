# onlyAuditFliles: START HERE (this link never changes)
Plain-text audit repo for a retail NIFTY 50 data-capture system (advisory only, no orders). Everything an auditor needs is reachable from THIS page; the owner does not paste new links.

1. Read `AUDITOR_PROTOCOL.md` (the zero-assumption rules and the required answer format).
2. Read `LATEST.md` (what is open for verification right now, newest first).
3. Check `CLAIMS_LEDGER.csv` (every claim: PROVEN / UNPROVEN / RETRACTED / NOT TESTED, with its evidence file).
4. `CHANGELOG.md` shows what changed since you last looked, including CORRECTIONS to earlier statements.
5. `MANIFEST.json` and `SHA256SUMS` list every file with its sha256 and raw URL, so you can detect a silent edit.
6. Your verdicts go back through the owner and are stored in `AUDITOR_RESPONSES/`.

Raw base URL: https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/<path>
Fixed entry points:
- https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/AUDITOR_PROTOCOL.md
- https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/LATEST.md
- https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/CLAIMS_LEDGER.csv
- https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/CHANGELOG.md
- https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/MANIFEST.json
Note: GitHub's raw cache can lag a few minutes after a push; compare sha256 with MANIFEST.json.
Folders: one per audit (`audit_DDMMYY_<topic>/`), each with an INDEX.md. No credentials are ever stored here.
