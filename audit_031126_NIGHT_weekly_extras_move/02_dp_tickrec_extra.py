#!/usr/bin/env python3
"""RECORD LIVE TICKS EVERY SESSION - so tick history exists from today on.

KUMAR 15-10-2026: "live ticks can be downlaoded daily then why you failed." He is right.
No broker of his SELLS old ticks, but every one of them STREAMS live ticks; a session
that is not recorded is lost for good. This records it.

WHAT (Kite WebSocket, MODE_FULL - Kite's own field list, per instrument, per tick):
    exchange timestamp, last trade time, last price, last traded quantity, average
    traded price, volume, total buy qty, total sell qty, OI, OI day high, OI day low,
    day open/high/low/close, and MARKET DEPTH: best 5 bids and 5 asks, each with
    price, quantity and number of orders.
INSTRUMENTS (refreshed every morning from Kite's instrument list):
    NIFTY 50 index, INDIA VIX, NIFTY near + next futures, NIFTY options of the near
    MONTHLY expiry (ATM +/- MONTHLY_STRIKES) and of the NEAREST expiry (ATM +/- NEAR_STRIKES),
    CE and PE.
WHERE: <DP_ROOT>/ticks/<box>/ticks_<YYYYMMDD>.db, one file per day per box. Both NAS boxes
    record independently, so a restart on one is covered by the other (Kumar: "even if one
    puller is restarted the other must cover that puller gap").
WHEN: 09:00-15:35 GMT+5:30 on trading days; the websocket reconnects by itself.
WRITES: batched, one commit every FLUSH_S seconds (per-row commits cost ~100x the disk,
    measured 14-10-2026).

ADVISORY ONLY. This reads market data. It places nothing.
"""
from __future__ import annotations

import json
import os
import queue
import sqlite3
import sys
import threading
import time
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

IST = timezone(timedelta(hours=5, minutes=30))
DP_ROOT = os.environ.get("DP_ROOT", "/data")
BOX = (os.environ.get("BOX_NAME") or "unknown").lower()
OUT_DIR = os.path.join(DP_ROOT, "ticks", BOX)
STATUS = os.path.join(OUT_DIR, "status.json")
START, STOP = os.environ.get("TICK_START", "09:00"), os.environ.get("TICK_STOP", "15:35")
MONTHLY_STRIKES = int(os.environ.get("TICK_MONTHLY_STRIKES", "20"))   # a declared choice
NEAR_STRIKES = int(os.environ.get("TICK_NEAR_STRIKES", "15"))         # a declared choice
FLUSH_S = 2.0
NIFTY_INDEX, INDIA_VIX = 256265, 264969          # Kite instrument tokens (NSE indices)
# T-0849, 16-10-2026: a SILENT SOCKET MUST NOT LOOK CONNECTED. KiteTicker reconnects by
# itself, but when it gives up (on_noreconnect) or the socket stays open and sends nothing,
# the loop below used to sit in the session until 15:35 storing nothing. Kite's reactor
# cannot be restarted in-process, so the cure is the same one used at the close: flush and
# exit, and Docker's restart policy brings a fresh process with a fresh socket.
# A declared choice: 180 s of no tick inside 09:16-15:29 (NIFTY alone ticks every second).
STALL_S = float(os.environ.get("TICK_STALL_S", "180"))
MIN_UP_S = float(os.environ.get("TICK_MIN_UP_S", "300"))   # never a restart flap
_T0 = time.time()

SCHEMA = """
CREATE TABLE IF NOT EXISTS ticks (
    recv_ts REAL NOT NULL, exch_ts TEXT, last_trade_ts TEXT, token INTEGER NOT NULL,
    last_price REAL, last_qty INTEGER, avg_price REAL, volume INTEGER,
    buy_qty INTEGER, sell_qty INTEGER, oi INTEGER, oi_high INTEGER, oi_low INTEGER,
    open REAL, high REAL, low REAL, close REAL,
    depth TEXT                       -- JSON {"buy":[[price,qty,orders]x5],"sell":[...]}
);
CREATE INDEX IF NOT EXISTS ix_ticks_token_ts ON ticks(token, recv_ts);
CREATE TABLE IF NOT EXISTS instruments_today (
    token INTEGER PRIMARY KEY, tradingsymbol TEXT, kind TEXT, expiry TEXT,
    strike REAL, option_type TEXT, lot_size INTEGER, why TEXT);
CREATE TABLE IF NOT EXISTS session_log (at TEXT, what TEXT);
"""

_Q: "queue.Queue" = queue.Queue(maxsize=500000)
STATE = {"box": BOX, "connected": False, "ticks_today": 0, "last_tick": None,
         "instruments": 0, "file": None, "errors": [], "started": None,
         "dropped": 0, "flushes": 0}


def now():
    return datetime.now(IST)


def _stamp():
    return now().strftime("%d-%m-%Y %H:%M:%S GMT+5:30")


def in_session(t=None) -> bool:
    t = t or now()
    if t.weekday() >= 5:
        return False
    try:
        import dp_calendar
        if dp_calendar.classify(t.date()) != dp_calendar.TRADING_DAY:
            return False
    except Exception:
        pass
    hm = t.strftime("%H:%M")
    return START <= hm < STOP


def pick_instruments(nfo: list, spot: float, today: date) -> list:
    """From Kite's NFO list: the futures and option strikes to record. Pure function."""
    nifty = [i for i in nfo if i.get("name") == "NIFTY"]
    fut = sorted((i for i in nifty if i.get("instrument_type") == "FUT"
                  and i["expiry"] >= today), key=lambda i: i["expiry"])[:2]
    opts = [i for i in nifty if i.get("instrument_type") in ("CE", "PE")
            and i["expiry"] >= today]
    expiries = sorted({i["expiry"] for i in opts})
    out = [dict(i, why="future %d" % (n + 1)) for n, i in enumerate(fut)]
    if not expiries:
        return out
    nearest = expiries[0]
    month_end = [e for e in expiries if e.month == nearest.month and e.year == nearest.year]
    monthly = max(month_end)                     # the last expiry of that month
    if monthly < today:
        monthly = nearest
    strikes = sorted({i["strike"] for i in opts if i["expiry"] == monthly})
    step = min((b - a for a, b in zip(strikes, strikes[1:]) if b > a), default=50) or 50
    for exp, n, why in ((monthly, MONTHLY_STRIKES, "monthly"), (nearest, NEAR_STRIKES,
                                                                "nearest")):
        lo, hi = spot - n * step - step / 2, spot + n * step + step / 2
        for i in opts:
            if i["expiry"] == exp and lo <= i["strike"] <= hi:
                out.append(dict(i, why="%s ATM+/-%d" % (why, n)))
    seen, uniq = set(), []
    for i in out:
        if i["instrument_token"] not in seen:
            seen.add(i["instrument_token"])
            uniq.append(i)
    return uniq


# EXTRA LIVE-ONLY INSTRUMENTS on the SAME Kite websocket (no new socket, no REST). OFF by default: TICK_EXTRA=0 keeps today's list
# byte for byte. TICK_EXTRA=1 adds (owner order 03-11-2026): Bank Nifty / Fin Nifty indices, NIFTYBEES (ETF vs futures divergence),
# the Bank Nifty near future, USDINR near future (CDS) and MCX CRUDEOIL / GOLD near futures (macro stress; MCX/CDS may not be enabled
# on the account: a failed instruments() call is logged and skipped), plus the first TICK_EXTRA_EQ constituents of config/nifty50.py
# (breadth; live L1+depth is not recoverable later). Kite allows 3000 tokens on one socket; today uses ~160.
TICK_EXTRA = os.environ.get("TICK_EXTRA", "0") == "1"
TICK_EXTRA_EQ = int(os.environ.get("TICK_EXTRA_EQ", "50"))                 # all 50 constituents: breadth sample must not be alphabetical-20 (auditor B2)
TICK_EXTRA_MACRO = os.environ.get("TICK_EXTRA_MACRO", "0") == "1"           # USDINR (CDS) + MCX crude/gold: OFF until a session proves the socket survives unentitled tokens (auditor B1)
EXTRA_NSE = ("NIFTY BANK", "NIFTY FIN SERVICE", "NIFTYBEES")


def pick_extra(nse, nfo, cds, mcx, today, eq_syms, n_eq=20):
    """Pure function. nse/nfo/cds/mcx = Kite instruments() lists (any may be [] if the call failed). -> list of dicts with 'why'."""
    out = []
    by_nse = {i.get("tradingsymbol"): i for i in nse}
    for sym in EXTRA_NSE:
        if sym in by_nse:
            out.append(dict(by_nse[sym], why="extra:index_or_etf"))
    for n, sym in enumerate(eq_syms[:max(0, n_eq)]):
        if sym in by_nse:
            out.append(dict(by_nse[sym], why="extra:constituent %d" % (n + 1)))

    def nearest_fut(rows, name):
        c = sorted((i for i in rows if i.get("name") == name and i.get("instrument_type") == "FUT" and i.get("expiry") and i["expiry"] >= today),
                   key=lambda i: i["expiry"])
        return c[0] if c else None
    for rows, name, why in ((nfo, "BANKNIFTY", "extra:banknifty_fut"), (cds, "USDINR", "extra:usdinr_fut"),
                            (mcx, "CRUDEOIL", "extra:crude_fut"), (mcx, "GOLD", "extra:gold_fut")):
        f = nearest_fut(rows, name)
        if f:
            out.append(dict(f, why=why))
    seen, uniq = set(), []
    for i in out:
        if i["instrument_token"] not in seen:
            seen.add(i["instrument_token"]); uniq.append(i)
    return uniq


def _eq_syms():
    """NSE trading symbols of the NIFTY 50 from config/nifty50.py (derived from the Fyers ticker 'NSE:SYM-EQ'); [] if unreadable."""
    try:        # the container mounts only pullers/shared: read the generated list beside this file first
        f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nifty50_syms.txt")
        if os.path.exists(f):
            return [l.strip() for l in open(f) if l.strip() and not l.startswith("#")]
    except OSError:
        pass
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
        import config.nifty50 as c
        rows = getattr(c, "NIFTY50", None) or []
        syms = []
        for r in rows:
            f = r[0] if isinstance(r, (tuple, list)) else None      # ("NSE:ADANIENT-EQ", "Adani_Enterprises")
            if f and f.startswith("NSE:") and f.endswith("-EQ"):
                syms.append(f[4:-3])
        return syms
    except Exception:
        return []


def tick_row(t: dict) -> tuple:
    d = t.get("depth") or {}
    depth = json.dumps({side: [[x.get("price"), x.get("quantity"), x.get("orders")]
                               for x in (d.get(side) or [])] for side in ("buy", "sell")}) \
        if d else None
    o = t.get("ohlc") or {}

    def ts(k):
        v = t.get(k)
        return v.isoformat() if hasattr(v, "isoformat") else (str(v) if v else None)
    return (time.time(), ts("exchange_timestamp"), ts("last_trade_time"),
            int(t["instrument_token"]), t.get("last_price"), t.get("last_traded_quantity"),
            t.get("average_traded_price"), t.get("volume_traded"),
            t.get("total_buy_quantity"), t.get("total_sell_quantity"), t.get("oi"),
            t.get("oi_day_high"), t.get("oi_day_low"), o.get("open"), o.get("high"),
            o.get("low"), o.get("close"), depth)


def day_file(d: date | None = None) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    try:
        import dp_paths
        dp_paths.set_nocow(OUT_DIR)
    except Exception:
        pass
    return os.path.join(OUT_DIR, "ticks_%s.db" % (d or now().date()).strftime("%Y%m%d"))


def _open(path):
    con = sqlite3.connect(path, timeout=30)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=FULL")           # power cuts are real on these boxes
    con.executescript(SCHEMA)
    return con


def writer(stop: threading.Event):
    """Drain the queue into today's file, one transaction every FLUSH_S."""
    con, path = None, None
    while not stop.is_set() or not _Q.empty():
        time.sleep(FLUSH_S)
        rows = []
        try:
            while len(rows) < 200000:
                rows.append(_Q.get_nowait())
        except queue.Empty:
            pass
        if not rows:
            continue
        p = day_file()
        if p != path:
            if con:
                con.close()
            con, path = _open(p), p
            STATE["file"] = p
        try:
            con.executemany("INSERT INTO ticks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            rows)
            con.commit()
            STATE["ticks_today"] += len(rows)
            STATE["flushes"] += 1
        except Exception as e:
            STATE["errors"] = (STATE["errors"] + ["write: %s" % e])[-10:]
            for r in rows:                       # keep them, never drop silently
                try:
                    _Q.put_nowait(r)
                except queue.Full:
                    STATE["dropped"] += 1
        _write_status()


def _write_status():
    try:
        os.makedirs(OUT_DIR, exist_ok=True)
        tmp = STATUS + ".tmp"
        with open(tmp, "w") as f:
            json.dump(dict(STATE, at=_stamp(), queue=_Q.qsize()), f, default=str)
        os.replace(tmp, STATUS)
    except Exception:
        pass


def run_session():
    """One trading session: instruments, websocket, record until STOP."""
    import dp_tokens
    from kiteconnect import KiteConnect, KiteTicker
    token, st = dp_tokens.get_token("kite")
    key = dp_tokens.get_pull_fields("kite").get("api_key")
    if not token or not key:
        raise RuntimeError("no usable Kite token/api_key: %s" % (st or {}).get("status"))
    kc = KiteConnect(api_key=key)
    kc.set_access_token(token)
    spot = kc.ltp(["NSE:NIFTY 50"])["NSE:NIFTY 50"]["last_price"]
    nfo = kc.instruments("NFO")
    picked = pick_instruments(nfo, spot, now().date())
    extra = []
    if TICK_EXTRA:
        def _get(ex):
            try:
                return kc.instruments(ex)
            except Exception as e:
                STATE["errors"] = (STATE["errors"] + ["extra: instruments(%s) failed: %s" % (ex, str(e)[:80])])[-10:]
                return []
        try:                              # the baseline list must NEVER be lost because an extra failed
            extra = pick_extra(_get("NSE"), nfo, _get("CDS") if TICK_EXTRA_MACRO else [], _get("MCX") if TICK_EXTRA_MACRO else [],
                               now().date(), _eq_syms(), TICK_EXTRA_EQ)
            picked = picked + extra
        except Exception as e:
            STATE["errors"] = (STATE["errors"] + ["extra: pick failed: %s: %s" % (type(e).__name__, str(e)[:80])])[-10:]
    tokens = [NIFTY_INDEX, INDIA_VIX] + [i["instrument_token"] for i in picked]
    con = _open(day_file())
    con.executemany("INSERT OR REPLACE INTO instruments_today VALUES (?,?,?,?,?,?,?,?)",
                    [(NIFTY_INDEX, "NIFTY 50", "INDEX", None, None, None, None, "spot"),
                     (INDIA_VIX, "INDIA VIX", "INDEX", None, None, None, None, "vix")] +
                    [(i["instrument_token"], i["tradingsymbol"], i["instrument_type"],
                      str(i["expiry"]), i["strike"],
                      i["instrument_type"] if i["instrument_type"] in ("CE", "PE") else None,
                      i.get("lot_size"), i["why"]) for i in picked])
    con.execute("INSERT INTO session_log VALUES (?,?)",
                (_stamp(), "subscribed %d instruments, spot %.2f" % (len(tokens), spot)))
    con.commit()
    con.close()
    STATE["instruments"] = len(tokens)

    kt = KiteTicker(key, token)

    def on_ticks(ws, ticks):
        STATE["last_tick"] = _stamp()
        STATE["last_tick_epoch"] = time.time()
        for t in ticks:
            try:
                _Q.put_nowait(tick_row(t))
            except queue.Full:
                STATE["dropped"] += 1
            except Exception as e:
                STATE["errors"] = (STATE["errors"] + ["tick: %s" % e])[-10:]

    def on_connect(ws, resp):
        STATE["connected"] = True
        ws.subscribe(tokens)
        ws.set_mode(ws.MODE_FULL, tokens)

    def on_close(ws, code, reason):
        STATE["connected"] = False
        STATE["errors"] = (STATE["errors"] + ["closed %s %s" % (code, reason)])[-10:]

    def on_error(ws, code, reason):
        STATE["errors"] = (STATE["errors"] + ["error %s %s" % (code, reason)])[-10:]

    def on_noreconnect(ws):
        STATE["gave_up"] = _stamp()
        STATE["errors"] = (STATE["errors"] + ["kite stopped reconnecting"])[-10:]

    kt.on_ticks, kt.on_connect, kt.on_close, kt.on_error = on_ticks, on_connect, on_close, on_error
    kt.on_noreconnect = on_noreconnect
    kt.connect(threaded=True)
    t_open = time.time()
    while in_session():
        _write_status()
        why = stalled(time.time(), STATE.get("last_tick_epoch"), t_open, now(),
                      bool(STATE.get("gave_up")))
        if why:
            STATE["errors"] = (STATE["errors"] + ["restarting: %s" % why])[-10:]
            try:
                c = _open(day_file())
                c.execute("INSERT INTO session_log VALUES (?,?)", (_stamp(), "restart: " + why))
                c.commit()
                c.close()
            except Exception:
                pass
            raise SocketStalled(why)
        time.sleep(10)
    try:
        kt.close()
    except Exception:
        pass
    STATE["connected"] = False


class SocketStalled(Exception):
    """The Kite socket stored nothing for STALL_S in the session - exit for a fresh one."""


def stalled(now_epoch: float, last_tick: float | None, opened: float, t, gave_up: bool,
            up_since: float | None = None) -> str | None:
    """Why this process should exit for a fresh socket, or None. Pure, tested."""
    up = now_epoch - (_T0 if up_since is None else up_since)
    if up < MIN_UP_S:
        return None
    hm = t.hour * 60 + t.minute
    if not (9 * 60 + 16 <= hm < 15 * 60 + 30):
        return None
    if gave_up:
        return "kite gave up reconnecting"
    quiet = now_epoch - max(last_tick or 0.0, opened)
    if quiet >= STALL_S:
        return "no tick for %.0f s while in the session" % quiet
    return None


def main():
    STATE["started"] = _stamp()
    stop = threading.Event()
    threading.Thread(target=writer, args=(stop,), name="tick_writer", daemon=True).start()
    while True:
        if in_session():
            try:
                try:
                    run_session()
                except SocketStalled as e:
                    print("tickrec: %s - flushing and exiting for a fresh socket" % e,
                          flush=True)
                # Kite's websocket runs on a twisted reactor, which cannot be started twice
                # in one process. Flush, then exit: Docker's restart policy brings a fresh
                # process up, and it waits for the next session.
                stop.set()
                time.sleep(FLUSH_S * 3)
                _write_status()
                os._exit(0)
            except Exception as e:
                STATE["errors"] = (STATE["errors"] + ["session: %s: %s"
                                                      % (type(e).__name__, e)])[-10:]
                _write_status()
                time.sleep(60)
                continue
        _write_status()
        time.sleep(30)


if __name__ == "__main__":
    main()
