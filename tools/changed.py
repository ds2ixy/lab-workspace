#!/usr/bin/env python3
"""사용: python3 -I tools/changed.py <이전 index.html> <새 index.html>
기준일(snapshot)만 다르면 'SAME', 실제 내용이 바뀌었으면 'CHANGED' 출력."""
import re,sys,json,gzip,base64
def norm(p):
    s=open(p).read()
    st=json.loads(re.search(r'<script id="state" type="application/json">(.*?)</script>',s,re.S).group(1)); st.pop('snapshot',None); st.pop('savedAt',None)
    lh=re.search(r'<script id="lunchhtml" type="application/octet-stream">([A-Za-z0-9+/=]*)</script>',s)
    lh=gzip.decompress(base64.b64decode(lh.group(1))).decode() if lh else ''
    rest=re.sub(r'<script id="(state|lunchhtml)"[^>]*>.*?</script>','',s,flags=re.S)
    return json.dumps(st,sort_keys=True,ensure_ascii=False),lh,rest
print('SAME' if norm(sys.argv[1])==norm(sys.argv[2]) else 'CHANGED')
