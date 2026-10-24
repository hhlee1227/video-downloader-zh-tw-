from pathlib import Path
import plistlib,copy,json,uuid,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
_serial=0
def uid():
    global _serial
    _serial+=1
    return str(uuid.uuid5(uuid.NAMESPACE_URL,'video-downloader-v1/'+str(_serial))).upper()
def act(name,**p): return {'WFWorkflowActionIdentifier':'is.workflow.actions.'+name,'WFWorkflowActionParameters':p}
def ref(u): return {'Value':{'Type':'ActionOutput','OutputUUID':u},'WFSerializationType':'WFTextTokenAttachment'}
def var(n): return {'Value':{'Type':'Variable','VariableName':n},'WFSerializationType':'WFTextTokenAttachment'}
def token(s,attachments):
    return {'Value':{'string':s,'attachmentsByRange':{'{%d, 1}'%i:a for i,a in attachments}},'WFSerializationType':'WFTextTokenString'}
def cond(value,code,g,mode=0,**kw): return act('conditional',WFInput={'Type':'Variable','Variable':value},WFCondition=code,GroupingIdentifier=g,WFControlFlowMode=mode,**kw)
def guard(value,message):
    g=uid()
    return [cond(value,101,g),act('alert',WFAlertActionTitle='無法繼續',WFAlertActionMessage=message,WFAlertActionCancelButtonShown=False),act('exit'),act('conditional',GroupingIdentifier=g,WFControlFlowMode=2)]
def jsbridge(source,inputref):
    b,u,d=uid(),uid(),uid()
    s='data:text/html,<script>var raw="\ufffc";'+source+'</script>'
    rich=ref(u);rich['Value']['Aggrandizements']=[{'Type':'WFCoercionVariableAggrandizement','CoercionItemClass':'WFRichTextContentItem'}]
    return [act('base64encode',WFInput=inputref,WFBase64LineBreakMode='None',UUID=b),act('url',WFURLActionURL=token(s,[(s.index('\ufffc'),{'Type':'ActionOutput','OutputUUID':b})]),UUID=u),act('urlencode',WFInput=rich,WFEncodeMode='Decode',UUID=d)],d
def build():
    global _serial
    _serial=0
    w=plistlib.loads((ROOT/'original/workflow.bplist').read_bytes()); a=copy.deepcopy(w['WFWorkflowActions']); out=[]
    w['WFWorkflowName']='🎞️ 影音下載器 V1.0'
    ext={'Value':{'Type':'ExtensionInput'},'WFSerializationType':'WFTextTokenAttachment'}
    g=uid(); ask=uid(); match=uid(); result=uid()
    out += [cond(ext,100,g),act('gettext',WFTextActionText=ext),act('conditional',GroupingIdentifier=g,WFControlFlowMode=1),act('ask',WFAskActionPrompt='請貼上影音連結',WFAskActionDefaultAnswer={'Value':{'Type':'Clipboard'},'WFSerializationType':'WFTextTokenAttachment'},UUID=ask),act('conditional',GroupingIdentifier=g,WFControlFlowMode=2,UUID=result)]
    out += [act('text.match',WFInput=ref(result),WFMatchTextPattern=r'https?://(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,63}(?::[0-9]{1,5})?(?:[/?#][^\s<>"\x00-\x1f]*)?(?=$|\s)',UUID=match)]
    out += guard(ref(match),'請提供以 http:// 或 https:// 開頭的有效影音連結。')
    first=uid(); out += [act('getitemfromlist',WFInput=ref(match),WFItemSpecifier='First Item',UUID=first)]
    for n in ['label_now','m_album','m_file','menu_done']:
        empty=uid();out += [act('nothing',UUID=empty),act('setvariable',WFVariableName=n,WFInput=ref(empty))]
    for i,x in enumerate(a):
        p=x['WFWorkflowActionParameters']
        if i==0:p['WFCommentActionText']='🎞️ 影音下載器 V1.0｜未簽署候選版本，待 iPhone 實機驗證。'
        if i==2:p['WFCommentActionText']='使用說明：從分享選單傳入影音連結，或執行捷徑後貼上連結。格式與多選項目由下載服務提供。音訊儲存至檔案；影片可儲存至照片。第三方服務會收到影音網址與網路資訊。'
        if i==3:p['WFInput']=ref(first)
        if i==4:
            v=p['WFURLActionURL']['Value']; s=v['string']; s=s.replace('lang:lang','lang:"zh-TW"').replace('skip_update:t.indexOf("{{skip_update}}")>-1?"true":"false"','skip_update:"true"');v['string']=s
        if i==15:
            x=act('alert',WFAlertActionTitle='服務要求重新載入',WFAlertActionMessage='已停止遠端重新執行，避免覆蓋繁體中文版。請稍後重新執行本捷徑。',WFAlertActionCancelButtonShown=False)
        if i==20:
            source=(ROOT/'src/localize.js').read_text(encoding='utf8')+'\ntry{document.write(JSON.stringify(normalize(JSON.parse(decodeURIComponent(escape(atob(raw)))))));}catch(e){document.write(JSON.stringify({error:String(e.message)}));}'
            bridge,last=jsbridge(source,p['WFInput']);out+=bridge;p['WFInput']=ref(last)
            out+=guard(ref(last),'下載服務沒有回傳可用資料。')
        if i==21:
            error=copy.deepcopy(a[22]['WFWorkflowActionParameters']['WFInput']);error['Value']['Aggrandizements'][-1]['DictionaryKey']='error'
            eg=uid();out += [cond(error,100,eg),act('alert',WFAlertActionTitle='下載服務無法繼續',WFAlertActionMessage=error,WFAlertActionCancelButtonShown=False),act('exit'),act('conditional',GroupingIdentifier=eg,WFControlFlowMode=2)]
            # Verify labels after dictionary coercion; guard malformed / empty API responses.
            labels=copy.deepcopy(a[22]['WFWorkflowActionParameters']['WFInput']);labels['Value']['Aggrandizements'][-1]['DictionaryKey']='labels'
            out+=guard(labels,'下載服務未提供可用的影音項目，可能不支援此連結或服務暫時異常。')
        if i in (25,27):p['WFChooseFromListActionPrompt']='請選擇影音格式或項目'
        if i==32:
            # First iteration has no media output yet; subsequent iterations retain last record.
            continue
        if i==38:
            out.append(act('setvariable',WFVariableName='label_now',WFInput=ref('790AF8CB-3ADA-4166-8259-635294BAB02C')))
        if i in (42,49):
            p['WFWorkflowName']='🎞️ 影音下載器 V1.0';p['WFWorkflow']['workflowName']='🎞️ 影音下載器 V1.0'
        if i==47:p['WFAskActionPrompt']='請貼上影音連結'
        if i==56:
            x=act('alert',WFAlertActionTitle='服務要求開啟外部頁面',WFAlertActionMessage='此版本已停止自動開啟遠端頁面及更新安裝。若下載失敗，請稍後再試。',WFAlertActionCancelButtonShown=False)
        if i==64:p.pop('WFFolder',None);p['WFAskWhereToSave']=True
        if i==63:
            sg=uid();li=uid();sel=uid();dest=uid()
            file_input=copy.deepcopy(p['WFInput']['Variable'])
            out += [cond(file_input,100,sg),act('gettext',WFTextActionText='儲存至檔案'),act('conditional',GroupingIdentifier=sg,WFControlFlowMode=1),act('list',WFItems=['儲存至照片','儲存至檔案'],UUID=li),act('choosefromlist',WFInput=ref(li),WFChooseFromListActionPrompt='請選擇儲存位置',WFChooseFromListActionSelectMultiple=False,UUID=sel),act('conditional',GroupingIdentifier=sg,WFControlFlowMode=2,UUID=dest)]
            p['WFInput']={'Type':'Variable','Variable':ref(dest)};p['WFCondition']=4;p['WFConditionalActionString']='儲存至檔案'
        if i==71:
            # Replace completion menu with a notification, then stop inside original if.
            pass
        if 72<=i<=81:continue
        if i==82:out.append(act('notification',WFNotificationActionTitle='影音下載器',WFNotificationActionBody='已完成所選影音的儲存。'))
        out.append(x)
    out.append(act('alert',WFAlertActionTitle='未能完成下載',WFAlertActionMessage='已達處理次數上限。請減少所選項目後重試；已儲存的項目會保留。',WFAlertActionCancelButtonShown=False))
    # Remove references to discarded completion menu output; no consumer remains.
    w['WFWorkflowActions']=out
    (ROOT/'dist/Video-Downloader-V1.0.unsigned.shortcut').write_bytes(plistlib.dumps(w,fmt=plistlib.FMT_BINARY))
    (ROOT/'src/workflow.zh-TW.plist').write_bytes(plistlib.dumps(w))
    return w
if __name__=='__main__': print('Built',len(build()['WFWorkflowActions']),'actions; UNSIGNED')
