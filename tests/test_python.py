"""Behavioral curriculum and offline-runtime regression tests.
Run: python3 tests/test_python.py [--browser]
Browser mode additionally needs Playwright and Chromium; no downloads at test time.
"""
from pathlib import Path
import json
import contextlib
import io
import runpy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BANK = json.loads((ROOT / 'web/python/exercises.json').read_text())['exercises']
EXERCISES = {entry['id']: entry for entry in BANK}
VALIDATE = runpy.run_path(str(ROOT / 'web/python/validator.py'))['validate']


def execute(exercise, code, variant='practice'):
    namespace = {}
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        exec(compile(code, '<test learner>', 'exec'), namespace)
        return VALIDATE(exercise, namespace, variant)


class CurriculumTests(unittest.TestCase):
    def test_exact_ids_levels_and_learning_material(self):
        self.assertEqual([e['id'] for e in BANK], [f'p{i:02}' for i in range(1, 41)])
        expected = list(range(1, 11)) + list(range(13, 101, 3))
        self.assertEqual([e['levelId'] for e in BANK], [f'l{i:03}' for i in expected])
        for e in BANK:
            for field in ['brief', 'starter', 'solution', 'workedExample', 'hint', 'battleUse', 'rubric', 'sources']:
                self.assertTrue(e[field], (e['id'], field))

    def test_all_reference_solutions_on_both_variants(self):
        for exercise in BANK:
            for variant in ['practice', 'transfer']:
                with self.subTest(id=exercise['id'], variant=variant):
                    result = execute(exercise['id'], exercise['solution'], variant)
                    self.assertTrue(result['passed'], result['checks'])
                    self.assertTrue(result['artifact']['output'])
                    self.assertGreater(len(result['checks']), 0)

    def test_unimplemented_starters_do_not_pass(self):
        for exercise in BANK:
            with self.subTest(id=exercise['id']):
                try:
                    result = execute(exercise['id'], exercise['starter'])
                except (NotImplementedError, SyntaxError):
                    continue
                self.assertFalse(result['passed'])

    def test_plausible_wrong_algorithms_are_rejected(self):
        mutants = {
            # Lexical instead of numeric packet ordering.
            'p01': "def decode_packets(records):\n d={}\n for r in records:\n  if '|' in r:\n   i,s=r.split('|',1)\n   if i.isdecimal(): d[i]=s\n return ''.join(d[k] for k in sorted(d))",
            # Shared mutable default accumulates previous calls.
            'p06': "def remember_event(event,history=[],limit=3):\n history.append(event)\n return history[-limit:]",
            # Materializes the entire iterator: correct values, wrong laziness.
            'p10': "def event_windows(events,size):\n if size<=0: raise ValueError()\n values=list(events)\n for i in range(len(values)-size+1): yield tuple(values[i:i+size])",
            # Naive softmax overflows under realistic large logits.
            'p18': "import math\ndef safe_softmax(logits):\n e=[math.exp(x) for x in logits]\n return [x/sum(e) for x in e]",
            # FIFO does not update recency on reads.
            'p24': "from collections import OrderedDict\nclass LRUCache:\n def __init__(self,capacity):\n  if capacity<=0: raise ValueError()\n  self.capacity=capacity;self.data=OrderedDict()\n def get(self,key): return self.data.get(key)\n def put(self,key,value):\n  self.data[key]=value\n  if len(self.data)>self.capacity:self.data.popitem(last=False)",
            # Ascending budget allows the same 0/1 knapsack item repeatedly.
            'p40': "def rescue_value(capacity,items):\n if capacity<0 or any(c<=0 for c,v in items):raise ValueError()\n dp=[0]*(capacity+1)\n for c,v in items:\n  for b in range(c,capacity+1):dp[b]=max(dp[b],dp[b-c]+v)\n return dp[capacity]",
        }
        for exercise, code in mutants.items():
            with self.subTest(exercise=exercise):
                self.assertFalse(execute(exercise, code)['passed'])

    def test_output_copies_and_key_order_are_checked(self):
        source = EXERCISES['p26']['solution']
        # A value-correct function returning aliases to input dictionaries.
        source = source.replace('dict(record)', 'record').replace('record.copy()', 'record')
        self.assertNotEqual(source, EXERCISES['p26']['solution'])
        self.assertFalse(execute('p26', source)['passed'])
        # Wrap the actual function so only insertion order changes.
        unordered = EXERCISES['p12']['solution'] + '\n_original = leakage_report\ndef leakage_report(a,b):\n result=_original(a,b)\n return {k:result[k] for k in reversed(result)}'
        self.assertFalse(execute('p12', unordered)['passed'])

    def test_artifact_captures_candidate_not_reference(self):
        result = execute('p01', "def decode_packets(records): return 'candidate-specific-result'")
        self.assertFalse(result['passed'])
        self.assertEqual(result['artifact']['output'], "'candidate-specific-result'")


def browser_tests():
    """Run the actual vendored CPython/Wasm with external network blocked."""
    import functools
    import http.server
    import shutil
    import threading
    from playwright.sync_api import sync_playwright

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT / 'web')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    external = []
    errors = []
    requested = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=shutil.which('chromium'), headless=True, args=['--no-sandbox'])
            context = browser.new_context()
            def route_request(route):
                requested.append(route.request.url)
                if not route.request.url.startswith(origin + '/'):
                    external.append(route.request.url)
                    route.abort()
                elif route.request.url.endswith('/qa-python.html'):
                    route.fulfill(content_type='text/html', body='<html><body>Offline Python test</body></html>')
                else:
                    route.continue_()
            context.route('**/*', route_request)
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(origin + '/qa-python.html')
            result = page.evaluate('''async () => {
                const {PythonRunner} = await import('/js/python-runner.js');
                const runner = new PythonRunner();
                await runner.init();
                const bank = (await (await fetch('/python/exercises.json')).json()).exercises;
                const runs = [];
                for (const exercise of bank) {
                    for (const variant of ['practice','transfer']) {
                        const result = await runner.run({exerciseId:exercise.id, code:exercise.solution, variant});
                        runs.push({id:exercise.id, variant, status:result.status, artifact:result.artifact, failed:result.checks.filter(c=>!c.passed)});
                    }
                }
                const syntax = await runner.run({exerciseId:'p01',code:'def broken('});
                const wrong = await runner.run({exerciseId:'p01',code:"print('REAL STDOUT')\\ndef decode_packets(records): return 'candidate-value'"});
                const timeout = await runner.run({exerciseId:'p01',code:'while True: pass',timeoutMs:120});
                const afterTimeout = await runner.run({exerciseId:'p01',code:bank[0].solution});
                const pending = runner.run({exerciseId:'p01',code:'while True: pass'});
                setTimeout(()=>runner.stop(), 100);
                const stopped = await pending;
                const afterStop = await runner.run({exerciseId:'p01',code:bank[0].solution});
                const outputLimit = await runner.run({exerciseId:'p01',code:"print('x'*40000)"});
                const version = await runner.run({exerciseId:'p01',code:bank[0].solution+'\\nimport sys\\nprint(sys.version)'});
                runner.stop();
                return {runs,syntax,wrong,timeout,afterTimeout,stopped,afterStop,outputLimit,pythonVersion:version.stdout};
            }''')
            injected = {'hook':'fatal'}
            def fatal_runtime(route):
                hook = 'settings.API.on_fatal' if injected['hook'] == 'fatal' else 'settings.onAbort'
                body = 'self._createPyodideModule = settings => { setTimeout(() => '+hook+'(new Error(\"INJECTED_BOOT_FAILURE\")), 0); return new Promise(() => {}); };'
                route.fulfill(content_type='text/javascript', body=body)
            context.route('**/vendor/pyodide/pyodide.asm.js', fatal_runtime)
            fatal_results = []
            for hook in ['fatal','abort']:
                injected['hook'] = hook
                checked = page.evaluate('''async () => {
                    const {PythonRunner} = await import('/js/python-runner.js');
                    const runner = new PythonRunner();
                    const result = await Promise.race([
                        runner.run({exerciseId:'p01',code:'pass'}),
                        new Promise(resolve=>setTimeout(()=>resolve({status:'test-hang'}),5000))
                    ]);
                    runner.stop();
                    return result;
                }''')
                fatal_results.append(checked)
            context.unroute('**/vendor/pyodide/pyodide.asm.js', fatal_runtime)
            after_fatal = page.evaluate('''async () => {
                const {PythonRunner} = await import('/js/python-runner.js');
                const runner = new PythonRunner();
                const bank = (await (await fetch('/python/exercises.json')).json()).exercises;
                const result = await runner.run({exerciseId:'p01',code:bank[0].solution});
                runner.stop();
                return result;
            }''')
            browser.close()
        for failure in fatal_results:
            assert failure['status'] == 'error', failure
            assert failure['phase'] == 'initialization', failure
            assert 'INJECTED_BOOT_FAILURE' in failure['feedback'], failure
            assert 'INJECTED_BOOT_FAILURE' in failure['stderr'], failure
        assert after_fatal['status'] == 'passed'
        assert len(result['runs']) == 80
        failures = [r for r in result['runs'] if r['status'] != 'passed' or not r['artifact']]
        assert not failures, failures
        assert result['syntax']['status'] == 'error' and 'SyntaxError' in result['syntax']['feedback']
        assert result['wrong']['status'] == 'failed' and result['wrong']['stdout'] == 'REAL STDOUT\n'
        assert result['wrong']['artifact']['output'] == "'candidate-value'"
        assert result['timeout']['status'] == 'timeout'
        assert result['stopped']['status'] == 'cancelled'
        assert result['afterTimeout']['status'] == result['afterStop']['status'] == 'passed'
        assert result['outputLimit']['status'] == 'error'
        assert len(result['outputLimit']['stdout']) == 32768
        assert not external, external
        assert not errors, errors
        report = {'referenceRuns':80,'referencePassed':80,'syntaxErrors':True,'stdout':True,'candidateArtifact':True,
                  'timeoutAndRecovery':True,'stopAndRecovery':True,'boundedOutput':True,
                  'fatalBootstrapPropagation':True,'abortBootstrapPropagation':True,'recoveryAfterBootstrapFailure':True,'externalRequests':external,
                  'pythonVersion':result['pythonVersion'].strip(),'runtimeAssets':sorted(set(url.split(origin)[-1] for url in requested if '/vendor/' in url))}
        artifacts = ROOT / 'artifacts'
        artifacts.mkdir(exist_ok=True)
        (artifacts/'python-browser-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False,indent=2))
    finally:
        server.shutdown()


if __name__ == '__main__':
    browser = '--browser' in sys.argv
    if browser:
        sys.argv.remove('--browser')
    outcome = unittest.main(exit=False)
    if not outcome.result.wasSuccessful():
        raise SystemExit(1)
    if browser:
        browser_tests()
