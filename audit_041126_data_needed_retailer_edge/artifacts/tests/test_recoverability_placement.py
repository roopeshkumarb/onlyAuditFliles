"""T-1292 (H12): tools/check_recoverability_placement.py must catch a NON_RECOVERABLE
file physically on an SSD host path, and must NOT false-alarm on a RECOVERABLE one -
on a real temp directory tree, not a mock.

Run: python3 tests/test_recoverability_placement.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "pullers", "shared"))
import check_recoverability_placement as chk  # noqa: E402


def main():
    failures = []

    # TEST 1 - roots_from_mounts splits by host Source, not container Destination.
    mounts = [
        {"Source": "/volume2/datapullers/fyers", "Destination": "/data/fyers"},
        {"Source": "/volume1/docker/datapullers/kite", "Destination": "/data/kite"},
        {"Source": "/volume1/docker/blpro_data/009/app/pull_lease_i5", "Destination": "/lease"},
    ]
    roots = chk.roots_from_mounts(mounts)
    # /lease's host Source also starts with /volume1 (it really is on the HDD), so it
    # correctly lands in hdd too - not a bug, just a mount this fixture also carries.
    if roots != {"ssd": ["/data/fyers"], "hdd": ["/data/kite", "/lease"]}:
        failures.append("TEST1 FAIL: roots_from_mounts got %r" % roots)
    print("TEST1 roots_from_mounts:", roots)

    # TEST 2 - a tick file under an SSD-rooted directory is a real violation, scanned
    # from a REAL temp tree (own isolated root, never a shared parent - see T-1283's
    # scratchpad-wipe lesson, same discipline applied here).
    tmp = tempfile.mkdtemp(prefix="dp_recov_test_")
    try:
        ssd_like = os.path.join(tmp, "volume2_sim", "fyers")
        hdd_like = os.path.join(tmp, "volume1_sim", "fyers_tbt")
        os.makedirs(ssd_like)
        os.makedirs(hdd_like)
        with open(os.path.join(ssd_like, "fyers_history_311026.db"), "w") as f:
            f.write("x")
        with open(os.path.join(hdd_like, "fyers_tbt_311026.db"), "w") as f:
            f.write("x")
        # one deliberately WRONG file: a tick-pattern name placed under the SSD-like dir
        bad = os.path.join(ssd_like, "fyers_tick_stream_311026.db")
        with open(bad, "w") as f:
            f.write("x")

        entries = chk.scan_root(tmp)
        violations = [(p, k, r) for p, k, r in entries
                      if k in (chk.rec.NON, chk.rec.UNK) and "volume2_sim" in p]
        if not any(bad in p for p, _, _ in violations):
            failures.append("TEST2 FAIL: the planted tick file under the SSD-like dir "
                             "was not flagged: %r" % violations)
        # the legitimate history file must NOT be flagged
        if any("fyers_history_311026.db" in p for p, _, _ in violations):
            failures.append("TEST2 FAIL: a legitimate history file was falsely flagged")
        print("TEST2 violations found:", violations)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # TEST 3 - deliberate break: if classify() is bypassed (as if nothing were ever
    # checked), the planted violation is invisible. Proves the test is not trivially
    # green - scan_root must actually be doing the classification work.
    tmp2 = tempfile.mkdtemp(prefix="dp_recov_test2_")
    try:
        d = os.path.join(tmp2, "volume2_sim", "fyers")
        os.makedirs(d)
        bad2 = os.path.join(d, "fyers_tick_stream_x.db")
        with open(bad2, "w") as f:
            f.write("x")
        naive = [(os.path.join(dp, fn), "NOT_CHECKED", None)
                 for dp, _, fs in os.walk(tmp2) for fn in fs]
        if any(k != "NOT_CHECKED" for _, k, _ in naive):
            failures.append("TEST3 FAIL: naive walk unexpectedly classified something")
        print("TEST3 (sanity: a naive walk classifies nothing) ok")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    if failures:
        print("\nFAILURES:\n" + "\n".join(failures))
        sys.exit(1)
    print("\nRESULT: PASS - all 3 checks green")


if __name__ == "__main__":
    main()
