"""THE DATASET FAMILIES. One collector fills many register fields.

KUMAR 14-10-2026: "by end of day i need to see pulling 490 on 930puller and full
puller but it is not 490 it is 530".

WHY FAMILIES AND NOT 523 COLLECTORS. The 930 register names 523 broker-pullable
fields, and for three weeks I treated that as 523 separate things to build, which is
why none of them got built. They are not separate. Every field in the register names
the STORE TABLE it belongs in, and one API call fills a whole table at once:

    one option-chain call        fills opt_snapshot_live, opt_chain_1m, greeks_1m,
                                 opt_summary_1m, opt_atm_1m, opt_depth_1m   -> 73 fields
    one full-quote call          fills depth_1m and equity_depth_1m          -> 90 fields
    three NSE public reports     fill market_1d, participant_oi_daily,
                                 fii_dii_daily                               -> 69 fields

MEASURED 14-10-2026 by grouping the register: 28 store tables account for 448 of the
523 fields. So this is a dozen collectors, not 523.

WHAT THIS FILE IS AND IS NOT. It is a DECLARATION of which family covers which store
tables, which brokers can serve it, and what one request costs. It fetches nothing.
The count of fields a family covers is COMPUTED from the register at runtime - it is
never a number typed here, because a number typed here would drift the first time the
register changed and nobody would notice.

BOTH PULLERS USE IT. Kumar, same message: "these 530 must also covered by full puller
as well." A family is not the 930 puller's property; it is a description of the data,
and either puller can be told to run it.
"""

from __future__ import annotations

# Each family: the store tables it fills, the brokers that can serve it, the kind of
# request, and how it is paced. `symbols` is what the planner expands - "CORE" means
# the model-critical set, "CHAIN" means the option chain around ATM.
#
# NOTHING HERE IS A MARKET DECISION. These are acquisition facts: which endpoint
# serves which table, and what the vendor's own limit is.
FAMILIES = {
    "candles_index_1m": {
        "tables": ["W.nifty_1m", "M.index_1m", "W.vix_1m", "W.index_1m"],
        "sources": ["upstox", "dhan", "kite", "fyers"],
        "kind": "candles", "interval": "1m", "symbols": "INDEX",
        "why": "the index series the whole system predicts",
    },
    "candles_index_1d": {
        "tables": ["W.nifty_daily", "W.index_daily"],
        "sources": ["upstox", "dhan", "kite", "fyers", "yahoo"],
        "kind": "candles", "interval": "1d", "symbols": "INDEX",
        "why": "the long daily history, 20+ years on Fyers Prime",
    },
    "candles_futures_1m": {
        "tables": ["W.fut_1m"],
        "sources": ["upstox", "dhan", "kite", "fyers"],
        "kind": "candles", "interval": "1m", "symbols": "FUTURES",
        "why": "basis and roll - the index alone cannot price a trade",
    },
    "candles_equity_1m": {
        "tables": ["W.equity_1m", "K.candles"],
        "sources": ["upstox", "dhan", "kite", "fyers"],
        "kind": "candles", "interval": "1m", "symbols": "EQUITY",
        "why": "constituents, for breadth and for the equity side of the register",
    },
    "option_chain": {
        "tables": ["W.opt_snapshot_live", "W.opt_chain_1m", "W.greeks_1m",
                   "W.opt_summary_1m", "W.opt_atm_1m", "W.opt_depth_1m"],
        # T-0984 (19-10-2026): kite and fyers have collectors now (dp_snap._kite_tick /
        # _fyers_tick). Fyers: the monthly chain band (options-chain-v3) + 5-level depth of the
        # front future and the ATM CE/PE. Kite has NO chain endpoint: its part is /quote of the
        # monthly future + ATM band (depth, OI, LTQ, average price) - no greeks, no IV. A field
        # counts for a broker only when the register names that broker (pull_score).
        "sources": ["upstox", "dhan", "kite", "fyers"],
        "kind": "option_chain", "interval": "snap", "symbols": "CHAIN",
        # Dhan documents one unique option-chain request every 3 seconds. That is the
        # vendor's number, not mine.
        "min_seconds_between": {"dhan": 3.0, "upstox": 1.0},
        "why": "strikes, premiums, OI, IV and Greeks - the instrument actually traded",
    },
    "quote_depth": {
        "tables": ["W.depth_1m", "W.equity_depth_1m", "UG.global_quotes",
                   "W.market_state_1m"],
        "sources": ["upstox", "dhan", "kite", "fyers"],
        "kind": "quote", "interval": "snap", "symbols": "CORE",
        "why": "bid/ask, sizes and the book - the biggest single family",
    },
    "trade_microstructure": {
        "tables": ["W.trade_microstructure_1m"],
        "sources": ["upstox", "dhan"],
        "kind": "quote", "interval": "snap", "symbols": "CORE",
        "why": "last traded quantity and trade-level detail, from the same quote call",
    },
    "nse_market_daily": {
        "tables": ["W.market_1d", "W.breadth_1d"],
        "sources": ["nse"],
        "kind": "nse_report", "interval": "1d", "symbols": "NSE_MARKET",
        "why": "the exchange's own daily market picture",
    },
    "nse_participant_oi": {
        "tables": ["W.participant_oi_daily", "W.derivative_activity"],
        "sources": ["nse"],
        "kind": "nse_report", "interval": "1d", "symbols": "NSE_PARTICIPANT",
        "why": "who holds the open interest - FII, DII, pro, client",
    },
    "nse_fii_dii": {
        "tables": ["W.fii_dii_daily"],
        "sources": ["nse"],
        "kind": "nse_report", "interval": "1d", "symbols": "NSE_FIIDII",
        "why": "institutional direction, the signal retail cannot see any other way",
    },
    "global_daily": {
        "tables": ["W.global_daily", "W.global_1m"],
        "sources": ["yahoo"],
        "kind": "candles", "interval": "1d", "symbols": "GLOBAL",
        "why": "S&P, Nasdaq, DXY, crude, gold - the lead-lag context",
    },
    "instruments": {
        "tables": ["K.instruments", "U.instruments", "W.instrument_master",
                   "W.expiry_calendar", "W.index_membership"],
        "sources": ["upstox", "dhan", "kite", "fyers"],
        "kind": "master", "interval": "1d", "symbols": "ALL",
        "why": "the universe itself, and every expiry and strike in it",
    },
    "calendar": {
        "tables": ["W.trading_holidays", "W.trading_calendar"],
        "sources": ["nse"],
        "kind": "nse_report", "interval": "1d", "symbols": "NSE_CALENDAR",
        "why": "which days and minutes are real, so a gap can be told from a holiday",
    },
    "corporate_actions": {
        "tables": ["W.corporate_actions"],
        "sources": ["nse", "yahoo"],
        "kind": "nse_report", "interval": "1d", "symbols": "NSE_CA",
        "why": "splits, bonuses and dividends - without them old prices are wrong",
    },
    "sector": {
        "tables": ["W.sector_1m"],
        "sources": ["upstox", "kite", "fyers"],
        "kind": "candles", "interval": "1m", "symbols": "SECTOR",
        "why": "sector indices, for rotation and breadth",
    },
}

# Which families exist but have NO collector written yet. Stated here so the count is
# honest before any of them runs - an empty list would read as "all done".
NOT_IMPLEMENTED_YET = set()


_REGISTER_ERROR = {"why": None}


def _register_fields() -> list:
    """The 930 register. An empty list MUST never read as "zero fields".

    Measured 14-10-2026: the full puller's image did not carry field_register.py, so
    this returned [] and every count came out 0 - which reads exactly like "nothing to
    cover", the most dangerous wrong answer a coverage report can give. The reason is
    kept and every caller reports it.
    """
    try:
        import field_register
        _REGISTER_ERROR["why"] = None
        return field_register.FIELDS
    except Exception as e:
        _REGISTER_ERROR["why"] = (
            "the 930 register is not in this image (%s: %s) - every count below is "
            "UNKNOWN, not zero" % (type(e).__name__, e))
        return []


def _table_of(field: dict) -> str:
    store = str(field.get("store") or "?")
    parts = store.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else parts[0]


def coverage() -> dict:
    """How many REGISTER FIELDS each family covers. Counted, never typed.

    A number written into this file would drift the moment the register changed and
    nobody would see it happen. So it is recomputed from field_register every call.
    """
    fields = _register_fields()
    pullable = [f for f in fields if f.get("pullable")]
    by_table = {}
    for f in pullable:
        by_table.setdefault(_table_of(f), []).append(f.get("id"))

    out = {"register_fields": len(fields), "pullable": len(pullable),
           "families": {}, "covered_ids": set(), "unmapped_tables": {},
           "register_error": _REGISTER_ERROR["why"]}
    claimed = set()
    for name, spec in FAMILIES.items():
        ids = []
        for t in spec["tables"]:
            ids.extend(by_table.get(t, []))
            claimed.add(t)
        out["families"][name] = {
            "fields": len(ids), "ids": ids, "tables": spec["tables"],
            "sources": spec["sources"], "kind": spec["kind"],
            "implemented": name not in NOT_IMPLEMENTED_YET, "why": spec["why"]}
        out["covered_ids"].update(ids)
    for t, ids in by_table.items():
        if t not in claimed:
            out["unmapped_tables"][t] = len(ids)
    out["covered"] = len(out["covered_ids"])
    out["not_covered"] = out["pullable"] - out["covered"]
    return out


def summary() -> dict:
    """The one-line answer: how many of the 523 these families reach."""
    c = coverage()
    fams = sorted(c["families"].items(), key=lambda x: -x[1]["fields"])
    if c.get("register_error"):
        return {"status": "UNKNOWN", "why": c["register_error"],
                "pullable_fields": None, "fields_a_family_covers": None,
                "families": len(FAMILIES),
                "note": "A count of 0 here would be a lie. The register is missing "
                        "from this image, so the answer is UNKNOWN."}
    return {
        "status": "OK",
        "pullable_fields": c["pullable"],
        "fields_a_family_covers": c["covered"],
        "fields_with_no_family": c["not_covered"],
        "families": len(FAMILIES),
        "implemented": sum(1 for _, v in fams if v["implemented"]),
        "top": [{"family": n, "fields": v["fields"], "sources": v["sources"],
                 "implemented": v["implemented"]} for n, v in fams[:12]],
        "biggest_unmapped": sorted(c["unmapped_tables"].items(),
                                   key=lambda x: -x[1])[:10],
        "note": ("Every number here is counted from field_register at call time. A "
                 "family being declared does NOT mean its collector runs - read "
                 "`implemented`."),
    }


def for_source(source: str) -> list:
    """Families this broker can serve. Used by both pullers' planners."""
    return [n for n, s in FAMILIES.items() if source in s["sources"]]


def spec(name: str) -> dict:
    return dict(FAMILIES.get(name) or {})
