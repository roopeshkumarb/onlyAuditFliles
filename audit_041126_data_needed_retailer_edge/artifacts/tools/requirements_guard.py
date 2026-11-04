#!/usr/bin/env python3
"""requirements_guard.py - mechanical check that our work still satisfies Kumar's 31 requirements.

Kumar 04-11-2026: "make mechanical check agent which checks and alerts and fixes whenever we
divert from the tasks; whatever you do must satisfy them directly or indirectly".

READ-ONLY by default. It reads docs/framework/REQUIREMENTS_REGISTER.json (R01..R31, S1..S5) and
docs/framework/APPROVALS_LEDGER.json, runs the rules each requirement maps to, and writes
docs/framework/guard_report.json (atomic, via guard_core). It never touches a box, never deletes,
never restarts, never stops a container. --fix only regenerates derived docs through their own
generator (CSV_TOTALS) and re-checks. --notify (off by default) sends the one-line summary through
guard_core.notify, the prebuilt alert path.

Reuses: guard_core._atomic_write / notify / NEVER_TOUCH / DOCKER_DANGEROUS (pullers/shared),
dp_recoverability.classify (the placement classifier) and the dp_families join, and the scan idea
of tools/check_recoverability_placement.py.

APPROVALS GATE (hardened 04-11-2026 after Fable rounds 2 and 3). A flag may be true only if its
<flag>_evidence is a regular file (no symlink anywhere in its path, no ./ or // aliases) under
docs/approvals_evidence/ (the ONLY allowed folder; never the pack, never framework docs, never a README),
whose text contains the line "APPROVAL <flag> APPROVES <build path>" for exactly that flag and build,
contains no "not approved" / "rejected" / FAIL verdict line, has enough prose to be a response, and whose
sha256 is recorded in <flag>_evidence_sha256 and recomputes. Ledger build paths are normalised (strip,
normpath, casefold) and a duplicate row for the same build is an ALERT. Accepted approvals are kept in an
append-only hash chain (docs/framework/APPROVALS_STATE.json, appended only by --accept-state). The chain
head is anchored in three places (the state file's own "anchor", the anchor_history carried in
guard_report.json, and git HEAD's copy of the state file when git works), so deleting the tail of the chain
ALERTs. --accept-state accepts at most ONE newly-true flag per call relative to the last accepted entry, only
when that flag's evidence file is already committed in git HEAD, and refuses to accept any true flag when git
history cannot be read. A removed build row, a chain break, edited evidence, or a true flag outside the
accepted chain all ALERT, and such a build is never "allowed to be called DONE".
HONEST LIMIT: this is an accident-and-sloppiness check, not a security control. One person with write
access to this repo can still write an evidence file containing the APPROVAL line, commit it, flip one flag,
run --accept-state, commit, and repeat for the other two flags: the guard cannot tell who wrote the file or
whether Fable / the auditor / Kumar really said it. What it does force is that this is done in separate,
visible commits, one flag at a time, with the response document committed first. The real gate is Kumar plus
the external auditor reading the evidence themselves.

Exit: 0 no ALERT, 1 at least one ALERT, 2 the guard itself could not run.
Status per requirement: GREEN only if every mapped machine rule is OK; RED on any ALERT; AMBER when
it is only INFO / traceability / a rule that could not run here. A TRACE-only requirement is never GREEN.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "pullers", "shared"))

IST = timezone(timedelta(hours=5, minutes=30))
OK, INFO, ALERT = "OK", "INFO", "ALERT"
REGISTER = "docs/framework/REQUIREMENTS_REGISTER.json"
LEDGER = "docs/framework/APPROVALS_LEDGER.json"
REPORT = "docs/framework/guard_report.json"
TASKS = "docs/tasks/TASKS.jsonl"
CSV_PATH = "docs/framework/data_needed_instruments_041126.csv"
MD_PATH = "docs/framework/DATA_NEEDED_INSTRUMENTS_041126.md"
GEN_CMD = "tools/gen_data_needed_instruments_041126.py"
STOP_VERBS = ("stop", "kill", "rm", "remove", "restart", "pause", "down")  # guard-allow
# lines carrying this marker are exempt from NO_OLD_STOP so the guard's own constant lists do not trip it
EXEMPT = "guard-allow"
PROBLEM_STATUS = ("DONE", "COMPLETE", "COMPLETED", "GREEN", "PROVEN", "APPROVED")
STATE = "docs/framework/APPROVALS_STATE.json"
FLAGS = ("fable", "external_auditor", "kumar")
EVIDENCE_DIRS = ("docs/approvals_evidence/",)
EVIDENCE_EXCLUDED_DIRS = ("docs/audit_pack_041126/artifacts/",)  # copies of code and CLAUDE.md, never evidence
EVIDENCE_FORBIDDEN_NAMES = ("claude.md", "approvals_ledger.json", "approvals_state.json",
                            "requirements_register.json", "guard_report.json", "readme.md", "readme.txt", "readme")
EVIDENCE_CODE_SUFFIXES = (".py", ".sh", ".js", ".bat", ".cmd", ".ps1", ".yml", ".yaml")
MIN_EVIDENCE_BYTES = 40
MIN_EVIDENCE_WORDS = 20   # prose words besides the APPROVAL line
APPROVAL_LINE = re.compile(r"^[ \t]*APPROVAL[ \t]+(fable|external_auditor|kumar)[ \t]+APPROVES[ \t]+(\S+)[ \t]*$",
                           re.I | re.M)
REJECT_LINE = re.compile(r"^.*\b(?:not[ \t_-]+approved|rejected)\b.*$|^\W*(?:verdict|status|decision|result)\W*fail\w*\b.*$|^\W*fail(?:ed)?\W*$",
                         re.I | re.M)


def F(rule, level, msg, req=None, fix=None, evidence=None):
    return {"rule": rule, "level": level, "msg": msg, "req": req or [], "fix": fix, "evidence": evidence}


def _load(ctx, rel):
    with open(os.path.join(ctx["root"], rel), encoding="utf-8") as fh:
        return json.load(fh)


def _csv_rows(ctx):
    p = os.path.join(ctx["root"], CSV_PATH)
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ---------------------------------------------------------------- recoverability join (copied from the
# scratchpad join script, parameterised so tests can feed synthetic configs)

def _recoverability(ctx):
    import dp_recoverability as rec
    if ctx.get("rec_cfg") is not None:
        return rec, ctx["rec_cfg"]
    return rec, rec.load(os.path.join(ctx["root"], "config", "recoverability.json"))


def _families(ctx):
    if ctx.get("families") is not None:
        return ctx["families"]
    import dp_families
    return dp_families.FAMILIES


def join(ctx):
    rec, cfg = _recoverability(ctx)
    rows = []
    for fam, spec in _families(ctx).items():
        for table in spec["tables"]:
            short = table.split(".")[-1]
            klass, rule, unknown = rec.effective(short, cfg)
            rows.append({"family": fam, "table": table, "short": short, "class": klass,
                         "rule": rule, "unknown": unknown, "kind": spec.get("kind"),
                         "sources": spec.get("sources", [])})
    return rec, cfg, rows


# ---------------------------------------------------------------- rules

def r_join_unknown(ctx):
    _rec, _cfg, rows = join(ctx)
    unk = [r["table"] for r in rows if r["unknown"]]
    if unk:
        return [F("JOIN_UNKNOWN", ALERT, "%d declared store tables match no recoverability rule (treated NON_RECOVERABLE "
                  "by fail-safe, but unproven): %s" % (len(unk), ", ".join(sorted(unk)[:12])))]
    return [F("JOIN_UNKNOWN", OK, "all %d declared store tables classified, 0 UNKNOWN" % len(rows))]


def r_join_live_safe(ctx):
    rec, cfg, rows = join(ctx)
    reg = ctx["register"]
    out, bad = [], []
    markers = [m.lower() for m in reg.get("live_only_markers", [])]
    for r in rows:
        looks_live = r["kind"] in ("option_chain", "quote") or any(m in r["short"].lower() for m in markers)
        if looks_live and r["class"] == rec.REC:
            bad.append(r["table"])
    for name in reg.get("window_limited_must_be_non_recoverable", []):
        if rec.effective(name, cfg)[0] == rec.REC:
            bad.append(name + " (window-limited)")
    if bad:
        out.append(F("JOIN_LIVE_SAFE", ALERT, "live-only or window-limited data classed RECOVERABLE, so it would be "
                     "allowed onto SSD: %s" % ", ".join(bad)))
    else:
        out.append(F("JOIN_LIVE_SAFE", OK, "no live-only / window-limited table is classed RECOVERABLE (%d tables checked)" % len(rows)))
    return out


def r_csv_totals(ctx):
    try:
        rows = _csv_rows(ctx)
    except OSError as e:
        return [F("CSV_TOTALS", ALERT, "instrument CSV unreadable: %s" % e)]
    cnt = {}
    for r in rows:
        cnt[r.get("class", "")] = cnt.get(r.get("class", ""), 0) + 1
    try:
        md = open(os.path.join(ctx["root"], MD_PATH), encoding="utf-8").read()
    except OSError as e:
        return [F("CSV_TOTALS", ALERT, "instrument MD unreadable: %s" % e)]
    classes = ("LIVE_ONLY_NON_RECOVERABLE", "PULLABLE_RECOVERABLE", "UNKNOWN")  # other 2-column tables (groups, brokers) share this layout
    stated = {m.group(1): int(m.group(2)) for m in re.finditer(r"^\|\s*([A-Z_]+)\s*\|\s*(\d+)\s*\|\s*$", md, re.M)
              if m.group(1) in classes}
    mism = []
    for k in sorted(set(cnt) | set(stated)):
        if stated.get(k, 0) != cnt.get(k, 0):
            mism.append("%s csv=%d md=%s" % (k, cnt.get(k, 0), stated.get(k)))
    m_all = re.search(r"\*\*all\*\*\s*\|\s*\*\*(\d+)\*\*", md)
    if m_all and int(m_all.group(1)) != len(rows):
        mism.append("all csv=%d md=%s" % (len(rows), m_all.group(1)))
    if mism:
        return [F("CSV_TOTALS", ALERT, "totals in the MD do not recompute from the CSV: " + "; ".join(mism), fix="regen_instruments")]
    return [F("CSV_TOTALS", OK, "MD class totals recompute from the CSV (%d rows)" % len(rows))]


def r_instr_detail(ctx):
    reg, out = ctx["register"], []
    try:
        rows = _csv_rows(ctx)
    except OSError as e:
        return [F("INSTR_DETAIL", ALERT, "per-instrument CSV missing: %s" % e)]
    if not rows:
        return [F("INSTR_DETAIL", ALERT, "per-instrument CSV has no rows")]
    cols = set(rows[0].keys())
    miss = [c for c in reg.get("required_csv_columns", []) if c not in cols]
    if miss:
        out.append(F("INSTR_DETAIL", ALERT, "CSV lacks required columns: %s" % ", ".join(miss)))
    allowed = {"LIVE_ONLY_NON_RECOVERABLE", "PULLABLE_RECOVERABLE", "UNKNOWN"}
    badc = [r.get("instrument_name") for r in rows if r.get("class") not in allowed]
    if badc:
        out.append(F("INSTR_DETAIL", ALERT, "%d rows have a class outside %s" % (len(badc), sorted(allowed))))
    noname = sum(1 for r in rows if not (r.get("instrument_name") or "").strip())
    if noname:
        out.append(F("INSTR_DETAIL", ALERT, "%d rows have no instrument name" % noname))
    nofeed = [r.get("instrument_name") for r in rows if r.get("class") == "LIVE_ONLY_NON_RECOVERABLE" and not (r.get("feeds_by_brokers") or "").strip()]
    if nofeed:
        out.append(F("INSTR_DETAIL", ALERT, "%d live-only rows name no feeding broker (e.g. %s)" % (len(nofeed), nofeed[0])))
    why_empty = sum(1 for r in rows if not (r.get("why_needed_for_regime") or "").strip())
    if why_empty > 0.10 * len(rows):
        out.append(F("INSTR_DETAIL", ALERT, "why_needed_for_regime is empty on %d of %d rows (>10%%)" % (why_empty, len(rows))))
    marker = sum(1 for r in rows if "MARKER-NOT-FOUND" in (r.get("evidence") or "") or "MARKER-NOT-FOUND" in (r.get("count_by_code") or ""))
    if marker:
        out.append(F("INSTR_DETAIL", ALERT, "%d rows cite MARKER-NOT-FOUND instead of a real file:line" % marker))
    unk = sum(1 for r in rows if r.get("class") == "UNKNOWN")
    if unk:
        out.append(F("INSTR_DETAIL", INFO, "%d rows class UNKNOWN (H21: UNKNOWN is never 0; each needs its resolving query)" % unk))
    if not out:
        out.append(F("INSTR_DETAIL", OK, "%d instrument rows, columns present, every live-only row names a broker, 0 UNKNOWN" % len(rows)))
    elif all(f["level"] == INFO for f in out):
        out.insert(0, F("INSTR_DETAIL", OK, "%d instrument rows, structure complete" % len(rows)))
    return out


def r_weekly_present(ctx):
    try:
        rows = _csv_rows(ctx)
    except OSError:
        return [F("WEEKLY_PRESENT", ALERT, "per-instrument CSV missing, cannot confirm weekly-expiry instruments")]
    n = sum(1 for r in rows if any("weekly" in (v or "").lower() for v in r.values()))
    if n == 0:
        return [F("WEEKLY_PRESENT", ALERT, "no weekly-expiry instrument appears in the data-needed list (Kumar asked for it)")]
    return [F("WEEKLY_PRESENT", OK, "%d rows mention weekly expiry" % n)]


def _scan_files(root):
    for d, _dirs, files in os.walk(root):
        if "/_state" in d or "/_auth" in d or "/@eaDir" in d:
            continue
        for fn in files:
            yield os.path.join(d, fn)


def r_ssd_nonrec(ctx):
    roots = ctx.get("ssd_roots") or []
    if not roots:
        return [F("SSD_NONREC", INFO, "NOT RUN: no --ssd-root given; the sandbox cannot see box disks. Run on each box (read-only)")]
    rec, cfg = _recoverability(ctx)
    out, n = [], 0
    for root in roots:
        if not os.path.isdir(root):
            out.append(F("SSD_NONREC", ALERT, "SSD root not readable: %s" % root))
            continue
        for p in _scan_files(root):
            n += 1
            klass, rule, unknown = rec.effective(p, cfg)
            if klass == rec.NON:
                out.append(F("SSD_NONREC", ALERT, "NON_RECOVERABLE%s file on SSD (%s): %s" % (" [unknown name]" if unknown else "", rule or "unclassified", p)))
    return out or [F("SSD_NONREC", OK, "%d files under %d SSD root(s), none NON_RECOVERABLE" % (n, len(roots)))]


def r_policy_file(ctx):
    out = []
    p = os.path.join(ctx["root"], "docs", "framework", "data_lifecycle_policy.json")
    try:
        pol = json.load(open(p, encoding="utf-8"))
        hs = pol.get("hot_ssd", {})
        if hs.get("min_free_gb") != 40 or hs.get("min_free_percent") != 40:
            out.append(F("POLICY_FILE", ALERT, "policy min_free is not 40 GB / 40%%: %s" % {k: hs.get(k) for k in ("min_free_gb", "min_free_percent")}))
        else:
            out.append(F("POLICY_FILE", OK, "repo policy present, min_free 40 GB / 40%"))
    except (OSError, ValueError) as e:
        out.append(F("POLICY_FILE", ALERT, "policy file missing/unreadable in repo: %s" % e))
    boxes = ctx.get("policy_paths") or []
    if not boxes:
        out.append(F("POLICY_FILE", INFO, "box copies NOT checked (no --policy-path). dp_spacegate fails open without it"))
    for b in boxes:
        if not os.path.isfile(b):
            out.append(F("POLICY_FILE", ALERT, "policy file absent at %s - dp_spacegate would fail open" % b))
    return out


def _ledger_paths(ctx):
    return [b["path"] for b in ctx["ledger"].get("builds", [])]


def r_no_old_stop(ctx):
    reg = ctx["register"]
    olds = [n.lower() for n in reg.get("old_puller_names", [])]
    try:
        import guard_core
        olds += [n.lower() for n in guard_core.NEVER_TOUCH]  # guard-allow
    except ImportError:
        pass
    hits, scanned = [], 0
    for rel in _ledger_paths(ctx):
        p = os.path.join(ctx["root"], rel)
        if not os.path.isfile(p) or not rel.endswith((".py", ".sh", ".yml", ".yaml")):
            continue
        scanned += 1
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            low = line.lower()
            if EXEMPT in low:
                continue
            if not ("docker" in low or "compose" in low):
                continue
            if any(re.search(r"\b%s\b" % v, low) for v in STOP_VERBS) and any(n in low for n in olds):
                hits.append("%s:%d" % (rel, i))
    if hits:
        return [F("NO_OLD_STOP", ALERT, "new code stops/removes an old puller or an untouchable container: %s" % ", ".join(hits[:10]))]
    return [F("NO_OLD_STOP", OK, "%d new files scanned, no code path stops an old puller or cloudflared/portainer/blpro_09" % scanned)]


def r_tool_tests(ctx):
    out = []
    for b in ctx["ledger"].get("builds", []):
        t = b.get("test")
        p = os.path.join(ctx["root"], t) if t else None
        if not os.path.isfile(os.path.join(ctx["root"], b["path"])):
            out.append(F("TOOL_TESTS", ALERT, "ledger lists %s but the file does not exist" % b["path"]))
        elif not p or not os.path.isfile(p):
            out.append(F("TOOL_TESTS", ALERT, "%s has no test file (%s)" % (b["path"], t)))
        else:
            body = open(p, encoding="utf-8", errors="replace").read()
            if not re.search(r"def test_|unittest|check\(", body):
                out.append(F("TOOL_TESTS", ALERT, "%s test file %s contains no test" % (b["path"], t)))
    return out or [F("TOOL_TESTS", OK, "every ledger build exists and has a non-empty test file")]


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha_bytes(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


def _snapshot(ledger):
    snap = {}
    for b in ledger.get("builds", []):
        snap[b["path"]] = {"claimed_status": str(b.get("claimed_status", "")),
                           "flags": {k: {"value": b.get(k) is True, "evidence": str(b.get(k + "_evidence") or ""),
                                         "sha256": str(b.get(k + "_evidence_sha256") or "")} for k in FLAGS}}
    return snap


def _chain_hash(prev, seq, snap):
    return _sha_bytes(("%s|%d|%s" % (prev, seq, _canon(snap))).encode("utf-8"))


def _load_state(ctx):
    """(entries, error). entries is None when the file does not exist."""
    p = os.path.join(ctx["root"], STATE)
    if not os.path.isfile(p):
        return None, None
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh).get("entries", []), None
    except (OSError, ValueError) as e:
        return None, "state file unreadable: %s" % e


def _state_anchor(ctx):
    try:
        with open(os.path.join(ctx["root"], STATE), encoding="utf-8") as fh:
            a = json.load(fh).get("anchor")
        return a if isinstance(a, dict) else None
    except (OSError, ValueError):
        return None


def _verify_chain(entries):
    prev = "GENESIS"
    for i, e in enumerate(entries, 1):
        if e.get("seq") != i or e.get("prev") != prev or e.get("hash") != _chain_hash(prev, i, e.get("builds", {})):
            return "chain broken at entry %d" % i
        prev = e["hash"]
    return None


def _norm_build(path):
    """Canonical key for a ledger build path: strip, forward slashes, normpath, casefold."""
    return os.path.normpath(str(path).strip().replace("\\", "/")).replace(os.sep, "/").casefold()


def _git_show(ctx, rel):
    """Bytes of <rel> at git HEAD, or None when git / HEAD / the file is unavailable. ctx['git_show'] lets
    tests inject a fake history; it must return bytes or None."""
    fn = ctx.get("git_show")
    if fn is not None:
        return fn(rel)
    try:
        r = subprocess.run(["git", "-C", ctx["root"], "show", "HEAD:" + rel], capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def _path_symlink(root, rel):
    cur = root
    for part in rel.split("/"):
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            return cur
    return None


def evidence_problem(ctx, b, k):
    """None when <k>_evidence is acceptable for build b, else why not. Mechanical only: it cannot tell
    who wrote the file."""
    raw = str(b.get(k + "_evidence") or "").strip()
    if not raw:
        return "no %s_evidence" % k
    if os.path.isabs(raw) or ".." in raw.replace("\\", "/").split("/"):
        return "%s_evidence must be a relative path inside the repo: %s" % (k, raw)
    rel = os.path.normpath(raw).replace(os.sep, "/")
    if rel != raw:
        return "%s_evidence path is not in canonical form (%r vs %r)" % (k, raw, rel)
    if not any(rel.startswith(d) for d in EVIDENCE_DIRS):
        return "%s_evidence is not under %s: %s" % (k, " or ".join(EVIDENCE_DIRS), rel)
    base = os.path.basename(rel).lower()
    if base in EVIDENCE_FORBIDDEN_NAMES or base.endswith(EVIDENCE_CODE_SUFFIXES):
        return "%s_evidence is code, a README or a project control file: %s" % (k, rel)
    full = os.path.join(ctx["root"], *rel.split("/"))
    link = _path_symlink(ctx["root"], rel)
    if link:
        return "%s_evidence path passes through a symlink: %s" % (k, rel)
    if not os.path.isfile(full):
        return "%s evidence file missing: %s" % (k, rel)
    if os.path.realpath(full) != os.path.join(os.path.realpath(ctx["root"]), *rel.split("/")):
        return "%s_evidence resolves outside its stated path: %s" % (k, rel)
    data = open(full, "rb").read()
    if len(data) < MIN_EVIDENCE_BYTES:
        return "%s_evidence file is too small to be evidence (%d bytes): %s" % (k, len(data), rel)
    rec = str(b.get(k + "_evidence_sha256") or "").strip().lower()
    if not rec:
        return "%s_evidence_sha256 not recorded in the ledger" % k
    if rec != _sha_bytes(data):
        return "%s_evidence sha256 does not recompute (file changed or hash wrong): %s" % (k, rel)
    text = data.decode("utf-8", "replace")
    if REJECT_LINE.search(text):
        return "%s_evidence contains a 'not approved' / 'rejected' / FAIL verdict line: %s" % (k, rel)
    want = _norm_build(b["path"])
    lines = [m for m in APPROVAL_LINE.finditer(text)]
    if not any(m.group(1).lower() == k and _norm_build(m.group(2)) == want for m in lines):
        return "%s_evidence has no line 'APPROVAL %s APPROVES %s'" % (k, k, b["path"])
    prose = APPROVAL_LINE.sub(" ", text).split()
    if len(prose) < MIN_EVIDENCE_WORDS:
        return "%s_evidence has only %d prose words besides the APPROVAL line (need %d)" % (k, len(prose), MIN_EVIDENCE_WORDS)
    return None


# ---------------------------------------------------------------- chain anchors (tail-deletion defence)

def _anchor_of(entries):
    return {"length": len(entries), "head": entries[-1]["hash"] if entries else "GENESIS"}


def _read_anchors(ctx):
    """anchor_history carried in the previous guard_report.json (second, independent place)."""
    try:
        with open(os.path.join(ctx["root"], REPORT), encoding="utf-8") as fh:
            h = json.load(fh).get("anchor_history", [])
        return [x for x in h if isinstance(x, dict) and "length" in x and "head" in x]
    except (OSError, ValueError):
        return []


def _anchor_problems(ctx, entries, state_anchor):
    """List of problem strings; empty when the chain is exactly what was anchored."""
    out, cur = [], _anchor_of(entries)
    if state_anchor is None:
        if entries and not ctx.get("accepting"):
            out.append("state file has no anchor (length/head) - run --accept-state once to anchor it")
    elif state_anchor.get("length") != cur["length"] or state_anchor.get("head") != cur["head"]:
        out.append("chain tail removed or state anchor edited (anchor says %s entries, file has %d)"
                   % (state_anchor.get("length"), cur["length"]))
    hist = _read_anchors(ctx)
    if hist:
        last = hist[-1]
        n = int(last["length"])
        if len(entries) < n or (n and entries[n - 1]["hash"] != last["head"]):
            out.append("chain no longer contains the head recorded in guard_report anchor_history "
                       "(length %d recorded, %d now)" % (n, len(entries)))
    raw = _git_show(ctx, STATE)
    if raw is not None:
        try:
            head_entries = json.loads(raw.decode("utf-8")).get("entries", [])
        except (ValueError, UnicodeDecodeError):
            head_entries = []
        if len(head_entries) > len(entries) or any(h.get("hash") != e.get("hash") for h, e in zip(head_entries, entries)):
            out.append("chain differs from git HEAD's copy (shortened or rewritten; HEAD has %d entries, file %d)"
                       % (len(head_entries), len(entries)))
    return out


def r_approvals(ctx):
    out = []

    def add(level, msg, build):
        f = F("APPROVALS", level, msg)
        f["build"] = build
        out.append(f)
        return f

    ledger = ctx["ledger"]
    entries, err = _load_state(ctx)
    state_snap, chain_ok = {}, True
    if err:
        add(ALERT, err, "*")
        chain_ok = False
    elif entries is None:
        any_true = any(b.get(k) is True for b in ledger.get("builds", []) for k in FLAGS)
        if any_true and not ctx.get("accepting"):
            add(ALERT, "ledger has an approval flag true but there is no accepted state chain (%s)" % STATE, "*")
            chain_ok = False
        else:
            add(INFO, "no accepted state baseline yet - run --accept-state to start the chain", "*")
    else:
        bad = _verify_chain(entries)
        if bad:
            add(ALERT, "approvals state %s - treat every approval as unproven" % bad, "*")
            chain_ok = False
        elif entries:
            state_snap = entries[-1].get("builds", {})
    seen = {}
    for b in ledger.get("builds", []):
        seen.setdefault(_norm_build(b["path"]), []).append(b["path"])
    for n, ps in seen.items():
        if len(ps) > 1:
            add(ALERT, "duplicate ledger rows for the same build %s: %s" % (n, ps), "*")
    if entries is not None and chain_ok:
        probs = _anchor_problems(ctx, entries, _state_anchor(ctx))
        for pr in probs:
            add(ALERT, pr, "*")
            chain_ok = False
        if not probs:
            ctx["_anchor_current"] = _anchor_of(entries)
    paths = [b["path"] for b in ledger.get("builds", [])]
    if entries:
        for sp in state_snap:
            if sp not in paths:
                add(ALERT, "build row removed from the ledger since the last accepted state: %s" % sp, "*")
    for b in ledger.get("builds", []):
        path = b["path"]
        flags = {k: b.get(k) for k in FLAGS}
        prev = state_snap.get(path)
        if entries is not None and chain_ok and prev is None:
            add(INFO, "%s is a new ledger row not yet in the accepted state" % path, path)
        valid = {}
        for k, v in flags.items():
            if v is not True:
                if prev and prev["flags"][k]["value"]:
                    add(INFO, "%s: %s was approved in the accepted state and is now revoked (--accept-state to record)" % (path, k), path)
                continue
            why = evidence_problem(ctx, b, k)
            if why:
                add(ALERT, "%s: %s=true but %s" % (path, k, why), path)
                continue
            cur = (b.get(k + "_evidence"), str(b.get(k + "_evidence_sha256")).lower())
            old = prev["flags"][k] if prev else None
            if old and old["value"]:
                if (old["evidence"], old["sha256"].lower()) != cur:
                    add(ALERT, "%s: %s evidence changed after it was accepted - re-approval needed" % (path, k), path)
                    continue
                valid[k] = True
            elif ctx.get("accepting"):
                valid[k] = True
            else:
                add(INFO, "%s: %s approval has valid evidence but is not yet in the accepted state (--accept-state)" % (path, k), path)
        allflags = all(v is True for v in flags.values())
        claimed = str(b.get("claimed_status", "")).upper()
        fully = allflags and chain_ok and all(valid.get(k) for k in FLAGS)
        if claimed in PROBLEM_STATUS and not fully:
            miss = [k for k in FLAGS if not valid.get(k)]
            add(ALERT, "%s claims %s but lacks accepted approval: %s" % (path, claimed, ", ".join(miss)), path)
        elif not fully:
            miss = [k for k in FLAGS if not valid.get(k)]
            add(INFO, "%s is %s - awaiting: %s (may NOT be called DONE)" % (path, claimed or "unstated", ", ".join(miss)), path)
        else:
            f = add(OK, "%s fully approved with accepted, recomputing evidence" % path, path)
            f["approved"] = True
    if not out:
        add(OK, "no builds in the ledger", "*")
    return out


def accept_state(ctx):
    """Append the current ledger to the hash chain. Refuses while any approvals ALERT stands."""
    ctx = dict(ctx, accepting=True)
    ctx["ledger"] = ctx.get("ledger") if ctx.get("ledger") is not None else _load(ctx, LEDGER)
    bad = [f for f in r_approvals(ctx) if f["level"] == ALERT]
    if bad:
        return False, "refused, approvals ALERT stands: " + "; ".join(f["msg"] for f in bad)
    entries, err = _load_state(ctx)
    if err:
        return False, err
    entries = entries or []
    prev = entries[-1]["hash"] if entries else "GENESIS"
    seq = len(entries) + 1
    snap = _snapshot(ctx["ledger"])
    last = entries[-1].get("builds", {}) if entries else {}
    new_true = []
    for path, bs in snap.items():
        for k in FLAGS:
            if bs["flags"][k]["value"] and not (last.get(path, {}).get("flags", {}).get(k, {}).get("value")):
                new_true.append((path, k, bs["flags"][k]["evidence"]))
    if len(new_true) > 1:
        return False, ("refused: %d approval flags became true since the last accepted entry (%s); accept ONE "
                       "flag per call, each in its own commit" % (len(new_true), ", ".join("%s/%s" % (p, k) for p, k, _e in new_true)))
    any_true = any(bs["flags"][k]["value"] for bs in snap.values() for k in FLAGS)
    if any_true:
        probe = _git_show(ctx, LEDGER)
        if probe is None:
            return False, "refused: git history cannot be read, so a single-flag flip cannot be verified"
    for path, k, ev in new_true:
        if _git_show(ctx, ev) is None:
            return False, ("refused: evidence %s for %s/%s is not committed in git HEAD yet - commit the response "
                           "document first, then flip the flag" % (ev, path, k))
    entries.append({"seq": seq, "accepted_ist": ctx.get("now", datetime.now(IST)).astimezone(IST).strftime("%d-%m-%Y %H:%M:%S"),
                    "builds": snap, "prev": prev, "hash": _chain_hash(prev, seq, snap)})
    data = json.dumps({"title": "Accepted approvals hash chain - append only, written by tools/requirements_guard.py --accept-state",
                       "anchor": _anchor_of(entries), "entries": entries}, indent=1, ensure_ascii=False)
    path = os.path.join(ctx["root"], STATE)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    return True, "accepted entry %d (%s)" % (seq, entries[-1]["hash"][:12])


def r_move_safety(ctx):
    out = []
    for rel, markers in ctx["register"].get("move_safety_markers", {}).items():
        p = os.path.join(ctx["root"], rel)
        try:
            body = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            out.append(F("MOVE_SAFETY", ALERT, "move/build tool missing: %s" % rel))
            continue
        miss = [m for m in markers if m not in body]
        if miss:
            out.append(F("MOVE_SAFETY", ALERT, "%s lacks safety marker(s): %s" % (rel, ", ".join(miss))))
    return out or [F("MOVE_SAFETY", OK, "copy+sha256+atomic-rename markers present in every move/build tool")]


def r_audit_repo(ctx):
    p = os.path.join(ctx["root"], "docs", "framework", "AUDIT_PUBLISH_RULE.md")
    try:
        body = open(p, encoding="utf-8").read()
    except OSError:
        return [F("AUDIT_REPO", ALERT, "AUDIT_PUBLISH_RULE.md missing")]
    if "roopeshkumarb/onlyAuditFliles" not in body:
        return [F("AUDIT_REPO", ALERT, "audit rule does not name roopeshkumarb/onlyAuditFliles")]
    return [F("AUDIT_REPO", OK, "audit rule names the public repo roopeshkumarb/onlyAuditFliles")]


def r_friday_ssd(ctx):
    dl = datetime.fromisoformat(ctx["register"].get("friday_deadline_ist", "2026-11-06T20:00:00+05:30"))
    now = ctx["now"]
    if now < dl:
        hrs = (dl - now).total_seconds() / 3600.0
        return [F("FRIDAY_SSD", INFO, "%.1f h until Fri 20:00 IST; no box has been checked for SSD-free yet" % hrs)]
    if not ctx.get("ssd_roots"):
        return [F("FRIDAY_SSD", ALERT, "deadline passed and SSD-free is UNVERIFIED (no --ssd-root scan)")]
    left = [p for r in ctx["ssd_roots"] if os.path.isdir(r) for p in _scan_files(r)]
    if left:
        return [F("FRIDAY_SSD", ALERT, "deadline passed, %d files still on SSD (e.g. %s)" % (len(left), left[0]))]
    return [F("FRIDAY_SSD", OK, "deadline passed and the scanned SSD roots are empty")]


def r_claude_md(ctx):
    p = os.path.join(ctx["root"], "CLAUDE.md")
    if not os.path.isfile(p) or os.path.getsize(p) == 0:
        return [F("CLAUDE_MD", ALERT, "CLAUDE.md missing or empty")]
    return [F("CLAUDE_MD", OK, "CLAUDE.md present (%d bytes)" % os.path.getsize(p))]


def r_no_bat(ctx):
    bad = [p for p in _ledger_paths(ctx) if p.lower().endswith((".bat", ".cmd"))]
    if bad:
        return [F("NO_BAT", ALERT, "new build is a .bat/.cmd (Cortex XDR reports these to IT): %s" % ", ".join(bad))]
    return [F("NO_BAT", OK, "no new build is a .bat/.cmd")]


def r_docs_present(ctx):
    out = []
    for r in ctx["register"].get("requirements", []):
        for rel in r.get("evidence_files", []):
            if not os.path.isfile(os.path.join(ctx["root"], rel)):
                out.append(F("DOCS_PRESENT", ALERT, "%s evidence file missing: %s" % (r["id"], rel), req=[r["id"]]))
    return out or [F("DOCS_PRESENT", OK, "all registered evidence files exist")]


def _parse_at(s):
    s = (s or "").replace("GMT+5:30", "").strip()
    return datetime.strptime(s, "%d-%m-%Y %H:%M").replace(tzinfo=IST)


def r_trace(ctx):
    cutoff = _parse_at(ctx["register"].get("traceability_cutoff", "01-01-2026 00:00"))
    ids = {}
    bad_at = 0
    p = os.path.join(ctx["root"], TASKS)
    try:
        lines = open(p, encoding="utf-8").read().splitlines()
    except OSError as e:
        return [F("TRACE", ALERT, "TASKS.jsonl unreadable: %s" % e)]
    pat = re.compile(r"\b(R(?:0[1-9]|[12]\d|3[01])|S[1-5])\b")
    touched = set()
    for line in lines:
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        tid = d.get("id")
        text = " ".join(str(d.get(k) or "") for k in ("title", "why", "note", "src"))
        ids.setdefault(tid, []).append(bool(pat.search(text)))
        try:
            if _parse_at(d.get("at")) >= cutoff:
                touched.add(tid)
        except (ValueError, TypeError):
            bad_at += 1
    unmapped = sorted(t for t in touched if not any(ids.get(t, [])))
    out = []
    if unmapped:
        out.append(F("TRACE", ALERT, "unmapped work: %d task ids touched since %s cite no R/S requirement id: %s%s" % (
            len(unmapped), ctx["register"].get("traceability_cutoff"), ", ".join(map(str, unmapped[:15])),
            " ..." if len(unmapped) > 15 else "")))
    else:
        out.append(F("TRACE", OK, "all %d task ids touched since the cutoff cite a requirement id" % len(touched)))
    if bad_at:
        out.append(F("TRACE", INFO, "%d TASKS.jsonl entries have an unparseable 'at'" % bad_at))
    return out


RULES = {
    "TRACE": r_trace, "JOIN_UNKNOWN": r_join_unknown, "JOIN_LIVE_SAFE": r_join_live_safe,
    "CSV_TOTALS": r_csv_totals, "INSTR_DETAIL": r_instr_detail, "WEEKLY_PRESENT": r_weekly_present,
    "SSD_NONREC": r_ssd_nonrec, "POLICY_FILE": r_policy_file, "NO_OLD_STOP": r_no_old_stop,
    "TOOL_TESTS": r_tool_tests, "APPROVALS": r_approvals, "MOVE_SAFETY": r_move_safety,
    "AUDIT_REPO": r_audit_repo, "FRIDAY_SSD": r_friday_ssd, "CLAUDE_MD": r_claude_md,
    "NO_BAT": r_no_bat, "DOCS_PRESENT": r_docs_present,
}


# ---------------------------------------------------------------- fixes (only regenerate derived docs)

def apply_fix(ctx, name):
    if name != "regen_instruments":
        return {"fix": name, "applied": False, "why": "unknown fix"}
    cmd = ctx.get("gen_cmd") or [sys.executable, os.path.join(ctx["root"], GEN_CMD)]
    if not os.path.isfile(cmd[-1]):
        return {"fix": name, "applied": False, "why": "generator missing: %s" % cmd[-1]}
    r = subprocess.run(cmd, cwd=ctx["root"], capture_output=True, text=True, timeout=300)
    return {"fix": name, "applied": r.returncode == 0, "why": (r.stderr or r.stdout)[-200:].strip()}


# ---------------------------------------------------------------- run

def run(ctx):
    ctx = dict(ctx)
    ctx.setdefault("now", datetime.now(IST))
    ctx["register"] = ctx.get("register") or _load(ctx, REGISTER)
    ctx["ledger"] = ctx.get("ledger") if ctx.get("ledger") is not None else _load(ctx, LEDGER)
    findings, fixes = [], []

    def run_all():
        res = []
        for rid, fn in RULES.items():
            try:
                res.extend(fn(ctx))
            except Exception as e:  # noqa: BLE001 - a broken rule must be loud, never silently skipped
                res.append(F(rid, ALERT, "rule crashed (%s: %s) - treated as failure, not as pass" % (type(e).__name__, e)))
        return res

    findings = run_all()
    if ctx.get("fix"):
        for f in [x for x in findings if x["level"] == ALERT and x.get("fix")]:
            done = apply_fix(ctx, f["fix"])
            fixes.append(done)
        if fixes:
            findings = run_all()
    by_rule = {}
    for f in findings:
        by_rule.setdefault(f["rule"], []).append(f)
    reqs = {}
    items = [(r["id"], r) for r in ctx["register"].get("requirements", [])] + \
            [(s["id"], s) for s in ctx["register"].get("sequence", [])]
    for rid, r in items:
        mapped = [x for x in r.get("rules", []) if x != "TRACE"]
        lv = []
        for name in mapped:
            for f in by_rule.get(name, []):
                if f["req"] and rid not in f["req"]:
                    continue
                lv.append(f["level"])
        if ALERT in lv:
            st = "RED"
        elif not mapped or INFO in lv or not lv:
            st = "AMBER"
        else:
            st = "GREEN"
        reqs[rid] = {"status": st, "rules": r.get("rules", []), "text": r["text"][:90]}
    approved = {f.get("build") for f in findings if f["rule"] == "APPROVALS" and f.get("approved")}
    blocked = {f.get("build") for f in findings if f["rule"] == "APPROVALS" and f["level"] == ALERT}
    done_allowed = {b["path"]: (b["path"] in approved and b["path"] not in blocked and "*" not in blocked)
                    for b in ctx["ledger"].get("builds", [])}
    cnt = {lv: sum(1 for f in findings if f["level"] == lv) for lv in (ALERT, INFO, OK)}
    sc = {s: sum(1 for v in reqs.values() if v["status"] == s) for s in ("GREEN", "AMBER", "RED")}
    now = ctx["now"].astimezone(IST)
    line = ("REQUIREMENTS-GUARD %s IST: %d ALERT, %d INFO, %d OK | requirements GREEN %d / AMBER %d / RED %d | "
            "builds allowed to be called DONE: %d of %d" % (
                now.strftime("%d-%m-%Y %H:%M"), cnt[ALERT], cnt[INFO], cnt[OK], sc["GREEN"], sc["AMBER"], sc["RED"],
                sum(done_allowed.values()), len(done_allowed)))
    hist = _read_anchors(ctx)
    cur = ctx.get("_anchor_current")
    if cur and (not hist or (hist[-1]["length"], hist[-1]["head"]) != (cur["length"], cur["head"])):
        hist.append({"length": cur["length"], "head": cur["head"], "ist": now.strftime("%d-%m-%Y %H:%M:%S")})
    return {"generated_ist": now.strftime("%d-%m-%Y %H:%M:%S") + " GMT+5:30", "summary_line": line,
            "anchor_history": hist,
            "counts": cnt, "requirement_status": sc, "requirements": reqs, "done_allowed": done_allowed,
            "fixes": fixes, "findings": findings}


def write_report(ctx, report, path=None):
    path = path or os.path.join(ctx["root"], REPORT)
    data = json.dumps(report, indent=2, ensure_ascii=False)
    try:
        from guard_core import _atomic_write
        _atomic_write(path, data)
    except ImportError:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--ssd-root", action="append", default=[], help="read-only scan root (repeatable)")
    ap.add_argument("--policy-path", action="append", default=[])
    ap.add_argument("--fix", action="store_true", help="regenerate derived docs via their generator, then re-check")
    ap.add_argument("--notify", action="store_true", help="send the summary through guard_core.notify (off by default)")
    ap.add_argument("--accept-state", action="store_true",
                    help="append the current approvals ledger to the hash chain (refused while an approvals ALERT stands)")
    ap.add_argument("--no-report", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    ctx = {"root": os.path.abspath(a.root), "ssd_roots": a.ssd_root, "policy_paths": a.policy_path, "fix": a.fix}
    if a.accept_state:
        try:
            ok, msg = accept_state(ctx)
        except Exception as e:  # noqa: BLE001
            print("REQUIREMENTS-GUARD could not accept state: %s: %s" % (type(e).__name__, e))
            return 2
        print("REQUIREMENTS-GUARD accept-state: %s" % msg)
        return 0 if ok else 1
    try:
        rep = run(ctx)
    except Exception as e:  # noqa: BLE001
        print("REQUIREMENTS-GUARD could not run: %s: %s" % (type(e).__name__, e))
        return 2
    if not a.no_report:
        write_report(ctx, rep)
    print(rep["summary_line"])
    for f in rep["findings"]:
        if f["level"] == ALERT or (a.verbose and f["level"] != OK) or (a.verbose and f["level"] == OK):
            print("  [%s] %s: %s" % (f["level"], f["rule"], f["msg"]))
    for fx in rep["fixes"]:
        print("  [FIX] %s applied=%s %s" % (fx["fix"], fx["applied"], fx["why"]))
    if a.notify and rep["counts"][ALERT]:
        try:
            import guard_core
            guard_core.notify(rep["summary_line"], "requirements guard ALERT", "requirements_guard")
        except Exception as e:  # noqa: BLE001
            print("  [notify failed] %s" % e)
    return 1 if rep["counts"][ALERT] else 0


if __name__ == "__main__":
    raise SystemExit(main())
