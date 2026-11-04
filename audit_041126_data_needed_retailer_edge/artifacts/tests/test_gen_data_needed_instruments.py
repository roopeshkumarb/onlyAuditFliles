"""Tests for tools/gen_data_needed_instruments_041126.py - runs the generator in a private copy of the
tree (symlinked code, fresh docs/framework) so the committed CSV/MD are never rewritten by the test."""
import csv
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(REPO, "tools", "gen_data_needed_instruments_041126.py")
CSV_NAME = "data_needed_instruments_041126.csv"
MD_NAME = "DATA_NEEDED_INSTRUMENTS_041126.md"


def _run_in_sandbox():
    root = tempfile.mkdtemp(prefix="gen_sandbox_")
    os.makedirs(os.path.join(root, "tools"))
    os.makedirs(os.path.join(root, "docs", "framework"))
    with open(GEN, encoding="utf-8") as src, open(os.path.join(root, "tools", os.path.basename(GEN)), "w", encoding="utf-8") as dst:
        dst.write(src.read())
    for name in os.listdir(REPO):
        if name in ("tools", "docs", ".git", ".claude") or name.startswith("."):
            continue
        os.symlink(os.path.join(REPO, name), os.path.join(root, name))
    for sub in os.listdir(os.path.join(REPO, "docs")):
        if sub != "framework":
            os.symlink(os.path.join(REPO, "docs", sub), os.path.join(root, "docs", sub))
    for f in os.listdir(os.path.join(REPO, "docs", "framework")):
        if f not in (CSV_NAME, MD_NAME):
            os.symlink(os.path.join(REPO, "docs", "framework", f), os.path.join(root, "docs", "framework", f))
    r = subprocess.run([sys.executable, os.path.join(root, "tools", os.path.basename(GEN))],
                       cwd=root, capture_output=True, text=True, timeout=300)
    return root, r


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root1, cls.r1 = _run_in_sandbox()
        cls.root2, cls.r2 = _run_in_sandbox()
        fw = os.path.join(cls.root1, "docs", "framework")
        cls.csv_path = os.path.join(fw, CSV_NAME)
        cls.md_path = os.path.join(fw, MD_NAME)
        cls.rows = list(csv.DictReader(open(cls.csv_path, newline="", encoding="utf-8"))) \
            if os.path.exists(cls.csv_path) else []

    def test_generator_runs_clean(self):
        self.assertEqual(self.r1.returncode, 0, self.r1.stderr[-800:])
        self.assertTrue(os.path.exists(self.csv_path) and os.path.exists(self.md_path))

    def test_regenerate_is_deterministic(self):
        for name in (CSV_NAME, MD_NAME):
            a = os.path.join(self.root1, "docs", "framework", name)
            b = os.path.join(self.root2, "docs", "framework", name)
            self.assertEqual(_sha(a), _sha(b), "%s differs between two runs" % name)

    def test_committed_files_match_a_fresh_regeneration(self):
        for name in (CSV_NAME, MD_NAME):
            fresh = os.path.join(self.root1, "docs", "framework", name)
            committed = os.path.join(REPO, "docs", "framework", name)
            self.assertEqual(_sha(fresh), _sha(committed),
                             "%s in the repo is stale: rerun tools/gen_data_needed_instruments_041126.py" % name)

    def test_no_blank_why_needed_and_no_missing_evidence(self):
        self.assertGreater(len(self.rows), 100)
        blank = [r.get("instrument_name") for r in self.rows if not (r.get("why_needed_for_regime") or "").strip()]
        self.assertEqual(blank, [], "blank why_needed_for_regime: %s" % blank[:5])
        self.assertFalse([r for r in self.rows if "MARKER-NOT-FOUND" in (r.get("evidence") or "")])

    def test_totals_in_md_recompute_from_csv(self):
        by_class = Counter(r["class"] for r in self.rows)
        md = open(self.md_path, encoding="utf-8").read()
        for klass, n in by_class.items():
            self.assertRegex(md, r"%s\W+%d\b" % (re.escape(klass), n),
                             "MD total for %s should be %d" % (klass, n))
        self.assertEqual(sum(by_class.values()), len(self.rows))

    def test_unknown_is_never_blank_or_zero(self):
        for r in self.rows:
            for k in ("symbol_upstox", "symbol_dhan", "symbol_kite", "symbol_fyers"):
                self.assertTrue((r.get(k) or "").strip(), "%s.%s is blank (must be a symbol or UNKNOWN)" % (r.get("instrument_name"), k))


if __name__ == "__main__":
    unittest.main()
