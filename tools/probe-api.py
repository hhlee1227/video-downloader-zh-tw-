import plistlib,urllib.request,json
from pathlib import Path
w=plistlib.load(open('original/workflow.bplist','rb'))
s=w['WFWorkflowActions'][7]['WFWorkflowActionParameters']['WFURLActionURL']['Value']['string']
s=s.replace('\ufffc','{}').format('zh-TW','true','true','true','')
try:
 r=urllib.request.urlopen(urllib.request.Request(s,headers={'User-Agent':'Mozilla/5.0'}),timeout=20)
 b=r.read(1000000); Path('reports/api-empty-input-response.bin').write_bytes(b)
 print(r.status,r.headers.get('Content-Type'));print(b.decode('utf8')[:14000])
except Exception as e:print(type(e).__name__,str(e))
