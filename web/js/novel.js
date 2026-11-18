// Original novel presentation. Atlas crops happen only while rendering the game.
let manifest={backgrounds:[],portraits:[]};
const images=new Map(),mounted=new Set();
const aliases={'Аэлина':'Ирис','Каэль':'Эйла','iris':'Ирис','eila':'Эйла','eyla':'Эйла','mira':'Мира','selena':'Селена'};
export const canonicalName=name=>aliases[name]||name||'Ирис';
export function setAssets(value){manifest=value||manifest;for(const key of ['backgrounds','portraits'])if(!Array.isArray(manifest[key]))manifest[key]=Object.entries(manifest[key]||{}).map(([id,v])=>({id,...v}));}
export function allArt(){return [...(manifest.backgrounds||[]),...(manifest.portraits||[])];}
export function artById(id){return allArt().find(a=>a.id===id)||null;}
export function sceneForChapter(chapter){const list=manifest.backgrounds||[];return list.find(a=>(a.chapterIds||a.chapters||[]).includes(Number(chapter)))||list[(Number(chapter)-1)%Math.max(1,list.length)]||null;}
export function portraitForName(name){name=canonicalName(name);const list=manifest.portraits||[];return list.find(a=>canonicalName(a.name||a.character||a.id)===name)||list[['Ирис','Эйла','Мира','Селена'].indexOf(name)]||list[0]||null;}
const attr=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function artMarkup(item,cls='',label=''){return '<div class="art-image '+attr(cls)+'" data-art="'+attr(item?.id||'')+'"'+(label?' role="img" aria-label="'+attr(label)+'"':' aria-hidden="true"')+'></div>';}
function imageFor(src){if(images.has(src))return images.get(src);const img=new Image();img.src=src;images.set(src,img);return img;}
function paint(el){const a=el._art;if(!a?.src)return;const img=imageFor(a.src);if(!img.complete||!img.naturalWidth){img.addEventListener('load',()=>paint(el),{once:true});return;}const at=a.atlas||{},cols=at.cols||1,rows=at.rows||1,col=at.col||0,row=at.row||0,cw=img.naturalWidth/cols,ch=img.naturalHeight/rows;
 const w=el.clientWidth,h=el.clientHeight;if(!w||!h)return;const scale=Math.max(w/cw,h/ch),isPortrait=manifest.portraits.some(x=>x.id===a.id);el.style.backgroundImage='url("'+a.src.replace(/"/g,'%22')+'")';el.style.backgroundSize=(img.naturalWidth*scale)+'px '+(img.naturalHeight*scale)+'px';el.style.backgroundPosition=((w-cw*scale)/2-col*cw*scale)+'px '+((isPortrait?0:(h-ch*scale)/2)-row*ch*scale)+'px';el.dataset.artLoaded='true';}
const observer=new ResizeObserver(entries=>{for(const {target}of entries){if(!target.isConnected){observer.unobserve(target);mounted.delete(target);}else paint(target);}});
export function bindArt(el,item){if(!el||!item)return;el._art=item;el.dataset.art=item.id;paint(el);if(!mounted.has(el)){mounted.add(el);observer.observe(el);}}
export function mountArt(root=document){for(const el of mounted)if(!el.isConnected){observer.unobserve(el);mounted.delete(el);}root.querySelectorAll('[data-art]').forEach(el=>bindArt(el,artById(el.dataset.art)));}
export function characterByName(data,name){name=canonicalName(name);return data.characters.find(c=>c.name===name)||data.characters[0];}
export function novelChapter(data,chapter){return data.chapters.find(c=>c.chapter===Number(chapter))||data.chapters[0];}
export function preference(bond){const traits=bond?.traits||{};return ['curiosity','care','candor'].reduce((best,k)=>(traits[k]||0)>(traits[best]||0)?k:best,'curiosity');}
