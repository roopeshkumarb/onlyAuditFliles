#!/usr/bin/env python3
"""RECORD THE UPSTOX LIVE FEED EVERY SESSION, RAW - the evidence for "Upstox Plus only" (T-0808).

KUMAR 16-10-2026 01:34: "I said all blpro container must use upstox plus only but still I
see as fyers login". blpro's engine has NO Upstox live path today (survey 16-10-2026: login,
NIFTY feed, failsafe price check and the judge's chain are all Fyers). Switching the engine
blind on a session day is how wrong numbers get in. So this records Upstox's own live feed
beside the engine, every session, and tools/broker_consensus.py scores it against every
broker after the close. The engine switch is built on that proof.

WHAT: Upstox market data feed v3 (GET /v3/feed/market-data-feed/authorize -> a one-time
    wss URL; subscribe {"guid","method":"sub","data":{"mode":"full","instrumentKeys":[...]}}
    sent as BINARY). Replies are protobuf; they are stored RAW (zlib) with the receive
    time and decoded later - a wrong decoder can never cost a day.
INSTRUMENTS (MONTHLY default, CLAUDE.md): NIFTY 50 index, India VIX, the NIFTY monthly
    future, NIFTY monthly options ATM +/- UPSTOX_STRIKES (default 10) CE and PE. Upstox's
    NSE_FO key is the exchange token, the same id Dhan uses (measured 16-10-2026:
    NSE_FO|51316 = Dhan 51316 = NIFTY 27 OCT 26 22200 CE), so the monthly set comes from
    Dhan's public master exactly as dp_depthrec picks it.
WHERE: <DP_ROOT>/upstox_live/<box>/upstox_<YYYYMMDD>.db, status.json beside it.
WHEN: 09:00-15:35 GMT+5:30 weekdays. One socket. Read-only market data; places nothing.
"""
from __future__ import annotations

import json
import os
import queue
import shutil
import sqlite3
import sys
import threading
import time
import uuid
import zlib
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import dp_depthrec as DR  # noqa: E402  - the monthly picker and the Dhan master reader
import dp_recguard  # noqa: E402  - one socket at a time, silent-socket drop, restart reuse

IST = timezone(timedelta(hours=5, minutes=30))
DP_ROOT = os.environ.get("DP_ROOT", "/data")
BOX = (os.environ.get("BOX_NAME") or "unknown").lower()
OUT_DIR = os.path.join(DP_ROOT, "upstox_live", BOX)
STATUS = os.path.join(OUT_DIR, "status.json")
START, STOP = os.environ.get("UPSTOX_START", "09:00"), os.environ.get("UPSTOX_STOP", "15:35")
STRIKES = int(os.environ.get("UPSTOX_STRIKES", "10"))               # a declared choice
MIN_FREE_GB = float(os.environ.get("UPSTOX_MIN_FREE_GB", "50"))
# NEAREST WEEKLY (02-11-2026). OFF by default (0 = today's key list, unchanged). ON = set
# UPSTOX_WEEKLY_STRIKES >= 1: the monthly then uses UPSTOX_MONTHLY_STRIKES_WITH_WEEKLY and the
# whole list is capped at UPSTOX_MAX_KEYS (50, the full_d30 per-connection limit; counted over
# ALL keys incl. the 2 index keys, the conservative reading). 5 + 5 -> 2 + 1 + 22 + 22 = 47.
WEEKLY_STRIKES = int(os.environ.get("UPSTOX_WEEKLY_STRIKES", "0"))
MONTHLY_STRIKES_WITH_WEEKLY = int(os.environ.get("UPSTOX_MONTHLY_STRIKES_WITH_WEEKLY", "5"))
MAX_KEYS = int(os.environ.get("UPSTOX_MAX_KEYS", "50"))
AUTH_URL = "https://api.upstox.com/v3/feed/market-data-feed/authorize"
LTP_URL = "https://api.upstox.com/v2/market-quote/ltp"
INDEX_KEYS = ["NSE_INDEX|Nifty 50", "NSE_INDEX|India VIX"]
FLUSH_S = 2.0

SCHEMA = """
CREATE TABLE IF NOT EXISTS frames (recv_ts REAL NOT NULL, raw BLOB NOT NULL);
CREATE INDEX IF NOT EXISTS ix_frames_ts ON frames(recv_ts);
CREATE TABLE IF NOT EXISTS instruments (day TEXT, key TEXT, symbol TEXT, expiry TEXT,
                                        strike REAL, opt TEXT, spot_at_start REAL);
"""


def now():
    return datetime.now(IST)


def in_session(t=None) -> bool:
    """Same holiday-aware rule as dp_depthrec.in_session (auditor A3)."""
    t = t or now()
    if t.weekday() >= 5:
        return False
    try:
        import dp_calendar
        if dp_calendar.classify(t.date()) != dp_calendar.TRADING_DAY:
            return False
    except Exception:
        pass
    hm = t.hour * 60 + t.minute
    return DR._hm(START) <= hm < DR._hm(STOP)


def instrument_keys(rows, today, spot, n=STRIKES, weekly_n=None, monthly_n_with_weekly=None,
                    max_keys=None):
    """[(key, symbol, expiry, strike, opt)] - index, VIX, monthly future, ATM +/- n options.

    weekly_n == 0 (default): exactly the old list. weekly_n >= 1: the nearest weekly ATM +/-
    weekly_n is added and the monthly shrinks to monthly_n_with_weekly, the whole list capped
    at max_keys (farthest strikes dropped). Returns (keys, monthly_expiry) as before.
    """
    weekly_n = WEEKLY_STRIKES if weekly_n is None else weekly_n
    mw = MONTHLY_STRIKES_WITH_WEEKLY if monthly_n_with_weekly is None else monthly_n_with_weekly
    cap = MAX_KEYS if max_keys is None else max_keys
    fut, opts, exp = DR.nifty_monthly(rows, today)
    if not fut:
        return [], None
    wopts, wexp = DR.nifty_weekly(rows, today, exp) if weekly_n > 0 else ([], None)
    out = [(k, k.split("|")[1], None, None, None) for k in INDEX_KEYS]
    out.append(("NSE_FO|%s" % fut["SEM_SMST_SECURITY_ID"], fut["SEM_TRADING_SYMBOL"],
                exp.isoformat(), None, None))
    if not wopts:
        picked = [(o, exp) for o in DR.pick_strikes(opts, spot, n)]
    else:
        wn, mn2 = DR.window_sizes(wexp, exp, weekly_n, mw)      # monthly-expiry week: the expiring monthly gets the wide window
        picked = [(o, wexp) for o in DR.pick_strikes(wopts, spot, wn)]
        picked += [(o, exp) for o in DR.pick_strikes(opts, spot, mn2)]
        picked = DR.cap_by_distance(picked, spot, max(0, cap - len(out)))
    for o, x in picked:
        out.append(("NSE_FO|%s" % o["SEM_SMST_SECURITY_ID"], o["SEM_TRADING_SYMBOL"],
                    x.isoformat(), float(o["SEM_STRIKE_PRICE"]), o["SEM_OPTION_TYPE"]))
    return out, exp


# 16-10-2026 (T-0825): Upstox Plus gives 30 levels ("full_d30", up to 50 keys a connection).
# We record 43 F&O keys at 30 levels; the 2 index keys have no book and stay on "full".
# If Upstox closes a 30-level socket before any frame arrives, the day falls back to "full".
DEPTH_MODE = os.environ.get("UPSTOXREC_DEPTH_MODE", "full_d30")


def subscriptions(keys, depth_mode=DEPTH_MODE):
    """[(mode, keys)]: the index keys in 'full', every F&O key in depth_mode."""
    idx = [k for k in keys if k.startswith("NSE_INDEX|")]
    fo = [k for k in keys if not k.startswith("NSE_INDEX|")]
    return [(m, ks) for m, ks in (("full", idx), (depth_mode, fo)) if ks]


def subscribe_message(keys, mode="full") -> bytes:
    """Upstox v3 wants the subscription as a BINARY frame of JSON."""
    return json.dumps({"guid": uuid.uuid4().hex, "method": "sub",
                       "data": {"mode": mode, "instrumentKeys": list(keys)}}).encode()


def upstox_spot(token):
    import requests
    r = requests.get(LTP_URL, params={"instrument_key": INDEX_KEYS[0]}, timeout=20,
                     headers={"Authorization": "Bearer %s" % token, "Accept": "application/json"})
    r.raise_for_status()
    for v in (r.json().get("data") or {}).values():
        if v.get("last_price"):
            return float(v["last_price"])
    return None


def authorize(token) -> str:
    import requests
    r = requests.get(AUTH_URL, timeout=20, headers={"Authorization": "Bearer %s" % token,
                                                     "Accept": "application/json"})
    r.raise_for_status()
    d = r.json().get("data") or {}
    url = d.get("authorized_redirect_uri") or d.get("authorizedRedirectUri")
    if not url:
        raise RuntimeError("no authorized_redirect_uri in %s" % str(r.json())[:200])
    return url


class Recorder:
    def __init__(self):
        self.q = queue.Queue()
        self.st = {"box": BOX, "started": now().strftime("%d-%m-%Y %H:%M:%S GMT+5:30"),
                   "connected": False, "frames": 0, "bytes": 0, "errors": [],
                   "instruments": 0, "spot_at_start": None, "expiry": None, "file": None}
        self.day, self.keys = None, None

    def err(self, msg):
        self.st["errors"] = (self.st["errors"] + ["%s %s" % (now().strftime("%H:%M:%S"), msg)])[-20:]

    def day_file(self):
        return os.path.join(OUT_DIR, "upstox_%s.db" % now().strftime("%Y%m%d"))

    def on_frame(self, frame: bytes):
        self.st["frames"] += 1
        self.st["bytes"] += len(frame)
        self.st["last_frame"] = now().strftime("%H:%M:%S")
        self.q.put((time.time(), zlib.compress(frame, 6)))

    def writer(self, stop):
        con, path, buf, last = None, None, [], time.time()
        while not stop.is_set() or not self.q.empty():
            try:
                buf.append(self.q.get(timeout=0.5))
            except queue.Empty:
                pass
            if buf and time.time() - last >= FLUSH_S:
                p = self.day_file()
                if p != path:
                    if con:
                        con.close()
                    con = sqlite3.connect(p, timeout=30)
                    con.execute("PRAGMA journal_mode=WAL")
                    con.executescript(SCHEMA)
                    path, self.st["file"] = p, os.path.basename(p)
                try:
                    con.executemany("INSERT INTO frames VALUES (?,?)", buf)
                    con.commit()
                    buf = []
                except sqlite3.Error as e:
                    self.err("write: %s" % e)
                last = time.time()

    def stored_plan(self, today) -> bool:
        """Reuse this morning's keys from today's day file after a restart (T-0849)."""
        rows = dp_recguard.stored_rows(
            self.day_file(), "SELECT key, expiry, spot_at_start FROM instruments WHERE day=? "
            "ORDER BY rowid", (today.isoformat(),))
        if not rows:
            return False
        exp = next((r[1] for r in rows if r[1]), None)
        self.st.update({"spot_at_start": rows[0][2], "expiry": exp, "instruments": len(rows),
                        "plan": "reused today's list from the day file (restart-safe)"})
        self.day, self.keys = today, [r[0] for r in rows]
        return True

    def plan_today(self, token):
        today = now().date()
        if self.stored_plan(today):
            return
        spot = upstox_spot(token)
        if spot is None:
            raise RuntimeError("no NIFTY spot from Upstox LTP")
        keys, exp = instrument_keys(DR.load_master(today), today, spot)
        if not keys:
            raise RuntimeError("no NIFTY monthly contracts in the master")
        os.makedirs(OUT_DIR, exist_ok=True)
        con = sqlite3.connect(self.day_file(), timeout=30)
        con.executescript(SCHEMA)
        con.execute("DELETE FROM instruments WHERE day=?", (today.isoformat(),))
        con.executemany("INSERT INTO instruments VALUES (?,?,?,?,?,?,?)",
                        [(today.isoformat(),) + k + (spot,) for k in keys])
        con.commit()
        con.close()
        self.st.update({"spot_at_start": spot, "expiry": exp.isoformat(), "instruments": len(keys),
                        "plan": "picked at %s from spot %s" % (now().strftime("%H:%M:%S"), spot)})
        self.day, self.keys = today, [k[0] for k in keys]

    def write_status(self):
        try:
            self.st["at"] = now().strftime("%d-%m-%Y %H:%M:%S GMT+5:30")
            self.st["in_session"] = in_session()
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(STATUS + ".tmp", "w") as f:
                json.dump(self.st, f, indent=1)
            os.replace(STATUS + ".tmp", STATUS)
        except Exception as e:
            print("status write failed: %s" % e, flush=True)


def run():
    from autobahn.twisted.websocket import (WebSocketClientFactory,
                                            WebSocketClientProtocol, connectWS)
    from twisted.internet import reactor, ssl, task
    import dp_tokens

    rec = Recorder()
    stop = threading.Event()
    threading.Thread(target=rec.writer, args=(stop,), daemon=True).start()
    live = {}
    guard = dp_recguard.SocketGuard()

    class P(WebSocketClientProtocol):
        def onOpen(self):
            live["p"] = self
            guard.opened("p")
            dp_recguard.log_event(rec.day_file(), "upstox", "open")
            rec.st["connected"] = True
            rec.st["since"] = now().strftime("%H:%M:%S")
            rec.st["frames_at_open"] = rec.st["frames"]
            mode = "full" if rec.st.get("d30_refused") == str(now().date()) else DEPTH_MODE
            rec.st["depth_mode"] = mode
            for m, ks in subscriptions(rec.keys, mode):
                self.sendMessage(subscribe_message(ks, m), isBinary=True)

        def onMessage(self, payload, isBinary):
            guard.frame("p")
            if isBinary:
                rec.on_frame(payload)
            else:
                rec.err("text: %s" % payload[:200])

        def onClose(self, wasClean, code, reason):
            if live.get("p") is self:
                live.pop("p", None)
            guard.closed("p", "%s %s" % (code, reason))
            dp_recguard.log_event(rec.day_file(), "upstox", "closed %s %s" % (code, reason))
            if rec.st.get("depth_mode") != "full" and \
                    rec.st["frames"] == rec.st.get("frames_at_open", -1):
                rec.st["d30_refused"] = str(now().date())
                rec.err("%s closed before any frame - falling back to 'full' today"
                        % rec.st.get("depth_mode"))
            rec.st.update({"connected": False, "closed": now().strftime("%H:%M:%S"),
                           "close": "%s %s" % (code, reason)})

    class Factory(WebSocketClientFactory):
        def clientConnectionFailed(self, connector, reason):
            guard.failed("p", str(getattr(reason, "value", reason))[:200])
            rec.err("connect failed: %s" % getattr(reason, "value", reason))

    def loop():
        try:
            free = shutil.disk_usage(DP_ROOT).free / 1e9
            want = in_session() and free >= MIN_FREE_GB
            quiet = guard.stalled("p") if want else None
            if quiet is not None and "p" in live:
                rec.err("SILENT %.0fs while connected - dropping it" % quiet)
                dp_recguard.log_event(rec.day_file(), "upstox", "silent %.0fs - dropped" % quiet)
                live["p"].dropConnection(abort=True)
            # ONE SOCKET AT A TIME: never a second while the first is still in its handshake.
            if want and guard.may_open("p"):
                token, _st = dp_tokens.get_token("upstox")
                if not token:
                    rec.err("no Upstox token in the shared store")
                else:
                    if rec.day != now().date() or not rec.keys:
                        rec.plan_today(token)
                    url = authorize(token)          # one-time URL, fetched per connect
                    guard.opening("p")
                    f = Factory(url)
                    f.protocol = P
                    connectWS(f, ssl.ClientContextFactory())
            elif not want and "p" in live:
                live["p"].sendClose()
        except Exception as e:
            rec.err("loop: %s: %s" % (type(e).__name__, e))
        rec.st["guard"] = guard.snapshot()
        rec.write_status()

    task.LoopingCall(loop).start(30, now=True)
    print("upstoxrec on %s: %s-%s GMT+5:30, monthly ATM +/- %d, weekly +/- %d (0 = off), raw to %s"
          % (BOX, START, STOP, STRIKES, WEEKLY_STRIKES, OUT_DIR), flush=True)
    reactor.run()
    stop.set()


if __name__ == "__main__":
    run()
