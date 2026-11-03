"""Dhan depth recorder: the right MONTHLY contracts, the right strikes, honest disconnect handling.

    python3 tests/test_dp_depthrec.py
"""
import os
import struct
import sys
import tempfile
import unittest
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pullers", "shared"))
os.environ.setdefault("DP_ROOT", tempfile.mkdtemp(prefix="dpdr_"))
import dp_depthrec as R  # noqa: E402


def row(sym, kind, exp, flag="M", strike="-0.01", opt="XX", sid="1", exch="NSE"):
    return {"SEM_EXM_EXCH_ID": exch, "SEM_TRADING_SYMBOL": sym, "SEM_INSTRUMENT_NAME": kind,
            "SEM_EXPIRY_DATE": exp + " 14:30:00", "SEM_EXPIRY_FLAG": flag,
            "SEM_STRIKE_PRICE": strike, "SEM_OPTION_TYPE": opt, "SEM_SMST_SECURITY_ID": sid}


ROWS = ([row("NIFTY-Oct2026-FUT", "FUTIDX", "2026-10-27", sid="48704"),
         row("NIFTY-Nov2026-FUT", "FUTIDX", "2026-11-24", sid="61471"),
         row("NIFTYNXT50-Oct2026-FUT", "FUTIDX", "2026-10-27", sid="9")]
        + [row("NIFTY-Oct2026-%d-%s" % (k, o), "OPTIDX", "2026-10-27", strike="%d.0" % k,
               opt=o, sid="%d%s" % (k, o)) for k in range(22000, 24050, 50) for o in ("CE", "PE")]
        + [row("NIFTY-20Oct2026-23000-CE", "OPTIDX", "2026-10-20", flag="W", strike="23000",
               opt="CE", sid="weekly")])


class Instruments(unittest.TestCase):
    def test_nearest_monthly_not_weekly_not_other_index(self):
        fut, opts, exp = R.nifty_monthly(ROWS, date(2026, 10, 16))
        self.assertEqual(fut["SEM_SMST_SECURITY_ID"], "48704")
        self.assertEqual(exp, date(2026, 10, 27))
        self.assertTrue(all(o["SEM_EXPIRY_FLAG"] == "M" for o in opts))

    def test_rolls_after_expiry(self):
        fut, _o, exp = R.nifty_monthly(ROWS, date(2026, 10, 28))
        self.assertIsNone(fut)          # Nov options absent in this sample -> says so

    def test_atm_plus_minus_n_both_sides(self):
        _f, opts, _e = R.nifty_monthly(ROWS, date(2026, 10, 16))
        got = R.pick_strikes(opts, 22988.0, 12)
        strikes = sorted({float(o["SEM_STRIKE_PRICE"]) for o in got})
        self.assertEqual(len(got), 50)
        self.assertEqual(strikes[12], 23000.0)            # ATM in the middle
        self.assertEqual((strikes[0], strikes[-1]), (22400.0, 23600.0))


class Frames(unittest.TestCase):
    def _msg(self, code, sid, levels=20):
        body = b"".join(struct.pack("<dII", 100.0 + i, 75, 3) for i in range(levels))
        return struct.pack("<hBBiI", 12 + len(body), code, 2, sid, 7) + body

    def test_stacked_bid_and_ask_are_split_by_length(self):
        f = self._msg(41, 48704) + self._msg(51, 48704) + self._msg(41, 47161)
        got = R.split_messages(f)
        self.assertEqual([(c, s) for c, _g, s, _n in got], [(41, 48704), (51, 48704), (41, 47161)])
        self.assertTrue(all(n == 332 for *_x, n in got))

    def test_disconnect_reason_is_read(self):
        f = struct.pack("<hBBiI", 14, 50, 2, 0, 0) + struct.pack("<h", 805)
        self.assertEqual(R.disconnect_code(f), 805)

    def test_805_stops_for_the_day_and_807_waits_for_a_new_token(self):
        rec = R.Recorder()
        rec.token_fp = "abc"
        rec.on_disconnect("d20", 807)
        self.assertEqual(rec.bad_token, "abc")
        self.assertIsNone(rec.stop_day)
        rec.on_disconnect("d200", 805)
        self.assertIsNotNone(rec.stop_day)
        self.assertIn("805", rec.st["stopped_for_day"])


class Session(unittest.TestCase):
    def test_hours(self):
        from datetime import datetime
        self.assertTrue(R.in_session(datetime(2026, 10, 16, 9, 0)))
        self.assertFalse(R.in_session(datetime(2026, 10, 16, 15, 35)))
        self.assertFalse(R.in_session(datetime(2026, 10, 17, 10, 0)))  # Saturday

    def test_known_holiday_is_out_of_session_auditor_a3(self):
        from datetime import datetime
        import dp_calendar
        old = dp_calendar.classify
        try:
            dp_calendar.classify = lambda d: dp_calendar.KNOWN_HOLIDAY
            self.assertFalse(R.in_session(datetime(2026, 11, 4, 10, 0)))  # a Wednesday, but marked a holiday
        finally:
            dp_calendar.classify = old

    def test_trading_day_is_unaffected_by_the_calendar_check(self):
        from datetime import datetime
        import dp_calendar
        old = dp_calendar.classify
        try:
            dp_calendar.classify = lambda d: dp_calendar.TRADING_DAY
            self.assertTrue(R.in_session(datetime(2026, 11, 4, 10, 0)))
        finally:
            dp_calendar.classify = old

    def test_missing_dp_calendar_falls_back_to_weekday_only_never_crashes(self):
        from datetime import datetime
        import sys
        old = sys.modules.pop("dp_calendar", None)
        sys.path_importer_cache.clear()
        try:
            import builtins
            real_import = builtins.__import__

            def blocked(name, *a, **kw):
                if name == "dp_calendar":
                    raise ImportError("simulated: dp_calendar not importable")
                return real_import(name, *a, **kw)
            builtins.__import__ = blocked
            try:
                self.assertTrue(R.in_session(datetime(2026, 11, 4, 10, 0)))   # weekday, no holiday file reachable -> still in session
            finally:
                builtins.__import__ = real_import
        finally:
            if old is not None:
                sys.modules["dp_calendar"] = old


if __name__ == "__main__":
    unittest.main()
