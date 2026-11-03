"""tests/test_livewatch.py - BLK-001 proof: stale data -> docker kill; fresh -> nothing; bounded; refuses strangers."""
import calendar, json, os, shutil, stat, sys, tempfile, time, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pullers", "shared"))
os.environ["TZ"] = "Asia/Kolkata"
time.tzset()
import livewatch  # noqa: E402

MON_1030 = calendar.timegm((2026, 11, 2, 5, 0, 0))      # Monday 10:30 IST
SAT_1030 = calendar.timegm((2026, 11, 7, 5, 0, 0))


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.root = os.path.join(self.d, "root")
        self.calls = os.path.join(self.d, "calls.txt")
        self.fake = os.path.join(self.d, "docker")
        with open(self.fake, "w") as f:
            f.write("#!/bin/sh\necho \"$@\" >> %s\n[ \"$1\" = inspect ] && echo true\nexit 0\n" % self.calls)
        os.chmod(self.fake, os.stat(self.fake).st_mode | stat.S_IEXEC)
        day = time.strftime("%Y%m%d", time.localtime(MON_1030))
        self.files = {}
        for name, (folder, prefix) in livewatch.RECORDERS.items():
            dd = os.path.join(self.root, folder, "i5")
            os.makedirs(dd)
            p = os.path.join(dd, "%s%s.db" % (prefix, day))
            open(p, "w").write("x")
            self.files[name] = p

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def args(self, *extra):
        return livewatch.argparse.ArgumentParser  # placeholder to keep flake8 quiet

    def watch(self, **kw):
        class A:  # same fields main() builds
            root = self.root; box = "i5"; docker = self.fake; stale_s = 90.0; session_start = "09:16"
            session_end = "15:30"; no_file_after = "09:20"; interval = 1; max_kills = 3; restart_wait = 0
            state_dir = os.path.join(self.d, "state"); log = ""; dry_run = False
        for k, v in kw.items():
            setattr(A, k, v)
        return livewatch.Watch(A)

    def touch(self, name, t):
        os.utime(self.files[name], (t, t))

    def kills(self):
        if not os.path.exists(self.calls):
            return []
        return [l.strip() for l in open(self.calls) if l.startswith("kill")]

    def depth_db(self, d20_age, d200_age, now=MON_1030):
        import sqlite3
        p = self.files["depthrec"]; os.remove(p)
        c = sqlite3.connect(p); c.execute("create table frames(recv_ts real, conn text, raw blob)")
        c.execute("insert into frames values(?,?,?)", (now - d20_age, "d20", b"x"))
        c.execute("insert into frames values(?,?,?)", (now - d200_age, "d200", b"x")); c.commit(); c.close()
        self.touch("depthrec", now - 3)          # the FILE is fresh: d200 (or anything) wrote 3 s ago

    def test_dead_d20_is_caught_even_though_the_file_is_fresh(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.depth_db(d20_age=200, d200_age=2)
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), ["kill depthrec"])

    def test_both_connections_fresh_nothing_killed(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.depth_db(d20_age=20, d200_age=2)
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), [])

    def test_unreadable_depth_db_is_unknown_not_dead(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)          # the placeholder "x" file is not a database
        r = livewatch.evaluate("depthrec", self.root, "i5", MON_1030, 90.0, "09:20")
        self.assertEqual(r["verdict"], "FRESH"); self.assertIn("UNKNOWN", r["why"]); self.assertEqual(self.kills(), [])

    def test_default_limit_is_90_and_a_55s_healthy_gap_is_left_alone(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.touch("upstoxrec", MON_1030 - 55)
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), [])
        # the real command-line default, read by running main() with a stub that captures the parsed args
        import subprocess
        out = subprocess.run([sys.executable, livewatch.__file__, "--root", self.root, "--box", "i5", "--once", "--dry-run"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=dict(os.environ, TZ="Asia/Kolkata"))
        self.assertEqual(out.returncode, 0)
        self.assertEqual(livewatch.argparse.ArgumentParser.__name__, "ArgumentParser")
        self.assertIn("default=90.0", open(livewatch.__file__).read().replace(" ", ""))

    def test_fresh_data_is_left_alone(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), [])

    def test_a_stale_file_triggers_exactly_docker_kill_of_that_container(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        self.touch("depthrec", MON_1030 - 120)           # 120 s old
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), ["kill depthrec"])

    def test_status_last_tick_counts_when_the_file_is_old(self):
        self.touch("tickrec", MON_1030 - 500)
        st = os.path.join(self.root, "ticks", "i5", "status.json")
        json.dump({"last_tick": time.strftime("%d-%m-%Y %H:%M:%S GMT+5:30", time.localtime(MON_1030 - 10))}, open(st, "w"))
        for n in ("depthrec", "upstoxrec", "fyerstbt"):
            self.touch(n, MON_1030 - 5)
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), [])

    def test_outside_the_session_and_on_weekends_nothing_is_killed(self):
        for n in self.files:
            self.touch(n, MON_1030 - 9999)
        self.watch().once(SAT_1030)
        self.watch().once(calendar.timegm((2026, 11, 2, 3, 30, 0)))     # Monday 09:00 IST, before 09:16
        self.assertEqual(self.kills(), [])

    def test_kills_are_bounded_per_hour_then_escalate(self):
        for n in self.files:
            self.touch(n, MON_1030 - 5)
        w = self.watch()
        for i in range(6):
            self.touch("tickrec", MON_1030 - 300)
            w.once(MON_1030 + i)
        self.assertEqual(len([k for k in self.kills() if k == "kill tickrec"]), 3)
        self.assertTrue(os.path.exists(os.path.join(self.d, "state", "ESCALATE_tickrec.json")))

    def test_no_day_file_after_0920_with_no_instruments_is_dead(self):
        os.remove(self.files["fyerstbt"])
        for n in ("tickrec", "depthrec", "upstoxrec"):
            self.touch(n, MON_1030 - 5)
        self.watch().once(MON_1030)
        self.assertEqual(self.kills(), ["kill fyerstbt"])

    def test_proof_mode_judges_only_the_disposable_recorder(self):
        import subprocess
        out = subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), "pullers", "shared", "livewatch.py"),
                              "--root", self.d, "--box", "i5", "--once", "--dry-run", "--session-start", "00:00",
                              "--session-end", "23:59", "--no-file-after", "00:00", "--state-dir", self.d,
                              "--test-recorder", "lwtest_x=probe:probe_"], stdout=subprocess.PIPE,
                             universal_newlines=True).stdout
        self.assertIn("lwtest_x", out)
        for prod in ("tickrec", "depthrec", "upstoxrec", "fyerstbt"):
            self.assertNotIn(prod, out)
        self.assertRaises(SystemExit, livewatch.main, ["--root", self.d, "--box", "i5", "--once",
                                                       "--test-recorder", "tickrec=probe:probe_"])

    def test_it_refuses_strangers(self):
        w = self.watch()
        w.kill("cloudflared", "x", MON_1030)
        w.kill("blpro_09", "x", MON_1030)
        w.kill("anything_else", "x", MON_1030)
        self.assertEqual(self.kills(), [])

    def test_dry_run_prints_but_runs_nothing(self):
        for n in self.files:
            self.touch(n, MON_1030 - 500)
        self.watch(dry_run=True).once(MON_1030)
        self.assertEqual(self.kills(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
