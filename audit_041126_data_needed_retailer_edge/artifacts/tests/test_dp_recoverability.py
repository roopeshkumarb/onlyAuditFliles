import os, sys, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pullers", "shared"))
import dp_recoverability as R

I5 = {"ssd": ["/volume2/datapullers"], "hdd": ["/volume1/docker/datapullers"], "ram": ["/dev/shm"]}
PI = {"ssd": ["/share/datapullers"], "hdd": [], "ram": ["/dev/shm"]}


class Classify(unittest.TestCase):
    def test_ticks_depth_chain_are_non_recoverable(self):
        for n in ("ticks_20261026.db", "fyerstbt_day.db", "dhan200_depth_20261027.db", "option_order_flow_x.db", "opt_chain_1m_live.db"):
            self.assertEqual(R.classify(n)[0], R.NON, n)

    def test_history_is_recoverable(self):
        for n in ("kite_history_candles_RELIANCE.db", "nse_bhavcopy_2026.db"):
            self.assertEqual(R.classify(n)[0], R.REC, n)

    def test_both_kinds_in_one_name_is_non_recoverable(self):
        self.assertEqual(R.classify("history_ticks_mix.db")[0], R.NON)

    def test_unknown_is_protected_not_ssd(self):
        c, rule, unk = R.effective("zzz_mystery_file.db")
        self.assertEqual((c, unk), (R.NON, True))


class Route(unittest.TestCase):
    def test_non_recoverable_goes_to_hdd_only(self):
        r = R.route(R.NON, I5)
        self.assertEqual(r["roots"], I5["hdd"])
        self.assertNotIn("/volume2/datapullers", r["roots"])

    def test_recoverable_goes_to_ssd(self):
        self.assertEqual(R.route(R.REC, I5)["roots"], I5["ssd"])

    def test_pi_has_no_hdd_so_non_recoverable_is_refused_not_put_on_ssd(self):
        r = R.route(R.NON, PI)
        self.assertEqual((r["status"], r["roots"]), ("NO_HDD", []))

    def test_pi_takes_recoverable_on_its_ssd(self):
        self.assertEqual(R.route(R.REC, PI)["roots"], PI["ssd"])


class Check(unittest.TestCase):
    def test_tick_file_on_ssd_is_a_violation(self):
        self.assertIsNotNone(R.check_path("/volume2/datapullers/upstox/ticks_20261026.db", I5))

    def test_tick_file_on_hdd_is_fine(self):
        self.assertIsNone(R.check_path("/volume1/docker/datapullers/upstox/ticks_20261026.db", I5))

    def test_history_on_ssd_is_fine(self):
        self.assertIsNone(R.check_path("/volume2/datapullers/kite/kite_history_candles_A.db", I5))

    def test_unknown_name_on_ssd_is_flagged(self):
        v = R.check_path("/volume2/datapullers/x/mystery.db", I5)
        self.assertIn("UNKNOWN", v)

    def test_scan_lists_only_violations(self):
        out = R.scan(["/volume2/datapullers/a/ticks_1.db", "/volume2/datapullers/a/history_1.db", "/volume1/docker/datapullers/a/ticks_2.db"], I5)
        self.assertEqual(len(out), 1)


class Pinned(unittest.TestCase):
    def test_only_the_file_name_decides_not_the_folder(self):
        self.assertEqual(R.classify("/data/ticks_archive/kite_history_candles_A.db")[0], R.REC)
        self.assertEqual(R.classify("/data/history/ticks_20261026.db")[0], R.NON)

    def test_route_statuses(self):
        self.assertEqual(R.route(R.NON, I5)["status"], "OK")
        self.assertEqual(R.route(R.REC, I5)["status"], "OK")

    def test_two_ssd_roots_either_one_is_flagged(self):
        roots = {"ssd": ["/s1", "/s2"], "hdd": ["/h1"]}
        self.assertIsNotNone(R.check_path("/s2/x/ticks_1.db", roots))
        self.assertIsNotNone(R.check_path("/s1/x/ticks_1.db", roots))

    def test_violation_text_names_the_rule_or_says_unclassified(self):
        self.assertIn("live_ticks", R.check_path("/volume2/datapullers/a/ticks_1.db", I5))
        self.assertIn("unclassified", R.check_path("/volume2/datapullers/a/zzz.db", I5))

    def test_non_recoverable_never_falls_back_to_ssd_even_when_hdd_empty(self):
        self.assertEqual(R.route(R.NON, {"ssd": ["/s"], "hdd": []})["roots"], [])


class Branches(unittest.TestCase):
    def test_recoverable_with_no_ssd_uses_hdd(self):
        r = R.route(R.REC, {"ssd": [], "hdd": ["/h"]})
        self.assertEqual((r["status"], r["roots"]), ("OK", ["/h"]))

    def test_recoverable_with_no_disk_is_refused(self):
        self.assertEqual(R.route(R.REC, {"ssd": [], "hdd": []})["status"], "NO_DISK")

    def test_route_rejects_an_unresolved_class(self):
        with self.assertRaises(ValueError):
            R.route(R.UNK, I5)

    def test_root_prefix_is_not_a_match(self):
        # /volume2x is NOT under /volume2
        self.assertIsNone(R.check_path("/volume2x/ticks_1.db", {"ssd": ["/volume2"], "hdd": []}))


try:
    from hypothesis import given, settings, strategies as st
    HAVE_H = True
except ImportError:
    HAVE_H = False

if HAVE_H:
    names = st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=60)
    roots_st = st.fixed_dictionaries({"ssd": st.lists(st.sampled_from(["/s1", "/s2"]), max_size=2), "hdd": st.lists(st.sampled_from(["/h1", "/h2"]), max_size=2)})

    class Properties(unittest.TestCase):
        @settings(max_examples=300, deadline=None)
        @given(names)
        def test_effective_is_never_unknown_and_never_raises(self, n):
            self.assertIn(R.effective(n)[0], (R.NON, R.REC))

        @settings(max_examples=300, deadline=None)
        @given(roots_st)
        def test_non_recoverable_never_routes_to_an_ssd_root(self, roots):
            r = R.route(R.NON, roots)
            self.assertFalse(set(r["roots"]) & set(roots["ssd"]) - set(roots["hdd"]))
            if not roots["hdd"]:
                self.assertEqual(r["status"], "NO_HDD")

        @settings(max_examples=300, deadline=None)
        @given(st.sampled_from(["ticks", "tbt_x", "depth_1m", "order_flow", "chain_snap", "news_items", "quote"]), names)
        def test_a_non_recoverable_name_under_any_ssd_root_is_always_flagged(self, stem, tail):
            tail = tail.replace("/", "_")
            path = "/s1/dir/" + stem + tail + ".db"
            self.assertIsNotNone(R.check_path(path, {"ssd": ["/s1"], "hdd": ["/h1"]}))


if __name__ == "__main__":
    unittest.main()
