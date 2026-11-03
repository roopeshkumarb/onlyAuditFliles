#!/usr/bin/env python3
"""audit_publish.py - keep the public audit repo self-describing so an outside auditor needs ONE fixed link.
  python3 tools/audit_publish.py <repo_dir>            rebuild MANIFEST.json + SHA256SUMS (every file, sha256, bytes, raw URL)
  python3 tools/audit_publish.py <repo_dir> --verify   fetch every raw URL from GitHub and compare sha256 (run a few minutes after push)
Skips .git. Fails (exit 1) if a file looks like it contains a secret. Stdlib only."""
import hashlib, json, os, re, sys, time, urllib.request
BASE = "https://raw.githubusercontent.com/roopeshkumarb/onlyAuditFliles/main/"
SECRET = re.compile(r"eyJ[A-Za-z0-9_\-]{20,}|BEGIN [A-Z ]*PRIVATE KEY|(?i:password|api[_-]?key|secret)\s*[:=]\s*['\"]?[A-Za-z0-9/+]{12,}")
def files(root):
    for d, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x != ".git"]
        for f in fs:
            p = os.path.join(d, f); rel = os.path.relpath(p, root).replace(os.sep, "/")
            if rel in ("MANIFEST.json", "SHA256SUMS"): continue
            yield rel, p
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def main():
    root = sys.argv[1]; items = []
    for rel, p in sorted(files(root)):
        data = open(p, "rb").read()
        if SECRET.search(data.decode("utf-8", "ignore")): print("SECRET-LIKE TEXT in", rel); sys.exit(1)
        items.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "raw_url": BASE + rel})
    if "--verify" in sys.argv:
        bad = 0
        for it in items:
            try: got = hashlib.sha256(urllib.request.urlopen(it["raw_url"], timeout=30).read()).hexdigest()
            except Exception as e: got = "ERR %s" % e
            ok = got == it["sha256"]; bad += (not ok)
            print("OK  " if ok else "FAIL", it["path"])
        print("verified %d files, %d mismatches" % (len(items), bad)); sys.exit(1 if bad else 0)
    json.dump({"generated": time.strftime("%d-%m-%Y %H:%M IST", time.gmtime(time.time() + 19800)), "files": items},
              open(os.path.join(root, "MANIFEST.json"), "w"), indent=1)
    open(os.path.join(root, "SHA256SUMS"), "w").write("".join("%s  %s\n" % (i["sha256"], i["path"]) for i in items))
    print("manifest: %d files" % len(items))
main()
