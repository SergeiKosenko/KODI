const test=require('node:test'),assert=require('node:assert/strict');
const C=require('../app/src/main/assets/core.js');
const data=require('../app/src/main/assets/catalog.json');
test('code normalization keeps real code distinctions and tolerates spaces/colon/Cyrillic lookalikes',()=>{
 assert(C.matchCode(['E:18'],' е 18 '));assert(C.matchCode(['OE'],'ОЕ'));assert(!C.matchCode(['OE'],'0E'));assert(!C.matchCode(['E10'],'E1'));
});
test('a code never leaks across selected manufacturers',()=>{
 const result=C.find(data.entries,{brand:'LG',code:'OE'});assert.equal(result.length,1);assert.equal(result[0].system,'drain');assert.equal(C.find(data.entries,{brand:'Bosch',code:'OE'}).length,0);
});
test('unlisted exact models cannot inherit a service procedure',()=>{
 assert.equal(C.procedures(data.procedures,'LG','F1096ND3').length,1);assert.equal(C.procedures(data.procedures,'LG',' F1096-ND3 ').length,1);assert.equal(C.procedures(data.procedures,'LG','F1096').length,0);assert.equal(C.procedures(data.procedures,'Samsung','F1096ND3').length,0);assert.equal(C.procedures(data.procedures,'LG','').length,0);
});
const pack=()=>({schemaVersion:1,entries:[{id:'manual-code',brand:'Test',models:['MODEL1'],title:'Test error',codes:['E01'],system:'drain',summary:'Summary',scope:'MODEL1, revision 1',checks:['Inspect'],causes:['Cause'],source:{title:'Service manual',url:'https://example.org/manual.pdf',page:'12'}}],procedures:[]});
test('imports retain exact scope, require provenance and cannot self-assert verification',()=>{
 const p=pack();p.entries[0].status='verified';assert.equal(C.validatePack(p).entries[0].status,'imported');assert.equal(C.find(C.validatePack(p).entries,{model:'MODEL2'}).length,0);
 delete p.entries[0].source;assert.throws(()=>C.validatePack(p),/source/);
});
test('malformed and unsafe imports fail atomically',()=>{
 const p=pack();p.entries[0].source.url='javascript:alert(1)';assert.throws(()=>C.validatePack(p),/HTTPS/);
 const p2=pack();p2.entries.push(p2.entries[0]);assert.throws(()=>C.validatePack(p2),/Повторяющийся/);
 assert.throws(()=>C.validatePack({schemaVersion:2}));assert.throws(()=>C.validatePack({schemaVersion:1,entries:[],procedures:[]}));
});
test('service imports need explicit model list and safe exit documentation',()=>{
 const p={schemaVersion:1,entries:[],procedures:[{id:'test',brand:'Test',models:[],title:'Service',scope:'Scope',steps:['Entry'],prepare:['Prep'],exit:'Power off',source:{title:'Manual',url:'https://example.org/manual.pdf',page:'10'}}]};assert.throws(()=>C.validatePack(p));p.procedures[0].models=['MODEL1'];assert.equal(C.validatePack(p).procedures.length,1);
});
test('catalog has unique IDs, explicit uncertainty, complete reference cards',()=>{
 assert.equal(new Set(data.entries.map(e=>e.id)).size,data.entries.length);
 for(const e of data.entries){assert(data.brands.includes(e.brand));assert(e.checks.length>0);assert.equal(e.status,'reference');assert.equal(e.source,null)}
});
