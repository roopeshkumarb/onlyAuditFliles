#!/usr/bin/env python3
"""livewatch.py - BLK-001 (Kumar, 03-11-2026): the DATA FRESHNESS WATCHDOG that kills a silent recorder.

WHY: on 02-11-2026 the i7 Dhan depth socket closed (1006) at 13:58 and never reopened while `docker ps`
said "Up". Docker status is not data. This daemon judges each live-only recorder by the DATA it last
stored and, when the data stops during the session, issues `docker kill <container>` so the restart
policy (and, if that does not bring it back, a `docker start`) replaces the dead socket.

THE RULE (as ordered): during the session, if now - last_data > STALE_S (default 60 s), run
`docker kill <container>`.
  last_data = the newest of (a) status.json "last_tick" when the recorder writes one (Kite ticks) and
              (b) the modification time of today's day file or its -wal (every stored row moves it).
              (b) costs no database read. MEASURED 03-11-2026 on the i5 during the session: the longest
              gap between writes of all four recorders was 4 s (150 s window, 2 s sampling).
DEVIATIONS FROM THE ORDER, each with its reason (Kumar can switch them back with the flags):
  1 SESSION_START default 09:16, not 09:00. Reason: the recorders' own silence guards dropped sockets that
    had been silent 197-210 s at 09:11-09:13 on 03-11-2026 (pre-open is quiet). A 60 s rule from 09:00 would
    kill every recorder every morning. Flag: --session-start 09:00.
  2 MAX_KILLS_PER_HOUR = 3 per container. Reason: a kill loop under a broker's connection cap (Dhan: 5
    sockets, the 6th drops the oldest) or an outage would flap forever and lose more data than it saves.
    After the third kill it writes an ESCALATE file and logs CRITICAL, and stops killing that container.
  3 NO DAY FILE by 09:20 with instruments 0 is also treated as dead (the i7 Fyers TBT wrote no file for
    three days; a rule that only reads file age could never see it).
It NEVER touches cloudflared, portainer, blpro_09 or any name not in RECORDERS.

Stdlib only, python 3.8 compatible, no pip. ADVISORY ONLY: it reads stored data and restarts recorders.
Runs on the host (outside Docker) so a Docker service restart cannot take it down.

    python3 livewatch.py --root /volume1/docker/datapullers --box i5            # live
    python3 livewatch.py --root ... --box i5 --dry-run --once                   # print what it would do
"""
import argparse
import json
import os
import subprocess
import sys
import time

RECORDERS = {                     # container -> (folder under root, day-file prefix)
    "tickrec": ("ticks", "ticks_"),
    "depthrec": ("depth", "depth_"),
    "upstoxrec": ("upstox_live", "upstox_"),
    "fyerstbt": ("fyers_tbt", "tbt_"),
}
NEVER_TOUCH = ("cloudflared", "portainer", "blpro_09", "blpro_compute", "blpro_synchub",
               "blpro_vendorwatch", "watchtower")
DEFAULT_DOCKER = "/var/packages/ContainerManager/target/usr/bin/docker"


def hhmm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def in_session(now, start, end):
    """Weekdays only, box-local time, [start, end]. (NSE holidays are not known here: on a holiday the
    recorders see no ticks, so a holiday can cost at most MAX_KILLS_PER_HOUR harmless restarts.)"""
    lt = time.localtime(now)
    return lt.tm_wday < 5 and hhmm(start) <= lt.tm_hour * 60 + lt.tm_min <= hhmm(end)


def file_write_time(path):
    """Newest write evidence of a SQLite day file: the file or its -wal."""
    best = 0.0
    for p in (path, path + "-wal"):
        try:
            best = max(best, os.stat(p).st_mtime)
        except OSError:
            pass
    return best


def status_last_tick(status):
    """Epoch of status.json 'last_tick' ('DD-MM-YYYY HH:MM:SS GMT+5:30') or 0.0 if absent/null."""
    v = status.get("last_tick")
    if not v:
        return 0.0
    try:
        return time.mktime(time.strptime(str(v).replace(" GMT+5:30", ""), "%d-%m-%Y %H:%M:%S"))
    except ValueError:
        return 0.0


def evaluate(name, root, box, now, stale_s, no_file_after):
    """-> dict(verdict, age_s, why). verdict in FRESH, DEAD, NO_FILE_DEAD, NO_FILE_WAITING."""
    folder, prefix = RECORDERS[name]
    day = time.strftime("%Y%m%d", time.localtime(now))
    path = os.path.join(root, folder, box, "%s%s.db" % (prefix, day))
    status = {}
    try:
        with open(os.path.join(root, folder, box, "status.json"), encoding="utf-8") as f:
            status = json.load(f)
    except (OSError, ValueError):
        pass
    fw = file_write_time(path)
    lt = status_last_tick(status)
    last = max(fw, lt)
    if fw == 0.0:
        lt_now = time.localtime(now)
        if lt_now.tm_hour * 60 + lt_now.tm_min >= hhmm(no_file_after) and not status.get("instruments"):
            return {"verdict": "NO_FILE_DEAD", "age_s": None,
                    "why": "no day file %s and instruments=0 after %s" % (os.path.basename(path), no_file_after)}
        return {"verdict": "NO_FILE_WAITING", "age_s": None, "why": "no day file yet"}
    age = now - last
    if age > stale_s:
        return {"verdict": "DEAD", "age_s": round(age, 1),
                "why": "last data %.0f s ago (limit %.0f s); file_write=%s last_tick=%s" % (
                    age, stale_s, time.strftime("%H:%M:%S", time.localtime(fw)),
                    time.strftime("%H:%M:%S", time.localtime(lt)) if lt else "n/a")}
    return {"verdict": "FRESH", "age_s": round(age, 1), "why": "last data %.1f s ago" % age}


class Watch(object):
    def __init__(self, a):
        self.a = a
        self.kills = {}                       # container -> [epoch,...]
        os.makedirs(a.state_dir, exist_ok=True)
        self.escalated = set()

    def log(self, level, msg):
        line = "%s [livewatch %s] %s %s" % (time.strftime("%d-%m-%Y %H:%M:%S GMT+5:30"), self.a.box, level, msg)
        print(line, flush=True)
        if self.a.log:
            try:
                with open(self.a.log, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except OSError:
                pass

    def docker(self, *args, **kw):
        cmd = [self.a.docker] + list(args)
        if self.a.dry_run:
            self.log("DRYRUN", "would run: " + " ".join(cmd))
            return 0, "", ""
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                           timeout=kw.get("timeout", 60))
        return p.returncode, p.stdout.strip(), p.stderr.strip()

    def kill(self, name, why, now):
        if name in NEVER_TOUCH or name not in RECORDERS:
            self.log("REFUSE", "%s is not a managed recorder" % name)
            return
        recent = [t for t in self.kills.get(name, []) if t > now - 3600]
        if len(recent) >= self.a.max_kills:
            if name not in self.escalated:
                self.escalated.add(name)
                self.log("CRITICAL", "%s killed %d times in the last hour and is still silent: NOT killing again. "
                         "Needs a human. reason=%s" % (name, len(recent), why))
                try:
                    with open(os.path.join(self.a.state_dir, "ESCALATE_%s.json" % name), "w") as f:
                        json.dump({"container": name, "box": self.a.box, "at": time.time(), "why": why}, f)
                except OSError:
                    pass
            return
        self.log("WARN", "%s: %s -> docker kill %s" % (name, why, name))
        rc, out, err = self.docker("kill", name)
        self.kills.setdefault(name, []).append(now)
        self.log("INFO", "docker kill %s rc=%s %s" % (name, rc, (err or out)[:120]))
        if self.a.dry_run:
            return
        time.sleep(self.a.restart_wait)
        rc, out, _ = self.docker("inspect", name, "--format", "{{.State.Running}}")
        if out != "true":                 # restart policy did not bring it back: start it
            rc, out, err = self.docker("start", name)
            self.log("INFO", "%s was not restarted by policy; docker start rc=%s" % (name, rc))
        else:
            self.log("INFO", "%s is running again (restart policy)" % name)

    def once(self, now=None):
        now = time.time() if now is None else now
        if not in_session(now, self.a.session_start, self.a.session_end):
            self.log("INFO", "outside session window %s-%s: nothing to judge" % (self.a.session_start, self.a.session_end))
            return []
        results = []
        for name in sorted(RECORDERS):
            r = evaluate(name, self.a.root, self.a.box, now, self.a.stale_s, self.a.no_file_after)
            results.append((name, r))
            if r["verdict"] in ("DEAD", "NO_FILE_DEAD"):
                self.kill(name, r["why"], now)
            else:
                self.log("OK", "%s %s (%s)" % (name, r["verdict"], r["why"]))
        return results


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--box", required=True)
    p.add_argument("--docker", default=DEFAULT_DOCKER)
    p.add_argument("--stale-s", type=float, default=60.0)
    p.add_argument("--session-start", default="09:16")
    p.add_argument("--session-end", default="15:30")
    p.add_argument("--no-file-after", default="09:20")
    p.add_argument("--interval", type=float, default=15.0)
    p.add_argument("--max-kills", type=int, default=3)
    p.add_argument("--restart-wait", type=float, default=10.0)
    p.add_argument("--state-dir", default="/tmp/livewatch_state")
    p.add_argument("--log", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--once", action="store_true")
    p.add_argument("--test-recorder", default="", help="PROOF HOOK: lwtest_NAME=folder:prefix adds a disposable "
                   "recorder. The name MUST start with lwtest_ so a production container can never be named here.")
    a = p.parse_args(argv)
    if a.test_recorder:
        nm, spec = a.test_recorder.split("=", 1)
        if not nm.startswith("lwtest_"):
            sys.exit("--test-recorder name must start with lwtest_")
        folder, prefix = spec.split(":", 1)
        RECORDERS.clear()                 # PROOF MODE: ONLY the disposable recorder is judged; production names are gone
        RECORDERS[nm] = (folder, prefix)
    w = Watch(a)
    if not any(os.path.isdir(os.path.join(a.root, f, a.box)) for f, _ in RECORDERS.values()):
        w.log("INFO", "no recorder folders under %s for box %s: nothing to watch on this box" % (a.root, a.box))
    if a.once:
        w.once()
        return 0
    lock = os.path.join(a.state_dir, "livewatch.pid")
    try:
        old = int(open(lock).read().strip())
        os.kill(old, 0)
        w.log("INFO", "another livewatch (pid %d) is running: exiting" % old)
        return 0
    except (OSError, ValueError):
        pass
    open(lock, "w").write(str(os.getpid()))
    while True:
        try:
            w.once()
        except Exception as e:                       # never die: a dead watchdog is the failure it prevents
            w.log("ERROR", "pass failed: %s: %s" % (type(e).__name__, e))
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
