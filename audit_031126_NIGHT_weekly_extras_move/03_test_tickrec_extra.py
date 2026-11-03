"""tests/test_tickrec_extra.py - TICK_EXTRA instruments on the Kite socket: pure selection, off by default, failure-tolerant."""
import os, sys, unittest
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pullers", "shared"))
import dp_tickrec as T  # noqa: E402

TODAY = date(2026, 11, 4)
def row(tok, sym, **kw):
    d = {"instrument_token": tok, "tradingsymbol": sym, "name": kw.pop("name", sym), "instrument_type": kw.pop("it", "EQ"),
         "expiry": kw.pop("expiry", None), "strike": 0.0, "lot_size": 1}
    d.update(kw); return d

class X(unittest.TestCase):
    def setUp(self):
        self.nse = [row(1, "NIFTY BANK", it="EQ"), row(2, "NIFTY FIN SERVICE"), row(3, "NIFTYBEES"), row(4, "RELIANCE"), row(5, "HDFCBANK"), row(6, "OTHER")]
        self.nfo = [row(10, "BANKNIFTY26NOVFUT", name="BANKNIFTY", it="FUT", expiry=date(2026, 11, 25)),
                    row(11, "BANKNIFTY26DECFUT", name="BANKNIFTY", it="FUT", expiry=date(2026, 12, 30)),
                    row(12, "BANKNIFTY26OLDFUT", name="BANKNIFTY", it="FUT", expiry=date(2026, 10, 28))]
        self.cds = [row(20, "USDINR26NOVFUT", name="USDINR", it="FUT", expiry=date(2026, 11, 27))]
        self.mcx = [row(30, "CRUDEOIL26NOVFUT", name="CRUDEOIL", it="FUT", expiry=date(2026, 11, 19)),
                    row(31, "GOLD26DECFUT", name="GOLD", it="FUT", expiry=date(2026, 12, 4))]

    def test_default_is_off(self):
        self.assertFalse(T.TICK_EXTRA)

    def test_macro_defaults_off_and_constituents_default_to_all_50(self):
        self.assertFalse(T.TICK_EXTRA_MACRO); self.assertEqual(T.TICK_EXTRA_EQ, 50)

    def test_run_session_does_not_ask_for_cds_or_mcx_unless_macro_is_on(self):
        src = open(T.__file__).read()
        self.assertIn('_get("CDS") if TICK_EXTRA_MACRO else []', src); self.assertIn('_get("MCX") if TICK_EXTRA_MACRO else []', src)

    def test_picks_indices_etf_constituents_and_nearest_futures(self):
        got = T.pick_extra(self.nse, self.nfo, self.cds, self.mcx, TODAY, ["RELIANCE", "HDFCBANK", "MISSING"], 3)
        toks = [i["instrument_token"] for i in got]
        self.assertEqual(sorted(toks), [1, 2, 3, 4, 5, 10, 20, 30, 31])
        self.assertNotIn(12, toks)            # an expired future is never picked
        self.assertNotIn(11, toks)            # only the NEAREST future
        self.assertTrue(all(i["why"].startswith("extra:") for i in got))

    def test_failed_exchange_lists_are_skipped_not_fatal(self):
        got = T.pick_extra(self.nse, self.nfo, [], [], TODAY, [], 0)
        self.assertEqual(sorted(i["instrument_token"] for i in got), [1, 2, 3, 10])

    def test_constituent_count_is_capped(self):
        got = T.pick_extra(self.nse, [], [], [], TODAY, ["RELIANCE", "HDFCBANK"], 1)
        self.assertEqual(len([i for i in got if "constituent" in i["why"]]), 1)

    def test_no_duplicate_tokens(self):
        got = T.pick_extra(self.nse + [row(4, "RELIANCE")], self.nfo, self.cds, self.mcx, TODAY, ["RELIANCE"], 5)
        toks = [i["instrument_token"] for i in got]
        self.assertEqual(len(toks), len(set(toks)))

    def test_compose_entrypoint_copies_the_symbol_file_into_the_container(self):
        y = open(os.path.join(os.path.dirname(HERE), "docker-compose.datapullers.yml")).read()
        self.assertIn("cp /src/dp_tickrec.py /src/nifty50_syms.txt /app/", y)     # found by the 2nd Fable review: the first version copied only the .py

    def test_empty_constituent_list_is_reported_not_silent(self):
        self.assertIn("constituent list EMPTY", open(T.__file__).read())

    def test_nifty50_symbols_come_from_the_config(self):
        syms = T._eq_syms()
        self.assertGreaterEqual(len(syms), 45); self.assertIn("RELIANCE", syms); self.assertIn("BAJAJ-AUTO", syms)

if __name__ == "__main__":
    unittest.main()
