# Regime-Detection Data Need — Audit of the Existing Build

**Date:** 04-11-2026
**Scope:** intraday regime detection across multiple timeframes ONLY — `domain/engines/mtf_regime_engine.py`,
`domain/engines/adaptive_regime_engine.py`, `domain/engines/regime_valves_engine.py`,
`domain/engines/judge_engine.py`, plus the four tools that fit/measure the regime calibration
(`tools/fit_regime_calibration.py`, `tools/measure_regime_horizons.py`, `tools/fit_regime_weights.py`,
`tools/calibration_regime_stack.py`). This is NOT a data wishlist. Every row below is something the
EXISTING code reads, cited by file:line. Nothing recommends new data.

Method: read every file named above end-to-end, grepped the whole repo for `LOOKBACK_DAYS`,
`market_1m`/`vix_1m`/`opt_chain_1m`/`fut_1m`/`trading_holidays`/`derived_1m`/`labels_1m` inside the
four engine files, and opened the two measured JSON assets (`regime_percentiles_mtf.json`,
`regime_calibration_report.json`) plus `regime_percentiles.json`, `regime_calibration_map.json`,
`regime_weights_report.json` to read the actual numbers rather than restate the brief.

---

## 1. What the code actually reads

### 1.1 The classifiers (the only two files that touch raw data)

| # | Input | Reader (file:line) | What it is | Held span (per CLAUDE.md / measured) | Sufficient for `LOOKBACK_DAYS=126` (~6mo)? |
|---|---|---|---|---|---|
| 1 | `df['close']` / `df[open,high,low,close]`, DatetimeIndex or `dt`/`ts` column — the 1-minute bar frame already held in memory, resampled to `30min/60min/120min/1D` | `domain/engines/mtf_regime_engine.py:59-64` (`TIMEFRAMES` tuple), `:108-131` (`classify`, builds the index, resamples at `:136`) | NIFTY 1-minute OHLC (`market_1m`/`nifty_1m` per CLAUDE.md §1.1 — the file itself never names a table, it takes whatever `df` the caller hands it) | working DB: 2022-01-03→present (~4.8y); archive `niftybkp.db`: 2008-01-01→present, 1.78M rows (cited, not independently reachable) | YES — both spans are >> 126 days |
| 2 | Same 1-minute frame, resampled to `m1/m5/m15/m30/h1/h2/d1` via `_HORIZON_RULES` | `domain/engines/adaptive_regime_engine.py:200-206` (`HORIZON_GROUPS`, `_HORIZON_RULES`), `:270-325` (`classify_stack`, resample at `:306`, indicator calc at `:311-318`) | same NIFTY 1-minute OHLC | same as row 1 | YES |
| 3 | `assets/regime_percentiles.json` — single-timeframe ADX/ATR%/slope15%/rv60 percentile table | `domain/engines/adaptive_regime_engine.py:43-55` (`load_percentiles`) | measured file, not a live feed | file says `measured_on: "nifty_1m 2015-01-09..2026-08-05, 1,069,092 bars"` (archive DB, ~11.6y) | YES, but see Gap G1 below — it is one static table, not a rolling 126-day one |
| 4 | `assets/regime_percentiles_mtf.json` — per-horizon percentile tables (`horizons.{m1,m5,m15,m30,h1,h2,d1}`) + `mtf_slope_abs_pct` (per-MTF-span EMA-slope floors) | `domain/engines/adaptive_regime_engine.py:209-222` (`load_percentiles_mtf`); consumed by `mtf_regime_engine.py:80-83` (`_flat_floor`) for the flat-floor, and by `adaptive_regime_engine.py:231-242` (`classify_horizon`) for the probability vector | measured file | same `measured_on` as row 3 (confirmed by reading the file: `"nifty_1m 2015-01-09 09:15:00..2026-08-05 15:29:00, 1,069,092 bars"`) | YES, same caveat as G1 |
| 5 | `domain.engines.indicator_engine.TechnicalIndicatorEngine` (ADX, ATR, ATR%) | `adaptive_regime_engine.py:279` (import), `:311-313` (call) | internal compute, no external data | n/a | n/a |

### 1.2 The 4 measurement tools (build the two JSON tables above)

All four tools (`tools/measure_regime_horizons.py`, `tools/fit_regime_calibration.py`,
`tools/fit_regime_weights.py`, `tools/calibration_regime_stack.py`) read **exactly one** external
source each, and it is the same source in every case:

```
measure_regime_horizons.py:14   DB = "/home/claude/data/niftybkp.db"
measure_regime_horizons.py:34   SELECT dt, open, high, low, close FROM nifty_1m ORDER BY dt
fit_regime_calibration.py:15    DB="/home/claude/data/niftybkp.db"
fit_regime_calibration.py:48-49 pd.read_sql("SELECT dt,open,high,low,close FROM nifty_1m ORDER BY dt", ...)
fit_regime_weights.py:15        DB="/home/claude/data/niftybkp.db"
fit_regime_weights.py:54-55     pd.read_sql("SELECT dt,open,high,low,close FROM nifty_1m ORDER BY dt", ...)
calibration_regime_stack.py:19  DB = "/home/claude/data/niftybkp.db"
calibration_regime_stack.py:37-38 pd.read_sql("SELECT dt,open,high,low,close FROM nifty_1m ORDER BY dt", ...)
```

That is: **OHLC close only, from the `nifty_1m` table of the master archive `niftybkp.db`, not the
live working DB.** No volume, no VIX, no options, no futures OI, no equity/breadth, no holiday
calendar is read by any of these four tools. `measure_regime_horizons.py:36` prints what it actually
loaded: `1,069,092 bars  2015-01-09 09:15:00 -> 2026-08-05 15:29:00` (~11.6 years) — this is the
real, confirmed span the percentile tables were measured on, independently of the CLAUDE.md figure
for `niftybkp.db`'s full depth (2008-01-01+, 1.78M rows, not independently reachable here).

### 1.3 `regime_valves_engine.py` and `judge_engine.py` — no direct data reads

`RegimeValvesEngine.adjust()` (`domain/engines/regime_valves_engine.py:19-58`) is a pure function.
Its only inputs are a `base` valves dict and a `regime` dict with `composite` and
`overlays.vix_state` keys (`:23-24`, `:47`). It reads no file, table, or DB — the regime dict and
the `vix_state` overlay are built elsewhere (outside this audit's four files) and simply handed in.

`JudgeEngine.decide()` (`domain/engines/judge_engine.py:759-761`) is likewise a pure decision
function over already-computed dicts (`sce`, `context`, `ml`, `regime`, `base_valves`, the options
chain). The gates that look like they read "regime" data (16 MTF alignment, 20 regime spine) are
reading pre-built dicts handed in through `self._cool_ctx` — `"mtf"` at `:1125`, `"spine"` at
`:1150`, `"stable_regime"` at `:915` — assembled by services outside the four audited files
(`domain/services/mtf_state.py`, `domain/engines/regime_stabiliser.py`). The judge itself touches
two local files directly:

* `data/hold_evidence.json` via `config.settings.DATA_DIR` — `judge_engine.py:637-665`
  (`_load_hold_evidence`). **Not present in this checkout** (`ls` confirms absent); the code's own
  `if not os.path.exists(p): return {}` branch at `:645` is what fires, so this degrades silently to
  "no hold evidence" rather than erroring — which the docstring at `:638-639` says is the intended
  "absent = {}" behaviour for a missing file.
* `data/calibration.json` via `config.settings.CALIBRATION_FILE` (`config/settings.py:997`), read
  by `domain/services/calibration.py:39-55` and called from `judge_engine.py:842-849` (gate `09b`).
  **Not present in this checkout either.** Gate `09b` is off by default (`use_calibrated_gate`), so
  this has no live effect regardless.

Comments inside `GATE_META_LIST` (not executable reads, but documentation of what feeds the gates
this judge runs alongside regime detection) cite real measured data: `fut_1m` holding 2,068,221 rows
with open interest, 44.7% of rows missing OI (`judge_engine.py:76-86`, gate `17_futures_confirm`);
NSE F&O bhavcopy, 2,601 sessions 2018-2026 (`:106-117`, gate `18_options_confirm`); and the regime
spine ladder measured on 299,917 minute bars + 4,604 daily bars (`:131-141`, gate `20_regime_spine`).
These are confirmation/quality gates that run beside regime detection, not the regime classifier
itself — flagged here only because the brief named `judge_engine.py` as a target file.

### 1.4 `LOOKBACK_DAYS = 126` — not actually inside any of the four audited files

The constant exists in the codebase (confirmed by grep) at:

```
domain/services/dynamic_exit.py:56        LOOKBACK_DAYS = 126
domain/services/new_opportunity_gate.py:82 LOOKBACK_DAYS = 126
domain/services/new_opportunity.py:69     LOOKBACK_DAYS = 126
```

All three are **exit / new-opportunity gating services**, not the regime classifiers in this
audit's scope. None of `mtf_regime_engine.py`, `adaptive_regime_engine.py`,
`regime_valves_engine.py`, or `judge_engine.py` defines or imports `LOOKBACK_DAYS`. The regime
percentile tables that `adaptive_regime_engine.py` and `mtf_regime_engine.py` actually use were
measured on the full archive history (2015-01-09→2026-08-05, ~11.6y — §1.2), as **one static
distribution**, not a rolling 126-day window. CLAUDE.md §2.1 states "The regime classifier must be
trained on rolling 126-day windows, not static historical buckets" — as written today, the
measurement tools do the opposite of that instruction (see Gap G1).

---

## 2. The already-measured calibration result (verbatim numbers)

`assets/regime_calibration_report.json`, produced by `tools/calibration_regime_stack.py`, fails its
own declared pass bar (`MAE<0.10 and max_gap<0.15`, stated in the tool's docstring,
`calibration_regime_stack.py:3-6`) on **every horizon measured, as of 11-08-2026**:

| horizon | n scored | MAE | max_gap | verdict | pattern |
|---|---|---|---|---|---|
| m5 | 213,709 | 0.131 | 0.235 | FAIL | low bucket (0.00-0.25) claims 0.227, realizes 0.462 (under-confident low); top bucket (0.60-1.01) claims 0.67, realizes 0.558 (over-confident top) |
| m30 | 36,946 | 0.137 | 0.236 | FAIL | same shape: low bucket claims 0.226 realizes 0.462; top claims 0.669 realizes 0.530 |
| h1 | 19,840 | 0.130 | 0.268 | FAIL | low bucket claims 0.227 realizes 0.495 (worst gap, 0.268); top claims 0.670 realizes 0.551 |
| d1 | 2,726 | 0.115 | 0.184 | FAIL | low/mid buckets realize ~0.49-0.53 against claims ~0.31-0.40; top bucket claims 0.676 realizes 0.507 |

Every horizon shows the same two-sided failure: the **low/mid confidence buckets are
under-confident** (they realize noticeably better than claimed — realized win rates cluster near
0.46-0.55 regardless of the claimed probability) and the **top bucket is over-confident** (claims
~0.67-0.68, realizes only ~0.51-0.56). In practice the stack's probability output barely separates
from its own base rate across the whole confidence range.

The follow-on fit (`assets/regime_calibration_map.json`, from `tools/fit_regime_calibration.py`)
confirms this is not fixable by post-hoc calibration: on the 30%-holdout it reports an **out-of-sample
inversion** — "highest calibrated claims (0.57-0.59) realize 0.30-0.38" — and its own `"finding"`
field states the hand-written score weights inside `classify()`/`classify_horizon()`
(`adaptive_regime_engine.py:120-127`, `:246-253`) "do not survive the holdout era" and "the score
function must be MEASURED ... or the stack stays display-only." Overall verdict in that file: `"FAIL"`.

`assets/regime_weights_report.json` (from `tools/fit_regime_weights.py`) independently shows why:
the **direction** sub-model's holdout AUC is **0.52-0.523** on m5/m30 (i.e., no better than a coin
flip beyond noise) while the **volatility** sub-model's AUC is a real 0.72-0.74 but its calibration
MAE is 0.41-0.54 — strong discriminative power, badly mis-scaled. Every horizon/question
combination in that file is marked `"verdict": "FAIL"` against its own declared pass bar
(`AUC>=0.55 and cal MAE<0.10`).

Net: the regime stack's own self-measurement, using the exact code paths and data this audit
traced in §1, says the probability vector it currently emits is not trustworthy as a probability on
any horizon from m5 to d1.

---

## 3. Gaps

**G1 — Static-history measurement contradicts CLAUDE.md's own rolling-126-day directive.**
`tools/measure_regime_horizons.py`, `tools/fit_regime_calibration.py`, `tools/fit_regime_weights.py`
and `tools/calibration_regime_stack.py` all build ONE percentile/calibration table from the entire
2015-01-09→2026-08-05 archive (`niftybkp.db:nifty_1m`), with a single chronological 70/30 split
(`fit_regime_calibration.py:68`, `fit_regime_weights.py:68`) — not a rolling 126-day re-fit. This is
not a missing *data* gap (the data held is far more than 126 days); it is a gap between the
measurement *method* the code uses today and the regime-awareness rule CLAUDE.md §2.1 states.

**G2 — The classifiers' own holdout measurement says they do not work for direction.**
`assets/regime_weights_report.json` direction AUC of 0.52-0.523 (§2) means the ADX/ATR%/slope
percentile features that `adaptive_regime_engine.py` and `mtf_regime_engine.py` build their
probability vectors from carry almost no forward direction information at m5/m30 on the held data.
This is not a data-availability gap — the OHLC data behind it is held in full — it is a gap between
what the code claims (`classify()`'s `"read"` string in `mtf_regime_engine.py:174-184`, e.g. "56.6%
win / +7.23 pts") and what the SAME measurement framework, run on more samples with a train/holdout
split, now shows (AUC 0.52, calibration FAIL at every horizon). Both numbers are measured on the
same `nifty_1m` archive; they were not reconciled before this audit.

**G3 — The calibration gate (`09b_calibrated_win_prob`) and the hold-evidence cooldown input are
both files judge_engine.py reads, and both are absent in this checkout.** `data/calibration.json`
(`config/settings.py:997`, read by `domain/services/calibration.py:39-55`) and
`data/hold_evidence.json` (`judge_engine.py:637-665`) do not exist on disk here. Gate `09b` is off
by default so this has no live effect, but it means the "actual 12y-measured win rate" input that
gate `09b`'s own label promises (`judge_engine.py:60-61`) has no file to read from in this checkout —
confirmed by `ls`, not inferred.

**G4 — VIX overlay (`regime_valves_engine.py:47`, `overlays.get("vix_state")`) depends on a feed
CLAUDE.md §1.1 states only goes back to 2025-08-11 (~14.7 months).** The valves engine itself
doesn't read VIX — it reads whatever `overlays.vix_state` the caller supplies — but if that overlay
is ever back-tested before 2025-08-11 it has no VIX to read, which is the exact "fallback required
for older backtests" CLAUDE.md flags. The regime *classifiers* audited in §1.1 avoid this already:
their volatility feature (`atr_pct`) is derived from price OHLC (ATR), not VIX, so it is available
for the full archive span — only the separate VIX-panic overlay consumed by the valves engine has
the short span.

**G5 — `trading_holidays` / Tuesday-rule / DTE-decay logic is absent from all four audited files.**
Grepping all four files for `trading_holidays`, `market_1m`, `equity_1m`, `breadth_1m`, `vix_1m`,
`opt_chain_1m`, `fut_1m` returns zero hits inside `mtf_regime_engine.py` and
`adaptive_regime_engine.py`. The expiry-dating / Tuesday-rule concern CLAUDE.md §2.1 raises belongs
to the exit/DTE simulator (`_reprice`, `dynamic_exit.py`), not to intraday regime detection as
currently built. This is noted so the regime-detection need is not conflated with the exit-pricing
need — they are different code paths reading different data.

**G6 — `derived_1m`/`derived_wide_1m` (held, ~160K rows, Feb-2025+) and `labels_1m` (absent) are not
read by any of the four audited files.** Grepping the four files for `derived_1m`, `derived_wide_1m`,
`labels_1m` returns zero hits. The existing regime-detection build needs neither: it is built
entirely on raw OHLC (`nifty_1m`/the in-memory `df`) plus the two measured percentile JSON files.
`labels_1m`'s absence is therefore not a gap against what this code currently reads.

---

## 4. Verdict

**The data need is already satisfied for what the existing regime-detection code reads.** Every
external input traced in §1 — the 1-minute OHLC frame, and the two percentile JSON tables built
from `nifty_1m` in `niftybkp.db` — is held, and held for a span (4.8-11.6 years depending on source)
far exceeding the 126-day figure CLAUDE.md names. There is no missing *table* and no *held-span*
shortfall for intraday regime detection as currently coded.

**What is actually broken is not a data gap, it is a measured-accuracy gap, proven by the code's own
output files (§2):** the probability vector `adaptive_regime_engine.classify()` /
`mtf_regime_engine.classify()` produce fails calibration on every horizon (m5/m30/h1/d1, MAE
0.115-0.137, max_gap 0.184-0.268), the direction sub-model's own holdout AUC is 0.52-0.523, and a
second fitted calibration attempt inverts out-of-sample. More history or a new table will not fix
this — the same archive already produced both the optimistic in-sample narrative in
`mtf_regime_engine.py`'s docstring and the failing holdout numbers in `assets/regime_calibration_report.json`.

**The one genuine process gap (G1) is methodological, not data-availability:** the measurement
tools build one static 11.6-year distribution instead of the rolling 126-day windows CLAUDE.md §2.1
calls for. Re-running the same four tools on a rolling 126-day re-fit, on data already held, is the
only change this audit finds actually missing — not a new feed, not a longer history, not a table
that doesn't exist.
