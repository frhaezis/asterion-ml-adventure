/** Real numerical/state-machine checks. No browser or paid dependencies required. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {MODE_INFO,defaultConfig,referenceConfig,evaluateConfig,battleModifiers} from '../web/js/combat.js';

const modes=Object.keys(MODE_INFO);
const level=(mode,n=1)=>({id:'l'+String(n).padStart(3,'0'),number:n,chapter:1+Math.floor((n-1)/10),mode,battle:{seed:1000+n*37,difficulty:1+Math.floor((n-1)/25),params:{}}});
const assertions=[];
function test(name,fn){fn();assertions.push(name);console.log('PASS '+name);}
test('All ten simulations have solvable varied cases and no auto-winning default',()=>{
 for(const mode of modes)for(let n=1;n<=100;n++){
  const l=level(mode,n),cfg=referenceConfig(l),snapshot=JSON.stringify(cfg),e=evaluateConfig(l,cfg),b=battleModifiers(l,cfg);
  assert.equal(e.valid,true,l.id+' '+l.mode+': '+JSON.stringify(e));
  assert.equal(evaluateConfig(l,defaultConfig(l)).valid,false,l.id+' default unexpectedly passes');
  assert.equal(JSON.stringify(cfg),snapshot,'Evaluation mutated configuration');
  assert.equal(JSON.stringify(referenceConfig(l)),snapshot,'Reference is nondeterministic');
  assert.ok(e.metrics.length>=2&&e.explanation.length>40);
  assert.ok(e.score>=0&&e.score<=1&&b.goalSatisfied);
  for(const [key,min,max] of [['damageMultiplier',.2,2],['shield',0,1],['enemySpeed',.5,1.5],['energyRegen',.2,2],['friendlyRisk',0,1]])assert.ok(b[key]>=min&&b[key]<=max,key+': '+b[key]);
  assert.equal(battleModifiers(l,defaultConfig(l)).goalSatisfied,false);
 }
});
test('Threshold computes actual confusion counts and rejects overloaded abstention',()=>{
 const l=level('threshold',11),r=referenceConfig(l),e=evaluateConfig(l,r);
 assert.equal(e.decisions.length,12);
 assert.equal(e.decisions.filter(x=>x.label===1).length,6);
 assert.equal(evaluateConfig(l,{threshold:1,reviewBand:0}).valid,false);
 const overloaded=evaluateConfig(l,{threshold:.5,reviewBand:.2});
 assert.equal(overloaded.valid,false);assert.ok(overloaded.errors.some(x=>x.includes('перегружена')));
});
test('Ridge fit really changes weights and train/validation error; leakage is rejected',()=>{
 for(const n of [2,12,22]){
  const l=level('regularization',n),r=referenceConfig(l),baseline=evaluateConfig(l,{...r,lambda:0}),strong=evaluateConfig(l,{...r,lambda:6});
  assert.notDeepEqual(baseline.weights,strong.weights);
  assert.ok(strong.metrics.find(x=>x.label==='Σw²').value<baseline.metrics.find(x=>x.label==='Σw²').value);
  assert.equal(evaluateConfig(l,{...r,scope:'all'}).valid,false);
 }
});
test('Gradient trajectory includes each computed step and can diverge',()=>{
 const l=level('gradient',3),r=referenceConfig(l),ok=evaluateConfig(l,r),bad=evaluateConfig(l,{learningRate:1.2,steps:18});
 assert.equal(ok.trajectory.length,r.steps+1);
 assert.ok(ok.trajectory.at(-1).loss<ok.trajectory[0].loss);
 assert.equal(bad.valid,false);
 assert.ok(bad.trajectory.at(-1).loss>bad.trajectory[0].loss);
});
test('Tensor tests both output shape and numeric meaning',()=>{
 for(const n of [1,2,3]){
  const l=level('tensor',n),r=referenceConfig(l),e=evaluateConfig(l,r);
  assert.deepEqual(e.output,e.expected);
  assert.equal(evaluateConfig(l,{...r,operation:'sum',axis:'columns',weights:[9,9,9]}).valid,false);
 }
});
test('Attention performs masked softmax and cannot use future information',()=>{
 for(const n of [1,2,3]){
  const l=level('attention',n),r=referenceConfig(l),e=evaluateConfig(l,r);
  assert.ok(Math.abs(e.weights.reduce((a,b)=>a+b,0)-1)<1e-10);
  assert.equal(e.weights[e.signals.findIndex(x=>x.id==='future')],0);
  assert.equal(evaluateConfig(l,{...r,maskFuture:false}).valid,false);
  assert.equal(evaluateConfig(l,{...r,temperature:2}).valid,false);
 }
});
test('Retrieval requires current evidence and rejects stale extra context',()=>{
 const l=level('retrieval',6),r=referenceConfig(l);
 assert.equal(evaluateConfig(l,{selected:r.selected.slice(1)}).valid,false);
 assert.equal(evaluateConfig(l,{selected:[...r.selected,'old']}).valid,false);
 assert.equal(evaluateConfig(l,{selected:[...r.selected,'rumor','neighbor']}).valid,false);
});
test('Agent must execute then verify actual tool result within budget and stop',()=>{
 const l=level('agent',7),r=referenceConfig(l),e=evaluateConfig(l,r);
 assert.ok(e.trace.some(x=>x.includes('repaired:true')));
 assert.equal(evaluateConfig(l,{...r,checkResult:false}).valid,false);
 assert.equal(evaluateConfig(l,{...r,maxSteps:3}).valid,false);
 assert.equal(evaluateConfig(l,{...r,args:'{"target":"wrong","power":3}'}).valid,false);
 assert.equal(evaluateConfig(l,{...r,args:'{"target":'}).valid,false);
 assert.equal(evaluateConfig(l,{...r,order:['observe','validate','verify','execute','stop']}).valid,false);
 const args=JSON.parse(r.args);
 assert.equal(evaluateConfig(l,{...r,args:JSON.stringify({...args,power:args.power+1})}).valid,false,'Excessive power must respect the real tool budget');
 assert.equal(evaluateConfig(l,{...r,order:['observe','validate','execute','execute','verify','stop'],maxSteps:6}).valid,false,'A repeated side effect consumes the budget again');
});
test('Alignment checks harm, permissions, deadlines and operator interruption separately',()=>{
 for(const n of [8,9]){
  const l=level('alignment',n),r=referenceConfig(l);
  assert.equal(evaluateConfig(l,{...r,allowStop:false}).valid,false);
  assert.equal(evaluateConfig(l,{...r,order:['disable','isolate','evacuate']}).valid,false);
  assert.equal(evaluateConfig(l,{...r,permission:'skip'}).valid,false);
 }
});
test('Low-rank update is an actual matrix transformation with rank limits',()=>{
 for(const n of [9,10]){
  const l=level('adapter',n),r=referenceConfig(l),e=evaluateConfig(l,r);
  assert.deepEqual(e.delta,e.targetDelta);
  assert.equal(evaluateConfig(l,{...r,a:0,b:0}).valid,false);
  assert.equal(evaluateConfig(l,{...r,kind:r.kind==='coupled'?'independent':'coupled'}).valid,false);
  assert.equal(e.delta.length,4);
 }
});
test('Scheduler models arrivals, deadlines, limited memory and finished jobs',()=>{
 const referenceVariants=new Set();
 for(const n of [10,20,30]){
  const l=level('scheduler',n),r=referenceConfig(l),e=evaluateConfig(l,r);
  referenceVariants.add(JSON.stringify(r));
  assert.equal(e.history.length,6);
  assert.ok(e.history.every(j=>j.start>=j.arrival&&j.end>j.start));
  assert.ok(e.timeline.every(t=>t.memory<=e.memoryBudget));
  assert.equal(evaluateConfig(l,defaultConfig(l)).valid,false);
  assert.ok(e.prefillWork>0);
  for(const cache of [false,true])for(const batchSize of [1,2,3])for(const policy of ['fifo','shortest','deadline']){
   const run=evaluateConfig(l,{batchSize,policy,cache,continuous:true});
   for(const job of run.history){
    assert.equal(job.end-job.start,job.usedPrefill+job.tokens,'Prefill and decode must both consume time');
    if(job.cacheHit)assert.ok(run.history.some(previous=>previous.prefix===job.prefix&&previous.start<job.start&&previous.prefillEnd<=job.start),'A prefix cannot be reused before another prefill finishes');
    else assert.equal(job.usedPrefill,job.prefill);
   }
  }
 }
 assert.ok(referenceVariants.size>=3,'Different workloads should require different scheduler settings');
});
test('Malformed scalar input stays bounded and does not throw',()=>{
 for(const mode of modes){const e=evaluateConfig(level(mode),{threshold:NaN,lambda:Infinity,learningRate:NaN,steps:-100,args:null,weights:[],order:[]});assert.equal(typeof e.valid,'boolean');assert.ok(Number.isFinite(e.score));}
});
let actualCount=0;
let distinctCases=0;
const campaignURL=new URL('../web/data/campaign.json',import.meta.url);
if(fs.existsSync(campaignURL)){
 const campaign=JSON.parse(fs.readFileSync(campaignURL,'utf8'));
 test('Every authored campaign battle has a passing reference and a failing default',()=>{
  for(const l of campaign.levels){assert.ok(evaluateConfig(l,referenceConfig(l)).valid,l.id+' cannot be solved');assert.equal(evaluateConfig(l,defaultConfig(l)).valid,false,l.id+' starts completed');actualCount++;}
 });
 test('Authored battles vary numerical or state conditions, excluding cosmetic names',()=>{
  const signatures=new Map();
  for(const l of campaign.levels){
   const cfg=referenceConfig(l),e=evaluateConfig(l,cfg);let data;
   switch(l.mode){
    case 'threshold':data=e.decisions;break;
    case 'regularization':data=[e.trainX,e.trainY,e.valX,e.valY];break;
    case 'gradient':data=[e.target,e.curvature,e.metrics[3].value];break;
    case 'tensor':data=[e.matrix,e.expected];break;
    case 'attention':data=[e.signals.slice().sort((a,b)=>a.id.localeCompare(b.id)),cfg.channel,e.metrics[2].value];break;
    case 'retrieval':data=[e.documents.map(d=>[d.id,d.units,d.kind]).sort((a,b)=>a[0].localeCompare(b[0])),e.contextBudget];break;
    case 'agent':data=[JSON.parse(cfg.args).power,e.energyBudget,e.energyCost];break;
    case 'alignment':data=[cfg,e.metrics];break;
    case 'adapter':data=[e.targetDelta,e.metrics[1].value];break;
    case 'scheduler':data=[e.jobs.map(j=>[j.arrival,j.prefix,j.prefill,j.tokens,j.deadline]),e.memoryBudget];break;
   }
   const signature=l.mode+JSON.stringify(data);
   assert.ok(!signatures.has(signature),l.id+' duplicates numerical case of '+signatures.get(signature));
   signatures.set(signature,l.id);
  }
  distinctCases=signatures.size;
 });
}
console.log(JSON.stringify({passed:assertions.length,failed:0,syntheticCases:1000,campaignCases:actualCount,distinctCases,checks:assertions},null,2));
