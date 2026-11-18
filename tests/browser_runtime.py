"""Real offline CPython worker integration with system Chromium.
Run from project root: python tests/browser_runtime.py
Uses only loopback HTTP; all external browser requests are rejected and reported.
"""
import functools
import json
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run():
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT / 'web')))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f'http://127.0.0.1:{server.server_port}'
    results = {'runtime': 'Chromium / real bundled Pyodide', 'origin': origin,
               'externalRequests': [], 'errors': [], 'solutions': [], 'checks': {}}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                                args=['--no-sandbox', '--disable-dev-shm-usage'])
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            def route(request):
                if urlparse(request.request.url).hostname not in {'127.0.0.1', 'localhost'}:
                    results['externalRequests'].append(request.request.url)
                    request.abort()
                else:
                    request.continue_()
            context.route('**/*', route)
            page = context.new_page()
            page.on('pageerror', lambda error: results['errors'].append(str(error)))
            # Directory document intentionally avoids booting the app's second runner.
            page.goto(origin + '/python/')
            page.set_default_timeout(120000)
            started = time.monotonic()
            init = page.evaluate('''async () => {
                const {PythonRunner} = await import('/js/python-runner.js');
                window.runner = new PythonRunner();
                await window.runner.init();
                window.exercises = (await (await fetch('/python/exercises.json')).json()).exercises;
                return {count:window.exercises.length};
            }''')
            results['initSeconds'] = round(time.monotonic() - started, 2)
            assert init['count'] == 40, init
            for index in range(40):
                outcome = page.evaluate('''async index => {
                    const e = window.exercises[index];
                    const practice = await window.runner.run({exerciseId:e.id, code:e.solution, variant:'practice', timeoutMs:20000});
                    const transfer = await window.runner.run({exerciseId:e.id, code:e.solution, variant:'transfer', timeoutMs:20000});
                    return {id:e.id, practice:practice.status, transfer:transfer.status,
                        checks:practice.checks?.length, feedback:practice.feedback};
                }''', index)
                results['solutions'].append(outcome)
                assert outcome['practice'] == 'passed' and outcome['transfer'] == 'passed', outcome
            wrong = page.evaluate('''async () => {
                const e = window.exercises[0];
                return await window.runner.run({exerciseId:e.id,code:e.starter,timeoutMs:10000});
            }''')
            assert wrong['status'] in {'failed', 'error'}, wrong
            results['checks']['unimplementedRejected'] = wrong['status']
            syntax = page.evaluate("async () => await window.runner.run({exerciseId:'p01',code:'def broken(:',timeoutMs:10000})")
            assert syntax['status'] == 'error', syntax
            results['checks']['syntaxError'] = syntax['status']
            timed = page.evaluate("""async () => {
                let ticks=0; const timer=setInterval(()=>ticks++,20);
                const result=await window.runner.run({exerciseId:'p01',code:'while True:\\n    pass',timeoutMs:700});
                clearInterval(timer);return {...result,uiTicks:ticks};
            }""")
            assert timed['status'] == 'timeout', timed
            results['checks']['infiniteLoopTerminated'] = timed['status']
            assert timed['uiTicks'] >= 5, timed
            results['checks']['uiHeartbeatDuringPythonLoop'] = timed['uiTicks']
            restarted = page.evaluate('''async () => {
                const e = window.exercises[0];
                return await window.runner.run({exerciseId:e.id, code:e.solution, timeoutMs:30000});
            }''')
            assert restarted['status'] == 'passed', restarted
            results['checks']['restartAfterTimeout'] = restarted['status']
            cancelled = page.evaluate('''async () => {
                const pending = window.runner.run({exerciseId:'p01',code:'while True:\\n    pass',timeoutMs:10000});
                setTimeout(() => window.runner.stop(), 200);
                return await pending;
            }''')
            assert cancelled['status'] == 'cancelled', cancelled
            results['checks']['stop'] = cancelled['status']
            assert not results['externalRequests'], results['externalRequests']
            assert not results['errors'], results['errors']
            results['elapsedSeconds'] = round(time.monotonic() - started, 2)
            results['passed'] = True
            browser.close()
    finally:
        server.shutdown()
        (ROOT / 'artifacts').mkdir(exist_ok=True)
        (ROOT / 'artifacts/browser_runtime_results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    run()
