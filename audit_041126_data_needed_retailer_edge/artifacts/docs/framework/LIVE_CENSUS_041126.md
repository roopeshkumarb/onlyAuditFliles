# LIVE CENSUS 04-11-2026 ~11:45 IST (read-only, market open)

Source: recorder status.json + day-DB dimension tables opened mode=ro, nice 19 (no ionice on box), plus `find -size +20M` metadata listing. Nothing written/moved on any box. Pi5 not queried (out of directive scope). All numbers below are computed by script from the CSV.

## Instruments subscribed today (live-only recorders), per box per broker

| box | broker | recorder | instruments | CE | PE | FUT | INDEX | EQ |
|---|---|---|---|---|---|---|---|---|
| i5 | kite | tickrec (ticks_*.db) | 202 | 72 | 72 | 3 | 2 | 53 |
| i5 | dhan | depthrec d20+d200 (depth_*.db) | 49 | 24 | 24 | 1 | 0 | 0 |
| i5 | upstox | upstoxrec full_d30 (upstox_*.db) | 47 | 22 | 22 | 1 | 2 | 0 |
| i5 | fyers | fyers_tbt (tbt_*.db) | 5 | 2 | 2 | 1 | 0 | 0 |
| i7 | kite | tickrec (ticks_*.db) | 202 | 72 | 72 | 3 | 2 | 53 |
| i7 | dhan | depthrec d20+d200 (depth_*.db) | 49 | 24 | 24 | 1 | 0 | 0 |
| i7 | upstox | upstoxrec full_d30 (upstox_*.db) | 47 | 22 | 22 | 1 | 2 | 0 |
| i7 | fyers | fyers_tbt (tbt_*.db) | 5 | 2 | 2 | 1 | 0 | 0 |

Note: counts are rows of each recorder's own dimension table (kite = instruments_today.kind). Dhan: 48 d20 option contracts (26 weekly 2026-11-09 + 22 monthly 2026-11-23) + 1 d200 monthly FUT = 49 distinct security_ids, but only 27 distinct symbol strings because weekly and monthly contracts carry the SAME label `NIFTY-Nov2026-<strike>-CE/PE` (symbol alone cannot identify the contract; security_id can). Kite EQ includes 2 index-like names NIFTY BANK and NIFTY FIN SERVICE as the DB itself classes them.

CORRECTED 04-11-2026 (Fable review defect 7): the earlier line said 'distinct instrument names 259 (i5), 259 (i7), union 269'. Those figures are distinct (broker, name) PAIRS, not names. Recomputed from LIVE_CENSUS_041126.csv (kind LIVE_ONLY, brokers kite/dhan/upstox/fyers): i5 303 recorder rows -> 259 (broker,name) pairs -> 236 distinct names; i7 the same, 303 -> 259 -> 236; union of both boxes 269 pairs -> 246 distinct names (the strike band is centred on each box's own start spot, so the two boxes differ slightly). Name collisions: Dhan 49 security_ids carry 27 distinct label strings (weekly and monthly share `NIFTY-Nov2026-<strike>-CE/PE`), and Upstox 47 keys carry 25 distinct names for the same reason; only the security_id / instrument key identifies the contract. Kite 202 and Fyers 5 are unique per name. Recompute: `python3 -c` over the CSV: pairs = len({(broker,instrument)}), names = len({instrument}) per box.

## Observations (evidence-backed)

- Weekly + monthly both recorded: Kite 62 weekly (2026-11-09) + 82 monthly (2026-11-23) option rows (+3 FUT, Nov/Dec/BANKNIFTY); Dhan 26 weekly + 22 monthly options; Upstox 22 weekly + 22 monthly options + 1 monthly FUT + 2 indices; Fyers TBT 4 monthly options + 1 FUT only. status.json `expiry` field shows only the monthly (2026-11-23) while `expiry_weekly` 2026-11-09 appears only on the Dhan status. Recorded as found, not interpreted.
- Per-token tick row counts: query exceeded the 5 s budget and was interrupted on both boxes; NOT collected (UNKNOWN, not 0).
- Dhan d200 silent-drop errors (3-4 per box 09:04-09:13) and Fyers TBT unclean close 09:12 still present in status.json errors.
- i5 `/volume2` (SSD): 1.8G free of 205G (100%). i7 `/volume2`: 279G free of 419G (34% used). `/volume1` HDD: i5 2.1T free, i7 1.1T free.
- `space_gate.json` on i5 still reports `failed_open: true` (policy file never found) - gate is not protecting SSD.

## Largest DBs under /volume1/docker/datapullers (>20 MB), per box - the 'bigger databases' reconciliation

### i5: 123 files >20MB, 238.9 GB total

| GB | file | kind |
|---|---|---|
| 68.53 | upstox/pullerfull_upstox_151026-0031.db | PULLER_HISTORY_DB |
| 28.47 | fyers/pullerfull_fyers_151026-0030.db | PULLER_HISTORY_DB |
| 16.14 | dhan/pullerfull_dhan_151026-0031.db | PULLER_HISTORY_DB |
| 9.83 | _static_copies/nse_121026-1534.db | PULLER_HISTORY_DB |
| 9.83 | nse/nse_121026-1534.db | PULLER_HISTORY_DB |
| 6.05 | _static_copies/fyers_121026-1534.db | PULLER_HISTORY_DB |
| 6.05 | fyers/fyers_121026-1534.db | PULLER_HISTORY_DB |
| 3.60 | upstox/puller930_upstox_151026-0033.db | PULLER_HISTORY_DB |
| 2.87 | _static_copies/dhan_121026-1533.db | PULLER_HISTORY_DB |
| 2.87 | dhan/dhan_121026-1533.db | PULLER_HISTORY_DB |
| 2.86 | _backup/141026-1514/dhan.db | OTHER_DB |
| 2.48 | _cold_from_ssd/fyers/pullerfull_fyers_141026-1658.db | PULLER_HISTORY_DB |
| 2.48 | _static_copies/pullerfull_fyers_141026-1658.db | PULLER_HISTORY_DB |
| 2.48 | fyers/pullerfull_fyers_141026-1658.db | PULLER_HISTORY_DB |
| 1.89 | _segsync/sealed/2026-10-28_dhan_dhan_121026-1533.delta0001.db | PULLER_HISTORY_DB |

By broker/area (GB): upstox=92.8, none=47.1, fyers=39.6, dhan=30.3, kite=17.7, nse=11.2, yahoo=0.0

### i7: 87 files >20MB, 236.0 GB total

| GB | file | kind |
|---|---|---|
| 84.29 | upstox/pullerfull_upstox_151026-0041.db | PULLER_HISTORY_DB |
| 33.71 | fyers/pullerfull_fyers_151026-0040.db | PULLER_HISTORY_DB |
| 15.77 | dhan/pullerfull_dhan_151026-0040.db | PULLER_HISTORY_DB |
| 9.83 | _static_copies/nse_121026-1534.db | PULLER_HISTORY_DB |
| 7.67 | upstox/puller930_upstox_151026-0053.db | PULLER_HISTORY_DB |
| 7.31 | kite/pullerfull_kite_151026-0040.db | PULLER_HISTORY_DB |
| 6.05 | _static_copies/fyers_121026-1534.db | PULLER_HISTORY_DB |
| 3.55 | nse/pullerfull_nse_151026-0053.db | PULLER_HISTORY_DB |
| 2.87 | _static_copies/dhan_121026-1533.db | PULLER_HISTORY_DB |
| 2.48 | _static_copies/pullerfull_fyers_141026-1658.db | PULLER_HISTORY_DB |
| 1.98 | upstox/upstox_141026-1043.db | PULLER_HISTORY_DB |
| 1.89 | _segsync_in/i5/2026-10-28_dhan_dhan_121026-1533.delta0001.db | PULLER_HISTORY_DB |
| 1.72 | upstox_live/j1800/upstox_20261027.db | LIVE_RECORDER_DAYFILE |
| 1.68 | upstox_live/j1800/upstox_20261026.db | LIVE_RECORDER_DAYFILE |
| 1.67 | fyers/fyers_141026-0143.db | PULLER_HISTORY_DB |

By broker/area (GB): upstox=111.0, fyers=38.2, none=35.2, dhan=26.4, kite=20.8, nse=4.4, yahoo=0.0

Note: `_static_copies/` (e.g. nse_121026-1534.db 9.8GB) and `_cold_from_ssd/` hold copies; they are counted in the totals above. `.db-wal`/`.db-shm` and files <20MB excluded.

## Live-only vs history, per recorder
- LIVE_ONLY (non-recoverable): ticks (Kite), depth d20/d200 (Dhan), upstox full_d30 frames, fyers_tbt frames - day files `ticks/ depth/ upstox_live/ fyers_tbt/` on /volume1 HDD on both boxes, ~0.2-1.4 GB per day each.
- HISTORY DBs (puller output): `upstox/ dhan/ fyers/ kite/ nse/ yahoo/` pullerfull_*/puller930_*/old epoch files.
- Daily single-file pullers on i5 root: gift_nifty_1d.db 274KB, macro_futures_1d.db 12KB, niftybees_1d.db 20KB (tiny; GIFT/macro/BEES are daily, not live-recorded).
