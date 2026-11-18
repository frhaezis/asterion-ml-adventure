"""Native CPython glue checks; Android process behavior has separate device QA."""
from pathlib import Path
import json
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'web/python'))
import native_runner
BANK=json.loads((ROOT/'web/python/exercises.json').read_text())['exercises']

class NativeGlueTests(unittest.TestCase):
    def test_all_forty_on_both_variants(self):
        for exercise in BANK:
            for variant in ['practice','transfer']:
                with self.subTest(id=exercise['id'],variant=variant):
                    result=json.loads(native_runner.run(exercise['id'],exercise['solution'],variant))
                    self.assertEqual(result['status'],'passed',result)
                    self.assertEqual(result['phase'],'execution')
                    self.assertTrue(result['artifact'])

    def test_stdout_stderr_and_bounded_output(self):
        code=BANK[0]['solution']+"\nimport sys\nprint('Лес')\nprint('diagnostic',file=sys.stderr)"
        result=json.loads(native_runner.run('p01',code))
        self.assertEqual(result['stdout'],'Лес\n')
        self.assertEqual(result['stderr'],'diagnostic\n')
        limited=json.loads(native_runner.run('p01',"print('x'*40000)"))
        self.assertEqual(limited['status'],'error')
        self.assertEqual(len(limited['stdout']),32768)

    def test_errors_and_namespace_isolation(self):
        broken=json.loads(native_runner.run('p01','def broken('))
        self.assertEqual(broken['status'],'error')
        self.assertEqual(broken['phase'],'execution')
        self.assertIn('SyntaxError',broken['feedback'])
        code=BANK[0]['solution']+"\nassert 'previous_run_secret' not in globals()\nprevious_run_secret = 42"
        for _ in range(2):
            self.assertEqual(json.loads(native_runner.run('p01',code))['status'],'passed')

if __name__=='__main__':unittest.main()
