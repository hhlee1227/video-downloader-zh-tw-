const fs=require('node:fs');
const {translations}=require('../src/localize.js');
const rows=[['來源','繁體中文（台灣）','處理方式'],...Object.entries(translations).map(([a,b])=>[a,b,'遠端顯示副本；保留原 medias key，另建帶索引對應'])];
rows.push(['原遠端 menu_title','請選擇影音格式或項目','格式／多選提示改為本地文字'],['原遠端貼上提示','請貼上影音連結','本地 Ask 提示'],['原完成後選單','已完成所選影音的儲存。','移除選單並以通知取代'],['原裝置儲存路徑','請選擇儲存位置','移除裝置綁定路徑'],['未知 API 文字／影音標題','保留原文','待取得真實回應後補充翻譯；不猜測內容']);
fs.writeFileSync('reports/localization.csv','\ufeff'+rows.map(r=>r.map(x=>'"'+x.replaceAll('"','""')+'"').join(',')).join('\n'));
