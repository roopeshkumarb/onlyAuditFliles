> UPDATE 04-11-2026 00:00 IST: the i7 NOW HAS A DIRECT CLOUDFLARE ROUTE: hostname sshi7 (tested, see 34_direct_cf_routes_tested.txt). The statements below that the i7 has no direct route describe the OLD hostname sshj1800, which still returns Bad Gateway. Open: which connector serves sshi7 and whether it survives the i5 tunnel being down (UNKNOWN); the Pi restarted at ~18:50 IST (cause UNKNOWN).

# ACCESS ROUTES: reach every box with no single point of failure (prepared 03-11-2026 ~13:55 IST; owner leaves for offshore on 05-11)
Hostnames are shown as aliases only (i5-cf, j1800-cf, pi-cf, sshpi-cf). No tokens or keys are in this file.

## 1. MEASURED today (not assumed)
| Route | Result 03-11 ~13:40 | Evidence |
|---|---|---|
| Cloudflare SSH to i5 (`i5-cf`) | WORKS | `box_reach.sh i5` -> `ROUTE: i5-cf`, host i5-4590-dsm72 |
| Cloudflare SSH to Pi (`pi-cf`) | WORKS | host a0d7b954-ssh, up 2 d 22 h |
| Cloudflare SSH to i7 (`j1800-cf`) | **FAILS: Bad Gateway** | every attempt today (also earlier in the session) |
| Cloudflare SSH to Pi, 2nd name (`sshpi-cf`) | **FAILS: Bad Gateway** | same |
| LAN hop i5 -> i7 and i7 -> i5 | WORKS | both directions tested |
| LAN hop Pi -> i5 and Pi -> i7 (user roopeshkumarb) | WORKS | tested |
| LAN hop i5 -> Pi and i7 -> Pi (user root) | WORKS | tested |
| Direct from the cloud sandbox to a LAN address (192.168.2.x) | impossible | timed out |
CORRECTED 03-11 21:50 (Fable review): the third i5 route in 11_box_reach.sh (i5-cf>i7>i5) starts with i5-cf, the very route that would have failed, so it is not independent. INDEPENDENT routes today: i5 has 2 (own tunnel; via Pi), i7 has 2 (via i5 tunnel; via Pi tunnel; neither is the i7's own), Pi has 1. (First version of this line said i5 has 3 routes.) So today: i5 has 2 independent routes (own tunnel, via Pi); i7 has 2 (via i5, via Pi) and **no direct Cloudflare route**; the Pi has 1 (`pi-cf`). Every route to the i7 passes through a box other than the i7 itself. If the i5 tunnel and the Pi tunnel both drop, the i7 is unreachable from offshore.
Facts about the connector: the i5 runs cloudflared as a DSM package (process started 12:45, i.e. it came back by itself after the reboot); it uses a remotely-managed tunnel token, so the hostname -> service mapping lives in the Cloudflare dashboard, which this session cannot read. The i7 has no cloudflared package or container (`/var/packages` shows only CloudSync; its `docker ps` has no cloudflared). Which connector serves `pi-cf`: UNKNOWN. Why `j1800-cf` and `sshpi-cf` return Bad Gateway: UNKNOWN (needs the dashboard).

## 2. WHICH DIRECTION WE ARE GOING (recommendation)
1. **Primary: Cloudflare Tunnel with THREE connectors** (i5 existing, i7 new, Pi new), all running the same tunnel, each hostname routed to its box's LAN address. Any one connector alive serves every hostname.
2. **Secondary: LAN hop** through any live box (already works; `tools/box_reach.sh` tries every route in order and prints which answered).
3. **Third, independent of Cloudflare: a second overlay (Tailscale) on the Pi only** (optional, needs the owner's account). Protects against a Cloudflare outage or an Access-policy mistake.
4. **Power, the real single point of failure:** both NAS boxes lost power together twice today; a UPS (NAS x2 + router + modem) and the DSM boot-up task are the first fixes. The boxes DID power back on by themselves (evidence: two unattended reboots), so "restart after power failure" is already effective. The router/modem on the same circuit is not yet verified.
Do not touch the existing cloudflared on the i5 or portainer: it is the owner's only way in.

## 3. SEQUENCE (do in this order; each step has a test)
| # | Step | Who | Test (pass = ...) |
|---|---|---|---|
| 1 | Verify LAN mesh in all 6 directions | Claude | DONE 03-11: 6/6 |
| 2 | `box_reach.sh` tries every route; keep ~/.ssh/config aliases in the repo template | Claude | DONE: i5, pi answer direct; i7 answers via `i5-cf>i7` |
| 3 | Show what `sshj1800` and `sshpi` point at in Zero Trust > Networks > Tunnels > (the tunnel of `sshi5`) > Public hostnames. Fix: `sshj1800` -> `ssh://192.168.2.100:22`, `sshpi` -> `ssh://192.168.2.130:22` | Owner in the dashboard (~5 min), OR owner authorises the Cloudflare connector in claude.ai settings and Claude does it | `box_reach.sh i7` prints `ROUTE: j1800-cf` |
| 4 | Add replica connectors: cloudflared on the i7 (Docker container, `restart: unless-stopped`) and on the Pi, using the same tunnel token. Claude reads the token on the box and never prints it | Claude, after step 3 and the owner's OK | dashboard shows 3 connectors healthy; `box_reach.sh i7` still passes |
| 5 | Put `boot_start_containers.sh` in DSM Task Scheduler (Triggered Task, Boot-up, root) on both boxes; add the cloudflared replica container to its start list | Owner (DSM admin login) | pull the box's network or reboot at a quiet time; recorders return without a human |
| 6 | Offshore rehearsal from a phone hotspot (NOT the home LAN) on the owner's laptop: install the cloudflared client, log in through Access, `ssh` to each alias | Owner, with Claude watching `box_reach.sh` | all three aliases answer from outside the LAN |
| 7 | Failure drill: stop the replica on ONE box (never the i5 package) and confirm the others still serve | Claude, at a quiet time | hostname still answers |
| 8 | UPS for NAS x2 + router + modem; second internet (4G failover) for the router | Owner | box rides through a 5-minute mains cut |
Target date: steps 3-6 before 05-11.

## 4. What this does NOT protect against
Total site power or internet loss with no UPS/4G; loss of the owner's Cloudflare account; an Access-policy change that locks everyone out. NOT TESTED: any offshore login from outside the LAN.
