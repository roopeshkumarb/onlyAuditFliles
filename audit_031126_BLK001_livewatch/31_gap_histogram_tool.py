#!/usr/bin/env python3
"""gap_histogram.py - READ-ONLY. For every day file of the four live recorders on THIS box, count the silent gaps inside the
session window (default 09:15-15:30 IST) above 60/90/120/180 s and print the longest gap. Evidence for the livewatch threshold.
  python3 gap_histogram.py <datapullers root> <box>     ticks = NIFTY 50 token 256265 only; depth split by conn (d20 / d200)
Opens each file with mode=ro and walks the recv_ts index in order; no writes. Gaps that span the window edge are ignored."""
import glob, os, sqlite3, sys, time
LIMITS = (60, 90, 120, 180)
SPECS = (("ticks", "ticks_", "select recv_ts from ticks where token=256265 and recv_ts>=? and recv_ts<=? order by recv_ts", ("NIFTY",)),
         ("depth", "depth_", "select recv_ts from frames where conn=? and recv_ts>=? and recv_ts<=? order by recv_ts", ("d20", "d200")),
         ("upstox_live", "upstox_", "select recv_ts from frames where recv_ts>=? and recv_ts<=? order by recv_ts", ("frames",)),
         ("fyers_tbt", "tbt_", "select recv_ts from frames where recv_ts>=? and recv_ts<=? order by recv_ts", ("frames",)))
def window(day, a="09:15", b="15:30"):
    t = lambda hm: time.mktime(time.strptime(day + " " + hm, "%Y%m%d %H:%M"))      # box TZ is IST (verified /etc/TZ)
    return t(a), t(b)
def main():
    root, box = sys.argv[1], sys.argv[2]
    print("recorder,conn,day,rows,max_gap_s,>60,>90,>120,>180,first,last")
    for folder, prefix, sql, conns in SPECS:
        for p in sorted(glob.glob(os.path.join(root, folder, box, prefix + "20??????.db"))):
            day = os.path.basename(p)[len(prefix):len(prefix) + 8]; t0, t1 = window(day)
            try:
                con = sqlite3.connect("file:%s?mode=ro" % p, uri=True, timeout=10)
            except Exception as e:
                print("%s,-,%s,ERR %s" % (folder, day, e)); continue
            for c in conns:
                args = (t0, t1) if folder in ("ticks", "upstox_live", "fyers_tbt") else (c, t0, t1)
                n = 0; prev = None; mx = 0.0; cnt = [0] * 4; first = last = None
                try:
                    for (t,) in con.execute(sql, args):
                        n += 1; first = first or t; last = t
                        if prev is not None:
                            g = t - prev; mx = max(mx, g)
                            for i, L in enumerate(LIMITS): cnt[i] += g > L
                        prev = t
                    print("%s,%s,%s,%d,%.0f,%d,%d,%d,%d,%s,%s" % (folder, c, day, n, mx, cnt[0], cnt[1], cnt[2], cnt[3],
                          time.strftime("%H:%M:%S", time.localtime(first)) if first else "", time.strftime("%H:%M:%S", time.localtime(last)) if last else ""))
                except Exception as e:
                    print("%s,%s,%s,ERR %s" % (folder, c, day, e))
            con.close()
main()
