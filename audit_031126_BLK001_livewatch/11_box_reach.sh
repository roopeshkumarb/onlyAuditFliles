#!/bin/bash
# box_reach.sh - run a command on a box, trying EVERY route in order so no single path is a single point of failure.
#   usage: box_reach.sh <i5|i7|pi> '<shell command>'
# Routes (Cloudflare SSH aliases come from ~/.ssh/config; LAN hops use the key already on the hop box):
#   i5: 1 i5-cf (direct)            2 pi-cf -> roopeshkumarb@192.168.2.91   3 i7 route -> i5
#   i7: 1 j1800-cf (direct, needs its own connector - see ACCESS_ROUTES) 2 i5-cf -> i7  3 pi-cf -> i7
#   pi: 1 pi-cf (direct sshha)      2 sshpi-cf (alias)                      3 i5-cf -> pi
# Prints "ROUTE: <name>" on stderr for the route that answered. Exit 99 if all fail. Read the command's own exit code otherwise.
BOX="$1"; CMD="$2"; [ -n "$BOX" ] && [ -n "$CMD" ] || { echo "usage: $0 <i5|i7|pi> '<cmd>'" >&2; exit 2; }
RUN="sh -s"   # the command travels on stdin, so nested hops need no quoting
O="-o BatchMode=yes -o ConnectTimeout=25 -o ServerAliveInterval=10"
LAN="ssh -o BatchMode=yes -o ConnectTimeout=10"
T=${REACH_TIMEOUT:-150}
try(){ name="$1"; shift; out=$(printf '%s\n' "$CMD" | timeout $T "$@" 2>/tmp/reach_err.$$); rc=$?
  if [ $rc -ne 255 ] && [ $rc -ne 124 ] && ! grep -qE "Bad Gateway|bad handshake|Connection closed by UNKNOWN|Permission denied" /tmp/reach_err.$$; then
     echo "ROUTE: $name" >&2; printf '%s\n' "$out"; rm -f /tmp/reach_err.$$; exit $rc; fi
  echo "route $name failed (rc=$rc: $(head -c 100 /tmp/reach_err.$$ | tr '\n' ' '))" >&2; }
case "$BOX" in
 i5) try i5-cf        ssh $O i5-cf "$RUN"
     try "pi-cf>i5"     ssh $O pi-cf "$LAN roopeshkumarb@192.168.2.91 '$RUN'"
     try "i5-cf>i7>i5"  ssh $O i5-cf "$LAN 192.168.2.100 \"$LAN 192.168.2.91 '$RUN'\"" ;;
 i7) try j1800-cf     ssh $O j1800-cf "$RUN"
     try "i5-cf>i7"     ssh $O i5-cf "$LAN 192.168.2.100 '$RUN'"
     try "pi-cf>i7"     ssh $O pi-cf "$LAN roopeshkumarb@192.168.2.100 '$RUN'" ;;
 pi) try pi-cf        ssh $O pi-cf "$RUN"
     try sshpi-cf     ssh $O sshpi-cf "$RUN"
     try "i5-cf>pi"     ssh $O i5-cf "$LAN root@192.168.2.130 '$RUN'" ;;
esac
echo "ALL ROUTES FAILED for $BOX" >&2; exit 99
