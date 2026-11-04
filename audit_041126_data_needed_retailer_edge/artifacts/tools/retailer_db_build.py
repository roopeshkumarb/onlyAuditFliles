#!/usr/bin/env python3
"""tools/retailer_db_build.py - fill retailer_db_edge from EXISTING databases, every row stamped with its supplier.

DESIGN: docs/framework/RETAILER_DB_EDGE_SCHEMA_041126.md (PROPOSED, 3 approvals pending). Provenance pattern copied
from the proven broker_bars_1m (broker, src_store, pulled_at, copied_at). NOTHING IS PULLED FROM ANY BROKER.

    python3 tools/retailer_db_build.py --out /path/retailer_db_edge.db \
        --source /copy/of/niftybkp.db=i7_niftybkp [--source PATH[=LABEL] ...] [--check quick|full|none] [--replace]

SUPPLIER RULES (never invented)
  nifty_1m, vix_1m  carry NO supplier column -> broker = src = pulled_at = 'UNKNOWN_HISTORICAL'. Never a vendor name.
  opt_chain_1m      src is kept as-is; broker is derived from it ('fyers_live+upstox_oi' -> 'fyers+upstox'). Any token
                    that is not one of the six vendors, or a NULL/empty src, makes broker 'UNKNOWN_HISTORICAL'.
  broker_bars_1m    broker and src_store/pulled_at/copied_at are carried exactly as the source holds them.
  src_store         = the source label, i.e. where THIS build read the row (two boxes' niftybkp.db need two labels).
  Same key arriving with two different src values INSIDE one source (opt_chain_1m): the winner is chosen by the project's
  SRC_ORDER (CLAUDE.md 1.2: upstox_live, upstox_expired, fyers_backfill, dhan, fyers_live, fyers_live+upstox_oi,
  fyers_live+dhan_oi; any src outside the list ranks last, ties by src text) - never by physical scan order. Every
  losing row whose src differs from the winner's is recorded in _build_conflicts and counted in _build_units.rows_conflict.
  Same key arriving from two SOURCES: the FIRST --source wins (not SRC_ORDER); the loser is counted in rows_dup and, if
  its src differs from the kept row's, recorded in _build_conflicts as 'cross_source_first_wins'. Never hidden.

DEVIATIONS FROM THE DESIGN DOC, for the auditor
  * opt_chain_1m_v2.expiry_confidence and days_to_expiry are left NULL: the archive holds no calendar information, and
    stamping 'HIGH' would be a claim nobody measured. (CHECK allows NULL, 'HIGH', 'LOW'.)
  * opt_chain_1m_v2.expiry_flag NULL is stored as '' (WITHOUT ROWID forbids NULL in the key).
  * broker_bars_1m_v2 is added (the doc keeps broker_bars_1m as-is); data_provenance_v2 carries source_db,
    source_table and source_sha256 as extra columns. derived_1m is NOT copied here (computed, not pulled; its own step).
  * The doc's opt_chain primary key (dt,strike,opt_type,expiry_flag) is the doc's inference, still to be confirmed.

SAFETY (no UPS: power or network can drop at any instant)
  * Sources are opened mode=ro + query_only, hashed (sha256) before the copy, and stat-checked after; a source whose
    size/mtime moved during the build aborts the build. Nothing is ever written to a source. Point this at a COPY of a
    live-written database (blpro_09 writes niftybkp.db).
  * Output is built in <out>.building, one source table per transaction (rows + progress committed together,
    synchronous=FULL). A kill between units resumes at the next unit. A kill INSIDE a unit's transaction (SIGKILL, power
    cut) leaves a hot <out>.building-journal; the resume probe opens the scratch file read-write (it is our own file) so
    SQLite rolls that unit back, and the units already committed are kept. A scratch file that is discarded is removed
    together with its -journal/-wal/-shm sidecars (a stale journal must never meet a new file). A finished file is verified (row counts and a per-unit
    content sha256 re-read from the new file, integrity_check), fsynced, then os.replace()d and the directory fsynced.
    The final path therefore never holds a half-built file.
  * Re-running with the same sources is a no-op (UP_TO_DATE). An existing different output is refused unless
    --replace, which moves it aside to <out>.prev-<stamp> - nothing is deleted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

BUILDER_VERSION = "retailer_db_build 1.0"
UNKNOWN = "UNKNOWN_HISTORICAL"
VENDORS = ("upstox", "dhan", "kite", "fyers", "nse", "yahoo")
IST = timezone(timedelta(hours=5, minutes=30))
SRC_ORDER = ("upstox_live", "upstox_expired", "fyers_backfill", "dhan", "fyers_live", "fyers_live+upstox_oi",
             "fyers_live+dhan_oi")


def src_rank(src) -> int:
    t = str(src).strip().lower() if src is not None else ""
    return SRC_ORDER.index(t) if t in SRC_ORDER else len(SRC_ORDER)


def _rank_sql(col: str = "src") -> str:
    whens = " ".join("WHEN '%s' THEN %d" % (n, i) for i, n in enumerate(SRC_ORDER))
    return "CASE lower(trim(%s)) %s ELSE %d END, %s" % (col, whens, len(SRC_ORDER), col)


class SourceRefused(Exception):
    """A source is corrupt, unreadable, or does not have the columns the build needs."""


class VerifyFailed(Exception):
    """The new file did not match what was read, or a source moved under the build."""


class OutExists(Exception):
    """An output file already exists and does not match these sources."""


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def broker_from_src(src) -> str:
    """Coarse vendor(s) named by a fine-grained src ('upstox_live' -> 'upstox'). Unrecognised -> UNKNOWN_HISTORICAL."""
    if src is None or not str(src).strip():
        return UNKNOWN
    found = []
    for tok in str(src).strip().lower().split("+"):
        head = tok.split("_", 1)[0]
        if head not in VENDORS:
            return UNKNOWN
        if head not in found:
            found.append(head)
    return "+".join(found)


# ------------------------------------------------------------------------------ schema
DDL = """
CREATE TABLE IF NOT EXISTS nifty_1m_v2 (
    ts INTEGER NOT NULL, dt TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, vol REAL,
    broker TEXT NOT NULL, src TEXT, src_store TEXT NOT NULL, pulled_at TEXT NOT NULL, copied_at TEXT NOT NULL,
    PRIMARY KEY (dt)) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS ix_nifty_1m_v2_broker ON nifty_1m_v2(broker, dt);
CREATE TABLE IF NOT EXISTS vix_1m_v2 (
    ts INTEGER NOT NULL, dt TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL,
    broker TEXT NOT NULL, src TEXT, src_store TEXT NOT NULL, pulled_at TEXT NOT NULL, copied_at TEXT NOT NULL,
    is_synthetic_fallback INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (dt)) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS ix_vix_1m_v2_fallback ON vix_1m_v2(is_synthetic_fallback, dt);
CREATE TABLE IF NOT EXISTS opt_chain_1m_v2 (
    dt TEXT NOT NULL, ts INTEGER, expiry_flag TEXT NOT NULL, strike_label TEXT, opt_type TEXT NOT NULL,
    strike REAL NOT NULL, spot REAL, close REAL, volume REAL, oi REAL, iv REAL, delta REAL, gamma REAL, theta REAL,
    vega REAL, bid_qty REAL, ask_qty REAL, close_price REAL, pop REAL, close_basis TEXT, vol_day_total REAL,
    vol_basis TEXT, src TEXT NOT NULL, broker TEXT NOT NULL, src_store TEXT NOT NULL, pulled_at TEXT NOT NULL,
    copied_at TEXT NOT NULL, days_to_expiry INTEGER,
    expiry_confidence TEXT CHECK (expiry_confidence IS NULL OR expiry_confidence IN ('HIGH','LOW')),
    PRIMARY KEY (dt, strike, opt_type, expiry_flag)) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS ix_opt_chain_1m_v2_broker ON opt_chain_1m_v2(broker, dt);
CREATE TABLE IF NOT EXISTS broker_bars_1m_v2 (
    dt TEXT NOT NULL, symbol TEXT NOT NULL, broker TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL,
    volume REAL, oi REAL, src_store TEXT, pulled_at TEXT, copied_at TEXT, source_db TEXT NOT NULL,
    edge_copied_at TEXT NOT NULL, PRIMARY KEY (dt, symbol, broker)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS data_provenance_v2 (
    tbl TEXT NOT NULL, sym TEXT NOT NULL, src TEXT NOT NULL, broker TEXT NOT NULL, dt_from TEXT, dt_to TEXT,
    rows INTEGER, gate TEXT, pulled_at_from TEXT, pulled_at_to TEXT, src_store TEXT, copied_at TEXT,
    added_at TEXT NOT NULL, source_db TEXT NOT NULL, source_table TEXT NOT NULL, source_sha256 TEXT NOT NULL,
    PRIMARY KEY (tbl, sym, src, broker, source_db, dt_from, dt_to));
CREATE TABLE IF NOT EXISTS _build_meta (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS _build_units (
    source_label TEXT NOT NULL, source_table TEXT NOT NULL, status TEXT NOT NULL, rows_read INTEGER,
    rows_inserted INTEGER, rows_dup INTEGER, rows_rejected INTEGER, data_sha256 TEXT, source_sha256 TEXT NOT NULL,
    rows_conflict INTEGER DEFAULT 0,
    PRIMARY KEY (source_label, source_table));
CREATE TABLE IF NOT EXISTS _build_conflicts (
    source_label TEXT NOT NULL, source_table TEXT NOT NULL, row_key TEXT NOT NULL, kept_src TEXT, dropped_src TEXT,
    kept_store TEXT, reason TEXT NOT NULL);
"""


class Spec:
    def __init__(self, src_table, required, optional, dest, dest_cols, keys, unit_col, notnull, mapper, src_col=None):
        self.src_col = src_col
        self.src_table, self.required, self.optional = src_table, required, optional
        self.dest, self.dest_cols, self.keys, self.unit_col = dest, dest_cols, keys, unit_col
        self.notnull, self.mapper = notnull, mapper


def _map_nifty(r, label, run_ts):
    return (r["ts"], r["dt"], r["open"], r["high"], r["low"], r["close"], r["vol"],
            UNKNOWN, UNKNOWN, label, UNKNOWN, run_ts)


def _map_vix(r, label, run_ts):
    return (r["ts"], r["dt"], r["open"], r["high"], r["low"], r["close"],
            UNKNOWN, UNKNOWN, label, UNKNOWN, run_ts, 0)


_OPT_COPY = ("dt", "ts", "expiry_flag", "strike_label", "opt_type", "strike", "spot", "close", "volume", "oi", "iv",
             "delta", "gamma", "theta", "vega", "bid_qty", "ask_qty", "close_price", "pop", "close_basis",
             "vol_day_total", "vol_basis")


def _map_opt(r, label, run_ts):
    flag = r["expiry_flag"] if r["expiry_flag"] is not None else ""
    vals = dict((c, r[c]) for c in _OPT_COPY)
    vals["expiry_flag"] = flag
    src = r["src"] if r["src"] is not None and str(r["src"]).strip() else UNKNOWN
    return tuple(vals[c] for c in _OPT_COPY) + (src, broker_from_src(r["src"]), label, UNKNOWN, run_ts, None, None)


def _map_bars(r, label, run_ts):
    broker = r["broker"] if r["broker"] is not None and str(r["broker"]).strip() else UNKNOWN
    return (r["dt"], r["symbol"], broker, r["open"], r["high"], r["low"], r["close"], r["volume"], r["oi"],
            r["src_store"], r["pulled_at"], r["copied_at"], label, run_ts)


SPECS = (
    Spec("nifty_1m", ("ts", "dt", "open", "high", "low", "close"), ("vol",), "nifty_1m_v2",
         ("ts", "dt", "open", "high", "low", "close", "vol", "broker", "src", "src_store", "pulled_at", "copied_at"),
         ("dt",), "src_store", ("ts", "dt", "broker", "src_store", "pulled_at", "copied_at"), _map_nifty),
    Spec("vix_1m", ("ts", "dt", "open", "high", "low", "close"), (), "vix_1m_v2",
         ("ts", "dt", "open", "high", "low", "close", "broker", "src", "src_store", "pulled_at", "copied_at",
          "is_synthetic_fallback"),
         ("dt",), "src_store", ("ts", "dt", "broker", "src_store", "pulled_at", "copied_at"), _map_vix),
    Spec("opt_chain_1m", ("dt", "opt_type", "strike"), tuple(c for c in _OPT_COPY if c not in ("dt", "opt_type", "strike")) + ("src",),
         "opt_chain_1m_v2", _OPT_COPY + ("src", "broker", "src_store", "pulled_at", "copied_at", "days_to_expiry",
                                         "expiry_confidence"),
         ("dt", "strike", "opt_type", "expiry_flag"), "src_store",
         ("dt", "expiry_flag", "opt_type", "strike", "src", "broker", "src_store", "pulled_at", "copied_at"), _map_opt,
         src_col="src"),
    Spec("broker_bars_1m", ("dt", "symbol", "broker"),
         ("open", "high", "low", "close", "volume", "oi", "src_store", "pulled_at", "copied_at"), "broker_bars_1m_v2",
         ("dt", "symbol", "broker", "open", "high", "low", "close", "volume", "oi", "src_store", "pulled_at",
          "copied_at", "source_db", "edge_copied_at"),
         ("dt", "symbol", "broker"), "source_db", ("dt", "symbol", "broker", "source_db", "edge_copied_at"), _map_bars),
)


# ------------------------------------------------------------------------------ helpers
def _canon(v) -> str:
    if v is None:
        return "\x00"
    if isinstance(v, (int, float)):
        return format(float(v), ".17g")
    if isinstance(v, bytes):
        return v.hex()
    return str(v)


def _row_hash(h, row) -> None:
    h.update(("|".join(_canon(v) for v in row) + "\n").encode("utf-8"))


def _ro(path: str) -> sqlite3.Connection:
    con = sqlite3.connect("file:%s?mode=ro" % quote(os.path.abspath(path)), uri=True, timeout=30)
    con.execute("PRAGMA query_only=ON")
    return con


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_source(path: str, mode: str) -> None:
    """Refuse anything that is not a healthy SQLite file. Reads only."""
    try:
        with open(path, "rb") as f:
            if f.read(16) != b"SQLite format 3\x00":
                raise SourceRefused("%s: not a SQLite database" % path)
        con = _ro(path)
        try:
            con.execute("select count(*) from sqlite_master").fetchone()
            if mode != "none":
                pragma = "integrity_check" if mode == "full" else "quick_check"
                res = con.execute("PRAGMA %s(1)" % pragma).fetchall()
                if res != [("ok",)]:
                    raise SourceRefused("%s: %s says %s" % (path, pragma, res[:1]))
        finally:
            con.close()
    except sqlite3.DatabaseError as e:
        raise SourceRefused("%s: %s" % (path, e))


def _stat(path):
    st = os.stat(path)
    return (st.st_size, st.st_mtime_ns)


def _fsync_dir(path: str) -> None:
    fd = os.open(os.path.dirname(os.path.abspath(path)) or ".", os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_file(path: str) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _meta(con, k):
    row = con.execute("select v from _build_meta where k=?", (k,)).fetchone()
    return row[0] if row else None


def _open_out(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=30, isolation_level=None)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA synchronous=FULL")
    return con


# ------------------------------------------------------------------------------ copy one unit
def _guard_rows(run, label, tbl):
    try:
        for r in run():
            yield r
    except sqlite3.DatabaseError as e:
        raise SourceRefused("%s: %s while reading %s" % (label, e, tbl))


def _copy_unit(out, src_path, label, spec, run_ts, src_sha):
    """One (source, table) unit in ONE transaction. Returns the unit dict."""
    sc = _ro(src_path)
    try:
        try:
            exists = sc.execute("select 1 from sqlite_master where type='table' and name=?", (spec.src_table,)).fetchone()
            have = set(r[1] for r in sc.execute('PRAGMA table_info("%s")' % spec.src_table))
        except sqlite3.DatabaseError as e:
            raise SourceRefused("%s: %s" % (label, e))
        if not exists:
            out.execute("BEGIN IMMEDIATE")
            out.execute("insert into _build_units(source_label,source_table,status,source_sha256) values(?,?,?,?)",
                        (label, spec.src_table, "ABSENT", src_sha))
            out.execute("COMMIT")
            return {"source": label, "table": spec.src_table, "status": "ABSENT"}
        missing = [c for c in spec.required if c not in have]
        if missing:
            raise SourceRefused("%s: table %s lacks required column(s) %s" % (label, spec.src_table, missing))
        sel = ", ".join(('"%s"' % c) if c in have else ("NULL AS %s" % c)
                        for c in spec.required + spec.optional + tuple(k for k in spec.keys
                                                                       if k not in spec.required + spec.optional))
        names = list(spec.required + spec.optional + tuple(k for k in spec.keys if k not in spec.required + spec.optional))
        ins = "INSERT INTO %s (%s) VALUES (%s)" % (spec.dest, ", ".join(spec.dest_cols), ",".join("?" * len(spec.dest_cols)))
        nn = [spec.dest_cols.index(c) for c in spec.notnull]
        read = inserted = dup = rejected = conflict = 0
        h = hashlib.sha256()
        kidx = [spec.dest_cols.index(k) for k in spec.keys]
        sidx = spec.dest_cols.index(spec.src_col) if spec.src_col else None
        kept_q = ("select %s, src_store from %s where %s" % (spec.src_col, spec.dest, " and ".join("%s=?" % k for k in spec.keys))
                  if spec.src_col else None)
        out.execute("BEGIN IMMEDIATE")
        try:
            order = ", ".join(spec.keys) + ((", " + _rank_sql("src")) if spec.src_col else "")
            sql = 'SELECT %s FROM "%s" ORDER BY %s' % (sel, spec.src_table, order)
            for tup in _guard_rows(lambda: sc.execute(sql), label, spec.src_table):
                read += 1
                row = spec.mapper(dict(zip(names, tup)), label, run_ts)
                if any(row[i] is None for i in nn):
                    rejected += 1
                    continue
                try:
                    out.execute(ins, row)
                except sqlite3.IntegrityError as e:
                    if "UNIQUE" in str(e) or "PRIMARY KEY" in str(e):
                        dup += 1
                        if kept_q:
                            kept = out.execute(kept_q, [row[i] for i in kidx]).fetchone()
                            if kept is not None and kept[0] != row[sidx]:
                                conflict += 1
                                out.execute("insert into _build_conflicts values(?,?,?,?,?,?,?)",
                                            (label, spec.src_table, json.dumps([row[i] for i in kidx], default=str),
                                             kept[0], row[sidx], kept[1],
                                             "within_source_src_order" if kept[1] == label else "cross_source_first_wins"))
                        continue
                    raise
                inserted += 1
                _row_hash(h, row)
            out.execute("insert into _build_units(source_label,source_table,status,rows_read,rows_inserted,rows_dup,"
                        "rows_rejected,data_sha256,source_sha256,rows_conflict) values(?,?,?,?,?,?,?,?,?,?)",
                        (label, spec.src_table, "DONE", read, inserted, dup, rejected, h.hexdigest(), src_sha, conflict))
            out.execute("COMMIT")
        except BaseException:
            out.execute("ROLLBACK")
            raise
        return {"source": label, "table": spec.src_table, "status": "DONE", "rows_read": read,
                "rows_inserted": inserted, "rows_dup": dup, "rows_rejected": rejected}
    finally:
        sc.close()


def _verify(out, specs_by_table):
    """Re-read the NEW file: counts and content hash per unit must equal what was read."""
    bad = []
    for lab, tbl, rd, ins, dup, rej, dsha in out.execute(
            "select source_label,source_table,rows_read,rows_inserted,rows_dup,rows_rejected,data_sha256 "
            "from _build_units where status='DONE'").fetchall():
        spec = specs_by_table[tbl]
        if rd != ins + dup + rej:
            bad.append("%s/%s: read %s != inserted %s + dup %s + rejected %s" % (lab, tbl, rd, ins, dup, rej))
        n = out.execute("select count(*) from %s where %s=?" % (spec.dest, spec.unit_col), (lab,)).fetchone()[0]
        if n != ins:
            bad.append("%s/%s: file holds %s rows, %s were inserted" % (lab, tbl, n, ins))
        h = hashlib.sha256()
        for row in out.execute("select %s from %s where %s=? order by %s"
                               % (", ".join(spec.dest_cols), spec.dest, spec.unit_col, ", ".join(spec.keys)), (lab,)):
            _row_hash(h, row)
        if h.hexdigest() != dsha:
            bad.append("%s/%s: content sha256 differs between what was read and what the file holds" % (lab, tbl))
    if bad:
        raise VerifyFailed("; ".join(bad))


_ROLLUP = (
    ("nifty_1m_v2", "nifty_1m", "'NIFTY'", "src"), ("vix_1m_v2", "vix_1m", "'INDIAVIX'", "src"),
    ("opt_chain_1m_v2", "opt_chain_1m", "'NIFTY_OPT'", "src"),
    ("broker_bars_1m_v2", "broker_bars_1m", "symbol", "'broker_bars_1m'"),
)


def _rollup(out, run_ts):
    out.execute("delete from data_provenance_v2")
    shas = dict(((a, b), c) for a, b, c in out.execute(
        "select source_label,source_table,source_sha256 from _build_units where status='DONE'"))
    for dest, srct, sym, srcexpr in _ROLLUP:
        spec = [s for s in SPECS if s.dest == dest][0]
        unit = spec.unit_col
        store = "MIN(src_store)" if dest != "broker_bars_1m_v2" else "CASE WHEN MIN(src_store)=MAX(src_store) THEN MIN(src_store) ELSE 'MULTIPLE' END"
        pulled = ("MIN(pulled_at), MAX(pulled_at)")
        sql = ("select %s, %s, broker, %s, MIN(dt), MAX(dt), COUNT(*), %s, %s from %s group by %s, %s, broker, %s"
               % (sym, srcexpr, unit, pulled, store, dest, unit, sym, srcexpr))
        for sy, sr, br, lab, dfrom, dto, n, pf, pt, st in out.execute(sql).fetchall():
            if (lab, srct) not in shas:
                continue
            out.execute("insert into data_provenance_v2 values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (dest, sy, sr if sr is not None else UNKNOWN, br, dfrom, dto, n, None, pf, pt, st, run_ts,
                         run_ts, lab, srct, shas[(lab, srct)]))


# ------------------------------------------------------------------------------ build
def _plan_json(infos):
    return json.dumps([[i["label"], i["sha256"], i["bytes"]] for i in infos], separators=(",", ":"))


def _complete_and_matches(path, plan):
    try:
        con = _ro(path)
        try:
            return _meta(con, "status") == "COMPLETE" and _meta(con, "plan") == plan
        finally:
            con.close()
    except sqlite3.DatabaseError:
        return False


def _rm_tmp(tmp):
    """Remove a scratch file AND its sidecars, journal first: a stale -journal must never meet a new file."""
    for suffix in ("-journal", "-wal", "-shm", ""):
        try:
            os.remove(tmp + suffix)
        except FileNotFoundError:
            pass


def _probe_tmp(tmp, plan):
    """Is the scratch file ours, for this plan, and still BUILDING? Opened read-write on purpose: it is our own file, and
    a read-only open cannot roll back the hot journal a kill inside a transaction leaves behind."""
    try:
        c = sqlite3.connect(tmp, timeout=30)
        try:
            return _meta(c, "plan") == plan and _meta(c, "status") == "BUILDING"
        finally:
            c.close()
    except sqlite3.DatabaseError:
        return False


def build(out_path, sources, check="quick", replace=False, _inject=None):
    """sources: list of (path, label). Returns a result dict. Raises SourceRefused / VerifyFailed / OutExists."""
    out_path = os.path.abspath(out_path)
    labels = [l for _, l in sources]
    if not sources or len(set(labels)) != len(labels):
        raise SourceRefused("need at least one source and every label must be unique: %s" % labels)
    infos = []
    for path, label in sources:
        if not os.path.isfile(path):
            raise SourceRefused("%s: no such file" % path)
        if os.path.abspath(path) == out_path or os.path.abspath(path) == out_path + ".building":
            raise SourceRefused("%s: the output may not be a source" % path)
        check_source(path, check)
        size, mt = _stat(path)
        infos.append({"label": label, "path": os.path.abspath(path), "sha256": file_sha256(path), "bytes": size,
                      "mtime_ns": mt})
    plan = _plan_json(infos)

    if os.path.exists(out_path):
        if _complete_and_matches(out_path, plan):
            return {"status": "UP_TO_DATE", "out": out_path, "units": []}
        if not replace:
            raise OutExists("%s exists and does not match these sources; use --replace (the old file is moved aside)"
                            % out_path)

    tmp = out_path + ".building"
    resumed = False
    if os.path.exists(tmp) or os.path.exists(tmp + "-journal"):
        if os.path.exists(tmp) and _probe_tmp(tmp, plan):
            resumed = True
        else:
            _rm_tmp(tmp)
    out = _open_out(tmp)
    try:
        if not resumed:
            out.executescript(DDL)
            out.execute("insert into _build_meta values('plan',?)", (plan,))
            out.execute("insert into _build_meta values('status','BUILDING')")
            out.execute("insert into _build_meta values('run_ts',?)", (now_ist(),))
            out.execute("insert into _build_meta values('builder',?)", (BUILDER_VERSION,))
        run_ts = _meta(out, "run_ts")
        done = set(out.execute("select source_label,source_table from _build_units").fetchall())
        results = []
        for info in infos:
            for spec in SPECS:
                if (info["label"], spec.src_table) in done:
                    continue
                results.append(_copy_unit(out, info["path"], info["label"], spec, run_ts, info["sha256"]))
                if _inject:
                    _inject((info["label"], spec.src_table))
        _verify(out, dict((s.src_table, s) for s in SPECS))
        out.execute("BEGIN IMMEDIATE")
        _rollup(out, run_ts)
        out.execute("update _build_meta set v='COMPLETE' where k='status'")
        out.execute("COMMIT")
        bad = out.execute("PRAGMA integrity_check").fetchall()
        if bad != [("ok",)]:
            raise VerifyFailed("integrity_check on the new file: %s" % bad[:3])
    except BaseException:
        out.close()
        raise
    out.close()
    for info in infos:
        if _stat(info["path"]) != (info["bytes"], info["mtime_ns"]):
            _rm_tmp(tmp)
            raise VerifyFailed("%s changed while it was being read; nothing published" % info["path"])
    _fsync_file(tmp)
    moved = None
    if os.path.exists(out_path):
        moved = out_path + ".prev-" + datetime.now(IST).strftime("%Y%m%d-%H%M%S")
        os.replace(out_path, moved)
        _fsync_dir(out_path)
    os.replace(tmp, out_path)
    _fsync_dir(out_path)
    return {"status": "RESUMED" if resumed else "BUILT", "out": out_path, "moved_aside": moved, "units": results}


def _parse_source(spec: str):
    path, _, label = spec.partition("=")
    return path, (label or re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(path)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", action="append", required=True, help="PATH[=LABEL]; first source wins on a duplicate key")
    ap.add_argument("--check", choices=("quick", "full", "none"), default="quick")
    ap.add_argument("--replace", action="store_true")
    a = ap.parse_args(argv)
    try:
        res = build(a.out, [_parse_source(s) for s in a.source], a.check, a.replace)
    except (SourceRefused, OutExists) as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2
    except VerifyFailed as e:
        print("VERIFY FAILED: %s" % e, file=sys.stderr)
        return 3
    print(json.dumps(res, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
