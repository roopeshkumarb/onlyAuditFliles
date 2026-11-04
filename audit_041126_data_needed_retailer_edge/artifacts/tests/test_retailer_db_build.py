"""tests/test_retailer_db_build.py - tools/retailer_db_build.py + tools/retailer_db_inventory.py on synthetic fixtures.

Nothing here touches a real database or a box. Plain unittest:  python3 tests/test_retailer_db_build.py
"""
import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import retailer_db_build as B  # noqa: E402
import retailer_db_inventory as INV  # noqa: E402

OPT_COLS = ("dt,ts,expiry_flag,strike_label,opt_type,strike,spot,close,volume,oi,iv,src,delta,gamma,theta,vega,"
            "bid_qty,ask_qty,close_price,pop,close_basis,vol_day_total,vol_basis")


def mk_source(path, nifty=True, vix=True, opt=True, bars=True, shift=0.0, n=6, day='01'):
    con = sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=DELETE")
    if nifty:
        con.execute("create table nifty_1m(ts int, dt text, open real, high real, low real, close real, vol real)")
        for i in range(n):
            con.execute("insert into nifty_1m values(?,?,?,?,?,?,?)",
                        (1700000000 + 60 * i, "2026-10-%s 09:%02d:00" % (day, 15 + i), 100 + i + shift, 101 + i, 99 + i,
                         100.5 + i, 7))
    if vix:
        con.execute("create table vix_1m(ts int, dt text, open real, high real, low real, close real)")
        for i in range(3):
            con.execute("insert into vix_1m values(?,?,?,?,?,?)",
                        (1700000000 + 60 * i, "2026-10-01 09:%02d:00" % (15 + i), 12, 13, 11, 12.5))
    if opt:
        con.execute("create table opt_chain_1m(%s)" % OPT_COLS)
        srcs = ["upstox_live", "fyers_live+upstox_oi", None, "weird_feed", "dhan", "fyers_live+mystery"]
        for i, s in enumerate(srcs):
            con.execute("insert into opt_chain_1m values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        ("2026-10-01 09:15:00", 1700000000, None if i == 0 else "W", "ATM", "CE", 25000.0 + 50 * i,
                         25010, 120.5, 10, 100, 0.15, s, .5, .001, -2, 3, 5, 6, 120, .4, "ltp", 10, "vol"))
    if bars:
        con.execute("create table broker_bars_1m(dt text, symbol text, broker text, open real, high real, low real,"
                    " close real, volume real, oi real, src_store text, pulled_at text, copied_at text,"
                    " primary key(dt,symbol,broker))")
        for b in ("dhan", "kite"):
            con.execute("insert into broker_bars_1m values(?,?,?,?,?,?,?,?,?,?,?,?)",
                        ("2026-10-01 09:15:00", "NIFTY", b, 1, 2, 0.5, 1.5, 9, None, "/data/%s/%s_current.db" % (b, b),
                         "2026-10-01 15:40:00", "2026-10-02 01:00:00"))
    con.commit()
    con.close()


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def dump(path):
    con = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
    out = {}
    for t in ("nifty_1m_v2", "vix_1m_v2", "opt_chain_1m_v2", "broker_bars_1m_v2", "data_provenance_v2"):
        out[t] = con.execute("select * from %s order by 1,2,3" % t).fetchall()
    con.close()
    return out


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name
        self.a = os.path.join(self.d, "a.db")
        self.b = os.path.join(self.d, "b.db")
        self.out = os.path.join(self.d, "edge", "retailer_db_edge.db")
        os.makedirs(os.path.dirname(self.out))

    def tearDown(self):
        self.tmp.cleanup()

    def q(self, sql, *args):
        con = sqlite3.connect("file:%s?mode=ro" % self.out, uri=True)
        try:
            return con.execute(sql, args).fetchall()
        finally:
            con.close()


class Stamping(Base):
    def test_provenance_stamping_per_table(self):
        mk_source(self.a)
        r = B.build(self.out, [(self.a, "i7_niftybkp")])
        self.assertEqual(r["status"], "BUILT")
        # opt_chain: src kept, broker derived from src
        got = dict(self.q("select strike, broker||'|'||src from opt_chain_1m_v2"))
        self.assertEqual(got[25000.0], "upstox|upstox_live")
        self.assertEqual(got[25050.0], "fyers+upstox|fyers_live+upstox_oi")
        self.assertEqual(got[25200.0], "dhan|dhan")
        # broker_bars: broker and the source's own src_store/pulled_at/copied_at carried exactly
        row = self.q("select broker,src_store,pulled_at,copied_at,source_db from broker_bars_1m_v2 where broker='kite'")[0]
        self.assertEqual(row, ("kite", "/data/kite/kite_current.db", "2026-10-01 15:40:00", "2026-10-02 01:00:00",
                               "i7_niftybkp"))
        # every table: src_store is the label this build read from; copied_at is the one run stamp
        run = self.q("select v from _build_meta where k='run_ts'")[0][0]
        for t in ("nifty_1m_v2", "vix_1m_v2", "opt_chain_1m_v2"):
            self.assertEqual(self.q("select distinct src_store, copied_at from %s" % t), [("i7_niftybkp", run)])
        # provenance rollup carries the sha256 of the source file that was read
        sha_a = sha(self.a)
        rows = self.q("select tbl,source_db,source_table,source_sha256,rows,dt_from,dt_to from data_provenance_v2")
        self.assertTrue(rows)
        for tbl, db, st, s, n, f, t in rows:
            self.assertEqual((db, s), ("i7_niftybkp", sha_a))
        nrow = [x for x in rows if x[0] == "nifty_1m_v2"][0]
        self.assertEqual(nrow[1:], ("i7_niftybkp", "nifty_1m", sha_a, 6, "2026-10-01 09:15:00", "2026-10-01 09:20:00"))

    def test_unknown_historical_never_becomes_a_broker(self):
        mk_source(self.a)
        B.build(self.out, [(self.a, "i7_niftybkp")])
        for t in ("nifty_1m_v2", "vix_1m_v2"):
            self.assertEqual(self.q("select distinct broker, src, pulled_at from %s" % t),
                             [(B.UNKNOWN, B.UNKNOWN, B.UNKNOWN)])
        vend = set(B.VENDORS)
        for t in ("nifty_1m_v2", "vix_1m_v2", "opt_chain_1m_v2"):
            for (b,) in self.q("select distinct broker from %s" % t):
                self.assertTrue(b == B.UNKNOWN or set(b.split("+")) <= vend, (t, b))
        # NULL src, an unrecognised feed and a half-recognised mix are all UNKNOWN, never a guess
        got = dict(self.q("select strike, broker from opt_chain_1m_v2"))
        self.assertEqual((got[25100.0], got[25150.0], got[25250.0]), (B.UNKNOWN,) * 3)
        self.assertEqual(self.q("select src from opt_chain_1m_v2 where strike=25100"), [(B.UNKNOWN,)])
        for bad in (None, "", "  ", "weird", "fyers_live+mystery", "UPSTOXX_live"):
            self.assertEqual(B.broker_from_src(bad), B.UNKNOWN)
        self.assertEqual(B.broker_from_src("Fyers_Live+Dhan_OI+fyers_x"), "fyers+dhan")
        # a NULL expiry_confidence is stored as NULL, not as a claimed HIGH
        self.assertEqual(self.q("select distinct expiry_confidence, days_to_expiry from opt_chain_1m_v2"), [(None, None)])

    def test_absent_table_is_absent_not_zero(self):
        mk_source(self.a, vix=False)
        B.build(self.out, [(self.a, "x")])
        self.assertEqual(self.q("select status, rows_read from _build_units where source_table='vix_1m'"),
                         [("ABSENT", None)])
        self.assertEqual(self.q("select count(*) from vix_1m_v2"), [(0,)])

    def test_first_source_wins_and_loser_is_counted(self):
        mk_source(self.a, shift=0.0)
        mk_source(self.b, shift=50.0)
        B.build(self.out, [(self.a, "a"), (self.b, "b")])
        self.assertEqual(self.q("select distinct src_store from nifty_1m_v2"), [("a",)])
        self.assertEqual(self.q("select open from nifty_1m_v2 where dt='2026-10-01 09:15:00'"), [(100.0,)])
        self.assertEqual(self.q("select rows_inserted, rows_dup from _build_units where source_label='b' and "
                                "source_table='nifty_1m'"), [(0, 6)])

    def test_required_column_missing_is_refused(self):
        con = sqlite3.connect(self.a)
        con.execute("create table nifty_1m(ts int, dt text, open real)")
        con.commit()
        con.close()
        with self.assertRaises(B.SourceRefused):
            B.build(self.out, [(self.a, "a")])
        self.assertFalse(os.path.exists(self.out))


class Safety(Base):
    def q_tmp(self, sql):
        con = sqlite3.connect("file:%s?mode=ro" % (self.out + ".building"), uri=True)
        try:
            return con.execute(sql).fetchall()
        finally:
            con.close()

    def corrupt(self, path):
        con = sqlite3.connect(path)
        con.execute("create table nifty_1m(ts int, dt text, open real, high real, low real, close real, vol real)")
        for i in range(4000):
            con.execute("insert into nifty_1m values(?,?,?,?,?,?,?)", (i, "d%06d" % i, i, i, i, i, i))
        con.commit()
        con.close()
        with open(path, "r+b") as f:
            f.seek(4096 * 3)
            f.write(b"\xff" * 4096 * 6)

    def test_corrupt_source_is_refused_and_nothing_is_written(self):
        self.corrupt(self.a)
        before = sha(self.a)
        con = sqlite3.connect(self.a)                            # precondition: the fixture really is malformed
        with self.assertRaises(sqlite3.DatabaseError):
            con.execute("select sum(open+high) from nifty_1m").fetchall()
        con.close()
        for mode in ("quick", "none"):
            with self.assertRaises(B.SourceRefused, msg=mode):
                B.build(self.out, [(self.a, "i5_niftybkp")], check=mode)
            self.assertFalse(os.path.exists(self.out))
            if mode == "quick":                                  # caught before any scratch file is made
                self.assertFalse(os.path.exists(self.out + ".building"))
            else:                                                # caught mid-read: scratch only, never the final path
                self.assertEqual(self.q_tmp("select v from _build_meta where k='status'"), [("BUILDING",)])
        rc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "retailer_db_build.py"), "--out", self.out,
                             "--source", self.a], capture_output=True, text=True)
        self.assertEqual(rc.returncode, 2)
        self.assertIn("REFUSED", rc.stderr)
        self.assertEqual(sha(self.a), before)

    def test_not_a_database_is_refused(self):
        open(self.a, "wb").write(b"hello" * 100)
        with self.assertRaises(B.SourceRefused):
            B.build(self.out, [(self.a, "a")])

    def test_interrupted_run_leaves_no_half_file_and_resumes(self):
        mk_source(self.a)
        mk_source(self.b, shift=1.0)
        code = ("import os,sys; sys.path.insert(0,%r); import retailer_db_build as B\n"
                "n=[0]\n"
                "def crash(k):\n"
                "    n[0]+=1\n"
                "    if n[0]==3: os._exit(9)\n"
                "B.build(%r,[(%r,'a'),(%r,'b')],_inject=crash)\n" % (os.path.join(ROOT, "tools"), self.out, self.a, self.b))
        rc = subprocess.run([sys.executable, "-c", code]).returncode
        self.assertEqual(rc, 9)
        self.assertFalse(os.path.exists(self.out), "final path must not exist after a crash")
        self.assertTrue(os.path.exists(self.out + ".building"))
        r = B.build(self.out, [(self.a, "a"), (self.b, "b")])
        self.assertEqual(r["status"], "RESUMED")
        self.assertEqual(len(r["units"]), 8 - 3)               # only the units not yet committed were redone
        self.assertFalse(os.path.exists(self.out + ".building"))
        self.assertEqual(self.q("pragma integrity_check"), [("ok",)])
        # identical content to an uninterrupted build (copied_at/run stamps aside)
        clean = os.path.join(self.d, "clean.db")
        B.build(clean, [(self.a, "a"), (self.b, "b")])
        got, want = dump(self.out), dump(clean)
        for t in ("nifty_1m_v2", "vix_1m_v2", "opt_chain_1m_v2"):
            self.assertEqual([r[:10] for r in got[t]], [r[:10] for r in want[t]], t)

    def test_changed_source_discards_stale_temp(self):
        mk_source(self.a)
        code = ("import os,sys; sys.path.insert(0,%r); import retailer_db_build as B\n"
                "B.build(%r,[(%r,'a')],_inject=lambda k: os._exit(9))\n" % (os.path.join(ROOT, "tools"), self.out, self.a))
        self.assertEqual(subprocess.run([sys.executable, "-c", code]).returncode, 9)
        con = sqlite3.connect(self.a)
        con.execute("update nifty_1m set close=close+1")
        con.commit()
        con.close()
        r = B.build(self.out, [(self.a, "a")])
        self.assertEqual(r["status"], "BUILT")                 # not RESUMED: the old partial no longer matched

    def test_rerun_is_idempotent_and_touches_nothing(self):
        mk_source(self.a)
        B.build(self.out, [(self.a, "a")])
        before, mt, ino = sha(self.out), os.stat(self.out).st_mtime_ns, os.stat(self.out).st_ino
        r = B.build(self.out, [(self.a, "a")])
        self.assertEqual(r["status"], "UP_TO_DATE")
        self.assertEqual((sha(self.out), os.stat(self.out).st_mtime_ns, os.stat(self.out).st_ino), (before, mt, ino))
        self.assertEqual(sorted(os.listdir(os.path.dirname(self.out))), ["retailer_db_edge.db"])

    def test_different_sources_refuse_without_replace_and_move_aside_with_it(self):
        mk_source(self.a)
        mk_source(self.b, shift=9.0)
        B.build(self.out, [(self.a, "a")])
        old = sha(self.out)
        with self.assertRaises(B.OutExists):
            B.build(self.out, [(self.b, "b")])
        self.assertEqual(sha(self.out), old)
        r = B.build(self.out, [(self.b, "b")], replace=True)
        self.assertEqual(sha(r["moved_aside"]), old)           # the old file is kept, not deleted
        self.assertEqual(self.q("select distinct src_store from nifty_1m_v2"), [("b",)])

    def test_sources_are_byte_identical_afterwards(self):
        mk_source(self.a)
        mk_source(self.b, shift=2.0)
        snap = dict((p, (sha(p), os.stat(p).st_mtime_ns, os.stat(p).st_size)) for p in (self.a, self.b))
        names = sorted(os.listdir(self.d))
        B.build(self.out, [(self.a, "a"), (self.b, "b")], check="full")
        for p, v in snap.items():
            self.assertEqual((sha(p), os.stat(p).st_mtime_ns, os.stat(p).st_size), v)
        self.assertEqual(sorted(x for x in os.listdir(self.d) if x != "edge"), [x for x in names if x != "edge"])

    def test_verification_catches_a_tampered_row(self):
        mk_source(self.a)
        tmp = self.out + ".building"
        code = ("import os,sys; sys.path.insert(0,%r); import retailer_db_build as B\n"
                "n=[0]\n"
                "def f(k):\n"
                "    n[0]+=1\n"
                "    if n[0]==1: os._exit(9)\n"
                "B.build(%r,[(%r,'a')],_inject=f)\n" % (os.path.join(ROOT, "tools"), self.out, self.a))
        subprocess.run([sys.executable, "-c", code])
        con = sqlite3.connect(tmp)
        con.execute("update nifty_1m_v2 set close=close+1 where dt='2026-10-01 09:16:00'")
        con.commit()
        con.close()
        with self.assertRaises(B.VerifyFailed):
            B.build(self.out, [(self.a, "a")])
        self.assertFalse(os.path.exists(self.out))


def _opt_row(con, src, strike=25000.0, flag="W"):
    con.execute("insert into opt_chain_1m values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("2026-10-02 09:15:00", 1700000000, flag, "ATM", "CE", strike, 25010, 120.5, 10, 100, 0.15, src,
                 .5, .001, -2, 3, 5, 6, 120, .4, "ltp", 10, "vol"))


class SrcOrderAndStamps(Base):
    def _src_with_dups(self, path, order):
        mk_source(path, opt=False)
        con = sqlite3.connect(path)
        con.execute("create table opt_chain_1m(%s)" % OPT_COLS)
        for s in order:
            _opt_row(con, s)
        _opt_row(con, "zzz_unlisted", strike=25050.0)
        _opt_row(con, "aaa_unlisted", strike=25050.0)
        con.commit()
        con.close()

    def test_src_order_decides_the_winner_not_scan_order(self):
        for n, order in enumerate((["dhan", "upstox_live", "fyers_live"], ["fyers_live", "upstox_live", "dhan"])):
            a = os.path.join(self.d, "a%d.db" % n)
            out = os.path.join(self.d, "edge", "o%d.db" % n)
            self._src_with_dups(a, order)
            r = B.build(out, [(a, "a")])
            con = sqlite3.connect(out)
            self.assertEqual(con.execute("select src from opt_chain_1m_v2 where strike=25000").fetchall(),
                             [("upstox_live",)], order)
            self.assertEqual(con.execute("select src from opt_chain_1m_v2 where strike=25050").fetchall(),
                             [("aaa_unlisted",)], "unlisted ranks last, ties by src text")
            self.assertEqual(con.execute("select rows_dup, rows_conflict from _build_units where "
                                         "source_table='opt_chain_1m'").fetchall(), [(3, 3)])
            got = sorted(con.execute("select kept_src, dropped_src, reason from _build_conflicts").fetchall())
            self.assertEqual(got, sorted([("upstox_live", x, "within_source_src_order") for x in
                                          [s for s in order if s != "upstox_live"]] +
                                         [("aaa_unlisted", "zzz_unlisted", "within_source_src_order")]))
            con.close()

    def test_cross_source_conflict_is_recorded_first_source_wins(self):
        mk_source(self.a, opt=False)
        mk_source(self.b, opt=False)
        for path, s in ((self.a, "dhan"), (self.b, "upstox_live")):
            con = sqlite3.connect(path)
            con.execute("create table opt_chain_1m(%s)" % OPT_COLS)
            _opt_row(con, s)
            con.commit()
            con.close()
        B.build(self.out, [(self.a, "a"), (self.b, "b")])
        self.assertEqual(self.q("select src from opt_chain_1m_v2"), [("dhan",)])
        self.assertEqual(self.q("select source_label, kept_src, dropped_src, reason from _build_conflicts"),
                         [("b", "dhan", "upstox_live", "cross_source_first_wins")])

    def test_null_or_blank_bars_broker_is_unknown_never_a_vendor(self):
        mk_source(self.a)
        con = sqlite3.connect(self.a)
        for i, b in enumerate((None, "  ")):
            con.execute("insert into broker_bars_1m values(?,?,?,?,?,?,?,?,?,?,?,?)",
                        ("2026-10-01 09:16:00", "SYM%d" % i, b, 1, 2, .5, 1.5, 9, None, "x", "p", "c"))
        con.commit()
        con.close()
        B.build(self.out, [(self.a, "a")])
        self.assertEqual(self.q("select distinct broker from broker_bars_1m_v2 where symbol like 'SYM%' "), [(B.UNKNOWN,)])

    def test_source_moving_during_the_build_publishes_nothing(self):
        mk_source(self.a)

        def touch(k):
            con = sqlite3.connect(self.a)
            con.execute("update nifty_1m set close=close+1")
            con.commit()
            con.close()
        with self.assertRaises(B.VerifyFailed):
            B.build(self.out, [(self.a, "a")], _inject=touch)
        self.assertFalse(os.path.exists(self.out))
        self.assertEqual([f for f in os.listdir(os.path.dirname(self.out)) if "building" in f], [])


class MidTransactionKill(Base):
    KILL = ("import os,signal,sys; sys.path.insert(0,%r); import retailer_db_build as B\n"
            "orig=B._open_out\n"
            "def small(p):\n"
            "    c=orig(p); c.execute('PRAGMA cache_size=5'); return c\n"
            "B._open_out=small\n"
            "n=[0]; rh=B._row_hash\n"
            "def hook(h,row):\n"
            "    n[0]+=1\n"
            "    if n[0]==%d: os.kill(os.getpid(), signal.SIGKILL)\n"
            "    rh(h,row)\n"
            "B._row_hash=hook\n"
            "B.build(%r,[(%r,'a'),(%r,'b')])\n")

    def _run_kill(self, at):
        code = self.KILL % (os.path.join(ROOT, "tools"), at, self.out, self.a, self.b)
        return subprocess.run([sys.executable, "-c", code]).returncode

    def test_sigkill_inside_a_transaction_resumes_and_converges(self):
        mk_source(self.a, n=3000)
        mk_source(self.b, n=3000, shift=1.0, day='02')
        snap = dict((p, (sha(p), os.stat(p).st_mtime_ns)) for p in (self.a, self.b))
        rc = self._run_kill(3000 + 3 + 6 + 2 + 1500)          # a: 4 units committed; dies 1500 rows into b's nifty unit
        self.assertEqual(rc, -9)
        tmp = self.out + ".building"
        self.assertFalse(os.path.exists(self.out))
        self.assertTrue(os.path.exists(tmp))
        self.assertTrue(os.path.exists(tmp + "-journal"), "precondition: the kill must leave a HOT journal")
        r = B.build(self.out, [(self.a, "a"), (self.b, "b")])
        self.assertEqual(r["status"], "RESUMED", "completed units must survive a mid-transaction kill")
        self.assertEqual(len(r["units"]), 4)
        self.assertEqual([f for f in os.listdir(os.path.dirname(self.out)) if "building" in f], [])
        self.assertEqual(self.q("pragma integrity_check"), [("ok",)])
        clean = os.path.join(self.d, "clean.db")
        B.build(clean, [(self.a, "a"), (self.b, "b")])
        got, want = dump(self.out), dump(clean)
        for t in ("nifty_1m_v2", "vix_1m_v2", "opt_chain_1m_v2", "broker_bars_1m_v2"):
            self.assertEqual([r[:10] for r in got[t]], [r[:10] for r in want[t]], t)
        for p, v in snap.items():
            self.assertEqual((sha(p), os.stat(p).st_mtime_ns), v, "a source changed")

    def test_rm_tmp_removes_every_sidecar(self):
        tmp = self.out + ".building"
        for suf in ("", "-journal", "-wal", "-shm"):
            open(tmp + suf, "wb").write(b"x")
        B._rm_tmp(tmp)
        self.assertEqual(os.listdir(os.path.dirname(self.out)), [])
        B._rm_tmp(tmp)                                           # idempotent on an empty directory

    def test_discarded_scratch_takes_its_journal_with_it(self):
        mk_source(self.a, n=3000)
        mk_source(self.b, n=3000, shift=1.0, day='02')
        self.assertEqual(self._run_kill(3000 + 3 + 6 + 2 + 1500), -9)
        self.assertTrue(os.path.exists(self.out + ".building-journal"))
        con = sqlite3.connect(self.a)
        con.execute("update nifty_1m set close=close+1")
        con.commit()
        con.close()
        r = B.build(self.out, [(self.a, "a"), (self.b, "b")])
        self.assertEqual(r["status"], "BUILT")                   # plan changed: scratch discarded, not resumed
        self.assertEqual([f for f in os.listdir(os.path.dirname(self.out)) if "building" in f], [])
        self.assertEqual(self.q("pragma integrity_check"), [("ok",)])


class Inventory(Base):
    def test_inventory_reports_and_writes_nothing(self):
        src = os.path.join(self.d, "src")
        os.makedirs(src)
        mk_source(os.path.join(src, "good.db"), vix=False)
        Safety.corrupt(self, os.path.join(src, "bad.db"))
        open(os.path.join(src, "junk.db"), "wb").write(b"x" * 50)
        before = dict((f, sha(os.path.join(src, f))) for f in os.listdir(src))
        recs = dict((os.path.basename(r["path"]), r) for r in
                    (INV.inspect(p, counts=True, check=True) for p in INV.find_dbs([src], 2)))
        self.assertEqual(sorted(recs), ["bad.db", "good.db", "junk.db"])
        g = recs["good.db"]
        self.assertTrue(g["opens"] and not g["error"])
        self.assertEqual(g["tables"]["vix_1m"], {"present": False})
        self.assertEqual(g["tables"]["nifty_1m"]["supplier_columns"], [])
        self.assertEqual(g["tables"]["opt_chain_1m"]["supplier_columns"], ["src"])
        self.assertEqual(g["tables"]["nifty_1m"]["rows"], 6)
        self.assertTrue(recs["bad.db"]["error"])
        self.assertEqual(recs["junk.db"]["error"], "not a SQLite database")
        self.assertEqual(before, dict((f, sha(os.path.join(src, f))) for f in os.listdir(src)))
        self.assertEqual(INV.main(["--root", src, "--json-out", os.path.join(src, "x.json")]), 2)
        self.assertEqual(sorted(os.listdir(src)), ["bad.db", "good.db", "junk.db"])


if __name__ == "__main__":
    unittest.main()
