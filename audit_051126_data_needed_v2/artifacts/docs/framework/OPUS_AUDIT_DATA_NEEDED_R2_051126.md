# Re-audit R2: data-needed list, live-only gate v2, pull-policy draft (05-11-2026)
Auditor: Claude Opus 5.5 (claude-opus-5-5). Read-only, no ssh. Scripts are in /tmp/audit (fwd.py, sim.py, plus inline probes).

## Verdicts
* **The list may govern a live-only pull policy: PASS-WITH-FIXES.** The list is now complete enough. It is safe only because the gate's `audit_not_safe()` guard protects data the classifier still calls NOT_NEEDED.
* **The policy draft may be deployed outside market hours: PASS-WITH-FIXES.** `--check` gives OK, and the draft lists no NIFTY, index, VIX, GIFT or universe-named id. But it must be rebuilt from same-day exports and masters, and it needs an expiry date (F1).

## 1. Status of D1-D6 (176 rows, 208 citations; every file:line exists)
| Defect | Status | Evidence |
|---|---|---|
| D1 sector / MIDCAP 100 / NEXT 50 | **FIXED at the gate, OPEN in the classifier** | U168/U169 added. `needed_vs_pulled.py` is unchanged (dated 04-11): `fyers NSE:NIFTYIT-INDEX 1m` is still NOT_NEEDED. It is protected by `dp_liveonly.audit_not_safe` (`:412-414`) and `not_safe_here` (master lookup). U168/U169 name no broker symbol (UNKNOWN or `<SECTOR>` placeholders), so the `needed` override adds nothing for them. |
| D2 RECOVERABLE without checking the window | **PARTLY** | `class_name_for` (`:475-496`) now sends options to `opt_ohlc_1m` and Yahoo/GLOBAL intraday to `global_1m`, both protected. Plain candles are still RECOVERABLE without a probe, and Fyers seconds data is accepted as lost. |
| D3 GIFT / Yahoo 1m | **FIXED** | U170/U171 added, U051 set to REQUIRED_ENGINE. The gate protects yahoo, GLOBAL_, GIFT and SGX. U170 cites docstring lines (`global_wire.py:23,46`), not code. |
| D4 EOD inputs | **FIXED in the list, OPEN in the classifier** | U172-U175 added. The classifier still calls `participant_vol` NOT_NEEDED and contract rows "duplicates broker candles". The gate protects every `nse` key. |
| D5 classifier vs U024/BANKNIFTY | **OPEN in the classifier, guarded at the gate** | MCX and BANKNIFTY futures are still NOT_NEEDED in `needed_vs_pulled.py`. `audit_not_safe` covers CRUDE, GOLD and BANKNIFTY. |
| D6 citations | **PARTLY** | U013/U014 still cite `options_chain_summary`, whose history comes from the bhavcopy. U064 still cites `_prior_session`. U022 still cites a label tuple. U168 cites `feature_compute_full.py:890`, which sits inside FEATURE_BLOCKED f151-f167. |

## 2. G6 and the retraction
* **G6 is plausible but overstated as RESOLVED.** Only rows since 2025-09-15 were measured.
  * 52 symbols against 50 constituents is unexplained.
  * `equity_1m` mixes 4 sources with different symbol spellings (Dhan file names against tickers; see the `config/nifty50.py` warning), so breadth double-counts unless it is keyed by db_sym.
  * The f151-f167 block also cites missing index weights.
  * `daily_recorder.py:88` still says "yahoo daily, 20 symbols".
* **The retraction is right in direction:** 5/28/60/100 d are mostly per-request limits, not depth.
  * The error is that "oldest row held" proves only what was once pulled, not what a broker serves today. Expired F&O contracts are not served at all by Kite or Dhan.
  * `dp_liveonly.BROKER_WINDOW_DAYS` (`:89`) and the deploy plan still carry the retracted numbers. They only change status text, not decisions.

## 3. Gate and generator: ways a NEEDED or live-only series could be stopped
* **F1 (high): numeric vendor ids are judged only at generation time.**
  * 2,066 of the 3,536 entries are bare Dhan/Kite ids. At runtime the gate's text rule cannot read them: `kite|15736578|1m` (the NIFTY Nov future) gives `audit_not_safe` None and RECOVERABLE, so it would be refused if listed.
  * The policy has no valid-until date and no master date. If a broker reassigns an expired contract's id to a NIFTY contract, or the policy outlives a roll or a NIFTY 50 rebalance, a needed series is refused.
  * Fix: put the master date in the checksummed doc and have the gate fail OPEN once it is more than 1 trading day old, or list only equity-segment ids.
* **F2 (medium): the classifier and the list disagree, and only a hand-written text rule closes the gap.** Fix: update `needed_vs_pulled.py` for U168-U176.
* **Checked and safe:**
  * Wildcards are only fyers 5s-45s and 15m. Exceptions cover NEEDED, UNKNOWN and NOT SAFE keys.
  * `needed` beats `not_needed`.
  * Keys with `|` (all Upstox keys) cannot be listed.
  * Every error path fails open. Recorders and snapshots never ask the gate.
  * `norm_interval` maps 1, D, minute and 5S correctly.
  * Constituents and universe ids are absent from the draft (probe).
* **The ~0.02 GB/day claim is not an upper bound on avoided writes.** It counts one session per key updated in the 24 h of the stale 04-11 export. It excludes backfills, which are the main load (32.8/22.6 GB held), and it excludes all Upstox NOT_NEEDED keys, which are unlistable (102 M/145 M rows). Read it as "steady-state top-up of the listed keys only".

## 4. Unproven
* Whether Kite/Dhan reuse ids.
* Per-symbol serving depth today.
* The masters used for the draft, which are not in the repo.
* The 2 extra symbols in G6.
* That the running images pass `kind="option"` on every option job.
