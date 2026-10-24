import plistlib,json
from pathlib import Path
w=plistlib.load(open('original/workflow.bplist','rb'))
s=w['WFWorkflowActions'][4]['WFWorkflowActionParameters']['WFURLActionURL']['Value']['string']
Path('reports/original-bootstrap.js').write_text(s.split('<script>')[1].split('</script>')[0].replace('\ufffc','e30='),encoding='utf8')
print(repr(s[s.index('var m='):s.index('var lang=')]))
