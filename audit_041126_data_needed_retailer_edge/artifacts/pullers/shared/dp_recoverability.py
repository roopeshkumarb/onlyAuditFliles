"""Where may a piece of data be written? (Kumar 28-10-2026)
NON_RECOVERABLE data (ticks, depth, order flow, live chain snapshots ...) goes to HDD only, never to an SSD, on every device.
RECOVERABLE data (history that the broker serves again) goes to the SSDs. UNKNOWN is treated as NON_RECOVERABLE.
This is a PURE function module: it decides and checks, it does not move or delete anything and never stops a pull.
Python 3.8 compatible, stdlib only."""
import json
import os

NON, REC, UNK = "NON_RECOVERABLE", "RECOVERABLE", "UNKNOWN"
CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "recoverability.json")


def load(path=None):
    return json.load(open(path or CONFIG, encoding="utf-8"))


def classify(name, cfg=None):
    """name = a dataset name or a file path. Returns (class, matched_rule_or_None). NON_RECOVERABLE patterns are tested first."""
    cfg = cfg or load()
    low = os.path.basename(str(name)).lower() if os.sep in str(name) else str(name).lower()
    for want in (False, True):
        for rule, spec in cfg["classes"].items():
            if bool(spec["recoverable"]) == want and any(p in low for p in spec["patterns"]):
                return (REC if want else NON), rule
    return UNK, None


def effective(name, cfg=None):
    """The class actually used for placement: UNKNOWN is protected, i.e. NON_RECOVERABLE."""
    c, rule = classify(name, cfg)
    return (NON if c == UNK else c), rule, (c == UNK)


def route(klass, roots):
    """roots = {"ssd": [paths], "hdd": [paths], "ram": [paths]} of THIS device.
    Returns {"status": ..., "roots": [...], "note": ...}.
    NON_RECOVERABLE: hdd roots only. No hdd root (the Pi) => NO_HDD, and NEVER falls back to ssd.
    RECOVERABLE: ssd roots; if the device has no ssd, hdd roots."""
    ssd, hdd = list(roots.get("ssd") or []), list(roots.get("hdd") or [])
    if klass == NON:
        if hdd:
            return {"status": "OK", "roots": hdd, "note": "non-recoverable: hard disk only"}
        return {"status": "NO_HDD", "roots": [], "note": "this device has no hard disk; non-recoverable data must be recorded by another device"}
    if klass == REC:
        if ssd:
            return {"status": "OK", "roots": ssd, "note": "recoverable: SSD"}
        if hdd:
            return {"status": "OK", "roots": hdd, "note": "recoverable, no SSD on this device: hard disk"}
        return {"status": "NO_DISK", "roots": [], "note": "no disk root configured"}
    raise ValueError("klass must be NON_RECOVERABLE or RECOVERABLE (use effective() first)")


def _under(path, root):
    root = root.rstrip("/")
    return path == root or path.startswith(root + "/")


def check_path(path, roots, cfg=None):
    """Returns None if the path is allowed, else a violation text. A NON_RECOVERABLE (or UNKNOWN) name under any SSD root is a violation."""
    klass, rule, unknown = effective(path, cfg)
    if klass == NON and any(_under(path, r) for r in (roots.get("ssd") or [])):
        return "%s file on an SSD (%s)%s: %s" % (NON, rule or "unclassified", " [UNKNOWN name treated as protected]" if unknown else "", path)
    return None


def scan(paths, roots, cfg=None):
    """Report only: list of violations among the given paths (no disk is touched)."""
    return [v for v in (check_path(p, roots, cfg) for p in paths) if v]
