const assert=require('node:assert/strict');
const {normalize,display,translations}=require('../src/localize.js');
let count=0;
function test(name,f){f();console.log('PASS '+name);count++;}
for(const [a,b] of Object.entries(translations))test('translation '+a,()=>assert.equal(display(a),b));
for(const [name,labels] of [['single video',['Video']],['multiple media',['Video 1','Video 2']],['audio',['Audio']]])test(name,()=>{const medias=Object.fromEntries(labels.map(x=>[x,{url:'https://example.invalid/media',ext:name==='audio'?'mp3':'mp4'}]));const r=normalize({labels,medias});r.labels.forEach((s,i)=>assert.deepEqual(r.medias[s],medias[labels[i]]));assert.deepEqual(r.medias[labels[0]],medias[labels[0]]);});
test('collision resistant',()=>{let r=normalize({labels:['关闭','關閉'],medias:{'关闭':{id:1},'關閉':{id:2}}});assert.equal(new Set(r.labels).size,2);});
test('malformed response',()=>assert.throws(()=>normalize({})));
test('missing media',()=>assert.throws(()=>normalize({labels:['x'],medias:{}})));
test('reload removed',()=>assert.equal(normalize({labels:[],medias:{},reload:'remote'}).reload,undefined));
test('API fields preserved',()=>{let r=normalize({labels:['选择格式'],medias:{'选择格式':{url:'x',file:true}},skip_select:true,select_multiple:true});assert.equal(r.skip_select,true);assert.equal(r.select_multiple,true);assert.equal(r.medias['选择格式'].url,'x');});
test('observed API update response blocked',()=>{const fs=require('node:fs');const o=JSON.parse(fs.readFileSync('reports/api-empty-input-response.bin','utf8'));assert.throws(()=>normalize(o),/更新/);});
test('unknown dynamic text retained honestly',()=>assert.equal(display('Unknown API label'),'Unknown API label'));
console.log(`${count} pure adapter tests passed. No iOS execution or network download.`);
