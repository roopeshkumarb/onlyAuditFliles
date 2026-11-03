import sqlite3,sys,time,os
B="/volume1/docker/datapullers"; box=sys.argv[1]
t0=time.mktime(time.strptime("2026-11-03 09:15:00","%Y-%m-%d %H:%M:%S"))
def hm(t): return time.strftime("%H:%M:%S",time.localtime(t))
def gaps(c,sql,args,lim=30):
    prev=None;out=[];n=0
    for (t,) in c.execute(sql,args):
        n+=1
        if prev is not None and t-prev>lim: out.append((prev,t))
        prev=t
    return n,prev,out
for d,x,sql,args in (("ticks","ticks_","select recv_ts from ticks where token=256265 and recv_ts>=? order by recv_ts",(t0,)),
                     ("depth","depth_","select recv_ts from frames where recv_ts>=? order by recv_ts",(t0,)),
                     ("upstox_live","upstox_","select recv_ts from frames where recv_ts>=? order by recv_ts",(t0,)),
                     ("fyers_tbt","tbt_","select recv_ts from frames where recv_ts>=? order by recv_ts",(t0,))):
    p="%s/%s/%s/%s20261103.db"%(B,d,box,x)
    try:
        c=sqlite3.connect("file:%s?mode=ro"%p,uri=True,timeout=10)
        n,last,g=gaps(c,sql,args)
        big=[(a,b) for a,b in g if b-a>60]
        print("%s rows(since 09:15)=%d last=%s gaps>30s=%d  gaps>60s:"%(d,n,hm(last) if last else "-",len(g)))
        for a,b in big[:12]: print("   %s -> %s  (%.0f s)"%(hm(a),hm(b),b-a))
    except Exception as e: print(d,"ERR",e)
