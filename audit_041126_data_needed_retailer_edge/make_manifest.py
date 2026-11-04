#!/usr/bin/env python3
"""Copy (never move) the audited artifacts into artifacts/, write MANIFEST.sha256 (sha256 of every
copied file, computed here, not typed) and scan the pack for secrets. Run from the repo root:
    python3 docs/audit_pack_041126/make_manifest.py
Exit 1 if a secret-looking VALUE is found (long hex/base64-ish token, password=, an RFC1918 address)."""
import hashlib, os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PACK = os.path.join(ROOT, "docs", "audit_pack_041126")
ART = os.path.join(PACK, "artifacts")
FILES = """CLAUDE.md
config/recoverability.json
pullers/shared/dp_recoverability.py
pullers/shared/dp_families.py
docs/framework/DATA_NEEDED_INSTRUMENTS_041126.md
docs/framework/data_needed_instruments_041126.csv
docs/framework/LIVE_CENSUS_041126.md
docs/framework/LIVE_CENSUS_041126.csv
docs/framework/RETAILER_PULLER_DESIGN_041126.md
docs/framework/RETAILER_DB_EDGE_SCHEMA_041126.md
docs/framework/FRIDAY_SSD_MIGRATION_PLAN_041126.md
docs/framework/REGIME_DATA_NEEDED_041126.md
docs/framework/FABLE_REVIEW_041126.md
docs/framework/REQUIREMENTS_REGISTER.json
docs/framework/APPROVALS_LEDGER.json
docs/framework/guard_report.json
tools/gen_data_needed_instruments_041126.py
tools/retailer_db_build.py
tools/retailer_db_inventory.py
tools/requirements_guard.py
tests/test_dp_recoverability.py
tests/test_recoverability_placement.py
tests/test_gen_data_needed_instruments.py
tests/test_retailer_db_build.py
tests/test_requirements_guard.py""".split()
SECRET = [("RFC1918 address", re.compile(r"\b(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")),
          ("password/secret assignment", re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|totp)\b\s*[:=]\s*['\"]?[A-Za-z0-9+/_\-]{8,}")),
          ("long opaque string (hex/base64, no path chars)", re.compile(r"(?<![A-Za-z0-9_/.\-])(?=[A-Za-z0-9+=]*\d)(?=[A-Za-z0-9+=]*[A-Za-z])[A-Za-z0-9+=]{32,}(?![A-Za-z0-9_/.\-])")),
          ("bearer/jwt", re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}|eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"))]
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()
os.makedirs(ART, exist_ok=True)
REDACT = [("192.168.2.x", "<LAN-subnet>"), ("192.168.", "<LAN>.")]
REDACTED = []
lines, missing = [], []
for rel in FILES:
    src = os.path.join(ROOT, rel)
    if not os.path.exists(src):
        missing.append(rel); continue
    dst = os.path.join(ART, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    txt = open(src, encoding="utf-8", errors="surrogateescape").read()
    red = txt
    for pat, rep in REDACT:
        red = red.replace(pat, rep)
    if red != txt:
        REDACTED.append(rel)
    with open(dst, "w", encoding="utf-8", errors="surrogateescape", newline="") as fo:
        fo.write(red)
    lines.append("%s  %s" % (sha(dst), rel))
with open(os.path.join(PACK, "MANIFEST.sha256"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
with open(os.path.join(PACK, "REDACTIONS.txt"), "w", encoding="utf-8") as f:
    f.write("Files whose pack copy differs from the repo file ONLY by these replacements %r:\n%s\n" % (REDACT, "\n".join(REDACTED) or "(none)"))
hits = []
for dp, _, fs in os.walk(PACK):
    for fn in fs:
        if fn in ("make_manifest.py", "MANIFEST.sha256", "REDACTIONS.txt"):
            continue
        p = os.path.join(dp, fn)
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for ln, line in enumerate(txt.splitlines(), 1):
            for name, rx in SECRET:
                for m in rx.finditer(line):
                    hits.append((os.path.relpath(p, PACK), ln, name, m.group(0)[:70]))
print("copied %d files, missing %s" % (len(lines), missing))
for h in hits:
    print("SECRET-SCAN HIT %s:%d [%s] %s" % h)
print("secret-scan hits: %d" % len(hits))
sys.exit(1 if (hits or missing) else 0)
