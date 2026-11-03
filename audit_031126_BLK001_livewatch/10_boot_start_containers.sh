#!/bin/sh
# boot_start_containers.sh - start the live recorders and the stack after a NAS reboot/power loss.
# WHY: on 03-11-2026 ~12:08 IST a power event took both boxes down; "restart: unless-stopped" did NOT bring
# the containers back, and live-only data was lost until a human started them. No UPS.
# INSTALL (Kumar, DSM admin, once per box): Control Panel > Task Scheduler > Create > Triggered Task >
#   User-defined script > User: root > Event: Boot-up > Task settings > Run command:
#   sh /volume1/docker/datapullers/boot_start_containers.sh >> /volume1/docker/datapullers/_state/boot_start.log 2>&1
# Safe: `docker start` on a running container is a no-op. Never touches cloudflared/portainer.
D=/var/packages/ContainerManager/target/usr/bin/docker
log(){ echo "$(date '+%d-%m-%Y %H:%M:%S') [boot_start] $*"; }
# wait for Docker (up to 10 min)
i=0; until $D info >/dev/null 2>&1; do i=$((i+1)); [ $i -gt 60 ] && { log "docker not ready after 10 min"; exit 1; }; sleep 10; done
sleep 30   # let network/mounts settle
# order matters: logins/lease first, then live-only recorders (non-recoverable), then pullers and helpers
for c in broker_login pull_lease_ctl tickrec depthrec upstoxrec fyerstbt dp_guard fullpuller puller930 dp_voter dbtools; do
  if $D inspect "$c" >/dev/null 2>&1; then
    $D start "$c" >/dev/null 2>&1 && log "started/ok $c" || log "FAILED $c"
  else
    log "absent $c"
  fi
done
