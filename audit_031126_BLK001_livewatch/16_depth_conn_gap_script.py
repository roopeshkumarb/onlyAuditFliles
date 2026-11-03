import sqlite3,sys,time
box=sys.argv[1]
c=sqlite3.connect("file:/volume1/docker/datapullers/depth/%s/depth_20261103.db?mode=ro"%box,uri=True,timeout=10)
t0=time.mktime(time.strptime("2026-11-03 09:15","%Y-%m-%d %H:%M"))
for conn in ("d20","d200"):
    prev=None;g=[]
    for (t,) in c.execute("select recv_ts from frames where conn=? and recv_ts>=? order by recv_ts",(conn,t0)):
        if prev and t-prev>60: g.append((time.strftime("%H:%M:%S",time.localtime(prev)),time.strftime("%H:%M:%S",time.localtime(t)),int(t-prev)))
        prev=t
    print(conn,"gaps>60s:",g)
