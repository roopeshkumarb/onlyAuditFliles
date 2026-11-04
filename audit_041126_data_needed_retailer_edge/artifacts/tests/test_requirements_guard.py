"""tests/test_requirements_guard.py - tools/requirements_guard.py on a synthetic repo.

A clean fixture must give zero ALERT; then each rule is broken on purpose and must be caught.
Pure unittest, no box, no network, nothing outside a temp dir.
"""
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "pullers", "shared"))
import requirements_guard as G  # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))
REG = json.load(open(os.path.join(REPO, "docs", "framework", "REQUIREMENTS_REGISTER.json"), encoding="utf-8"))
CFG = {"classes": {
    "live_depth": {"recoverable": False, "patterns": ["depth", "tick"]},
    "window_limited_intraday": {"recoverable": False, "patterns": ["global_1m"]},
    "history_candles": {"recoverable": True, "patterns": ["nifty_1m", "candles"]},
}}
FAMS = {"candles_index_1m": {"tables": ["W.nifty_1m"], "kind": "candles", "sources": ["upstox"]},
        "quote_depth": {"tables": ["W.depth_1m"], "kind": "quote", "sources": ["upstox"]}}
HEADER = ["group", "instrument_name", "feeds_by_brokers", "class", "store_table", "why_needed_for_regime", "evidence", "note"]


def w(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


def write_csv(root, rows):
    lines = [",".join(HEADER)] + [",".join(r) for r in rows]
    w(root, G.CSV_PATH, "\n".join(lines) + "\n")


GOOD_ROWS = [["IDX", "NIFTY 50", "upstox", "PULLABLE_RECOVERABLE", "W.nifty_1m", "traded series", "dp.py:1", ""],
             ["OPT", "NIFTY weekly 23000 CE", "upstox", "LIVE_ONLY_NON_RECOVERABLE", "W.depth_1m", "depth weekly", "dp.py:2", ""]]
GOOD_MD = ("| class | rows |\n|---|---|\n| LIVE_ONLY_NON_RECOVERABLE | 1 |\n| PULLABLE_RECOVERABLE | 1 |\n"
           "| UNKNOWN | 0 |\n| **all** | **2** |\n")


def make_repo(root):
    reg = copy.deepcopy(REG)
    for r in reg["requirements"]:
        r["evidence_files"] = []
    reg["move_safety_markers"] = {"tools/mover.sh": ["sha256sum", "ALLOW_REMOVE"], "tools/build.py": ["os.replace", "fsync"]}
    w(root, G.REGISTER, json.dumps(reg))
    ledger = {"builds": [{"path": "tools/build.py", "kind": "tool", "test": "tests/test_build.py", "claimed_status": "DRAFT",
                          "fable": False, "external_auditor": False, "kumar": False}]}
    w(root, G.LEDGER, json.dumps(ledger))
    w(root, "tools/build.py", "import os\nos.replace('a','b')\nos.fsync(1)\n")
    w(root, "tools/mover.sh", "sha256sum x\nALLOW_REMOVE=0\n")
    w(root, "tests/test_build.py", "def test_x():\n    pass\n")
    w(root, "CLAUDE.md", "rules\n")
    w(root, "docs/framework/AUDIT_PUBLISH_RULE.md", "use roopeshkumarb/onlyAuditFliles\n")
    w(root, "docs/framework/data_lifecycle_policy.json", json.dumps({"hot_ssd": {"min_free_gb": 40, "min_free_percent": 40}}))
    w(root, G.MD_PATH, GOOD_MD)
    write_csv(root, GOOD_ROWS)
    w(root, G.TASKS, json.dumps({"ev": "add", "id": "T-1", "at": "04-11-2026 10:00 GMT+5:30", "by": "c", "title": "does R02 work", "note": ""}) + "\n")
    return root


def tree_hash(root):
    h = hashlib.sha256()
    for d, _ds, fs in sorted(os.walk(root)):
        for fn in sorted(fs):
            p = os.path.join(d, fn)
            h.update(p.encode())
            h.update(open(p, "rb").read())
    return h.hexdigest()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="reqguard_")
        self.root = make_repo(self.tmp)
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def run_guard(self, **kw):
        ctx = {"root": self.root, "rec_cfg": CFG, "families": FAMS,
               "now": datetime(2026, 11, 4, 12, 0, tzinfo=IST)}
        ctx.update(kw)
        return G.run(ctx)

    def alerts(self, rep, rule=None):
        return [f for f in rep["findings"] if f["level"] == G.ALERT and (rule is None or f["rule"] == rule)]


class Clean(Base):
    def test_clean_fixture_has_no_alert(self):
        rep = self.run_guard()
        self.assertEqual(self.alerts(rep), [], [f["msg"] for f in self.alerts(rep)])

    def test_guard_is_read_only_by_default(self):
        before = tree_hash(self.root)
        self.run_guard()
        self.assertEqual(before, tree_hash(self.root))

    def test_done_allowed_needs_all_three(self):
        rep = self.run_guard()
        self.assertEqual(list(rep["done_allowed"].values()), [False])
        led = json.load(open(os.path.join(self.root, G.LEDGER)))
        b = led["builds"][0]
        b.update(fable=True, fable_evidence="docs/framework/AUDIT_PUBLISH_RULE.md", external_auditor=True,
                 external_auditor_evidence="audit repo commit abc", kumar=True, kumar_evidence="04-11 'approved'",
                 claimed_status="DONE")
        w(self.root, G.LEDGER, json.dumps(led))
        rep = self.run_guard()
        self.assertEqual(self.alerts(rep, "APPROVALS"), [])
        self.assertEqual(list(rep["done_allowed"].values()), [True])


class Mutations(Base):
    def test_m1_unmapped_work_is_alerted(self):
        w(self.root, G.TASKS, open(os.path.join(self.root, G.TASKS)).read() +
          json.dumps({"ev": "add", "id": "T-2", "at": "04-11-2026 11:00 GMT+5:30", "by": "c", "title": "random side quest"}) + "\n")
        self.assertTrue(any("T-2" in f["msg"] for f in self.alerts(self.run_guard(), "TRACE")))

    def test_m1b_old_work_before_cutoff_is_not_flagged(self):
        w(self.root, G.TASKS, open(os.path.join(self.root, G.TASKS)).read() +
          json.dumps({"ev": "add", "id": "T-0", "at": "01-10-2026 11:00 GMT+5:30", "by": "c", "title": "old"}) + "\n")
        self.assertFalse(any("T-0" in f["msg"] for f in self.alerts(self.run_guard(), "TRACE")))

    def test_m2_live_only_classed_recoverable_is_alerted(self):
        bad = copy.deepcopy(CFG)
        bad["classes"]["live_depth"]["patterns"] = ["zzz"]
        bad["classes"]["history_candles"]["patterns"].append("depth")
        self.assertTrue(self.alerts(self.run_guard(rec_cfg=bad), "JOIN_LIVE_SAFE"))

    def test_m2b_window_limited_table_classed_recoverable_is_alerted(self):
        bad = copy.deepcopy(CFG)
        bad["classes"]["window_limited_intraday"]["patterns"] = ["zzz"]
        bad["classes"]["history_candles"]["patterns"].append("global_1m")
        self.assertTrue(any("global_1m" in f["msg"] for f in self.alerts(self.run_guard(rec_cfg=bad), "JOIN_LIVE_SAFE")))

    def test_m3_unknown_table_is_alerted(self):
        fams = dict(FAMS)
        fams["x"] = {"tables": ["W.mystery_tbl"], "kind": "candles", "sources": ["upstox"]}
        self.assertTrue(self.alerts(self.run_guard(families=fams), "JOIN_UNKNOWN"))

    def test_m4_csv_total_mismatch_is_alerted_and_fix_regenerates(self):
        w(self.root, G.MD_PATH, GOOD_MD.replace("| PULLABLE_RECOVERABLE | 1 |", "| PULLABLE_RECOVERABLE | 9 |"))
        self.assertTrue(self.alerts(self.run_guard(), "CSV_TOTALS"))
        gen = w(self.root, "gen_stub.py", "import sys\nopen(sys.argv[1], 'w').write(%r)\n" % GOOD_MD)
        rep = self.run_guard(fix=True, gen_cmd=[sys.executable, gen, os.path.join(self.root, G.MD_PATH)])
        self.assertTrue(rep["fixes"] and rep["fixes"][0]["applied"])
        self.assertEqual(self.alerts(rep, "CSV_TOTALS"), [])

    def test_m4b_fix_never_runs_without_the_flag(self):
        w(self.root, G.MD_PATH, GOOD_MD.replace("| UNKNOWN | 0 |", "| UNKNOWN | 5 |"))
        rep = self.run_guard()
        self.assertEqual(rep["fixes"], [])
        self.assertTrue(self.alerts(rep, "CSV_TOTALS"))

    def test_m5_false_done_without_approval_is_alerted(self):
        led = json.load(open(os.path.join(self.root, G.LEDGER)))
        led["builds"][0]["claimed_status"] = "DONE"
        w(self.root, G.LEDGER, json.dumps(led))
        self.assertTrue(any("claims DONE" in f["msg"] for f in self.alerts(self.run_guard(), "APPROVALS")))

    def test_m5b_approval_flag_without_evidence_is_alerted(self):
        led = json.load(open(os.path.join(self.root, G.LEDGER)))
        led["builds"][0]["fable"] = True
        w(self.root, G.LEDGER, json.dumps(led))
        self.assertTrue(any("no fable_evidence" in f["msg"] for f in self.alerts(self.run_guard(), "APPROVALS")))

    def test_m6_new_code_stopping_an_old_puller_is_alerted(self):
        w(self.root, "tools/build.py", "import os\nos.replace('a','b')\nos.fsync(1)\nos.system('docker stop kitepuller')\n")
        self.assertTrue(self.alerts(self.run_guard(), "NO_OLD_STOP"))

    def test_m6b_stopping_cloudflared_is_alerted(self):
        w(self.root, "tools/build.py", "import os\nos.replace('a','b')\nos.fsync(1)\nos.system('docker rm cloudflared')\n")
        self.assertTrue(self.alerts(self.run_guard(), "NO_OLD_STOP"))

    def test_m7_missing_test_file_is_alerted(self):
        os.remove(os.path.join(self.root, "tests/test_build.py"))
        self.assertTrue(self.alerts(self.run_guard(), "TOOL_TESTS"))

    def test_m8_nonrecoverable_file_on_ssd_is_alerted(self):
        ssd = os.path.join(self.tmp, "ssd")
        w(ssd, "upstox/upstox_tick_20261104.db", "x")
        self.assertTrue(self.alerts(self.run_guard(ssd_roots=[ssd]), "SSD_NONREC"))

    def test_m8b_recoverable_file_on_ssd_is_fine(self):
        ssd = os.path.join(self.tmp, "ssd")
        w(ssd, "upstox/upstox_candles_20261104.db", "x")
        self.assertEqual(self.alerts(self.run_guard(ssd_roots=[ssd]), "SSD_NONREC"), [])

    def test_m9_missing_box_policy_is_alerted(self):
        self.assertTrue(self.alerts(self.run_guard(policy_paths=[os.path.join(self.tmp, "nope.json")]), "POLICY_FILE"))

    def test_m9b_wrong_min_free_is_alerted(self):
        w(self.root, "docs/framework/data_lifecycle_policy.json", json.dumps({"hot_ssd": {"min_free_gb": 10, "min_free_percent": 40}}))
        self.assertTrue(self.alerts(self.run_guard(), "POLICY_FILE"))

    def test_m10_friday_deadline_unverified_is_alerted(self):
        late = datetime(2026, 11, 6, 20, 5, tzinfo=IST)
        self.assertTrue(self.alerts(self.run_guard(now=late), "FRIDAY_SSD"))

    def test_m10b_friday_deadline_with_files_left_is_alerted(self):
        ssd = os.path.join(self.tmp, "ssd")
        w(ssd, "a/b.db", "x")
        late = datetime(2026, 11, 6, 20, 5, tzinfo=IST)
        self.assertTrue(self.alerts(self.run_guard(now=late, ssd_roots=[ssd]), "FRIDAY_SSD"))

    def test_m11_move_safety_marker_removed_is_alerted(self):
        w(self.root, "tools/mover.sh", "cp a b\n")
        self.assertTrue(self.alerts(self.run_guard(), "MOVE_SAFETY"))

    def test_m12_live_only_row_without_broker_is_alerted(self):
        write_csv(self.root, [GOOD_ROWS[0], ["OPT", "X", "", "LIVE_ONLY_NON_RECOVERABLE", "W.depth_1m", "w", "e", ""]])
        self.assertTrue(self.alerts(self.run_guard(), "INSTR_DETAIL"))

    def test_m13_empty_why_and_marker_not_found_are_alerted(self):
        write_csv(self.root, [["I", "A", "u", "PULLABLE_RECOVERABLE", "t", "", "MARKER-NOT-FOUND(x)", ""],
                              ["I", "B", "u", "PULLABLE_RECOVERABLE", "t", "", "ok", ""]])
        msgs = " ".join(f["msg"] for f in self.alerts(self.run_guard(), "INSTR_DETAIL"))
        self.assertIn("why_needed_for_regime", msgs)
        self.assertIn("MARKER-NOT-FOUND", msgs)

    def test_m14_no_weekly_row_is_alerted(self):
        write_csv(self.root, [GOOD_ROWS[0]])
        w(self.root, G.MD_PATH, GOOD_MD.replace("LIVE_ONLY_NON_RECOVERABLE | 1", "LIVE_ONLY_NON_RECOVERABLE | 0").replace("**2**", "**1**"))
        self.assertTrue(self.alerts(self.run_guard(), "WEEKLY_PRESENT"))

    def test_m15_new_bat_build_is_alerted(self):
        led = json.load(open(os.path.join(self.root, G.LEDGER)))
        led["builds"].append({"path": "tools/connect.bat", "kind": "tool", "test": "tests/test_build.py", "claimed_status": "DRAFT"})
        w(self.root, G.LEDGER, json.dumps(led))
        w(self.root, "tools/connect.bat", "echo hi\n")
        self.assertTrue(self.alerts(self.run_guard(), "NO_BAT"))

    def test_m16_missing_audit_repo_is_alerted(self):
        w(self.root, "docs/framework/AUDIT_PUBLISH_RULE.md", "post it anywhere\n")
        self.assertTrue(self.alerts(self.run_guard(), "AUDIT_REPO"))

    def test_m17_crashing_rule_is_loud_not_a_pass(self):
        self.assertTrue(self.alerts(self.run_guard(families={"x": {"kind": "candles"}}), "JOIN_UNKNOWN"))

    def test_m18_missing_evidence_file_turns_requirement_red(self):
        reg = json.load(open(os.path.join(self.root, G.REGISTER)))
        reg["requirements"][0]["evidence_files"] = ["docs/framework/NOPE.md"]
        w(self.root, G.REGISTER, json.dumps(reg))
        rep = self.run_guard()
        self.assertEqual(rep["requirements"]["R01"]["status"], "RED")

    def test_trace_only_requirement_is_never_green(self):
        rep = self.run_guard()
        self.assertEqual(rep["requirements"]["R07"]["status"], "AMBER")


class Register(unittest.TestCase):
    def test_register_has_31_requirements_and_5_sequence_rules(self):
        self.assertEqual([r["id"] for r in REG["requirements"]], ["R%02d" % i for i in range(1, 32)])
        self.assertEqual([s["id"] for s in REG["sequence"]], ["S1", "S2", "S3", "S4", "S5"])

    def test_every_mapped_rule_exists(self):
        for r in REG["requirements"] + REG["sequence"]:
            for rule in r["rules"]:
                self.assertIn(rule, G.RULES, "%s maps unknown rule %s" % (r["id"], rule))


if __name__ == "__main__":
    unittest.main()
