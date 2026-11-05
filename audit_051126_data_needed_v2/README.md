# Round 6 (05-11-2026): is the DATA-NEEDED LIST complete for an intraday NIFTY 50 DIRECTIONAL prediction engine?

Owner question (Kumar): "Is more data needed apart from this list, or not? The data must satisfy our directional prediction engine for intraday."
Why it matters: the pullers will STOP pulling anything not on this list (disk is saturated). A missing input that is live-only, or older than a broker history window (Dhan 1m 5 d, Upstox 28 d, Kite 60 d, Fyers 100 d), is lost for good.

## What is claimed
1. `artifacts/config/retailer_edge_universe.json` (176 rows) is the list; `artifacts/docs/framework/DATA_NEEDED_LIST_051126.md` is the readable form.
2. An Opus audit (05-11) found the earlier 167-row list INCOMPLETE and wrong in places (`OPUS_AUDIT_DATA_NEEDED_051126.md`). 9 rows were added (U168-U176) and U024, U051, U054 corrected afterwards. That fix is itself NOT yet re-audited.

## What is NOT proven (do not assume)
- Broker instrument ids for the 9 added rows (GIFT NIFTY key, sector index symbols).
- Per-broker history windows for index 1m, Fyers seconds, Upstox global 1m.
- That any directional edge exists. Data completeness is only useful if an edge is demonstrable; say so if the repo shows none.
- Retail constraints (CLAUDE.md): no signed option order flow, no dealer GEX, no intraday FII/DII, no historical tick depth. Any suggestion must respect them or be marked impossible.

## Questions for you
1. Is anything an intraday NIFTY direction model would plausibly use missing from the list? For each item: available at retail from which broker/free source (UNKNOWN if you cannot verify), recoverable later or live-only, storage cost, evidence for its value (cite), verdict ADD NOW / ADD LATER / SKIP.
2. Is any row on the list unnecessary (wasted disk)?
3. Do you agree with the Opus audit's 6 'rows to add' and 'NOT SAFE' classes?
4. Anything in CLAUDE.md's constraints that you think is wrong?

Fable result (05-11): see FABLE_DATA_COMPLETENESS (in this folder and AUDITOR_RESPONSES/20261105_FABLE_DATA_COMPLETENESS.md). Answer in the format of AUDITOR_PROTOCOL.md (ITEM / FILE-BY-FILE / CLAIMS / MISSING PROOF / ASSUMPTIONS / VERDICT). No approval is recorded by this publication; the owner decides.
