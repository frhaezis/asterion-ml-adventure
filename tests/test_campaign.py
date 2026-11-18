"""Release content invariants. Run: python -m unittest discover -s tests -p test_campaign.py -v.

These checks establish route integrity and declared coverage, not learning outcomes.
"""
import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(relative):
    return json.loads((ROOT / relative).read_text())


class CampaignContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = read('web/data/campaign.json')
        cls.levels = cls.campaign['levels']
        cls.exercises = read('web/python/exercises.json')['exercises']
        cls.sources = {s['id'] for s in read('web/data/sources.json')['sources']}

    def test_complete_contiguous_route(self):
        self.assertEqual([x['id'] for x in self.levels], [f'l{i:03}' for i in range(1, 101)])
        self.assertEqual([x['number'] for x in self.levels], list(range(1, 101)))
        self.assertEqual([c['id'] for c in self.campaign['chapters']], list(range(1, 11)))
        for level in self.levels:
            with self.subTest(level=level['id']):
                self.assertEqual(level['chapter'], 1 + (level['number'] - 1) // 10)
                prior = {x['id'] for x in self.levels[:level['number'] - 1]}
                self.assertTrue(set(level['prerequisites']) <= prior)
                if level['number'] > 1:
                    self.assertIn(f"l{level['number'] - 1:03}", level['prerequisites'])
        self.assertEqual(len({l['reward']['id'] for l in self.levels}), 100)

    def test_forty_real_python_missions_with_spaced_return(self):
        expected_levels = list(range(1, 11)) + list(range(13, 101, 3))
        self.assertEqual([e['id'] for e in self.exercises], [f'p{i:02}' for i in range(1, 41)])
        self.assertEqual([e['levelId'] for e in self.exercises], [f'l{i:03}' for i in expected_levels])
        by_level = {e['levelId']: e for e in self.exercises}
        self.assertEqual(len(by_level), 40)
        for level in self.levels:
            expected = by_level.get(level['id'])
            self.assertEqual(level['pythonId'], expected['id'] if expected else None)
        self.assertEqual(len({e['brief'].strip() for e in self.exercises}), 40)
        self.assertEqual(len({e['solution'].strip() for e in self.exercises}), 40)
        for exercise in self.exercises:
            with self.subTest(exercise=exercise['id']):
                ast.parse(exercise['solution'])
                self.assertTrue(exercise['teaching']['taskBridge'].strip())
                self.assertTrue(exercise['rubric'])
                self.assertTrue(exercise['examples'])
                self.assertTrue(exercise['starter'].strip())
                self.assertNotEqual(exercise['starter'].strip(), exercise['solution'].strip())
                self.assertTrue(set(exercise['sources']) <= self.sources)

    def test_first_ten_are_substantial_syntax_practice(self):
        trees = [ast.parse(e['solution']) for e in self.exercises[:10]]
        nodes = [n for tree in trees for n in ast.walk(tree)]
        for required in [ast.FunctionDef, ast.ClassDef, ast.If, ast.For, ast.Return,
                         ast.Call, ast.List, ast.Dict, ast.ImportFrom, ast.Try]:
            self.assertTrue(any(isinstance(n, required) for n in nodes), required.__name__)
        self.assertTrue(any(isinstance(n, (ast.Yield, ast.YieldFrom, ast.GeneratorExp)) for n in nodes))
        self.assertTrue(any(isinstance(n, ast.arguments) and n.defaults for n in nodes))
        for exercise, tree in zip(self.exercises[:10], trees):
            functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
            self.assertTrue(functions, exercise['id'])
            self.assertGreater(len(list(ast.walk(tree))), 20, exercise['id'])

    def test_authored_lessons_and_independent_transfer(self):
        for field in ['title', 'objective', 'workedExample', 'hint', 'remedial']:
            self.assertEqual(len({str(l[field]).strip() for l in self.levels}), 100, field)
        self.assertEqual(len({json.dumps(l['lesson'], ensure_ascii=False) for l in self.levels}), 100)
        for level in self.levels:
            with self.subTest(level=level['id']):
                for field in ['story', 'lesson', 'topics', 'reflection']:
                    self.assertTrue(level[field])
                teaching = level['teaching']
                self.assertTrue(teaching['goal'].strip())
                self.assertTrue(teaching['prerequisites'])
                self.assertTrue(teaching['steps'])
                for step in teaching['steps']:
                    self.assertTrue(step['title'].strip())
                    self.assertTrue(step['text'].strip())
                self.assertTrue(teaching['workedExample']['steps'])
                self.assertTrue(teaching['taskBridge'].strip())
                self.assertTrue(level['reflection']['checklist'])
                self.assertNotEqual(level['check']['question'], level['transfer']['question'])
                for key in ['check', 'transfer']:
                    check = level[key]
                    self.assertGreaterEqual(len(check['options']), 3)
                    self.assertEqual(len(set(check['options'])), len(check['options']))
                    self.assertIsInstance(check['answer'], int)
                    self.assertIn(check['answer'], range(len(check['options'])))
                    self.assertTrue(check['explanation'].strip())
                for topic in level['topics']:
                    self.assertIn(topic['depth'], {'apply', 'explain', 'recognize'})
                    self.assertIn(topic['source'], self.sources)
                    self.assertTrue(topic['example'].strip())
                    self.assertTrue(topic['question'].strip())

    def test_practice_matches_assignment_without_mandatory_combat(self):
        self.assertEqual(sum(l['practiceKind'] == 'python' for l in self.levels), 40)
        self.assertEqual(sum(l['practiceKind'] == 'concept' for l in self.levels), 60)
        for level in self.levels:
            self.assertIs(level['mandatoryCombat'], False)
            self.assertEqual(level['practiceKind'], 'python' if level['pythonId'] else 'concept')

    def test_required_theory_is_declared_with_sources(self):
        text = '\n'.join(t['name'] + ' ' + t['example'] for l in self.levels for t in l['topics']).lower()
        # A declared concept is required. Causal simulation quality is checked separately.
        coverage = {
            'dataframes': r'pandas|dataframe',
            'arrays': r'numpy|массив',
            'splits and leakage': r'leakage|утечк|разбиени',
            'metrics': r'f1|precision|полнот|точност',
            'classical learning': r'дерев|forest|логистическ|svm',
            'unsupervised learning': r'кластер|pca|снижени.*размерност',
            'generalization': r'регуляризац|regularization|переобуч',
            'autodiff': r'autograd|backpropagation|автоматическ.*дифференц|обратн.*распростран',
            'normalization': r'layernorm|batchnorm|нормализац',
            'attention': r'attention|внимани',
            'tokenization': r'токенизац|tokeniz',
            'KV cache': r'kv.?cache|kv.?к[еэ]ш',
            'retrieval': r'rag|retrieval',
            'tools': r'mcp|схем.*инструмент',
            'adapters': r'lora|низкоранг',
            'quantization': r'квантизац|quantiz',
            'distillation': r'дистилл|distill',
            'preference learning': r'dpo|rlhf',
            'alignment': r'alignment|corrigib|корриг|исправим',
            'evaluation': r'judge|судья|бенчмарк',
            'serving': r'vllm|инференс|serving',
        }
        for label, pattern in coverage.items():
            self.assertRegex(text, pattern, label)


if __name__ == '__main__':
    unittest.main(verbosity=2)
