import re,base64,gzip,json,sys
p=sys.argv[1]; s=open(p).read()
m=re.search(r'(<script id="regdata" type="application/octet-stream">)(.*?)(</script>)',s,re.S)
d=json.loads(gzip.decompress(base64.b64decode(m.group(2).strip())))
d.update(json.load(open('/home/claude/kb/kb.json')))
b64=base64.b64encode(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),9)).decode()
s=s[:m.start(2)]+b64+s[m.end(2):]
open(p,'w').write(s); print('regdata',len(b64), list(d.keys()))
