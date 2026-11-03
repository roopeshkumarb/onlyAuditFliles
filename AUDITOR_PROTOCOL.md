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
