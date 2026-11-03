# DATA MASTER FOR THE RETAIL NIFTY ENGINE (02-11-2026, GMT +5:30): every instrument, which broker feeds it, where it is stored

Status: PROPOSAL FOR KUMAR TO LOCK. Built from read-only measurements on the i5 and i7 (CSVs in `docs/framework/data_master/`). Every count below is generated from those CSVs by `tools/build_data_master.py`; nothing is retyped. UNKNOWN stays UNKNOWN.

## 0. WHAT IS DECIDED FOR YEARS, AND WHAT IS NOT

Contracts change every week (new expiries, new strikes). So the decision that lasts for years is the **RULE**, not today's names. Today's names are the rule applied on 02-11-2026.
- **NON-RECOVERABLE, live only (HDD RAID on i5 and i7):** captured by recorders. Rule R-NR below.
- **RECOVERABLE, history exists (SSD while pulling, then sealed copies):** pulled by the pullers. Rule R-RC below.
- **ROLLING WINDOW (recoverable only for a short time, so pulled daily or lost):** Fyers seconds bars (30 trading days), Upstox news (7 days).

**Not locked until measured (see section 6):** NSE scripted-download terms, Dhan plan and socket cap, Upstox Plus connection count, vendor documentation check, per-day completeness of held data.

## 1. RULES THAT FIX THE INSTRUMENT UNIVERSE

**R-NR (non-recoverable, recorded live):**
1. NIFTY 50 index and India VIX: every broker that streams them (Kite, Upstox, Dhan, Fyers).
2. NIFTY futures: current month and next month.
3. NIFTY options: the nearest 2 weekly expiries and the current monthly, strikes ATM +/- 25 steps of 50 points, both CE and PE, re-centred on live spot (not on the morning price).
4. Option-chain snapshots (all strikes, bid/ask/OI/IV/Greeks) every minute for the same expiries, plus BANKNIFTY and FINNIFTY expiries where the broker serves them.
5. 5-level depth on all of item 3 where the broker offers it; 20-level (Dhan, Upstox 30-level) on ATM +/- 12; 200-level / 50-level TBT only on the futures and nearest ATM, one contract per connection (broker cap).
6. Closing-auction fields (Upstox, Fyers, Dhan CAS) from the live feeds, kept as raw frames.
7. Instrument-master snapshot every morning (brokers serve only today's file).
8. Every non-recoverable file goes to the HDD RAID of the box that recorded it, then a checksummed copy to the other box and Drive.

**R-RC (recoverable, pulled):** NIFTY 50, BANKNIFTY, FINNIFTY, MIDCPNIFTY, NIFTY NEXT 50, India VIX, sector indices, the 50 constituents, index futures (current and expired), expired option bars, NIFTYBEES, GIFT NIFTY, USDINR, crude, gold, global indices; intervals 1m and 1d from the brokers, 5m/15m/60m/weekly derived from 1m, so no separate pull. Stored on the SSDs while pulling; sealed copies on HDD RAID and Drive.

## 2. NON-RECOVERABLE, LIVE ONLY: EVERY INSTRUMENT RECORDED TODAY, AND WHICH BROKER FEED CARRIES IT

Measured from today's recorder files on both boxes (`depth_20261102.db`, `upstox_20261102.db`, `ticks_20261102.db`). **160 distinct instruments.** Carried by 3 feeds: 45; by 2 feeds: 10; by 1 feed only: 105. The full per-feed list with broker keys is `NONREC_RECORDED_CONTRACTS_021126.csv` (260 rows).

**Gap found in this data:** the nearest weekly expiry (2026-11-03) has **68** contracts and **all 68 are carried by Kite only**. Dhan depth and the Upstox feed record the 2026-11-23 monthly only.

| instrument (UNDERLYING|EXPIRY|STRIKE|TYPE) | class | Kite ticks | Dhan 20-lvl | Dhan 200-lvl | Upstox feed | box(es) |
|---|---|---|---|---|---|---|
| INDIA VIX | INDEX | YES | - | - | YES | i5+i7 |
| NIFTY 50 | INDEX | YES | - | - | YES | i5+i7 |
| NIFTY|2026-11-23|FUT | FUT | YES | - | YES | YES | i5+i7 |
| NIFTY|2026-12-29|FUT | FUT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22450|CE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-03|22450|PE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-03|22500|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22500|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22550|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22550|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22600|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22600|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22650|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22650|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22700|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22700|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22750|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22750|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22800|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22800|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22850|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22850|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22900|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22900|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22950|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|22950|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23000|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23000|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23050|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23050|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23100|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23100|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23150|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23150|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23200|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23200|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23250|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23250|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23300|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23300|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23350|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23350|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23400|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23400|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23450|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23450|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23500|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23500|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23550|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23550|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23600|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23600|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23650|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23650|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23700|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23700|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23750|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23750|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23800|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23800|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23850|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23850|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23900|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23900|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23950|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|23950|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|24000|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|24000|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-03|24050|CE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-03|24050|PE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-03|24100|CE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-03|24100|PE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-23|22200|CE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-23|22200|PE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-23|22250|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22250|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22300|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22300|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22350|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22350|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22400|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22400|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22450|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22450|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22500|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22500|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|22550|CE | OPT | YES | YES | - | - | i5+i7 |
| NIFTY|2026-11-23|22550|PE | OPT | YES | YES | - | - | i5+i7 |
| NIFTY|2026-11-23|22600|CE | OPT | YES | YES | - | - | i5+i7 |
| NIFTY|2026-11-23|22600|PE | OPT | YES | YES | - | - | i5+i7 |
| NIFTY|2026-11-23|22650|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22650|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22700|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22700|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22750|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22750|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22800|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22800|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22850|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22850|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22900|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22900|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22950|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|22950|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23000|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23000|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23050|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23050|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23100|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23100|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23150|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23150|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23200|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23200|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23250|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23250|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23300|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23300|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23350|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23350|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23400|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23400|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23450|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23450|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23500|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23500|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23550|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23550|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23600|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23600|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23650|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23650|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23700|CE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23700|PE | OPT | YES | YES | - | YES | i5+i7 |
| NIFTY|2026-11-23|23750|CE | OPT | YES | YES | - | - | i5+i7 |
| NIFTY|2026-11-23|23750|PE | OPT | YES | YES | - | - | i5+i7 |
| NIFTY|2026-11-23|23800|CE | OPT | YES | YES | - | - | i5+i7 |
| NIFTY|2026-11-23|23800|PE | OPT | YES | YES | - | - | i5+i7 |
| NIFTY|2026-11-23|23850|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|23850|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|23900|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|23900|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|23950|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|23950|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24000|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24000|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24050|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24050|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24100|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24100|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24150|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24150|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24200|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24200|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24250|CE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24250|PE | OPT | YES | - | - | - | i5+i7 |
| NIFTY|2026-11-23|24300|CE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-23|24300|PE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-23|24350|CE | OPT | YES | - | - | - | i5 |
| NIFTY|2026-11-23|24350|PE | OPT | YES | - | - | - | i5 |

### 2b. Option-chain snapshot universe (non-recoverable): what each broker's snapshot job captured in its last 250,000 rows (i5 puller databases)

| broker | underlying key | expiry | strikes seen | rows | first | last |
|---|---|---|---|---|---|---|
| dhan | 13 (NIFTY 50, IDX_I) | 2026-11-03 | 235 | 75670 | 2026-11-02 10:36 | 2026-11-02 23:30 |
| dhan | 13 (NIFTY 50, IDX_I) | 2026-11-23 | 253 | 82205 | 2026-11-02 10:36 | 2026-11-02 23:30 |
| dhan | 13 (NIFTY 50, IDX_I) | 2026-12-29 | 259 | 84175 | 2026-11-02 10:36 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty 50 | 2026-11-03 | 104 | 25992 | 2026-11-02 11:45 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty 50 | 2026-11-23 | 122 | 30378 | 2026-11-02 11:46 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty 50 | 2026-12-29 | 120 | 29880 | 2026-11-02 11:46 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty Bank | 2026-11-23 | 154 | 38500 | 2026-11-02 11:45 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty Bank | 2026-12-29 | 147 | 36750 | 2026-11-02 11:45 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty Bank | 2027-01-25 | 121 | 30250 | 2026-11-02 11:45 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty Fin Service | 2026-11-23 | 101 | 25250 | 2026-11-02 11:45 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty Fin Service | 2026-12-29 | 63 | 15750 | 2026-11-02 11:45 | 2026-11-02 23:30 |
| upstox | NSE_INDEX|Nifty Fin Service | 2027-01-25 | 49 | 12201 | 2026-11-02 11:45 | 2026-11-02 23:30 |
| fyers | NSE:NIFTY50-INDEX | 2026-10-27 | 34 | 54780 | 2026-10-19 11:52 | 2026-10-27 22:30 |
| fyers | NSE:NIFTY50-INDEX | 2026-11-23 | 37 | 39226 | 2026-10-28 00:00 | 2026-11-02 23:30 |

Note: Dhan and Upstox chain snapshots DO include the 2026-11-03 weekly. Only the depth/feed recorders in section 2 miss it. Fyers snapshots in the sample cover the monthly only (the weekly was captured until 2026-10-27).

## 3. RECOVERABLE: HISTORY INSTRUMENTS BY BROKER, DEPTH HELD IN THE PULLER DATABASES (coverage ledger, both boxes)

Source: `RECOVERABLE_INDEX_FUT_MACRO_021126.csv` (513 rows; every symbol exactly as stored, per box). Summary by category, broker and interval:

| category | broker | interval | symbols | oldest | newest | max rows in one symbol |
|---|---|---|---|---|---|---|
| 1_broad_index | dhan | 1d | 3 | 2026-10-30 | 2026-10-30 | 30 |
| 1_broad_index | dhan | 1m | 2 | 2017-04-03 | 2026-11-02 | 2352111 |
| 1_broad_index | fyers | 10s | 5 | 2026-09-10 | 2026-11-02 | 522686 |
| 1_broad_index | fyers | 15m | 8 | 2026-07-08 | 2026-11-02 | 6385 |
| 1_broad_index | fyers | 15s | 5 | 2026-09-10 | 2026-11-02 | 345679 |
| 1_broad_index | fyers | 1d | 3 | 2001-10-15 | 2026-11-02 | 7634 |
| 1_broad_index | fyers | 1m | 14 | 2017-07-17 | 2026-11-02 | 2457830 |
| 1_broad_index | fyers | 30s | 5 | 2026-09-10 | 2026-11-02 | 172230 |
| 1_broad_index | fyers | 45s | 5 | 2026-09-10 | 2026-11-02 | 113383 |
| 1_broad_index | fyers | 5s | 5 | 2026-09-10 | 2026-11-02 | 1047519 |
| 1_broad_index | kite | 1d | 2 | 2001-10-16 | 2026-11-02 | 7494 |
| 1_broad_index | kite | 1m | 9 | 2015-01-13 | 2026-11-02 | 1543859 |
| 1_broad_index | upstox | 1d | 5 | 2001-10-29 | 2026-10-30 | 7316 |
| 1_broad_index | upstox | 1m | 13 | 2022-01-03 | 2026-11-02 | 5116723 |
| 1_broad_index | yahoo | 1d | 3 | 2001-10-15 | 2026-11-02 | 11711 |
| 1_broad_index_UNVERIFIED_numeric_id | dhan | 1m | 4 | 2019-10-03 | 2026-11-02 | 679008 |
| 2_india_vix | dhan | 1d | 1 | 2026-10-30 | 2026-10-30 | 30 |
| 2_india_vix | dhan | 1m | 1 | 2021-08-04 | 2026-11-02 | 1529037 |
| 2_india_vix | fyers | 10s | 1 | 2026-09-10 | 2026-11-02 | 522686 |
| 2_india_vix | fyers | 15m | 1 | 2026-07-08 | 2026-11-02 | 6382 |
| 2_india_vix | fyers | 15s | 1 | 2026-09-10 | 2026-11-02 | 345678 |
| 2_india_vix | fyers | 1d | 1 | 2008-07-14 | 2026-11-02 | 5931 |
| 2_india_vix | fyers | 1m | 2 | 2017-07-17 | 2026-11-02 | 2307680 |
| 2_india_vix | fyers | 30s | 1 | 2026-09-10 | 2026-11-02 | 171484 |
| 2_india_vix | fyers | 45s | 1 | 2026-09-10 | 2026-11-02 | 113383 |
| 2_india_vix | fyers | 5s | 1 | 2026-09-10 | 2026-11-02 | 1047511 |
| 2_india_vix | kite | 1d | 1 | 2009-05-20 | 2026-11-02 | 5590 |
| 2_india_vix | kite | 1m | 1 | 2015-01-13 | 2026-11-02 | 1543202 |
| 2_india_vix | upstox | 1d | 1 | 2009-06-05 | 2026-10-30 | 5440 |
| 2_india_vix | upstox | 1m | 2 | 2022-01-03 | 2026-11-02 | 1346627 |
| 2_india_vix | yahoo | 1d | 1 | 2008-03-03 | 2026-11-02 | 6870 |
| 2_india_vix_UNVERIFIED_numeric_id | dhan | 1m | 1 | 2026-07-13 | 2026-11-02 | 227075 |
| 3_sector_index | fyers | 15m | 18 | 2026-07-08 | 2026-10-15 | 1751 |
| 3_sector_index | fyers | 1m | 27 | 2017-10-26 | 2026-10-30 | 2145390 |
| 3_sector_index | kite | 1m | 14 | 2017-01-02 | 2026-11-02 | 920539 |
| 3_sector_index | upstox | 1m | 26 | 2022-01-03 | 2026-11-02 | 5226177 |
| 4_UNKNOWN_nse_NIFTY1_BANKNIFTY1_meaning | nse | 1d | 2 | 2025-10-14 | 2026-11-02 | 2056 |
| 4_index_futures | fyers | 1m | 23 | 2024-04-18 | 2026-10-30 | 1545631 |
| 5_etf_macro | fyers | 1m | 6 | 2024-04-30 | 2026-10-26 | 275454 |
| 5_etf_macro | nse | 1d | 8 | 2025-10-14 | 2026-11-02 | 2056 |
| 5_etf_macro | upstox | 1m | 13 | 2025-03-28 | 2026-10-23 | 505416 |
| 5_etf_macro | yahoo | 1d | 26 | 1962-01-02 | 2026-11-02 | 17540 |

Held option history in the puller databases (direct table reads, i5 SSD): Dhan `expired_options` up to 327,434,252 rows from 2021-10-18 (NIFTY alone 73,985,902 rows); Upstox `expired_contracts` up to 147,388,209 rows, expiries 2024-10-03 to 2026-10-27; Fyers `fyers_expired` 13,776,150 rows, NIFTY 13,766,103, expiries 2020-01-30 to 2026-10-19. Per-day completeness is not yet measured.

**Rolling window, pulled daily or lost:** Fyers seconds bars (5s/10s/15s/30s/45s), held since 2026-09-10 on the i5 for NIFTY 50, India VIX and 3 others.

## 3c. PER-DAY COMPLETENESS OF THE 1-MINUTE NIFTY 50 AND VIX HISTORY (measured, i5 puller databases; detail in `COMPLETENESS_1M_NIFTY_VIX_031126.md`, `COMPLETENESS_1M_DAYS_031126.csv`)

A full session is 375 bars (09:15 to 15:29). Counts cover only days that have at least one bar; whole missing trading days are NOT counted (no holiday calendar used).

| broker | NIFTY 1m span | days with data | days with exactly 375 or a full in-session count | quality |
|---|---|---|---|---|
| Fyers | 2017-10-30 to 2026-10-28 | 2,230 | 2,199 | longest; 19 gap days for NIFTY (300-374 bars), 22 for VIX; worst 2018-02-08 (294) |
| Upstox | 2022-01-03 to 2026-10-28 | 1,195 | 1,184 NIFTY / 1,185 VIX (in-session) | clean; 89 days have extra pre-open/post-close minutes; the spelling `NIFTY50` holds history, `NSE_INDEX|Nifty 50` holds 19 days |
| Dhan | 2017-04-03 (NIFTY), 2021-08-04 (VIX) | 2,378 | 2,073 | dirtiest: up to 765 bars/day in Aug-Sep 2021, duplicate minute labels; do not trust before about 2022-05 without cleaning |
| Kite | only 3 days (2026-10-15, 10-16, 10-19) in `pullerfull_kite_151026-0030.db` | 3 | 3 | the ledger shows Kite NIFTY50 from 2015-01-13, so the deep Kite history lives in ANOTHER file. Location UNKNOWN (to find). Kite tokens 256265 and 264969 are used, not the names |

Cross-broker price check: on 10 random full days the 09:15, 12:00 and 15:29 closes of Dhan, Fyers and Upstox differ by at most 0.05 points (rounding, 2022-23 only); from 2024 identical. All four agree exactly on the 3 Kite days. VIX mapping of Kite token 264969 was not cross-checked.

**Load plan from this measurement:** primary NIFTY and VIX 1-minute source = Fyers (from 2017-10-30), cross-checked against Upstox (from 2022-01-03) and Dhan (from about 2022-05). Kite deep history: find the file first. Bars outside 09:15-15:29 are kept in a separate column, not mixed into the session.

### 3b. The 50 NIFTY constituents

`RECOVERABLE_CONSTITUENTS_021126.csv` has 1020 rows (stock x broker x interval x box); exact SQL and the UNKNOWN list in `R2_NOTES_021126.md` (measured by a read-only agent run, 02-11-2026).

| fact (measured) | value |
|---|---|
| stocks in the engine's equity_1m on 2026-10-29 | 50 |
| mapped in the instruments master: Upstox / Kite / Fyers / Dhan | 50 / 50 / 50 / 48 (Dhan UNKNOWN for ADANIENT and HDFCLIFE) |
| stocks with a 1-minute row in the coverage ledger (union of both boxes): Fyers / Upstox / Kite / Dhan | 43 / 25 / 11 / 4 |
| oldest stock 1-minute row in the ledger: Upstox / Kite / Fyers / Dhan | 2026-07-30 / 2026-07-27 / 2026-07-27 / 2026-07-29 |
| stock 1-day rows from the four brokers | none on either box (only index 1d); NSE end-of-day file has 50 of 50 from 2025-10-14 (i5) |
| NIFTY 50 membership per the engine tables on 2026-11-02 | BSE Ltd. IN, Wipro OUT. equity_1m still carries Wipro and has no BSE |

**What this means.** (1) The puller databases hold stock 1-minute history for only about 3 months, though the brokers serve far more (earlier measurement: Kite RELIANCE 1m from 2015-04-26, Upstox from 2022-01-24). For stocks that is a PULL gap, not a load. (2) The membership change (BSE in, Wipro out) is the point-in-time problem in action: the engine's stock set is already out of date, which is why dated membership is a CORE item. (3) The ledger is a partial snapshot: a missing row does not prove the broker lacks the history.

## 4. IS IT SUFFICIENT FOR REGIME DETECTION (MULTI TIME FRAME), DIRECTION AND EDGE? FAMILY BY FAMILY

Verdicts use only what is measured above. COVERED = held or recorded at the depth needed; PARTLY = held but depth, completeness or legality unproven; GAP = cannot be obtained by pulling.

| # | what regime / direction / edge work needs | instruments | time frames | where it comes from | verdict |
|---|---|---|---|---|---|
| 1 | Price trend, momentum, range structure | NIFTY 50 index, NIFTY futures | 1m, 5m, 15m, 60m, daily, weekly (5m to weekly are made from 1m) | 1m: Kite from 2015-01-13, Dhan 2017-04-03, Fyers 2017-07-17, Upstox 2022-01-03; daily from 2001 | COVERED in depth (4 brokers cross-check); engine DB does not yet hold it: LOAD |
| 2 | Volatility regime | India VIX; realised vol from price; IV from options | 1m, daily | VIX 1m: Kite 2015-01-13, Fyers 2017-07-17, Dhan 2021-08-04, Upstox 2022-01-03; IV: derived from expired option bars (Dhan from 2021-10-18, Fyers from 2020-01-30) and live chain snapshots | VIX COVERED; IV history PARTLY (completeness unmeasured) |
| 3 | Futures basis, OI, roll | NIFTY futures current + expired | 1m, daily | Fyers current contracts from 2024-04-18; expired futures: Fyers endpoint works, floor not probed | PARTLY |
| 4 | Option structure: PCR, max pain, OI walls, skew, gamma proxy | chain snapshots; expired option bars; NSE daily strike OI | intraday and daily | snapshots: weeks only (since 2026-10-14 in the pullers); daily strike OI from NSE 2012+ (scripted-download terms unread) | PARTLY: intraday depth grows only by capture |
| 5 | Breadth, dispersion, sector rotation | 50 constituents; sector indices; BANKNIFTY, FINNIFTY | 1m, daily | sector indices 1m: Kite 2017-01-02, Fyers 2017-10-26, Upstox 2022-01-03; constituents: see 3b; point-in-time membership NOT held | PARTLY (membership history is a hard gap) |
| 6 | Participant flows | FII/DII, participant OI | daily, end of day only | NSE files 2012+ (engine), stopped 2026-10-19/29; scripted-download terms unread | PARTLY |
| 7 | Cross-asset and macro | GIFT NIFTY, USDINR, crude, gold, US indices, DXY, NIFTYBEES | daily; intraday only where the broker serves it | Yahoo daily from 1962 for globals; GIFT: Yahoo + Upstox legacy key; USDINR futures Fyers from 2024-04-30; MCX tokens unmapped | daily COVERED; intraday MCX/USDINR UNKNOWN |
| 8 | Liquidity, spread, slippage, order-book pressure | depth, bid/ask, ticks | tick to 1m | live only; recorded since 2026-10-15; gaps on several days | GAP IN TIME: weeks of history, grows only by recording. No pull can fix it |
| 9 | Calendar, expiry, lot size, special sessions, events | holidays, expiry calendar, lot size history, event calendar | daily | held in the engine; date ranges of two tables unmeasured | PARTLY |
| 10 | Costs and execution model | charges by date; measured slippage | per trade | published rates; slippage from item 8 | GAP: cost table to build; slippage needs item 8 |

**Plain verdict.** For regime detection on price, volatility, breadth and macro over multiple time frames, the held data is deep (years) once loaded into one database. For option-structure and microstructure signals, depth is weeks, not years, and can only grow by recording every session. **Having enough data does not mean an edge exists**: the pre-registered tests on this price data found no tradable intraday edge in 6 rules, and the GIFT gap predicts the open, not the intraday move.

## 5. STORAGE (decided by recoverability)

| data | while being captured / pulled | sealed copies |
|---|---|---|
| non-recoverable (section 2, 2b) | HDD RAID of the recording box | the other box's HDD RAID + Drive, each with sha256 |
| recoverable (section 3) | SSD of the pulling box (i5, i7, Pi5) | HDD RAID of i5 and i7 + Drive |
| the engine's working database | SSD only | rebuilt from the sealed copies |

## 6. WHAT MUST BE SETTLED BEFORE KUMAR LOCKS THIS (each is measured or UNKNOWN, not guessed)

1. NSE scripted-download terms (primary text unread): affects the daily strike-OI, participant and FII/DII files.
2. Dhan: plan status and whether the 5-socket cap is shared across depth and live feed (4 of 5 sockets are in use).
3. Upstox Plus connection count (forum reports of 3, not 5).
4. Vendor limits checked against the vendors' own pages (needs the four hosts allowed in this session).
5. Per-day completeness (375 bars a day) of the held 1-minute data, per broker.
6. Point-in-time NIFTY 50 membership history: no source found yet.
7. Weekly contracts on the Dhan and Upstox depth/feed recorders (Kite only today).
8. Why the i7 Fyers TBT recorder wrote nothing on 29-10, 30-10 and 02-11.

