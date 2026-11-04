# retailer_db_edge — Schema Design (DESIGN ONLY, NOT BUILT)

Date: 04-11-2026 | Status: PROPOSED — pending 3 approvals (Fable, external auditor, Kumar)
Author pass: Claude Code, read-only investigation against the local sandbox repo at `/home/user/blpro`.

**This document is the entire deliverable.** No code was executed, no database file was
created, no file outside this one was touched. Everything below is a design for a NEW
SQLite store, `retailer_db_edge`, meant to sit alongside — not replace — `niftybkp.db` and
`blpro_working.db` until the owner signs off on an actual build.

---

## 0. The hard requirement this design exists to satisfy

> "If we pulled X named data from Dhan and Kite, the database must show where it was
> pulled from." — every row, every table, no exceptions.

Three of the five tables named in the brief (`nifty_1m`, `vix_1m`, `derived_1m`) currently
have **no source column at all** on the master archive (`niftybkp.db`, confirmed by direct
query and taken as given). `opt_chain_1m` has a `src` column but it is the only one that
does. A fifth table, `labels_1m`, does not exist yet. Meanwhile `broker_bars_1m` — a table
already proven to work at 382,700+ rows across two boxes — carries full row-level
provenance (`broker`, `src_store`, `pulled_at`, `copied_at`) and is held up in this
project's own audit trail as the reference pattern (`docs/research/T0894_BROKER_BARS_171026-1435.md`).

This design does exactly one thing: it takes that proven pattern and applies it,
consistently, to every table a retail backtest actually reads from.

---

## 1. What the puller code actually returns (read, not guessed)

Read: `pullers/fullpuller/download_engine.py` (the live puller engine) and
`tools/download_engine.py` (the bronze-lake variant).

The contract in `pullers/fullpuller/download_engine.py` is explicit and load-bearing:

```
(rows, None)      the vendor ANSWERED
(None, "reason")  the vendor FAILED
```

Every one of the six download functions — `download_fyers`, `download_kite`,
`download_dhan`, `download_upstox`, `download_yahoo`, `download_nse` — ends by building rows
through the shared `_row()` helper (line 573):

```python
def _row(ts, o, h, l, c, v, oi, symbol, interval, source):
    return (ts, symbol, interval, o, h, l, c,
            v if v is not None else None,
            oi if oi is not None else None,
            source, BOX_NAME, now_ist().strftime("%Y-%m-%d %H:%M:%S"))
```

Two facts matter for this design:

1. **`source` is always one of exactly the six literal broker names the owner named**:
   `"fyers"`, `"kite"`, `"dhan"`, `"upstox"`, `"yahoo"`, `"nse"` — passed explicitly at each
   call site inside the per-source function, never inferred. This is the `broker` column.
2. **`now_ist()` at the moment `_row()` runs is the pull timestamp** (`pulled_at`), and
   `BOX_NAME` (which physical box/container made the call — i5, i7, J1800, Pi5) is captured
   too, though the proven `broker_bars_1m` pattern folds the box into `src_store` (the
   puller DB path already encodes which box's store it is) rather than giving it its own
   column. This design keeps that same economy rather than inventing a parallel concept.

`opt_chain_1m`'s existing `src` column is **finer-grained than `broker`** — it already
carries the `SRC_ORDER` variant (e.g. `"upstox_live"` vs `"upstox_expired"` vs
`"fyers_backfill"`), read from `domain/services/traded_volume.py`:

```python
SRC_ORDER = ("upstox_live", "upstox_expired", "fyers_backfill", "dhan", "fyers_live",
             "fyers_live+upstox_oi", "fyers_live+dhan_oi")
```

So `src` and `broker` are not the same thing and this design keeps both: `broker` answers
"which of the six vendors," `src` (where known) answers "which feed variant of that vendor."

---

## 2. The proven pattern being copied

`broker_bars_1m` (confirmed: 382,700 rows, `tools/broker_bars_copy.py`):

```sql
CREATE TABLE IF NOT EXISTS broker_bars_1m (
    dt        TEXT NOT NULL,
    symbol    TEXT NOT NULL,
    broker    TEXT NOT NULL,
    open      REAL, high REAL, low REAL, close REAL,
    volume    REAL,
    oi        REAL,
    src_store TEXT,     -- which puller DB/file this row was copied from
    pulled_at TEXT,     -- when the vendor answered (capture time, from the puller store)
    copied_at TEXT,     -- when this row was copied into the engine store
    PRIMARY KEY (dt, symbol, broker)
) WITHOUT ROWID;
```

`data_provenance` (confirmed: exists, 1 row, nearly unused, `tools/data_provenance_seed.py`):

```sql
-- CREATE TABLE data_provenance(tbl, sym, src, dt_from, dt_to, rows, gate, added_at)
```

`data_ledger` (confirmed: 2,195 rows, `domain/services/daily_recorder.py:52`) — a run-level
ledger, not a per-row stamp, kept as-is and used only as an input to the migration
(section 6), never modified by this design.

---

## 3. The five row-level tables

### 3.1 `nifty_1m_v2` — fixes the gap in `nifty_1m`

Design choice: **one canonical row per minute is kept** (not one row per broker per
minute — that duplication already exists, on purpose, in `broker_bars_1m`, which is the
reconciliation/consensus table read by `domain/services/broker_bars.py`). What
`nifty_1m` lacks is not more rows, it is a stamp on the row it already has. Keeping the
cardinality identical to the legacy table means `research/labels.py` (`load_bars`),
`tools/label_backfill.py` and `domain/services/derived_compute.py` — all of which expect
exactly one OHLC row per minute — read `nifty_1m_v2` with no logic change, only a `SELECT *`
that now also returns where the bar came from.

```sql
CREATE TABLE IF NOT EXISTS nifty_1m_v2 (
    ts         INTEGER NOT NULL,   -- epoch seconds, carried from legacy nifty_1m.ts
    dt         TEXT NOT NULL,      -- 'YYYY-MM-DD HH:MM:SS' GMT+5:30, bar-start minute
    open       REAL, high REAL, low REAL, close REAL,
    vol        REAL,               -- CAUTION: index volume, vendor aggregate - see docs/research/
                                    -- DATA_PROVENANCE_AND_QUALITY_181026-0755.md item 1. Never VWAP/OBV input.
    broker     TEXT NOT NULL,      -- dhan | kite | upstox | fyers | nse | yahoo
    src        TEXT,               -- fine-grained SRC_ORDER variant when known, else NULL
    src_store  TEXT NOT NULL,      -- puller DB/file (or 'niftybkp.db' for historical backfill rows)
    pulled_at  TEXT NOT NULL,      -- GMT+5:30, when the vendor answered this bar
    copied_at  TEXT NOT NULL,      -- GMT+5:30, when this row was written into retailer_db_edge
    PRIMARY KEY (dt)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS ix_nifty_1m_v2_broker ON nifty_1m_v2(broker, dt);
```

### 3.2 `vix_1m_v2` — fixes the gap in `vix_1m`, and makes Defect #2 impossible to repeat silently

Same shape as `nifty_1m_v2` (no `vol` column — legacy `vix_1m` has none). One extra column
exists specifically because of a known codebase defect (CLAUDE.md §4.2): `meta_label.py`
currently defaults a missing VIX to a fake neutral `0.5`. This table cannot stop that code
bug by itself, but it can make sure nobody ever loads a synthetic/fallback value into this
table and has it silently read back as a real VIX print:

```sql
CREATE TABLE IF NOT EXISTS vix_1m_v2 (
    ts                   INTEGER NOT NULL,
    dt                   TEXT NOT NULL,
    open REAL, high REAL, low REAL, close REAL,
    broker               TEXT NOT NULL,   -- dhan | kite | upstox | fyers | nse | yahoo
    src                  TEXT,
    src_store            TEXT NOT NULL,
    pulled_at            TEXT NOT NULL,
    copied_at            TEXT NOT NULL,
    is_synthetic_fallback INTEGER NOT NULL DEFAULT 0,
        -- 0 = a real vendor print. 1 = a stand-in value was knowingly stored here
        -- (e.g. a fut_1m-realized-vol proxy for pre-11-08-2025 dates, per CLAUDE.md
        -- §2.2). When 1, broker MUST be 'DERIVED_PROXY', never a real vendor name -
        -- a proxy value is never allowed to impersonate a vendor print.
    PRIMARY KEY (dt)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS ix_vix_1m_v2_fallback ON vix_1m_v2(is_synthetic_fallback, dt);
```

Data horizon note carried through unchanged: real rows exist only from 2025-08-11
onward (~14.7 months, per CLAUDE.md §1.1). A backtest before that date finds **no row at
all** here, by design — never a faked one — which is the honest signal that forces the
caller down to the `fut_1m` realized-volatility fallback CLAUDE.md §2.2 already mandates.

### 3.3 `opt_chain_1m_v2` — extends the one table that already has provenance

`opt_chain_1m` already carries `src`, so this is additive, not corrective: it adds the
`broker`/`src_store`/`pulled_at`/`copied_at` quartet for consistency with every other table,
plus the two columns CLAUDE.md §2.1 requires for the DTE Decay Rule and the Tuesday-rule
fallback to be checkable instead of assumed.

```sql
CREATE TABLE IF NOT EXISTS opt_chain_1m_v2 (
    dt               TEXT NOT NULL,
    ts               INTEGER,
    expiry_flag      TEXT,
    strike_label     TEXT,
    opt_type         TEXT NOT NULL,     -- CE | PE
    strike           REAL NOT NULL,
    spot             REAL,
    close            REAL,
    volume           REAL,
    oi               REAL,
    iv               REAL,
    delta REAL, gamma REAL, theta REAL, vega REAL,
    bid_qty REAL, ask_qty REAL,
    close_price      REAL,
    pop              REAL,
    close_basis      TEXT,
    vol_day_total    REAL,
    vol_basis        TEXT,
    src              TEXT NOT NULL,     -- kept as-is: the existing fine-grained SRC_ORDER value
    broker           TEXT NOT NULL,     -- NEW: coarse vendor name, derived from src (e.g. 'upstox_live' -> 'upstox')
    src_store        TEXT NOT NULL,
    pulled_at        TEXT NOT NULL,
    copied_at        TEXT NOT NULL,
    days_to_expiry   INTEGER,           -- CLAUDE.md 2.1: the dte the simulator's _reprice() must decay against
    expiry_confidence TEXT NOT NULL DEFAULT 'HIGH'
        CHECK (expiry_confidence IN ('HIGH','LOW')),
        -- 'LOW' exactly when nse_calendar.py fell back to the Tuesday rule because
        -- trading_holidays / "NSE holiday-master FO" could not be read for this date.
    PRIMARY KEY (dt, strike, opt_type, expiry_flag)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS ix_opt_chain_1m_v2_broker ON opt_chain_1m_v2(broker, dt);
CREATE INDEX IF NOT EXISTS ix_opt_chain_1m_v2_expconf ON opt_chain_1m_v2(expiry_confidence, dt);
```

Note on the primary key: the brief gives the legacy column list but not its key, so
`(dt, strike, opt_type, expiry_flag)` is this design's best inference from the column
names (one row per strike/type/expiry per minute) — **flag this specific choice for the
auditor to confirm or correct against the real legacy constraint before any build.**

Note on options data horizon (CLAUDE.md §1.1): `opt_ohlc_1m` only goes back to
2025-09-15 (~13.5 months). `opt_chain_1m_v2` inherits the same real horizon; it does not
manufacture history that was never pulled.

### 3.4 `derived_1m_v2` — not pulled, so it gets a different kind of stamp

`derived_1m` is computed, not pulled (CLAUDE.md is explicit about this), so it gets no
`broker`/`pulled_at` columns of its own — a derived bar was never "pulled" from anyone.
What it needs instead, per CLAUDE.md §1: *"should note which upstream inputs computed
it"* — i.e. a stamp of which pulled series (and which broker) fed the computation, so a
reader can trace a derived value back to the raw rows the way `pulled_at`/`broker` trace a
raw row back to a vendor.

```sql
CREATE TABLE IF NOT EXISTS derived_1m_v2 (
    dt            TEXT NOT NULL,
    orb_high      REAL,
    orb_low       REAL,
    -- ... every other existing derived_1m column, carried through unchanged ...
    computed_ist  TEXT NOT NULL,     -- kept, legacy column: when this bar was computed
    computed_by   TEXT NOT NULL,     -- e.g. 'domain/services/derived_compute.py'
    inputs_broker TEXT,              -- comma list of brokers whose pulled rows fed this computation,
                                     -- e.g. 'upstox,dhan' - NEVER blank if any pulled input was used
    inputs_src    TEXT,              -- comma list of the fine-grained src/SRC_ORDER values actually
                                     -- used for this bar (e.g. the fut_1m source chosen that day)
    inputs_ref    TEXT,              -- pointer into data_provenance_v2: 'tbl:dt_from:dt_to' triples,
                                     -- one per upstream table this bar's computation read from
    copied_at     TEXT NOT NULL,
    PRIMARY KEY (dt)
) WITHOUT ROWID;
```

This directly closes the volume-proxy trap in CLAUDE.md §2.2: any derived VWAP/OBW bar
computed from `fut_1m.traded_volume` now carries `inputs_broker`/`inputs_src` naming
exactly which future contract and vendor fed it, instead of leaving a reader to assume
`market_1m`'s (unusable) index-volume column was the input.

### 3.5 `labels_1m_v2` — does not exist yet; designed from `research/labels.py` + `tools/label_backfill.py`

`research/labels.py`'s `label_grid()` produces exactly one label per (eligible minute
`i`, barrier, horizon) triple, 4 barriers × 6 horizons = 24 configurations per minute,
values restricted to `UP | DOWN | NEITHER | AMBIGUOUS`. `tools/label_backfill.py` runs this
day-by-day into a **new research store** it calls `labels.db`, resumable, never touching
the master. This design gives that store's table a provenance-complete shape that fits
inside `retailer_db_edge` as `labels_1m_v2`:

```sql
CREATE TABLE IF NOT EXISTS labels_1m_v2 (
    dt                   TEXT NOT NULL,     -- the bar being evaluated (bars['dt'][i])
    barrier              REAL NOT NULL,     -- one of 5, 10, 15, 20 (points)
    horizon              INTEGER NOT NULL,  -- one of 5, 10, 15, 20, 30, 60 (minutes)
    label                TEXT NOT NULL CHECK (label IN ('UP','DOWN','NEITHER','AMBIGUOUS')),
    entry_dt             TEXT,              -- dt of open[i+1], the actionable entry bar
    entry_open           REAL,
    source_broker        TEXT NOT NULL,     -- the nifty_1m_v2.broker of the bar this label was computed from
    source_src           TEXT,              -- the nifty_1m_v2.src of that bar, where known
    label_engine_version TEXT NOT NULL,     -- e.g. 'research.labels V1.0' - which code produced this row
    computed_ist         TEXT NOT NULL,     -- when label_backfill.py ran this day (run_day's own timestamp)
    copied_at            TEXT NOT NULL,
    PRIMARY KEY (dt, barrier, horizon)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS ix_labels_1m_v2_broker ON labels_1m_v2(source_broker, dt);
```

`source_broker`/`source_src` matter specifically because `nifty_1m_v2` can hold rows from
different brokers on different days (whichever puller's bar was chosen as canonical for
that minute) — a label is a function of the OHLC it was computed from, so if that OHLC's
source is ever challenged (e.g. the T-0916 finding that one box's own NIFTY bar was wrong
on 11 sessions, `docs/research/T0894_BROKER_BARS_171026-1435.md`), every label that used it
can be found and re-run instead of silently staying wrong. `label_engine_version` exists so
a future V1.1/V2 label definition never gets confused with V1.0 rows sitting in the same
table.

---

## 4. The companion rollup table — extending, not reinventing, `data_provenance`

Per the brief's explicit instruction, this is the **existing** `data_provenance` shape
(`tbl, sym, src, dt_from, dt_to, rows, gate, added_at`) with exactly the columns needed to
roll up the per-row stamps above — nothing invented from scratch.

```sql
CREATE TABLE IF NOT EXISTS data_provenance_v2 (
    tbl            TEXT NOT NULL,     -- e.g. 'nifty_1m_v2', 'opt_chain_1m_v2'
    sym            TEXT NOT NULL,     -- e.g. 'NIFTY', 'INDIAVIX', or the option's strike_label
    src            TEXT NOT NULL,     -- kept: fine-grained SRC_ORDER value or vendor dataset name
    broker         TEXT NOT NULL,     -- NEW: the coarse vendor name (dhan/kite/upstox/fyers/nse/yahoo)
                                      -- - this is the literal column the owner's requirement asks for
                                      -- at rollup grain, not just per-row
    dt_from        TEXT,
    dt_to          TEXT,
    rows           INTEGER,
    gate           TEXT,              -- kept, legacy semantics preserved (unused on the legacy table today)
    pulled_at_from TEXT,              -- NEW: earliest pulled_at folded into this range
    pulled_at_to   TEXT,              -- NEW: latest pulled_at folded into this range
    src_store      TEXT,              -- NEW: puller store/path this range was rolled up from
                                      -- ('MULTIPLE' if more than one store contributed; 'niftybkp.db' for
                                      -- the one-time historical backfill rows, see section 6)
    copied_at      TEXT,              -- NEW: when this rollup row itself was computed
    added_at       TEXT NOT NULL,     -- kept: legacy column name, same meaning
    PRIMARY KEY (tbl, sym, src, dt_from, dt_to)
);
```

This table is filled the same way `tools/data_provenance_seed.py` already fills the legacy
one — a `GROUP BY src, sym` scan over each `_v2` table — so no new tooling concept is
needed, only the same script pointed at the new tables and columns.

---

## 5. How this closes the gap, table by table

| Table | Gap before | Fix |
|---|---|---|
| `nifty_1m` | No source column at all. A bar's broker was unknowable after the fact. | `nifty_1m_v2` stamps `broker`, `src`, `src_store`, `pulled_at`, `copied_at` on every row, same cardinality, same PK shape (`dt`), zero logic change for existing readers. |
| `vix_1m` | No source column. Also the table most exposed to Defect #2 (fake `0.5` fallback) since it has the shortest real history (Aug 2025+). | Same four provenance columns, plus `is_synthetic_fallback` so a proxy value can never be mistaken for a real vendor print again. |
| `derived_1m` | No source column, and none makes sense directly (it's computed, not pulled) — but the brief notes it should still "note which upstream inputs computed it", which nothing did. | `inputs_broker` / `inputs_src` / `inputs_ref` trace every derived bar back to the raw pulled rows and brokers that fed it. |
| `opt_chain_1m` | Had `src`, but no coarse `broker`, no `src_store`/`pulled_at`/`copied_at`, and no way to check the Tuesday-rule / DTE risk CLAUDE.md flags. | Adds the missing provenance quartet plus `days_to_expiry` and `expiry_confidence`. |
| `labels_1m` | Did not exist. A label is useless as a research target if nobody can say which OHLC source produced it. | New table ties every label row to the exact `nifty_1m_v2` broker/src it was computed from, and to the label engine version that computed it. |
| (summary) `data_provenance` | Existed, 1 row, unused; no per-row-table link anyone actually queried. | `data_provenance_v2` adds `broker`, the pull-time range, and the store path, filled by the same seeding script pattern already in the repo. |

---

## 6. Migration note — this is a BACKFILL, never a re-pull

None of the `_v2` tables are to be filled by calling any broker again. They are filled
**once**, by reading the existing `niftybkp.db` tables (`nifty_1m`, `vix_1m`,
`opt_chain_1m`, `derived_1m`) and the existing `data_ledger` / `data_provenance` rows,
read-only, and writing the `_v2` row with the best provenance that can honestly be
inferred:

1. For each legacy row, look up the most specific matching `data_ledger` entry
   (`dataset`, `source`, `newest_row` near this row's `dt`) or `data_provenance` entry
   (`tbl`, `sym`, `src`, date range containing this row's `dt`).
2. If a match exists: carry its `source`/`src` into `broker`/`src`, its `run_ist`/`added_at`
   into `pulled_at`, and stamp `copied_at` with the backfill's own run time. `src_store`
   becomes `'niftybkp.db'` (that is genuinely where the row was read from for this
   migration, which is itself a true provenance fact worth keeping, distinct from
   whatever store first captured it live).
3. If no match exists (the ledger/provenance rows are sparse — `data_provenance` had only
   1 row before seeding): `broker` and `src` are both stamped `'UNKNOWN_HISTORICAL'` —
   never guessed, never defaulted to a plausible-looking vendor name. This is the same
   discipline `pullers/fullpuller/download_engine.py` already enforces for a live pull
   (`(None, "reason")`, never a fabricated empty-but-green row) applied to history instead
   of to a live call.
4. `opt_chain_1m` rows already carrying a real `src` keep it; only the new `broker` /
   `src_store` / `pulled_at` / `copied_at` / `days_to_expiry` / `expiry_confidence` columns
   are backfilled from step 1–3 (and `expiry_confidence` is set `'LOW'` for any date the
   Tuesday-rule fallback is known to have been active, `'HIGH'` otherwise).
5. `labels_1m_v2` has no legacy table to migrate from at all — it is populated by running
   `tools/label_backfill.py`'s existing logic (unchanged) against `nifty_1m_v2`, which
   naturally carries `source_broker`/`source_src` through from whichever `nifty_1m_v2` row
   fed each label.
6. `data_provenance_v2` is filled last, by the same `GROUP BY` seeding approach
   `tools/data_provenance_seed.py` already uses, pointed at the five `_v2` tables.

No broker API is called during this migration. No existing table (`niftybkp.db`,
`blpro_working.db`, `broker_bars_1m`, `data_provenance`, `data_ledger`) is written to.
`retailer_db_edge` is a new, separate SQLite file.

---

## 7. Explicitly out of scope / not done

* No `CREATE TABLE` was executed. No `.db` file exists anywhere from this task.
* No puller, engine, gate, or UI file was edited.
* No institutional data (signed option flow, dealer GEX, intraday FII/DII) is proposed
  anywhere above, per CLAUDE.md §6.1.
* `SRC_ORDER` (`domain/services/traded_volume.py`) was read and respected, not
  reinvented — `src` columns above are typed to carry its values, never a new taxonomy.
* This is a design pending three approvals (Fable, an external auditor, Kumar) before any
  build step is taken.
