# RETAILER-EDGE PULLER DESIGN, PER BROKER (04-11-2026)

STATUS: DESIGN ONLY (rev 2, 04-11-2026: corrected against docs/framework/FABLE_REVIEW_041126.md defects 8-11 and every cite re-opened). Nothing here is built, deployed, restarted or run on any box. Written from the repo at
`/home/user/blpro`; every "exists" claim cites file:line read in this checkout. Anything that needs a live box is
marked **UNVERIFIED-LIVE** (market open, IO Gate Rule; run after 15:35 IST, read-only).
Rule in force (Kumar): prebuilt proven tools only. Anything new needs Fable + external auditor + Kumar.
Brokers: Upstox Plus, DhanHQ, Kite Connect, Fyers Prime (`dp_paths.py` SOURCE_LABELS). Class of each datum
follows `config/recoverability.json` (PROPOSED, still unconfirmed by Kumar/auditors).

## 0. Four findings that change the brief

1. **`dp_quorum` is a login lease, not a data voter.** It is imported only by `dp_login_lease.py`, `dp_voter/voter_server.py`,
   `broker_login/leader.py` (and `tools/build_frame_page.py`, a report page) (grep of pullers/ and tools/). Nothing votes on tick/depth data. Real redundancy today is:
   (a) the same live feed recorded independently by i5 AND i7 (`dp_tickrec.py:17-19`), and (b) four brokers recorded
   side by side, never merged (`gift_nifty_puller.py` PK `(dt, src)`), scored after the close by `tools/broker_consensus.py:1-25`
   (median of brokers, per-minute, read-only). "Quorum via dp_quorum" should read "consensus via broker_consensus.py".
2. **Gift/BEES/MCX are daily candles, not live.** `gift_nifty_puller.py:44` (`gift_nifty_1d`), `niftybees_puller.py:38`
   (`niftybees_1d`), `macro_futures_puller.py:53` (`macro_futures_1d`), clocked every 6 h by `planner.py:1260-1290`
   (`EXTRAS_EVERY_SECONDS`, wiring loop `:1273-1275`). Live (intraday) GIFT NIFTY exists nowhere.
   Live Bank Nifty / Fin Nifty / NIFTYBEES exist as Kite extras (`dp_tickrec.py:141-144`, compose default `TICK_EXTRA: 0`
   at `docker-compose.datapullers.yml:331`), and the 04-11 live census shows `TICK_EXTRA` is **ON on both boxes** (50 EQ + NIFTY BANK /
   NIFTY FIN SERVICE / NIFTYBEES present), so the box `.env` overrides the compose default. Live MCX / USDINR (`TICK_EXTRA_MACRO`, compose `:333`)
   are absent from the census, i.e. still OFF.
3. **No same-day SSD-to-HDD mover exists.** `ssd_to_hdd_move.sh` by DEFAULT skips anything younger than 168 h and anything under 100 MB (`MIN_AGE_H`/`MIN_BYTES`, env-overridable, `:7`)
   and is copy-only unless `ALLOW_REMOVE=1` (`:9,14`). Lowering `MIN_AGE_H` does not fix this: the epoch DBs are live-appended and `*_current.db` pointers are skipped (`dp_paths.py:305-306`). `dp_segsync_run.py:1-9` copies only SEALED files and never deletes.
   Recoverable candle stores are continuously appended epoch DBs (`<broker>_current.db`), so they are never "sealed" daily.
4. **i7's compose can put the whole `/data` root on SSD.** `docker-compose.datapullers.i7.yml:52,79` (services `fullpuller` `:42`, `puller930` `:70`) mount `${DP_SSD_ROOT:-/volume1/...}:/data`;
   if `/volume2/datapullers` is set there, anything written under `/data` (including recorders, if they run from that root) lands on SSD,
   contradicting live-only -> HDD. The repo's i7 file lists only `fullpuller` and `puller930` (`grep '^  [a-z0-9_]*:$'`); the recorders
   are in `docker-compose.datapullers.yml:316-455` (`tickrec` `:316`, `depthrec` `:355`, `upstoxrec` `:388`, `fyerstbt` `:422`; profiles `ticks`, `depth`, `upstox`, `fyerstbt`). **UNVERIFIED-LIVE:** which compose file starts the
   recorders on i7, and what i7's `.env` sets. `.env` files are not in the repo.

## 1. Disk rule applied (Kumar, `dp_recoverability.py:1-3`, `route()` `:34-50`)

| Class | Written to | Where in code |
|---|---|---|
| NON_RECOVERABLE (live-only) | HDD RAID1 `/volume1/docker/datapullers` on i5 and i7. Never SSD. Pi5 has no HDD (`recoverability.json` pi_note), so it records none. | all four recorders: compose HDD mount `/volume1/docker/datapullers:/data` (compose `:324,363,396,430`); `OUT_DIR = DP_ROOT/<kind>/<box>` |
| RECOVERABLE (history) | SSD first (i5 `/volume2`, i7 `/volume2/datapullers`, Pi5 `/share/pull`), then HDD the same day | fullpuller / puller930 via `dp_paths.source_dir`; mount overrides `DP_UPSTOX_DIR` etc. (compose `:207-213` fullpuller, `:282-288` puller930) |
| UNKNOWN name | treated NON_RECOVERABLE | `dp_recoverability.py:23-25,28-31` |

## 2. Per-broker tables

Legend: **EXISTS** = in the repo and tested/ran live per the cited docstring. **GAP** = not in the repo. **PARTIAL** = exists with a stated limit.
"Reaches HDD": for live-only the recorder writes to HDD directly (no move needed).

### 2.1 UPSTOX PLUS

| Datum | Module | Status | Runs where | Lands on | Reaches HDD |
|---|---|---|---|---|---|
| NIFTY 50 index, India VIX, monthly future, monthly options ATM+/-10 CE/PE, full + 30-level depth (raw protobuf, zlib) | `dp_upstoxrec.py:14-18, 50, 91` (`instrument_keys`) | EXISTS | container `upstoxrec`, i5 + i7 (compose `:388`, mount `:396`) | HDD `.../upstox_live/<box>/upstox_<YYYYMMDD>.db` | direct |
| Weekly expiry | same, `UPSTOX_WEEKLY_STRIKES` `dp_upstoxrec.py:56` (code and compose `:403` default 0) | EXISTS, **ON in practice**: census shows 22 weekly + 22 monthly + 1 fut + 2 index = 47 keys on both boxes (the `weekly5_monthly5` picker, `dp_upstoxrec.py:53-55`), so the box `.env` sets it; not in the repo (**UNVERIFIED-LIVE**: exact env values) | i5 + i7 | HDD | direct |
| News (per-constituent, 30 keys/request) | `dp_news.py` (`MAX_KEYS` `:~50`), wired `planner.py:1163-1216` | EXISTS (Upstox only; Dhan news blocked DH-902) | fullpuller | SSD or HDD per `DP_UPSTOX_DIR` **UNVERIFIED-LIVE** | see 3.2 |
| GIFT NIFTY daily candles | `gift_nifty_puller.py` | EXISTS (daily only) | fullpuller, every 6 h `planner.py:1262` | `<source_dir>/../gift_nifty_1d.db` | see 3.2 |
| **GIFT NIFTY live ticks** | none | **GAP** | - | - | - |
| NIFTYBEES daily | `niftybees_puller.py` | EXISTS (daily) | fullpuller | `niftybees_1d.db` | see 3.2 |
| 1m/1d index, futures, equity, sector candles (recoverable) | `fullpuller/download_engine.py` `download_upstox`; families `dp_families.py:39-141` | EXISTS | fullpuller + puller930 | SSD (`DP_UPSTOX_DIR`) | see 3.2 |
| Expired options history | `dp_upstox_expired.py`, `dp_expired_runner.py` | EXISTS | fullpuller | SSD | see 3.2 |
| Option chain snapshots (opt_chain_1m, greeks, ...) | `dp_snap.py` -> `rows_raw` (`dp_snap.py:837`) | EXISTS, NON_RECOVERABLE | fullpuller | **must be HDD**; `rows_raw` shares a file with recoverable datasets | split needed, GAP G3 |

### 2.2 DHANHQ

| Datum | Module | Status | Runs where | Lands on | Reaches HDD |
|---|---|---|---|---|---|
| 20-level depth: NIFTY options, raw. Compose/code default is monthly ATM+/-12 (50 inst., `dp_depthrec.py:17,60`); **what runs today is 48 options + 1 future = 49** (26 weekly + 22 monthly per the census) | `dp_depthrec.py:17-20, 60, 192` (`select_d20`) | EXISTS | `depthrec` i5 + i7 (compose `:355`, mount `:363`) | HDD `.../depth/<box>/depth_<YYYYMMDD>.db` | direct |
| 200-level depth: monthly future (1 inst./socket) | `dp_depthrec.py:18` | EXISTS | same | HDD | direct |
| Weekly expiry depth | `DEPTH_WEEKLY_STRIKES` `dp_depthrec.py:65` (code and compose `:370` default 0; weekly/monthly split `:62-63`) | EXISTS, **ON in practice** per the census (26 weekly + 22 monthly + 1 fut = 49; the `weekly6_monthly5` split); box `.env`, **UNVERIFIED-LIVE** | same | HDD | direct |
| MCX Crude + Gold near-month daily futures | `macro_futures_puller.py:17-32` (Dhan only has current MCX masters) | EXISTS (daily; vendor_id rolls monthly, manual `CONTRACTS` list) | fullpuller | `macro_futures_1d.db` | see 3.2 |
| **USDINR futures** | none: master carries only expired 2024 FUTCUR (`macro_futures_puller.py:7-12`) | **GAP** (refresh currency master) | - | - | - |
| GIFT NIFTY daily (vendor 5024) | `gift_nifty_puller.py` | EXISTS (daily) | fullpuller | `gift_nifty_1d.db` | see 3.2 |
| History candles, expired options | `download_engine.download_dhan`, `dp_expired*.py` | EXISTS | fullpuller | SSD | see 3.2 |
| News | `dp_news.py` | **BLOCKED** DH-902 (needs Plus) | - | - | - |
| Socket safety (5 sockets/account, 6th kills oldest) | `dp_depthrec.py:26` SAFETY block; `dp_recguard.py:1-14` | EXISTS | | | |

### 2.3 KITE CONNECT

| Datum | Module | Status | Runs where | Lands on | Reaches HDD |
|---|---|---|---|---|---|
| FULL ticks + 5-level book: NIFTY, VIX, near+next futures, options monthly ATM+/-20 and nearest expiry ATM+/-15 | `dp_tickrec.py:5-19, 47-48` | EXISTS | `tickrec` i5 + i7 (compose `:316`, mount `:324`) | HDD `.../ticks/<box>/ticks_<YYYYMMDD>.db` | direct |
| Breadth: all 50 constituents live, Bank Nifty / Fin Nifty index, NIFTYBEES live, Bank Nifty future | `TICK_EXTRA=1`, `pick_extra` `dp_tickrec.py:147`; `TICK_EXTRA_EQ` default 50 (`:142`) | EXISTS; **ON in practice**: 09:15 verify on 04-11 saw `extra:banknifty_fut=1, extra:index_or_etf=3` (TASKS.jsonl T-1311 note logged 09:26) and the live census shows 53 EQ + NIFTY BANK / NIFTY FIN SERVICE / NIFTYBEES on both boxes | same | HDD | direct |
| USDINR (CDS) + MCX crude/gold live | `TICK_EXTRA_MACRO` `dp_tickrec.py:143`, compose `:333` | PARTIAL: built, OFF (census shows no USDINR/MCX tokens) "until a session proves the socket survives unentitled tokens" | same | HDD | direct |
| History candles (limited window) | `download_engine.download_kite` | EXISTS | fullpuller | SSD | see 3.2 |
| GIFT NIFTY | Kite lists it (vendor 291849, NSEIX) but symbol unresolved (`gift_nifty_puller.py:19-23`) | **GAP** (low value: Upstox/Dhan cover it) | - | - | - |
| Constraint | ONE Kite session per API key: only `broker_login` may mint (`MINT_POLICY`, `broker_login/login_engine.py:50`; the 3-replica majority proof is `dp_quorum.py:12-18`) | EXISTS | | | |

### 2.4 FYERS PRIME

| Datum | Module | Status | Runs where | Lands on | Reaches HDD |
|---|---|---|---|---|---|
| Tick-by-tick 50-level book, monthly future + ATM CE/PE + OTM pairs, hard cap 5 symbols (Fyers refuses more) | `dp_fyerstbt.py:14-28, 57` | EXISTS | `fyerstbt` i5 + i7 (compose `:422`, mount `:430`) | HDD `.../fyers_tbt/<box>/tbt_<YYYYMMDD>.db` | direct |
| History candles: 20+ years daily, 1m window | `download_engine.download_fyers`; `dp_fyers_expired.py`; `pullers/fyers/*` | EXISTS | fullpuller | SSD | see 3.2 |
| Option chain v3 + 5-level depth of front future / ATM | `dp_snap._fyers_tick` (T-0984) | EXISTS, NON_RECOVERABLE | fullpuller | **must be HDD** | split needed, GAP G3 |

### 2.5 Broker-independent items (NSE reports, event calendar) and the live-only list Kumar gave for the first GUI tab

No broker feeds the first two rows (they are filed here, not under Fyers Prime as rev 1 did):

| Datum | Module | Status | Runs where | Lands on | Reaches HDD |
|---|---|---|---|---|---|
| NSE reports (FII/DII, participant OI, bhavcopy, holidays), recoverable | `dp_nse_reports.py` (no broker), `planner.py:1141`, `puller930_server.py:275` | EXISTS | fullpuller / puller930 | `rows_raw` | see 3.2 |
| Event calendar (RBI/FOMC/CPI) | `dp_event_calendar.py` reads `config/event_calendar.json` (CLAUDE.md s5.4 names `data/event_calendar.yaml`: path mismatch to settle) | EXISTS as a reader; the file is manual | engine | SSD + Drive (CLAUDE.md s3) | Drive sync |


| Datum | Covered by | Status |
|---|---|---|
| Options chain, OI, VIX, futures | Upstox + Dhan + Kite + Fyers recorders above | EXISTS x4 brokers (weekly + monthly ON per census) |
| Bank Nifty | Kite extras (index + future); Upstox/Dhan can add via master | EXISTS (Kite), PARTIAL elsewhere |
| NIFTY 50 constituent volumes / breadth | Kite `TICK_EXTRA_EQ=50` | EXISTS (one broker only = no cross-check) |
| BEES live | Kite extra (NIFTYBEES in `EXTRA_NSE`, `dp_tickrec.py:144`), ON per census | EXISTS (one broker only) |
| GIFT NIFTY live | none | **GAP G1** |
| World markets intraday | Yahoo `global_daily`/`global_1m` families (`dp_families.py:110-115`); collector EXISTS: `download_engine.py:1012` `download_yahoo(..., interval="1m")`, window 7 days per request (`:160`), ~30 days at all (`INTERVAL_HISTORY_CAP_DAYS`, `:166-170`) | EXISTS but window-limited, so `global_1m` is now NON_RECOVERABLE (class `window_limited_intraday`, Fable defect 1); **UNVERIFIED-LIVE**: that the table actually fills and what the boxes hold |
| News (domestic/international) | Upstox only (`dp_news.py`) | PARTIAL; no international source |
| FII/DII | NSE EOD only (`dp_nse_reports.py`); intraday FII/DII does not exist (CLAUDE.md s1) | EXISTS (EOD) |

## 3. Data flow

### 3.1 Live-only (already the design, already built)
Each recorder writes one file per day per box straight to HDD. i5 and i7 record independently, so a restart or outage on one is covered by the other.
Four brokers run in parallel on each box (tickrec / depthrec / upstoxrec / fyerstbt = Kite / Dhan / Upstox / Fyers).
After the close, `tools/broker_consensus.py` scores each broker and each box against the median. That is the consensus layer; it is measurement, not a vote at write time.
Guards that exist: `dp_recguard.py` (one socket, silent-socket detection), `dp_calendar.classify` in `in_session` (holiday awareness, A3 fix),
`MIN_FREE_GB=50` stop-writing guard in every recorder (`dp_depthrec.py:68`, `dp_upstoxrec.py` `MIN_FREE_GB`, `dp_fyerstbt.py:58`), `dp_placement_guardian.py` (proposes only, never moves). The IO gate monitors only.

### 3.2 Recoverable (the part that is not yet one flow)
Target: pulled after 15:35 -> SSD (i5, i7, Pi5) -> same day to HDD with sha256 + read-back, copy-only until `ALLOW_REMOVE` is approved -> Pi5 copy lands on i5.
Pieces that exist: `dp_segsync.py:1-14` (copy to temp name, receiver hashes, rename only on match, PROVEN ledger), `dp_segsync_transport.py:71-101`
(LAN over ssh with remote hash + `.BAD` on mismatch; Drive via rclone), `dp_segsync_run.py` (register, copy to every missing place, retry, alerts, exit 2 on mismatch),
`ssd_to_hdd_move.sh` v3 (symlink-aware, `-wal/-shm`-aware, mount check, free-space check, lock, MANIFEST), `dp_placement.py` (chooses a root, never refuses).
Pieces missing: see G2-G4.

## 4. Minimal NEW code that is truly required

| # | Gap | Why it is real | Smallest fix | Prebuilt alternative checked |
|---|---|---|---|---|
| G1 | Live GIFT NIFTY | only daily exists (`gift_nifty_puller.py:26`) | add the GIFT key to the existing Upstox (`dp_upstoxrec` key list) and/or Dhan feed as an extra instrument, same pattern as `pick_extra` (`dp_tickrec.py:147`). Config-sized change, no new recorder. Needs a measured instrument key from the Upstox master. | recorders already take extra keys |
| G2 | Daily seal of recoverable stores | epoch DBs append forever; segsync only ships sealed files; mover waits 168 h | one small "daily export" step: after 15:35, copy that day's rows (or a SQLite online-backup) to a dated sealed file, then hand it to `dp_segsync_run`. Uses `sqlite3` backup API; no new transport | `dp_segsync*`, `ssd_to_hdd_move.sh` reused as is |
| G3 | `rows_raw` mixes classes | recoverable `fii_dii`/`holidays` and NON_RECOVERABLE `option_chain`/`quote_depth` share one file (`dp_paths.py:427-437`; `dp_verify.py:77`); classifier is now per dataset name (commit `93f9b296`) but placement is per FILE | route `option_chain`/`quote_depth` rows to a separate HDD-only DB (new `DP_SERVICE`/file), recoverable rows stay | `dp_placement.py` already picks a root per file |
| G4 | i7 root can resolve to SSD | `${DP_SSD_ROOT}:/data` (`...i7.yml:52,79`) | deploy-time check only: fail the start if a recorder's `OUT_DIR` resolves under an SSD mount. `dp_recoverability.check_path` already does this test | `dp_recoverability.check_path`, `tools/check_recoverability_placement.py` |
| G5 | Currency master stale (USDINR) | no 2025/2026 FUTCUR in any master (`macro_futures_puller.py:7-12`) | refresh the currency-segment instrument master pull, then add USDINR to `CONTRACTS` | `dp_instruments.py`, `dp_expired` |
| G6 | MCX contract roll is manual | vendor_id changes each expiry (`macro_futures_puller.py:32`) | derive near-month from the master each run | `dp_instruments.py` |

Not required: any new recorder, any new transport, any new socket client. G1, G4 are configuration-sized. G2, G3 are small orchestration. Do not rebuild what exists.

## 5. Tests each item needs (write first, break on purpose)

| Item | Tests |
|---|---|
| G1 | extra key appears in `instrument_keys`; total keys <= `MAX_KEYS` (50) and d30 sub-limit (`test_dp_upstoxrec.py` `test_fo_keys_ask_30_levels...`); GIFT absent from master -> logs and skips, never crashes; raw frame stored unchanged |
| G2 | sealed file hash equals source at seal time; a row written after seal is not in the file; interrupted export leaves only `.part`; re-run is idempotent; two boxes' same-day seals do not collide (box in name) |
| G3 | `option_chain` row lands only in the HDD-only DB; `fii_dii` row only in the recoverable DB; read-back count equals write count per dataset; `check_path` reports a violation if a NON_RECOVERABLE dataset's file sits under an SSD root |
| G4 | start refused when `OUT_DIR` is under an SSD root; passes when under `/volume1`; UNKNOWN name treated as protected |
| G5/G6 | master with no current contract -> reports "gap", not zero rows; roll on expiry day picks next month |
| Move chain | `ALLOW_REMOVE=0` leaves source untouched (exists in v3); power cut between copy and rename leaves no half file; hash mismatch deletes only `.part`; symlink/-wal/-shm skip cases (exist) |
| Existing, must stay green | `tests/test_dp_recoverability.py`, `tests/test_recoverability_placement.py` (25 pass after `93f9b296`), `tests/test_dp_depthrec.py`, `tests/test_dp_upstoxrec.py`, segsync tests |

## 6. Rollout order (old pullers keep running until the replacement is proven)

1. Today: nothing deployed. This document + the recoverability table go to Fable and the external auditor (public repo `roopeshkumarb/onlyAuditFliles`).
2. After 15:35, read-only: run `tools/check_recoverability_placement.py` on i5 and i7 (UNVERIFIED-LIVE items above), and `SELECT DISTINCT dataset, source FROM rows_raw` per box to prove which broker really fills which dataset.
3. Build G1, G4 (config-sized), then G3, G2 in a branch with tests; mutation-check each.
4. Run new and old side by side for a full session; `broker_consensus.py` must agree within the brokers' own spread.
5. Friday 20:00 IST: SSD empty per `FRIDAY_SSD_MIGRATION_PLAN_041126.md` (i5 `.env` SSD override removed; i7 `DP_SSD_ROOT` stays on HDD; Pi5 `dp_voter` lease state needs Kumar's named exception).
6. Only after proof: stop the old pullers. `ALLOW_REMOVE=1` is a separate Kumar decision.

## 7. Three-approval checklist (nothing counts as done without all three)

| Item | Fable | External auditor | Kumar |
|---|---|---|---|
| Recoverability table (`config/recoverability.json`, `93f9b296`) | [ ] | [ ] | [ ] |
| This per-broker inventory (is each EXISTS/GAP row correct?) | [ ] | [ ] | [ ] |
| G1 live GIFT NIFTY | [ ] | [ ] | [ ] |
| G2 daily seal + same-day copy | [ ] | [ ] | [ ] |
| G3 `rows_raw` split | [ ] | [ ] | [ ] |
| G4 SSD-root start guard | [ ] | [ ] | [ ] |
| G5/G6 currency + MCX roll | [ ] | [ ] | [ ] |
| `TICK_EXTRA_MACRO=1` (USDINR/MCX live on Kite; still OFF per census) | [ ] | [ ] | [ ] |
| Weekly-expiry recording: ON live per census (`*_WEEKLY_STRIKES` > 0 in box `.env`); approve committing it as the repo default (compose default is 0) | [ ] | [ ] | [ ] |
| `ALLOW_REMOVE=1` | [ ] | [ ] | [ ] |
| Stop old pullers | [ ] | [ ] | [ ] |

## 6b. Same-day SSD to HDD: exactly what must be built, and the safety contract

Reality today (section 0 finding 3): no component moves a recoverable store to HDD on the day it is pulled. **To build (nothing else):**

- **G2, daily seal.** After 15:35 IST, for each recoverable store that is live-appended (`<broker>_current.db`, `<broker>_<service>_raw_current.db`),
  write that day's rows to a dated, immutable sealed file on the SSD using the SQLite online-backup API (consistent snapshot, WAL-safe), named with box + date.
  Then register it with `dp_segsync_run.py` so it is copied to the HDD volume (and Drive) by the existing proven transport. The live epoch DB is never moved or renamed.
- **G3, `rows_raw` split.** `option_chain` / `quote_depth` rows (NON_RECOVERABLE) go to an HDD-only DB; `fii_dii` / `participant_*` / `holidays` (RECOVERABLE) stay on the SSD path.
  The classifier already works per dataset name; placement is still per file (`dp_paths.py:427-437`).
- Pi5: seal on the Pi (`/share/pull`), copy to i5 over `LanSsh` (`dp_segsync_transport.py:70-101`), then i5 copies on to its HDD. Pi5 holds no non-recoverable data.

**Power-failure and network-failure contract (no UPS; any step can be cut at any moment).** Every step must satisfy all of:

1. Source is opened read-only (or snapshotted with the backup API); a source file is never modified, renamed or truncated.
2. Copy to a temporary name (`.part`) on the destination volume; `fsync` the file, then `fsync` the directory.
3. sha256 of source and of the copy computed independently; a **separate process** re-reads the destination and compares (read-back), as `dp_segsync.py:1-14` and `data_lifecycle_policy.json` already require.
4. Only a matching hash is atomically renamed (`os.replace` / `mv` on the same volume) to its final name and recorded PROVEN in the ledger; a mismatch leaves only `.part`/`.BAD`, never a final-named file.
5. **Copy-only.** Nothing on the SSD is deleted until `ALLOW_REMOVE=1` is a separate, written Kumar decision, and then only for files with 2 proven copies in different places and a second verify pass (policy `copies.required_proven_before_delete: 2`).
6. **Resumable.** A power cut leaves a ledger of what is PROVEN and what is queued; on restart the run re-copies only unproven segments. A half-copied `.part` is discarded, never reused unverified.
7. Gates: mover refuses if `/volume1` is not mounted, a lock is held, or the destination lacks free space (`ssd_to_hdd_move.sh:9-14`). The IO gate only monitors and never stops a puller.
8. Tests required before this runs (section 5 rows G2 and "Move chain"), each broken on purpose once.

## 8. What this document does NOT prove

- Per-instrument names (the "10,000 instruments, each by name") are not here: that list comes from the broker masters on the boxes (`_state/instruments.db`), which are not in the repo. UNVERIFIED-LIVE.
- How many of the four brokers actually serve each instrument is declared in `dp_families.py` `sources`, not measured per instrument. The measured answer is `dp_maxproof.py` / the coverage ledger on the boxes.
- That the recorders on i7 run from the compose file that mounts HDD (finding 4).
- Whether i5 or i7 currently write any live-only file to SSD (`tools/check_recoverability_placement.py` is the proof; not run).
