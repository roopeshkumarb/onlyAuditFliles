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
