# Paste this whole file into the auditor (Kimi, or any model). It is self-contained; links are public raw files.

You are an independent, adversarial auditor. You did not write this work. Do not agree to be polite. Say UNKNOWN when you cannot verify; UNKNOWN is never zero.

## Context
A retail trader (India) runs an ADVISORY intraday NIFTY 50 directional-prediction engine (no live orders). Data pullers will be told to STOP pulling anything not on a "data needed" list, because the disks are saturated. A series that is live-only, or older than a broker history window (Dhan 1-minute 5 days, Upstox 28 days, Kite 60 days, Fyers 100 days), is lost for good once it stops being pulled.
Hard retail limits: NO signed option order flow, NO dealer gamma/GEX, NO intraday FII/DII positions (end-of-day only), NO historical tick-by-tick depth. Any suggestion must respect these or be marked impossible.

## Read (public files)
- The list, readable: https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/audit_051126_data_needed_v2/artifacts/docs/framework/DATA_NEEDED_LIST_051126.md
- The list, machine form (176 rows, each row names its code citations): https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/audit_051126_data_needed_v2/artifacts/config/retailer_edge_universe.json
- An earlier audit that found the list incomplete: https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/audit_051126_data_needed_v2/artifacts/docs/framework/OPUS_AUDIT_DATA_NEEDED_051126.md
- The retail constraints and data horizons: https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/audit_051126_data_needed_v2/artifacts/CLAUDE.md
(The engine code is not published; judge from the list, the earlier audit and your own knowledge of intraday index direction modelling, and say which you used.)

## Questions
1. Is more data needed beyond this list for an intraday NIFTY 50 DIRECTIONAL model? First line of your answer: YES (top items) or NO, with your confidence and what would change your mind.
2. For each extra item you propose: available at retail from which broker or free source (UNKNOWN if unverified, never guess); recoverable later or live-only; rough storage cost (mark estimates); evidence for its predictive value (cite a source or say speculation); verdict ADD NOW / ADD LATER / SKIP.
3. Is any row on the list unnecessary (wasted disk)?
4. Do you agree with the earlier audit's "rows to add" and "NOT SAFE to stop" groups?
5. Is there any sign in the materials that an intraday edge is actually demonstrated? If not, say data collection is not the bottleneck.

## Answer format
ITEM / FILE-BY-FILE (SUPPORTS | DOES NOT SUPPORT | CANNOT CHECK) / CLAIMS (AGREE | DISAGREE | UNPROVEN) / MISSING PROOF YOU WANT RUN / ASSUMPTIONS YOU FOUND / VERDICT (VERIFIED | NOT VERIFIED | VERIFIED WITH CONDITIONS). Under 800 words. State which model you are.
