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


PACK = "docs/audit_pack_041126/"
NOW = datetime(2026, 11, 4, 12, 0, tzinfo=IST)


class ApprovalsGate(Base):
    """Fable round 2: the first gate accepted evidence "ok" and a deleted row. Each attack below must ALERT."""

    def led(self):
        return json.load(open(os.path.join(self.root, G.LEDGER)))

    def save(self, led):
        w(self.root, G.LEDGER, json.dumps(led))

    def evidence(self, rel, text=None):
        text = text if text is not None else "Independent review of tools/build.py: verdict PASS. Signed reviewer, 04-11-2026.\n"
        w(self.root, rel, text)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def approve(self, led, flag="fable", rel=None, text=None):
        rel = rel or (PACK + "%s_review.md" % flag)
        sha = self.evidence(rel, text)
        b = led["builds"][0]
        b[flag] = True
        b[flag + "_evidence"] = rel
        b[flag + "_evidence_sha256"] = sha
        return led

    def approve_all(self):
        led = self.led()
        for f in G.FLAGS:
            self.approve(led, f)
        led["builds"][0]["claimed_status"] = "DONE"
        self.save(led)

    def accept(self):
        return G.accept_state({"root": self.root, "now": NOW})

    def msgs(self, rep):
        return " | ".join(f["msg"] for f in self.alerts(rep, "APPROVALS"))

    def test_full_path_is_allowed_only_after_accept_state(self):
        self.approve_all()
        rep = self.run_guard()
        self.assertTrue(self.alerts(rep, "APPROVALS"), "DONE claimed but not accepted into the chain must ALERT")
        self.assertEqual(list(rep["done_allowed"].values()), [False])
        ok, msg = self.accept()
        self.assertTrue(ok, msg)
        rep = self.run_guard()
        self.assertEqual(self.alerts(rep, "APPROVALS"), [], self.msgs(rep))
        self.assertEqual(list(rep["done_allowed"].values()), [True])

    def test_attack_flip_all_flags_with_ok_text(self):
        led = self.led()
        b = led["builds"][0]
        b.update(fable=True, fable_evidence="approved in chat", external_auditor=True, external_auditor_evidence="ok",
                 kumar=True, kumar_evidence="ok", claimed_status="DONE")
        self.save(led)
        rep = self.run_guard()
        self.assertTrue(self.alerts(rep, "APPROVALS"))
        self.assertEqual(list(rep["done_allowed"].values()), [False])

    def test_attack_evidence_is_claude_md(self):
        led = self.led()
        self.approve(led, "fable", rel="CLAUDE.md")
        self.save(led)
        self.assertIn("not under", self.msgs(self.run_guard()))

    def test_attack_evidence_is_the_ledger_or_state_itself(self):
        for rel in (G.LEDGER, G.STATE):
            led = self.led()
            b = led["builds"][0]
            b.update(fable=True, fable_evidence=rel, fable_evidence_sha256="0" * 64)
            self.save(led)
            self.assertTrue(self.alerts(self.run_guard(), "APPROVALS"), rel)

    def test_attack_evidence_is_code_inside_the_allowed_folder(self):
        led = self.led()
        self.approve(led, "fable", rel=PACK + "notes.py", text="# tools/build.py approved " + "x" * 50)
        self.save(led)
        self.assertIn("code or a project control file", self.msgs(self.run_guard()))

    def test_attack_evidence_under_artifacts_copy_dir(self):
        led = self.led()
        self.approve(led, "fable", rel=PACK + "artifacts/docs/review.md")
        self.save(led)
        self.assertIn("artifacts/", self.msgs(self.run_guard()))

    def test_attack_evidence_file_missing(self):
        led = self.led()
        b = led["builds"][0]
        b.update(fable=True, fable_evidence=PACK + "nope.md", fable_evidence_sha256="a" * 64)
        self.save(led)
        self.assertIn("evidence file missing", self.msgs(self.run_guard()))

    def test_attack_hash_not_recorded_or_wrong(self):
        led = self.led()
        self.approve(led, "fable")
        led["builds"][0]["fable_evidence_sha256"] = ""
        self.save(led)
        self.assertIn("not recorded", self.msgs(self.run_guard()))
        led["builds"][0]["fable_evidence_sha256"] = "b" * 64
        self.save(led)
        self.assertIn("does not recompute", self.msgs(self.run_guard()))

    def test_attack_evidence_does_not_name_the_build(self):
        led = self.led()
        self.approve(led, "fable", text="This is a long enough review of something else entirely, all good.\n")
        self.save(led)
        self.assertIn("never names the build", self.msgs(self.run_guard()))

    def test_attack_evidence_too_small(self):
        led = self.led()
        self.approve(led, "fable", text="tools/build.py ok")
        self.save(led)
        self.assertIn("too small", self.msgs(self.run_guard()))

    def test_attack_path_traversal_and_absolute(self):
        for bad in ("../outside.md", "/etc/passwd", PACK + "../../CLAUDE.md"):
            led = self.led()
            led["builds"][0].update(fable=True, fable_evidence=bad, fable_evidence_sha256="c" * 64)
            self.save(led)
            self.assertTrue(self.alerts(self.run_guard(), "APPROVALS"), bad)

    def test_attack_delete_the_build_row(self):
        led = self.led()
        led["builds"].append({"path": "tools/other.py", "kind": "tool", "test": "tests/test_build.py",
                              "claimed_status": "DRAFT", "fable": False, "external_auditor": False, "kumar": False})
        self.save(led)
        w(self.root, "tools/other.py", "import os\n")
        ok, msg = self.accept()
        self.assertTrue(ok, msg)
        led["builds"] = led["builds"][:1]
        self.save(led)
        rep = self.run_guard()
        self.assertIn("removed from the ledger", self.msgs(rep))
        self.assertTrue(all(v is False for v in rep["done_allowed"].values()))

    def test_attack_flag_flipped_true_but_never_accepted(self):
        ok, _ = self.accept()
        led = self.led()
        self.approve(led, "fable")
        self.approve(led, "external_auditor")
        self.approve(led, "kumar")
        self.save(led)
        rep = self.run_guard()
        self.assertEqual(list(rep["done_allowed"].values()), [False])
        self.assertEqual(self.alerts(rep, "APPROVALS"), [])
        led["builds"][0]["claimed_status"] = "DONE"
        self.save(led)
        self.assertIn("lacks accepted approval", self.msgs(self.run_guard()))

    def test_attack_evidence_edited_after_acceptance(self):
        self.approve_all()
        self.assertTrue(self.accept()[0])
        w(self.root, PACK + "fable_review.md", "Rewritten after approval, still names tools/build.py in text. " * 2)
        rep = self.run_guard()
        self.assertTrue(self.alerts(rep, "APPROVALS"))
        self.assertEqual(list(rep["done_allowed"].values()), [False])

    def test_attack_evidence_and_recorded_hash_both_edited_after_acceptance(self):
        self.approve_all()
        self.assertTrue(self.accept()[0])
        led = self.led()
        new = "Rewritten after approval and re-hashed, still names tools/build.py in its text body.\n"
        led["builds"][0]["fable_evidence_sha256"] = self.evidence(PACK + "fable_review.md", new)
        self.save(led)
        rep = self.run_guard()
        self.assertIn("changed after it was accepted", self.msgs(rep))
        self.assertEqual(list(rep["done_allowed"].values()), [False])

    def test_one_removed_row_blocks_every_done_even_a_fully_approved_build(self):
        self.approve_all()
        led = self.led()
        led["builds"].append({"path": "tools/other.py", "kind": "tool", "test": "tests/test_build.py",
                              "claimed_status": "DRAFT", "fable": False, "external_auditor": False, "kumar": False})
        self.save(led)
        w(self.root, "tools/other.py", "import os\n")
        self.assertTrue(self.accept()[0])
        self.assertTrue(self.run_guard()["done_allowed"]["tools/build.py"])
        led["builds"] = led["builds"][:1]
        self.save(led)
        rep = self.run_guard()
        self.assertIn("removed from the ledger", self.msgs(rep))
        self.assertFalse(rep["done_allowed"]["tools/build.py"])

    def test_dotdot_inside_the_allowed_folder_is_still_refused_by_name(self):
        led = self.led()
        self.approve(led, "fable", rel=PACK + "sub/../fable_review.md")
        self.save(led)
        self.assertIn("relative path inside the repo", self.msgs(self.run_guard()))

    def test_attack_state_chain_tampered_or_entry_dropped(self):
        self.approve_all()
        self.assertTrue(self.accept()[0])
        self.assertTrue(self.accept()[0])
        sp = os.path.join(self.root, G.STATE)
        good = open(sp, encoding="utf-8").read()
        st = json.loads(good)
        st["entries"][0]["builds"]["tools/build.py"]["claimed_status"] = "EDITED"
        open(sp, "w", encoding="utf-8").write(json.dumps(st))
        rep = self.run_guard()
        self.assertIn("chain broken", self.msgs(rep))
        self.assertEqual(list(rep["done_allowed"].values()), [False])
        st = json.loads(good)
        del st["entries"][0]
        open(sp, "w", encoding="utf-8").write(json.dumps(st))
        self.assertIn("chain broken", self.msgs(self.run_guard()))

    def test_attack_state_file_deleted_while_flags_true(self):
        self.approve_all()
        self.assertTrue(self.accept()[0])
        os.remove(os.path.join(self.root, G.STATE))
        rep = self.run_guard()
        self.assertIn("no accepted state chain", self.msgs(rep))
        self.assertEqual(list(rep["done_allowed"].values()), [False])

    def test_accept_state_is_refused_while_an_alert_stands(self):
        led = self.led()
        led["builds"][0].update(fable=True, fable_evidence="ok")
        self.save(led)
        ok, msg = self.accept()
        self.assertFalse(ok)
        self.assertIn("refused", msg)
        self.assertFalse(os.path.exists(os.path.join(self.root, G.STATE)))

    def test_every_problem_status_is_alerted_when_unapproved(self):
        self.assertEqual(set(G.PROBLEM_STATUS), {"DONE", "COMPLETE", "COMPLETED", "GREEN", "PROVEN", "APPROVED"})
        for st in sorted(G.PROBLEM_STATUS):
            led = self.led()
            led["builds"][0]["claimed_status"] = st.lower()
            self.save(led)
            self.assertIn("claims %s" % st, self.msgs(self.run_guard()), st)

    def test_draft_and_proposed_status_are_not_alerted(self):
        for st in ("DRAFT", "PROPOSED", ""):
            led = self.led()
            led["builds"][0]["claimed_status"] = st
            self.save(led)
            self.assertEqual(self.alerts(self.run_guard(), "APPROVALS"), [], st)


class ExitCode(unittest.TestCase):
    """G3: main() must return 1 on any ALERT, 0 on none, 2 when the guard cannot run."""

    def fake(self, alerts):
        return {"summary_line": "x", "findings": [], "fixes": [],
                "counts": {G.ALERT: alerts, G.INFO: 0, G.OK: 1}}

    def call(self, fn):
        old = G.run
        G.run = fn
        try:
            return G.main(["--no-report", "--root", tempfile.gettempdir()])
        finally:
            G.run = old

    def test_alert_gives_exit_1(self):
        self.assertEqual(self.call(lambda ctx: self.fake(3)), 1)

    def test_no_alert_gives_exit_0(self):
        self.assertEqual(self.call(lambda ctx: self.fake(0)), 0)

    def test_crash_gives_exit_2(self):
        def boom(ctx):
            raise RuntimeError("x")
        self.assertEqual(self.call(boom), 2)


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
