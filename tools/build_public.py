#!/usr/bin/env python3
"""hver-workspace 공개용 빌드.
사용: python3 -I tools/build_public.py <내부용 index.html> <중식비 현황 index.html> <repo 경로>
- 중식비 현황 원본 HTML을 내부용 HTML에 동기화(lunchhtml, lunchdata)하고 <repo>/internal-synced.html 로 저장(내부용 재게시용, git에 올리지 말 것: .gitignore)
- 내부용 state를 걸러 공개용 index.html, kcce/lab-workspace-public.html 생성
"""
import json,re,sys,gzip,base64,os,datetime
INT,BOARD,REPO=sys.argv[1],sys.argv[2],sys.argv[3]
src=open(INT).read(); b=open(BOARD).read()
# --- lunch sync ---
b64=base64.b64encode(gzip.compress(b.encode(),9,mtime=0)).decode()
tag='<script id="lunchhtml" type="application/octet-stream">'
assert tag in src
src=re.sub(re.escape(tag)+r'[A-Za-z0-9+/=]*</script>',lambda x:tag+b64+'</script>',src,count=1)
st=re.search(r'<script type="application/json" id="state">(.*?)</script>',b,re.S).group(1).strip(); json.loads(st)
src=re.sub(r'(<script id="lunchdata" type="application/json">)(.*?)(</script>)',lambda x:x.group(1)+st+x.group(3),src,count=1,flags=re.S)
open(os.path.join(REPO,'internal-synced.html'),'w').write(src)
live=json.loads(re.search(r'<script id="state" type="application/json">(.*?)</script>',src,re.S).group(1))
TODAY=datetime.datetime.utcnow()+datetime.timedelta(hours=9)
def setstate(s,st):
    m=re.search(r'(<script id="state" type="application/json">)(.*?)(</script>)',s,re.S)
    return s[:m.start(2)]+json.dumps(st,ensure_ascii=False).replace('<','\\u003c')+s[m.end(2):]
pub=json.loads(json.dumps(live))
for p in pub['projects']:
    p['memo']=''; p['owner']=''
    p['links']=[l for l in p['links'] if l['note'] not in ('내부','관리자 전용')]
    for l in p['links']:
        if l['note'] in ('공개','공유'): l['note']=''
    p['logs']=[l for l in p['logs'] if l['type']!='메모']
    for l in p['logs']:
        l['text']=l['text'].replace('내부용·공개용 수치 일치 확인','대시보드 수치 검증').replace(' 내부용·공개용','').replace('현황·장부','현황')
P={p['id']:p for p in pub['projects']}
P['finance']['desc']='고등교육 재정지원 현황을 사업·기관별로 분석하는 대시보드'
RN={'내부용·공개용 수치 일치 확인':'대시보드 수치 검증','이번 달 장부 입력 마감':'이번 달 중식비 입력 마감'}
for p in pub['projects']:
    for t in p['tasks']: t['text']=RN.get(t['text'],t['text'])
    for l in p['logs']:
        for a,b in RN.items(): l['text']=l['text'].replace(a,b)
P['lunchboard']['desc']='구성원 중식비 현황 공유 (장부는 관리자만 입력할 수 있어요)'
pub['snapshot']=TODAY.strftime('%Y-%m-%d')
s=setstate(src,pub)
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b)
rep('<title>연구소 작업공간</title>','<title>hver-workspace</title>')
rep('<div class="t">연구소 작업공간</div>','<div class="t">Workspace Page</div>')
rep('function changed(){','function changed(){ render(); return;')
rep('function loadLocal(){','function loadLocal(){ return;')
rep("(function connect(){","(function connect(){ return;")
rep("'<div class=\"sideinfo\">'+saveHTML()+'<div style=\"margin-top:4px\">'+(state.savedAt?\"최근 수정 \"+esc(state.savedAt.slice(0,10)):\"\")+'</div></div>","'<div class=\"sideinfo\"><div class=\"save ok\"><i></i>공개용 · 읽기 전용</div><div style=\"margin-top:4px\">기준일 '+esc(state.snapshot||\"\")+'</div></div>")
rep("개 작업의 진행 상황과 최근 기록</div>","개 작업의 진행 상황과 최근 기록 · 기준일 '+esc(state.snapshot||\"\")+'</div>")
rep("""    '<div class="field"><label>상태</label><select data-f="status">'+Object.keys(STATUS).map(function(s){return '<option'+(s===p.status?' selected':'')+'>'+s+'</option>';}).join("")+'</select></div>'+
    '<div class="field"><label>마감일 '+(p.due?'<span class="num">· '+dday(p.due)+'</span>':'')+'</label><input type="date" data-f="due" value="'+esc(p.due)+'"></div>'+
    '<div class="field"><label>담당</label><input data-f="owner" value="'+esc(p.owner)+'" placeholder="담당자"></div>'+""",
"""    '<div class="field"><label>상태</label><div style="height:34px;display:flex;align-items:center">'+badge(p.status)+'</div></div>'+
    '<div class="field"><label>마감일</label><div class="num" style="height:34px;display:flex;align-items:center">'+(p.due?esc(p.due)+' · '+dday(p.due):'—')+'</div></div>'+
    '<div class="field"><label>최근 기록</label><div class="num" style="height:34px;display:flex;align-items:center">'+(lastLog(p)?esc(lastLog(p).date):'—')+'</div></div>'+""")
rep('<input type="checkbox" data-act="toggle" data-id="\'+t.id+\'"\'+(t.done?" checked":"")+\'>','<input type="checkbox" disabled\'+(t.done?" checked":"")+\'>')
rep('<button class="btn ghost sm" data-act="delTask" data-id="\'+t.id+\'" title="삭제">✕</button>','')
rep('<button class="btn ghost sm" data-act="delLog" data-id="\'+l.id+\'" title="삭제">✕</button>','')
rep('<button class="btn ghost sm" data-act="delLink" data-i="\'+i+\'" title="삭제">✕</button>','')
rep("할 일을 추가하면 진행률이 자동 계산됩니다","등록된 할 일이 없습니다")
rep("""tasks += '</ul><form class="addrow" data-form="task"><input name="t" placeholder="할 일 추가" autocomplete="off"><button class="btn">추가</button></form></div>';""","""tasks += '</ul></div>';""")
rep("""<h3>진행·결과 기록</h3><form class="addrow" data-form="log" style="margin:0 0 8px"><select name="ty">'+Object.keys(LOGTYPE).map(function(k){return '<option>'+k+'</option>';}).join("")+'</select><input name="t" placeholder="무엇이 진행됐나요?" autocomplete="off"><input name="d" type="date" value="'+today()+'" style="flex:none;width:140px"><button class="btn">기록</button></form><ul class="logs">""","""<h3>진행·결과 기록</h3><ul class="logs">""")
rep("""links += '</ul><form class="addrow" data-form="link"><input name="l" placeholder="이름" style="flex:.8"><input name="u" placeholder="https://…" style="flex:1.2"><button class="btn">추가</button></form></div>';""","""links += '</ul></div>';""")
rep("""'</div><div class="stack">'+links+memo+'</div></div>';""","""'</div><div class="stack">'+links+'</div></div>';""")
rep("(p.owner?'<span>담당 '+esc(p.owner)+'</span>':'')","''")
s=s.replace(' (공개용)','')
d='한국고등직업교육연구소(KCCE HVER)의 통계·출판·연구소 작업 진행 현황과 학사편람·규정 질의응답을 한눈에 보는 공개 페이지'
import base64; fav=base64.b64encode(open(os.path.join(REPO,'favicon-32x32.png'),'rb').read()).decode()
u='https://lab-workspace-public.pages.dev/'; img=u+'img/og/og-main.jpg'
meta=f'''<title>hver-workspace</title>
<meta name="description" content="{d}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="hver Workspace · 한국고등직업교육연구소">
<meta property="og:title" content="hver-workspace | Workspace Page">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{u}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="hver-workspace | Workspace Page">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{img}">
<link rel="icon" type="image/png" sizes="32x32" href="data:image/png;base64,{fav}">
<link rel="apple-touch-icon" href="{u}apple-touch-icon.png">'''
a='if(p.id==="lunchboard") h += lunchFrameHTML();'
assert s.count(a)==1
s=s.replace(a,'if(p.id==="lunchboard") return h + lunchFrameHTML();',1)
s=s.replace('<title>hver-workspace</title>',meta,1)
open(os.path.join(REPO,'index.html'),'w').write(s)
open(os.path.join(REPO,'kcce/lab-workspace-public.html'),'w').write(s.replace('<head>\n','<head>\n<base href="/">\n',1))
print('pub built', 'margin:0 auto' in s)
