from pathlib import Path
import plistlib,json,re,hashlib,subprocess,sys,platform,shutil
ROOT=Path(__file__).resolve().parents[1]
def walk(x,path='$'):
    yield path,x
    if isinstance(x,dict):
        for k,v in x.items():yield from walk(v,path+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'['+str(i)+']')
def audit(w,name):
    a=w['WFWorkflowActions']; ids={x['WFWorkflowActionParameters'].get('UUID'):i for i,x in enumerate(a)}; ids.pop(None,None)
    variables={x['WFWorkflowActionParameters'].get('WFVariableName') for x in a if x['WFWorkflowActionIdentifier'].endswith(('setvariable','appendvariable'))}
    missing=[];forward=[];refs=[];stack=[];errors=[];strings=[]
    for i,x in enumerate(a):
        p=x['WFWorkflowActionParameters']; ident=x['WFWorkflowActionIdentifier']; mode=p.get('WFControlFlowMode');g=p.get('GroupingIdentifier')
        if mode==0:stack.append((g,ident))
        elif mode in (1,2):
            if not stack or stack[-1]!=(g,ident):errors.append([i,'unbalanced control group',g])
            elif mode==2:stack.pop()
        for path,v in walk(p):
            if isinstance(v,str):strings.append({'action':i,'path':path,'text':v})
            if isinstance(v,dict):
                if 'OutputUUID' in v:
                    target=ids.get(v['OutputUUID']);refs.append([i,target,v['OutputUUID']])
                    if target is None:missing.append([i,path,v['OutputUUID']])
                    elif target>=i:forward.append([i,target,path])
                if v.get('Type')=='Variable' and 'VariableName' in v and v['VariableName'] not in variables|{'Repeat Index','Repeat Item'}:missing.append([i,path,v['VariableName']])
                if 'attachmentsByRange' in v:
                    s=v['string']; raw=s.encode('utf-16-le')
                    for r in v['attachmentsByRange']:
                        start,length=map(int,re.findall(r'\d+',r))
                        if length!=1 or raw[start*2:(start+1)*2]!=b'\xfc\xff':errors.append([i,'invalid UTF16 token range',r])
    if stack:errors.append(['unclosed groups',stack])
    report={'actions':len(a),'missing_references':missing,'forward_references':forward,'control_or_token_errors':errors,'note':'UUID existence and lexical control checks only; branch dominance and iOS action schemas require device verification.'}
    (ROOT/f'reports/{name}-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/f'reports/{name}-strings.json').write_text(json.dumps(strings,ensure_ascii=False,indent=2),encoding='utf8')
    lines=['# '+name+' action inventory','']+[f"{i:03d} | {x['WFWorkflowActionIdentifier']} | {json.dumps(x['WFWorkflowActionParameters'],ensure_ascii=False)}" for i,x in enumerate(a)]
    (ROOT/f'reports/{name}-actions.txt').write_text('\n'.join(lines),encoding='utf8')
    graph=['flowchart TD']
    for i,x in enumerate(a):
        graph.append(f' a{i}["{i}: {x["WFWorkflowActionIdentifier"].split(".")[-1]}"]')
        if i+1<len(a):graph.append(f' a{i} --> a{i+1}')
    for src,dst,u in refs:
        if dst is not None:graph.append(f' a{dst} -. data .-> a{src}')
    graph.insert(1,' %% Solid edges are lexical order, NOT runtime branch edges. Grouping identifiers in inventory define branches.')
    (ROOT/f'reports/{name}-dependencies.mmd').write_text('\n'.join(graph),encoding='utf8')
    cfg=['flowchart TD',' %% Static control flow; native errors/cancellation may terminate at any UI/network action.']
    groups={}
    for i,x in enumerate(a):
        p=x['WFWorkflowActionParameters']
        if 'GroupingIdentifier' in p:groups.setdefault(p['GroupingIdentifier'],{})[p['WFControlFlowMode']]=i
        cfg.append(f' a{i}["{i}: {x["WFWorkflowActionIdentifier"].split(".")[-1]}"]')
    for i,x in enumerate(a):
        p=x['WFWorkflowActionParameters'];kind=x['WFWorkflowActionIdentifier'];mode=p.get('WFControlFlowMode');g=groups.get(p.get('GroupingIdentifier'),{})
        if kind.endswith('exit'):continue
        edges=[]
        if mode==0 and kind.endswith('conditional'):edges=[(i+1,'true'),(g.get(1,g[2]-1)+1,'false')]
        elif mode==1:edges=[(g[2],'join')]
        elif kind.endswith('repeat.count') and mode==0:edges=[(i+1,'iterate'),(g[2]+1,'zero iterations')]
        elif kind.endswith('repeat.count') and mode==2:edges=[(g[0]+1,'next iteration'),(i+1,'finished')]
        else:edges=[(i+1,'next')]
        for dest,label in edges:
            if dest<len(a):cfg.append(f' a{i} -->|{label}| a{dest}')
    (ROOT/f'reports/{name}-control-flow.mmd').write_text('\n'.join(cfg),encoding='utf8')
    return report
def main():
    original=plistlib.loads((ROOT/'original/workflow.bplist').read_bytes());new=plistlib.loads((ROOT/'dist/Video-Downloader-V1.0.unsigned.shortcut').read_bytes())
    before=audit(original,'original'); after=audit(new,'candidate')
    assert not after['missing_references'],after
    assert not after['forward_references'],after
    assert not after['control_or_token_errors'],after
    assert not any('deviceSpecific:' in str(v) for _,v in walk(new))
    assert not any(x['WFWorkflowActionIdentifier'].endswith('openurl') for x in new['WFWorkflowActions'])
    assert 'skip_update:"true"' in str(new)
    assert new['WFWorkflowName']=='🎞️ 影音下載器 V1.0'
    scripts=[]
    for x in new['WFWorkflowActions']:
        value=x['WFWorkflowActionParameters'].get('WFURLActionURL',{})
        if isinstance(value,dict):
            s=value.get('Value',{}).get('string','')
            if s.startswith('data:text/html,<script>'):scripts.append(s[len('data:text/html,<script>'):-len('</script>')])
    (ROOT/'reports/candidate-javascript.json').write_text(json.dumps(scripts,ensure_ascii=False,indent=2),encoding='utf8')
    # Deterministic rebuilding / plist round trip.
    sys.path.insert(0,str(ROOT/'src'));import build
    b=plistlib.dumps(new,fmt=plistlib.FMT_BINARY);build.build();assert (ROOT/'dist/Video-Downloader-V1.0.unsigned.shortcut').read_bytes()==b
    assert plistlib.loads(plistlib.dumps(new))==new
    result=subprocess.run(['node','tools/test-localize.cjs'],cwd=ROOT,capture_output=True,encoding='utf8');assert result.returncode==0,result.stderr
    (ROOT/'reports/adapter-tests.txt').write_text(result.stdout,encoding='utf8')
    runtime=subprocess.run(['node','tools/test-candidate-js.cjs'],cwd=ROOT,capture_output=True,encoding='utf8');assert runtime.returncode==0,runtime.stderr
    (ROOT/'reports/candidate-js-tests.txt').write_text(runtime.stdout,encoding='utf8')
    summary={'platform':platform.platform(),'official_shortcuts_cli':shutil.which('shortcuts'),'original':before,'candidate':after,'static_checks':'PASS','adapter_tests':result.stdout.splitlines()[-1],'candidate_js_tests':runtime.stdout.splitlines()[-1],'actual_download':'NOT EXECUTED','iOS_runtime':'待 iPhone 實機驗證','Apple_signature':'UNSIGNED CANDIDATE'}
    (ROOT/'reports/test-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.name!='sha256.json'}
    (ROOT/'reports/sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
