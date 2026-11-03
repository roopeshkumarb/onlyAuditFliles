# ADDENDUM 03-11-2026 15:50 IST: end-of-session numbers (changes one conclusion in 01_REPORT_BLK001.md)
Source: files 14 (i5) and 15 (i7), produced by 09_gapdb_script.py (now listing every gap > 30 s) at 15:4x IST, after the session. Rows counted from 09:15. Ticks use the NIFTY 50 token only.
| Recorder | i5 rows | i7 rows | i5 gaps > 30 s | i7 gaps > 30 s |
|---|---|---|---|---|
| ticks (NIFTY token) | 85,363 | 84,268 | 2 (the outages) | 2 (the outages) |
| depth frames | 135,300 | 152,017 | 2 | 3 (+39 s at 15:08:03) |
| upstox frames | 123,915 | 129,384 | 3 (+55 s at 14:24:57-14:25:52) | 6 (+31, 31, 39, 38 s) |
| fyers tbt frames | 75,760 | 72,297 | 2 | 2 |
All recorders on both boxes last wrote 15:35:00-15:35:21 (they stop themselves after the session; at 15:41 the file ages were 358-378 s, as expected).
## What this changes
1. **CORRECTION (16:10 IST, supersedes my first version of this point).** I wrote that the only gaps over 60 s were the two power windows and that livewatch had nothing to catch. That was WRONG for Dhan depth: my gap script merged the `d20` and `d200` connections of `depth_*.db`. Split by the `conn` column: **i5 d20 has 12 silent gaps of 211-240 s between 13:55 and 15:17 (~46 min of ~82), i7 d20 has one (13:59:58 -> 14:04:16, 257 s); d200 had no gap outside the power windows.** The recorder's own status.json logs 'd20 SILENT 199 s while connected - dropping it' (i5 13:59:10; i7 14:03:13 shows 194 s). Cause UNKNOWN. UNPROVEN hypothesis: both boxes use one Dhan account and the 5-socket cap kicks sockets off.
   **Consequence for BLK-001:** livewatch judges the day FILE; d200 keeps writing, so the file stays fresh while d20 (50 contracts) is dead. livewatch as written would NOT have detected this, and its remedy (`docker kill depthrec`) would drop the healthy d200 as well. Per-connection freshness is needed.
2. **The 60 s threshold is too close to normal behaviour for upstox.** The longest non-outage gap is 55 s (i5 upstox, 14:24:57 -> 14:25:52); the i7 has four upstox gaps of 31-39 s. A strict 60 s rule would have been within 5 s of killing a healthy recorder on the i5, and the i7 (load 25-29) is closer still. Earlier support for 60 s (a 4 s maximum in a 150 s sample) was too short a sample. RECOMMENDATION: 90 s from 09:16, and measure per recorder before locking. This is a deviation from the owner's 60 s order and needs his decision.
3. **Row counts differ between boxes** (e.g. depth: i7 +12%; upstox: i7 +4%; fyers tbt: i5 +5%). Cause UNKNOWN: the boxes subscribe to slightly different strike windows, and the outages differ by minutes. Do not treat either box as the complete record.
4. Unchanged: livewatch has still not run against production recorders; the boot script and access routes are untested across a real reboot / from outside the LAN.
