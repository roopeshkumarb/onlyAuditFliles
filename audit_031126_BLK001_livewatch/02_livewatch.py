#!/usr/bin/env python3
"""livewatch.py - BLK-001 (Kumar, 03-11-2026): the DATA FRESHNESS WATCHDOG that kills a silent recorder.

WHY: on 02-11-2026 the i7 Dhan depth socket closed (1006) at 13:58 and never reopened while `docker ps`
said "Up". Docker status is not data. This daemon judges each live-only recorder by the DATA it last
stored and, when the data stops during the session, issues `docker kill <container>` so the restart
policy (and, if that does not bring it back, a `docker start`) replaces the dead socket.

THE RULE (as ordered): during the session, if now - last_data > STALE_S (default 90 s since v2; the owner ordered 60 s), run
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
import calendar
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
# v2 (auditor condition, 03-11-2026): a recorder that writes SEVERAL sockets into ONE day file hides a dead socket behind
# the live ones (Dhan: d20 silent ~4 min 12 times on the i5 while d200 kept the file fresh). So judge each connection by
# the newest recv_ts of its own rows. Unreadable DB / no rows for the connection = UNKNOWN (never killed on UNKNOWN).
# v3: upstox/tbt write a heartbeat/open/close row into the SAME day file's `events` table (dp_recguard.log_event), which moves the
# file mtime with zero frames; so judge those by the newest frames.recv_ts too (col None = single series).
CONNS = {"depthrec": ("frames", "conn", ("d20", "d200")),
         "upstoxrec": ("frames", None, ("frames",)),
         "fyerstbt": ("frames", None, ("frames",))}
NEVER_TOUCH = ("cloudflared", "portainer", "blpro_09", "blpro_compute", "blpro_synchub",
               "blpro_vendorwatch", "watchtower")
DEFAULT_DOCKER = "/var/packages/ContainerManager/target/usr/bin/docker"


def ist(now):
    """Struct time in IST (GMT+5:30) computed from the epoch, independent of the host TZ (auditor defect 6)."""
    return time.gmtime(now + 19800)


def hhmm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def in_session(now, start, end):
    """Weekdays only, box-local time, [start, end]. (NSE holidays are not known here: on a holiday the
    recorders see no ticks, so a holiday can cost at most MAX_KILLS_PER_HOUR harmless restarts.)"""
    lt = ist(now)
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
    e = status.get("last_tick_epoch")             # TZ-safe field some recorders write
    if isinstance(e, (int, float)) and e > 0:
        return float(e)
    v = status.get("last_tick")
    if not v:
        return 0.0
    try:
        return calendar.timegm(time.strptime(str(v).replace(" GMT+5:30", ""), "%d-%m-%Y %H:%M:%S")) - 19800
    except ValueError:
        return 0.0


def conn_last(path, spec, since=0.0):
    """-> {conn: last recv_ts}; 0.0 = NO row newer than `since` (silent at least that long, or never connected: bounded scan so a dead
    connection cannot make every pass walk the whole index); None = UNKNOWN (db unreadable or locked)."""
    table, col, conns = spec
    out = {c: None for c in conns}
    try:
        import sqlite3
        con = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=3)
        try:
            for c in conns:
                if col is None:
                    r = con.execute("select recv_ts from %s where recv_ts>? order by recv_ts desc limit 1" % table, (since,)).fetchone()
                else:
                    r = con.execute("select recv_ts from %s where %s=? and recv_ts>? order by recv_ts desc limit 1" % (table, col), (c, since)).fetchone()
                out[c] = float(r[0]) if r and r[0] is not None else 0.0
        finally:
            con.close()
    except Exception:
        pass
    return out


def events_max(path, name):
    """Newest row time in the table dp_recguard writes events to (depth/upstox/tbt: events.at_ts; tickrec has session_log, a count only).
    Lets the dry run show whether non-data rows keep the file mtime fresh. '' = unknown."""
    try:
        import sqlite3
        con = sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=3)
        try:
            if name == "tickrec":
                return "session_log_rows=%d" % con.execute("select count(*) from session_log").fetchone()[0]
            r = con.execute("select max(at_ts) from events").fetchone()
            return "%.0f" % r[0] if r and r[0] is not None else ""
        finally:
            con.close()
    except Exception:
        return ""


def evaluate(name, root, box, now, stale_s, no_file_after, ex=None):
    """-> dict(verdict, age_s, why). verdict in FRESH, DEAD, NO_FILE_DEAD, NO_FILE_WAITING."""
    folder, prefix = RECORDERS[name]
    day = time.strftime("%Y%m%d", ist(now))
    path = os.path.join(root, folder, box, "%s%s.db" % (prefix, day))
    status = {}
    try:
        with open(os.path.join(root, folder, box, "status.json"), encoding="utf-8") as f:
            status = json.load(f)
    except (OSError, ValueError):
        pass
    fw = file_write_time(path)
    lt = status_last_tick(status)
    if lt > now + 5:                      # future-dated last_tick would give a negative age = FRESH forever: not trusted
        lt = 0.0
    last = max(fw, lt)
    if ex is not None:                    # observation fields for the --csv dry-run log (auditor round 2)
        ex.update({"file_mtime": os.stat(path).st_mtime if os.path.exists(path) else 0.0, "wal_mtime": (os.stat(path + "-wal").st_mtime if os.path.exists(path + "-wal") else 0.0),
                   "last_tick_epoch": lt, "events_max": events_max(path, name)})
    if fw == 0.0:
        lt_now = ist(now)
        if lt_now.tm_hour * 60 + lt_now.tm_min >= hhmm(no_file_after) and not status.get("instruments"):
            return {"verdict": "NO_FILE_DEAD", "age_s": None,
                    "why": "no day file %s and instruments=0 after %s" % (os.path.basename(path), no_file_after)}
        return {"verdict": "NO_FILE_WAITING", "age_s": None, "why": "no day file yet"}
    age = now - last
    if age > stale_s:
        return {"verdict": "DEAD", "age_s": round(age, 1),
                "why": "last data %.0f s ago (limit %.0f s); file_write=%s last_tick=%s" % (
                    age, stale_s, time.strftime("%H:%M:%S", ist(fw)),
                    time.strftime("%H:%M:%S", ist(lt)) if lt else "n/a")}
    why = "last data %.1f s ago" % age
    if name in CONNS:
        t_q = time.time()
        cl = conn_last(path, CONNS[name], now - max(600.0, 4 * stale_s))
        if ex is not None:
            ex["frames"] = ";".join("%s=%s" % (c, ("%.0f" % t) if t else ("none_in_window" if t == 0.0 else "UNKNOWN")) for c, t in sorted(cl.items()))
            ex["query_ms"] = "%.0f" % ((time.time() - t_q) * 1000)
        dead = [("%s silent >= %.0f s (no row in window)" % (c, max(600.0, 4 * stale_s))) if t == 0.0 else "%s silent %.0f s" % (c, now - t)
                for c, t in sorted(cl.items()) if t is not None and (t == 0.0 or now - t > stale_s)]
        unk = [c for c, t in sorted(cl.items()) if t is None]
        if dead:
            multi = CONNS[name][1] is not None          # several sockets share one file: killing the container drops the healthy ones
            return {"verdict": "CONN_DEAD" if multi else "DEAD", "age_s": round(age, 1),
                    "why": "file is fresh but %s dead: %s (limit %.0f s)" % ("connection(s)" if multi else "frames", ", ".join(dead), stale_s)}
        if unk:
            why += "; connection check UNKNOWN for %s (not judged)" % ",".join(unk)
    return {"verdict": "FRESH", "age_s": round(age, 1), "why": why}


class Watch(object):
    def __init__(self, a):
        self.a = a
        self.kills = {}                       # container -> [epoch,...]
        os.makedirs(a.state_dir, exist_ok=True)
        self.escalated = {}
        self.rc_cache = {}

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
        if self.a.dry_run:                # dry run keeps EVERY verdict of EVERY cycle: no bound, no hourly suppression, no kill counting
            self.log("WARN", "DRYRUN %s: %s -> WOULD docker kill %s" % (name, why, name))
            return
        today = time.strftime("%Y%m%d", ist(now))
        recent = [t for t in self.kills.get(name, []) if time.strftime("%Y%m%d", ist(t)) == today]   # per IST DAY, not rolling hour
        if len(recent) >= self.a.max_kills:
            if now - self.escalated.get(name, 0) > 3600:      # re-armed: CRITICAL + file again at most once an hour
                self.escalated[name] = now
                self.log("CRITICAL", "%s killed %d times today and is still silent: NOT killing again. "
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

    def docker_ro(self, *args):
        """READ-ONLY docker query (inspect); runs even under --dry-run because it changes nothing. '' on any failure."""
        try:
            p = subprocess.run([self.a.docker] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True, timeout=15)
            return p.stdout.strip() if p.returncode == 0 else ""
        except Exception:
            return ""

    def csv_row(self, name, r, ex, now, action="none"):
        path = getattr(self.a, "csv", "")
        if not path:
            return
        import csv
        c = self.rc_cache.get(name)
        if c is None or now - c[0] >= 60:        # docker CLI is slow on these boxes under load: sample the restart counter once a minute
            c = (now, self.docker_ro("inspect", name, "--format", "{{.RestartCount}}|{{.State.StartedAt}}|{{.State.Running}}") if name in RECORDERS else "")
            self.rc_cache[name] = c
        rc = c[1]
        new = not os.path.exists(path)
        try:
            with open(path, "a", newline="") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(["ts_epoch", "timestamp_ist", "box", "recorder", "verdict", "action", "age_s", "last_tick_epoch", "frames_recv_ts", "query_ms",
                                "file_mtime", "wal_mtime", "events_max", "restart_count|started_at|running", "reason"])
                w.writerow(["%.0f" % now, time.strftime("%Y-%m-%d %H:%M:%S", ist(now)), self.a.box, name, r["verdict"], action, r["age_s"],
                            "%.0f" % ex.get("last_tick_epoch", 0), ex.get("frames", ""), ex.get("query_ms", ""), "%.0f" % ex.get("file_mtime", 0),
                            "%.0f" % ex.get("wal_mtime", 0), ex.get("events_max", ""), rc, r["why"]])
        except OSError:
            pass

    def alarm(self, name, why, now):
        """Alarm only (owner decision pending, both auditors: do not kill a container for one dead socket): CRITICAL log +
        ALARM file, at most once an hour per container."""
        key = "alarm:" + name
        if self.a.dry_run:
            self.log("CRITICAL", "DRYRUN %s: %s -> WOULD ALARM (--conn-action alarm)" % (name, why))
            return
        if now - self.escalated.get(key, 0) <= 3600:
            return
        self.escalated[key] = now
        self.log("CRITICAL", "%s: %s -> ALARM ONLY, no kill (--conn-action alarm)" % (name, why))
        try:
            with open(os.path.join(self.a.state_dir, "ALARM_%s.json" % name), "w") as f:
                json.dump({"container": name, "box": self.a.box, "at": now, "why": why}, f)
        except OSError:
            pass

    def once(self, now=None):
        now = time.time() if now is None else now
        if not in_session(now, self.a.session_start, self.a.session_end):
            self.log("INFO", "outside session window %s-%s: nothing to judge" % (self.a.session_start, self.a.session_end))
            return []
        results = []
        for name in sorted(RECORDERS):
            ex = {}
            r = evaluate(name, self.a.root, self.a.box, now, self.a.stale_s, self.a.no_file_after, ex)
            results.append((name, r))
            if r["verdict"] == "CONN_DEAD" and getattr(self.a, "conn_action", "alarm") != "kill":
                self.csv_row(name, r, ex, now, "would_alarm" if self.a.dry_run else "alarm")
                self.alarm(name, r["why"], now)
            elif r["verdict"] in ("DEAD", "NO_FILE_DEAD", "CONN_DEAD"):
                self.csv_row(name, r, ex, now, "would_kill" if self.a.dry_run else "kill_or_suppressed")
                self.kill(name, r["why"], now)
            else:
                self.csv_row(name, r, ex, now, "none")
                self.log("OK", "%s %s (%s)" % (name, r["verdict"], r["why"]))
        return results


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--box", required=True)
    p.add_argument("--docker", default=DEFAULT_DOCKER)
    p.add_argument("--stale-s", type=float, default=90.0)   # v2: 60 s was 5 s from a healthy 55 s gap (i5 upstox 14:24:57-14:25:52)
    p.add_argument("--session-start", default="09:16")
    p.add_argument("--session-end", default="15:30")
    p.add_argument("--no-file-after", default="09:20")
    p.add_argument("--interval", type=float, default=15.0)
    p.add_argument("--max-kills", type=int, default=3, help="kills per container per IST day")
    p.add_argument("--conn-action", choices=("alarm", "kill"), default="alarm",
                   help="what to do when ONE connection of a multi-socket recorder is silent while the file is fresh")
    p.add_argument("--restart-wait", type=float, default=10.0)
    p.add_argument("--state-dir", default="/volume1/docker/datapullers/_state/livewatch_host")   # v3: not /tmp (tmpfs on DSM: ESCALATE/ALARM files vanished on reboot)
    p.add_argument("--log", default="")
    p.add_argument("--csv", default="", help="append one row per recorder per pass (dry-run evidence log)")
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
    missing = [n for n, (f, _) in sorted(RECORDERS.items()) if not os.path.isdir(os.path.join(a.root, f, a.box))]
    if missing:      # fail closed (auditor defect 1): a wrong --box/--root or an unmounted volume must never read as "all recorders dead"
        w.log("CRITICAL", "REFUSING TO RUN: no folder under %s for box '%s' for: %s (wrong --box? volume not mounted?)" % (a.root, a.box, ", ".join(missing)))
        return 2
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
