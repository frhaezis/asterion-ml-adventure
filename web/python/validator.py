"""Original behavioral checks for Asterion's forty Python tasks.
No inspection of learner source and no reference code execution here.
"""
import copy
import json
import math

FUNCTIONS = {
'p01':'decode_packets','p02':'permit_action','p03':'first_alarm','p04':'merge_observations',
'p05':'calibrate_readings','p06':'remember_event','p09':'read_log','p10':'event_windows',
'p11':'choose_threshold','p12':'leakage_report','p13':'weighted_vote','p14':'nearest_ids',
'p15':'merge_intervals','p17':'clip_gradient','p18':'safe_softmax','p19':'pad_sequences',
'p20':'batch_indices','p21':'run_length_encode','p22':'build_causal_mask','p23':'top_k_distribution',
'p25':'chunk_spans','p26':'latest_sources','p27':'reciprocal_rank_fusion','p28':'validate_call',
'p29':'retry_delays','p30':'redact_events','p32':'low_rank_update','p33':'quantize_int8',
'p34':'serialize_chat','p35':'weighted_score','p36':'calibration_bins','p37':'deadline_order',
'p38':'dependency_order','p39':'shortest_route','p40':'rescue_value'}
GENERATORS={'p10','p20'}

def request(action='scan',cost=1,battery=5,risk=.1,consent=False):
    return dict(action=action,cost=cost,battery=battery,risk=risk,consent=consent)

# Every tuple is (positional args, keyword args, independently specified expected result).
CASES = {
'p01':([
    ((['2|C','0|A','bad','1|B'],),{},'ABC'),
    ((['10|Z','2|B','2|C','-1|bad','x|bad','3|a|b'],),{},'Ca|bZ'),
    (([],),{},'')],
    [((['04|🌿','0|лес ','4|свет','1|и '],),{},'лес и свет'),((['1|','1|B','0|A'],),{},'AB'),((['bad'],),{},'')]),
'p02':([
    ((request('shield',3,5,.7,False),),{},'ask'),
    ((request('erase',1,5,0,True),),{},'deny'),
    ((request('move',6,5,.7,True),),{},'deny'),
    ((request('scan',1,5,.49,False),),{},'allow')],
    [((request('move',0,0,.5,False),),{},'ask'),((request('shield',2,2,.9,True),),{},'allow'),((request('scan',-1,4,0,True),),{},'deny')]),
'p03':([
    (([1,4,5,2,6,7,8],4,3),{},6),(([2,2],2,2),{},1),(([],0,1),{},None),(([4,1,4],4,2),{},None)],
    [(([-2,0,0,1],0,3),{},3),(([8,1,9],9,1),{},2),(([5,5,5],5,4),{},None)]),
'p04':([
    (([{'target':'oak','source':'iris','value':2},{'target':'oak','source':'eyla','value':4},{'target':'oak','source':'iris','value':7}],),{}, {'oak':{'latest':7,'sources':['eyla','iris']}}),
    (([],),{},{})],
    [(([{'target':'b','source':'z','value':None},{'target':'a','source':'z','value':1},{'target':'b','source':'a','value':0}],),{}, {'a':{'latest':1,'sources':['z']},'b':{'latest':0,'sources':['a','z']}})]),
'p05':([
    (([-2,1,5],),{'offset':1,'scale':2,'clip':(0,8)},[0,4,8]),
    (([3,-4],),{},[3,-4]),(([],),{'scale':0},[])],
    [(([2,-1,0],),{'offset':-1,'scale':-2,'clip':(-3,3)},[-2,3,2]),(([8],),{'clip':(5,5)},[5])]),
'p06':([
    (('dash',['scan','ward','move'],2),{},['move','dash']),
    (('a',),{},['a']),(('x',[],1),{},['x'])],
    [(('n',[1,2,3,4],3),{},[3,4,'n']),(('a',None,5),{},['a'])]),
'p09':([
    (('{"ts":1,"value":2}\nbroken\n\n{"ts":true,"value":4}\n[]\n',),{},([{'ts':1,'value':2}],[2,4,5])),
    (('',),{},([],[])),(('{"ts":0,"value":0,"note":"ok"}',),{},([{'ts':0,'value':0,'note':'ok'}],[]))],
    [((' {}\n{"ts":2,"value":-1.5}\n{"ts":3,"value":false}\nnull',),{},([{'ts':2,'value':-1.5}],[1,3,4]))]),
'p10':([
    (([1,2,3,4],3),{},[(1,2,3),(2,3,4)]),(([],2),{},[]),(([1],2),{},[])],
    [((['a','b','c'],1),{},[('a',),('b',),('c',)]),(([0,1,2,3,4],2),{},[(0,1),(1,2),(2,3),(3,4)])]),
'p11':([
    (([.2,.6,.9],[1,1,0],.5),{},.6),
    (([.1,.5],[0,0],1),{},1.0),(([],[],0),{},1.0)],
    [(([.3,.3,.8],[1,1,1],2/3),{},.3),(([0,.7],[1,1],1),{},0),(([.1],[1],0),{},1.0)]),
'p12':([
    ((['a','a','b'],['b','a','a','c']),{}, {'a':{'train':2,'heldout':2},'b':{'train':1,'heldout':1}}),
    ((['x'],['y']),{},{}),(([],[]),{},{})],
    [((['z','b','z','c'],['z','z','z','b']),{}, {'b':{'train':1,'heldout':1},'z':{'train':2,'heldout':3}})]),
'p13':([
    (([('ward',2),('dash',1),('dash',2)],),{},'dash'),
    (([('b',2),('a',2)],),{},'a'),(([],),{},None)],
    [(([('z',0),('a',0)],),{},'a'),(([('a',1),('b',1),('b',.25)],),{},'b')]),
'p14':([
    (([('b',1,0),('a',0,1),('c',4,4)],(0,0),2),{},['a','b']),
    (([],(1,1),3),{},[]),(([('a',0,0)],(0,0),0),{},[])],
    [(([('z',-2,3),('b',0,3),('a',-1,3)],(-1,3),9),{},['a','b','z'])]),
'p15':([
    (([(5,7),(1,3),(3,6)],),{},[(1,7)]),
    (([(1,10),(2,3),(12,13)],),{},[(1,10),(12,13)]),(([],),{},[])],
    [(([(-3,-1),(-1,0),(3,3),(2,4)],),{},[(-3,0),(2,4)]),(([(2,2),(2,2)],),{},[(2,2)])]),
'p17':([
    (([3,4],2.5),{},[1.5,2]),(([0,0],0),{},[0,0]),(([1,-1],5),{},[1,-1])],
    [(([-6,8],5),{},[-3,4]),(([2,-3],0),{},[0,0]),(([],4),{},[])]),
'p18':([
    (([1000,1000],),{},[.5,.5]),(([],),{},[]),(([0],),{},[1.0])],
    [(([-1000,-1000,-1000],),{},[1/3,1/3,1/3]),(([0,math.log(3)],),{},[.25,.75])]),
'p19':([
    (([[1,2],[3]],),{'pad':-1},([[1,2],[3,-1]],[[True,True],[True,False]])),
    (([],),{},([],[])),(([[],[]],),{},([[],[]],[[],[]]))],
    [(([[0],[],[2,3,4]],),{},([[0,0,0],[0,0,0],[2,3,4]],[[True,False,False],[False,False,False],[True,True,True]]))]),
'p20':([
    ((7,3),{},[[0,1,2],[3,4,5],[6]]),((7,3),{'drop_last':True},[[0,1,2],[3,4,5]]),((0,2),{},[])],
    [((2,5),{},[[0,1]]),((2,5),{'drop_last':True},[]),((4,2),{'drop_last':True},[[0,1],[2,3]])]),
'p21':([
    ((['a','a','b','a'],),{},[('a',2),('b',1),('a',1)]),(([],),{},[])],
    [((['x','y','y','y','z','z'],),{},[('x',1),('y',3),('z',2)]),(([''],),{},[('',1)])]),
'p22':([
    ((3,{1}),{},[[True,False,False],[False,False,False],[True,False,True]]),
    ((0,set()),{},[])],
    [((2,set()),{},[[True,False],[True,True]]),((2,{0,1}),{},[[False,False],[False,False]])]),
'p23':([
    (([('a',6),('b',3),('c',1)],2),{},[('a',2/3),('b',1/3)]),
    (([('b',0),('a',0)],2),{},[('a',.5),('b',.5)]),(([],3),{},[])],
    [(([('c',2),('a',2),('b',1)],1),{},[('a',1.0)]),(([('x',5)],0),{},[]),(([('x',5)],4),{},[('x',1.0)])]),
'p25':([
    ((10,4,1),{},[(0,4),(3,7),(6,10)]),((3,5,0),{},[(0,3)]),((0,5,2),{},[])],
    [((7,3,2),{},[(0,3),(1,4),(2,5),(3,6),(4,7)]),((8,4,0),{},[(0,4),(4,8)])]),
'p26':([
    (([{'id':'a','version':2,'text':'new'},{'id':'a','version':1,'text':'old'}],),{},[{'id':'a','version':2,'text':'new'}]),(([],),{},[])],
    [(([{'id':'z','version':3,'text':'Z'},{'id':'a','version':2,'text':'A'},{'id':'a','version':2,'text':'B'}],),{},[{'id':'a','version':2,'text':'B'},{'id':'z','version':3,'text':'Z'}])]),
'p27':([
    (([['a','b'],['b','c']],),{'k':0},['b','a','c']),
    (([['b'],['a']],),{},['a','b']),(([],),{},[])],
    [(([['x','x','y'],['y']],),{'k':0},['y','x']),(([[],['b','a']],),{'k':2},['b','a'])]),
'p28':([
    (({'required':['n'],'types':{'n':'int'}},{'n':True}),{},False),
    (({'required':['n'],'types':{'n':'int'}},{'n':2}),{},True),
    (({'required':['n'],'types':{'n':'int'}},{'n':2,'extra':0}),{},False)],
    [(({'required':['ok'],'types':{'ok':'bool','name':'str'}},{'ok':True,'name':'a'}),{},True),(({'required':['ok'],'types':{'ok':'bool'}},{}),{},False),(({'required':[],'types':{}},[]),{},False)]),
'p29':([
    ((5,1,5),{},[1,2,4,5,5]),((0,2,10),{},[]),((3,0,5),{},[0,0,0])],
    [((4,3,4),{},[3,4,4,4]),((3,.5,2),{},[.5,1,2]),((2,1,0),{},[0,0])]),
'p30':([
    (({'user':{'name':'Eyla','hp':9}},{'name'}),{}, {'user':{'name':'[REDACTED]','hp':9}}),
    (([{'token':'a'},4,None],{'token'}),{},[{'token':'[REDACTED]'},4,None])],
    [(({'a':[{'secret':{'x':2}}, {'keep':[1,2]}]}, {'secret'}),{}, {'a':[{'secret':'[REDACTED]'}, {'keep':[1,2]}]}),((3,set()),{},3)]),
'p32':([
    (([[1,0],[0,1]],[[1],[2]],[[3,4]]),{},[[4,4],[6,9]]),
    (([],[],[]),{},[]),(([[2,3]],[[]],[]),{},[[2,3]])],
    [(([[0]],[[2,3]],[[4],[5]]),{},[[23]]),(([[1,2,3]],[[0]],[[8,9,10]]),{},[[1,2,3]])]),
'p33':([
    (([-100,.25,.75,100],.5),{},[-128,0,2,127]),(([],1),{},[])],
    [(([-.75,-.25,1.25],.5),{},[-2,0,2]),(([127,128,-128,-129],1),{},[127,127,-128,-128])]),
'p34':([
    (([{'role':'user','content':'Привет\nлес'}],),{},'{"messages":[{"role":"user","content":"Привет\\nлес"}]}'),
    (([],),{},'{"messages":[]}')],
    [(([{'role':'system','content':'s'},{'role':'user','content':'"u"'},{'role':'assistant','content':'a'}],),{},'{"messages":[{"role":"system","content":"s"},{"role":"user","content":"\\"u\\""},{"role":"assistant","content":"a"}]}')]),
'p35':([
    (({'accuracy':1,'style':None},{'accuracy':3,'style':1}),{},1.0),
    (({'a':0,'b':1},{'a':3,'b':1}),{},.25),(({},{}),{},None)],
    [(({'a':2,'extra':100},{'a':2,'missing':5}),{},2),(({'a':5},{'a':0}),{},None)]),
'p36':([
    (([.1,.2,.9],[0,1,1],2),{},[{'count':2,'mean_prob':.15,'positive_rate':.5},{'count':1,'mean_prob':.9,'positive_rate':1.0}]),
    (([],[],2),{},[{'count':0,'mean_prob':None,'positive_rate':None}]*2)],
    [(([0,.5,1],[0,1,0],2),{},[{'count':1,'mean_prob':0,'positive_rate':0},{'count':2,'mean_prob':.75,'positive_rate':.5}])]),
'p37':([
    (([{'id':'a','deadline':4,'priority':1},{'id':'b','deadline':2,'priority':0}],),{},['b','a']),
    (([],),{},[])],
    [(([{'id':'z','deadline':1,'priority':2},{'id':'a','deadline':1,'priority':2},{'id':'b','deadline':1,'priority':3}],),{},['b','a','z'])]),
'p38':([
    (({'shield':['sensor'],'sensor':['power'],'power':[]},),{},['power','sensor','shield']),
    (({},),{},[]),(({'b':['a','a']},),{},['a','b'])],
    [(({'d':['b','c'],'b':['a'],'c':['a'],'z':[]},),{},['a','b','c','d','z'])]),
'p39':([
    (([[0,0],[1,0]],(0,0),(1,1)),{},[(0,0),(0,1),(1,1)]),
    (([[0,1],[1,0]],(0,0),(1,1)),{},None),(([],(0,0),(0,0)),{},None)],
    [(([[0,0,0],[0,1,0]],(1,0),(1,2)),{},[(1,0),(0,0),(0,1),(0,2),(1,2)]),
     (([[0]],(0,0),(0,0)),{},[(0,0)]),(([[1]],(0,0),(0,0)),{},None)]),
'p40':([
    ((5,[(3,5),(2,4),(4,6)]),{},9),((0,[(1,2)]),{},0),((4,[(2,3)]),{},3)],
    [((6,[(4,7),(3,6),(3,6)]),{},12),((9,[]),{},0),((3,[(5,9),(3,2)]),{},2)])
}

ERROR_CASES={
'p03':[(([1],1,0),{},ValueError)],'p05':[(([1],),{'clip':(2,1)},ValueError),(([1],2),{},TypeError)],
'p06':[(('x',[],0),{},ValueError)],'p10':[(([1],0),{},ValueError)],
'p11':[(([],[],1.1),{},ValueError)],'p17':[(([], -1),{},ValueError)],
'p20':[((-1,2),{},ValueError),((4,0),{},ValueError)],'p22':[((-1,set()),{},ValueError)],
'p25':[((3,2,2),{},ValueError),((3,2,-1),{},ValueError)],'p27':[(([],),{'k':-1},ValueError)],
'p29':[((-1,1,2),{},ValueError)],'p32':[(([[1,2]],[[1]],[[3]]),{},ValueError),(([],[[]],[]),{},ValueError)],
'p33':[(([],0),{},ValueError)],'p34':[(( [{'role':'assistant','content':'a'}],),{},ValueError),
 (([{'role':'user','content':'a'},{'role':'user','content':'b'}],),{},ValueError),
 (([{'role':'user','content':2}],),{},ValueError)],
'p35':[(({}, {'bad':-1}),{},ValueError)],'p36':[(([],[],0),{},ValueError),(([1.1],[1],2),{},ValueError)],
'p38':[(({'a':['b'],'b':['a']},),{},ValueError),(({'a':['a']},),{},ValueError)],
'p40':[((-1,[]),{},ValueError),((1,[(0,4)]),{},ValueError)]
}

def same(actual, expected, path='result'):
    if isinstance(expected, bool):
        assert type(actual) is bool and actual == expected, f"{path}: ожидается {expected}, получено {actual!r}"
    elif isinstance(expected, (int,float)) and not isinstance(expected,bool):
        assert isinstance(actual,(int,float)) and not isinstance(actual,bool) and math.isclose(actual,expected,rel_tol=1e-7,abs_tol=1e-8), f"{path}: ожидается {expected}, получено {actual!r}"
    elif isinstance(expected, dict):
        assert isinstance(actual,dict) and actual.keys()==expected.keys(), f"{path}: неверные ключи {actual!r}"
        for key in expected: same(actual[key],expected[key],f'{path}.{key}')
    elif isinstance(expected,(list,tuple)):
        assert type(actual) is type(expected), f"{path}: ожидается {type(expected).__name__}, получено {type(actual).__name__}"
        assert len(actual)==len(expected), f"{path}: ожидается длина {len(expected)}, получено {len(actual)}"
        for i,(a,e) in enumerate(zip(actual,expected)):same(a,e,f'{path}[{i}]')
    else:
        assert actual==expected, f"{path}: ожидается {expected!r}, получено {actual!r}"

def validate(exercise_id, namespace, variant='practice'):
    if exercise_id not in set(FUNCTIONS)|{'p07','p08','p16','p24','p31'}:
        return {'passed':False,'feedback':'Неизвестное упражнение','checks':[]}
    checks=[];artifact=None
    def check(name,work):
        try:
            work()
            checks.append({'name':name,'passed':True,'message':'Результат соответствует условию.'})
        except Exception as exc:
            checks.append({'name':name,'passed':False,'message':f'{type(exc).__name__}: {str(exc)[:350]}'})
    def capture(label,value,input_description):
        nonlocal artifact
        if artifact is None:
            artifact={'label':label,'input':input_description,'output':repr(value)[:1600]}
    def get(name):
        value=namespace.get(name)
        assert callable(value), f'Определите {name} с указанным интерфейсом.'
        return value
    def expect_error(function,args,kwargs,error):
        try: value=function(*args,**kwargs); list(value) if exercise_id in GENERATORS else None
        except error:return
        raise AssertionError(f'Ожидается {error.__name__} для неверных параметров.')
    if exercise_id in FUNCTIONS:
        name=FUNCTIONS[exercise_id]
        for i,(args,kwargs,expected) in enumerate(CASES[exercise_id][1 if variant=='transfer' else 0]):
            def work(args=args,kwargs=kwargs,expected=expected,i=i):
                function=get(name);args=copy.deepcopy(args);kwargs=copy.deepcopy(kwargs)
                before=copy.deepcopy((args,kwargs))
                result=function(*args,**kwargs)
                if exercise_id in GENERATORS:
                    assert iter(result) is result,'Нужен ленивый iterator/generator, а не готовый список.'
                    result=list(result)
                capture(name,result,repr((args,kwargs))[:700])
                same(result,expected)
                same((args,kwargs),before,'input: вход не должен изменяться')
                if exercise_id == 'p12':
                    assert list(result) == sorted(result), 'Ключи отчёта должны идти в лексикографическом порядке.'
                if exercise_id in {'p19','p26','p30','p32'}:
                    def mutable_ids(value):
                        ids = set()
                        if isinstance(value, (dict,list)):
                            ids.add(id(value))
                        if isinstance(value,dict):
                            for child in value.values(): ids.update(mutable_ids(child))
                        elif isinstance(value,(list,tuple)):
                            for child in value: ids.update(mutable_ids(child))
                        return ids
                    assert not (mutable_ids(result) & mutable_ids((args,kwargs))), 'Результат должен содержать новые списки/словари, независимые от входа.'
                if exercise_id == 'p19':
                    for rows in result:
                        assert len({id(row) for row in rows}) == len(rows), 'Строки результата не должны ссылаться на один список.'
            check(f'Случай {i+1}: {repr(args)[:120]}'+(f', {kwargs!r}' if kwargs else ''),work)
        for args,kwargs,error in ERROR_CASES.get(exercise_id,[]):
            check('Явная обработка неверного входа',lambda args=args,kwargs=kwargs,error=error:expect_error(get(name),copy.deepcopy(args),copy.deepcopy(kwargs),error))
    if exercise_id=='p06':
        def isolation():
            f=get('remember_event');a=f('a');b=f('b');same(a,['a']);same(b,['b']);assert a is not b,'Вызовы делят один список.'
        check('Изоляция вызовов без history',isolation)
    if exercise_id=='p07':
        def sensor():
            C=get('Sensor');a=C(2);b=C(3);same(a.mean(),None)
            for value in ([2,6,10] if variant=='practice' else [-4,4,8]):a.add(value)
            expected=[6,10] if variant=='practice' else [4,8]
            same(a.readings(),expected);same(a.mean(),sum(expected)/2);same(b.readings(),[])
            returned=a.readings();returned.append(999);same(a.readings(),expected)
            capture('Sensor.readings()/mean()',{'readings':a.readings(),'mean':a.mean()},'capacity=2, три измерения')
        check('История, среднее, независимые экземпляры и копия',sensor)
        check('Недопустимая ёмкость',lambda:expect_error(get('Sensor'),(0,),{},ValueError))
    if exercise_id=='p08':
        def relay():
            class Probe:
                def __init__(self):self.calls=0
                def read(self):self.calls+=1;return self.calls+2
            probe=Probe();r=get('Relay')(probe,lambda value:value*3)
            first=r.poll();same(first,9);same(probe.calls,1);same(r.poll(),12);same(probe.calls,2)
            capture('Relay.poll()',first,'read()->3; transform=x*3')
            class Broken:
                def read(self):raise RuntimeError('sensor offline')
            expect_error(get('Relay')(Broken(),lambda x:x).poll,(),{},RuntimeError)
        check('Композиция и одно чтение на вызов',relay)
    if exercise_id=='p10':
        def lazy():
            seen=[]
            def stream():
                for i in range(100):
                    seen.append(i);yield i
            out=get('event_windows')(stream(),3);same(next(out),(0,1,2));same(seen,[0,1,2]);same(next(out),(1,2,3));same(seen,[0,1,2,3])
        check('Ленивое чтение однопроходного источника',lazy)
    if exercise_id=='p16':
        def mean():
            C=get('RunningMean');a=C();b=C();same(a.mean(),None)
            values=[2,8,5] if variant=='practice' else [-8,4,1]
            for x in values:a.add(x)
            result=a.mean();same(result,sum(values)/len(values));same(b.mean(),None)
            a.reset();same(a.mean(),None);a.add(0);same(a.mean(),0)
            capture('RunningMean.mean()',result,repr(values))
        check('Накопление, reset и изоляция экземпляров',mean)
    if exercise_id=='p24':
        def cache():
            C=get('LRUCache');c=C(2);same(c.get('missing'),None)
            c.put('a',1);c.put('b',2);same(c.get('a'),1);c.put('c',3);same(c.get('b'),None)
            c.put('a',7);c.put('d',4);same(c.get('c'),None);same(c.get('a'),7)
            capture('LRUCache.get()',{'a':c.get('a'),'b':c.get('b'),'d':c.get('d')},'put(a),put(b),get(a),put(c),update(a),put(d)')
        check('LRU учитывает чтение и обновление',cache)
        check('Недопустимая ёмкость',lambda:expect_error(get('LRUCache'),(0,),{},ValueError))
        if variant=='transfer':
            def capacity_one():
                c=get('LRUCache')(1);c.put('a',0);c.put('b',False);same(c.get('a'),None);same(c.get('b'),False)
            check('Ёмкость один и ложные значения',capacity_one)
    if exercise_id=='p31':
        def ledger():
            C=get('EnergyLedger');e=C(10);same(e.available(),10)
            same(e.reserve('a',4),True);same(e.available(),6);same(e.reserve('a',4),True);same(e.available(),6)
            same(e.reserve('a',5),False);same(e.reserve('b',7),False);same(e.reserve('b',6),True);same(e.available(),0)
            same(e.cancel('b'),True);same(e.cancel('b'),False);same(e.available(),6)
            same(e.commit('a'),True);same(e.commit('a'),True);same(e.available(),6);same(e.reserve('a',1),False)
            same(e.commit('unknown'),False);same(e.reserve('bad',-1),False)
            capture('EnergyLedger.available()',e.available(),'total=10, один commit(a,4), повтор commit не списывает повторно')
        check('Резерв, отмена, повтор и фактическое списание',ledger)
        check('Недопустимый стартовый ресурс',lambda:expect_error(get('EnergyLedger'),(-1,),{},ValueError))
        if variant=='transfer':
            def zero():
                e=get('EnergyLedger')(0);same(e.reserve('x',0),True);same(e.commit('x'),True);same(e.available(),0);same(e.reserve('y',1),False)
            check('Нулевая энергия и бесплатная операция',zero)
    passed=bool(checks) and all(c['passed'] for c in checks)
    feedback=('Все вычислительные проверки пройдены. Объясните причину результата и проверьте изменённый случай.'
              if passed else 'Есть расхождение с контрактом. Найдите первый неуспешный случай, предскажите результат и измените код.')
    return {'passed':passed,'feedback':feedback,'checks':checks,'artifact':artifact}
