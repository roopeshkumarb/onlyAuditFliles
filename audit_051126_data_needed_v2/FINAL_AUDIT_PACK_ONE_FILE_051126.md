# FINAL AUDIT PACK (single file) - data-needed list for the NIFTY 50 intraday directional engine - 05-11-2026

STATUS: nothing here is approved by anyone. Questions for you are in PART 0. Everything you need is in this file.

## PART 0: what we ask
1. Is more data needed beyond this list (intraday NIFTY 50 direction)? First line YES/NO + confidence. 2. For each extra item: retail source (UNKNOWN if unverified), recoverable vs live-only, storage cost, evidence, ADD NOW / ADD LATER / SKIP. 3. Any row unnecessary? 4. Do the Opus and Fable reports below contain errors? 5. Any row marked recoverable that the brokers will not serve for the needed history? 6. Is any edge demonstrated? Answer: CLAIMS (AGREE|DISAGREE|UNPROVEN) / MISSING PROOF / ASSUMPTIONS / VERDICT (VERIFIED | NOT VERIFIED | VERIFIED WITH CONDITIONS). State your model.

Retail limits: no signed option flow, no dealer GEX, no intraday FII/DII, no historical tick depth.
RETRACTION: earlier material said broker 1m 'windows' were Dhan 5 d, Upstox 28 d, Kite 60 d, Fyers 100 d. Measured 05-11 from coverage.db: oldest 1m HELD = Kite 2015-01-13, Dhan 2017-04-03, Fyers 2017-07-17, Upstox 2022-01-03. Treat the short figures as unverified per-request limits, not depth.

## PART 1: THE LIST
# DATA NEEDED LIST - FINAL FOR EXTERNAL AUDIT (05-11-2026)

Source of truth: `config/retailer_edge_universe.json` (176 rows). **Status: NOT approved by anyone.** Fable (05-11): no new feed needed, ~75% confidence, no edge demonstrated. Opus round 1: FAIL as written; round 2: PASS-WITH-FIXES. External audit: pending. Owner: pending.

## Open gaps (known, unfixed or partly fixed)

- **G1** point-in-time NIFTY 50 membership history (survivorship bias); static config/nifty50.py is used -- _NOT BUILT; history must come from NSE index circulars, UNVERIFIED, do not invent_
- **G2** rule_change_history: lot size, expiry-day, STT/charges by effective date (backtest PnL validity) -- _NOT BUILT; values must be sourced from NSE/SEBI circulars; the figures quoted by auditors (75->65) are UNVERIFIED_
- **G3** historical news archive: Upstox ~7 d only; international news not available at retail -- _decision: news features LIVE/PAPER ONLY, blocked from ML training/backtest until an archive exists_
- **G4** continuous-futures roll adjustment for fut_1m backtests -- _UNVERIFIED whether the engine adjusts; to be read from code and proven_
- **G5** per-broker 1m history depth per dataset (index 1m is held from 2022-01-03 per CLAUDE.md, so not every 1m series is window-limited to 28/100 days) -- _to be MEASURED: task T-0832 max depth x max period; classifier must not be changed before_
- **G6** feature_compute_full.py:50 blocks breadth f151-f167 saying equity_1m holds ETFs not constituents; MEASURED 05-11 on i5 blpro_working.db: equity_1m holds 52 symbols (NIFTY constituents by name) from dhan since 2025-09-15 (4.39M rows), fyers_backfill since 2026-09-15 (677k rows, 50 symbols, 75,000 rows for 4 days = 50x375x4 complete), fyers_live 50 symbols (Aug-Sep 2026), kite 23 symbols; older rows before 2025-09-15 not measured -- _PARTLY RESOLVED (Opus R2): measured only rows since 2025-09-15; 52 symbols vs 50 constituents unexplained; equity_1m mixes 4 sources with different symbol spellings (breadth can double-count unless keyed by db_sym in config/nifty50.py); f151-f167 block also cites missing index weights. Code block not touched._
- **G7** residual wrong citations (Opus R2 D6): U013/U014 options_chain_summary (history is bhavcopy), U064 _prior_session reads no membership, U022 label tuple, U168 feature_compute_full.py:890 inside the blocked f151-f167 range, U170 cites docstring lines -- _OPEN_

## Summary by group

| group | rows | required | optional | drop |
|---|---|---|---|---|
| INDEX_SPOT | 11 | 9 | 2 | 0 |
| NIFTY_FUTURES | 3 | 3 | 0 | 0 |
| NIFTY_OPTIONS | 5 | 3 | 0 | 1 |
| PREMARKET_GAP | 2 | 2 | 0 | 0 |
| ETF | 2 | 1 | 1 | 0 |
| MACRO | 5 | 3 | 0 | 1 |
| WORLD_MARKETS | 26 | 26 | 0 | 0 |
| NSE_REPORT | 11 | 7 | 4 | 0 |
| SECTOR | 1 | 0 | 0 | 1 |
| INSTRUMENT_MASTER | 4 | 4 | 0 | 0 |
| NEWS | 2 | 1 | 0 | 0 |
| EVENTS | 1 | 1 | 0 | 0 |
| NIFTY50_CONSTITUENT | 100 | 100 | 0 | 0 |
| GLOBAL_CUE | 2 | 2 | 0 | 0 |
| FUTURES | 1 | 1 | 0 | 0 |

## Every row

| id | name | group | decision | primary | intervals | store | class | cites |
|---|---|---|---|---|---|---|---|---|
| U001 | NIFTY 50 index 1m+1d candles | INDEX_SPOT | REQUIRED_ENGINE | upstox | 1m,5m,15m,30m,60m,120m,1D | nifty_1m | RECOVERABLE | 4 cited, 4 pinned |
| U002 | NIFTY 50 index live ticks | INDEX_SPOT | REQUIRED_OWNER | upstox | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U003 | India VIX 1m+1d candles | INDEX_SPOT | REQUIRED_ENGINE | upstox | 1m,1D | vix_1m | RECOVERABLE | 3 cited, 3 pinned |
| U004 | India VIX live ticks | INDEX_SPOT | REQUIRED_ENGINE | upstox | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U005 | NIFTY BANK 1m+1d candles | INDEX_SPOT | REQUIRED_ENGINE | upstox | 1m,1D | index_1m | RECOVERABLE | 1 cited, 1 pinned |
| U006 | NIFTY BANK live ticks | INDEX_SPOT | REQUIRED_OWNER | kite | tick | ticks_live | NON_RECOVERABLE | 0 cited, 0 pinned |
| U007 | SENSEX (BSE) 1m+1d candles | INDEX_SPOT | REQUIRED_ENGINE | upstox | 1m,1D | index_1m | RECOVERABLE | 1 cited, 1 pinned |
| U008 | NIFTY FIN SERVICE 1m+1d candles | INDEX_SPOT | OPTIONAL_KEEP | upstox | 1m,1D | index_1m | RECOVERABLE | 0 cited, 0 pinned |
| U009 | NIFTY MID SELECT 1m+1d candles | INDEX_SPOT | OPTIONAL_KEEP | upstox | 1m,1D | index_1m | RECOVERABLE | 0 cited, 0 pinned |
| U010 | NIFTY near-month future 1m candles + OI + traded volume | NIFTY_FUTURES | REQUIRED_ENGINE | upstox | 1m,5m,1D | fut_1m | RECOVERABLE | 4 cited, 4 pinned |
| U011 | NIFTY monthly+next-month future live ticks/depth/OI | NIFTY_FUTURES | REQUIRED_ENGINE | upstox | tick,1m | ticks_depth_live | NON_RECOVERABLE | 2 cited, 2 pinned |
| U012 | BANKNIFTY near-month future live ticks | NIFTY_FUTURES | REQUIRED_OWNER | kite | tick | ticks_live | NON_RECOVERABLE | 0 cited, 0 pinned |
| U013 | NIFTY options live ticks/depth, monthly + weekly ATM band | NIFTY_OPTIONS | REQUIRED_ENGINE | kite | tick,1m | ticks_depth_live | NON_RECOVERABLE | 3 cited, 3 pinned |
| U014 | NIFTY option chain snapshots (opt_chain_1m, greeks_1m, opt_snapshot_live, opt_summary_1m, opt_atm_1m, opt_depth_1m) | NIFTY_OPTIONS | REQUIRED_ENGINE | upstox | 1m | opt_chain_1m | NON_RECOVERABLE | 1 cited, 1 pinned |
| U015 | NIFTY option contracts 1m OHLC history (live + expired) | NIFTY_OPTIONS | REQUIRED_OWNER | upstox | 1m | opt_ohlc_1m | NON_RECOVERABLE | 1 cited, 1 pinned |
| U016 | BANKNIFTY options (monthly) live ticks | NIFTY_OPTIONS | OPTIONAL_ADD | kite | tick | ticks_live | NON_RECOVERABLE | 0 cited, 0 pinned |
| U017 | SENSEX / BSE F&O options | NIFTY_OPTIONS | DROP |  |  | ticks_live | NON_RECOVERABLE | 0 cited, 0 pinned |
| U018 | GIFT NIFTY daily candles | PREMARKET_GAP | REQUIRED_ENGINE | dhan | 1D | gift_nifty_1d | RECOVERABLE | 2 cited, 2 pinned |
| U019 | GIFT NIFTY live overnight / pre-open ticks | PREMARKET_GAP | REQUIRED_ENGINE | dhan | tick,1m | gift_nifty_ticks | NON_RECOVERABLE | 2 cited, 2 pinned |
| U020 | NIFTYBEES daily candles | ETF | OPTIONAL_KEEP | upstox | 1D | niftybees_1d | RECOVERABLE | 0 cited, 0 pinned |
| U021 | NIFTYBEES live ticks | ETF | REQUIRED_OWNER | kite | tick | ticks_live | NON_RECOVERABLE | 0 cited, 0 pinned |
| U022 | USDINR spot daily (Yahoo INR=X) | MACRO | REQUIRED_ENGINE | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U023 | USDINR NSE currency future (live or daily) | MACRO | UNKNOWN |  |  | ticks_live | NON_RECOVERABLE | 0 cited, 0 pinned |
| U024 | MCX CRUDEOIL + GOLD near-month futures daily | MACRO | REQUIRED_ENGINE | dhan | 1D | macro_futures_1d | RECOVERABLE | 1 cited, 1 pinned |
| U025 | USDINR / MCX live ticks (Kite TICK_EXTRA_MACRO) | MACRO | DROP |  |  | ticks_live | NON_RECOVERABLE | 0 cited, 0 pinned |
| U026 | ASX200 daily (Yahoo ^AXJO) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U027 | BITCOIN daily (Yahoo BTC-USD) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U028 | BRENT daily (Yahoo BZ=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U029 | CAC daily (Yahoo ^FCHI) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U030 | COPPER daily (Yahoo HG=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U031 | DAX daily (Yahoo ^GDAXI) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U032 | DOW daily (Yahoo ^DJI) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U033 | DXY daily (Yahoo DX-Y.NYB) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U034 | EURUSD daily (Yahoo EURUSD=X) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U035 | FTSE daily (Yahoo ^FTSE) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U036 | GOLD daily (Yahoo GC=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U037 | HANGSENG daily (Yahoo ^HSI) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U038 | KOSPI daily (Yahoo ^KS11) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U039 | NASDAQ daily (Yahoo ^IXIC) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U040 | NIKKEI daily (Yahoo ^N225) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U041 | RUSSELL2000 daily (Yahoo ^RUT) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U042 | SHANGHAI daily (Yahoo 000001.SS) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U043 | SILVER daily (Yahoo SI=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U044 | SP500 daily (Yahoo ^GSPC) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U045 | US10Y daily (Yahoo ^TNX) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U046 | US2Y daily (Yahoo ^IRX) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U047 | USDINR daily (Yahoo INR=X) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U048 | USDJPY daily (Yahoo JPY=X) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U049 | VIX_US daily (Yahoo ^VIX) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U050 | WTI daily (Yahoo CL=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 0 cited, 0 pinned |
| U051 | World markets intraday 1m (Yahoo) | WORLD_MARKETS | REQUIRED_ENGINE | yahoo |  | global_1m | NON_RECOVERABLE | 3 cited, 3 pinned |
| U052 | FII/DII daily | NSE_REPORT | REQUIRED_ENGINE | nse | 1D | fii_dii_daily | RECOVERABLE | 2 cited, 2 pinned |
| U053 | Participant OI daily | NSE_REPORT | REQUIRED_OWNER | nse | 1D | participant_oi_daily | RECOVERABLE | 0 cited, 0 pinned |
| U054 | Derivative activity daily | NSE_REPORT | OPTIONAL_KEEP | nse | 1D | derivative_activity | RECOVERABLE | 1 cited, 1 pinned |
| U055 | Market daily | NSE_REPORT | OPTIONAL_KEEP | nse | 1D | market_1d | RECOVERABLE | 0 cited, 0 pinned |
| U056 | Breadth daily (NSE advance/decline) | NSE_REPORT | OPTIONAL_KEEP | nse | 1D | breadth_1d | RECOVERABLE | 1 cited, 1 pinned |
| U057 | Corporate actions (NSE/Yahoo) | NSE_REPORT | OPTIONAL_KEEP | nse | 1D | corporate_actions | RECOVERABLE | 0 cited, 0 pinned |
| U058 | Trading holidays / calendar | NSE_REPORT | REQUIRED_OWNER | nse | 1D | trading_holidays | RECOVERABLE | 1 cited, 1 pinned |
| U059 | Sector indices 1m (sector_1m) | SECTOR | DROP |  |  | sector_1m | RECOVERABLE | 0 cited, 0 pinned |
| U060 | upstox instrument master (daily snapshot) | INSTRUMENT_MASTER | REQUIRED_OWNER | upstox | 1D | instrument_master | NON_RECOVERABLE | 1 cited, 1 pinned |
| U061 | dhan instrument master (daily snapshot) | INSTRUMENT_MASTER | REQUIRED_ENGINE | dhan | 1D | instrument_master | NON_RECOVERABLE | 2 cited, 2 pinned |
| U062 | kite instrument master (daily snapshot) | INSTRUMENT_MASTER | REQUIRED_OWNER | kite | 1D | instrument_master | NON_RECOVERABLE | 1 cited, 1 pinned |
| U063 | fyers instrument master (daily snapshot) | INSTRUMENT_MASTER | REQUIRED_OWNER | fyers | 1D | instrument_master | NON_RECOVERABLE | 1 cited, 1 pinned |
| U064 | Index membership (NIFTY 50 list) | NSE_REPORT | REQUIRED_ENGINE | nse | 1D | index_membership | NON_RECOVERABLE | 1 cited, 1 pinned |
| U065 | Domestic news by NIFTY 50 constituent | NEWS | REQUIRED_OWNER | upstox | event | news_items | NON_RECOVERABLE | 0 cited, 0 pinned |
| U066 | International news | NEWS | NOT_AVAILABLE_AT_RETAIL |  |  | news_items | NON_RECOVERABLE | 0 cited, 0 pinned |
| U067 | Event calendar (RBI / FOMC / CPI) - manual | EVENTS | REQUIRED_ENGINE | manual | event | event_calendar | NON_RECOVERABLE | 2 cited, 2 pinned |
| U068 | ADANIENT 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U069 | ADANIENT live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U070 | ADANIPORTS 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U071 | ADANIPORTS live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U072 | APOLLOHOSP 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U073 | APOLLOHOSP live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U074 | ASIANPAINT 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U075 | ASIANPAINT live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U076 | AXISBANK 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U077 | AXISBANK live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U078 | BAJAJ-AUTO 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U079 | BAJAJ-AUTO live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U080 | BAJFINANCE 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U081 | BAJFINANCE live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U082 | BAJAJFINSV 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U083 | BAJAJFINSV live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U084 | BEL 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U085 | BEL live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U086 | BHARTIARTL 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U087 | BHARTIARTL live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U088 | CIPLA 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U089 | CIPLA live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U090 | COALINDIA 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U091 | COALINDIA live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U092 | DRREDDY 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U093 | DRREDDY live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U094 | EICHERMOT 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U095 | EICHERMOT live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U096 | ETERNAL 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U097 | ETERNAL live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U098 | GRASIM 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U099 | GRASIM live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U100 | HCLTECH 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U101 | HCLTECH live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U102 | HDFCBANK 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U103 | HDFCBANK live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U104 | HDFCLIFE 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U105 | HDFCLIFE live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U106 | HINDALCO 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U107 | HINDALCO live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U108 | HINDUNILVR 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U109 | HINDUNILVR live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U110 | ICICIBANK 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U111 | ICICIBANK live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U112 | INDIGO 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U113 | INDIGO live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U114 | INFY 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U115 | INFY live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U116 | ITC 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U117 | ITC live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U118 | JIOFIN 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U119 | JIOFIN live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U120 | JSWSTEEL 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U121 | JSWSTEEL live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U122 | KOTAKBANK 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U123 | KOTAKBANK live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U124 | LT 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U125 | LT live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U126 | M&M 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U127 | M&M live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U128 | MARUTI 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U129 | MARUTI live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U130 | MAXHEALTH 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U131 | MAXHEALTH live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U132 | NESTLEIND 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U133 | NESTLEIND live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U134 | NTPC 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U135 | NTPC live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U136 | ONGC 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U137 | ONGC live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U138 | POWERGRID 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U139 | POWERGRID live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U140 | RELIANCE 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U141 | RELIANCE live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U142 | SBILIFE 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U143 | SBILIFE live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U144 | SBIN 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U145 | SBIN live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U146 | SHRIRAMFIN 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U147 | SHRIRAMFIN live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U148 | SUNPHARMA 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U149 | SUNPHARMA live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U150 | TATACONSUM 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U151 | TATACONSUM live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U152 | TMPV 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U153 | TMPV live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U154 | TATASTEEL 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U155 | TATASTEEL live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U156 | TCS 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U157 | TCS live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U158 | TECHM 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U159 | TECHM live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U160 | TITAN 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U161 | TITAN live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U162 | TRENT 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U163 | TRENT live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U164 | ULTRACEMCO 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U165 | ULTRACEMCO live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U166 | WIPRO 1m candles | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | upstox | 1m,1D | equity_1m | RECOVERABLE | 2 cited, 2 pinned |
| U167 | WIPRO live ticks | NIFTY50_CONSTITUENT | REQUIRED_ENGINE | kite | tick,1m | ticks_live | NON_RECOVERABLE | 1 cited, 1 pinned |
| U168 | Sector indices 1m (NIFTY BANK/IT/FIN/AUTO/PHARMA/FMCG/METAL/ENERGY/REALTY and siblings) | INDEX_SPOT | REQUIRED_ENGINE | fyers | 1m | index_1m | RECOVERABLE | 2 cited, 2 pinned |
| U169 | NIFTY MIDCAP 100 + NIFTY NEXT 50 index 1m | INDEX_SPOT | REQUIRED_ENGINE | fyers | 1m | index_1m | RECOVERABLE | 2 cited, 2 pinned |
| U170 | GIFT NIFTY 1m (pre-market gap cue) | GLOBAL_CUE | REQUIRED_ENGINE | upstox | 1m | global_cues_1m | NON_RECOVERABLE | 2 cited, 2 pinned |
| U171 | Upstox GLOBAL_INDEX / INDICATOR 1m series | GLOBAL_CUE | REQUIRED_ENGINE | upstox | 1m | global_cues_1m | NON_RECOVERABLE | 2 cited, 2 pinned |
| U172 | NSE F&O UDiFF bhavcopy, NIFTY contracts (daily) | NSE_REPORT | REQUIRED_ENGINE | nse | 1D | fo_bhav_nifty_daily | RECOVERABLE | 1 cited, 1 pinned |
| U173 | participant_vol (NSE participant volume, daily) | NSE_REPORT | REQUIRED_ENGINE | nse | 1D | participant_vol | RECOVERABLE | 1 cited, 1 pinned |
| U174 | CM bhavcopy / MTO delivery files (daily) | NSE_REPORT | REQUIRED_ENGINE | nse | 1D | bhavcopy | RECOVERABLE | 2 cited, 2 pinned |
| U175 | india_macro (RBI / macro series, manual curated) | MACRO | REQUIRED_ENGINE | manual | 1D | india_macro | NON_RECOVERABLE | 1 cited, 1 pinned |
| U176 | BANKNIFTY futures daily | FUTURES | REQUIRED_ENGINE | dhan | 1D | fut_1d | NON_RECOVERABLE | 1 cited, 1 pinned |

## PART 2: OPUS AUDIT ROUND 1 (FAIL as written)
# Adversarial audit: is the DATA-NEEDED list safe to govern a live-only pull policy? (05-11-2026)
Auditor: Claude Opus 5.5 (claude-opus-5-5), independent. Read-only; scripts in /tmp/audit (fwd.py, rev.py, sim.py).

## Verdict: FAIL as written; PASS-WITH-FIXES once the 6 ADD rows below and fixes D1-D4 are in.
The live-only gate itself is built safely (`pullers/dhan/dp_liveonly.py:244-266`: it refuses only a key that is listed NOT_NEEDED **and** RECOVERABLE, and UNKNOWN or unlisted keys are allowed). But the list misses inputs the code reads, and the gate's recoverability test is wrong for window-limited intraday data (D2).

## 1. Forward proof
The file has 167 rows, not 165, and 215 citations. All 215 file:line citations exist. 197 contain their cite token at that line. 10 cite CLAUDE.md only, with no code reader. 18 rows have no consumer. Six citations exist but do not read what the row claims:
* U022-U050 (Yahoo daily) cite `global_cues.py:84`. That line reads `global_cues_1m`, which is built from **1m** Upstox GLOBAL_* and Yahoo bars (`tools/global_wire.py:144-161`). Only 16 series feed it. ASX200, BTC, COPPER, EURUSD, KOSPI, NASDAQ, RUT, SSE, SILVER, US2Y, USDJPY and VIX_US daily feed nothing there.
* U022 cites `global_cues.py:38`, which is a label tuple, not a read.
* U024 (MCX) cites `global_cues.py:84`. The real reader is `global_context.py:231` (`macro_1d`).
* U064 cites `constituents_top20.py:216` (`_prior_session`). That code reads no membership: the list is the static `config/nifty50.py`.
* U013/U014 cite `regime_6m_build.py:69` (`options_chain_summary`). That table's history comes from the **NSE F&O bhavcopy** (`daily_recorder.py:90`); only today's row comes from live snapshots (`daily_writers.py:235`).

## 2. Reverse proof: inputs the code reads that no row covers
| Input | Read at | Classifier today | Recoverable? |
|---|---|---|---|
| Sector indices + NIFTY MIDCAP 100 + NIFTY NEXT 50, 1m (`index_1m`) | `derived_wide.py:452-489` (datasets 109/110/112/115); `feature_compute_full.py:890` | NOT_NEEDED (bulk reason 1) | Only inside the broker window (Fyers 100 d); older minutes are lost |
| GIFT NIFTY **1m** (Upstox `GLOBAL_INDEX\|SGX NIFTY`) + Upstox GLOBAL_INDEX/INDICATOR 1m (DJI, SPX, BRENT, WTI, USDINR...) | `global_wire.py:89-103,144` -> `global_cues.py:84`, `regime_forecast2_export.py:38` | UNKNOWN or NOT_NEEDED, depending on the master (sim.py: master name "SGX NIFTY" gives NOT_NEEDED) | Unproven |
| Yahoo 1m DXY / US10Y / GOLD (U051 = DROP) | `global_wire.py:147-150` | outside the coverage ledger | **No**: Yahoo serves ~30 d, then lost |
| NSE F&O bhavcopy (NIFTY contracts) | `eod_pit.py:156`, `options_context.py` (judge gate 18, `judge_engine.py:106`), `options_chain_summary` | NOT_NEEDED ("duplicates broker candles", which is false: broker candles have no EOD OI of expired strikes); `fo_bhavcopy` snap = UNKNOWN | Yes (NSE archive) |
| participant_vol | `eod_pit.py:130` | NOT_NEEDED (`needed_vs_pulled.py:49`) | Yes (NSE archive, 2012+) |
| CM bhavcopy / MTO delivery, `india_macro` | `eod_pit.py:218,229,242` | no row | Yes / manual |
| BANKNIFTY future daily | `global_context.py:55,224` | NOT_NEEDED | Yes, within the window |
| MCX crude/gold daily (U024 = OPTIONAL_KEEP) | `global_context.py:231` | NOT_NEEDED: the classifier treats every non-NIFTY future as unneeded, which contradicts U024 | Expired months: no (Dhan serves only active contracts) |

These are covered: VIX pre-2025 fallback (U010 futures realized vol), `fut_1m traded_volume` (U010), all 50 constituents (they match `config/nifty50.py` exactly), holidays (U058), event calendar (U067), masters (U060-063), and the NIFTY option chain (U014). Native 5m/15m is never read: `mtf_regime_engine.py:136`, `regime_spine.py:235,311` and `multi_timeframe.py:170` all resample 1m or daily data. U054/U055 say "nothing reads it", but `eod_pit.py:280` reads `derivative_activity`.

## 3. The five NOT_NEEDED bulk reasons
1. Unnamed indices: **NOT SAFE**. Sector indices, MIDCAP 100 and NEXT 50 are read (table above). Recoverable only inside the broker window.
2. NSE contract-level daily: **NOT SAFE** unless `tools/nse_reports.py` (the lake) keeps fetching the FO UDiFF files, because the engine's copy is built from the lake (`nse_eod_copy.py`). Recoverable from the NSE archive.
3. Equities outside the NIFTY 50: **SAFE today**, but the list is static. At the next NIFTY 50 rebalance an entering stock's ticks are lost for good and its 1m is recoverable only within the window. Needs a rule that follows `index_membership`.
4. Fyers 5s-45s: **SAFE** (no reader). But the gate calls them RECOVERABLE without any probe, so stopping them is an owner decision to lose them for good.
5. Stock F&O / MCX: **SAFE for stock F&O. NOT SAFE for MCX crude/gold and BANKNIFTY futures**, which `global_context` reads.

## 4. Ranked defects
* **D1 (high).** Sector, MIDCAP 100 and NEXT 50 1m will be refused. Loss: all derived_wide 109/110/112/115 history older than ~100 days.
* **D2 (high).** `dp_liveonly.class_name_for` (`:229-241`) maps every non-NSE, non-expired job to `history_candles_<src>_<iv>`, so it always returns RECOVERABLE. That bypasses `recoverability.json`'s `window_limited_intraday` rule (global_1m, opt_ohlc_1m) and probes no window. Loss: any window-limited key listed NOT_NEEDED (Yahoo/Upstox global 1m, Fyers seconds) is gone for good.
* **D3 (high).** No GIFT 1m row (U018 is 1D only, U019 is ticks), and U051 is DROP. Loss: the GIFT/DXY/US10Y/brent inputs of the gap cue. `global_cues_1m` has been stale since 16-10 (`lc_families.py:466`), so this loss has already started.
* **D4 (medium).** No rows for the F&O bhavcopy, participant_vol, delivery/MTO or `india_macro`, which feed the edge-research reader (`eod_pit` -> `edge_ladder.py:157`) and judge gate 18.
* **D5 (medium).** The classifier contradicts its own rows: MCX (U024), and GIFT detection depends on the master's name text, not on the U018 key.
* **D6 (low).** Wrong citations (section 1). U015 names no strike band, so a puller that follows the list cannot know which strikes to pull.

## 5. Rows to ADD
1. NSE sector indices + NIFTY MIDCAP 100 + NIFTY NEXT 50, 1m (`index_1m`), REQUIRED_ENGINE.
2. GIFT NIFTY 1m + Upstox GLOBAL_INDEX/INDICATOR 1m, REQUIRED_ENGINE, window-limited.
3. Yahoo 1m DXY / ^TNX / GC=F (change U051 from DROP to REQUIRED_ENGINE), NON_RECOVERABLE.
4. NSE F&O UDiFF bhavcopy (NIFTY contracts) + participant_vol + CM bhavcopy/MTO delivery + `india_macro`.
5. BANKNIFTY near-month future 1d; MCX crude/gold daily (make the classifier honour U024).
6. A membership-follow rule: the constituent rows equal `index_membership` of the prior session, not a static 50.

## 6. Unproven
* The Upstox master names for the GLOBAL_* keys. The masters were not in /tmp/board, and the upstox DBs on i5 have no `instruments` table.
* Per-broker windows for index 1m, Fyers seconds and Upstox global 1m.
* Whether `tools/nse_reports.py` falls under the stop policy.
* No `pull_policy.json` is deployed yet (the i5 `_state` directory holds none), so nothing has been refused so far.
* GB/day of live data, which the coverage ledger does not see.

## PART 3: OPUS AUDIT ROUND 2 (PASS-WITH-FIXES)
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

## PART 4: FABLE AUDIT (no new feed needed, ~75%, no edge demonstrated)
# Is MORE data needed for the NIFTY intraday DIRECTION engine? (05-11-2026)
Auditor: Claude Fable 5.1 (claude-fable-5-1), independent, read-only. No box DB was reachable (local `data/blpro_working.db` is an 81 KB stub); table contents come from repo docs, not re-measured.

## Answer
**NO new feed is needed now. The list covers everything the direction engine reads. No intraday direction edge has been shown on data already held, so collection is not the bottleneck; the real gaps are data QUALITY (constituent bars) and PLACEMENT (chain snapshots on a full SSD).** Confidence ~75%. Two cheap items are worth adding later (section 2).

## 1. What the engine reads vs the list
| Input (reader file:line) | Row | Covered |
|---|---|---|
| `nifty_1m` (`feature_compute_full.py:221`, `derived_wide.py:370`, `mtf_regime_engine.py:132`) | U001 | yes |
| `vix_1m` (`feature_compute_full.py:242`, `market_state.py:114`, `global_context.py:216`) | U003/4 | yes |
| `fut_1m` close/vol/OI (`feature_compute_full.py:261`, `market_state.py:126`; judge gate 17) | U010/11 | yes |
| `opt_chain_1m`, `opt_atm_1m` OI/IV/PCR (`feature_compute_full.py:298`, `derived_wide.py:507,555`, `market_state.py:121-124`) | U013/14 | yes; U014 "NOT RECORDED by the new set", old pullers hold ~15M rows in `rows_raw` on SSD |
| `equity_1m`, `breadth_1m` (`feature_compute_full.py:311`, `wired_readings.py:76`) | U068-167 | on paper. **Contradiction:** `feature_compute_full.py:50` blocks f151-f167 because "equity_1m records ETFs, NOT constituents (known defect)". Unresolved |
| `index_1m` sectors/MIDCAP/NEXT50/BANK/SENSEX (`feature_compute_full.py:323`, `derived_wide.py:317-352`) | U005/7/168/169 | yes |
| `expiry_calendar` (`derived_wide.py:414`), holidays | U058/60-63 | yes |
| `global_cues_1m` <- Upstox GLOBAL + Yahoo 1m (`global_cues.py:84`, `global_wire.py:495`) | U051/170/171 | yes; stale since 16-10 |
| `depth_top_1m` (`wired_readings.py:81`), `broker_quote_depth_snap` (`live_snap.py:82`) | U011/13 raw | yes |
| EOD: participant OI/vol, F&O bhav, delivery, `india_macro`, `breadth_1d`, `derivative_activity` (`eod_pit.py:80-280`); `options_chain_summary` (`options_context.py`, gate 18) | U052-58, 172-175 | yes |
| `fut_1d`, `macro_1d` (`global_context.py:224,231`); `institutional_flow_eod`, `event_calendar` (`institutional_flow.py:180,189`) | U176/24/52/67 | yes |
| News RSS (`news_engine.py`, display-only) | U065 | no decision reader |
| `preopen_snap` (`db_completeness.py:132`; `task_runner.py:1399` "no source") | none | NOT covered, no reader |
| Block/bulk deals (`flow_engine.py:149`; SCE vote `signal_consensus_engine.py:376`) | none | NOT covered; vote runs on nothing |

`ml_consensus_engine.py:200-238` features are NIFTY OHLC indicators plus hour/dow; `meta_label.py:35` uses confidence, vix, hour, atr_pct, regime, votes. The ML path consumes none of the options, breadth or global tables it could.

## 2. Extra data a retail model might want (not read, not listed)
| Item | Retail source | Recoverable | Storage (est.) | Direction value, evidence | Verdict |
|---|---|---|---|---|---|
| Chain OI/IV/Greeks snapshots | Upstox/Dhan (1 req/3 s)/Fyers; `dp_snap.py:1048` in-session cadence | live-only | ~15M rows/box held | PCR corr -0.02/-0.04 FLAT; max-pain only dte<=2 (`options_context.py:15-40`) | already captured; move to HDD, no 2nd feed |
| IV term / skew across expiries | weekly+monthly chains now recorded (U013) | live-only, held | none new | `derived_wide` BLOCKED 068 is a writer gap | SKIP (build writer) |
| Depth imbalance | Kite 5/Dhan 20+200/Upstox 30/Fyers 50, recording | live-only | 0.2-1.4 GB/day per feed | seconds-scale in literature; no repo test | covered, SKIP more |
| 50-constituent breadth, sector rotation | Kite ticks + Upstox/Fyers 1m | window-limited | small | plausible; blocked in code by ETF defect | fix quality first |
| USDINR/crude/gold intraday | Kite CDS/MCX (entitlement UNKNOWN, off) | live-only | small | weak plausibility | ADD LATER after a one-box probe |
| GIFT intraday | Dhan IDX 5024 / Upstox GLOBAL, unproven | live-only | tiny | measured: gap leg t=12.7, intraday leg +4.78 pts t=1.02 (EDGE_GIFTNIFTY 02-11) | daily covered; intraday SKIP |
| Pre-open auction (indicative price/qty) | Dhan CAS (B2), broker quotes 09:07-09:14; NSE terms unread | live-only | KB/day | plausibility only, no test, no reader | ADD LATER (cheap) |
| FII/DII, participant OI | NSE reports | archive | tiny | EOD, flat in lead-lag tests | covered |
| Bulk/block deals | NSE EOD CSV | archive | tiny | stock-level, EOD | SKIP |
| Heavyweight results dates | NSE/BSE, manual | archive | tiny | event flag only | ADD LATER into event_calendar |
| News sentiment | RSS live; Upstox news 7-day | live-only | small | lexicon, unproven | SKIP |

## 3. Was any edge demonstrated? No.
Every pre-registered intraday test is null: E1/E2 momentum, E4 gap, E5 ORB, 6-rule study (0/6), E3/E7 straddle (net t 0.16-0.76), E8 GEX trade (net negative), GIFT intraday (t=1.02). Direction AUC 0.52; regime calibration FAIL on every horizon (04-11); regime_6m worse than a random side (-2.67 vs -1.85 pts); REGIME_FORECAST2: move/quiet skill, "no direction skill". The one positive (variance-gap, synthetic option) is volatility, not direction. i5 SSD: 11 GB free of 205. New feeds add bytes, not evidence.

**Would change my mind:** a model on the held f001-f490 set whose error is explained by a feature NULL for a data reason; proof equity_1m still holds ETFs; a 60-session pre-open imbalance test with a signed open-to-10:00 effect.
