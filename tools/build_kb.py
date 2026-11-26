import subprocess,json,re,os
W="/mnt/user-data/uploads/claude data/2026년도 전문대학 정책건의 백서.pdf"
def pages(pdf):
    out=subprocess.run(['pdftotext','-enc','UTF-8',pdf,'-'],capture_output=True,text=True).stdout
    return out.split('\f')
def clean(t):
    t=re.sub(r'\d+\s*╻\s*전문대학 정책건의 백서[^\n]*','',t)
    t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n{2,}','\n',t)
    return t.strip()
parts=[(1,'표지·발간사'),(6,'목차'),(11,'건의 현황'),(16,'1부 재정지원 건의'),(66,'2부 규제개선 발굴 및 관계기관 건의'),(230,'3부 정책 공유(더 이슈)')]
def part(n):
    lab=parts[0][1]
    for a,l in parts:
        if n>=a: lab=l
    return lab
wp=[]
for i,t in enumerate(pages(W),1):
    t=clean(t)
    if len(t)<40: continue
    lines=[x.strip() for x in t.split('\n') if len(x.strip())>=4]
    head=next((x for x in lines if not re.match(r'^[\d\s.,%()~·-]+$',x)),'')[:60]
    wp.append(['정책건의 백서 · '+part(i), head, i, t])
# THE ISSUE
import json as J
node=subprocess.run(['node','-e',"global.window={};require('/home/claude/lab-workspace/the-issue/data/issues.js');console.log(JSON.stringify(window.THE_ISSUE.issues))"],capture_output=True,text=True).stdout
iss=J.loads(node); isu=[]
for v in iss:
    for a in v.get('articles',[]):
        pdf=f"/home/claude/lab-workspace/the-issue/pdf/{a['id']}.pdf"
        if not os.path.exists(pdf): continue
        for k,t in enumerate(pages(pdf),1):
            t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n{2,}','\n',t).strip()
            if len(t)<40: continue
            isu.append([f"THE ISSUE Vol.{v['vol']} ({v['month']}월호) · {a.get('category','')}", a['title'], k, t, [], a['id']])
print(len(wp), sum(len(x[3]) for x in wp), len(isu), sum(len(x[3]) for x in isu))
J.dump({'whitepaper':wp,'issue':isu},open('/home/claude/kb/kb.json','w'),ensure_ascii=False)
