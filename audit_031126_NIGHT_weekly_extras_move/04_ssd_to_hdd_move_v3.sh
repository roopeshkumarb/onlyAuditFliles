#!/bin/sh
# ssd_to_hdd_move.sh - move INACTIVE big files from the SSD share to the HDD RAID volume, with proof. Kumar 03-11-2026.
# Rules (his standing rules): copy -> sha256 of source and copy -> atomic rename on the HDD volume -> only then remove the source.
# Never touches a file modified in the last MIN_AGE_H hours (an active DB), never a file under 100 MB, never overwrites.
# Leaves <name>.MOVED_TO_HDD (dest + sha256) where the file was, and appends every move to MANIFEST (sha256, bytes, src, dest, time).
#   usage: ssd_to_hdd_move.sh [--dry-run]     env: SRC=/volume2/datapullers  DST=/volume1/docker/datapullers_ssd_overflow  MIN_AGE_H=168
SRC=${SRC:-/volume2/datapullers}; DST=${DST:-/volume1/docker/datapullers_ssd_overflow}; MIN_AGE_H=${MIN_AGE_H:-168}; MIN_BYTES=${MIN_BYTES:-104857600}
MAN=$DST/MANIFEST.tsv; LOG=$DST/move.log; DRY=0; [ "$1" = "--dry-run" ] && DRY=1
# v3 (03-11-2026, after Fable audit C1-C4): COPY-ONLY unless ALLOW_REMOVE=1; the HDD volume must really be mounted; one run at a time; -shm too.
case "$DST" in /volume1/*) mountpoint -q /volume1 2>/dev/null || grep -q " /volume1 " /proc/mounts || { echo "REFUSE: /volume1 is not mounted"; exit 1; } ;; esac
mkdir -p "$DST" || exit 1
LOCK=$DST/.move.lock; mkdir "$LOCK" 2>/dev/null || { echo "REFUSE: another run holds $LOCK (rm -r it only if no run is active)"; exit 1; }
trap 'rmdir "$LOCK" 2>/dev/null' EXIT INT TERM
ALLOW_REMOVE=${ALLOW_REMOVE:-0}
log(){ echo "$(date '+%d-%m-%Y %H:%M:%S') $*" | tee -a "$LOG"; }
now=$(date +%s); moved=0; failed=0
find "$SRC" -xdev -type f -size +${MIN_BYTES}c ! -name '*.part' ! -name '*.MOVED_TO_HDD' 2>/dev/null | sort | while read -r f; do
  m=$(stat -c %Y "$f"); s=$(stat -c %s "$f"); age=$(( (now - m) / 3600 ))
  [ "$age" -lt "$MIN_AGE_H" ] && { log "SKIP active/recent (age ${age} h < $MIN_AGE_H): $f"; continue; }
  # v2 (03-11-2026 after the dhan/fyers incident): NEVER move a file that a symlink points at (*_current.db, *_raw_current.db are
  # epoch pointers read by containers that cannot follow a link into another volume), nor one with a live -wal/-shm sidecar, nor from a directory we cannot write.
  base=$(basename "$f"); dir=$(dirname "$f")
  if find "$SRC" -xdev -type l -lname "*$base" 2>/dev/null | grep -q .; then log "SKIP referenced by a symlink (epoch pointer): $f"; continue; fi
  if [ -e "$f-shm" ] && [ "$ALLOW_REMOVE" = 1 ]; then log "SKIP has a -shm sidecar (open or recently open SQLite): $f"; continue; fi
  if [ -s "$f-wal" ]; then log "SKIP has a non-empty -wal (possible unflushed data): $f"; continue; fi
  if [ ! -w "$dir" ]; then log "SKIP directory not writable by $(id -un): $dir"; continue; fi
  rel=${f#$SRC/}; dest="$DST/$rel"; [ -e "$dest" ] && { log "SKIP dest exists: $dest"; continue; }
  free=$(df -B1 "$DST" | tail -1 | awk '{print $4}'); case "$free" in ''|*[!0-9]*) log "STOP cannot read free space of $DST"; break;; esac; [ "$free" -lt $(( s * 2 + 10737418240 )) ] && { log "STOP not enough free space on HDD for $f"; break; }
  [ "$DRY" = 1 ] && { log "DRYRUN would move ${s} bytes: $f -> $dest"; continue; }
  mkdir -p "$(dirname "$dest")"
  log "COPY $f ($((s/1048576)) MB)"
  if ! nice cp -p "$f" "$dest.part"; then log "FAIL copy $f"; rm -f "$dest.part"; continue; fi
  sync
  a=$(nice sha256sum "$f" | cut -d' ' -f1); b=$(nice sha256sum "$dest.part" | cut -d' ' -f1)
  m2=$(stat -c %Y "$f")
  if [ "$a" != "$b" ] || [ "$m2" != "$m" ]; then log "FAIL verify (hash or source changed) $f src=$a copy=$b"; rm -f "$dest.part"; continue; fi
  mv "$dest.part" "$dest" || { log "FAIL rename $dest"; continue; }
  if [ "$ALLOW_REMOVE" != 1 ]; then log "COPIED-ONLY (ALLOW_REMOVE!=1, source left in place; verified copy at $dest sha256=$a)"; continue; fi
  if rm -f "$f" && [ ! -e "$f" ]; then
    printf 'moved to HDD %s\nsha256 %s\nbytes %s\nmoved %s\n' "$dest" "$a" "$s" "$(date '+%d-%m-%Y %H:%M:%S')" > "$f.MOVED_TO_HDD"
    printf '%s\t%s\t%s\t%s\t%s\n' "$a" "$s" "$f" "$dest" "$(date '+%d-%m-%Y %H:%M:%S')" >> "$MAN"
    log "MOVED $f -> $dest sha256=$a"
  else
    log "COPIED-NOT-MOVED (source could not be removed; it is still in place; extra verified copy at $dest sha256=$a)"
  fi
done
log "done"
