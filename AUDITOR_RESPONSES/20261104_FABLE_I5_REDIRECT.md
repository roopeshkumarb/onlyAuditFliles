# Fable gate: i5 redirect plan (I5_REDIRECT_PLAN_041126) - 04-11-2026 14:10 IST

**Decision: GREEN-WITH-CONDITIONS.** The redirect (drop the three `.env` overrides, recreate the two pullers) is sound. Step 2/3 (160 GB online-backup copy of open DBs) is wrong as written and must be dropped. Code read; i5/i7 read-only; nothing changed.

## Live facts that change the plan (read 14:00-14:08 IST)
- **Both old pullers on i5 are already down**: `fullpuller` Exited(128) 13:37 IST, `puller930` Exited(128) 13:42, `restart=always`, RestartCount 0, no OOM: matches a manual stop. puller930's last line (13:38:24) was a healthy chain snapshot. Kumar's "not stopped until replacement proven" rule is already broken by someone; i5 chain snapshots are lost since 13:38 (i7 pullers and recorders Up, healthy). Tell Kumar.
- IO pressure still 97-98% with both pullers down: they are **not** the IO cause.
- **The HDD folders already hold the same epochs**: `/volume1/docker/datapullers/{upstox,fyers,dhan}/pullerfull_<src>_151026-00xx.db`, identical `epoch_meta`, with their own `pullerfull_<src>_raw_current.db` symlinks pointing at them. HDD copies are older (upstox 68.5 vs 77.5 GB on SSD; fyers 28.5 vs 44.7; dhan 16.1 vs 28.5), last written 03-11 12:33, WAL 0 B, open cleanly.
- `coverage.db`, `jobs_fullpuller.db` (43 queued), `jobs_puller930.db`, `tokens.json`, `_quorum`, `/lease` are all on HDD paths: **the queue, lease and gate need nothing on the SSD**.
- `_state/space_gate.json`: **CLOSED** ("303.4 GB vs budget 100 GB"). The policy file was deployed to `_state` at 13:25 today; before that the gate failed open (jobs ran 13:10-13:15). i7's gate is closed too (248.7 GB).
- On-box compose md5 == repo. `.env` overrides only upstox/dhan/fyers (kite already HDD).

## The six checks
1. **Same epoch, no re-pull: YES, with no copy.** `open_source_db` -> `current_pointer` -> `/data/<src>/pullerfull_<src>_raw_current.db`; the HDD already has that symlink, so `roll_epoch` never fires. `held()` reads `dp_coverage` in `_state` (HDD), never the data file, so windows stay held whatever is mounted. Cost: rows written on the SSD since 23-10 (candles + live-only chain snapshots) stay there until merged.
2. **Online backup at this IO: unsafe and unneeded.** `con.backup()` would hold a WAL read mark for hours on a 1.3 GB-free SSD; copying "to the same relative names" would overwrite the HDD namesakes. Drop it. After the switch the SSD files are closed (WAL 0 B): `cp`+sha256 cold, nice 19, IO <= 90, into a **non-colliding** `/volume1/docker/datapullers_ssd_overflow/<broker>/`, then merge via dbtools/dp_merge under its own approval.
3. **Files:** copy nothing for the switch. Later, cold: the 6 live `.db` files only (`-wal` 0 B, `-shm` not needed). Leave pointers, `.copy_status`, `.integrity`, legacy `<src>_current.db`. The old dir is needed only as the unmerged source: protect it, delete nothing.
4. **Recreate breaks nothing durable:** `resume_sweep()` re-queues `running` jobs at start (seen in the 13:30 log); broker_login/dp_voter untouched; `dp_gate` reads `/lease` (updated 14:02). **But the plan's command is wrong**: `up -d --force-recreate` with no profile or names selects **dp_voter and broker_login** and would recreate the login-lease holder. Use the form below.
5. **Rollback:** restore `.env`, recreate the two: process-complete. Rows written to the HDD epoch meanwhile stay there (their correct home). Rollback re-points writes at a 1.3 GB-free SSD: use it only if the HDD mounts fail.
6. **Rules:** nothing deleted, no open DB copied, live-only snapshots land on HDD. The "not stopped" rule is already violated; this change restores the pullers.

## Corrected steps
1. `cp /volume1/docker/blpro009/.env /volume1/docker/blpro009/.env.bak_041126_<HHMM>`.
2. Remove the three `DP_*_DIR` lines; keep `BOX_NAME`, `DP_MAX_CONCURRENT`.
3. `cd /volume1/docker/blpro009 && /var/packages/ContainerManager/target/usr/bin/docker compose -p datapullers -f docker-compose.datapullers.yml --profile full --profile p930 up -d fullpuller puller930` (the volume change recreates them; never a bare `up`/`down`).
4. Verify: mounts show `/volume1/docker/datapullers/<broker> -> /data/<broker>`; log shows "resume sweep"; no new `pullerfull_*_041126-*.db`; HDD epoch mtimes move.
5. **Gate (owner decision, else "rows_written rises" fails):** with `/data` on HDD, `managed_used_gb` walks the whole HDD tree (>=133 GB of broker folders alone) against `pull_budget_gb=100`, so every queued job stays held; only snapshots run. Kumar either sets a budget for the HDD tree in `_state/data_lifecycle_policy.json` or renames that file aside (restores the pre-13:25 fail-open, logged loudly). `DP_SPACE_ROOTS`/`DP_SPACE_GATE` cannot be set via `.env` (compose does not pass them).
6. Cold SSD copy + merge per (2)/(3), separate approval.

## Not verified
Who stopped the pullers at 13:37/13:42 and why; HDD tree size (`du` timed out); which windows exist only on the SSD (merge-time diff); row-level integrity of the HDD epochs (only `epoch_meta` read).
