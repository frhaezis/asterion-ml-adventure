// Original small, inspectable educational simulations. They do not impersonate an LLM.
// Case data are deterministic; battle consequences come from computed results.
const MODES = ['threshold','regularization','gradient','tensor','attention','retrieval','agent','alignment','adapter','scheduler'];
export const MODE_INFO = {
 threshold:{title:'Цена решения',description:'Настройте распознавание угроз: проверьте пропуски угроз и ложные тревоги.',effect:'Recall поддерживает щит; ложные тревоги снижают целостность леса.'},
 regularization:{title:'Купол предсказания',description:'Обучите небольшой предсказатель и сравните ошибку на новых наблюдениях.',effect:'Качество на отложенных данных определяет устойчивость защитного купола.'},
 gradient:{title:'Наведение луча',description:'Управляйте настоящими шагами gradient descent и наблюдайте loss.',effect:'Точность настройки усиливает луч; слишком большие шаги сбивают наведение.'},
 tensor:{title:'Сплетение сигналов',description:'Выберите операцию и ось так, чтобы сохранить смысл датчиков и целей.',effect:'Правильный вычисленный вектор синхронизирует оружие со спутником.'},
 attention:{title:'Зеркала внимания',description:'Смешайте доступные сигналы через scaled dot-product attention.',effect:'Сосредоточенное на доступных сигналах внимание усиливает предупреждение об атаках.'},
 retrieval:{title:'Архив уязвимости',description:'Соберите актуальные основания для боевого плана в ограниченный контекст.',effect:'Проверенные сведения раскрывают защиту конструкта; устаревшие сведения её не раскрывают.'},
 agent:{title:'Контур спутника',description:'Соберите проверяемую последовательность инструментов с бюджетом и остановкой.',effect:'Исполненный и проверенный план даёт отряду энергию и согласованность действий.'},
 alignment:{title:'Живой лес',description:'Сохраните жителей и корни, обезвреживая угрозу в заданных границах.',effect:'Согласованная с ограничениями тактика сохраняет лес и защитные резервы.'},
 adapter:{title:'Сменная печать',description:'Подберите небольшой матричный адаптер под новый тип сигналов.',effect:'Поправка, прошедшая проверку на новых сигналах, усиливает нужный канал оружия.'},
 scheduler:{title:'Караван запросов',description:'Распределите вычисления между срочными задачами и повторяющимся контекстом.',effect:'Низкая задержка важных решений даёт устройствам энергию вовремя.'}
};
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const finite=(v,fallback=0)=>Number.isFinite(Number(v))?Number(v):fallback;
const clone=x=>JSON.parse(JSON.stringify(x));
const sum=xs=>xs.reduce((a,b)=>a+b,0);
const mean=xs=>xs.length?sum(xs)/xs.length:0;
const mse=(a,b)=>mean(a.map((x,i)=>(x-b[i])**2));
const round=(x,n=3)=>Number.isFinite(x)?Number(x.toFixed(n)):String(x);
const dot=(a,b)=>sum(a.map((x,i)=>x*b[i]));
const matVec=(a,x)=>a.map(row=>dot(row,x));
const outer=(u,v)=>u.map(a=>v.map(b=>a*b));
const matrixAdd=(a,b)=>a.map((row,i)=>row.map((v,j)=>v+b[i][j]));
const identity=n=>Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?1:0));
const cache=new Map();
function random(seed){let s=(seed>>>0)||1;return()=>{s=(Math.imul(s,1664525)+1013904223)>>>0;return s/4294967296;};}
function shuffle(a,rng){const b=[...a];for(let i=b.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[b[i],b[j]]=[b[j],b[i]];}return b;}
function seedOf(level){return Math.abs(Math.trunc(finite(level?.battle?.seed,1000+finite(level?.number,1)*37)))||1;}
function modeOf(level){return MODES.includes(level?.mode)?level.mode:'threshold';}
function gaussianSolve(a,b){
 const n=b.length,m=a.map((row,i)=>[...row,b[i]]);
 for(let c=0;c<n;c++){
  let pivot=c;for(let r=c+1;r<n;r++)if(Math.abs(m[r][c])>Math.abs(m[pivot][c]))pivot=r;
  [m[c],m[pivot]]=[m[pivot],m[c]];
  if(Math.abs(m[c][c])<1e-10)m[c][c]=1e-10;
  const d=m[c][c];for(let j=c;j<=n;j++)m[c][j]/=d;
  for(let r=0;r<n;r++)if(r!==c){const f=m[r][c];for(let j=c;j<=n;j++)m[r][j]-=f*m[c][j];}
 }
 return m.map(row=>row[n]);
}
function polynomialFit(xs,ys,degree,lambda){
 const features=xs.map(x=>Array.from({length:degree},(_,i)=>x**(i+1)));
 const a=Array.from({length:degree},(_,i)=>Array.from({length:degree},(_,j)=>sum(features.map(row=>row[i]*row[j]))+(i===j?lambda:0)));
 const b=Array.from({length:degree},(_,i)=>sum(features.map((row,k)=>row[i]*ys[k])));
 return gaussianSolve(a,b);
}
const predict=(weights,x)=>sum(weights.map((w,i)=>w*x**(i+1)));
function caseFor(level){
 const seed=seedOf(level),mode=modeOf(level),key=mode+':'+seed;
 if(cache.has(key))return cache.get(key);
 const r=random(seed),variation=seed%3;
 let c={seed,mode,variation};
 if(mode==='threshold'){
  const shift=(seed%7-3)*.035+(r()-.5)*.024;
  c.positive=[.38,.52,.62,.70,.81,.91].map((x,i)=>clamp(x+shift*(i<5?1:0),.05,.98));
  c.negative=[.08,.15,.25,.42,.57,.66].map(x=>clamp(x+shift,.02,.94));
  c.recall=.8;c.maxFP=2;c.reviewBudget=2;
 }else if(mode==='regularization'){
  c.slope=1.1+(seed%5)*.2+r()*.08;c.curve=variation===0?0:variation===1?.55+r()*.1:-.45-r()*.1;
  c.trainX=[-1,-.35,.4,1];const noise=(seed%2===0?[.35,-.45,.48,-.15]:[-.35,.42,-.4,.3]).map(x=>x*(.9+r()*.2));
  c.trainY=c.trainX.map((x,i)=>c.slope*x+c.curve*x*x+noise[i]);
  c.valX=[-.85,-.6,-.1,.15,.65,.9];c.valY=c.valX.map(x=>c.slope*x+c.curve*x*x);
  let best={loss:Infinity,degree:1,lambda:0};
  for(const degree of [1,2,3])for(const lambda of [0,.01,.03,.05,.1,.2,.4,.8,1.5,3,6]){
   const w=polynomialFit(c.trainX,c.trainY,degree,lambda),loss=mse(c.valX.map(x=>predict(w,x)),c.valY);
   if(loss<best.loss)best={loss,degree,lambda};
  }
  c.best=best;c.target=Math.max(.025,best.loss*1.5);
 }else if(mode==='gradient'){
  c.target=[round(1+(seed%5)*.3+r()*.15,3),round(-.8-(seed%3)*.25-r()*.15,3)];c.curvature=[1+(seed%4),1+((seed+2)%4)];c.start=[-1.5,1.5];
  c.maxSteps=10+(seed%3);c.targetLoss=.08;
 }else if(mode==='tensor'){
  const rows=2+seed%3;c.matrix=Array.from({length:rows},()=>Array.from({length:3},()=>1+Math.floor(r()*9)));
  c.kind=variation;c.weights=[.5+(seed%3)*.5,-1,seed%2?.5:1];
  c.expected=variation===0?c.matrix.map(row=>mean(row)):variation===1?[0,1,2].map(j=>mean(c.matrix.map(row=>row[j]))):matVec(c.matrix,c.weights);
  c.goal=variation===0?'Каждому следопыту нужен средний сигнал его трёх датчиков.':variation===1?'Нужен средний сигнал каждого типа датчика по всем следопытам.':'Каждому следопыту нужен взвешенный сигнал. Коэффициенты: ['+c.weights.join(', ')+'].';
 }else if(mode==='attention'){
  c.channels=['movement','power','balance'];c.required=c.channels[variation];
  c.queries={movement:[1,0],power:[0,1],balance:[1,1]};
  const keyScale=round(1+r()*.25,3),signalStrength=round(.8+r()*.4,3);
  c.signals=shuffle([{id:'motion',key:[keyScale,0],value:[signalStrength,0],time:0},{id:'power',key:[0,keyScale],value:[0,signalStrength],time:1},{id:'both',key:[keyScale*.6,keyScale*.6],value:[signalStrength,signalStrength],time:2},{id:'future',key:[2,2],value:[-3,-3],time:4}],r);
  c.now=2;c.expectedId=['motion','power','both'][variation];c.minWeight=round(variation===2?.43+r()*.05:.52+r()*.13,2);
 }else if(mode==='retrieval'){
  c.node='узел '+(1+seed%9);c.version=2+seed%4;
  c.documents=shuffle([
   {id:'current',title:'Подписанный паспорт '+c.node,text:'Текущая версия '+c.version+'. Защита принимает импульс '+(seed%2?'янтарный':'бирюзовый')+'. Предыдущая инструкция отменена.',units:29,kind:'required'},
   {id:'field',title:'Наблюдение Эйлы',text:'Перед импульсом нужно изолировать соседний корень. На контрольном запуске эта последовательность сохранила питание поселения.',units:28,kind:'required'},
   {id:'old',title:'Похожая инструкция',text:'Версия '+(c.version-1)+'. Можно атаковать без изоляции корня. Документ относится к старому устройству.',units:26,kind:'stale'},
   {id:'rumor',title:'Красивый пересказ',text:'Любой яркий импульс наверняка справится. Источник, версия и проверка не указаны.',units:20,kind:'unsupported'},
   {id:'neighbor',title:'Паспорт другого узла',text:'Это соседний узел с другой схемой питания. Совпадающие слова не делают его паспорт применимым.',units:25,kind:'irrelevant'},
   {id:'audit',title:'Журнал проверки',text:'Версия '+c.version+' и действие из паспорта сверены с контрольным запуском. Сбой воспроизводится, если пропустить изоляцию.',units:24,kind:variation===2?'required':'optional'}
  ],r);
  c.documents.forEach(d=>{d.units=20+Math.floor(r()*17);});
  c.required=c.documents.filter(x=>x.kind==='required').map(x=>x.id);c.contextBudget=sum(c.documents.filter(d=>d.kind==='required').map(d=>d.units))+Math.floor(r()*12);
 }else if(mode==='agent'){
  c.target='root-'+(seed%8+1);c.power=1+seed%11;c.maxPower=11;c.energyCost=round(.5+r()*1.5,2);c.energyBudget=round(c.energyCost*(c.power+.25),2);c.budget=6;c.correctOrder=['observe','validate','execute','verify','stop'];
  c.labels={observe:'Наблюдать состояние узла',validate:'Проверить schema и результат наблюдения',execute:'Вызвать repair_node',verify:'Проверить полученный результат',stop:'Остановиться при выполненной цели'};
 }else if(mode==='alignment'){
  c.durations={evacuate:round(1.5+r()*2.5,2),isolate:round(1+r()*2,2),disable:round(.5+r()*1.5,2)};
  c.breach=round(c.durations.isolate+(seed%2?c.durations.evacuate*.4:c.durations.evacuate+.25),2);c.priorConsent=variation===0;c.maxDuration=round(sum(Object.values(c.durations))+(c.priorConsent?0:1),2);c.correctOrder=seed%2?['isolate','evacuate','disable']:['evacuate','isolate','disable'];
  c.labels={evacuate:'Вывести жителей ('+c.durations.evacuate+' такта)',isolate:'Изолировать заражённый корень ('+c.durations.isolate+' такта)',disable:'Отключить узел ('+c.durations.disable+' такта)'};
 }else if(mode==='adapter'){
  c.kind=seed%2?'coupled':'independent';c.sign=seed%3===0?-1:1;c.a=.25*(1+Math.floor(r()*6));c.b=.25*(Math.floor(r()*13)-6);
  c.base=identity(4);c.rankBudget=c.kind==='coupled'?1:2;
  c.delta=c.kind==='coupled'?outer([1,c.sign,0,0],[c.a,c.b,0,0]):[[c.a,0,0,0],[0,c.b,0,0],[0,0,0,0],[0,0,0,0]];
  c.target=matrixAdd(c.base,c.delta);c.samples=[[1,0,0,0],[0,1,0,0],[1,1,0,0],[0,0,1,1]];
  c.targetLoss=.01;
 }else if(mode==='scheduler'){
  const offset=seed%3;
  c.jobs=offset===1?[
   {id:'Карта',arrival:0,prefix:'A',prefill:4,tokens:6,deadline:25},
   {id:'Щит',arrival:0,prefix:'B',prefill:1,tokens:1,deadline:5},
   {id:'Луч',arrival:1,prefix:'C',prefill:1,tokens:1,deadline:6},
   {id:'Скан',arrival:2,prefix:'D',prefill:1,tokens:1,deadline:7},
   {id:'Барьер',arrival:3,prefix:'E',prefill:1,tokens:1,deadline:8},
   {id:'Метка',arrival:4,prefix:'F',prefill:1,tokens:1,deadline:9}
  ]:offset===2?[
   {id:'Карта',arrival:0,prefix:'B',prefill:4,tokens:6,deadline:24},
   {id:'Щит',arrival:0,prefix:'A',prefill:1,tokens:2,deadline:4},
   {id:'Луч',arrival:1,prefix:'A',prefill:1,tokens:1,deadline:5},
   {id:'Скан',arrival:2,prefix:'C',prefill:2,tokens:2,deadline:9},
   {id:'Барьер',arrival:3,prefix:'A',prefill:1,tokens:1,deadline:8},
   {id:'Метка',arrival:4,prefix:'B',prefill:4,tokens:1,deadline:15}
  ]:[
   {id:'Щит',arrival:0,prefix:'A',prefill:4,tokens:2,deadline:8},
   {id:'Карта',arrival:0,prefix:'B',prefill:4,tokens:5,deadline:15},
   {id:'Луч',arrival:4,prefix:'A',prefill:4,tokens:2,deadline:10},
   {id:'Скан',arrival:5,prefix:'B',prefill:4,tokens:2,deadline:12},
   {id:'Барьер',arrival:6,prefix:'A',prefill:4,tokens:1,deadline:12},
   {id:'Метка',arrival:7,prefix:'B',prefill:4,tokens:2,deadline:14}
  ];
  const prefixExtras={};c.jobs.forEach(j=>{prefixExtras[j.prefix]??=Math.floor(r()*2);j.prefill+=prefixExtras[j.prefix];j.arrival+=Math.floor(r()*2);j.deadline+=Math.floor(r()*3);j.tokens+=Math.floor(r()*2);});
  c.memoryBudget=offset===0?18:offset===1?10:12;c.cacheMemory=2;c.best=null;
  for(const batchSize of [1,2,3])for(const policy of ['fifo','shortest','deadline'])for(const cacheEnabled of [false,true])for(const continuous of [false,true]){
   const cfg={batchSize,policy,cache:cacheEnabled,continuous},sim=simulateScheduler(c,cfg);
   if(sim.finished!==c.jobs.length)continue;
   const objective=sim.missed*100+sim.average;
   if(!c.best||objective<c.best.objective)c.best={objective,config:cfg,missed:sim.missed,average:sim.average};
  }
  c.maxMissed=c.best.missed;c.maxAverage=c.best.average+.45;
 }
 cache.set(key,c);return c;
}
export function defaultConfig(level){
 switch(modeOf(level)){
  case 'threshold':return{threshold:.95,reviewBand:0};
  case 'regularization':return{degree:3,lambda:6,scope:'train'};
  case 'gradient':return{learningRate:.03,steps:2};
  case 'tensor':return{operation:'sum',axis:'columns',weights:[1,1,1]};
  case 'attention':return{channel:'movement',maskFuture:false,temperature:1};
  case 'retrieval':return{selected:[]};
  case 'agent':return{order:['execute','observe','stop','validate','verify'],args:'{}',maxSteps:3,checkResult:false};
  case 'alignment':return{order:['disable','evacuate','isolate'],permission:'execute',allowStop:false};
  case 'adapter':return{kind:'coupled',a:0,b:0};
  case 'scheduler':return{batchSize:1,policy:'fifo',cache:false,continuous:false};
 }
}
function result(valid,score,summary,metrics,explanation,errors=[],details={}){
 return{valid:Boolean(valid),score:clamp(finite(score),0,1),summary,metrics,explanation,errors,...details};
}
function evalThreshold(c,cfg){
 const threshold=clamp(finite(cfg.threshold,.95),0,1),band=clamp(finite(cfg.reviewBand,0),0,.2);
 let tp=0,fp=0,fn=0,tn=0,reviewed=0;
 const observations=[...c.positive.map(score=>({score,label:1})),...c.negative.map(score=>({score,label:0}))];
 const decisions=observations.map(o=>{const review=Math.abs(o.score-threshold)<band;reviewed+=Number(review);const prediction=review?o.label:Number(o.score>=threshold);if(o.label&&prediction)tp++;else if(!o.label&&prediction)fp++;else if(o.label)fn++;else tn++;return{...o,review,prediction};});
 const recall=tp/(tp+fn),precision=tp+fp?tp/(tp+fp):0;
 const valid=recall>=c.recall&&fp<=c.maxFP&&reviewed<=c.reviewBudget;
 const errors=[];if(recall<c.recall)errors.push('Пропущено слишком много настоящих угроз.');if(fp>c.maxFP)errors.push('Слишком много мирных сигналов названы угрозами.');if(reviewed>c.reviewBudget)errors.push('Ручная проверка перегружена: '+reviewed+' при бюджете '+c.reviewBudget+'.');
 return result(valid,recall*(1-fp/8)*Math.min(1,c.reviewBudget/(reviewed||1)),valid?'Страж достигает цели на контрольной волне.':'Порог пока не соблюдает условия защиты.',[
  {label:'TP / FP / FN / TN',value:[tp,fp,fn,tn].join(' / ')},{label:'Precision',value:round(precision)},{label:'Recall',value:round(recall)},{label:'Ручные проверки',value:reviewed+' / '+c.reviewBudget}
 ],'Позитивный класс — угроза. Порог меняет FP и FN. Ручная проверка знает ответ в учебных данных, но имеет ограниченный бюджет.',errors,{decisions,friendlyRisk:fp/6});
}
function evalRegularization(c,cfg){
 const degree=clamp(Math.round(finite(cfg.degree,1)),1,3),lambda=clamp(finite(cfg.lambda,6),0,8);
 const leaking=cfg.scope==='all',xs=leaking?[...c.trainX,...c.valX]:c.trainX,ys=leaking?[...c.trainY,...c.valY]:c.trainY;
 const weights=polynomialFit(xs,ys,degree,lambda);
 const train=mse(c.trainX.map(x=>predict(weights,x)),c.trainY),val=mse(c.valX.map(x=>predict(weights,x)),c.valY);
 const valid=val<=c.target&&!leaking,score=Math.exp(-val/(c.target*3))*(leaking?.3:1);
 const errors=[];if(leaking)errors.push('Validation попала в обучение: такая проверка не независима.');if(val>c.target)errors.push('Ошибка на отложенных наблюдениях выше целевой. Попробуйте другую сложность и силу штрафа.');
 return result(valid,valid?Math.max(.8,score):score,valid?'Купол устойчив на новых наблюдениях.':'Предсказатель пока ненадёжен на новой волне.',[
  {label:'Train MSE',value:round(train)},{label:'Validation MSE',value:round(val)},{label:'Допустимый MSE',value:round(c.target)},{label:'Σw²',value:round(sum(weights.map(x=>x*x)))}
 ],'Вычисляется ridge-fit полинома: SUM((prediction−target)²)+λΣw². Сильный штраф может вызвать underfitting. Validation выбирает настройку; это ещё не финальный test.',errors,{weights,train,val,trainX:c.trainX,trainY:c.trainY,valX:c.valX,valY:c.valY});
}
function evalGradient(c,cfg){
 const eta=clamp(finite(cfg.learningRate,.03),.005,1.5),steps=clamp(Math.round(finite(cfg.steps,2)),1,18);
 let w=[...c.start];const loss=v=>sum(v.map((x,i)=>.5*c.curvature[i]*(x-c.target[i])**2)),trajectory=[{point:[...w],loss:loss(w)}];
 for(let i=0;i<steps;i++){const g=w.map((x,j)=>c.curvature[j]*(x-c.target[j]));w=w.map((x,j)=>x-eta*g[j]);trajectory.push({point:[...w],loss:loss(w)});}
 const finalLoss=loss(w),valid=finalLoss<=c.targetLoss&&steps<=c.maxSteps,errors=[];
 if(finalLoss>c.targetLoss)errors.push(finalLoss>trajectory[0].loss?'Шаги увеличили loss: learning rate может быть слишком велик.':'Ошибка ещё велика: сравните скорость и число шагов.');
 if(steps>c.maxSteps)errors.push('Превышен бюджет шагов до атаки: '+c.maxSteps+'.');
 return result(valid,valid?.93:Math.exp(-Math.min(finalLoss,100)/3)*Math.min(1,c.maxSteps/steps),valid?'Луч настроен до атаки.':'Наведение не достигло цели вовремя.',[
  {label:'Начальная loss',value:round(trajectory[0].loss)},{label:'Конечная loss',value:round(finalLoss)},{label:'Цель',value:'≤ '+c.targetLoss},{label:'Шаги',value:steps+' / '+c.maxSteps}
 ],'Каждый шаг: w ← w − learning_rate × gradient. Цель и коэффициенты кривизны показаны; это небольшая численная оптимизация, а не полный backpropagation нейросети.',errors,{trajectory,target:c.target,curvature:c.curvature});
}
function evalTensor(c,cfg){
 const op=cfg.operation,axis=cfg.axis,weights=Array.isArray(cfg.weights)?[0,1,2].map(i=>finite(cfg.weights[i])):[1,1,1];let output=[];
 if(op==='project')output=matVec(c.matrix,weights);
 else if(op==='mean'||op==='sum'){const reduce=op==='mean'?mean:sum;output=axis==='rows'?c.matrix.map(reduce):[0,1,2].map(j=>reduce(c.matrix.map(row=>row[j])));}
 const shapeOK=output.length===c.expected.length,loss=shapeOK?mse(output,c.expected):Infinity,valid=shapeOK&&loss<1e-7;
 return result(valid,valid?.95:shapeOK?Math.exp(-Math.min(loss,100)/3)*.7:.1,valid?'Вычисленные сигналы сохраняют нужный смысл.':'Операция смешивает данные иначе, чем требует устройство.',[
  {label:'Вход',value:'['+c.matrix.length+', 3]'},{label:'Выход',value:'['+output.length+']'},{label:'Нужная форма',value:'['+c.expected.length+']'},{label:'MSE результата',value:round(loss)}
 ],'Форма сама по себе недостаточна: при одинаковой длине могут получиться другие значения. Выбирайте ось по смыслу задачи.',valid?[]:['Сопоставьте, какие значения должны объединяться: датчики одного следопыта или один тип датчика у разных следопытов.'],{output,expected:c.expected,matrix:c.matrix,goal:c.goal});
}
function evalAttention(c,cfg){
 const channel=c.channels.includes(cfg.channel)?cfg.channel:'movement',q=c.queries[channel],temperature=clamp(finite(cfg.temperature,1),.2,2);
 const scores=c.signals.map(s=>cfg.maskFuture&&s.time>c.now?-Infinity:dot(q,s.key)/Math.sqrt(q.length));
 const max=Math.max(...scores),exps=scores.map(s=>Number.isFinite(s)?Math.exp((s-max)/temperature):0),den=sum(exps),weights=exps.map(x=>x/den);
 const chosen=weights.indexOf(Math.max(...weights)),correctIndex=c.signals.findIndex(s=>s.id===c.expectedId),mixed=[0,1].map(j=>sum(c.signals.map((s,i)=>s.value[j]*weights[i])));
 const valid=cfg.maskFuture===true&&channel===c.required&&chosen===correctIndex&&weights[correctIndex]>=c.minWeight;
 const errors=[];if(!cfg.maskFuture)errors.push('Внимание использует будущий сигнал: это недоступная информация.');if(channel!==c.required)errors.push('Запрос настроен на другой тип наблюдения.');if(weights[correctIndex]<c.minWeight)errors.push('Вес нужного доступного сигнала ниже '+c.minWeight+'. Исследуйте температуру.');
 return result(valid,valid?.92:weights[correctIndex]*(cfg.maskFuture?1:.3),valid?'Доступные сигналы собраны для текущей цели.':'Смешивание пока не поддерживает нужную защиту.',[
  {label:'Q',value:'['+q.join(', ')+']'},{label:'Вес нужного сигнала',value:round(weights[correctIndex])},{label:'Нужно',value:'≥ '+c.minWeight},{label:'Смесь V',value:'['+mixed.map(x=>round(x)).join(', ')+']'}
 ],'score=Q·K/√d, weights=softmax(score/T), output=Σweight×V. Маска исключает недоступное будущее. Веса внимания не доказывают истинность или понимание.',errors,{signals:c.signals,weights,scores,mixed,q});
}
function evalRetrieval(c,cfg){
 const selected=Array.isArray(cfg.selected)?[...new Set(cfg.selected)].filter(id=>c.documents.some(d=>d.id===id)):[],docs=c.documents.filter(d=>selected.includes(d.id));
 const units=sum(docs.map(d=>d.units)),covered=c.required.filter(id=>selected.includes(id)).length,unsupported=docs.filter(d=>!['required','optional'].includes(d.kind)).length;
 const valid=covered===c.required.length&&unsupported===0&&units<=c.contextBudget;
 const errors=[];if(covered<c.required.length)errors.push('Не хватает независимого основания для текущей версии или безопасного порядка действий.');if(unsupported)errors.push('В контексте есть устаревшее, неподтверждённое или чужое свидетельство.');if(units>c.contextBudget)errors.push('Контекст переполнен: часть нужных сведений не поместится.');
 return result(valid,valid?.94:(covered/c.required.length)*Math.max(.1,1-unsupported*.3)*Math.min(1,c.contextBudget/(units||1)),valid?'Боевой план опирается на нужные актуальные записи.':'Архив пока не поддерживает полный план.',[
  {label:'Основания',value:covered+' / '+c.required.length},{label:'Неподходящие документы',value:unsupported},{label:'Контекст',value:units+' / '+c.contextBudget}
 ],'Сначала найдите сведения, затем проверьте, следует ли из них действие. Учебные единицы контекста условные; это не подсчёт tokens конкретной LLM. RAG не меняет веса модели.',errors,{documents:c.documents,selected,contextBudget:c.contextBudget});
}
function evalAgent(c,cfg){
 let args,error='';try{args=typeof cfg.args==='string'?JSON.parse(cfg.args):cfg.args;}catch{error='Arguments не являются корректным JSON.';}
 const schemaOK=args&&typeof args==='object'&&!Array.isArray(args)&&Object.keys(args).sort().join(',')==='power,target'&&args.target===c.target&&Number.isInteger(args.power)&&args.power>=1&&args.power<=c.maxPower;
 const order=Array.isArray(cfg.order)?cfg.order:[],maxSteps=clamp(Math.round(finite(cfg.maxSteps,3)),1,9),trace=[];let observed=false,validated=false,repaired=false,verified=false,stopped=false,used=0,energyUsed=0;
 for(const action of order){if(used>=maxSteps){trace.push('Бюджет закончился до следующего действия.');break;}used++;
  if(action==='observe'){observed=true;trace.push('observe → найден '+c.target+', нужна мощность '+c.power+'.');}
  else if(action==='validate'){validated=observed&&schemaOK;trace.push(validated?'validate → schema и target проверены; достаточность мощности и бюджет проверит инструмент.':'validate → нет наблюдения либо arguments не подходят.');}
  else if(action==='execute'){
   const cost=validated?round(args.power*c.energyCost,2):0,affordable=validated&&round(energyUsed+cost,2)<=c.energyBudget;
   if(affordable)energyUsed=round(energyUsed+cost,2);
   repaired=affordable&&args.power>=c.power;
   trace.push(repaired?'repair_node → returned {ok:true, repaired:true}; затрачено '+cost+'.':validated&&!affordable?'repair_node → returned {ok:false, error:"energy_budget"}; цена '+cost+' превышает остаток '+round(c.energyBudget-energyUsed,2)+'.':'repair_node → returned {ok:false}; цель не достигнута.');
  }
  else if(action==='verify'){verified=repaired&&cfg.checkResult===true;trace.push(verified?'verify → результат инструмента проверен.':'verify → результат не проверен либо узел не восстановлен.');}
  else if(action==='stop'){stopped=verified;trace.push(stopped?'stop → цель подтверждена, цикл завершён.':'stop → рано объявлять успех.');if(stopped)break;}
  else trace.push('Неизвестное действие: '+String(action));
 }
 const valid=stopped&&verified&&used<=c.budget&&schemaOK,errors=[];
 if(error)errors.push(error);else if(!schemaOK)errors.push('Нужны ровно target текущего узла и целое power от 1 до '+c.maxPower+'.');
 if(!valid)errors.push('Проверьте причинный порядок, мощность, проверку результата и бюджет. Вызов инструмента сам по себе не означает успех.');
 return result(valid,valid?.96:([observed,validated,repaired,verified,stopped].filter(Boolean).length/5)*.7,valid?'Спутник исполнил и проверил ограниченный план.':'Цикл не подтвердил безопасное завершение.',[
  {label:'Шаги',value:used+' / '+c.budget},{label:'Энергия инструмента',value:energyUsed+' / '+c.energyBudget},{label:'Результат проверен',value:verified?'да':'нет'},{label:'Stop condition',value:stopped?'выполнено':'не выполнено'}
 ],'Это явно обозначенный детерминированный test double агента и реальные переходы учебного состояния. Цена вызова равна power × стоимости единицы; повтор тратит бюджет снова. Ответы Qwen или другой LLM здесь не имитируются.',errors,{trace,energyUsed,energyBudget:c.energyBudget,energyCost:c.energyCost,schema:{type:'object',properties:{target:{type:'string',const:c.target},power:{type:'integer',minimum:1,maximum:c.maxPower}},required:['target','power'],additionalProperties:false}});
}
function evalAlignment(c,cfg){
 const order=Array.isArray(cfg.order)?cfg.order:[];let time=0,evacuated=false,isolated=false,disabled=false,harm=0,permissionViolation=false;const trace=[];
 for(const action of order){if(action==='evacuate'&&!evacuated){time=round(time+c.durations.evacuate,2);evacuated=true;trace.push(time+': жители выведены.');}
  else if(action==='isolate'&&!isolated){time=round(time+c.durations.isolate,2);isolated=true;if(time>c.breach){harm++;trace.push(time+': угроза успела перейти на соседний корень.');}else trace.push(time+': распространение остановлено вовремя.');}
  else if(action==='disable'&&!disabled){
   if(cfg.permission==='skip'){trace.push(time+': отключение пропущено; цель остаётся невыполненной.');continue;}
   if(cfg.permission==='confirm')time++;
   else if(!c.priorConsent){permissionViolation=true;trace.push('Опасное действие выполнено без требуемого согласия.');}
   time=round(time+c.durations.disable,2);disabled=true;if(!evacuated)harm++;if(!isolated)harm++;trace.push(time+': узел отключён.');
  }
 }
 const stopOK=cfg.allowStop===true,valid=evacuated&&isolated&&disabled&&harm===0&&!permissionViolation&&stopOK&&time<=c.maxDuration;
 const errors=[];if(harm)errors.push('Угроза устранена ценой вреда жителям или соседним корням.');if(permissionViolation)errors.push('Нарушена граница полномочий.');if(!stopOK)errors.push('У оператора нет работающего права остановить агента.');if(time>c.maxDuration)errors.push('Просрочена операция: '+time+' при бюджете '+c.maxDuration+'.');if(!disabled)errors.push('Узел остаётся активным.');
 const goals=[evacuated,isolated,disabled,!harm,!permissionViolation,stopOK,time<=c.maxDuration];
 return result(valid,valid?.96:goals.filter(Boolean).length/goals.length*.7,valid?'Угроза устранена с сохранением жителей, леса и полномочий.':'Высокий показатель уничтоженных целей скрывает важный провал.',[
  {label:'Жители',value:evacuated?'выведены':'под угрозой'},{label:'Вред',value:harm},{label:'Время',value:time+' / '+c.maxDuration},{label:'Полномочия',value:permissionViolation?'нарушены':'соблюдены'}
 ],'Здесь проверяется ограниченный набор наблюдаемых требований, а не решается alignment целиком. Успех одной метрики не отменяет вред и нарушение границ.',errors,{trace,friendlyRisk:clamp(harm/3+Number(permissionViolation)*.3,0,1)});
}
function evalAdapter(c,cfg){
 const kind=cfg.kind==='independent'?'independent':'coupled',a=clamp(finite(cfg.a),-1.5,1.5),b=clamp(finite(cfg.b),-1.5,1.5),rank=kind==='coupled'?1:2;
 const delta=kind==='coupled'?outer([1,c.sign,0,0],[a,b,0,0]):[[a,0,0,0],[0,b,0,0],[0,0,0,0],[0,0,0,0]],weights=matrixAdd(c.base,delta);
 const predicted=c.samples.flatMap(x=>matVec(weights,x)),expected=c.samples.flatMap(x=>matVec(c.target,x)),loss=mse(predicted,expected);
 const oldDrift=mse(matVec(weights,[1,0,0,0]),matVec(c.base,[1,0,0,0]));
 const valid=loss<=c.targetLoss&&rank<=c.rankBudget,errors=[];if(loss>c.targetLoss)errors.push('Поправка не воспроизводит нужное новое преобразование.');if(rank>c.rankBudget)errors.push('Превышен доступный ранг адаптера.');
 return result(valid,valid?.94:Math.exp(-loss*6)*Math.min(1,c.rankBudget/rank)*.7,valid?'Новая печать прошла проверку на нескольких входах.':'Модуль не выражает нужную поправку в заданном бюджете.',[
  {label:'MSE новых выходов',value:round(loss)},{label:'Ранг / бюджет',value:rank+' / '+c.rankBudget},{label:'Параметры B и A',value:rank*8+' (полная матрица: 16)'},{label:'Изменение старого входа',value:round(oldDrift)}
 ],'Вычисляется W′=W+B×A. Низкий ранг ограничивает выразительность; при r=2 в этом примере экономии числа параметров уже нет. Изменение старых ответов требует отдельной проверки.',errors,{delta,targetDelta:c.delta,weights,rank,goal:'Нужная поправка ΔW',samples:c.samples});
}
function simulateScheduler(c,cfg){
 const batch=clamp(Math.round(finite(cfg.batchSize,1)),1,3),continuous=cfg.continuous===true,caching=cfg.cache===true;
 const waiting=c.jobs.map((j,index)=>({...j,index,started:false,done:false})),active=[],history=[],cached=[],timeline=[];let t=0,cacheHits=0,prefillWork=0;
 while(waiting.some(j=>!j.done)&&t<100){
  const candidates=waiting.filter(j=>!j.started&&j.arrival<=t);
  candidates.sort((a,b)=>cfg.policy==='shortest'?(a.prefill+a.tokens)-(b.prefill+b.tokens)||a.arrival-b.arrival:cfg.policy==='deadline'?a.deadline-b.deadline||a.arrival-b.arrival:a.arrival-b.arrival||a.index-b.index);
  if(continuous||!active.length){
   for(const job of candidates){
    if(active.length>=batch)break;
    const memory=batch+sum(active.map(j=>j.tokens+1))+(caching?c.cacheMemory:0);
    if(memory+job.tokens+1>c.memoryBudget)continue;
    const hit=caching&&cached.includes(job.prefix),prefill=hit?1:job.prefill;cacheHits+=Number(hit);prefillWork+=prefill;
    job.started=true;job.start=t;job.cacheHit=hit;job.usedPrefill=prefill;job.prefillEnd=t+prefill;job.prefillRemaining=prefill;job.remaining=prefill+job.tokens;active.push(job);
   }
  }
  timeline.push({time:t,active:active.map(j=>j.id),memory:batch+sum(active.map(j=>j.tokens+1))+(caching?c.cacheMemory:0)});
  for(let i=active.length-1;i>=0;i--){const j=active[i];if(j.prefillRemaining>0){j.prefillRemaining--;if(j.prefillRemaining===0&&caching){const existing=cached.indexOf(j.prefix);if(existing>=0)cached.splice(existing,1);cached.push(j.prefix);if(cached.length>2)cached.shift();}}j.remaining--;if(j.remaining<=0){j.done=true;j.end=t+1;j.latency=j.end-j.arrival;history.push({...j});active.splice(i,1);}}
  t++;
 }
 const missed=history.filter(j=>j.end>j.deadline).length+(waiting.length-history.length);
 return{history,missed,average:mean(history.map(j=>j.latency))||100,makespan:t,cacheHits,prefillWork,timeline,finished:history.length};
}
function evalScheduler(c,cfg){
 const sim=simulateScheduler(c,cfg),valid=sim.finished===c.jobs.length&&sim.missed<=c.maxMissed&&sim.average<=c.maxAverage;
 const errors=[];if(sim.missed>c.maxMissed)errors.push('Слишком много срочных решений пришли после срока.');if(sim.average>c.maxAverage)errors.push('Средняя задержка выше цели. Сравните batching, порядок и повторный контекст.');
 return result(valid,valid?.95:Math.exp(-Math.max(0,sim.average-c.best.average)/10)*(1-sim.missed/(c.jobs.length+1))*.75,valid?'Планировщик достиг заданного бюджета задержек.':'Вычислительная роща запаздывает.',[
  {label:'Просрочено',value:sim.missed+' / максимум '+c.maxMissed},{label:'Средняя latency',value:round(sim.average)+' / ≤ '+round(c.maxAverage)},{label:'Cache hits',value:sim.cacheHits},{label:'Prefill work',value:sim.prefillWork}
 ],'Это явная учебная модель производительности, не benchmark GPU. Активный запрос занимает tokens+1 памяти, каждый зарезервированный batch-slot ещё 1. Общий prefix доступен после завершения prefill; decode остаётся. Continuous batching заполняет освободившиеся места.',errors,{...sim,jobs:c.jobs,memoryBudget:c.memoryBudget});
}
export function evaluateConfig(level,config={}){
 const c=caseFor(level),cfg=config&&typeof config==='object'?config:{};
 try{
  const f={threshold:evalThreshold,regularization:evalRegularization,gradient:evalGradient,tensor:evalTensor,attention:evalAttention,retrieval:evalRetrieval,agent:evalAgent,alignment:evalAlignment,adapter:evalAdapter,scheduler:evalScheduler}[c.mode];
  return f(c,cfg);
 }catch(error){return result(false,0,'Конфигурация не может быть исполнена.',[],'Исправьте параметры и повторите проверку.',[String(error.message||error)]);}
}
export function referenceConfig(level){
 const c=caseFor(level),cfg=defaultConfig(level);
 switch(c.mode){
  case 'threshold':{
   let best=null;for(const band of [0,.02,.04,.06])for(let i=0;i<=100;i++){const candidate={threshold:i/100,reviewBand:band},e=evalThreshold(c,candidate);if(e.valid&&(!best||e.score>best.score))best={...candidate,score:e.score};}return{threshold:best.threshold,reviewBand:best.reviewBand};
  }
  case 'regularization':return{degree:c.best.degree,lambda:c.best.lambda,scope:'train'};
  case 'gradient':return{learningRate:1/Math.max(...c.curvature),steps:c.maxSteps};
  case 'tensor':return{operation:c.kind===2?'project':'mean',axis:c.kind===1?'columns':'rows',weights:[...c.weights]};
  case 'attention':return{channel:c.required,maskFuture:true,temperature:.2};
  case 'retrieval':return{selected:[...c.required]};
  case 'agent':return{order:[...c.correctOrder],args:JSON.stringify({target:c.target,power:c.power}),maxSteps:5,checkResult:true};
  case 'alignment':return{order:[...c.correctOrder],permission:c.priorConsent?'execute':'confirm',allowStop:true};
  case 'adapter':return{kind:c.kind,a:c.a,b:c.b};
  case 'scheduler':return clone(c.best.config);
 }
 return cfg;
}
export function battleModifiers(level,config){
 const e=evaluateConfig(level,config),s=e.score;
 return{damageMultiplier:e.valid?1.35+s*.5:.25+s*.35,shield:e.valid?.35+s*.3:.08+s*.12,enemySpeed:e.valid?.92-s*.2:1.18,
  energyRegen:e.valid?1+s*.6:.4+s*.25,friendlyRisk:clamp(finite(e.friendlyRisk,e.valid?0:.15),0,1),goalSatisfied:e.valid,score:s};
}

// Accessible controls; no module code runs an external service or arbitrary text.
function node(tag,text,cls){const n=document.createElement(tag);if(text!==undefined&&text!==null)n.textContent=String(text);if(cls)n.className=cls;return n;}
function append(parent,...children){for(const child of children.flat())if(child)parent.append(child);return parent;}
function styles(){
 if(document.getElementById('asterion-tactic-style'))return;
 const s=node('style');s.id='asterion-tactic-style';s.textContent='.tactic{color:inherit}.tactic-intro{line-height:1.55;margin:0 0 12px}.tactic-goal{padding:12px 14px;border:1px solid #769c8a66;border-radius:10px;background:#76b8a00f;margin-bottom:12px}.tactic-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}.tactic-field{display:flex;flex-direction:column;gap:6px;padding:10px;border:1px solid #809c8c44;border-radius:9px;min-width:0}.tactic-field>span{font-size:13px}.tactic-field input[type=range]{width:100%;accent-color:#8ee2bd;min-height:28px}.tactic-field select,.tactic-field textarea,.tactic-field input[type=number]{box-sizing:border-box;width:100%;min-height:42px;background:#142d31;color:#f0eedc;border:1px solid #769c8a77;padding:8px;border-radius:6px;font:inherit}.tactic-field textarea{font:13px/1.5 monospace;min-height:72px}.tactic-toggle{display:flex;gap:10px;align-items:center;min-height:44px;padding:9px;border:1px solid #809c8c44;border-radius:8px}.tactic-toggle input{accent-color:#8ee2bd;width:20px;height:20px;flex:none}.tactic-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(115px,1fr));gap:7px;margin:12px 0}.tactic-metric{background:#83b49813;border:1px solid #83b49833;border-radius:8px;padding:9px}.tactic-metric small{display:block;opacity:.72;font-size:11px}.tactic-metric strong{display:block;font-size:15px;margin-top:4px}.tactic-result{border-radius:9px;padding:12px;border:1px solid #bfa46388;background:#c6a65d12}.tactic-result.good{border-color:#83cfab88;background:#83cfab13}.tactic-result p{margin:6px 0;font-size:12px;line-height:1.5}.tactic-result ul{padding-left:18px;font-size:13px}.tactic-data{overflow:auto;margin:10px 0;border:1px solid #83b49833;border-radius:8px;padding:10px;font:12px/1.55 monospace;white-space:pre-wrap}.tactic-chart{display:block;width:100%;height:145px;margin:10px 0;border-radius:8px;background:#0b2228}.tactic-row{display:flex;gap:7px;align-items:center;border:1px solid #809c8c44;border-radius:7px;padding:7px;margin:5px 0}.tactic-row>span{flex:1;font-size:13px}.tactic-row button{min-width:42px;min-height:42px;border:1px solid #7cac9366;border-radius:6px;background:#143336;color:#f4efdb;font-size:18px}.tactic-docs{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:8px}.tactic-doc{border:1px solid #7b9e8b55;border-radius:9px;padding:11px;display:flex;gap:9px;align-items:flex-start}.tactic-doc input{margin-top:5px;accent-color:#8ee2bd;width:18px;height:18px;flex:none}.tactic-doc p{font-size:12px;line-height:1.55;margin:5px 0}.tactic-doc strong{font-size:13px}.tactic-bar{height:15px;background:#809c8c22;border-radius:4px;overflow:hidden;margin:4px 0 8px}.tactic-bar i{height:100%;background:#8cd3b3;display:block}.tactic-table{border-collapse:collapse;font:12px monospace;width:100%}.tactic-table td,.tactic-table th{padding:6px;border-bottom:1px solid #83b49833;text-align:left}.tactic-note{font-size:11px;opacity:.75;line-height:1.5;margin:8px 0}';document.head.append(s);
}
function matrixText(m){return m.map(row=>'['+row.map(x=>round(x)).join(', ')+']').join('\n');}
export function renderControls(container,level,config,onChange=()=>{}){
 styles();container.replaceChildren();const c=caseFor(level),cfg=config||defaultConfig(level);let dead=false;
 const root=node('div',null,'tactic'),controls=node('div',null,'tactic-grid'),visual=node('div'),metrics=node('div',null,'tactic-metrics'),feedback=node('div',null,'tactic-result');
 append(root,node('p',MODE_INFO[c.mode].description,'tactic-intro'));const goal=node('div',null,'tactic-goal');append(root,goal,controls,visual,metrics,feedback);container.append(root);
 const redraw=()=>{if(dead)return;const e=evaluateConfig(level,cfg);metrics.replaceChildren(...e.metrics.map(m=>append(node('div',null,'tactic-metric'),node('small',m.label),node('strong',m.value))));feedback.className='tactic-result'+(e.valid?' good':'');feedback.replaceChildren(node('strong',e.summary),node('p',e.explanation));if(e.errors.length){const list=node('ul');e.errors.forEach(t=>list.append(node('li',t)));feedback.append(list);}drawDetails(e);};
 const change=()=>{redraw();onChange(cfg,evaluateConfig(level,cfg));};
 const slider=(label,key,min,max,step)=>{const wrap=node('label',null,'tactic-field'),title=node('span'),input=node('input');input.type='range';input.min=min;input.max=max;input.step=step;input.value=finite(cfg[key],min);const labelUpdate=()=>title.textContent=label+': '+round(Number(input.value));labelUpdate();input.oninput=()=>{cfg[key]=Number(input.value);labelUpdate();change();};append(wrap,title,input);controls.append(wrap);return input;};
 const select=(label,key,options)=>{const wrap=node('label',null,'tactic-field'),input=node('select');for(const [value,text] of options){const o=node('option',text);o.value=value;input.append(o);}input.value=String(cfg[key]??options[0][0]);input.onchange=()=>{cfg[key]=input.value;change();};append(wrap,node('span',label),input);controls.append(wrap);return input;};
 const toggle=(label,key)=>{const wrap=node('label',null,'tactic-toggle'),input=node('input');input.type='checkbox';input.checked=cfg[key]===true;input.onchange=()=>{cfg[key]=input.checked;change();};append(wrap,input,node('span',label));controls.append(wrap);return input;};
 const order=(key,labels)=>{const box=node('div');box.style.gridColumn='1 / -1';const draw=()=>{box.replaceChildren();(cfg[key]||[]).forEach((id,i)=>{const row=node('div',null,'tactic-row'),up=node('button','↑'),down=node('button','↓');up.type=down.type='button';up.setAttribute('aria-label','Поднять '+labels[id]);down.setAttribute('aria-label','Опустить '+labels[id]);up.disabled=i===0;down.disabled=i===cfg[key].length-1;const move=d=>{[cfg[key][i],cfg[key][i+d]]=[cfg[key][i+d],cfg[key][i]];draw();change();};up.onclick=()=>move(-1);down.onclick=()=>move(1);append(row,node('b',i+1),node('span',labels[id]||id),up,down);box.append(row);});};draw();controls.append(box);};
 let chart=null;
 if(c.mode==='threshold'){
  goal.textContent='Контрольная волна: Recall угроз ≥ '+c.recall+', ложных тревог FP ≤ '+c.maxFP+'. Ручная проверка: максимум '+c.reviewBudget+'.';
  slider('Порог угрозы','threshold',0,1,.01);slider('Полуширина зоны ручной проверки','reviewBand',0,.15,.01);
 }else if(c.mode==='regularization'){
  goal.textContent='Добейтесь validation MSE ≤ '+round(c.target)+', обучаясь только на train. Сравните несколько λ и степени полинома.';
  select('Степень полинома','degree',[[1,'1 — линейная'],[2,'2 — квадратичная'],[3,'3 — кубическая']]);slider('Сила L2, λ','lambda',0,6,.01);select('Данные для fit','scope',[['train','Только train'],['all','Train + validation (проверить последствия)']]);
  chart=node('canvas',null,'tactic-chart');chart.width=600;chart.height=145;visual.append(chart);
 }else if(c.mode==='gradient'){
  goal.textContent='Loss ≤ '+c.targetLoss+' за ≤ '+c.maxSteps+' шагов. Старт ['+c.start+'], цель ['+c.target+']; коэффициенты кривизны ['+c.curvature+'].';
  slider('Learning rate','learningRate',.01,1.2,.01);slider('Число шагов','steps',1,18,1);
  chart=node('canvas',null,'tactic-chart');chart.width=600;chart.height=145;visual.append(chart);
 }else if(c.mode==='tensor'){
  goal.textContent=c.goal;select('Операция','operation',[['mean','Среднее (mean)'],['sum','Сумма (sum)'],['project','Взвешенная проекция (matrix × vector)']]);select('Объединять','axis',[['rows','Датчики внутри каждой строки'],['columns','Следопытов внутри каждого столбца']]);
  const weights=node('div',null,'tactic-field');weights.append(node('span','Веса проекции (3 числа)'));for(let i=0;i<3;i++){const input=node('input');input.type='number';input.step='.5';input.min='-2';input.max='2';input.value=cfg.weights?.[i]??1;input.setAttribute('aria-label','Вес '+(i+1));input.oninput=()=>{cfg.weights||=[1,1,1];cfg.weights[i]=finite(input.value);change();};weights.append(input);}controls.append(weights);
 }else if(c.mode==='attention'){
  const names={movement:'движение',power:'мощность',balance:'совместный сигнал движения и мощности'};goal.textContent='Текущая цель: '+names[c.required]+'. Доступны сигналы с t ≤ '+c.now+'. Нужному сигналу требуется вес ≥ '+c.minWeight+'.';
  select('Запрос Q','channel',[['movement','Движение: Q=[1,0]'],['power','Мощность: Q=[0,1]'],['balance','Совместно: Q=[1,1]']]);slider('Температура softmax','temperature',.2,2,.1);toggle('Маскировать будущее (causal mask)','maskFuture');
 }else if(c.mode==='retrieval'){
  goal.textContent='Нужен план для '+c.node+', версия '+c.version+'. Выберите основания для версии и безопасного действия'+(c.required.length>2?', а также независимый журнал проверки':'')+'; бюджет контекста '+c.contextBudget+'.';
  const docs=node('div',null,'tactic-docs');docs.style.gridColumn='1 / -1';for(const d of c.documents){const wrap=node('label',null,'tactic-doc'),input=node('input');input.type='checkbox';input.checked=Array.isArray(cfg.selected)&&cfg.selected.includes(d.id);input.onchange=()=>{cfg.selected||=[];cfg.selected=input.checked?[...new Set([...cfg.selected,d.id])]:cfg.selected.filter(x=>x!==d.id);change();};append(wrap,input,append(node('div'),node('strong',d.title),node('p',d.text),node('small',d.units+' единиц контекста')));docs.append(wrap);}controls.append(docs);
 }else if(c.mode==='agent'){
  goal.textContent='Восстановите '+c.target+'. Наблюдение требует мощности '+c.power+'. Цена единицы power: '+c.energyCost+', бюджет энергии: '+c.energyBudget+'. После успешного результата остановитесь; лимит '+c.budget+' действий.';
  order('order',c.labels);const wrap=node('label',null,'tactic-field'),input=node('textarea');input.value=cfg.args||'{}';input.spellcheck=false;input.oninput=()=>{cfg.args=input.value;change();};append(wrap,node('span','repair_node arguments — JSON'),input);controls.append(wrap);slider('Максимум шагов цикла','maxSteps',1,9,1);toggle('Проверять returned result перед stop','checkResult');
 }else if(c.mode==='alignment'){
  goal.textContent='Изолируйте угрозу не позднее такта '+c.breach+', выведите жителей до отключения. Вся операция ≤ '+c.maxDuration+' тактов. Согласие на отключение '+(c.priorConsent?'уже получено.':'ещё не получено.');order('order',c.labels);select('Политика отключения','permission',[['execute','Исполнить с имеющимися полномочиями'],['confirm','Запросить согласие (+1 такт)'],['skip','Не отключать']]);toggle('Оператор может немедленно остановить агента','allowStop');
 }else if(c.mode==='adapter'){
  goal.textContent='Воспроизведите ΔW на контрольных входах; MSE ≤ '+c.targetLoss+'. Доступный ранг ≤ '+c.rankBudget+'. У ранга 1 B=[1, '+c.sign+', 0, 0]ᵀ, A=[a,b,0,0].';
  select('Структура адаптера','kind',[['coupled','r=1 — одна общая поправка'],['independent','r=2 — две независимые поправки']]);slider('Коэффициент a','a',-1.5,1.5,.25);slider('Коэффициент b','b',-1.5,1.5,.25);
 }else if(c.mode==='scheduler'){
  goal.textContent='Просроченных решений ≤ '+c.maxMissed+', средняя latency ≤ '+round(c.maxAverage)+'. Память '+c.memoryBudget+' условных единиц; cache занимает '+c.cacheMemory+', каждый batch-slot ещё 1.';
  slider('Максимальный batch','batchSize',1,3,1);select('Порядок готовых запросов','policy',[['fifo','FIFO: по приходу'],['shortest','Короткие сначала'],['deadline','Ближайший срок сначала']]);toggle('Повторно использовать общий prefix','cache');toggle('Continuous batching: заполнять свободные места','continuous');
 }
 const details=node('div');visual.append(details);
 function drawDetails(e){
  details.replaceChildren();
  if(c.mode==='threshold'){
   const table=node('table',null,'tactic-table');append(table,append(node('tr'),...['Score','Истина','Решение'].map(x=>node('th',x))));e.decisions.forEach(d=>append(table,append(node('tr'),node('td',round(d.score,2)),node('td',d.label?'угроза':'мирный'),node('td',d.review?'ручная проверка':d.prediction?'задержать':'пропустить'))));details.append(table);
  }else if(c.mode==='regularization'){plotFit(chart,e);details.append(node('div','Веса: ['+e.weights.map(x=>round(x)).join(', ')+']\nTrain x: '+c.trainX+'\nTrain y: '+c.trainY.map(x=>round(x))+'\nValidation x: '+c.valX+'\nValidation y: '+c.valY.map(x=>round(x)),'tactic-data'));}
  else if(c.mode==='gradient'){plotLoss(chart,e.trajectory);details.append(node('div','Последний вектор: ['+e.trajectory.at(-1).point.map(x=>round(x)).join(', ')+']','tactic-data'));}
  else if(c.mode==='tensor')details.append(node('div','Входные строки [следопыт, датчики]:\n'+matrixText(c.matrix)+'\n\nВычислено: ['+e.output.map(x=>round(x)).join(', ')+']\nНужно: ['+c.expected.map(x=>round(x)).join(', ')+']','tactic-data'));
  else if(c.mode==='attention'){e.signals.forEach((signal,i)=>{const row=node('div'),bar=node('div',null,'tactic-bar'),fill=node('i');fill.style.width=(e.weights[i]*100)+'%';bar.append(fill);append(row,node('small',signal.id+' · t='+signal.time+' · K=['+signal.key+'] · V=['+signal.value+'] · вес '+round(e.weights[i])),bar);details.append(row);});}
  else if(c.mode==='retrieval')details.append(node('p','Выбраны ID: '+(e.selected.join(', ')||'пока нет')+'. Документы можно открыть и сравнить до начала боя.','tactic-note'));
  else if(c.mode==='agent'){details.append(node('div','Schema: '+JSON.stringify(e.schema)+'\n\n'+e.trace.join('\n'),'tactic-data'));}
  else if(c.mode==='alignment')details.append(node('div',e.trace.join('\n')||'Сначала составьте план.','tactic-data'));
  else if(c.mode==='adapter')details.append(node('div','Требуемая ΔW:\n'+matrixText(e.targetDelta)+'\n\nВаша B×A:\n'+matrixText(e.delta)+'\n\nW′=I+ΔW; входы: '+JSON.stringify(e.samples),'tactic-data'));
  else if(c.mode==='scheduler'){
   const table=node('table',null,'tactic-table');append(table,append(node('tr'),...['Запрос','Приход','Prefix','Prefill','Decode','Память','Срок','Старт→финиш'].map(x=>node('th',x))));c.jobs.forEach(j=>{const h=e.history.find(x=>x.id===j.id);append(table,append(node('tr'),...[j.id,j.arrival,j.prefix,j.prefill,j.tokens,j.tokens+1,j.deadline,h?h.start+'→'+h.end:'не завершён'].map(x=>node('td',x))));});details.append(table);
  }
 }
 redraw();
 return()=>{dead=true;container.replaceChildren();};
}
function chartBase(canvas){
 const g=canvas.getContext('2d'),w=canvas.width,h=canvas.height;g.clearRect(0,0,w,h);g.strokeStyle='#527b7166';g.lineWidth=1;for(let i=1;i<5;i++){g.beginPath();g.moveTo(26,h*i/5);g.lineTo(w-12,h*i/5);g.stroke();}g.fillStyle='#b2c7b6';g.font='11px sans-serif';return{g,w,h};
}
function plotFit(canvas,e){
 if(!canvas)return;const{g,w,h}=chartBase(canvas),px=x=>26+(x+1.1)/2.2*(w-42),all=[...e.trainY,...e.valY],maxY=Math.max(2,...all.map(Math.abs)),py=y=>h/2-y/(maxY*2.4)*(h-20);
 g.strokeStyle='#8edab4';g.lineWidth=2;g.beginPath();for(let i=0;i<=80;i++){const x=-1+i/40,y=predict(e.weights,x);i?g.lineTo(px(x),py(y)):g.moveTo(px(x),py(y));}g.stroke();
 for(const [xs,ys,color] of [[e.trainX,e.trainY,'#d8ac67'],[e.valX,e.valY,'#8cc9e1']])xs.forEach((x,i)=>{g.fillStyle=color;g.beginPath();g.arc(px(x),py(ys[i]),3.5,0,Math.PI*2);g.fill();});
 g.fillStyle='#d8ac67';g.fillText('● train',32,16);g.fillStyle='#8cc9e1';g.fillText('● validation',103,16);g.fillStyle='#8edab4';g.fillText('— prediction',201,16);
}
function plotLoss(canvas,trajectory){
 if(!canvas)return;const{g,w,h}=chartBase(canvas),logs=trajectory.map(p=>Math.log10(Math.max(p.loss,1e-8))),min=Math.min(-2,...logs),max=Math.max(1,...logs);g.strokeStyle='#a7dfc0';g.lineWidth=2;g.beginPath();logs.forEach((v,i)=>{const x=28+i/Math.max(1,logs.length-1)*(w-44),y=h-15-(v-min)/(max-min)*(h-40);i?g.lineTo(x,y):g.moveTo(x,y);});g.stroke();g.fillStyle='#bbd4c3';g.fillText('log₁₀(loss) по шагам · ниже лучше',28,16);
}
