# BLK-001 EXTERNAL AUDIT REPORT: data-freshness watchdog ("livewatch") + the 03-11-2026 power incident
Prepared 03-11-2026 ~13:50 IST (GMT+5:30) for an outside auditor. Everything here is ADVISORY infrastructure for a retail NIFTY 50 data-capture system (AUTO_TRADE_ALLOWED=False; no orders are placed by anything in this package).
Rule used throughout: a claim is stated only if a file in this folder or a named command shows it. Otherwise it is marked UNKNOWN / NOT TESTED. UNKNOWN is never read as zero.

## 1. What BLK-001 is, and what was delivered
**Order (owner, Kumar):** during the session, if now - last_data > 60 s for a live-only recorder, run `docker kill <container>` so a dead socket is replaced. Docker status "Up" is not data (on 02-11-2026 the i7 Dhan depth socket closed at 13:58 and never reopened while `docker ps` said Up).
**Delivered:** `02_livewatch.py` (stdlib only, python 3.8, ~235 lines), judged by DATA written, not by container state.
- Watches 4 recorders: tickrec, depthrec, upstoxrec, fyerstbt (day files `ticks_/depth_/upstox_/tbt_YYYYMMDD.db`).
- last_data = newest of (status.json `last_tick`, mtime of the day file or its -wal).
- Kills with `docker kill`, waits, checks `.State.Running`, and if the restart policy did not bring it back runs `docker start`.
- Refuses any name outside the 4 (hard NEVER_TOUCH list: cloudflared, portainer, blpro_09, ...).
**Status: written, tested, proven on a disposable container on the i5. NOT running as a daemon on any box. Not yet approved by the owner.**

## 2. Deviations from the order (each is a decision for the auditor to challenge)
| # | Order | What the code does | Reason (evidence) |
|---|---|---|---|
| 1 | 60 s rule from 09:00 | session start 09:16 | on 03-11 the recorders' own guards dropped sockets silent 197-210 s at 09:11-09:13 (pre-open is quiet); a 09:00 rule would kill every recorder every morning |
| 2 | unlimited kills | max 3 kills/container/hour, then ESCALATE file + CRITICAL and stop | a kill loop under a broker connection cap (Dhan: 5 sockets) or outage flaps forever and loses more data than it saves |
| 3 | (silent) | no day file by 09:20 with instruments=0 counts as dead | the i7 Fyers TBT wrote no file on 29-10, 30-10, 02-11 (folder listing); a file-age rule can never see a missing file |
| 4 | (silent) | weekends only skipped; NSE holidays not known | on a holiday at most 3 harmless restarts per recorder |

## 3. Evidence (files in this folder)
| Claim | Evidence | Result |
|---|---|---|
| 9 unit tests pass | `06_unit_tests_output.txt`, `03_test_livewatch.py` | Ran 9, OK (13:41 IST). Tests use a fake `docker` script, so they prove the decision logic, not Docker itself |
| Tests can fail (not vacuous) | `05_mutation_log.txt`: 5 deliberate code breaks (threshold reversed, kill replaced, stranger-guard removed, kill bound removed, session guard removed) | each broke at least 1 test; the file was restored after each. Baseline OK |
| Works on a real box | `04_proof_i5_raw.txt` (machine-captured, 12:24 IST, i5) | stale probe file (5 min old) -> dry run names ONLY `lwtest_rec`; live run killed it; policy did NOT restart it; the `docker start` fallback did (running again 12:25:06); a fresh file killed nothing |
| Normal write gaps are small | measured 03-11 during session on i5: longest gap between writes of all four recorders 4 s (150 s window, 2 s sampling) | supports a 60 s threshold; sample is 150 s only |
| Restart policy cannot be trusted | proof run D->E above; plus after a Docker service restart (i7, 13:56 02-11) and after the 03-11 power event, `unless-stopped` containers stayed down | this is why the `docker start` fallback exists |

**Honest limits of the proof.**
1. The real-box proof used a disposable container. The 4 production recorders were never killed by livewatch.
2. Section G of `04_proof_i5_raw.txt` ("production recorders untouched") is EMPTY: that run happened right after the power event, when the production recorders were down. The earlier proof run (12:02 IST, same script) showed them Up 19 h, but its raw file is not in this folder (UNVERIFIABLE by you).
3. The 60 s threshold is proven only against a 150 s sample on one box on one day.
4. Two instances of restart logic now exist (livewatch.py and `dp_watchdog.py`, which does `docker restart` of stalled recorders, max 2/h). If BLK-001 is approved, the old restart must be switched off or they will fight. Not done.

## 4. The 03-11-2026 power incident (found while preparing this report)
Measured from inside the day files (`09_gapdb_script.py`; rows with recv_ts >= 09:15; gaps > 60 s listed; ticks measured on the NIFTY 50 token 256265 only):
| Recorder | i5 gap 1 | i5 gap 2 | i7 gap 1 | i7 gap 2 |
|---|---|---|---|---|
| ticks | 12:08:36 -> 12:26:05 | 12:42:18 -> 12:48:23 | 12:09:16 -> 12:30:51 | 12:42:16 -> 12:48:30 |
| depth | 12:08:06 -> 12:27:06 | 12:42:07 -> 12:50:44 | 12:09:31 -> 12:31:20 | 12:42:08 -> 12:48:45 |
| upstox | 12:08:16 -> 12:27:58 | 12:42:08 -> 12:51:25 | 12:08:29 -> 12:30:57 | 12:42:08 -> 12:48:36 |
| fyers tbt | 12:08:20 -> 12:28:47 | 12:42:07 -> 12:48:59 | 12:08:46 -> 12:31:48 | 12:42:07 -> 12:48:30 |
Each recorder on each box has exactly 2 gaps > 30 s since 09:15 (full output in files 07 and 08).
- **Both boxes were down at the same time, twice** (~12:08-12:26 and ~12:42-12:48). Live-only data (ticks, depth, upstox frames, fyers TBT) for those windows exists on NEITHER box. Two-box redundancy gave no protection because the cause is common to both. INFERENCE (not proven): site power loss; no UPS; the Pi, on the same network, stayed up (uptime 2 d 22 h).
- Box uptimes at 12:51-12:53 were 7-9 min, i.e. second boot ~12:44; first boot ~12:16 (uptime 12 min at 12:28).
- Docker `restart: unless-stopped` did not restart containers after either boot. Recorders were restarted by hand/script at 12:26-12:31 and again 12:45-12:51 (`recover_loop.log` not included; gap end times above are the evidence).
- livewatch would NOT have prevented this loss: a powered-off box has no watchdog. It addresses a different failure (silent socket death while Up).
- At 13:26 IST all 8 recorder day files were still being written (-wal mtime within 6 s), sizes growing. No further gap > 30 s.
**Remedy delivered (untested on a real reboot):** `10_boot_start_containers.sh` (waits for Docker, then `docker start` in a fixed order; no-op on running containers). Needs a DSM boot-up Task Scheduler entry (root) on each box: NOT installed; it needs DSM admin login. File is on both boxes (md5 3758a9cc1f198d187258fccda8da3238, verified identical).

## 5. Remote-access resilience (owner leaves for offshore on 5th)
See `12_ACCESS_ROUTES.md`. Summary of measured state: LAN mesh between i5, i7 and Pi works in every direction (6 of 6 directed pairs tested); Cloudflare SSH works for i5 and the Pi; the i7 has NO working Cloudflare route (its hostname returns Bad Gateway) and the Pi's second hostname is also dead. `11_box_reach.sh` tries every route in order.

## 6. Questions for the auditor (please answer each)
1. Is judging "last data" by file/-wal mtime a sound liveness signal for SQLite WAL writers? Which failure would keep the mtime fresh while data is bad (e.g. a recorder writing only heartbeats or error rows)?
2. Is `docker kill` + `docker start` fallback the right action versus `docker restart`? (The old watchdog uses restart; this one kills as ordered.)
3. 60 s from 09:16 and 3 kills/hour: too tight, too loose? What breaks at the 09:15 open and in a mid-session broker outage?
4. Should livewatch run on the host (as designed, so a Docker restart cannot take it down) or as a container? It currently dies on a reboot unless a boot task starts it.
5. Is it acceptable that kills can lose the in-memory buffer of a recorder (data written since its last commit)? UNKNOWN: commit interval per recorder was not measured.
6. Single-site power is the biggest measured loss. Is a UPS + graceful-shutdown the first-priority fix ahead of any software watchdog?
7. Any claim above that is not supported by a file in this folder?

## 7. DONE WITH PROOF / PENDING / NOT TESTED / BLOCKED
**DONE WITH PROOF:** 9 tests OK; 5 mutations caught; disposable-container kill/start proof on i5; 2 data gaps per recorder per box measured; all 8 day files fresh at 13:26; boot script on both boxes with md5.
**PENDING:** owner verification of BLK-001; switch off old restart in dp_watchdog.py; start livewatch (host daemon) on both boxes; DSM boot task; commit-interval measurement; BLK-002..BLK-010 NOT started.
**NOT TESTED:** livewatch against the 4 production recorders; livewatch as a daemon across a reboot; boot script across a real reboot; commit interval; behaviour on an NSE holiday.
**BLOCKED:** DSM boot task and Cloudflare dashboard changes need owner logins.
