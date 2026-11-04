#!/usr/bin/env python3
"""tools/retailer_db_inventory.py - READ-ONLY list of candidate source databases for tools/retailer_db_build.py.

For every SQLite file under the given roots: size, mtime, whether it opens, which retailer-relevant tables it holds,
and for each whether it carries a supplier column (src / broker). Sources are opened mode=ro + query_only; nothing is
written anywhere (output goes to stdout, or to --json-out which must not be inside a root). Row counts and the
integrity check cost a full read of a big file, so they are OFF unless asked for (--counts, --check).

    python3 tools/retailer_db_inventory.py --root /volume1/docker/blpro_data/009/app [--root ...] [--depth 3]
                                           [--counts] [--check] [--json-out /tmp/inv.json]

A table that is absent is reported as ABSENT - never as 0 rows. A file that will not open is reported with the error.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

IST = timezone(timedelta(hours=5, minutes=30))
WANTED = ("nifty_1m", "vix_1m", "opt_chain_1m", "broker_bars_1m", "derived_1m", "labels_1m", "data_provenance",
          "data_ledger")
SUPPLIER_COLS = ("src", "broker", "src_store")
DEFAULT_ROOTS = ("/volume1/docker/blpro_data/009/app", "/volume1/docker/datapullers", "/volume1/docker/blpro_derived")
SUFFIXES = (".db", ".sqlite", ".sqlite3")


def _ro(path):
    con = sqlite3.connect("file:%s?mode=ro" % quote(os.path.abspath(path)), uri=True, timeout=10)
    con.execute("PRAGMA query_only=ON")
    return con


def find_dbs(roots, depth):
    seen = []
    for root in roots:
        root = os.path.abspath(root)
        if not os.path.isdir(root):
            continue
        base = root.rstrip(os.sep).count(os.sep)
        for d, dirs, files in os.walk(root):
            if d.rstrip(os.sep).count(os.sep) - base >= depth:
                dirs[:] = []
            for f in sorted(files):
                if f.lower().endswith(SUFFIXES):
                    seen.append(os.path.join(d, f))
    return sorted(set(seen))


def inspect(path, counts=False, check=False):
    st = os.stat(path)
    rec = {"path": path, "bytes": st.st_size,
           "mtime": datetime.fromtimestamp(st.st_mtime, IST).strftime("%Y-%m-%d %H:%M:%S"),
           "opens": False, "error": None, "tables": {}}
    try:
        with open(path, "rb") as f:
            if f.read(16) != b"SQLite format 3\x00":
                rec["error"] = "not a SQLite database"
                return rec
        con = _ro(path)
        try:
            names = set(r[0] for r in con.execute("select name from sqlite_master where type='table'"))
            rec["opens"] = True
            rec["table_count"] = len(names)
            for t in WANTED:
                if t not in names:
                    rec["tables"][t] = {"present": False}
                    continue
                cols = [r[1] for r in con.execute('PRAGMA table_info("%s")' % t)]
                info = {"present": True, "columns": cols,
                        "supplier_columns": [c for c in SUPPLIER_COLS if c in cols]}
                if counts:
                    info["rows"] = con.execute('select count(*) from "%s"' % t).fetchone()[0]
                    if "dt" in cols:
                        info["dt_min"], info["dt_max"] = con.execute('select min(dt), max(dt) from "%s"' % t).fetchone()
                rec["tables"][t] = info
            if check:
                res = con.execute("PRAGMA quick_check(1)").fetchall()
                rec["quick_check"] = res[0][0] if res else None
                if res != [("ok",)]:
                    rec["error"] = "quick_check: %s" % (res[:1],)
        finally:
            con.close()
    except sqlite3.DatabaseError as e:
        rec["error"] = "%s: %s" % (type(e).__name__, e)
        rec["opens"] = False if rec.get("table_count") is None else rec["opens"]
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", action="append", help="directory to scan (repeatable); default: the known box paths")
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--counts", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json-out")
    a = ap.parse_args(argv)
    roots = a.root or [r for r in DEFAULT_ROOTS if os.path.isdir(r)]
    if a.json_out:
        out = os.path.abspath(a.json_out)
        if any(out.startswith(os.path.abspath(r) + os.sep) for r in roots):
            print("REFUSED: --json-out may not be inside a scanned root", file=sys.stderr)
            return 2
    recs = [inspect(p, a.counts, a.check) for p in find_dbs(roots, a.depth)]
    for r in recs:
        print("%s  %.2f GB  %s  %s" % (r["path"], r["bytes"] / 1e9, r["mtime"],
                                        "OK" if r["opens"] and not r["error"] else "PROBLEM: %s" % r["error"]))
        for t, i in r["tables"].items():
            if i["present"]:
                print("    %-16s supplier columns: %-22s%s" % (t, ",".join(i["supplier_columns"]) or "NONE",
                                                               ("  rows=%s %s..%s" % (i.get("rows"), i.get("dt_min"), i.get("dt_max"))) if a.counts else ""))
            else:
                print("    %-16s ABSENT" % t)
    if not recs:
        print("no SQLite files found under: %s" % ", ".join(roots) if roots else "no existing root to scan")
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as f:
            json.dump(recs, f, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
