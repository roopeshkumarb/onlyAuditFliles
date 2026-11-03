"""Upstox live recorder: the monthly set, keys in Upstox's form, a BINARY subscribe (T-0808)."""
import json
import os
import sys
import tempfile
import unittest
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pullers", "shared"))
sys.path.insert(0, HERE)
os.environ.setdefault("DP_ROOT", tempfile.mkdtemp(prefix="dpur_"))
import dp_upstoxrec as U  # noqa: E402
from test_dp_depthrec import ROWS  # noqa: E402


class Keys(unittest.TestCase):
    def test_index_vix_monthly_future_and_atm_options(self):
        keys, exp = U.instrument_keys(ROWS, date(2026, 10, 16), 22988.0, n=10)
        k = [x[0] for x in keys]
        self.assertEqual(exp, date(2026, 10, 27))
        self.assertEqual(k[:3], ["NSE_INDEX|Nifty 50", "NSE_INDEX|India VIX", "NSE_FO|48704"])
        self.assertEqual(len(k), 3 + 21 * 2)
        self.assertNotIn("NSE_FO|weekly", k)               # never the weekly contract
        self.assertTrue(all(x.startswith("NSE_FO|") for x in k[2:]))

    def test_subscribe_is_binary_json_full_mode(self):
        m = U.subscribe_message(["NSE_FO|1"])
        self.assertIsInstance(m, bytes)
        d = json.loads(m)
        self.assertEqual((d["method"], d["data"]["mode"], d["data"]["instrumentKeys"]),
                         ("sub", "full", ["NSE_FO|1"]))

    def test_fo_keys_ask_30_levels_index_keys_stay_full(self):
        keys, _ = U.instrument_keys(ROWS, date(2026, 10, 16), 22988.0, n=10)
        subs = U.subscriptions([x[0] for x in keys], "full_d30")
        self.assertEqual([m for m, _ in subs], ["full", "full_d30"])
        self.assertEqual(subs[0][1], ["NSE_INDEX|Nifty 50", "NSE_INDEX|India VIX"])
        self.assertEqual(len(subs[1][1]), 43)
        self.assertLessEqual(len(subs[1][1]), 50)          # Upstox: 50 keys per d30 socket
        self.assertEqual(U.DEPTH_MODE, "full_d30")

    def test_session_hours(self):
        self.assertTrue(U.in_session(datetime(2026, 10, 16, 9, 0)))
        self.assertFalse(U.in_session(datetime(2026, 10, 16, 15, 35)))

    def test_known_holiday_is_out_of_session_auditor_a3(self):
        import dp_calendar
        old = dp_calendar.classify
        try:
            dp_calendar.classify = lambda d: dp_calendar.KNOWN_HOLIDAY
            self.assertFalse(U.in_session(datetime(2026, 11, 4, 10, 0)))
        finally:
            dp_calendar.classify = old

    def test_trading_day_is_unaffected_by_the_calendar_check(self):
        import dp_calendar
        old = dp_calendar.classify
        try:
            dp_calendar.classify = lambda d: dp_calendar.TRADING_DAY
            self.assertTrue(U.in_session(datetime(2026, 11, 4, 10, 0)))
        finally:
            dp_calendar.classify = old

    def test_missing_dp_calendar_falls_back_to_weekday_only_never_crashes(self):
        import sys, builtins
        old = sys.modules.pop("dp_calendar", None)
        real_import = builtins.__import__

        def blocked(name, *a, **kw):
            if name == "dp_calendar":
                raise ImportError("simulated: dp_calendar not importable")
            return real_import(name, *a, **kw)
        builtins.__import__ = blocked
        try:
            self.assertTrue(U.in_session(datetime(2026, 11, 4, 10, 0)))
        finally:
            builtins.__import__ = real_import
            if old is not None:
                sys.modules["dp_calendar"] = old


if __name__ == "__main__":
    unittest.main()
