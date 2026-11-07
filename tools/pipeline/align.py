import re, json, difflib, sys
import numpy as np
from num2words import num2words
lines=[l.strip() for l in open('script.txt') if l.strip()]
def norm(s):
    s=s.replace("’","'")
    s=re.sub(r'(\d[\d,]*)', lambda m: ' '+num2words(int(m.group(1).replace(',','')))+' ', s)
    s=s.lower().replace('-',' ')
    s=re.sub(r"[^a-z' ]"," ",s)
    return s.split()
lw=[norm(l) for l in lines]
sw=[]; sidx=[]
for i,ws in enumerate(lw):
    for w in ws: sw.append(w); sidx.append(i)
hyp=json.load(open('hyp.json'))
hw=[re.sub(r'\(\d+\)$','',h[0]) for h in hyp]
sm=difflib.SequenceMatcher(None, sw, hw, autojunk=False)
match={}
for a,b,n in sm.get_matching_blocks():
    for k in range(n): match[a+k]=b+k
dur=float(sys.argv[1])
starts=[None]*len(lines)
for i in range(len(sw)):
    if i in match and starts[sidx[i]] is None:
        starts[sidx[i]]=hyp[match[i]][1]
known=[(i,s) for i,s in enumerate(starts) if s is not None]
cum=np.cumsum([0]+[len(w) for w in lw])
for i,s in enumerate(starts):
    if s is None:
        prev=[k for k in known if k[0]<i]; nxt=[k for k in known if k[0]>i]
        if prev and nxt:
            (pi,pt),(ni,nt)=prev[-1],nxt[0]
            starts[i]=pt+(nt-pt)*(cum[i]-cum[pi])/(cum[ni]-cum[pi])
        elif prev: starts[i]=prev[-1][1]+(cum[i]-cum[prev[-1][0]])*0.4
        else: starts[i]=0.0
for i in range(1,len(starts)):
    if starts[i]<=starts[i-1]+0.3: starts[i]=starts[i-1]+0.3
sil=[tuple(map(float,l.split())) for l in open('silences.txt')]
snapped=0
for i,s in enumerate(starts):
    if i==0: continue
    cands=[e for (a,e) in sil if -0.6<=(s-e)<=0.2]
    if cands:
        e=min(cands,key=lambda e:abs(s-e))
        if e>starts[i-1]+0.3: starts[i]=e; snapped+=1
print('anchored',len(known),'/',len(lines),' snapped',snapped)
caps=[]
for i,l in enumerate(lines):
    st=round(starts[i],3); en=round(starts[i+1],3) if i+1<len(lines) else round(dur,3)
    caps.append({"i":i,"start":st,"end":en,"text":l})
json.dump(caps, open('captions.json','w'), indent=1)
for c in caps[:12]+caps[44:50]+caps[-6:]: print(c['i'],c['start'],c['end'],c['text'][:55])
