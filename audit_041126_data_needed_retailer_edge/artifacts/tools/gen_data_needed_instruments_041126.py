#!/usr/bin/env python3
"""Generate docs/framework/data_needed_instruments_041126.csv and DATA_NEEDED_INSTRUMENTS_041126.md.

READ-ONLY on the repo; touches no box and no database. Every symbol comes from a file in the repo
(evidence column carries file:line, the line looked up here, not typed). Anything the repo cannot
show is the word UNKNOWN. Strike-window counts are produced by running the recorders' own pure
picker functions on a SYNTHETIC scrip master (spot 24000, step 50): they prove what the CODE selects,
not what a vendor currently lists. Nothing here is 'proven' - declared in code, pending live census.

    python3 tools/gen_data_needed_instruments_041126.py
"""
import csv
import os
import sys
import tempfile
from collections import Counter, OrderedDict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SH = os.path.join(ROOT, "pullers", "shared")
os.environ.setdefault("DP_ROOT", tempfile.mkdtemp(prefix="dni_"))
sys.path.insert(0, SH)
sys.path.insert(0, os.path.join(ROOT, "pullers", "puller930"))
sys.path.insert(0, ROOT)

import dp_depthrec as DR      # noqa: E402
import dp_upstoxrec as UR     # noqa: E402
import dp_tickrec as TR       # noqa: E402
import dp_fyerstbt as FT      # noqa: E402
import dp_instruments as INS  # noqa: E402
import dp_families as FAM     # noqa: E402
import dp_recoverability as REC  # noqa: E402
import config.nifty50 as N50  # noqa: E402

OUT_CSV = os.path.join(ROOT, "docs", "framework", "data_needed_instruments_041126.csv")
OUT_MD = os.path.join(ROOT, "docs", "framework", "DATA_NEEDED_INSTRUMENTS_041126.md")
CFG = REC.load(os.path.join(ROOT, "config", "recoverability.json"))
BROKERS = ("upstox", "dhan", "kite", "fyers")
LIVE, PULL, UNK = "LIVE_ONLY_NON_RECOVERABLE", "PULLABLE_RECOVERABLE", "UNKNOWN"


def ln(rel, marker):
    """file:line of the first line containing marker (computed, so it cannot drift from the code)."""
    p = os.path.join(ROOT, rel)
    with open(p, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if marker in line:
                return "%s:%d" % (rel, i)
    return "%s:MARKER-NOT-FOUND(%s)" % (rel, marker)


# ---------------------------------------------------------------- synthetic-master counts (code-derived)
TODAY, SPOT, STEP = date(2026, 11, 4), 24000.0, 50
STRIKES = [22000 + STEP * i for i in range(0, 41)]            # 22000..24000 only; widen to cover +-20 around 24000
STRIKES = [24000 + STEP * i for i in range(-40, 41)]
MON, WK = date(2026, 11, 24), date(2026, 11, 10)


def _dhan_row(sym, kind, exp, flag, strike="-0.01", opt="XX", sid="1"):
    return {"SEM_EXM_EXCH_ID": "NSE", "SEM_TRADING_SYMBOL": sym, "SEM_INSTRUMENT_NAME": kind,
            "SEM_EXPIRY_DATE": exp.isoformat() + " 14:30:00", "SEM_EXPIRY_FLAG": flag,
            "SEM_STRIKE_PRICE": strike, "SEM_OPTION_TYPE": opt, "SEM_SMST_SECURITY_ID": sid}


DHAN_ROWS = [_dhan_row("NIFTY-Nov2026-FUT", "FUTIDX", MON, "M", sid="F1")]
for k in STRIKES:
    for o in ("CE", "PE"):
        DHAN_ROWS.append(_dhan_row("NIFTY-Nov2026-%d-%s" % (k, o), "OPTIDX", MON, "M", "%d.0" % k, o, "M%d%s" % (k, o)))
        DHAN_ROWS.append(_dhan_row("NIFTY-10Nov2026-%d-%s" % (k, o), "OPTIDX", WK, "W", "%d.0" % k, o, "W%d%s" % (k, o)))

_f, _exp, _w, d20_default = DR.select_d20(DHAN_ROWS, TODAY, SPOT, weekly_n=0)
_f, _exp, _w, d20_weekly = DR.select_d20(DHAN_ROWS, TODAY, SPOT, weekly_n=6, monthly_n_with_weekly=5)
CNT = OrderedDict()
CNT["dhan_d20_default"] = len(d20_default)
CNT["dhan_d20_weekly6_monthly5"] = len(d20_weekly)
CNT["dhan_d200_futures"] = 1
keys_def, _ = UR.instrument_keys(DHAN_ROWS, TODAY, SPOT, weekly_n=0)
keys_wk, _ = UR.instrument_keys(DHAN_ROWS, TODAY, SPOT, weekly_n=5, monthly_n_with_weekly=5)
CNT["upstox_keys_default"] = len(keys_def)
CNT["upstox_keys_weekly5_monthly5"] = len(keys_wk)

KITE = []
tok = 1000
for e, tag in ((MON, "M"), (WK, "W")):
    for k in STRIKES:
        for o in ("CE", "PE"):
            tok += 1
            KITE.append({"name": "NIFTY", "instrument_type": o, "expiry": e, "strike": float(k),
                         "instrument_token": tok, "tradingsymbol": "NIFTY%s%d%s" % (tag, k, o)})
for e in (MON, date(2026, 12, 29)):
    tok += 1
    KITE.append({"name": "NIFTY", "instrument_type": "FUT", "expiry": e, "strike": 0.0,
                 "instrument_token": tok, "tradingsymbol": "NIFTYFUT%s" % e})
kite_picked = TR.pick_instruments(KITE, SPOT, TODAY)
CNT["kite_picked_default_20_15"] = len(kite_picked)           # + NIFTY 50 index + INDIA VIX added by main()
CNT["kite_subscribed_default"] = len(kite_picked) + 2

eq_syms = TR._eq_syms()
NSE_LIST = [{"tradingsymbol": s, "instrument_token": 5000 + i, "instrument_type": "EQ", "expiry": None, "strike": 0}
            for i, s in enumerate(list(TR.EXTRA_NSE) + eq_syms)]
NFO_X = [{"name": "BANKNIFTY", "instrument_type": "FUT", "expiry": MON, "instrument_token": 9001, "tradingsymbol": "BNFUT", "strike": 0}]
extra = TR.pick_extra(NSE_LIST, NFO_X, [], [], TODAY, eq_syms, TR.TICK_EXTRA_EQ)
CNT["kite_extra_tick_extra1"] = len(extra)
CNT["kite_subscribed_with_tick_extra"] = len(kite_picked) + len(extra) + 2

FY_ROWS = [("NSE:NIFTY26NOVFUT", "NIFTY 24 Nov 26 FUT")]
for k in STRIKES:
    for o in ("CE", "PE"):
        FY_ROWS.append(("NSE:NIFTY26NOV%d%s" % (k, o), "NIFTY 24 Nov 26 %d %s" % (k, o)))
fy, _ = FT.monthly_set(FY_ROWS, TODAY, SPOT)
CNT["fyers_tbt_symbols"] = len(fy)

# ---------------------------------------------------------------- rows
COLS = ["group", "instrument_name", "data_product", "symbol_upstox", "symbol_dhan", "symbol_kite", "symbol_fyers",
        "feeds_by_brokers", "class", "store_table", "need_tier", "enabled_in_repo_default", "count_by_code",
        "why_needed_for_regime", "evidence", "notes"]
ROWS = []


def classify(store):
    if not store:
        return UNK
    k, _rule, unknown = REC.effective(store.replace("YYYYMMDD", "20261104"), CFG)
    if unknown:
        return UNK
    return LIVE if k == "NON_RECOVERABLE" else PULL


def add(group, name, product, up, dh, ki, fy, feeds, store, tier, enabled, count, why, evidence, notes=""):
    ROWS.append(OrderedDict(zip(COLS, [group, name, product, up, dh, ki, fy, feeds, classify(store), store, tier,
                                       enabled, count, why, evidence, notes])))


U = "UNKNOWN"
E_CANON = lambda sym: ln("pullers/shared/dp_instruments.py", '    "%s":' % sym)
REGIME_NIFTY = "the traded series; every regime feature (ADX/ATR/slope, 5d return, range) is computed from it"

# --- A. indices (candles) -------------------------------------------------------------------------------
IDX = [
    ("NIFTY50", "NIFTY 50 index", "W.nifty_1m", "CORE", REGIME_NIFTY, "13 = Dhan IDX_I id (dp_depthrec.py:73)"),
    ("INDIAVIX", "India VIX", "W.vix_1m", "CORE", "volatility regime (CLAUDE.md 2.2); 1m history only since 2025-08-11 (CLAUDE.md 1.1)", ""),
    ("BANKNIFTY", "NIFTY BANK", "W.index_1m", "CORE", "banknifty_rs relative strength is already a derived_1m feature; sector-led vs index-led moves", ""),
    ("FINNIFTY", "NIFTY FIN SERVICE", "W.index_1m", "WISHLIST", "breadth context; not in any CLAUDE.md requirement", ""),
    ("MIDCPNIFTY", "NIFTY MID SELECT", "W.index_1m", "WISHLIST", "risk-on/off context; not in any CLAUDE.md requirement", ""),
    ("SENSEX", "SENSEX (BSE)", "W.index_1m", "WISHLIST", "cross-check of the large-cap tape", ""),
]
for canon, nm, store, tier, why, note in IDX:
    c = INS.CANON[canon]
    k = c["kite"]
    d = c["dhan"]
    dh = "IDX_I name=%s (securityId UNKNOWN: resolved from Dhan master at runtime)" % d["name"]
    if canon == "NIFTY50":
        dh = "IDX_I name=NIFTY securityId=13"
    add("INDEX_SPOT", nm, "1m+1d candles history", c["upstox"], dh,
        "%s:%s (token %s)" % (k["exchange"], k["tradingsymbol"], "256265" if canon == "NIFTY50" else ("264969" if canon == "INDIAVIX" else U)),
        c["fyers"], "upstox,dhan,kite,fyers", store, tier, "declared family candles_index_1m (all 4 brokers)", "",
        why, E_CANON(canon) + "; " + ln("pullers/shared/dp_families.py", '"candles_index_1m"'), note)

for nm, tok, tier in (("NIFTY 50 index", "256265", "CORE"), ("INDIA VIX", "264969", "CORE")):
    add("INDEX_SPOT", nm, "live ticks L1+5-depth (Kite websocket)", U, U, "token %s" % tok, U, "kite", "ticks_YYYYMMDD.db", tier,
        "ON (always in token list)", "", "live spot/VIX tape; the HDD file is the only record of the tick sequence",
        ln("pullers/shared/dp_tickrec.py", "NIFTY_INDEX, INDIA_VIX ="))
for nm, key in (("NIFTY 50 index", "NSE_INDEX|Nifty 50"), ("India VIX", "NSE_INDEX|India VIX")):
    add("INDEX_SPOT", nm, "live feed v3 full (Upstox websocket)", key, U, U, U, "upstox", "upstox_YYYYMMDD.db", "CORE",
        "ON (INDEX_KEYS)", "", "second independent live spot/VIX record (broker_consensus scoring)",
        ln("pullers/shared/dp_upstoxrec.py", "INDEX_KEYS ="))
for nm, tier in (("NIFTY BANK", "CORE"), ("NIFTY FIN SERVICE", "WISHLIST")):
    add("INDEX_SPOT", nm, "live ticks (Kite websocket, TICK_EXTRA)", U, U, "NSE:%s" % nm, U, "kite", "ticks_YYYYMMDD.db", tier,
        "compose default OFF (TICK_EXTRA=0); box .env reportedly ON, not verified here", "",
        "live cross-index tape", ln("pullers/shared/dp_tickrec.py", "EXTRA_NSE ="))

# --- B. NIFTY 50 constituents ---------------------------------------------------------------------------
for i, (fy, dbsym) in enumerate(N50.NIFTY50):
    sym = fy[4:-3]
    dh = U
    if dbsym == "Tata_Motors_Passenger_Vehicles":
        dh = "securityId 3456 (from config/nifty50.py comment on file NSE_NSE_EQ_3456_...)"
    notes = "db_sym=%s" % dbsym
    add("NIFTY50_CONSTITUENT", sym, "1m candles history (equity_1m)", U + " (NSE_EQ|<ISIN>; ISIN not in repo)", dh,
        "NSE:%s" % sym, fy, "upstox,dhan,kite,fyers", "W.equity_1m", "CORE",
        "declared family candles_equity_1m", "", "breadth + volume leadership (CLAUDE.md 2.2: breadth from equity_1m)",
        ln("config/nifty50.py", '"%s"' % fy) + "; " + ln("pullers/shared/dp_families.py", '"candles_equity_1m"'), notes)
for i, (fy, dbsym) in enumerate(N50.NIFTY50):
    sym = fy[4:-3]
    add("NIFTY50_CONSTITUENT", sym, "live L1 + 5-depth ticks (Kite, TICK_EXTRA_EQ)", U, U, "NSE:%s" % sym, fy, "kite",
        "ticks_YYYYMMDD.db", "CORE", "compose default OFF (TICK_EXTRA=0); box .env reportedly ON (T-1311 09:26: 50 constituents present, 0 missing)", "",
        "live breadth sample; intraday L1/depth of constituents is not recoverable later",
        ln("pullers/shared/dp_tickrec.py", "TICK_EXTRA_EQ ="), "Kite tradingsymbol equals NSE symbol: supported by the recorded live check only")

# --- C. futures -----------------------------------------------------------------------------------------
add("NIFTY_FUTURES", "NIFTY near-month future", "1m candles + OI history (fut_1m)", "NSE_FO|<exchange token> (resolved from master)",
    "<securityId> from master", "<token> from master", "NSE:NIFTY<YY><MON>FUT", "upstox,dhan,kite,fyers", "W.fut_1m", "CORE",
    "declared family candles_futures_1m", "", "basis/roll; futures traded volume is the only valid VWAP/OBV volume (CLAUDE.md 2.2); fut_1m since 2024-10-01",
    ln("pullers/shared/dp_families.py", '"candles_futures_1m"'), "ids roll monthly - resolved at runtime, never typed")
add("NIFTY_FUTURES", "NIFTY near + next-month futures", "live ticks L1+5-depth+OI (Kite)", U, U, "2 contracts, tokens from NFO list", U, "kite",
    "ticks_YYYYMMDD.db", "CORE", "ON", "2", "futures volume/OI tape", ln("pullers/shared/dp_tickrec.py", "fut = sorted"))
add("NIFTY_FUTURES", "NIFTY monthly future", "live feed v3 full (Upstox)", "NSE_FO|<exchange token> = Dhan securityId (T-0808)", U, U, U, "upstox",
    "upstox_YYYYMMDD.db", "CORE", "ON", "1", "second live futures record", ln("pullers/shared/dp_upstoxrec.py", "out.append((\"NSE_FO|%s\" % fut"))
add("NIFTY_FUTURES", "NIFTY monthly future", "200-level depth (Dhan d200)", U, "securityId from Dhan scrip master (SEM_EXPIRY_FLAG M)", U, U, "dhan",
    "depth_YYYYMMDD.db", "CORE", "ON", "1", "deepest book on the most liquid instrument", ln("pullers/shared/dp_depthrec.py", "200 level:"))
add("NIFTY_FUTURES", "NIFTY monthly future + ATM CE/PE + OTM pairs", "50-level tick-by-tick book (Fyers Prime TBT)", U, U, U, "NSE:NIFTY<YY><MON>FUT + options (from Fyers master)",
    "fyers", "tbt_YYYYMMDD.db", "SUPPORT", "ON", str(CNT["fyers_tbt_symbols"]), "only retail 50-level feed; capped at 5 symbols (measured 16-10)",
    ln("pullers/shared/dp_fyerstbt.py", "MAX_SYMBOLS ="), "monthly only by construction (weekly symbol never matches)")
add("NIFTY_FUTURES", "BANKNIFTY near future", "live ticks (Kite, TICK_EXTRA)", U, U, "token from NFO list", U, "kite", "ticks_YYYYMMDD.db",
    "CORE", "compose default OFF; box .env reportedly ON", "1", "BANKNIFTY lead/lag", ln("pullers/shared/dp_tickrec.py", "extra:banknifty_fut"))

# --- D. options (RULE rows, not thousands of invented rows) ---------------------------------------------
add("NIFTY_OPTIONS_RULE", "Kite: monthly ATM+-20 and nearest-expiry ATM+-15, CE and PE", "live ticks L1+5-depth+OI", U, U, "tokens from NFO list", U, "kite",
    "ticks_YYYYMMDD.db", "CORE", "ON (env TICK_MONTHLY_STRIKES/TICK_NEAR_STRIKES not verified on boxes)", str(CNT["kite_picked_default_20_15"]),
    "option tape: direction lead sits in option order flow", ln("pullers/shared/dp_tickrec.py", "MONTHLY_STRIKES ="),
    "count = options+2 futures from the code on a synthetic master (spot 24000, step 50, monthly 2026-11-24, weekly 2026-11-10); +2 index tokens when subscribed = %d" % CNT["kite_subscribed_default"])
add("NIFTY_OPTIONS_RULE", "Dhan d20: monthly ATM+-12 (weekly OFF)", "20-level depth", U, "securityIds from Dhan master", U, U, "dhan", "depth_YYYYMMDD.db",
    "CORE", "compose default (DEPTH_WEEKLY_STRIKES=0)", str(CNT["dhan_d20_default"]), "20-level book at ATM band", ln("pullers/shared/dp_depthrec.py", "DEPTH_STRIKES ="),
    "+1 d200 future = %d instruments" % (CNT["dhan_d20_default"] + 1))
add("NIFTY_OPTIONS_RULE", "Dhan d20: weekly ATM+-6 plus monthly ATM+-5", "20-level depth", U, "securityIds from Dhan master", U, U, "dhan", "depth_YYYYMMDD.db",
    "CORE", "reported ON in box .env (DATA_NEEDED_FOR_EDGE_031126.md section 3); live env UNKNOWN to this scan", str(CNT["dhan_d20_weekly6_monthly5"]),
    "weekly expiry is where most intraday option activity sits", ln("pullers/shared/dp_depthrec.py", "DEPTH_WEEKLY_STRIKES ="),
    "+1 d200 future = %d (matches the 49 recorded in TASKS.jsonl T-1311 09:26 note)" % (CNT["dhan_d20_weekly6_monthly5"] + 1))
add("NIFTY_OPTIONS_RULE", "Upstox: monthly ATM+-10 (weekly OFF)", "full_d30 depth (index keys stay full)", "NSE_FO|<token> list", U, U, U, "upstox",
    "upstox_YYYYMMDD.db", "CORE", "compose default (UPSTOX_WEEKLY_STRIKES=0)", str(CNT["upstox_keys_default"]),
    "30-level book, second record of ATM band", ln("pullers/shared/dp_upstoxrec.py", "STRIKES = int"), "keys include 2 index keys + 1 future")
add("NIFTY_OPTIONS_RULE", "Upstox: weekly ATM+-5 plus monthly ATM+-5", "full_d30 depth", "NSE_FO|<token> list", U, U, U, "upstox",
    "upstox_YYYYMMDD.db", "CORE", "reported ON in box .env; live env UNKNOWN to this scan", str(CNT["upstox_keys_weekly5_monthly5"]),
    "weekly expiry coverage", ln("pullers/shared/dp_upstoxrec.py", "WEEKLY_STRIKES = int"),
    "matches 47 recorded in TASKS.jsonl T-1311 09:26 note; the 30-level request itself is UNVERIFIED (DATA_NEEDED_FOR_EDGE_031126.md G10)")
add("NIFTY_OPTIONS_RULE", "Fyers TBT: ATM CE/PE + OTM pairs of the monthly", "50-level tick-by-tick", U, U, U, "NSE:NIFTY<YY><MON><strike>CE|PE", "fyers",
    "tbt_YYYYMMDD.db", "SUPPORT", "ON", str(CNT["fyers_tbt_symbols"]) + " incl. 1 future", "deepest retail book; tiny sample", ln("pullers/shared/dp_fyerstbt.py", "def monthly_set"))
for tbl, why in (("W.opt_chain_1m", "OI/IV/greeks per strike per minute: PCR, walls, IV percentile"),
                 ("W.greeks_1m", "delta/gamma/theta/vega per strike"), ("W.opt_snapshot_live", "raw chain snapshot"),
                 ("W.opt_summary_1m", "chain summary (PCR, max-pain inputs)"), ("W.opt_atm_1m", "ATM-band series"),
                 ("W.opt_depth_1m", "option book snapshots")):
    add("NIFTY_OPTIONS_RULE", "NIFTY option chain (ATM band, monthly + weekly)", "snapshot table " + tbl.split(".")[1], "yes (option chain endpoint)",
        "yes (/optionchain)", "no chain endpoint: /quote of ATM band only", "yes (options-chain-v3)", "upstox,dhan,kite,fyers", tbl.split(".")[1], "CORE",
        "dp_snap runs on boxes: UNKNOWN (not in compose); old pullers store it in rows_raw on SSD", "", why,
        ln("pullers/shared/dp_families.py", '"option_chain": {'), "chain snapshots are not served again later; completeness UNMEASURED (DATA_NEEDED_FOR_EDGE_031126.md section 4.2)")
add("NIFTY_OPTIONS_RULE", "NIFTY option contracts 1m OHLC history (live and expired)", "opt_ohlc_1m / expired-contracts history", "Plus: ~6 months expired", U, U,
    "Prime: expired F&O from page date 2018 (our plan floor 2019-10-31 per DATA_ITEMS csv)", "upstox,fyers (expired); dhan active only", "opt_ohlc_1m", "CORE", "dp_expired wired (T-0749)", "",
    "backtest of option legs; opt_ohlc_1m held only since 2025-09-15 (CLAUDE.md 1.1)", ln("pullers/shared/dp_families.py", '"candles_equity_1m"'),
    "windows are broker claims; probe result UNKNOWN until the live census")

# --- E. macro / overnight / ETF -------------------------------------------------------------------------
add("PREMARKET_GAP", "GIFT NIFTY (ex SGX Nifty)", "daily candles (gift_nifty_1d)", "GLOBAL_INDEX|SGX NIFTY", "5024",
    "NSEIX token 291849 (canonical format unresolved: SymbolUnresolved)", U, "upstox,dhan (confirmed live 01-11-2026 per docstring); kite unresolved", "gift_nifty_1d", "CORE",
    "puller exists, run manually inside fullpuller", "", "pre-market gap signal (CLAUDE.md section 5.1)", ln("pullers/shared/gift_nifty_puller.py", "CANON = {"),
    "DAILY only. DATA_NEEDED_FOR_EDGE_031126.md G9 says the key was 'NOT found' on 03-11 - CONTRADICTS this docstring (01-11). Resolve with a read-only master query.")
add("PREMARKET_GAP", "GIFT NIFTY", "live overnight / pre-open intraday feed", U, U, U, U, "NONE RECORDING", "", "CORE", "MISSING (B7)", "",
    "the actual overnight tape; live-only if it exists", ln("pullers/shared/gift_nifty_puller.py", "WHAT THIS WRITES"), "live key/entitlement UNKNOWN")
add("ETF", "NIFTYBEES", "daily candles (niftybees_1d)", "NSE_EQ|INF204KB14I2", "10576", "NSE:NIFTYBEES (token 2707457)", "NSE:NIFTYBEES-EQ", "upstox,dhan,kite,fyers",
    "niftybees_1d", "CORE", "puller exists, run manually", "", "ETF vs futures divergence (CLAUDE.md section 5.2)", ln("pullers/shared/niftybees_puller.py", "CANON = {"))
add("ETF", "NIFTYBEES", "live ticks (Kite, TICK_EXTRA)", U, U, "NSE:NIFTYBEES", U, "kite", "ticks_YYYYMMDD.db", "CORE", "compose default OFF; box .env reportedly ON", "",
    "intraday ETF/futures spread", ln("pullers/shared/dp_tickrec.py", "EXTRA_NSE ="))
add("MACRO_FUTURES", "MCX CRUDEOIL near-month future", "daily candles+OI (macro_futures_1d)", U, "573422 (expiry 2026-11-19; rolls)", U, U, "dhan only (others returned nothing, measured 01-11)",
    "macro_futures_1d", "SUPPORT", "puller exists, run manually; contract id hand-maintained", "", "macro stress overlay (CLAUDE.md 5.3)", ln("pullers/shared/macro_futures_puller.py", "CONTRACTS = {"),
    "vendor_id rolls; stale id returns empty silently (roll check is a warning only)")
add("MACRO_FUTURES", "MCX GOLD near-month future", "daily candles+OI (macro_futures_1d)", U, "495213 (expiry 2026-12-04; rolls)", U, U, "dhan only", "macro_futures_1d", "SUPPORT",
    "puller exists, run manually", "", "macro stress overlay", ln("pullers/shared/macro_futures_puller.py", "CONTRACTS = {"))
for nm in ("USDINR near future (CDS)", "MCX CRUDEOIL near future", "MCX GOLD near future"):
    add("MACRO_FUTURES", nm, "live ticks (Kite, TICK_EXTRA_MACRO)", U, U, "token from CDS/MCX list (entitlement UNKNOWN)", U, "kite", "ticks_YYYYMMDD.db", "SUPPORT",
        "OFF (TICK_EXTRA_MACRO=0)", "", "intraday macro stress", ln("pullers/shared/dp_tickrec.py", "TICK_EXTRA_MACRO ="),
        "Fable could not exclude that an unentitled token flaps the socket")
add("MACRO_FUTURES", "USDINR future (daily)", "daily candles", U, U, U, U, "NONE (no current-dated FUTCUR in any broker master, measured 01-11)", "", "SUPPORT",
    "NOT PULLED", "", "currency stress", ln("pullers/shared/macro_futures_puller.py", "USDINR FUTURES IS DELIBERATELY NOT INCLUDED"), "use Yahoo INR=X spot meanwhile")

# --- F. world markets (Yahoo only; no premium broker serves them) ---------------------------------------
for canon in INS.GLOBAL_SYMBOLS:
    c = INS.CANON[canon]
    if canon == "GIFTNIFTY":
        add("WORLD_MARKETS", "GIFTNIFTY via Yahoo (^NSEI) - PLACEHOLDER", "daily", "None", "None", "None", "None", "NONE (Yahoo placeholder is the CASH index)",
            "global_daily", "WISHLIST", "declared, reported NO_DATA by design", "", "must NOT be read as the overnight gap", E_CANON(canon), c.get("caution", ""))
        continue
    tier = "SUPPORT" if canon in ("SP500", "NASDAQ", "DXY", "USDINR", "BRENT", "GOLD", "US10Y", "VIX_US", "NIKKEI", "HANGSENG") else "WISHLIST"
    add("WORLD_MARKETS", canon, "daily (global_daily)", "None", "None", "None", "None", "NONE of the 4 brokers; Yahoo %s" % c["yahoo"], "global_daily", tier,
        "declared family global_daily", "", "overnight/lead-lag context for the opening regime", E_CANON(canon), "Yahoo ticker %s" % c["yahoo"])

NSE_FAMILY_MARKER = {"fii_dii_daily": '"nse_fii_dii": {', "participant_oi_daily": '"nse_participant_oi": {',
                     "derivative_activity": '"nse_participant_oi": {', "market_1d": '"nse_market_daily": {',
                     "breadth_1d": '"nse_market_daily": {', "corporate_actions": '"corporate_actions": {',
                     "trading_holidays": '"calendar": {', "index_membership": '"instruments": {'}
# --- G. NSE exchange reports (no broker) ----------------------------------------------------------------
for tbl, why in (("fii_dii_daily", "FII/DII net flows - EOD only, never intraday (CLAUDE.md 1)"), ("participant_oi_daily", "participant OI - EOD"),
                 ("derivative_activity", "derivative activity - EOD"), ("market_1d", "exchange daily market picture"),
                 ("breadth_1d", "daily breadth (recomputable from equity_1m)"), ("corporate_actions", "splits/bonuses: without them old prices are wrong"),
                 ("trading_holidays", "tells a holiday from a gap; degrades to Tuesday rule if unreadable (CLAUDE.md 2.1)"),
                 ("index_membership", "point-in-time NIFTY 50 membership: avoids survivorship bias")):
    add("NSE_REPORT", tbl, "daily report", "None", "None", "None", "None", "NSE (not a broker)" + (" + Yahoo" if tbl == "corporate_actions" else ""), tbl,
        "CORE" if tbl in ("fii_dii_daily", "trading_holidays", "index_membership") else "SUPPORT", "declared in dp_families", "", why,
        ln("pullers/shared/dp_families.py", NSE_FAMILY_MARKER[tbl]))

# --- H. masters, news, events ---------------------------------------------------------------------------
for b, tbl in (("upstox", "U.instruments"), ("dhan", "instruments"), ("kite", "K.instruments"), ("fyers", "instruments")):
    add("INSTRUMENT_MASTER", "%s instrument master (daily snapshot)" % b, "master", U, U, U, U, b, tbl.split(".")[-1], "CORE", "declared family instruments", "",
        "only today's list is served; old lists map old contracts and expiries", ln("pullers/shared/dp_families.py", '"instruments": {'))
add("NEWS", "Upstox news by NIFTY 50 constituent instrument_keys", "live news items", U, U, U, U, "upstox (Dhan blocked DH-902: needs PLUS)", "news_items", "SUPPORT",
    "module exists; scheduling UNKNOWN", "50 keys", "news before volume reacts (Kumar 18-09)", ln("pullers/shared/dp_news.py", "Upstox GET /v2/news"),
    "Nifty INDEX has no news (measured 26-10)")
add("EVENTS", "RBI / FOMC / CPI event calendar", "manual file config/event_calendar.json", "None", "None", "None", "None", "NONE (manual)", "event_calendar", "SUPPORT",
    "file exists", "", "event windows widen NO_TRADE threshold", ln("pullers/shared/dp_event_calendar.py", "DEFAULT_PATH ="),
    "CLAUDE.md section 5.4 names data/event_calendar.yaml; repo holds config/event_calendar.json - path mismatch")
for nm, why in (("BANKNIFTY options", "no recorder anywhere (DATA_NEEDED_FOR_EDGE_031126.md B12)"), ("Sensex / BSE F&O", "offered by Kite BFO / Upstox BSE_FO, not subscribed")):
    add("GAP", nm, "live ticks/depth", U, U, U, U, "NONE RECORDING", "", "WISHLIST", "MISSING", "", why, "docs/framework/DATA_NEEDED_FOR_EDGE_031126.md section 2")

# ---------------------------------------------------------------- write CSV
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(ROWS)

# ---------------------------------------------------------------- write MD (all totals computed here)
cls = Counter(r["class"] for r in ROWS)
tier = Counter((r["need_tier"], r["class"]) for r in ROWS)
by_broker = {b: Counter() for b in BROKERS}
for r in ROWS:
    for b in BROKERS:
        if any(p.strip().lower().startswith(b) for p in r["feeds_by_brokers"].split(",")):
            by_broker[b][r["class"]] += 1
unk_cells = Counter()
rt_cells = Counter()
for r in ROWS:
    for b in BROKERS:
        if str(r["symbol_" + b]).startswith(U):
            unk_cells[b] += 1
        elif "<" in str(r["symbol_" + b]) or "from master" in str(r["symbol_" + b]) or "from NFO" in str(r["symbol_" + b]):
            rt_cells[b] += 1
unk_class = [r for r in ROWS if r["class"] == UNK]
groups = Counter(r["group"] for r in ROWS)
# register tables the families declare but no CSV row covers
fam_tables = sorted({t.split(".")[-1] for s in FAM.FAMILIES.values() for t in s["tables"]})
covered = {r["store_table"].split(".")[-1] for r in ROWS}
missing_tables = [t for t in fam_tables if t not in covered]

L = []
w = L.append
w("# DATA NEEDED - PER INSTRUMENT (retailer_db_edge) - 04-11-2026")
w("")
w("STATUS: **declared in code, pending live census + Fable + external auditor + Kumar.** Nothing here is proven. Generated by `tools/gen_data_needed_instruments_041126.py` from files in the repo; no box, no database was touched. The CSV is `docs/framework/data_needed_instruments_041126.csv` (%d rows, one per instrument x data product)." % len(ROWS))
w("")
w("Companion, not replacement: `DATA_NEEDED_FOR_EDGE_031126.md` is the group-level list (G1-G14); this file is the per-instrument expansion. Class comes from `config/recoverability.json` (itself still PROPOSED) via `dp_recoverability.effective()`, applied to the store table or day-file name. For day files named `ticks_YYYYMMDD.db` / `upstox_YYYYMMDD.db` the generator substitutes a sample date (20261104) before classifying, because `classify()` on the literal string `upstox_YYYYMMDD.db` returns UNKNOWN (its `upstox_20` pattern needs a real date); the substitution is what makes those 6 INDEX_SPOT rows LIVE_ONLY, and the live-file check `tools/check_recoverability_placement.py` classifies real file names, which do carry a date.")
w("")
w("## 1. Totals (computed from the CSV)")
w("")
w("| class | rows |")
w("|---|---|")
for k in (LIVE, PULL, UNK):
    w("| %s | %d |" % (k, cls.get(k, 0)))
w("| **all** | **%d** |" % len(ROWS))
w("")
w("By need tier (author's PROPOSED tier - judgement, not a proof; CORE = named in CLAUDE.md or already a regime feature):")
w("")
w("| tier | %s | %s | %s |" % (LIVE, PULL, UNK))
w("|---|---|---|---|")
for t in ("CORE", "SUPPORT", "WISHLIST"):
    w("| %s | %d | %d | %d |" % (t, tier[(t, LIVE)], tier[(t, PULL)], tier[(t, UNK)]))
w("")
w("By group:")
w("")
w("| group | rows |")
w("|---|---|")
for g, n in groups.items():
    w("| %s | %d |" % (g, n))
w("")
w("## 2. Which of the four premium brokers can supply how many rows (declared, from the `feeds_by_brokers` column)")
w("")
w("Counting rule (single, stated): a broker is counted for a row when ANY comma-separated token of `feeds_by_brokers`, lower-cased and stripped, STARTS WITH the broker's name (so 'dhan only (...)' counts for dhan; 'kite unresolved' inside a token that starts with another broker does not count for kite). Free-text after the first word is ignored.")
w("")
w("| broker | LIVE_ONLY rows | PULLABLE rows | UNKNOWN-class rows | symbol cells UNKNOWN | symbol cells resolved at runtime from the broker master (placeholder, no value in repo) |")
w("|---|---|---|---|---|---|")
for b in BROKERS:
    w("| %s | %d | %d | %d | %d | %d |" % (b, by_broker[b][LIVE], by_broker[b][PULL], by_broker[b][UNK], unk_cells[b], rt_cells[b]))
none_rows = [r for r in ROWS if not any(b in r["feeds_by_brokers"].lower() for b in BROKERS)]
w("")
w("Rows no premium broker feeds (Yahoo / NSE / manual / nobody): %d. Only the declared capability is counted; whether a broker actually returns the instrument is the live census, not this file." % len(none_rows))
w("")
w("## 3. Option-chain rules and the counts the CODE produces")
w("")
w("Run on a synthetic master (spot 24000, strike step 50, monthly 2026-11-24, weekly 2026-11-10). They show what each picker selects, **not** what a vendor lists today.")
w("")
w("| picker | count | note |")
w("|---|---|---|")
for k, v in CNT.items():
    w("| %s | %d | |" % (k, v))
w("")
w("Cross-check against live-recorded numbers in `docs/tasks/TASKS.jsonl` T-1311 (09:26): Dhan d20 49 instruments, Upstox 47. The code reproduces both only with the weekly settings ON (Dhan %d = %d + 1 d200 future; Upstox %d). Compose defaults are weekly OFF (%d / %d); the env actually set on each box is not in the repo - UNKNOWN to this scan." % (
    CNT["dhan_d20_weekly6_monthly5"] + 1, CNT["dhan_d20_weekly6_monthly5"], CNT["upstox_keys_weekly5_monthly5"], CNT["dhan_d20_default"] + 1, CNT["upstox_keys_default"]))
w("Typical option instruments recorded per box per session (rule x count): Kite %d subscribed (default 20/15) %s; Dhan %d; Upstox %d; Fyers %d. These are overlapping records of the same ATM band by different brokers, not %d distinct instruments." % (
    CNT["kite_subscribed_default"], "or %d with TICK_EXTRA=1" % CNT["kite_subscribed_with_tick_extra"], CNT["dhan_d20_weekly6_monthly5"] + 1,
    CNT["upstox_keys_weekly5_monthly5"], CNT["fyers_tbt_symbols"],
    CNT["kite_subscribed_default"] + CNT["dhan_d20_weekly6_monthly5"] + 1 + CNT["upstox_keys_weekly5_monthly5"] + CNT["fyers_tbt_symbols"]))
w("")
w("## 4. UNKNOWNs and the exact read-only step that resolves each")
w("")
w("| # | unknown | resolving step (read-only, after 15:35 IST) |")
w("|---|---|---|")
n = 0
def U_(a, b):
    global n
    n += 1
    w("| %d | %s | %s |" % (n, a, b))
U_("Upstox NSE_EQ key and Dhan securityId of the 50 constituents (the repo holds only Fyers tickers, Kite-by-name and Dhan db_sym names; CSV symbol cells UNKNOWN: upstox %d, dhan %d, of %d rows)" % (unk_cells["upstox"], unk_cells["dhan"], len(ROWS)),
   "`SELECT vendor_id,tradingsymbol FROM instruments WHERE source IN ('upstox','dhan') AND tradingsymbol IN (<nifty50_syms.txt>)` on `_state/instruments.db` of each box")
U_("Kite instrument_token of every non-index instrument (cells say `from NFO list`)", "`SELECT token,tradingsymbol,why FROM instruments_today` in today's `ticks_YYYYMMDD.db` on each box")
U_("Whether TICK_EXTRA / weekly flags are really ON on i5 and i7 (compose default OFF)", "`docker exec tickrec env | grep TICK_`, same for depthrec/upstoxrec; or read `status.json` beside each day file")
U_("GIFT NIFTY: contradiction between gift_nifty_puller.py (keys found 01-11) and DATA_NEEDED_FOR_EDGE G9 (key not found 03-11); live intraday key", "`SELECT * FROM instruments WHERE source='upstox' AND (tradingsymbol LIKE '%GIFT%' OR tradingsymbol LIKE '%SGX%')`; same for dhan/kite")
U_("Which dataset names and rows per day sit in `rows_raw` per broker (option_chain, quote_depth) and since when", "`SELECT dataset,source,COUNT(*),MIN(ts),MAX(ts) FROM rows_raw GROUP BY dataset,source` on each pullerfull_/puller930_ DB (read-only, mode=ro)")
U_("Broker history windows (opt 1m, expired, equity 1m) - `recoverable_until` is UNKNOWN per broker in recoverability.json", "the max-depth proof (task #43 T-0832) per broker x dataset")
U_("Whether the Upstox 30-level request is accepted (UNVERIFIED in DATA_NEEDED_FOR_EDGE G10)", "`status.json` of upstoxrec: depth mode actually used + a frame count of one day file")
U_("Whether dp_snap (chain snapshots) runs on the boxes", "`docker ps` + `_state/` snapshot clock files; compose file does not list it")
U_("Tables the classifier does not match: %s. (gift_nifty_1d, niftybees_1d, macro_futures_1d were added to history_candles and event_calendar to manual_curated/NON_RECOVERABLE on 04-11-2026 after the Fable review; global_1m and opt_ohlc_1m are protected as window_limited_intraday)" % (", ".join(sorted({r["store_table"] for r in unk_class if r["store_table"]})) or "none"),
   "confirm the new rules with Kumar + external auditor (config/recoverability.json is still PROPOSED)")
U_("Rows with NO store table (nothing records them): %s" % ("; ".join("%s / %s" % (r["instrument_name"], r["data_product"]) for r in unk_class if not r["store_table"]) or "none"),
   "decide whether to build a recorder (GIFT live; USDINR daily)")
w("")
if unk_class:
    w("Rows whose class is UNKNOWN (classifier has no rule or no store table); the project fail-safe would treat them as NON_RECOVERABLE (HDD only), but that is a default, not a finding:")
    w("")
    for r in unk_class:
        w("- %s | %s | table=%s" % (r["instrument_name"], r["data_product"], r["store_table"] or "(none)"))
    w("")
w("Tables the dp_families declaration lists that this CSV does not name as a store_table: %s. Most are columns of a covered family (e.g. market_state_1m, trade_microstructure_1m, sector_1m rows are per instrument x product, not named here) - confirm in the live census." % ", ".join(missing_tables))
w("")
w("## 5. Gaps against Kumar's wishlist")
w("")
w("| wishlist item | in the CSV? | status (declared in code) | gap |")
w("|---|---|---|---|")
w("| GIFT NIFTY | yes, 2 rows | daily puller exists (Upstox+Dhan); live overnight NOT recorded | no live feed; contradiction in docs (section 4 #4) |")
w("| options | yes (rule rows + chain tables) | ticks/depth for monthly (+weekly if env ON) on 4 recorders | BANKNIFTY options none; second-month none; chain snapshot completeness UNMEASURED |")
w("| VIX | yes | candles all 4 brokers; live Kite + Upstox | 1m history only since 2025-08-11 (CLAUDE.md 1.1) |")
w("| OI | futures `fut_1m` OI, tick OI (Kite), chain OI | declared | no verified OI series per strike over time |")
w("| futures | yes | near+next Kite, monthly Upstox/Dhan d200/Fyers | only monthly; no BANKNIFTY options |")
w("| Bank Nifty | index + near future | candles declared; live ticks only with TICK_EXTRA | options none |")
w("| world markets | yes (%d Yahoo rows) | Yahoo daily only, no intraday | no premium broker supplies them; intraday world data not declared anywhere |" % groups["WORLD_MARKETS"])
w("| news / events | yes | Upstox news module; manual event JSON | scheduling UNKNOWN; Dhan news blocked; CLAUDE.md names a .yaml path the repo does not have |")
w("| NIFTY 50 volumes | yes (50 candle rows + 50 live rows) | equity_1m candles declared; live L1 only if TICK_EXTRA=1 | `market_1m` volume is index aggregate - do not use (CLAUDE.md 2.2) |")
w("| BEES | yes | daily puller + Kite live (extra) | only daily is a puller; manual run |")
w("| FII/DII | yes | EOD NSE report | intraday FII/DII does not exist at retail (CLAUDE.md 1) |")
w("| weekly expiry | rule rows | Kite already; Dhan/Upstox via env; Fyers TBT monthly only | box env unverified; Fyers weekly missing (B9) |")
w("")
w("## 6. Honesty list")
w("")
w("- Counts of strikes are from running the pickers on a synthetic master, not from a vendor.")
w("- `class` is the classifier's answer on a table or file name; the live census (what each broker's store actually holds) is still to come.")
w("- Tier labels are the author's proposal. They have not been shown to Fable, an external auditor or Kumar.")
w("- No instrument here is 'proven'.")
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print("rows", len(ROWS), dict(cls), "md lines", len(L))
