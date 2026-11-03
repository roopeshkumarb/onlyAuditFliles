# AUDIT SCOREBOARD, 02-11-2026: who audited, what the list is, who said what, what I accepted and refused

Kumar asked: who are the three auditors, where is the proposed list, what did they answer, what was agreed and not agreed. This file is the one place for both sides. Plain words. Nothing here is approved until Kumar says so.

## 1. WHO THE AUDITORS ARE (no names hidden)

| # | Who | What it is | What it saw | What it did |
|---|---|---|---|---|
| EXT-1 | the AI chat YOU pasted the first live-only package into (I do not know which product) | an outside AI, answers came through you | package V1 (4 files) | answered L1-L7, verdict APPROVE WITH CONDITIONS |
| AGENT A | "Instruments and limits" | an AI agent started by me, fresh context, read-only, same model family as me | package V2 files 001-004 only | counted contracts on i5 and i7, compared them, checked limits as written in file 002. Verdict APPROVE WITH CONDITIONS |
| AGENT B | "Reliability" | same kind of agent | package V2 files 001-004 only | Dhan sockets, Fyers TBT coverage, checked each row of the first reconciliation, listed ways data can be lost silently. APPROVE WITH CONDITIONS |
| AGENT C | "Skeptic" | same kind of agent, allowed to use the web | file 002 only | tried to prove the list wrong from the vendors' own documentation. FAILED TO OPEN the vendor sites (blocked in this session), so it verified NOTHING. It answered from forum posts. APPROVE WITH CONDITIONS, but see the weakness below |

**Honest weakness:** agents A, B, C are the same AI family as me. They are independent of this conversation, not independent of my training. They catch my mistakes; they are not a substitute for your outside auditors. The outside AIs you use are the real second opinion. Earlier today three outside AIs audited the DATA LIST (two on the first package, one on the second), all scored it PARTLY.

## 2. THE LIST I PROPOSED (so you can read both sides)

### 2a. Live-only data per broker (full text with quotes: docs/framework/LIVE_ONLY_PER_BROKER_021126.md)
| Broker | Only available live (no history endpoint) | Recorded by us today? |
|---|---|---|
| Upstox Plus | market data feed (ticks, 5-level, 30-level depth, closing-auction fields), option chain with bid/ask and Greeks, option Greeks, quotes | feed: YES (`upstox_live` files, about 45 contracts); chain: YES in puller DB; Greeks, quotes, auction fields: NO |
| DhanHQ | 20-level and 200-level depth, live feed, option chain, quotes, closing-auction feed | depth: YES (50 contracts 20-level + 1 contract 200-level); chain: YES in puller DB; auction feed: NO |
| Kite Connect | websocket ticks (5-level depth + OI), quote snapshots | ticks: YES (160 tokens on i5); quote snapshots: UNKNOWN. Kite does not serve expired options at all |
| Fyers Prime | 50-level TBT depth, data socket quotes, option chain, quotes with auction fields | TBT: YES but thin (i5 four days, i7 three days, one of them empty); chain: YES in puller DB; data socket: NO |
| NSE | live option chain, live indices | NO recorder found; NSE says scripted collection is not allowed (unread primary text) |
Fyers seconds candles are NOT live-only (30 trading days of history): moved to a rolling-window list.

### 2b. Exact instruments recorded (every name, per box)
In the audit package: `003_INSTRUMENTS_I5` and `004_INSTRUMENTS_I7`. Summary: Dhan 51 per box (monthly expiry 2026-11-23, 25 strikes x CE/PE + the Nov future), Upstox 45 per box (same monthly expiry + India VIX + Nifty 50), Kite 160 on i5 / 148 on i7 (weekly 2026-11-03 AND monthly 2026-11-23, Nov and Dec futures, NIFTY 50, INDIA VIX).

## 3. WHAT EACH SIDE SAID, AND WHAT I DID

### 3a. EXT-1 (the outside AI you pasted)
| Point | Agree? | Why |
|---|---|---|
| Fyers seconds candles are not live-only | AGREE | the list itself says 30 trading days |
| Upstox news has a 7-day window | AGREE | file says so |
| Recorders need a data-freshness check, not only "container is up" | AGREE | built and deployed tonight (below) |
| Add `upstox_live`, `fyers_tbt`, `ticks_` to recoverability rules | PARTLY | `tick` and `tbt` already matched those names; `upstox_live` did not, so I added it |
| "Exit code 137 means out of memory" | REFUSE | 137 is a kill signal. The i7 recorders were killed two minutes after the Docker service restarted. Memory is unproven |
| "Move recorders to systemd" | REFUSE | needs admin rights on the NAS that this session does not have |
| "The pattern `news` might not match news_events" | REFUSE | I tested it: it matches |
| "Set memory limits on containers" | NOT DONE | no evidence memory is the cause |

### 3b. Agents A, B, C
| Finding | Said by | My check | Result |
|---|---|---|---|
| Weekly NIFTY options are recorded only by Kite; Dhan and Upstox record only the 2026-11-23 monthly | A | true in files 003/004 | ACCEPTED. NEEDS YOUR DECISION |
| i5 and i7 strike windows shifted by one strike | A | true (Dhan 22550-23750 vs 22600-23800) | ACCEPTED, minor |
| Both boxes record the SAME 200-depth contract, not split | A, B | true | ACCEPTED. NEEDS YOUR DECISION |
| Dhan: 4 of 5 sockets used, depth sockets full at 50 of 50 | A, B | true in the event lines | ACCEPTED: no new Dhan socket until the cap rules are known |
| i7 Fyers TBT wrote nothing on 29-10, 30-10, 02-11 | B | true (folder listing) | ACCEPTED. Cause UNKNOWN. To investigate |
| Container Up with dead socket: i7 Dhan closed 13:58, never reopened | B | true in the events list | ACCEPTED. Freshness watchdog built |
| Snapshots stopped on i7 for Dhan and Kite at 13:55-13:56 | B | true in the ledger | ACCEPTED. To investigate |
| Kite i7 count (148) not like-for-like with i5 (160) | A | true: i7 was sampled from the last 400,000 ticks | ACCEPTED. To re-measure |
| Upstox "Plus = 5 connections" is contested | C | forum posts only, no vendor page | ACCEPTED as UNVERIFIED |
| "None found" claims are absence, not proof | C | right | ACCEPTED: relabel |
| Vendor limits not verified | C | the vendor sites are blocked here | NOT DONE. Needs the four hosts allowed |
Where I disagree with the agents: nowhere on substance. Their weakness is the one in section 1.

## 4. WHAT I CHANGED WITHOUT ASKING YOU (so you see it)
- `config/recoverability.json`: added `upstox_live`, `live_feed`, `feed_frames`, `upstox_20` so the real recorder file names are classed non-recoverable. 25 tests pass.
- `dp_watchdog.py` on both boxes: starts any stopped recorder; restarts a RUNNING recorder only if its own status file is stale or its frame counter stays flat for 7 minutes during the session; at most 2 restarts an hour; every action logged. 23 tests pass. Not yet proven in a live session.
- Both are small, reversible (backup files `.bak_021126*` on the boxes), and pushed to git.

## 5. WHAT ONLY YOU CAN DECIDE (my recommendation first)
1. Add the nearest weekly to Dhan depth and Upstox feed? **Yes**, inside the connection limits.
2. Split the Dhan 200-depth (i5 on the future, i7 on the nearest weekly ATM)? **Yes.**
3. Allow the four vendor documentation hosts in the session network settings so an agent can verify every limit against the vendor's own text? **Yes.**
4. Treat the AI agents as a first check only and keep your outside AIs as the second? **Yes.**

## 6. WHERE EACH THING IS
- Full list with quotes: docs/framework/LIVE_ONLY_PER_BROKER_021126.md
- The data-need list: docs/framework/RETAILER_DATA_FINAL_V3_021126.md
- Audit packages sent: docs/audit/package_out/ (live_only_021126_IST, final_list_v3_021126_IST, paths_021126_IST)
- This scoreboard: docs/framework/AUDIT_SCOREBOARD_021126.md
