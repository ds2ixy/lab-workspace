import json,re,glob,os
toc=json.loads(re.search(r'\[\{"lv":\d.*?\}\]',open('/home/claude/lab-workspace/history30/index.html').read()).group(0))
toc=[(int(t['l']),t['t'],t['lv']) for t in toc]
def where(L):
    big=sec=''
    for l,t,lv in toc:
        if l>L: break
        if lv==0: big=t; sec=''
        elif lv==1: sec=t
        elif lv==2: pass
    return big, sec
def sub(L):
    s=''
    for l,t,lv in toc:
        if l>L: break
        if lv>=2: s=t
        elif lv<=1: s=''
    return s
out=[]
for f in sorted(glob.glob('/tmp/ocr/txt/*.txt')):
    L=int(os.path.basename(f)[:3]); t=open(f).read()
    t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t).strip()
    t=re.sub(r'^\s*\d{1,3}\s*한국전문대학교육\s*30년사\s*$','',t,flags=re.M)
    if len(t)<60: continue
    big,sec=where(L)
    out.append(['30년사 · '+(sec or big), sub(L), L, t])
kb=json.load(open('/home/claude/kb/kb.json')); kb['history30']=out
json.dump(kb,open('/home/claude/kb/kb.json','w'),ensure_ascii=False)
print(len(out), sum(len(x[3]) for x in out))
