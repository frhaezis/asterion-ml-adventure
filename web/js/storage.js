const KEY='asterion.novel.v2', BACKUP=KEY+'.previous';
const native=()=>window.Android&&typeof window.Android.loadSave==='function';
async function digest(text){const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text));return [...new Uint8Array(bytes)].map(b=>b.toString(16).padStart(2,'0')).join('');}
function parse(value){if(typeof value==='string')return JSON.parse(value);return value;}
export async function unpack(value){
 const e=parse(value);
 if(e===null||e?.state===null)return null;
 if(e?.error)throw new Error(e.error);
 if(e.format!=='asterion-save'||e.version!==2||typeof e.payload!=='string')throw Error('Несовместимый формат сохранения.');
 if(await digest(e.payload)!==e.checksum)throw Error('Контрольная сумма сохранения не совпадает.');
 const state=JSON.parse(e.payload);
 if(state.version!==2||!Array.isArray(state.completed)||!state.levels||typeof state.levels!=='object')throw Error('Повреждено состояние игры.');
 if(state.campaignEdition!=='elf-beauties-v2')throw Error('Это сохранение другой редакции. Для новой истории нужен файл elf-beauties-v2; прежний прогресс не изменён.');
 return state;
}
export async function envelope(state){const payload=JSON.stringify(state);return {format:'asterion-save',version:2,payload,checksum:await digest(payload),savedAt:Date.now()};}
export class Store{
 async load(){
  try{if(native()){const e=parse(window.Android.loadSave());if(e?.error)return {state:null,error:e.error,recoveryAvailable:!!e.recoveryAvailable};return {state:await unpack(e)};}
   const value=localStorage.getItem(KEY);if(!value){if(localStorage.getItem(BACKUP))return {state:null,error:'Основное сохранение отсутствует. Доступна резервная копия.',recoveryAvailable:true};return {state:null};}
   return {state:await unpack(value)};
  }catch(e){return {state:null,error:e.message,recoveryAvailable:native()?true:!!localStorage.getItem(BACKUP)};}
 }
 async save(state){
  if(native()){const r=parse(window.Android.saveState(JSON.stringify(state)));if(!r?.ok)throw Error(r?.error||'Запись Android не подтверждена.');return r;}
  const old=localStorage.getItem(KEY);if(old){await unpack(old);localStorage.setItem(BACKUP,old);}
  localStorage.setItem(KEY,JSON.stringify(await envelope(state)));return {ok:true,savedAt:Date.now()};
 }
 async recover(){
  if(native())return unpack(window.Android.recoverSave());
  const previous=localStorage.getItem(BACKUP);if(!previous)throw Error('Резервная копия отсутствует.');
  const state=await unpack(previous);localStorage.setItem(KEY,previous);return state;
 }
 async export(state){
  if(native()){window.Android.exportSave();return;}
  const blob=new Blob([JSON.stringify(await envelope(state),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download='Asterion-save.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
 }
 async import(value){
  const state=await unpack(value);if(!state)throw Error('В файле нет прогресса.');
  if(native()){const r=parse(window.Android.saveState(JSON.stringify(state)));if(!r.ok)throw Error(r.error||'Импорт не записан.');}
  else{const current=localStorage.getItem(KEY);if(current){try{await unpack(current);localStorage.setItem(BACKUP,current);}catch{}}
   localStorage.setItem(KEY,JSON.stringify(parse(value)));
  }return state;
 }
 nativeImport(){if(native()){window.Android.importSave();return true;}return false;}
 get native(){return !!native();}
}
