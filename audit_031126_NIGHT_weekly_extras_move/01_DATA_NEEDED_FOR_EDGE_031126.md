# DATA NEEDED FOR EDGE (retail, API-limited) - one list, live-only vs recoverable, recorder status. 03-11-2026 23:00 IST
Owner order: record the weekly expiry and every missing live-only feed; do not ask. Status words: RECORDING (day-file proof exists), DEPLOYED-NOT-YET-SEEN (code+env on both boxes, first proof = 04-11 09:00 session), MISSING (no recorder), UNKNOWN.

## 0. Why weekly expiry was not covered (facts, not excuses)
- The older need lists (docs/framework/data_need/NEED_BACKTEST/ML/PAPER/LIVE_291026.md and NEW_SYSTEM_NEED_LIST_301026.md) are organised by CONSUMER of the old engine (backtest, ML, paper, live). They mention weekly only as an expiry RULE or a history flag: BT-09, N4, L24, NEED_BACKTEST E2, NEED_PAPER P7, ML-12, ML-05 ("weekly rows exist only from the weekly start dates"), OFFER_VS_HELD row 19. None of them says "record the live ticks/depth/chain of the weekly contracts". CORRECTION after the Fable audit: the weekly WAS on record as a data FEATURE need earlier: docs/research/ALGOTEST_FEATURES_DATA_151026-0808.md line 70 (15-10-2026) "G2 weekly and next-weekly expiries ... add WEEK AFTER monthly". It was never turned into a recorder requirement.
- The live-only work (02-11) was organised BY BROKER. The audit scoreboard listed "weekly options only on Kite; Dhan and Upstox record only the monthly" as ACCEPTED, NEEDS YOUR DECISION (AUDIT_SCOREBOARD_021126.md section 3b) and I left it there instead of promoting it into the need list. That was my miss: a recommendation I had already made ("Yes") needed no decision.
- Consequence: weekly expiry (Tuesday) is the contract family where most intraday option activity sits, and 2 of 3 depth recorders did not have it. Fixed tonight (section 3). Two corrections from the Fable audit: there are FOUR depth/tick recorders (Kite, Dhan, Upstox, Fyers TBT), not three; Fyers TBT is monthly-only by construction (dp_fyerstbt.py:106-111 'a weekly symbol never matches') and is STILL not fixed (B9).

## 1. Feature groups the engine needs (multi-timeframe regime, direction, edge after costs)
| # | Group | What exactly | Live-only? | Source (per CLAUDE.md constraints) | Status |
|---|---|---|---|---|---|
| G1 | Spot and futures | NIFTY 50 index, near + next futures: price, traded volume (futures volume only; index volume is vendor-aggregate), OI | candles recoverable (SSD); live L1+5-depth NOT | Kite ticks; Upstox feed; Dhan | RECORDING (Kite: near+next fut, index). Dhan d200 = one monthly future |
| G2 | Options, monthly | ATM+/- strikes: ticks, depth, OI | live-only | Kite (code defaults +/-20 monthly, +/-15 nearest, dp_tickrec.py:47-48; env override UNKNOWN); Dhan d20; Upstox | RECORDING |
| G3 | Options, WEEKLY (nearest) | ATM+/- strikes: ticks, depth, OI | live-only | Kite (already); Dhan d20 + Upstox via weekly patch | Kite RECORDING; Dhan/Upstox DEPLOYED-NOT-YET-SEEN (final settings: Dhan DEPTH_WEEKLY_STRIKES=6 + monthly 5 = 26 + 22 = 48 of 50 slots; Upstox UPSTOX_WEEKLY_STRIKES=5 + monthly 5 inside 50 keys incl. index, VIX, future; no new socket). Monthly-expiry week (18-24 Nov and every month) fixed after the Fable audit: the expiring monthly gets the wide window |
| G4 | Option chain snapshots with Greeks/IV (dp_snap.py takes the weekly too: DP_SNAP_WEEKLY default 1; whether dp_snap runs on the boxes is UNKNOWN, it is not in the compose file) | per strike: OI, prev OI, IV, delta/gamma/theta/vega, bid/ask | live-only (no history anywhere) | Upstox /v2/option/chain, Dhan /optionchain, Fyers options-chain-v3, NSE | PARTIAL: old pullers (fullpuller/puller930) store snapshots in puller DB table rows_raw on SSD (content and cadence UNMEASURED, see 4) |
| G5 | Volatility | India VIX live; realized vol from futures | VIX live in Kite+Upstox feeds; history only since 2025-08-11 | Kite token 264969; Upstox NSE_INDEX|India VIX | RECORDING |
| G6 | Breadth | all 50 NIFTY constituents live (TICK_EXTRA_EQ=50; the first version took the first 20 alphabetically, a poor sample, changed after the Fable audit); candles recoverable | live L1/depth live-only | Kite websocket | DEPLOYED-NOT-YET-SEEN (TICK_EXTRA=1) |
| G7 | Cross-index / ETF | NIFTY BANK, NIFTY FIN SERVICE, NIFTYBEES (ETF vs futures divergence), BANKNIFTY near future | live-only for ticks | Kite websocket | DEPLOYED-NOT-YET-SEEN |
| G8 | Macro stress | USDINR near future (CDS), MCX CRUDEOIL and GOLD near futures | live ticks live-only | Kite websocket (CDS/MCX entitlement UNKNOWN) | CODE READY, OFF (TICK_EXTRA_MACRO=0): Fable could not exclude that an unentitled token flaps the socket and loses the baseline; enable on one box after a clean session |
| G9 | Pre-market gap | GIFT NIFTY | live-only (history UNKNOWN) | Upstox master (instrument_key NOT found yet) | MISSING (B7) |
| G10 | Microstructure depth | 5/20/30/50/200 level books | live-only | Kite 5; Dhan 20+200; Upstox 30; Fyers TBT 50 | RECORDING (Fyers TBT: 5 symbols; Upstox 30-level request UNVERIFIED) |
| G11 | Auction / quote extras | closing-auction fields, quotes with CAS, option-Greek quote, market status | live-only | Dhan CAS feed; Upstox quote V3/option-greek; Fyers quotes+marketStatus | MISSING (B1-B4) |
| G12 | Flows and positions | FII/DII (EOD only), participant OI (EOD) | EOD reports recoverable | NSE reports | outside the live recorders |
| G13 | Events and news | RBI/FOMC/CPI calendar (manual file), news | news live-only (Upstox 7-day window; Dhan blocked) | manual data/event_calendar.yaml; Upstox /v2/news | calendar MISSING (B6), news NEAR ZERO |
| G14 | Costs | brokerage, STT, exchange charges, slippage | not market data | broker schedules | MISSING: needed before any edge claim |

## 2. Live-only items the old pullers/recorders do NOT cover (build queue, in order; none needs a new broker socket except B8)
| id | item | broker | how | blocker |
|---|---|---|---|---|
| B1 | Option-Greek quote V3 | Upstox | REST snapshot every N s inside the API budget | must go through the pull-lease/budget system; key cap CONFLICT 50 vs 500 (docs) |
| B2 | Closing-auction live feed (CAS) | Dhan | websocket subscribe 23 on the existing feed host | socket cap (4 of 5 used) |
| B3 | Futures chain + market status + quotes with call-auction fields | Fyers | REST | rate budget |
| B4 | Quote snapshots (5-level, OI, circuits) | Kite | REST /quote | quote group 1 req/s |
| B5 | Live indices cadence; live option chain | NSE | REST scripts | NSE says scripted collection not allowed (terms unread) |
| B6 | News + manual event calendar | Upstox/Dhan/manual | puller + yaml | Dhan news blocked (DH-902) |
| B7 | GIFT NIFTY | Upstox | find instrument_key in the Upstox master, add to feed | key unknown; one connection is full at 50 keys |
| B8 | Extra index keys (Bank Nifty, ETF) on Upstox | Upstox | a SECOND websocket connection | connection count on Plus UNVERIFIED (5? contested) |
| B9 | Weekly NIFTY options on Fyers TBT 50-level | Fyers | extend dp_fyerstbt.py symbol picker to the weekly symbol format | weekly symbol format and the TBT symbol cap (5 today) must be read from the Fyers master first |
| B10 | Split the Dhan d200 contract between the boxes (i5 future, i7 nearest weekly ATM) | Dhan | env/plan change | owner's earlier accepted split, not done |
| B11 | NIFTY index + India VIX on Dhan | Dhan | d20 is NSE_FNO only today | slot/segment rules |
| B12 | BANKNIFTY options (none anywhere); Sensex (BSE F&O is offered by Kite BFO / Upstox BSE_FO but not subscribed) | Kite/Upstox | add to Kite socket | decide value; Bank Nifty weekly discontinued by NSE (UNVERIFIED) |
B1-B5 are REST pollers: they must be built behind the lease/budget controller and tested supervised in a session, so they are NOT deployed tonight.

## 3. Done tonight (03-11-2026 22:28-00:10 IST)  [final state after the Fable audit fixes]
- WEEKLY: dp_depthrec.py, dp_upstoxrec.py and the compose file deployed on i5 and i7 (originals kept as *.bak_031126_*), .env DEPTH_WEEKLY_STRIKES=6 and UPSTOX_WEEKLY_STRIKES=5 (first deployed as 6, changed to the tested 5 after the Fable audit), recorders recreated (env confirmed inside the containers). The recorders reuse today's list from today's day file, so the first weekly list is chosen at the 04-11 start. Revert: set both to 0 in .env and recreate.
- TICK_EXTRA: dp_tickrec.py (+ nifty50_syms.txt; the tickrec entrypoint now copies the file into /app, first version did NOT, so it would have recorded 0 constituents: found by the second Fable review) deployed on both boxes, TICK_EXTRA=1 TICK_EXTRA_EQ=50 TICK_EXTRA_MACRO=0 in .env, tickrec recreated (final). Never replaces the baseline list; any failure is logged to status.json errors.
- SSD to HDD: DID NOT HAPPEN, and one attempt caused an incident. The first version of tools/ssd_to_hdd_move.sh moved dhan_121026-1533.db and fyers_121026-1534.db, which dhan_current.db / fyers_current.db point at; the links dangled for several minutes until both files were restored from the sha256-verified HDD copies (T-1313). With the guards added (never a symlink target, never a file with a -wal/-shm, never an unwritable directory, copy-only unless ALLOW_REMOVE=1) a dry run finds NOTHING on the i5 SSD that is safely movable: every file over 100 MB is written today, an epoch-pointer target, or in a root-owned directory. The real fix needs the old pullers' mounts changed (epoch DBs on the HDD volume with the path mounted into the containers) or the old pullers replaced: it waits for that.

## 4. Similar-data audit: other gaps of the same kind as the weekly miss
1. Next-month future: Kite has near+next; Dhan d200 records one; Upstox the monthly only. Second-month option strikes: none anywhere. [open, low value for intraday]
2. Option chain snapshots (G4) sit in puller DBs table rows_raw on SSD: this is live-only data in a recoverable-class location and NOT proven complete. First check (read-only, tomorrow): which datasets rows_raw holds, rows per day, cadence. Move such data to HDD going forward.
3. Fyers TBT covers 5 symbols only; Fyers seconds candles keep 30 days only (daily pull needed): not verified running.
4. Other weekly families: Bank Nifty / Fin Nifty / Midcap weekly were, to my knowledge, discontinued by NSE in Nov 2024; verify by counting expiries per name in tomorrow's Kite NFO list before closing this item. Sensex weekly is BSE (not in any broker feed here).
5. Both boxes record the SAME d200 contract and the same strike windows (shifted by one strike): no diversity; consider splitting after the weekly proof.
6. Per-feed gaps today: Dhan d20 silent ~4 min repeatedly (T-1311), both boxes lost 12:08-12:31 and 12:42-12:51 (T-1310).
