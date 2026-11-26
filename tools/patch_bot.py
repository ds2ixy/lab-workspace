import re,base64,gzip,json,sys
p=sys.argv[1]; s=open(p).read()
# 1) merge KB into REG pack
m=re.search(r'(<script id="regdata" type="application/octet-stream">)(.*?)(</script>)',s,re.S)
d=json.loads(gzip.decompress(base64.b64decode(m.group(2).strip())))
kb=json.load(open('/home/claude/kb/kb.json'))
d.update(kb)
b64=base64.b64encode(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),9)).decode()
s=s[:m.start(2)]+b64+s[m.end(2):]
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
# 2) chunk mapping keeps extra field (article id)
rep('return { doc: k, i: i, title: c[0], head: c[1], page: c[2], text: c[3], imgs: c[4] || [] };',
    'return { doc: k, i: i, title: c[0], head: c[1], page: c[2], text: c[3], imgs: c[4] || [], aid: c[5] || "" };')
# 3) label
rep('function regLabel(c) {\n','function regLabel(c) {\n  if (c.doc === "whitepaper" || c.doc === "issue" || c.doc === "history30") return c.title + (c.head ? " · " + c.head : "");\n')
# 4) KB helpers before botAsk
rep('async function botAsk(q){',
'''var KB_DOCS = {handbook:"학사편람", rules:"협의회 규정집", whitepaper:"정책건의 백서", issue:"THE ISSUE", history30:"30년사"};
var KB_PUB = "https://lab-workspace-public.pages.dev/";
function kbUrl(c){
  if(c.doc==="whitepaper") return KB_PUB+"report-ebook/#whitepaper/"+c.page;
  if(c.doc==="issue") return KB_PUB+"the-issue/pdf/"+c.aid+".pdf#page="+c.page;
  if(c.doc==="history30") return KB_PUB+"history30/#p"+c.page;
  return "";
}
function kbHits(q){
  var keys=Object.keys(KB_DOCS).filter(function(k){ return REG && REG[k]; });
  var r=regSearch(keys, q), per={}, out=[];
  r.hits.forEach(function(h){ var k=h.c.doc; per[k]=(per[k]||0)+1; if(per[k]<=2 && out.length<6) out.push(h); });
  return out;
}
async function botAsk(q){''')
rep('if(wantReg){ try{ await regLoad(); var r=regSearch(["handbook","rules"], q); regHits=r.hits.slice(0,3); }catch(e){} }',
    'try{ await regLoad(); regHits=kbHits(q); }catch(e){}')
rep('var wantReg = !pm.length || pm[0].sc<3 || /','var wantReg = true || /')
rep('regHits.forEach(function(x,i){ ctx.push("[규정"+(i+1)+"] "+regLabel(x.c)+" (p."+x.c.page+")\\n"+x.c.text.slice(0,1100)); });',
    'regHits.slice(0,4).forEach(function(x,i){ ctx.push("[규정"+(i+1)+"] "+KB_DOCS[x.c.doc]+" · "+regLabel(x.c)+" (p."+x.c.page+")\\n"+x.c.text.slice(0,1100)); });')
rep("srcLine='<p class=\"bSrc\">출처 · '+esc(regLabel(c0))+' (p.'+c0.page+')</p>';",
    "srcLine='<p class=\"bSrc\">출처 · '+esc(KB_DOCS[c0.doc]||'')+' · '+esc(regLabel(c0))+' (p.'+c0.page+')</p>';")
rep("""if(regHits.length) more+='<div class="bReg"><p class="bRegH">관련 조항 '+regHits.length+'건</p>'+regHits.map(function(x){ return '<div class="bRegI"><b>'+esc(regLabel(x.c))+'</b> <small>p.'+x.c.page+'</small><span>'+esc(botSnip(x.c,q))+'</span></div>'; }).join("")+'</div>';""",
"""if(regHits.length) more+='<div class="bReg"><p class="bRegH">관련 자료 '+regHits.length+'건</p>'+regHits.map(function(x){ var u=kbUrl(x.c); var lab='<em class="bDoc">'+esc(KB_DOCS[x.c.doc]||'')+'</em> <b>'+esc(regLabel(x.c))+'</b> <small>p.'+x.c.page+'</small>'; return '<div class="bRegI">'+(u?'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+lab+' ↗</a>':'<button class="bRegLink" data-bot="reg" data-v="'+(x.c.doc==="rules"?"reg-rules":"reg-handbook")+'" data-q="'+esc(q)+'">'+lab+'</button>')+'<span>'+esc(botSnip(x.c,q))+'</span></div>'; }).join("")+'</div>';""")
rep("""if(useReg) acts+='<button data-bot="reg" data-v="'+(regHits[0].c.doc==="rules"?"reg-rules":"reg-handbook")+'" data-q="'+esc(q)+'">원문에서 보기</button>';""",
"""if(useReg){ var h0=regHits[0].c, u0=kbUrl(h0); acts+= u0 ? '<a href="'+esc(u0)+'" target="_blank" rel="noopener">원문에서 보기 ↗</a>' : '<button data-bot="reg" data-v="'+(h0.doc==="rules"?"reg-rules":"reg-handbook")+'" data-q="'+esc(q)+'">원문에서 보기</button>'; }""")
# 5) prompt wording: 규정 -> 자료
s=s.replace('규정을 근거로 하면 문장 끝에 [규정1]처럼 표기','자료를 근거로 하면 문장 끝에 [규정1]처럼 번호로 표기하고, 여러 자료(편람·규정집·백서·THE ISSUE·30년사)에 걸쳐 있으면 함께 정리')
# css
rep('</style>','.bDoc{font-style:normal;font-size:11px;font-weight:700;color:#fff;background:#3b6fb6;border-radius:6px;padding:1px 6px;margin-right:2px}\n.bRegI a,.bRegLink{color:inherit;text-decoration:none;background:none;border:0;padding:0;font:inherit;text-align:left;cursor:pointer;display:block}\n.bRegI a:hover b,.bRegLink:hover b{text-decoration:underline}\n</style>') if s.count('</style>')==1 else None
open(p,'w').write(s)
print('ok', len(b64))
