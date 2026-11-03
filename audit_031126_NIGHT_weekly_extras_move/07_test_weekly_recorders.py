"""Nearest-weekly option for the Dhan depth and Upstox live recorders (02-11-2026).

OFF (default env) must give exactly the instrument list the ORIGINAL code gave; ON must give
weekly + monthly inside Dhan's 50 per 20-level connection and Upstox's 50 keys per connection.
    python3 -m pytest tests/test_weekly_recorders.py
"""
import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pullers", "shared"))
sys.path.insert(0, HERE)
os.environ.setdefault("DP_ROOT", tempfile.mkdtemp(prefix="dpwk_"))
import dp_depthrec as R  # noqa: E402
import dp_upstoxrec as U  # noqa: E402
from test_dp_depthrec import row  # noqa: E402

TODAY = date(2026, 11, 2)
SPOT = 24988.0
STRIKES = range(23000, 27050, 50)


def chain(sym_fmt, exp, flag, tag):
    return [row(sym_fmt % (k, o), "OPTIDX", exp, flag=flag, strike="%d.0" % k, opt=o,
                sid="%s%d%s" % (tag, k, o)) for k in STRIKES for o in ("CE", "PE")]


MASTER = ([row("NIFTY-Nov2026-FUT", "FUTIDX", "2026-11-24", sid="61471")]
          + chain("NIFTY-Nov2026-%d-%s", "2026-11-24", "M", "m")
          + chain("NIFTY-03Nov2026-%d-%s", "2026-11-03", "W", "w1")
          + chain("NIFTY-10Nov2026-%d-%s", "2026-11-10", "W", "w2")
          + chain("NIFTY-24Nov2026-%d-%s", "2026-11-24", "W", "wdup")   # same day as the monthly
          + [row("BANKNIFTY-04Nov2026-1-CE", "OPTIDX", "2026-11-04", flag="W", strike="1", opt="CE",
                 sid="bn")])


def old_d20(rows, spot):
    """The ORIGINAL plan_today selection, copied verbatim from the pre-change file."""
    fut, opts, exp = R.nifty_monthly(rows, TODAY)
    picked = R.pick_strikes(opts, spot, 12)[:50]
    return [o["SEM_SMST_SECURITY_ID"] for o in picked], [exp.isoformat()] * len(picked)


def old_upstox(rows, spot, n=10):
    """The ORIGINAL instrument_keys body, copied verbatim from the pre-change file."""
    fut, opts, exp = R.nifty_monthly(rows, TODAY)
    out = [(k, k.split("|")[1], None, None, None) for k in U.INDEX_KEYS]
    out.append(("NSE_FO|%s" % fut["SEM_SMST_SECURITY_ID"], fut["SEM_TRADING_SYMBOL"],
                exp.isoformat(), None, None))
    for o in R.pick_strikes(opts, spot, n):
        out.append(("NSE_FO|%s" % o["SEM_SMST_SECURITY_ID"], o["SEM_TRADING_SYMBOL"],
                    exp.isoformat(), float(o["SEM_STRIKE_PRICE"]), o["SEM_OPTION_TYPE"]))
    return out, exp


class DefaultsAreOff(unittest.TestCase):
    def test_module_defaults(self):
        self.assertEqual(R.DEPTH_WEEKLY_STRIKES, 0)
        self.assertEqual(U.WEEKLY_STRIKES, 0)

    def test_defaults_when_env_unset_in_a_fresh_process(self):
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("DEPTH_", "UPSTOX_"))}
        env["DP_ROOT"] = tempfile.mkdtemp()
        code = ("import sys; sys.path.insert(0, %r); import dp_depthrec as R, dp_upstoxrec as U;"
                "print(R.DEPTH_WEEKLY_STRIKES, U.WEEKLY_STRIKES, R.DEPTH_STRIKES, U.STRIKES)"
                % os.path.join(os.path.dirname(HERE), "pullers", "shared"))
        out = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True,
                             text=True, check=True).stdout.split()
        self.assertEqual(out, ["0", "0", "12", "10"])

    def test_dhan_default_list_identical_to_old_code(self):
        for spot in (SPOT, 23010.0, 26990.0, 24975.5):
            fut, exp, wexp, chosen = R.select_d20(MASTER, TODAY, spot)
            self.assertIsNone(wexp)
            self.assertEqual(([o["SEM_SMST_SECURITY_ID"] for o, _ in chosen],
                              [x.isoformat() for _, x in chosen]), old_d20(MASTER, spot))
            self.assertLessEqual(len(chosen), 50)
        self.assertEqual(len(R.select_d20(MASTER, TODAY, SPOT)[3]), 50)

    def test_upstox_default_list_identical_to_old_code(self):
        for spot in (SPOT, 23010.0, 26990.0):
            self.assertEqual(U.instrument_keys(MASTER, TODAY, spot, n=10),
                             old_upstox(MASTER, spot))
        keys, _ = U.instrument_keys(MASTER, TODAY, SPOT)
        self.assertEqual(len(keys), 45)                      # the measured 45 keys

    def test_default_ignores_the_monthly_with_weekly_knob(self):
        a = R.select_d20(MASTER, TODAY, SPOT)[3]
        b = R.select_d20(MASTER, TODAY, SPOT, monthly_n_with_weekly=1)[3]
        self.assertEqual(a, b)


class SwitchedOn(unittest.TestCase):
    def test_nearest_weekly_not_other_index_not_monthly_date(self):
        opts, exp = R.nifty_weekly(MASTER, TODAY, date(2026, 11, 24))
        self.assertEqual(exp, date(2026, 11, 3))
        self.assertTrue(all(o["SEM_SMST_SECURITY_ID"].startswith("w1") for o in opts))
        _o, exp2 = R.nifty_weekly(MASTER, date(2026, 11, 4), date(2026, 11, 24))
        self.assertEqual(exp2, date(2026, 11, 10))
        _o, exp3 = R.nifty_weekly(MASTER, date(2026, 11, 11), date(2026, 11, 24))
        self.assertIsNone(exp3)                              # 24 Nov weekly == monthly: skipped

    def test_expiry_day_itself_still_included(self):
        _o, exp = R.nifty_weekly(MASTER, date(2026, 11, 3), date(2026, 11, 24))
        self.assertEqual(exp, date(2026, 11, 3))

    def test_dhan_on_split_inside_50_and_both_expiries(self):
        fut, exp, wexp, chosen = R.select_d20(MASTER, TODAY, SPOT, weekly_n=6)
        self.assertEqual((exp, wexp), (date(2026, 11, 24), date(2026, 11, 3)))
        self.assertLessEqual(len(chosen), 50)
        self.assertEqual(len(chosen), 26 + 22)
        ids = [o["SEM_SMST_SECURITY_ID"] for o, _ in chosen]
        self.assertEqual(len(ids), len(set(ids)))            # no duplicate subscription
        self.assertEqual({x for _, x in chosen}, {date(2026, 11, 3), date(2026, 11, 24)})
        w = [o for o, x in chosen if x == wexp]
        m = [o for o, x in chosen if x == exp]
        self.assertTrue(all(o["SEM_SMST_SECURITY_ID"].startswith("w1") for o in w))
        self.assertTrue(all(o["SEM_SMST_SECURITY_ID"].startswith("m") for o in m))
        self.assertEqual(sorted({float(o["SEM_STRIKE_PRICE"]) for o in w})[6], 25000.0)

    def test_dhan_sockets_unchanged_and_sub_within_limit(self):
        _f, _e, _w, chosen = R.select_d20(MASTER, TODAY, SPOT, weekly_n=6)
        s20, s200 = R.subscriptions([o["SEM_SMST_SECURITY_ID"] for o, _ in chosen], "61471")
        self.assertEqual(s20["InstrumentCount"], len(s20["InstrumentList"]))
        self.assertLessEqual(s20["InstrumentCount"], 50)
        self.assertEqual(s200["SecurityId"], "61471")        # the one 200-level contract: monthly future

    def _monthly_week_master(self):
        return ([row("NIFTY-Nov2026-FUT", "FUTIDX", "2026-11-24", sid="61471")]
                + chain("NIFTY-Nov2026-%d-%s", "2026-11-24", "M", "m")
                + chain("NIFTY-24Nov2026-%d-%s", "2026-11-24", "W", "wdup")
                + chain("NIFTY-01Dec2026-%d-%s", "2026-12-01", "W", "wnext"))

    def test_monthly_expiry_week_gives_the_expiring_monthly_the_wide_window(self):
        """Auditor A1: on 18-11..24-11 the 'weekly' is NEXT week's (01-12); the EXPIRING monthly must get the wide window."""
        rows = self._monthly_week_master(); today = date(2026, 11, 18)
        fut, mexp, wexp, picked = R.select_d20(rows, today, SPOT, weekly_n=6, monthly_n_with_weekly=5)
        self.assertEqual(mexp, date(2026, 11, 24)); self.assertEqual(wexp, date(2026, 12, 1))
        n_m = len([1 for o, e in picked if e == mexp]); n_w = len([1 for o, e in picked if e == wexp])
        self.assertEqual((n_m, n_w), (26, 22))                      # monthly 2*(2*6+1)=26, next weekly 2*(2*5+1)=22; was (22, 26)
        self.assertLessEqual(len(picked), R.D20_MAX)

    def test_window_sizes_normal_week_unchanged(self):
        self.assertEqual(R.window_sizes(date(2026, 11, 10), date(2026, 11, 24), 6, 5), (6, 5))
        self.assertEqual(R.window_sizes(None, date(2026, 11, 24), 6, 5), (6, 5))
        self.assertEqual(R.window_sizes(date(2026, 12, 1), date(2026, 11, 24), 6, 5), (5, 6))

    def test_upstox_monthly_week_same_rule_and_cap(self):
        rows = self._monthly_week_master()
        import datetime as _d
        keys, exp = U.instrument_keys(rows, date(2026, 11, 18), SPOT, weekly_n=5, monthly_n_with_weekly=5, max_keys=50)
        self.assertLessEqual(len(keys), 50)

    def test_dhan_over_ask_is_capped_at_50_not_exceeded(self):
        _f, _e, _w, chosen = R.select_d20(MASTER, TODAY, SPOT, weekly_n=12,
                                          monthly_n_with_weekly=12)
        self.assertEqual(len(chosen), 50)
        self.assertEqual(len({o["SEM_SMST_SECURITY_ID"] for o, _ in chosen}), 50)
        far = max(abs(float(o["SEM_STRIKE_PRICE"]) - SPOT) for o, _ in chosen)
        self.assertLessEqual(far, 12 * 50 + 50)

    def test_dhan_on_but_no_weekly_in_master_keeps_old_list(self):
        rows = [r for r in MASTER if r["SEM_EXPIRY_FLAG"] != "W"]
        got = R.select_d20(rows, TODAY, SPOT, weekly_n=6)
        self.assertIsNone(got[2])
        self.assertEqual([o["SEM_SMST_SECURITY_ID"] for o, _ in got[3]], old_d20(rows, SPOT)[0])

    def test_upstox_on_inside_50_keys_all_expiries(self):
        keys, exp = U.instrument_keys(MASTER, TODAY, SPOT, weekly_n=5)
        self.assertEqual(exp, date(2026, 11, 24))
        self.assertEqual(len(keys), 2 + 1 + 22 + 22)
        self.assertLessEqual(len(keys), 50)
        ks = [k[0] for k in keys]
        self.assertEqual(len(ks), len(set(ks)))
        self.assertEqual({k[2] for k in keys if k[2]}, {"2026-11-03", "2026-11-24"})
        self.assertEqual(ks[:3], ["NSE_INDEX|Nifty 50", "NSE_INDEX|India VIX", "NSE_FO|61471"])
        subs = U.subscriptions(ks, "full_d30")
        self.assertEqual([m for m, _ in subs], ["full", "full_d30"])
        self.assertLessEqual(len(subs[1][1]), 50)

    def test_upstox_over_ask_is_capped(self):
        keys, _ = U.instrument_keys(MASTER, TODAY, SPOT, weekly_n=12, monthly_n_with_weekly=12)
        self.assertEqual(len(keys), 50)
        self.assertEqual(len({k[0] for k in keys}), 50)
        self.assertEqual([k[0] for k in keys[:3]],
                         ["NSE_INDEX|Nifty 50", "NSE_INDEX|India VIX", "NSE_FO|61471"])

    def test_upstox_on_no_weekly_in_master_keeps_old_list(self):
        rows = [r for r in MASTER if r["SEM_EXPIRY_FLAG"] != "W"]
        self.assertEqual(U.instrument_keys(rows, TODAY, SPOT, weekly_n=5),
                         old_upstox(rows, SPOT))

    def test_env_switch_end_to_end_in_a_fresh_process(self):
        env = dict(os.environ, DP_ROOT=tempfile.mkdtemp(), DEPTH_WEEKLY_STRIKES="6",
                   UPSTOX_WEEKLY_STRIKES="5")
        code = ("import sys; sys.path.insert(0, %r); sys.path.insert(0, %r);"
                "import dp_depthrec as R, dp_upstoxrec as U, test_weekly_recorders as T;"
                "d=R.select_d20(T.MASTER,T.TODAY,T.SPOT)[3]; k=U.instrument_keys(T.MASTER,T.TODAY,T.SPOT)[0];"
                "print(len(d), len(k))" % (os.path.join(os.path.dirname(HERE), "pullers", "shared"), HERE))
        out = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True,
                             text=True, check=True).stdout.split()
        self.assertEqual(out, ["48", "47"])


if __name__ == "__main__":
    unittest.main()
