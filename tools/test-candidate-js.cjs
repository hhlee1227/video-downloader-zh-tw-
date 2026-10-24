const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const scripts=JSON.parse(fs.readFileSync('reports/candidate-javascript.json','utf8'));
assert.equal(scripts.length,2);
function run(s,values){let i=0,output='';s=s.replaceAll('\ufffc',()=>values[i++]);new vm.Script(s).runInNewContext({atob,btoa,escape,unescape,encodeURIComponent,decodeURIComponent,navigator:{language:'en-US'},document:{write:s=>output+=s}});return JSON.parse(output);}
const url='https://example.invalid/video?id=123';
const first=run(scripts[0],[Buffer.from('Caption '+url).toString('base64'),JSON.stringify({ask_format:true,show_menu:true})]);
assert.equal(Buffer.from(first.url64,'base64').toString(),url);assert.equal(first.lang,'zh-TW');assert.equal(first.skip_update,'true');
console.log('PASS actual generated bootstrap URL extraction, locale and update flag in Node VM');
const fixture={labels:['选择操作'],medias:{'选择操作':{url,ext:'mp4'}},menu_title:'选择操作'};
let result=run(scripts[1],[Buffer.from(JSON.stringify(fixture)).toString('base64')]);assert.equal(result.labels[0],'1. 請選擇操作');assert.equal(result.medias[result.labels[0]].url,url);
console.log('PASS actual generated adapter bridge preserves media mapping');
result=run(scripts[1],[Buffer.from('invalid JSON').toString('base64')]);assert.equal(typeof result.error,'string');
console.log('PASS actual generated adapter bridge catches malformed JSON');
const update=fs.readFileSync('reports/api-empty-input-response.bin');result=run(scripts[1],[update.toString('base64')]);assert.match(result.error,/更新/);
console.log('PASS actual generated adapter bridge rejects observed update response');
console.log('4 generated JavaScript tests passed in Node VM; WebKit and iOS not executed.');
