// Pure display adapter. API request keys and media records remain unchanged.
const translations = {
  '选择操作':'請選擇操作','输入视频链接':'貼上影音連結','使用指南':'使用說明',
  '分享菜单中没有显示？':'分享選單未顯示？','下次隐藏此菜单':'下次不再顯示',
  '输入视频链接。已复制的链接会自动粘贴。':'請貼上影音連結',
  '关闭':'關閉','打开相册':'開啟照片','打开文件':'開啟檔案',
  '下载完成':'儲存完成','选择格式':'請選擇影音格式','选择视频':'請選擇影音項目',
  'Choose media:':'請選擇影音項目','Close':'關閉','JPG UPDATE GUIDE':'更新說明圖片'
};
function display(s) {
  if (typeof s !== 'string') return s;
  for (const [a,b] of Object.entries(translations).sort((a,b)=>b[0].length-a[0].length)) s=s.split(a).join(b);
  return s;
}
function normalize(o) {
  if (!o || typeof o !== 'object' || !Array.isArray(o.labels) || !o.medias || typeof o.medias !== 'object')
    throw new Error('服務回應格式不符，請稍後再試。');
  if (/updat.{0,30}shortcut/i.test(String(o.title||'')+' '+String(o.message||'')))
    throw new Error('服務要求更新原版捷徑，已停止以保留繁體中文版。');
  const r={...o, labels:[], medias:{...o.medias}};
  o.labels.forEach((key,i)=>{
    if(typeof key!=='string' || !Object.prototype.hasOwnProperty.call(o.medias,key)) throw new Error('找不到影音項目。');
    const label=`${i+1}. ${display(key)}`;
    r.labels.push(label); r.medias[label]=o.medias[key];
  });
  for(const k of ['menu_title','menu_done_title','open_album','open_file','close']) r[k]=display(o[k]);
  r.menu_title=display(o.menu_title||'請選擇影音格式或項目');
  // Reload is controlled by the server and can re-enter an update path.
  delete r.reload;
  return r;
}
if(typeof module!=='undefined') module.exports={normalize,display,translations};
