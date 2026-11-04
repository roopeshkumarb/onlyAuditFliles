#!/usr/bin/env python3
"""Mutation runner behind MUTATION_LOG.txt. Each mutation patches ONE exact string in a throwaway copy of tools/tests/pullers-shared/docs-framework/config, runs the guard and builder test files, and records CAUGHT (first failing test) or SURVIVED. Run: python3 docs/audit_pack_041126/mutation_runner.py [ID ...]   (the repo itself is never modified)."""
import os, re, shutil, subprocess, sys, tempfile, time
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COPY = ["tools", "tests", "pullers/shared", "docs/framework", "config"]
G, Bd = "tools/requirements_guard.py", "tools/retailer_db_build.py"
TESTS = ["tests/test_requirements_guard.py", "tests/test_retailer_db_build.py"]
M = [
 # id, file, old, new, count, description
 ("G1", G, 'if not os.path.isfile(full) or not os.path.realpath(full).startswith(root_real + os.sep):', 'if False:', 1, "delete the evidence-file-exists branch (Fable G1)"),
 ("G2", G, 'PROBLEM_STATUS = ("DONE", "COMPLETE", "COMPLETED", "GREEN", "PROVEN", "APPROVED")', 'PROBLEM_STATUS = ("DONE", "COMPLETE")', 1, "shrink PROBLEM_STATUS to DONE/COMPLETE (Fable G2)"),
 ("G3", G, 'return 1 if rep["counts"][ALERT] else 0', 'return 0', 1, "main() always exits 0 (Fable G3)"),
 ("G4", G, 'if rec != _sha_bytes(data):', 'if False:', 1, "evidence sha256 never recomputed"),
 ("G5", G, 'if b["path"].encode("utf-8") not in data:', 'if False:', 1, "evidence need not name the build"),
 ("G6", G, 'if not any(rel.startswith(d) for d in EVIDENCE_DIRS):', 'if False:', 1, "evidence may live anywhere (e.g. CLAUDE.md)"),
 ("G7", G, 'if any(rel.startswith(d) for d in EVIDENCE_EXCLUDED_DIRS):', 'if False:', 1, "artifacts/ copies accepted as evidence"),
 ("G8", G, 'if base in EVIDENCE_FORBIDDEN_NAMES or base.endswith(EVIDENCE_CODE_SUFFIXES):', 'if False:', 1, "code / control files accepted as evidence"),
 ("G9", G, 'if sp not in paths:', 'if False:', 1, "removed ledger row not alerted"),
 ("G10", G, 'if e.get("seq") != i or e.get("prev") != prev or e.get("hash") != _chain_hash(prev, i, e.get("builds", {})):', 'if False:', 1, "hash chain never verified"),
 ("G11", G, 'if (old["evidence"], old["sha256"].lower()) != cur:', 'if False:', 1, "evidence edited after acceptance not alerted"),
 ("G12", G, ' and b["path"] not in blocked and "*" not in blocked', '', 1, "done_allowed ignores approvals ALERTs"),
 ("G13", G, '    bad = [f for f in r_approvals(ctx) if f["level"] == ALERT]\n    if bad:', '    bad = [f for f in r_approvals(ctx) if f["level"] == ALERT]\n    if False:', 1, "accept_state accepts while an ALERT stands"),
 ("G14", G, '".." in raw.replace("\\\\", "/").split("/")', 'False', 1, "path traversal not rejected by name"),
 ("G15", G, 'MIN_EVIDENCE_BYTES = 40', 'MIN_EVIDENCE_BYTES = 0', 1, "empty / tiny evidence files accepted"),
 ("G16", G, 'if any_true and not ctx.get("accepting"):', 'if False:', 1, "true flags with no state chain not alerted"),
 ("B1", Bd, 'if n != ins:', 'if False:', 1, "_verify row-count check deleted (Fable B1)"),
 ("B1b", Bd, 'if rd != ins + dup + rej:', 'if False:', 1, "_verify read=inserted+dup+rejected check deleted"),
 ("B2", Bd, 'if any(row[i] is None for i in nn):', 'if all(row[i] is None for i in nn):', 1, "NOT NULL reject any->all (Fable B2)"),
 ("B3", Bd, 'if res != [("ok",)]:', 'if False:', 1, "quick_check result ignored (Fable B3)"),
 ("B4", Bd, 'broker = r["broker"] if r["broker"] is not None and str(r["broker"]).strip() else UNKNOWN', 'broker = r["broker"] if r["broker"] is not None and str(r["broker"]).strip() else "kite"', 1, "NULL bars broker -> 'kite' (Fable M4)"),
 ("B5", Bd, 'r["vol"],\n            UNKNOWN, UNKNOWN, label, UNKNOWN, run_ts)', 'r["vol"],\n            "kite", UNKNOWN, label, UNKNOWN, run_ts)', 1, "nifty_1m rows stamped with a broker that supplied nothing"),
 ("B6", Bd, 'return "CASE lower(trim(%s)) %s ELSE %d END, %s" % (col, whens, len(SRC_ORDER), col)', 'return col', 1, "SRC_ORDER ranking removed (scan order decides)"),
 ("B7", Bd, 'if _stat(info["path"]) != (info["bytes"], info["mtime_ns"]):', 'if False:', 1, "post-read stat guard dropped (Fable M3)"),
 ("B8", Bd, '        if head not in VENDORS:\n            return UNKNOWN', '        if head not in VENDORS:\n            continue', 1, "unrecognised feed name guessed as a vendor"),
 ("B9", Bd, 'if _complete_and_matches(out_path, plan):', 'if False:', 1, "no-op rerun skipped"),
 ("B10", Bd, 'if h.hexdigest() != dsha:', 'if False:', 1, "content sha256 read-back check skipped"),
 ("B11", Bd, '    _fsync_file(tmp)\n', '    pass\n', 1, "final fsync of the scratch file removed"),
 ("B12", Bd, '_fsync_dir(out_path)', 'pass', 0, "every directory fsync removed (0 = all occurrences)"),
 ("B13", Bd, 'c = sqlite3.connect(tmp, timeout=30)', 'c = sqlite3.connect("file:%s?mode=ro" % tmp, uri=True, timeout=30)', 1, "resume probe opened read-only again (round-1 bug)"),
 ("B14", Bd, 'for suffix in ("-journal", "-wal", "-shm", ""):', 'for suffix in ("",):', 1, "scratch sidecars no longer removed"),
 ("B15", Bd, 'if kept is not None and kept[0] != row[sidx]:', 'if False:', 1, "supplier conflicts no longer recorded"),
 ("B16", Bd, 'fcntl.flock(dfd, fcntl.LOCK_EX | fcntl.LOCK_NB)', 'pass', 1, "build lock removed (Fable defect 5)"),
]
only = sys.argv[1:]
res = []
for mid, rel, old, new, cnt, desc in M:
    if only and mid not in only: continue
    d = tempfile.mkdtemp(prefix="mut_")
    for c in COPY:
        shutil.copytree(os.path.join(REPO, c), os.path.join(d, c), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    p = os.path.join(d, rel)
    s = open(p, encoding="utf-8").read()
    n = s.count(old)
    if (cnt and n != cnt) or n == 0:
        res.append((mid, desc, "BAD-PATCH (found %d)" % n, "")); shutil.rmtree(d, True); continue
    open(p, "w", encoding="utf-8").write(s.replace(old, new))
    t0 = time.time()
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"] + TESTS, cwd=d, capture_output=True, text=True, timeout=600)
    out = r.stdout + r.stderr
    failed = re.findall(r"^FAILED (\S+)", out, re.M) or re.findall(r"^ERROR (\S+)", out, re.M)
    if r.returncode == 0:
        res.append((mid, desc, "SURVIVED", re.findall(r"\d+ passed", out)[-1:] and re.findall(r"\d+ passed", out)[-1]))
    else:
        res.append((mid, desc, "CAUGHT", failed[0] if failed else out.strip().splitlines()[-1]))
    shutil.rmtree(d, True)
    print(mid, res[-1][2], res[-1][3], "%.0fs" % (time.time() - t0), flush=True)
import json
json.dump(res, open(os.environ.get("MUT_OUT", os.path.join(tempfile.gettempdir(), "mut_result.json")), "w"), indent=1)
