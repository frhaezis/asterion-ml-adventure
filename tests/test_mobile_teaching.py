"""Regression checks for the previously observed pedagogy failures.

These check contract alignment and executable examples, not human learning.
Manual reasoning review is documented in docs/mobile_curriculum_review.md.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((ROOT/path).read_text())

class TeachingAlignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.levels=read('web/data/campaign.json')['levels']
        cls.by_number={l['number']:l for l in cls.levels}
        cls.exercises={e['id']:e for e in read('web/python/exercises.json')['exercises']}

    def test_route_requires_relevant_practice_not_legacy_combat(self):
        for level in self.levels:
            with self.subTest(level=level['id']):
                self.assertIs(level['mandatoryCombat'],False)
                self.assertEqual(level['practiceKind'],'python' if level['pythonId'] else 'concept')
                self.assertEqual(level['learningVersion'],2)
                for kind in ('check','transfer'):
                    q=level[kind]
                    self.assertEqual(len(q['options']),len(set(q['options'])))
                    self.assertIn(q['answer'],range(len(q['options'])))
                    self.assertNotIn('Обоснуйте причинную связь и проверьте её на новом случае.',q['explanation'])

    def test_python_tutorial_is_present_before_exact_contract(self):
        for level in self.levels:
            if not level['pythonId']:
                continue
            ex=self.exercises[level['pythonId']]
            with self.subTest(level=level['id']):
                self.assertEqual(ex['levelId'],level['id'])
                self.assertEqual(level['exerciseContract'],ex['brief'])
                self.assertEqual(level['teaching']['prerequisites'],ex['teaching']['prerequisites'])
                self.assertEqual(level['teaching']['steps'][:len(ex['teaching']['steps'])],ex['teaching']['steps'])
                self.assertEqual(level['teaching']['workedExample'],ex['teaching']['workedExample'])
                self.assertEqual(level['teaching']['taskBridge'],ex['teaching']['taskBridge'])

    def test_every_lesson_supplies_method_example_boundaries_and_remediation(self):
        prompts=[]
        for level in self.levels:
            with self.subTest(level=level['id']):
                teaching=level['teaching']
                self.assertTrue(teaching['goal'])
                self.assertTrue(teaching['prerequisites'])
                self.assertTrue(all(x['name'] and x['explanation'] and x['example'] for x in teaching['prerequisites']))
                self.assertGreaterEqual(len(teaching['steps']),3)
                self.assertTrue(all(x['title'] and x['text'] for x in teaching['steps']))
                self.assertGreaterEqual(len(teaching['workedExample']['steps']),3)
                self.assertTrue(teaching['taskBridge'])
                self.assertTrue(all(p['symptom'] and p['explanation'] for p in teaching['pitfalls']))
                self.assertTrue(teaching['interview'])
                self.assertNotEqual(level['check']['question'],level['transfer']['question'])
                prompts.extend([level['check']['question'],level['transfer']['question']])
        self.assertEqual(len(prompts),len(set(prompts)))

    def test_inventory_is_preserved_but_known_misplacements_are_corrected(self):
        seed=read('tools/mobile_curriculum_seed.json')['levels']
        before={t['name'] for l in seed for t in l['topics']}
        after={t['name'] for l in self.levels for t in l['topics']}
        self.assertEqual(before,after)
        locations={t['name']:l['number'] for l in self.levels for t in l['topics']}
        self.assertEqual(locations['multi-head attention'],44)
        self.assertEqual(locations['QLoRA'],72)
        self.assertEqual(locations['MCP / tools / resources / prompts'],66)
        self.assertEqual(locations['Decision Tree / Random Forest'],26)
        self.assertEqual(locations['KV cache / prefill vs decode'],87)
        self.assertEqual(locations['pandas / tabular data / index alignment'],17)
        self.assertEqual(locations['agent / workflow / chatbot'],62)

    def test_no_hidden_rag_requirement_in_packet_parsing(self):
        l=self.by_number[1]
        assessed=' '.join([l['objective'],l['check']['question'],l['transfer']['question'],l['hint']]).lower()
        self.assertNotIn('retrieval',assessed)
        self.assertNotIn('подтверждающий источник',assessed)
        self.assertIn('split',json.dumps(l['teaching']))
        self.assertIn('isdecimal',json.dumps(l['teaching']))

    def test_permission_is_not_granted_by_argument_schema(self):
        l=self.by_number[64]
        theory=' '.join(s['text'] for s in l['teaching']['steps'])
        self.assertIn('разрешения проверяются отдельно',theory)
        ns={};exec(self.exercises['p28']['solution'],ns)
        schema={'required':['id'],'types':{'id':'str','limit':'int'}}
        self.assertTrue(ns['validate_call'](schema,{'id':'x','limit':2}))
        self.assertFalse(ns['validate_call'](schema,{'id':'x','limit':True}))
        self.assertFalse(ns['validate_call'](schema,{'id':'x','extra':2}))
        self.assertNotIn('ToolPolicy',l['exerciseContract'])

    def test_zero_denominator_convention_is_local_not_a_contradictory_global_rule(self):
        # The threshold exercise deliberately defines recall=1 with no positives.
        # The next lesson uses zero for undefined aggregate metrics, so it must
        # explicitly distinguish conventions instead of asserting a global rule.
        ns={};exec(self.exercises['p11']['solution'],ns)
        self.assertEqual(ns['choose_threshold']([],[],1),1.0)
        theory=' '.join(s['text'] for s in self.by_number[14]['teaching']['steps'])
        self.assertIn('Конкретный контракт',theory)
        self.assertIn('recall=1',theory)
        self.assertNotIn('в этом курсе метрика равна нулю',theory)

    def test_new_numeric_transfer_examples_match_runtime(self):
        def solution(id):
            ns={};exec(self.exercises[id]['solution'],ns);return ns
        self.assertEqual(solution('p01')['decode_packets'](['8|B|C','2|A','8|D','x|E']),'AD')
        self.assertEqual(solution('p02')['permit_action']({'action':'scan','cost':1,'battery':3,'risk':0.5,'consent':False}),'ask')
        self.assertEqual(solution('p03')['first_alarm']([5,1,5,5],5,2),3)
        self.assertEqual(solution('p05')['calibrate_readings']([3],offset=2,scale=4,clip=(0,12)),[12])
        self.assertEqual(solution('p11')['choose_threshold']([0.2,0.8],[1,1],0.5),0.8)
        self.assertEqual(solution('p13')['weighted_vote']([('b',2),('a',1),('a',1)]),'a')
        self.assertEqual(solution('p14')['nearest_ids']([('a',1,0),('b',0,1),('c',3,0)],(0,0),1),['a'])
        self.assertEqual(solution('p15')['merge_intervals']([(1,5),(2,3),(5,7)]),[(1,7)])
        self.assertEqual(solution('p19')['pad_sequences']([[0],[2,3]],0),([[0,0],[2,3]],[[True,False],[True,True]]))
        self.assertEqual(list(solution('p20')['batch_indices'](7,3,False)),[[0,1,2],[3,4,5],[6]])

    def test_contract_state_changes_match_oop_transfer(self):
        ns={};exec(self.exercises['p07']['solution'],ns)
        sensor=ns['Sensor'](2);sensor.add(6);sensor.add(10)
        snapshot=sensor.readings();snapshot.pop()
        self.assertEqual(sensor.mean(),8)
        other=ns['Sensor'](2);self.assertIsNone(other.mean())
        ns={};exec(self.exercises['p16']['solution'],ns)
        mean=ns['RunningMean']()
        for value in [2,4,12]:mean.add(value)
        self.assertEqual(mean.mean(),6);mean.reset();self.assertIsNone(mean.mean())

    def test_all_source_links_resolve_inside_offline_registry(self):
        sources=read('web/data/sources.json')['sources'];ids={s['id'] for s in sources}
        self.assertEqual(len(sources),len(ids))
        for level in self.levels:
            self.assertLessEqual(set(level['sources']),ids)
            self.assertLessEqual({t['source'] for t in level['topics']},ids)
        for source in sources:
            self.assertTrue(source['url'].startswith('https://'))
            self.assertTrue(source['readScope'])
            self.assertTrue(source['caveat'])

    def test_mechanism_limitations_are_taught_before_assessment(self):
        cases={
            23:['data_loss','lambda','Elastic Net','SUM','MEAN','AdamW'],
            39:['1−p','не означает','model.eval()','torch.no_grad()'],
            44:['j>i','строки','столбцы'],
            72:['QLoRA','ранг'],
            86:['prefill','decode','continuous batching'],
            87:['prefill','не отменяет','прав пользователя'],
            96:['ограничение','Corrigibility','необратимые'],
        }
        for n,needles in cases.items():
            text=' '.join(s['text'] for s in self.by_number[n]['teaching']['steps'])
            for needle in needles:
                self.assertIn(needle.lower(),text.lower(),(n,needle))

if __name__=='__main__':
    unittest.main(verbosity=2)
