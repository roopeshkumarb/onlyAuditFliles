#!/usr/bin/env python3
"""RECORD DHAN 20-LEVEL AND 200-LEVEL MARKET DEPTH EVERY SESSION (T-0745).

KUMAR 15-10-2026: buy the depth history, or record it. No retail vendor sells NIFTY option
order-book history (docs/research/BUY_DATA_OPTIONS_151026-2300.md); a session not recorded
is lost for good. Kite's 5 levels are already recorded by dp_tickrec. This adds the deep
book Dhan streams with the Data API we already pay for.

WHAT (Dhan "Full Market Depth", dhanhq.co/docs/v2/full-market-depth, read 16-10-2026):
    20 level  wss://depth-api-feed.dhan.co/twentydepth   up to 50 instruments / connection
    200 level wss://full-depth-api.dhan.co/twohundreddepth  1 instrument / connection
    subscribe {"RequestCode": 23, ...}; replies are binary: a 12-byte header (int16 length,
    byte response code 41 bid / 51 ask / 50 disconnect, byte segment, int32 security id,
    uint32 sequence or row count) then 16-byte levels (float64 price, uint32 qty,
    uint32 orders), several messages stacked in one frame.
INSTRUMENTS, declared choices (env), MONTHLY contract by default (CLAUDE.md):
    20 level : NIFTY monthly options, ATM +/- DEPTH_STRIKES (default 12), CE and PE = 50
    200 level: the NIFTY monthly future
    from Dhan's public scrip master (SEM_EXPIRY_FLAG 'M'), read once each morning; ATM from
    Dhan's LTP of the NIFTY 50 index at the start, fixed for the day and written in status.
RAW, PARSE LATER (Kumar, T-0782): every websocket frame is stored zlib-compressed as it
    came, with the receive time. Only the headers are read live, to count and to catch a
    disconnect code. A wrong decoder can then be fixed later without losing a day.
WHERE: <DP_ROOT>/depth/<box>/depth_<YYYYMMDD>.db, status.json beside it.
WHEN: 09:00-15:35 GMT+5:30 on weekdays.
SAFETY: Dhan allows 5 websockets per account and a sixth DISCONNECTS THE OLDEST (code 805).
    This opens two. On 805/806/808 it stops for the day and says why - it never reconnects
    in a loop that could knock another connection off. 807/809 (token) wait for a new
    token. Stops writing if the disk has less than DEPTH_MIN_FREE_GB free.

ADVISORY ONLY. This reads market data. It places nothing.
"""
from __future__ import annotations

import csv
import json
import os
import queue
import shutil
import sqlite3
import struct
import sys
import threading
import time
import zlib
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import dp_recguard  # noqa: E402  - one socket per name, silent-socket drop, restart reuse

IST = timezone(timedelta(hours=5, minutes=30))
DP_ROOT = os.environ.get("DP_ROOT", "/data")
BOX = (os.environ.get("BOX_NAME") or "unknown").lower()
OUT_DIR = os.path.join(DP_ROOT, "depth", BOX)
STATUS = os.path.join(OUT_DIR, "status.json")
START, STOP = os.environ.get("DEPTH_START", "09:00"), os.environ.get("DEPTH_STOP", "15:35")
DEPTH_STRIKES = int(os.environ.get("DEPTH_STRIKES", "12"))          # a declared choice
# NEAREST WEEKLY (02-11-2026). OFF by default: 0 = today's behaviour, byte for byte.
# ON = set DEPTH_WEEKLY_STRIKES >= 1. The 50 d20 slots are then SPLIT, never added to:
# weekly ATM +/- DEPTH_WEEKLY_STRIKES and monthly ATM +/- DEPTH_MONTHLY_STRIKES_WITH_WEEKLY.
# 2 x (2n+1) options per side-pair: 6 -> 26 weekly, 5 -> 22 monthly = 48 (<= D20_MAX).
DEPTH_WEEKLY_STRIKES = int(os.environ.get("DEPTH_WEEKLY_STRIKES", "0"))
DEPTH_MONTHLY_STRIKES_WITH_WEEKLY = int(os.environ.get("DEPTH_MONTHLY_STRIKES_WITH_WEEKLY", "5"))
D20_MAX = 50                      # Dhan: 50 instruments per 20-level connection (a limit, not a choice)
MIN_FREE_GB = float(os.environ.get("DEPTH_MIN_FREE_GB", "50"))      # a declared choice
SCRIP_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
LTP_URL = "https://api.dhan.co/v2/marketfeed/ltp"
URL20 = "wss://depth-api-feed.dhan.co/twentydepth?token=%s&clientId=%s&authType=2"
URL200 = "wss://full-depth-api.dhan.co/twohundreddepth?token=%s&clientId=%s&authType=2"
NIFTY_INDEX_ID = 13                                                  # Dhan IDX_I id
FLUSH_S = 2.0
STOP_FOR_DAY = {805: "connection limit exceeded - a 6th socket kicks the OLDEST off",
                806: "Data APIs not subscribed", 808: "authentication failed (client id)"}
WAIT_TOKEN = {807: "access token expired", 809: "access token invalid"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS frames (
    recv_ts REAL NOT NULL,          -- epoch seconds when the frame arrived
    conn    TEXT NOT NULL,          -- d20 | d200
    n_msgs  INTEGER,                -- messages found in the frame by their length field
    raw     BLOB NOT NULL           -- zlib(frame bytes), exactly as received
);
CREATE INDEX IF NOT EXISTS ix_frames_ts ON frames(recv_ts);
CREATE TABLE IF NOT EXISTS instruments (
    day TEXT, conn TEXT, security_id TEXT, symbol TEXT, expiry TEXT, strike REAL,
    opt TEXT, spot_at_start REAL
);
"""


def now():
    return datetime.now(IST)


def _hm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def in_session(t=None) -> bool:
    """Weekday AND not a known NSE holiday (auditor A3, 04-11-2026: before this fix the
    recorder opened Dhan sockets and planned a strike list on a holiday it had no ticks for,
    wasting part of the 5-socket budget; dp_tickrec.py already does this check, mirrored here)."""
    t = t or now()
    if t.weekday() >= 5:
        return False
    try:
        import dp_calendar
        if dp_calendar.classify(t.date()) != dp_calendar.TRADING_DAY:
            return False
    except Exception:          # no dp_calendar / unreadable holiday file: fall back to weekday-only, never crash the recorder
        pass
    return _hm(START) <= t.hour * 60 + t.minute < _hm(STOP)


# ── instruments ────────────────────────────────────────────────────────────────
def nifty_monthly(rows, today: date):
    """From scrip-master rows: (future, options, expiry) of the nearest NIFTY MONTHLY expiry."""
    futs, opts = {}, {}
    for r in rows:
        if r.get("SEM_EXM_EXCH_ID") != "NSE" or r.get("SEM_EXPIRY_FLAG") != "M":
            continue
        sym = r.get("SEM_TRADING_SYMBOL") or ""
        if sym.split("-")[0] != "NIFTY":
            continue
        try:
            exp = datetime.strptime(r["SEM_EXPIRY_DATE"][:10], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if exp < today:
            continue
        kind = r.get("SEM_INSTRUMENT_NAME")
        if kind == "FUTIDX":
            futs[exp] = r
        elif kind == "OPTIDX":
            opts.setdefault(exp, []).append(r)
    common = sorted(set(futs) & set(opts))
    if not common:
        return None, [], None
    exp = common[0]
    return futs[exp], opts[exp], exp


def nifty_weekly(rows, today: date, monthly_exp=None):
    """(options, expiry) of the nearest NIFTY WEEKLY expiry (SEM_EXPIRY_FLAG 'W'), else ([], None).

    A date equal to monthly_exp is skipped so one contract is never subscribed twice.
    Dhan lists no weekly future, so only options are returned.
    """
    opts = {}
    for r in rows:
        if r.get("SEM_EXM_EXCH_ID") != "NSE" or r.get("SEM_EXPIRY_FLAG") != "W":
            continue
        if (r.get("SEM_TRADING_SYMBOL") or "").split("-")[0] != "NIFTY":
            continue
        if r.get("SEM_INSTRUMENT_NAME") != "OPTIDX":
            continue
        try:
            exp = datetime.strptime(r["SEM_EXPIRY_DATE"][:10], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if exp < today or exp == monthly_exp:
            continue
        opts.setdefault(exp, []).append(r)
    if not opts:
        return [], None
    exp = min(opts)
    return opts[exp], exp


def window_sizes(wexp, mexp, weekly_n: int, monthly_n_with_weekly: int):
    """(n for the weekly list, n for the monthly list). Normally the nearer contract is the weekly and gets the wide window.
    In the monthly-expiry week nifty_weekly skips the date equal to the monthly and returns NEXT week's weekly, so the EXPIRING
    monthly is the nearer contract: it must get the wide window and next week's weekly the narrow one (auditor A1, 03-11-2026)."""
    if wexp is not None and mexp is not None and wexp > mexp:
        return monthly_n_with_weekly, weekly_n
    return weekly_n, monthly_n_with_weekly


def cap_by_distance(picked, spot: float, cap: int):
    """picked = [(option_row, expiry)]. Over cap: drop the strikes farthest from spot."""
    if len(picked) <= cap:
        return picked
    keep = sorted(range(len(picked)),
                  key=lambda i: (abs(float(picked[i][0]["SEM_STRIKE_PRICE"]) - spot), i))[:cap]
    return [picked[i] for i in sorted(keep)]


def select_d20(rows, today: date, spot: float, weekly_n=None, monthly_n_with_weekly=None,
               monthly_n=None):
    """The day's 20-level options: (future_row, monthly_exp, weekly_exp, [(option_row, expiry)]).

    weekly_n == 0 (the default): EXACTLY the old list - monthly ATM +/- DEPTH_STRIKES, first 50.
    weekly_n >= 1 : weekly ATM +/- weekly_n, then monthly ATM +/- monthly_n_with_weekly, both
    inside D20_MAX (farthest strikes dropped if ever over). If the master holds no weekly the
    monthly keeps its full DEPTH_STRIKES (nothing is lost by switching on).
    """
    weekly_n = DEPTH_WEEKLY_STRIKES if weekly_n is None else weekly_n
    mw = DEPTH_MONTHLY_STRIKES_WITH_WEEKLY if monthly_n_with_weekly is None else monthly_n_with_weekly
    mn = DEPTH_STRIKES if monthly_n is None else monthly_n
    fut, opts, exp = nifty_monthly(rows, today)
    if not fut:
        return None, None, None, []
    wopts, wexp = nifty_weekly(rows, today, exp) if weekly_n > 0 else ([], None)
    if not wopts:
        return fut, exp, None, [(o, exp) for o in pick_strikes(opts, spot, mn)[:D20_MAX]]
    wn, mn2 = window_sizes(wexp, exp, weekly_n, mw)
    picked = [(o, wexp) for o in pick_strikes(wopts, spot, wn)]
    picked += [(o, exp) for o in pick_strikes(opts, spot, mn2)]
    return fut, exp, wexp, cap_by_distance(picked, spot, D20_MAX)


def pick_strikes(options, spot: float, n: int):
    """ATM +/- n strikes, CE and PE. ATM = the listed strike nearest the spot."""
    strikes = sorted({float(o["SEM_STRIKE_PRICE"]) for o in options})
    if not strikes:
        return []
    atm = min(strikes, key=lambda k: abs(k - spot))
    i = strikes.index(atm)
    keep = set(strikes[max(0, i - n): i + n + 1])
    out = [o for o in options if float(o["SEM_STRIKE_PRICE"]) in keep
           and o.get("SEM_OPTION_TYPE") in ("CE", "PE")]
    return sorted(out, key=lambda o: (float(o["SEM_STRIKE_PRICE"]), o["SEM_OPTION_TYPE"]))


def load_master(day: date):
    import requests
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "scrip_master_%s.csv" % day.strftime("%Y%m%d"))
    if not os.path.exists(path):
        r = requests.get(SCRIP_URL, timeout=180)
        r.raise_for_status()
        with open(path + ".tmp", "wb") as f:
            f.write(r.content)
        os.replace(path + ".tmp", path)
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def nifty_spot(token: str, client: str):
    import requests
    r = requests.post(LTP_URL, json={"IDX_I": [NIFTY_INDEX_ID]}, timeout=20,
                      headers={"access-token": token, "client-id": client,
                               "Content-Type": "application/json"})
    r.raise_for_status()
    d = (r.json().get("data") or {}).get("IDX_I") or {}
    v = (d.get(str(NIFTY_INDEX_ID)) or {}).get("last_price")
    return float(v) if v else None


# ── frames ─────────────────────────────────────────────────────────────────────
def split_messages(frame: bytes):
    """[(response_code, segment, security_id, length)] by each message's own length."""
    out, i = [], 0
    while i + 12 <= len(frame):
        n, code, seg, sid = struct.unpack_from("<hBBi", frame, i)
        if n < 12:
            break
        out.append((code, seg, sid, n))
        i += n
    return out


def disconnect_code(frame: bytes):
    """Dhan's reason code from a disconnect message (response code 50), else None."""
    for code, _seg, _sid, n in split_messages(frame):
        if code == 50 and len(frame) >= 14:
            return struct.unpack_from("<h", frame, 12)[0]
    return None


def decode_frame(frame: bytes) -> list:
    """[(security_id, side, level, price, qty, orders)] from one stored frame (T-0830).

    Dhan's documented layout, as split_messages reads it: each message is a 12-byte header
    (int16 length, byte code 41 bid / 51 ask, byte segment, int32 security id, uint32
    sequence or row count) then (length - 12) / 16 levels of float64 price, uint32 qty,
    uint32 orders. Level 1 is the best price. Any other code (50 disconnect) is skipped.
    """
    out, i = [], 0
    while i + 12 <= len(frame):
        n, code, _seg, sid = struct.unpack_from("<hBBi", frame, i)
        if n < 12 or i + n > len(frame):
            break
        if code in (41, 51):
            side = "bid" if code == 41 else "ask"
            for k in range((n - 12) // 16):
                price, qty, orders = struct.unpack_from("<dII", frame, i + 12 + 16 * k)
                out.append((sid, side, k + 1, price, qty, orders))
        i += n
    return out


# ── recorder ───────────────────────────────────────────────────────────────────
class Recorder:
    def __init__(self):
        self.q = queue.Queue()
        self.st = {"box": BOX, "started": now().strftime("%d-%m-%Y %H:%M:%S GMT+5:30"),
                   "conns": {}, "frames": 0, "bytes": 0, "codes": {}, "errors": [],
                   "stopped_for_day": None, "instruments": 0, "spot_at_start": None,
                   "expiry": None, "file": None, "disk_free_gb": None}
        self.day = None
        self.stop_day = None
        self.bad_token = None          # fingerprint of a token Dhan refused (807/809)
        self.token_fp = None

    def err(self, msg):
        e = "%s %s" % (now().strftime("%H:%M:%S"), msg)
        self.st["errors"] = (self.st["errors"] + [e])[-20:]

    def day_file(self):
        return os.path.join(OUT_DIR, "depth_%s.db" % now().strftime("%Y%m%d"))

    def on_frame(self, conn, frame: bytes):
        msgs = split_messages(frame)
        for code, _s, _i, _n in msgs:
            self.st["codes"][str(code)] = self.st["codes"].get(str(code), 0) + 1
        dc = disconnect_code(frame)
        if dc is not None:
            self.on_disconnect(conn, dc)
        self.st["frames"] += 1
        self.st["bytes"] += len(frame)
        c = self.st["conns"].setdefault(conn, {})
        c["last_frame"] = now().strftime("%H:%M:%S")
        self.q.put((time.time(), conn, len(msgs), zlib.compress(frame, 6)))

    def on_disconnect(self, conn, code):
        why = STOP_FOR_DAY.get(code) or WAIT_TOKEN.get(code) or "code %s" % code
        self.err("%s DISCONNECT %s: %s" % (conn, code, why))
        if code in STOP_FOR_DAY:
            self.stop_day = now().date()
            self.st["stopped_for_day"] = "%s: %s" % (code, why)
        elif code in WAIT_TOKEN:
            self.bad_token = self.token_fp
            self.st["waiting_for_new_token"] = why

    def writer(self, stop: threading.Event):
        con, path, buf, last = None, None, [], time.time()
        while not stop.is_set() or not self.q.empty():
            try:
                buf.append(self.q.get(timeout=0.5))
            except queue.Empty:
                pass
            if buf and (time.time() - last >= FLUSH_S):
                p = self.day_file()
                if p != path:
                    if con:
                        con.close()
                    con = sqlite3.connect(p, timeout=30)
                    con.execute("PRAGMA journal_mode=WAL")
                    con.executescript(SCHEMA)
                    path = p
                    self.st["file"] = os.path.basename(p)
                try:
                    con.executemany("INSERT INTO frames VALUES (?,?,?,?)", buf)
                    con.commit()
                    buf = []
                except sqlite3.Error as e:
                    self.err("write: %s" % e)
                last = time.time()

    def write_status(self):
        try:
            free = shutil.disk_usage(DP_ROOT).free / 1e9
            self.st["disk_free_gb"] = round(free, 1)
            self.st["at"] = now().strftime("%d-%m-%Y %H:%M:%S GMT+5:30")
            self.st["in_session"] = in_session()
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(STATUS + ".tmp", "w") as f:
                json.dump(self.st, f, indent=1)
            os.replace(STATUS + ".tmp", STATUS)
        except Exception as e:
            print("status write failed: %s" % e, flush=True)

    def stored_plan(self, today):
        """This morning's list from today's day file - (sub20, sub200) - or None.

        A RESTART MUST NOT CHANGE THE DAY'S INSTRUMENTS (T-0849). Before 16-10-2026 a
        restart deleted the morning's list and re-picked ATM from the spot at restart time,
        so one day file held two strike sets and lost the record of the first.
        """
        rows = dp_recguard.stored_rows(
            self.day_file(), "SELECT conn, security_id, symbol, expiry, spot_at_start "
            "FROM instruments WHERE day=? ORDER BY rowid", (today.isoformat(),))
        fut = [r for r in rows if r[0] == "d200"]
        d20 = [r for r in rows if r[0] == "d20"]
        if not fut or not d20:
            return None
        self.st.update({"spot_at_start": fut[0][4], "expiry": fut[0][3],
                        "instruments": len(d20) + 1, "future": fut[0][2],
                        "plan": "reused today's list from the day file (restart-safe)"})
        return subscriptions([r[1] for r in d20], fut[0][1])

    def plan_today(self, token, client):
        """The day's instruments, recorded in the day file as well as in status."""
        today = now().date()
        again = self.stored_plan(today)
        if again is not None:
            return again
        rows_m = load_master(today)
        fut, _o, exp = nifty_monthly(rows_m, today)
        if not fut:
            raise RuntimeError("no NIFTY monthly future+options in the Dhan master")
        spot = nifty_spot(token, client)
        if spot is None:
            raise RuntimeError("no NIFTY spot from Dhan LTP - ATM cannot be placed")
        _f, _e, wexp, chosen = select_d20(rows_m, today, spot)
        picked = [o for o, _x in chosen]
        self.st.update({"spot_at_start": spot, "expiry": exp.isoformat(),
                        "expiry_weekly": wexp.isoformat() if wexp else None,
                        "instruments": len(picked) + 1,
                        "future": fut["SEM_TRADING_SYMBOL"]})
        con = sqlite3.connect(self.day_file(), timeout=30)
        con.executescript(SCHEMA)
        con.execute("DELETE FROM instruments WHERE day=?", (today.isoformat(),))
        rows = [(today.isoformat(), "d200", fut["SEM_SMST_SECURITY_ID"],
                 fut["SEM_TRADING_SYMBOL"], exp.isoformat(), None, None, spot)]
        rows += [(today.isoformat(), "d20", o["SEM_SMST_SECURITY_ID"], o["SEM_TRADING_SYMBOL"],
                  x.isoformat(), float(o["SEM_STRIKE_PRICE"]), o["SEM_OPTION_TYPE"], spot)
                 for o, x in chosen]
        con.executemany("INSERT INTO instruments VALUES (?,?,?,?,?,?,?,?)", rows)
        con.commit()
        con.close()
        self.st["plan"] = "picked at %s from spot %s" % (now().strftime("%H:%M:%S"), spot)
        return subscriptions([o["SEM_SMST_SECURITY_ID"] for o in picked],
                             fut["SEM_SMST_SECURITY_ID"])


def subscriptions(d20_ids, fut_id):
    """(sub20, sub200) request bodies for Dhan's 20-level and 200-level sockets."""
    sub20 = {"RequestCode": 23, "InstrumentCount": len(d20_ids),
             "InstrumentList": [{"ExchangeSegment": "NSE_FNO", "SecurityId": str(i)}
                                for i in d20_ids]}
    sub200 = {"RequestCode": 23, "ExchangeSegment": "NSE_FNO", "SecurityId": str(fut_id)}
    return sub20, sub200


def run():
    """Twisted reactor for ever; a 30 s loop opens the sockets in session, closes after."""
    from autobahn.twisted.websocket import (WebSocketClientFactory,
                                            WebSocketClientProtocol, connectWS)
    from twisted.internet import reactor, ssl, task
    import dp_tokens

    rec = Recorder()
    stop = threading.Event()
    threading.Thread(target=rec.writer, args=(stop,), daemon=True).start()
    live = {}                                    # conn -> protocol
    guard = dp_recguard.SocketGuard()

    def make(conn, sub):
        class P(WebSocketClientProtocol):
            def onOpen(self):
                live[conn] = self
                guard.opened(conn)
                rec.st["conns"][conn] = {"connected": True,
                                         "since": now().strftime("%H:%M:%S")}
                dp_recguard.log_event(rec.day_file(), conn, "open")
                self.sendMessage(json.dumps(sub).encode("utf-8"), isBinary=False)

            def onMessage(self, payload, isBinary):
                guard.frame(conn)
                if isBinary:
                    rec.on_frame(conn, payload)
                else:
                    rec.err("%s text: %s" % (conn, payload[:200]))

            def onClose(self, wasClean, code, reason):
                if live.get(conn) is self:
                    live.pop(conn, None)
                guard.closed(conn, "%s %s" % (code, reason))
                c = rec.st["conns"].setdefault(conn, {})
                c.update({"connected": False, "closed": now().strftime("%H:%M:%S"),
                          "close": "%s %s" % (code, reason)})
                dp_recguard.log_event(rec.day_file(), conn, "closed %s %s" % (code, reason))
        return P

    class Factory(WebSocketClientFactory):
        conn = None

        def clientConnectionFailed(self, connector, reason):
            guard.failed(self.conn, str(getattr(reason, "value", reason))[:200])
            rec.err("%s connect failed: %s" % (self.conn, getattr(reason, "value", reason)))

    def open_conn(conn, url, sub):
        guard.opening(conn)
        f = Factory(url)
        f.conn = conn
        f.protocol = make(conn, sub)
        connectWS(f, ssl.ClientContextFactory())

    def loop():
        try:
            today = now().date()
            free = shutil.disk_usage(DP_ROOT).free / 1e9
            want = (in_session() and rec.stop_day != today and free >= MIN_FREE_GB)
            if free < MIN_FREE_GB:
                rec.st["paused"] = "disk free %.0f GB below %.0f GB" % (free, MIN_FREE_GB)
            if want:
                for conn, p in list(live.items()):
                    quiet = guard.stalled(conn)
                    if quiet is not None:
                        # A socket that stays "connected" but sends nothing stores
                        # nothing - drop it, the next pass opens a fresh one.
                        rec.err("%s SILENT %.0fs while connected - dropping it" % (conn, quiet))
                        dp_recguard.log_event(rec.day_file(), conn, "silent %.0fs - dropped"
                                              % quiet)
                        p.dropConnection(abort=True)
            if want and (guard.may_open("d20") or guard.may_open("d200")):
                token, _st = dp_tokens.get_token("dhan")
                client = str(dp_tokens.get_pull_fields("dhan").get("client_id") or "")
                import hashlib
                rec.token_fp = hashlib.sha1((token or "").encode()).hexdigest()[:10]
                if not token or not client:
                    rec.err("no Dhan token/client id in the shared store")
                elif rec.bad_token and rec.token_fp == rec.bad_token:
                    pass                      # Dhan refused this token: wait for a new one
                else:
                    rec.st.pop("waiting_for_new_token", None)
                    if rec.day != today or not rec.st.get("_subs"):
                        rec.st["_subs"] = rec.plan_today(token, client)
                        rec.day = today
                    sub20, sub200 = rec.st["_subs"]
                    # ONE SOCKET PER NAME, EVER: never a second while one is still in its
                    # handshake. Dhan's 6th socket kicks the OLDEST off (805).
                    if guard.may_open("d20"):
                        open_conn("d20", URL20 % (token, client), sub20)
                    if guard.may_open("d200"):
                        open_conn("d200", URL200 % (token, client), sub200)
            elif not want:
                for p in list(live.values()):
                    p.sendMessage(json.dumps({"RequestCode": 12}).encode(), isBinary=False)
                    p.sendClose()
        except Exception as e:
            rec.err("loop: %s: %s" % (type(e).__name__, e))
        _status(rec)

    def _status(r):
        subs = r.st.pop("_subs", None)
        r.st["guard"] = guard.snapshot()
        r.write_status()
        if subs is not None:
            r.st["_subs"] = subs

    task.LoopingCall(loop).start(30, now=True)
    print("depthrec on %s: session %s-%s GMT+5:30, ATM +/- %d monthly, weekly +/- %d "
          "(0 = off), raw frames to %s"
          % (BOX, START, STOP, DEPTH_STRIKES, DEPTH_WEEKLY_STRIKES, OUT_DIR), flush=True)
    reactor.run()
    stop.set()


if __name__ == "__main__":
    run()
