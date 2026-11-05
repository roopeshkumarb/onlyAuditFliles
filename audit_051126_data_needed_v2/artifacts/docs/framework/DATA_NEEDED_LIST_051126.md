# DATA NEEDED LIST (05-11-2026) - what the engines read, per row

Source of truth: `config/retailer_edge_universe.json` (176 rows). **Status: NOT yet proven or audited.** An Opus audit on 05-11 found it incomplete; 9 rows were added (U168-U176) and 3 corrected; a second audit and an external audit are pending. Broker ids for the added rows are unproven.

Decision values: REQUIRED_* = must be pulled; OPTIONAL_KEEP = keep if cheap; DROP = not read by any engine. `cites` = code lines that read it (pinned = registered in tests/fixtures/universe_cite_pins.json).

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
| U026 | ASX200 daily (Yahoo ^AXJO) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U027 | BITCOIN daily (Yahoo BTC-USD) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U028 | BRENT daily (Yahoo BZ=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U029 | CAC daily (Yahoo ^FCHI) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U030 | COPPER daily (Yahoo HG=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U031 | DAX daily (Yahoo ^GDAXI) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U032 | DOW daily (Yahoo ^DJI) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U033 | DXY daily (Yahoo DX-Y.NYB) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U034 | EURUSD daily (Yahoo EURUSD=X) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U035 | FTSE daily (Yahoo ^FTSE) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U036 | GOLD daily (Yahoo GC=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U037 | HANGSENG daily (Yahoo ^HSI) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U038 | KOSPI daily (Yahoo ^KS11) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U039 | NASDAQ daily (Yahoo ^IXIC) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U040 | NIKKEI daily (Yahoo ^N225) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U041 | RUSSELL2000 daily (Yahoo ^RUT) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U042 | SHANGHAI daily (Yahoo 000001.SS) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U043 | SILVER daily (Yahoo SI=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U044 | SP500 daily (Yahoo ^GSPC) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U045 | US10Y daily (Yahoo ^TNX) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U046 | US2Y daily (Yahoo ^IRX) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U047 | USDINR daily (Yahoo INR=X) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U048 | USDJPY daily (Yahoo JPY=X) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U049 | VIX_US daily (Yahoo ^VIX) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
| U050 | WTI daily (Yahoo CL=F) | WORLD_MARKETS | REQUIRED_OWNER | yahoo | 1D | global_daily | RECOVERABLE | 1 cited, 1 pinned |
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
