# FRIDAY SSD MIGRATION PLAN (04-11-2026)

STATUS: PLAN ONLY. Nothing in this document has been executed. Nothing may be run against
i5, i7 or the Pi 5 until Kumar, Fable and the external auditor have all signed off (3-way
approval, per the owner's standing rule). This file is read-only reasoning built from the
repo in `/home/user/blpro` plus the facts handed to me; no box was reached, no command was
run against <LAN-subnet>.

**Deadline:** this Friday 20:00 IST — no SSD on i5, i7 or Pi 5 may hold data after that time.
Everything goes to HDD (RAID1) + Google Drive. No UPS on any of these boxes is the stated
reason.

**Constraint that shapes everything below:** the old pullers (`fullpuller`, `puller930`,
containers from `docker-compose.datapullers.yml`, project `datapullers`) **keep running**
past Friday, by Kumar's explicit decision, until a new puller system is built and proven.
So this is not a one-time file move — the pullers' *next* write, Friday night and every day
after, must already land on HDD. A single migration of existing files without redirecting
future writes would be full again within a day.

---

## 0. What exists today (read from the repo, not re-measured live)

| Box | SSD | HDD | What the given facts say |
|---|---|---|---|
| i5 | `/volume2`, 205 GB, **~2.3–2.6 GB free (99% full)** | `/volume1` RAID1, 3.5 TB, 2.1 TB free | Pullers already redirected here via `DP_UPSTOX_DIR`/`DP_DHAN_DIR`/`DP_FYERS_DIR`/`DP_KITE_DIR` in i5's local `.env` (not in this repo — each box keeps its own `.env`, confirmed by `.env.example` having no `DP_*_DIR` lines). |
| i7 | `/volume2`, 419 GB, 279 GB free (34% used ≈ 140 GB) | `/volume1` RAID1, 3.5 TB, 1.1 TB free | `docker-compose.datapullers.i7.yml` exists but is explicitly **"PREPARED, NOT STARTED"** — its `DP_SSD_ROOT` defaults to the HDD path, so the puller containers are *not* the ones filling that 140 GB today. What is using it is **unknown from this repo** — see Risk R1. |
| Pi 5 | `/share`, 256 GB (≈110 GB free per the 28-10 measurement in `THREE_SSD_PLAN_281026.md`) | **none** — `config/recoverability.json`'s `protection.devices.pi` says `"hdd": []` and "the Pi has one disk and it is an SSD" | No recorder container runs there. `docker-compose.datapullers.pi_public.yml` and `docker-compose.datapullers.pi_local.yml` are both marked **"PREPARED, NOT STARTED"**. See §4 for the honest finding. |

Two load-bearing documents already in the repo matter a lot here and are **in direct tension
with Friday's rule**:

- `config/recoverability.json` / `docs/framework/data_lifecycle_policy.json` encode Kumar's
  28-10-2026 rule: *"history and data that can be recovered: pull and store to SSD on all
  three (i5, i7, Pi5)"* and are marked `PROPOSED, NOT YET APPROVED`. They are the opposite of
  Friday's "nothing on SSD" rule. Nothing in the repo currently *acts* on them (`dp_placement.py`
  / `dp_shard.py` are built but **not wired in** — `THREE_SSD_PLAN_281026.md`: *"the pullers do
  not call dp_placement yet. Until they do, nothing moves"*), so there is no live code to turn
  off. But the policy document itself will say the wrong thing to the next engineer unless it
  is explicitly superseded. **This plan does not change that file — flagging it is as far as a
  read-only plan goes; the status update is a separate, owner-approved edit.**

---

## (a) Redirect the OLD pullers' NEW writes: SSD → HDD, via `DP_<BROKER>_DIR`, no new code

The mechanism already exists and needs no code change — confirmed in
`docker-compose.datapullers.yml` (services `fullpuller` and `puller930`, both boxes' mounts):

```yaml
- ${DP_UPSTOX_DIR:-/volume1/docker/datapullers/upstox}:/data/upstox
- ${DP_DHAN_DIR:-/volume1/docker/datapullers/dhan}:/data/dhan
- ${DP_FYERS_DIR:-/volume1/docker/datapullers/fyers}:/data/fyers
- ${DP_KITE_DIR:-/volume1/docker/datapullers/kite}:/data/kite
```

The **default** (when the var is unset) is already the HDD path
(`/volume1/docker/datapullers/<broker>`). The SSD path only gets used because i5's local
`.env` currently *overrides* these four vars to `/volume2/datapullers/<broker>` (per the
comments: *"i5 overrides DP_UPSTOX_DIR in its local .env to /volume2/datapullers/upstox"*).
NSE/kite's auth and lease mounts are not overridable the same way and already default to the
HDD path (`_auth`, `pull_lease_i5`), so they need no change.

**Exact change needed, per box:**

- **i5** — in i5's own `/volume1/docker/datapullers/.env` (or wherever that box's compose
  `.env` lives — not in this repo): **delete or comment out** the four lines
  `DP_UPSTOX_DIR=/volume2/datapullers/upstox`, `DP_DHAN_DIR=...`, `DP_FYERS_DIR=...`,
  `DP_KITE_DIR=...`. With them gone, the compose defaults take over and every *new* write goes
  to `/volume1/docker/datapullers/<broker>` (HDD) automatically. **No `docker-compose.datapullers.yml`
  edit required** — the file already defaults to HDD; only the i5-local override needs removing.
- **i7** — nothing to redirect for the old-style `fullpuller`/`puller930` under the *main*
  compose file: it was never pointed at an SSD path there (no override is mentioned for i7 in
  that file). The separate `docker-compose.datapullers.i7.yml` (a *different*, not-yet-started
  puller instance under project `datapullers_i7`) already defaults `DP_SSD_ROOT` to the HDD
  path too, and its own comment says explicitly it must stay that way until Kumar approves
  (T-1184). **Action: confirm i7's `.env` has no `DP_SSD_ROOT` override set, and do not set one
  before Friday.** This is a "don't touch it" rather than a "change it."
- **Pi 5** — `docker-compose.datapullers.pi.yml` remaps every path to `/share/...`, which *is*
  the Pi's only disk (its SSD). There is no `DP_<BROKER>_DIR` override pattern to flip here
  because there is no second disk to point at (see §4). Nothing to redirect because nothing is
  running.

**After the env change, restart just the two puller services, nothing else**, since the
compose file's own warnings are explicit about blast radius:

```
docker compose -p datapullers -f docker-compose.datapullers.yml --profile full --profile p930 up -d
```

This recreates only `fullpuller`/`puller930` (profile-gated) with the new mount; `dp_voter`
and `broker_login` (no profile, shared quorum/login) are unaffected, and a bare `down` must
still never be used (that is the exact 12-10-2026 incident the file's banner documents).

**Symlink note (directly relevant here):** `*_current.db` / `*_raw_current.db` in each
broker's SSD folder are symlinks to the live file of the day. Once the env var points the
*mount* at the HDD folder, the container's `/data/<broker>` is simply a different directory —
the symlinks that currently live under `/volume2/datapullers/<broker>/` are **not followed or
moved by this step**, they are just no longer the active write target. They become stale and
should be either removed or left as dead links once step (b) has copied/verified everything
under them; do **not** attempt to "fix" them by hand while they're still potentially read by a
running container — this is exactly the operation that broke two symlinks for several minutes
before.

---

## (b) One-time move of EXISTING SSD data, with `ssd_to_hdd_move.sh`

Read in full (`/home/user/blpro/tools/ssd_to_hdd_move.sh`). What it already guards, verified
line-by-line:

- **Mount guard** — refuses if `/volume1` is not an actual mountpoint (`mountpoint -q` or
  `/proc/mounts` check) before doing anything.
- **Single-run lock** — `mkdir "$LOCK"` as the lock primitive; a second concurrent run refuses
  cleanly instead of racing.
- **Age guard** — skips any file modified in the last `MIN_AGE_H` hours (default **168 h = 7
  days**). This is the main protection against moving something still being actively written.
- **Size guard** — only considers files ≥ `MIN_BYTES` (default 100 MB); small/working files
  are left alone.
- **Symlink guard (the fix after the earlier incident)** — before touching a file, it checks
  `find "$SRC" -type l -lname "*$base"` and **skips** any file a symlink in the tree points at.
  This is exactly the protection the two broken `*_current.db` symlinks needed and didn't have
  before 03-11.
- **Open-database guard** — skips if a non-empty `-wal` sidecar exists (possible unflushed
  data); additionally, when `ALLOW_REMOVE=1`, also skips if a `-shm` sidecar exists (open or
  recently-open SQLite handle). Note this `-shm` check is **only enforced when `ALLOW_REMOVE=1`** —
  in copy-only mode it will still *copy* a file with a live `-shm` next to it (copy-only is
  non-destructive either way, so this is low-risk, but worth knowing before trusting a
  copy-only dry run as proof nothing is open).
- **Copy-then-hash-then-rename** — copies to `$dest.part`, `sync`s, `sha256sum`s both source and
  copy, re-checks the source's mtime didn't change mid-copy, and only then atomically
  `mv`s the `.part` into place. A hash mismatch or a source that changed during the copy aborts
  that file only (`continue`), not the whole run.
- **Free-space guard on the destination** — stops the whole run if the HDD has less than
  `2× file size + 10 GiB` free.
- **Destination-exists guard** — refuses to overwrite an existing file at the destination.
- **Default is copy-only** (`ALLOW_REMOVE=0`): verified copy is left in place, source is
  **never deleted** unless `ALLOW_REMOVE=1` is explicitly set, and even then the source is only
  `rm -f`'d after its own existence is re-checked (`[ ! -e "$f" ]`), with a `.MOVED_TO_HDD`
  tombstone (dest path + sha256) written where the file was and an append-only `MANIFEST.tsv`
  row recorded.

**What it does NOT do, and what still needs an owner decision before `ALLOW_REMOVE=1`:**

1. **It does not touch the symlinks themselves.** It skips the file a symlink points at, but it
   never updates, relinks, or removes the symlink. After a move, the dangling
   `*_current.db` / `*_raw_current.db` symlinks still point at wherever the live file is — which
   is fine as long as step (a) has already redirected new writes to the HDD path and the
   *currently live* file (today's, <168 h old) is correctly skipped by the age guard. **The
   owner decision needed:** confirm the order of operations is (a) first, (b) second, never
   reversed — moving old data before redirecting new writes is safe (age guard protects the
   live file); redirecting writes before the old data is moved just means old and new data
   temporarily live in different trees, which is also safe. Either order is fine *individually*,
   but they must both land **before Friday 20:00**, and (a) should happen first in practice so
   the SSD stops growing while (b) is still copying.
2. **`ALLOW_REMOVE=1` is a real decision, not a formality.** Copy-only satisfies "a verified
   copy exists on HDD" but does **not** satisfy "nothing may remain on SSD" — the source files
   are still sitting on `/volume2` at 99% full on i5 either way. Given i5 has only 2.3–2.6 GB
   free, copy-only mode cannot even be meaningfully run repeatedly (nothing is being freed), so
   **this migration specifically requires `ALLOW_REMOVE=1` to actually relieve i5's SSD** — this
   is the single biggest owner decision in this plan, not a detail. The script's own guards
   (hash-verify before remove, re-check existence) make the deletion itself safe engineering-wise;
   what needs Kumar/Fable/auditor sign-off is the *policy* decision to delete at all, consistent
   with the standing "2 proven copies in different places before delete" rule in
   `data_lifecycle_policy.json` (`copies.required_proven_before_delete: 2`,
   `places: [box_hdd, peer_box, drive]`, `read_back_by_separate_process: true`). **The HDD copy
   this script makes is only ONE of those two required copies — Drive is the second, and per
   that same policy "the SSD copy never counts."** So in strict policy terms, `ALLOW_REMOVE=1`
   should not be flipped until the Drive copy (part c) is *also* confirmed, not just started.
3. **`MIN_AGE_H=168` (7 days) means most of i5's recent data will be skipped entirely** by a
   run before Friday if run with defaults — only files untouched for a week qualify. Given i5 is
   99% full *today*, the big dated snapshot files described in
   `config/recoverability.json`'s `measured_28_10_i5` note (`pullerfull_upstox_*.db` 72 GB,
   `pullerfull_fyers_*.db` 43 GB, `pullerfull_dhan_*.db` 27 GB — all dated-snapshot files, not
   the live `_current.db`) are almost certainly old enough to clear that bar and are exactly
   what should move. **Owner decision needed:** whether `MIN_AGE_H` can safely be lowered for
   this one Friday run to catch anything written in the last few days too, or whether 7 days is
   kept as-is and a second pass is scheduled next week for the newer files (which, after step
   (a), will no longer be arriving on the SSD anyway).
4. **It only ever handles ONE `SRC`/`DST` pair per invocation.** It needs to be run once per
   broker-folder/root that holds qualifying data on each box (i5's `/volume2/datapullers`, i7's
   `/volume2` once its content is inventoried per Risk R1, and nothing for the Pi since it has
   no second disk — see §4). Each invocation is independent; there is no fan-out across boxes
   built in, so each box's run is a separate, explicitly-approved step.

**No change to the script is proposed or needed for this plan** — it already does exactly what
a careful one-time SSD→HDD move should do. The only thing to decide is *when to flip
`ALLOW_REMOVE=1`* and *on which roots*, both owner decisions, not engineering ones.

---

## (c) `tools/ssd_backup_gdrive.py` — what it backs up today, and the gap

Read in full. Today it is scoped like this:

```python
STAGE_ROOT = ... "/volume2/ssd_backup_gdrive" if os.path.isdir("/volume2") else ~/gdrive_backup/ssd_pi5
SSD_ROOTS = {
    "i5":    ["/volume2/datapullers", "/volume2/blpro_hot"],
    "pi5":   ["/share/CC-Roopesh", "/share/blpro"],
    "j1800": [],  # j1800 HDD is RAID1, not at risk
}
```

Three concrete gaps, in order of how badly they'd break the Friday rule if not fixed first:

1. **The staging folder it writes its own backups INTO is itself on the SSD on i5**
   (`/volume2/ssd_backup_gdrive`), to be picked up later by Synology Cloud Sync. On a box that
   is 99% full with 2.3–2.6 GB free, this tool **cannot even run** today — there is no room to
   stage a snapshot, and worse, if it ever did run it would be *adding* to the exact SSD the
   Friday rule wants emptied, not relieving it. This has to be fixed before relying on this tool
   at all for i5: `STAGE_ROOT` needs to point at an HDD path (e.g.
   `/volume1/docker/ssd_backup_gdrive_stage`) so Cloud Sync — or an equivalent rclone-to-Drive
   step — lifts data to Drive straight from the HDD, never from the SSD. This is a **required
   code/config change**, not optional, if this script is to be part of the Friday plan.
2. **`"j1800": []` is wrong given the facts in this task, and is itself a naming trap.**
   `j1800` is the i7's `BOX_NAME` in the fleet (confirmed in `docker-compose.datapullers.i7.yml`:
   `BOX_NAME: "j1800"  # the i7's name in the fleet list`). The comment `"j1800 HDD is RAID1,
   not at risk"` talks about the *HDD*, but says nothing about the i7's **SSD**
   (`/volume2`, 419 GB, 279 GB free — i.e. ~140 GB in use, origin unknown, Risk R1 below). As
   written, this script backs up **nothing at all for the i7**, SSD or otherwise. If any of that
   140 GB needs a Drive copy by Friday (it does, if it's going to be deleted off the SSD per
   part (b)), `SSD_ROOTS["j1800"]` needs a real entry once Risk R1 is resolved — i.e. once
   someone has actually looked at what is on i7's `/volume2`.
3. **After part (a) and (b), the puller data simply will not be under `/volume2/datapullers`
   on i5 any more** — it will be under `/volume1/docker/datapullers`. `discover_ssd_data()`
   only walks the roots named in `SSD_ROOTS`, which are hard-coded to the SSD paths. Post-move,
   a backup run with the current `SSD_ROOTS` would walk an increasingly empty `/volume2/datapullers`
   and quietly report "0 items to back up" — looking healthy while backing up nothing. **This is
   the central design question for part (c):** does this tool get:
   - **Option A — rename its job.** Add an `HDD_ROOTS` dict (or just repoint `SSD_ROOTS`'s
     values) at the post-migration HDD paths (`/volume1/docker/datapullers`,
     `/volume1/docker/blpro_hot` or wherever `blpro_hot` ends up) and keep calling the daily
     Drive sync from there. Simplest change, same code shape, same guards (SQLite backup API,
     integrity check, row-count compare, retain 7 daily/4 weekly) — they don't care whether the
     source is SSD or HDD. The `_wal`/`_shm` exclusion and the dated-snapshot exclusion
     (`_\d{6}-\d{4}\.db$`) logic carries over unchanged.
   - **Option B — keep it SSD-only and add a second, HDD-focused script/mode.** More honest
     naming, more surface to maintain. Not recommended unless there's a reason to keep backing
     up a (hopefully near-empty) SSD separately from the HDD going forward.
   **Recommendation for the write-up only (not actioned): Option A**, since Friday's whole point
   is that nothing interesting remains on SSD — a script still named for SSD but pointed at the
   HDD roots is a one-line change (plus the `STAGE_ROOT` fix above) and keeps the proven
   SQLite-backup-API + verify + manifest machinery exactly as audited.
4. **One more gap worth naming directly: the dated-snapshot exclusion may be hiding the biggest
   files from Drive entirely, today, independent of Friday.** `discover_ssd_data()`'s own
   comment says it skips `*_\d{6}-\d{4}\.db` files because "those are local backups already" —
   but the measured i5 SSD content named in `config/recoverability.json`
   (`pullerfull_upstox_151026-0031.db`, `pullerfull_fyers_151026-0030.db`,
   `pullerfull_dhan_151026-0031.db` — 72 GB / 43 GB / 27 GB) matches that exact dated-filename
   pattern and is described elsewhere in the same repo as the *main* puller output, not a
   "local backup" of anything. If that reading is right, this script has never actually backed
   up the largest class of puller data to Drive — it has only ever backed up the small
   `_current.db` symlink targets and the `_state`/`_auth`/`_config` directories. **This needs
   confirming with Kumar/the puller code before Friday**, because if true, the Drive copy the
   Friday rule wants is not just "needs a new HDD_ROOTS mode" — it currently has a content gap
   that predates this migration and should be fixed in the same pass.

---

## (d) The Pi 5 — honest finding, not a hypothetical

**What is actually deployed on the Pi today, read from the compose files:**

- `docker-compose.datapullers.pi.yml` — an override of the main compose file that remaps
  `dp_voter`/`broker_login`/`fullpuller`/`puller930` paths to `/share/pull/datapullers`. This is
  the file that *would* run the same old-puller services on the Pi if invoked with it, but
  nothing in the repo or in the given facts says it is currently `up`.
- `docker-compose.datapullers.pi_public.yml` — header says **"PREPARED 28-10-2026, NOT STARTED"**
  in plain text, defines `pi_public_puller` (nse/yahoo only, `/mnt/data/supervisor/share/pull/datapullers_pi`).
- `docker-compose.datapullers.pi_local.yml` — header says **"PREPARED, NOT STARTED"**, defines
  `pi_fullpuller`/`pi_puller930` as the *replacement* for `pi_public_puller`, explicitly not to
  be run alongside it.
- The main `docker-compose.datapullers.yml`'s only mention of the Pi as *currently* active is
  `dp_voter` (quorum voter, part of the 3-replica login-lease register, "runs on ALL THREE
  boxes"). It holds no credential and pulls no market data — it writes a small lease file under
  `VOTER_ROOT: /data/_quorum`, which on the Pi (per `pi.yml`'s remap) is
  `/share/pull/datapullers/_quorum`, i.e. **on the Pi's one and only disk, which is an SSD.**

**Conclusion, stated plainly: the given task brief is right — nothing substantial runs on the
Pi today.** No puller, no recorder, no live feed. The only thing writing to the Pi's SSD today
is `dp_voter`'s tiny quorum-lease state, which is operational state, not held market data, and
is inherently regenerable (a lease is re-elected, not historical).

**What "Pi5 data moves to i5" should concretely mean, given that reality:**

There is close to no *data* to move — this is not a backlog-clearing exercise the way i5's is.
The concrete, doable actions by Friday are:

1. **Confirm, don't assume, that `pi_public_puller`/`pi_fullpuller`/`pi_puller930` are not
   running.** The repo says "prepared, not started" as of 28-10; that is six days old by the
   time of this deadline and nobody has re-verified it live (this plan cannot — no SSH access).
   This is a one-line check someone with box access needs to do before Friday, not an assumption
   to carry into the deadline.
2. **If they are still not running (expected): there is nothing to redirect and nothing to
   move.** "Pi5 data moves to i5" in that case means at most moving `dp_voter`'s `_quorum`
   lease-state directory — which is tiny (KB-scale lease tokens, not GB-scale market data) and
   arguably doesn't need "moving" at all since it is ephemeral and re-created by the next
   election. If the letter of "nothing on SSD" must be honored exactly, the only real option is
   to relocate `VOTER_ROOT` for the Pi's `dp_voter` instance off `/share` entirely — but the Pi
   **has no second local disk** (`config/recoverability.json`: `"pi": {"ssd": ["/share"], "hdd":
   []}`, "the Pi has one disk and it is an SSD"). The only place that state could go that is not
   the Pi's SSD is a network path to i5's or i7's HDD, which the voter's design explicitly does
   not do today (`VOTER_ROOT: /data/_quorum` is a local bind mount, by design, because the whole
   point of a 3-way quorum is that each replica is independent — pointing the Pi's replica at a
   network path on i5 would make it not an independent replica any more, undermining the thing
   it exists for). **Recommendation: leave `dp_voter`'s quorum state where it is and treat it as
   an explicitly accepted exception to the "nothing on SSD" rule, on the grounds that it is
   operational lease state, not data, and is already covered by the house rule that "the Pi5
   holds no non-recoverable data" (it holds no data of any kind right now).** This needs an
   explicit yes from Kumar, not a silent exception — it's small, but "nothing may remain" is an
   absolute statement and this plan should not quietly carve out an exception without saying so
   out loud.
3. **If a live-box check finds a puller *is* actually running on the Pi (contradicting the
   repo's "not started" headers) — stop treating this as a non-event.** In that case, the data
   under `/mnt/data/supervisor/share/pull/datapullers_pi` (or `/share/pull/datapullers`) is real
   and growing on the Pi's only disk with no HDD to fall back to locally, and "Pi5 data moves to
   i5" becomes a real, non-trivial copy-off-box operation: there is no `DP_<BROKER>_DIR`-style
   redirect to flip on the Pi (there's no second disk for it to point at), so the only two
   options are (i) stop the Pi puller entirely and let i5/i7 absorb its tiny nse/yahoo-only load
   (trivial, since it's `DP_SOURCES_ONLY: nse,yahoo` and already capped at
   `DP_MAX_CONCURRENT=2`), or (ii) have it write across the network to i5's HDD path directly —
   which is a real design change (the Pi's pullers have never been run against a network mount;
   `pi_local.yml`'s own banner says *"SQLite files stay on a LOCAL path; never a network
   mount"* — a deliberate choice to avoid SQLite-over-network corruption risk) and should not be
   improvised under Friday's deadline pressure. **Recommendation if this branch turns out to be
   true: stop the Pi puller (option i) rather than invent a network-mount path this week.**

---

## (e) Risk list

| # | Risk | Mitigation already built in | Still missing / needs a decision |
|---|---|---|---|
| R1 | **i7's SSD has ~140 GB in use and nobody knows what it is.** `docker-compose.datapullers.i7.yml` pullers are "prepared, not started," so it isn't old-style puller data by the compose file's own account. Could be Synology package data, Docker images/layers, logs, or something unrelated entirely. | None — this is a visibility gap, not a code gap. | **Required before touching i7 at all:** run `tools/fleet_truth.py` (or an equivalent inventory) against the live i7 and get an actual directory listing of `/volume2` before deciding what, if anything, `ssd_to_hdd_move.sh` should target there. Moving/deleting unidentified Docker image layers or Synology package state would be a self-inflicted outage, not a data-safety win. |
| R2 | **Dangling symlinks.** `*_current.db`/`*_raw_current.db` point at the live file of the day; an earlier manual move attempt broke two of these for several minutes. | `ssd_to_hdd_move.sh`'s symlink guard (`find -type l -lname "*$base"`) already refuses to move any file a symlink points at. | The guard protects the *move* step; it does nothing about the stale symlink left behind once the env-var redirect (part a) moves new writes elsewhere. Someone needs to clean up or re-point those SSD-side symlinks **after** confirming (via the new HDD path) that the puller is healthy, not before. |
| R3 | **Open database / unflushed WAL during the move.** A puller could be mid-write when `ssd_to_hdd_move.sh` runs. | Non-empty `-wal` sidecar check (always on); `-shm` sidecar check (only when `ALLOW_REMOVE=1`); hash-and-mtime re-check before the final `mv`; `MIN_AGE_H` (168 h default) keeps it away from anything recently touched at all. | The `-shm` check not applying in copy-only mode means a "successful" dry-run/copy-only pass is not proof that nothing was open — it's proof nothing was *deleted* unsafely. Don't read a clean copy-only run as "safe to flip ALLOW_REMOVE=1 with no further checks." |
| R4 | **IO load during the move itself.** i5 is already the box under the most pressure (99% full, presumably also the busiest disk). Copying tens of GB off it competes with live pulling. | `nice cp`/`nice sha256sum` (lower scheduling priority); the script's own one-run lock prevents overlapping copies; `data_lifecycle_policy.json`'s `io_gate` is advisory-only by design and explicitly must never throttle a puller — consistent with the standing rule in this repo that pulling is never paused for IO. | No time-of-day guard in `ssd_to_hdd_move.sh` itself (unlike `ssd_backup_gdrive.py`, which has explicit `EXCLUDED_WINDOWS` for market hours and nightly sync). **Recommendation: run the move outside 09:00–15:40 IST market hours and outside the 02:10–06:00 nightly sync window, by hand, the same windows the backup script already respects** — not a code change, just a scheduling discipline borrowed from the sibling tool. |
| R5 | **Deleting before the Drive copy is actually verified, not just started.** `data_lifecycle_policy.json` requires 2 proven copies in different places before delete, and says explicitly the SSD copy never counts. | `ssd_to_hdd_move.sh`'s hash verification covers the HDD copy. | There is currently no automated check that gates `ALLOW_REMOVE=1` on the Drive copy having *also* landed and been verified — that ordering has to be enforced by hand/process this week (do the Drive backup first or in parallel, confirm its manifest, then flip `ALLOW_REMOVE=1`), since part (c)'s gaps (STAGE_ROOT on SSD, missing i7 entry, dated-file exclusion, post-move path) all need fixing first anyway. |
| R6 | **Policy document contradiction surviving past Friday.** `config/recoverability.json`/`data_lifecycle_policy.json` currently say recoverable data *belongs* on all three SSDs. Nothing live acts on that today (`dp_placement`/`dp_shard` not wired in), but the documents are there for the next person (or the next Claude session) to read. | N/A — this is a documentation risk, not a running-system risk. | Needs an explicit owner-approved status update to those two files once Friday's rule is confirmed as the standing policy (or scoped as temporary), so the next reader doesn't re-point a puller back at an SSD "per policy." Out of scope for this read-only plan to edit unilaterally. |
| R7 | **Pi quorum exception left unspoken.** See §4.2 — `dp_voter`'s lease state is a small, accepted exception to "nothing on SSD." | N/A | Needs Kumar's explicit yes, in writing, that this one exception is accepted — not left as an unstated gap in an otherwise absolute rule. |

---

## Summary of actions, gated on 3-way approval

1. **(a)** Remove the `DP_UPSTOX_DIR`/`DP_DHAN_DIR`/`DP_FYERS_DIR`/`DP_KITE_DIR` overrides from
   i5's local `.env`, restart only `fullpuller`+`puller930` with
   `--profile full --profile p930 up -d`. Confirm i7's `.env` has no `DP_SSD_ROOT` override and
   leave it that way. No code changes.
2. **(b)** Run `tools/ssd_to_hdd_move.sh` against i5's `/volume2/datapullers` (and, once R1 is
   resolved, i7's `/volume2`), outside market hours / nightly sync, copy-only first, then
   `ALLOW_REMOVE=1` only after the Drive copy in (c) is verified — not merely started.
3. **(c)** Before relying on it at all: move `STAGE_ROOT` off the SSD on i5; add or fix the
   i7/`j1800` entry in `SSD_ROOTS`; repoint (or add an `HDD_ROOTS` mode) at the post-migration
   HDD paths; confirm with Kumar whether the dated-snapshot exclusion is hiding the largest
   puller files from Drive and fix if so.
4. **(d)** Verify live whether any Pi puller is actually running (repo says no, six days stale).
   If no: accept `dp_voter`'s tiny quorum state as a named, approved exception to "nothing on
   SSD," or explicitly decide otherwise. If yes: stop it rather than inventing a network-mount
   design this week.
5. **(e)** Carry R1–R7 into the sign-off conversation explicitly — none of them block writing
   this plan, but several (R1, R5, R7) block safely *executing* it.

Nothing above has been run. This document is the artifact for Kumar / Fable / the external
auditor to review before anything in it touches a live box.
