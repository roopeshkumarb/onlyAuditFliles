# BL PRO / ZERO: PROJECT-SPECIFIC REGIME & DATA ARCHITECTURE
# Date: 03-11-2026 | Status: ACTIVE REALITY | Replaces all theoretical specs

## 1. THE HARD REALITY (Proven by Audit)
This engine operates under strict retail constraints. We do not chase institutional ghosts. 
* **NO** signed option order flow (aggressor side).
* **NO** dealer gamma / GEX (NSE account-type data is unavailable).
* **NO** intraday FII/DII positions (EOD only).
* **NO** historical tick-by-tick depth (capture-forward only, stored on HDD RAID).

### 1.1 The Data Horizon (Measured)
* **Nifty 1m (`market_1m`):** 2022-01-03 to present.
* **India VIX (`vix_1m`):** 2025-08-11 to present (~14.7 months). *Fallback required for older backtests.*
* **Options 1m (`opt_ohlc_1m`):** 2025-09-15 to present (~13.5 months).
* **Futures 1m (`fut_1m`):** 2024-10-01 to present.
* **Trading Holidays (`trading_holidays`):** Degrades to **"Tuesday rule only"** if the `NSE holiday-master FO` src is unreadable or missing.

### 1.2 The Source Priority (Code-Read)
The engine must respect the established `SRC_ORDER` for bar construction:
`("upstox_live", "upstox_expired", "fyers_backfill", "dhan", "fyers_live", "fyers_live+upstox_oi", "fyers_live+dhan_oi")`

---

## 2. REGIME ENGINE INTEGRATION (Codebase Specific)

The Regime Engine is not a standalone black box; it must integrate with the existing `BL Pro` / `ZERO` pipeline (`ml_consensus_engine.py`, `meta_label.py`, `judge_engine.py`).

### 2.1 Time & Expiry Handling (Critical Bug Fix Area)
* **The DTE Decay Rule:** The simulator (`_reprice`) mandates that exit MUST decay the SAME `dte` the entry was priced with. `t_x = max((dte - held / 375.0) / 365.0, _MIN_T)`. The regime engine must pass accurate `days_to_expiry` to prevent phantom time-value PnL.
* **The Tuesday Rule Fallback:** If `nse_calendar.py` cannot read `trading_holidays` (src `NSE holiday-master FO`), expiry dating falls back to "Tuesday rule only". The regime engine must flag `expiry_confidence = LOW` on these days and increase the `NO_TRADE` threshold.
* **Regime Lookback:** The codebase defines `LOOKBACK_DAYS = 126` (~6 months). The regime classifier must be trained on rolling 126-day windows, not static historical buckets.

### 2.2 Feature Engineering (Restricted to Held Data)
* **Volume Proxy:** `market_1m` volume is the *NIFTY INDEX volume* (vendor aggregate, Kite/Upstox send 0). It must NOT be used for VWAP/OBV. VWAP/OBV must use `fut_1m` traded volume (`traded_volume` column), NaN where unmeasured.
* **Volatility Regime:** Since `vix_1m` only goes back to Aug 2025, pre-2025 backtests must use `fut_1m` realized volatility (rolling 20m/60m standard deviation) as the primary regime volatility feature.
* **Breadth:** Computed from `equity_1m` (Top 20 constituents). If `breadth_1m` feed stops (as seen on 10-30), the engine must rely on raw `equity_1m` calculations.

---

## 3. HARDWARE & STORAGE TOPOLOGY (H12 Compliance)

Data placement is dictated by **recoverability**, not convenience.

| Data Type | Storage Medium | Box | Rationale |
| :--- | :--- | :--- | :--- |
| **Broker Candles** (1m, daily, expired chains) | **SSD** (WAL mode) | i5, i7 | Recoverable via API. High IO required for backtests. |
| **Live Ticks / Depth / Chain Snapshots** | **HDD RAID1** | i5, i7 | **NON-RECOVERABLE**. Once missed, gone forever. |
| **Paper State / Journal** (`sim_state.json`) | **SSD** | i5, i7 | Own output, but critical for same-day restore. |
| **Event Calendar** (`event_calendar.yaml`) | **SSD + Cloud Sync** | i5, i7, Pi5 | Manual curation. Must survive box death. |
| **Pi5 Storage** | **SSD ONLY** | Pi5 | USB HDD is unmounted/unverified. Pi5 holds NO non-recoverable data. |

### 3.1 The IO Gate Rule
* The IO Gate **MONITORS ONLY**. It **NEVER** stops the pullers. 
* If HDD RAID1 IO pressure > 80, defer backtest/ML training jobs. Do not throttle live tick ingestion.

---

## 4. KNOWN CODEBASE DEFECTS TO RESOLVE FIRST

Before training the ML Regime Classifier, these audit-proven defects must be patched:

1. **Phantom PnL Journal:** `journal.record_sim_close()` is currently firing from `sim_on_bar()` even when the simulator is disabled, showing massive fake losses in the UI. *Fix: Gate strictly behind `self.sim_enabled`.*
2. **VIX Stale Fallback:** `meta_label.py` defaults VIX to `0.5` if missing (`float(vix) / 30.0 if vix is not None else 0.5`). *Fix: Trigger a `DATA_STALE` flag and reduce model confidence rather than feeding a fake neutral VIX.*
3. **Orphaned Paper Tables:** `paper_positions`, `paper_orders`, `paper_exits` in `blpro_working.db` are mostly empty/dead (`PP:X3`). *Fix: Clean up schema or route paper state strictly through `sim_state.json`.*
4. **ML Gate Hold:** `_ml_allowed` is tied to `ML_ON_HOLD` and `trade_control.state().get("ml_vote")`. Ensure the regime engine's output is correctly formatted to pass through this gate without triggering a silent refusal.

---

## 5. THE "CHEAP ADDITIONS" PULLER LIST

To improve regime accuracy without breaking broker limits, add these to the `ZERO` puller framework:

1. **GIFT NIFTY (Upstox):** Pre-market gap signal. (Find `instrument_key` in Upstox master).
2. **NIFTY BEES (Any Broker):** ETF vs Futures divergence. (Standard equity endpoint).
3. **USDINR / MCX Crude / Gold (Fyers/Dhan):** Macro stress overlay. (Currency/Commodity segments).
4. **Manual Event Calendar:** Create `data/event_calendar.yaml` for RBI, FOMC, CPI. *No broker provides this.*

---

## 6. FINAL DIRECTIVE FOR CLAUDE CODE

When working on this project, Claude must:
1. **Never suggest institutional data** (GEX, signed flow, intraday FII).
2. **Always check the `SRC_ORDER`** before proposing a new data source.
3. **Respect the "Tuesday Rule"** when dealing with expiry dating logic.
4. **Enforce HDD vs SSD separation** based on recoverability.
5. **Run read-only SQL queries** on `blpro_working.db` to verify table existence before claiming a dataset is "held".
