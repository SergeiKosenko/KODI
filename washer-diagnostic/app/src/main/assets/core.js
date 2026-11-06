/* Shared pure data logic; testable without an Android runtime. */
(function(root){
'use strict';
const norm=v=>String(v||'').trim().toUpperCase().replace(/[\s:._-]/g,'');
const codeNorm=v=>norm(v).replace(/[Оо]/g,'O').replace(/[Ее]/g,'E').replace(/[Сс]/g,'C').replace(/[Нн]/g,'H').replace(/[Рр]/g,'P').replace(/[Аа]/g,'A');
const modelNorm=v=>norm(v);
const matchCode=(codes,q)=>!q||codes.some(c=>codeNorm(c)===codeNorm(q));
const find=(entries,{brand='',model='',code='',system='all',saved=null}={})=>entries.filter(e=>(!brand||e.brand===brand)&&matchCode(e.codes,code)&&(system==='all'||e.system===system)&&(!saved||saved.includes(e.id))&&(!model||!e.models.length||e.models.some(m=>modelNorm(m)===modelNorm(model))));
const procedures=(items,brand,model)=>items.filter(p=>p.brand===brand&&model&&p.models.some(m=>modelNorm(m)===modelNorm(model)));
const string=(v,max=5000)=>typeof v==='string'&&v.trim().length>0&&v.length<=max;
const arr=(v,max=50)=>Array.isArray(v)&&v.length>0&&v.length<=max&&v.every(x=>string(x,2000));
function validatePack(raw){
 if(!raw||raw.schemaVersion!==1)throw Error('Нужен формат schemaVersion: 1.');
 const entries=raw.entries||[],procs=raw.procedures||[];
 if(!Array.isArray(entries)||!Array.isArray(procs)||entries.length+procs.length===0||entries.length+procs.length>3000)throw Error('База должна содержать от 1 до 3000 записей.');
 const ids=new Set();
 const base=x=>{if(!x||!string(x.id,100)||!string(x.brand,80)||!string(x.title,160)||!Array.isArray(x.models)||!x.models.every(m=>string(m,100)))throw Error('Некорректная запись: id, brand, title, models.');if(ids.has(x.id))throw Error('Повторяющийся id: '+x.id);ids.add(x.id);};
 const source=x=>{if(!x.source||!string(x.source.title,300)||!string(x.source.url,1500)||!string(x.source.page,100))throw Error('Для каждой записи укажите source: title, url, page.');let u;try{u=new URL(x.source.url)}catch{throw Error('Некорректная ссылка источника.')}if(u.protocol!=='https:')throw Error('Источник должен иметь HTTPS-ссылку.');return {title:x.source.title,url:u.href,page:x.source.page};};
 const es=entries.map(x=>{base(x);if(!arr(x.codes,20)||!arr(x.checks,30)||!arr(x.causes,20)||!string(x.summary)||!string(x.scope)||!['fill','drain','door','heat','motor','level','leak','balance','foam','comm'].includes(x.system))throw Error('Некорректные поля карточки ошибки.');return {id:x.id,brand:x.brand,title:x.title,models:x.models,codes:x.codes,checks:x.checks,causes:x.causes,summary:x.summary,scope:x.scope,system:x.system,source:source(x),status:'imported'};});
 const ps=procs.map(x=>{base(x);if(!x.models.length||!arr(x.steps,30)||!arr(x.prepare,20)||!string(x.exit)||!string(x.scope))throw Error('Сервисному режиму нужны точные models, prepare, steps, exit, scope.');return {id:x.id,brand:x.brand,title:x.title,models:x.models,steps:x.steps,prepare:x.prepare,exit:x.exit,scope:x.scope,source:source(x),status:'imported'};});
 return {schemaVersion:1,entries:es,procedures:ps};
}
const merge=(base,extra)=>{const m=new Map(base.map(x=>[x.id,x]));for(const x of extra)m.set(x.id,x);return [...m.values()];};
const api={norm,codeNorm,modelNorm,matchCode,find,procedures,validatePack,merge};root.WasherCore=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
