#!/usr/bin/env python3
"""Mutation runner behind MUTATION_LOG.txt. Each mutation patches ONE exact string in a throwaway copy of tools/tests/pullers-shared/docs-framework/config, runs the guard and builder test files, and records CAUGHT (first failing test) or SURVIVED. Run: python3 docs/audit_pack_041126/mutation_runner.py [ID ...]   (the repo itself is never modified)."""
import os, re, shutil, subprocess, sys, tempfile, time
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COPY = ["tools", "tests", "pullers/shared", "docs/framework", "config"]
G, Bd = "tools/requirements_guard.py", "tools/retailer_db_build.py"
TESTS = ["tests/test_requirements_guard.py", "tests/test_retailer_db_build.py"]
M = [
 # id, file, old, new, count, description
 ("G1", G, 'if not os.path.isfile(full):', 'if False:', 1, "delete the evidence-file-exists branch (Fable G1)"),
 ("G2", G, 'PROBLEM_STATUS = ("DONE", "COMPLETE", "COMPLETED", "GREEN", "PROVEN", "APPROVED")', 'PROBLEM_STATUS = ("DONE", "COMPLETE")', 1, "shrink PROBLEM_STATUS to DONE/COMPLETE (Fable G2)"),
 ("G3", G, 'return 1 if rep["counts"][ALERT] else 0', 'return 0', 1, "main() always exits 0 (Fable G3)"),
 ("G4", G, 'if rec != _sha_bytes(data):', 'if False:', 1, "evidence sha256 never recomputed"),
 ("G5", G, 'if not any(m.group(1).lower() == k and _norm_build(m.group(2)) == want for m in APPROVAL_LINE.finditer(body)):', 'if False:', 1, "evidence need not carry 'APPROVAL <flag> APPROVES <this build>'"),
 ("G6", G, 'if not any(rel.startswith(d) for d in EVIDENCE_DIRS):', 'if False:', 1, "evidence may live anywhere (e.g. CLAUDE.md)"),
 ("G7", G, 'EVIDENCE_DIRS = ("docs/approvals_evidence/",)', 'EVIDENCE_DIRS = ("docs/",)', 1, "evidence folder widened to docs/ (Fable round-3 GN3)"),
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
 ("B7", Bd, '_stat(info["path"]) != (info["bytes"], info["mtime_ns"]) or ', '', 1, "post-read stat guard dropped, full re-hash remains (Fable M3; EXPECTED EQUIVALENT since round 4: the content hash subsumes size+mtime)"),
 ("B7b", Bd, ' or file_sha256(info["path"]) != info["sha256"]:', ':', 1, "post-read FULL re-hash dropped, size+mtime remain (round-4 defect 7: utime() hides a same-size change)"),
 ("B8", Bd, '        if head not in VENDORS:\n            return UNKNOWN', '        if head not in VENDORS:\n            continue', 1, "unrecognised feed name guessed as a vendor"),
 ("B9", Bd, 'if _complete_and_matches(out_path, plan):', 'if False:', 1, "no-op rerun skipped"),
 ("B10", Bd, 'if h.hexdigest() != dsha:', 'if False:', 1, "content sha256 read-back check skipped"),
 ("B11", Bd, '    _fsync_file(tmp)\n', '    pass\n', 1, "final fsync of the scratch file removed"),
 ("B12", Bd, '_fsync_dir(out_path)', 'pass', 0, "every directory fsync removed (0 = all occurrences)"),
 ("B13", Bd, 'c = sqlite3.connect(tmp, timeout=30)', 'c = sqlite3.connect("file:%s?mode=ro" % tmp, uri=True, timeout=30)', 1, "resume probe opened read-only again (round-1 bug)"),
 ("B14", Bd, 'for suffix in ("-journal", "-wal", "-shm", ""):', 'for suffix in ("",):', 1, "scratch sidecars no longer removed"),
 ("B15", Bd, 'if kept is not None and kept[0] != row[sidx]:', 'if False:', 1, "supplier conflicts no longer recorded"),
 ("B16", Bd, 'fcntl.flock(dfd, fcntl.LOCK_EX | fcntl.LOCK_NB)', 'pass', 1, "build lock removed (Fable defect 5)"),
 ("G17", G, 'link = _path_symlink(ctx["root"], rel)', 'link = None', 1, "symlinks inside the evidence path accepted (Fable round-3 trick B)"),
 ("G18", G, 'if os.path.realpath(full) != os.path.join(os.path.realpath(ctx["root"]), *rel.split("/")):', 'if False:', 1, "realpath-equals-stated-path check removed (Fable round-3 GN1; expected EQUIVALENT, the symlink walk fires first)"),
 ("G19", G, '        if len(ps) > 1:\n', '        if False:\n', 1, "duplicate ledger rows not refused (Fable round-3 trick F4)"),
 ("G20", G, 'return os.path.normpath(str(path).strip().replace("\\\\", "/")).replace(os.sep, "/").casefold()', 'return str(path)', 1, "ledger build paths not normalised (aliases and case differ)"),
 ("G21", G, 'elif state_anchor.get("length") != cur["length"] or state_anchor.get("head") != cur["head"]:', 'elif False:', 1, "state-file anchor not checked (tail deletion)"),
 ("G22", G, 'if len(entries) < n or (n and entries[n - 1]["hash"] != last["head"]):', 'if False:', 1, "guard_report anchor_history not checked"),
 ("G23", G, 'if len(head_entries) > len(entries) or any(h.get("hash") != e.get("hash") for h, e in zip(head_entries, entries)):', 'if False:', 1, "git HEAD copy of the chain not compared"),
 ("G24", G, 'if REJECT_LINE.search(text):', 'if False:', 1, "'not approved' / 'rejected' / FAIL verdict lines accepted (Fable round-3 trick G)"),
 ("G25", G, 'if len(new_true) > 1:', 'if False:', 1, "several flags may flip in one --accept-state (Fable round-3 trick A)"),
 ("G26", G, 'if raw is None:\n            return False, ("refused: evidence %s for %s/%s is not committed', 'if False:\n            return False, ("refused: evidence %s for %s/%s is not committed', 1, "evidence need not be committed in git HEAD before the flip"),
 ("G27", G, 'if probe is None:', 'if False:', 1, "true flags accepted when git history is unreadable"),
 ("G28", G, '"guard_report.json", "readme.md", "readme.txt", "readme")', '"guard_report.json")', 1, "a README may be evidence (Fable round-3 trick A)"),
 ("G29", G, 'if len(prose) < MIN_EVIDENCE_WORDS:', 'if False:', 1, "evidence with the APPROVAL line and no prose accepted"),
 ("G30", G, 'if rel != raw:', 'if False:', 1, "non-canonical evidence path spellings accepted"),
 ("G31", G, 'hist.append({"length": cur["length"], "head": cur["head"], "ist": now.strftime("%d-%m-%Y %H:%M:%S")})', 'pass', 1, "anchor_history never written to guard_report.json"),
 ("G32", G, '"anchor": _anchor_of(entries), "entries": entries}', '"entries": entries}', 1, "anchor never written to the state file"),
 ("BN1", Bd, 'if os.path.abspath(path) == out_path or os.path.abspath(path) == out_path + ".building":', 'if False:', 1, "output file may be its own source (Fable round-3 BN1)"),
 ("BN1b", Bd, ' or os.path.abspath(path) == out_path + ".building":', ':', 1, "scratch .building file may be a source"),
 ("BN3", Bd, 'if not sources or len(set(labels)) != len(labels):', 'if not sources:', 1, "duplicate source labels accepted (Fable round-3 BN3)"),
 ("BN3b", Bd, 'if not sources or len(set(labels)) != len(labels):', 'if len(set(labels)) != len(labels):', 1, "empty source list accepted"),

 # ---- round 4 (04-11-2026): Fable round-4 mutants GN5/GN6/GN7/BN5/BN7 and one mutation per new rule
 ("GN5", G, 'if len(new_true) > 1:', 'if len(new_true) > 2:', 1, "two flags may flip in one --accept-state (Fable round-4 GN5)"),
 ("GN6", G, 'if len(entries) < n or (n and entries[n - 1]["hash"] != last["head"]):', 'if len(entries) < n:', 1, "report anchor compared by length only (Fable round-4 GN6)"),
 ("GN7", G, 'if len(head_entries) > len(entries) or any(h.get("hash") != e.get("hash") for h, e in zip(head_entries, entries)):', 'if len(head_entries) > len(entries):', 1, "git HEAD chain compared by length only (Fable round-4 GN7)"),
 ("G33", G, 'body = _strip_fences(text)', 'body = text', 1, "APPROVAL line inside a code fence counts (round-4 defect 2)"),
 ("G34", G, 'if NONFINAL_LINE.search(text):', 'if False:', 1, "withdrawn / draft / template / not-final lines accepted (round-4 defect 2)"),
 ("G35", G, '.replace("\\r\\n", "\\n").replace("\\r", "\\n")', '', 1, "CRLF not folded: Windows responses refused with a misleading reason (round-4 defect 3)"),
 ("G36", G, 'if _sha_bytes(raw) != rec_sha:', 'if False:', 1, "evidence text at git HEAD need not equal the approved text (round-4 defect 1, trick T3)"),
 ("G37", G, 'if he is not None and len(entries) > len(he):', 'if False:', 1, "previous accepted entry may be uncommitted at the next accept (round-4 defect 1, trick T2)"),
 ("G39", G, 'if len(entries) > len(he) + 1:', 'if False:', 1, "report does not ALERT on several uncommitted accepted entries (round-4 defect 1)"),
 ("G40", G, 'if len(new_vs_head) > 1:', 'if False:', 1, "report does not ALERT on several flags newly true against HEAD (round-4 defect 1)"),
 ("G41", G, 'if len(oe) > len(entries) or any(h.get("hash") != e.get("hash") for h, e in zip(oe, entries)):', 'if False:', 1, "chain need not extend earlier COMMITTED versions of the state file (round-4 defect 4, trick T8)"),
 ("G42", G, 'if _git_show(ctx, REPORT) is not None and not os.path.isfile(os.path.join(ctx["root"], REPORT)):', 'if False:', 1, "a committed guard_report.json may vanish unnoticed (round-4 defect 4)"),
 ("G43", G, 'prose = APPROVAL_LINE.sub(" ", body).split()', 'prose = APPROVAL_LINE.sub(" ", text).split()', 1, "prose inside a code fence counts toward the 20-word minimum"),
 ("BN5", Bd, 'return "CASE lower(trim(%s)) %s ELSE %d END, %s" % (col, whens, len(SRC_ORDER), col)', 'return "CASE trim(%s) %s ELSE %d END, %s" % (col, whens, len(SRC_ORDER), col)', 1, "SQL SRC_ORDER rank is case-sensitive (Fable round-4 BN5)"),
 ("BN5b", Bd, 't = str(src).strip().lower() if src is not None else ""', 't = str(src).strip() if src is not None else ""', 1, "Python src_rank is case-sensitive, disagrees with SQL"),
 ("BN7", Bd, 'for chunk in iter(lambda: f.read(8 << 20), b""):\n            h.update(chunk)\n    return h.hexdigest()', 'for chunk in [f.read(8 << 20)]:\n            h.update(chunk)\n    return h.hexdigest()', 1, "source sha256 covers only the first 8 MB (Fable round-4 BN7)"),
 ("B17", Bd, 'if m0 == m1 and w0 == w1 and mn == m1[0] and (w1 is None or wn == w1[0]):', 'if True:', 1, "snapshot accepted even if the source moved while it was copied"),
 ("B18", Bd, 'if len(hdr) >= 20 and (hdr[18] == 2 or hdr[19] == 2):\n        return True', 'if False:\n        return True', 1, "WAL header not recognised (only a non-empty -wal triggers the snapshot path)"),
 ("B18b", Bd, 'return os.path.getsize(path + "-wal") > 0', 'return False', 1, "a non-empty -wal beside a non-WAL header ignored"),
 ("B19", Bd, 'return hashlib.sha256(("main:%s|wal:%s" % (main_sha, wal_sha or "-")).encode()).hexdigest()', 'return main_sha', 1, "source_sha256 / plan ignore the -wal (round-4 defect 5: false UP_TO_DATE)"),
 ("B20", Bd, '            try:                                  # a failed COMMIT (disk full) already ended the transaction: never mask it\n                if out.in_transaction:\n                    out.execute("ROLLBACK")\n            except sqlite3.Error:\n                pass\n', '            out.execute("ROLLBACK")\n', 1, "ROLLBACK after a failed COMMIT masks the disk-full error (round-4 defect 6)"),
 ("B21", Bd, 'os.link(out_path, moved)          # the final path keeps existing the whole time', 'raise OSError("no link")', 1, "old output moved aside by rename: final path empty for an instant (round-4 defect 8)"),
 ("B22", Bd, 'return st if st in ("BUILDING", "COMPLETE") else None', 'return st if st == "BUILDING" else None', 1, "a COMPLETE scratch file is discarded instead of published (round-4 defect 8)"),
 ("B23", Bd, 'if info["snapshot"]:\n            continue', 'if False:\n            continue', 1, "snapshot sources re-checked against the live source (would flag a normal build as moved)"),
 ("B24", Bd, '            shutil.rmtree(snapdir, ignore_errors=True)', '            pass', 1, "private snapshot directory not removed on exit"),
 ("B25", Bd, 'shutil.rmtree(os.path.join(d, n), ignore_errors=True)', 'pass', 1, "stale snapshot directory of a killed run not removed"),
 ("B26", Bd, 'while os.path.exists(cand):', 'while False:', 1, "two replaces in one second overwrite the kept old output"),
 ("B27", Bd, 'if _is_wal(path):\n                need', 'if False:\n                need', 1, "WAL sources opened directly through SQLite again (round-4 defect 5)"),
 ("B28", Bd, 'if shutil.disk_usage(snapdir).free < need + (64 << 20):', 'if False:', 1, "no free-space check before the private snapshot"),
 ("B29", Bd, 'state = _tmp_state(tmp, plan) if os.path.exists(tmp) else None', 'state = None', 1, "scratch file never reused (no resume, no publish-from-scratch)"),
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
