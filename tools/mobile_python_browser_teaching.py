"""Execute the 40 lesson demos and all syntax primers in vendored Pyodide.

This supplements, rather than repeats, the UI owner's 80 reference-task runs.
All non-local network requests are blocked. Requires installed Chromium and
Playwright; does not download dependencies or modify runtime code.
"""
from pathlib import Path
import functools
import http.server
import json
import runpy
import shutil
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def main():
    authoring = runpy.run_path(str(ROOT / "tools/mobile_python_teaching_content.py"))
    bank = json.loads((ROOT / "web/python/exercises.json").read_text())["exercises"]
    snippets = [dict(id=e["id"], code=e["teaching"]["workedExample"]["code"],
                     expected=e["teaching"]["workedExample"]["expectedStdout"]) for e in bank]
    snippets += [dict(id="primer-" + key, code=value["example"], expected="")
                 for key, value in authoring["PRIMERS"].items()]

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
        functools.partial(QuietHandler, directory=str(ROOT / "web")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    external = []
    errors = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=shutil.which("chromium"),
                                                 headless=True, args=["--no-sandbox"])
            context = browser.new_context()

            def route_request(route):
                if not route.request.url.startswith(origin + "/"):
                    external.append(route.request.url)
                    route.abort()
                elif route.request.url.endswith("/qa-teaching.html"):
                    route.fulfill(content_type="text/html", body="<html><body>Teaching checks</body></html>")
                else:
                    route.continue_()

            context.route("**/*", route_request)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(origin + "/qa-teaching.html")
            result = page.evaluate("""async ({snippets, reference}) => {
                const {PythonRunner} = await import('/js/python-runner.js');
                const runner = new PythonRunner();
                await runner.init();
                const runs = [];
                for (const snippet of snippets) {
                    // JSON string literals are valid Python string literals here;
                    // Unicode is preserved by JSON.stringify, no interpolation.
                    const code = reference + '\\nexec(' + JSON.stringify(snippet.code) + ', {})';
                    const value = await runner.run({exerciseId:'p01', code});
                    runs.push({id:snippet.id, status:value.status, stdout:value.stdout,
                        expected:snippet.expected, stderr:value.stderr});
                }
                const version = await runner.run({exerciseId:'p01', code:reference+'\\nimport sys\\nprint(sys.version)'});
                runner.stop();
                return {runs, pythonVersion:version.stdout.trim()};
            }""", dict(snippets=snippets, reference=bank[0]["solution"]))
            browser.close()
        failed = [r for r in result["runs"] if r["status"] != "passed" or r["stdout"] != r["expected"] or r["stderr"]]
        assert not failed, failed
        assert not external, external
        assert not errors, errors
        report = dict(demonstrations=40, syntaxPrimers=len(authoring["PRIMERS"]),
                      passed=len(result["runs"]), pythonVersion=result["pythonVersion"],
                      externalRequests=external, browserErrors=errors)
        destination = ROOT / "artifacts/mobile-python-teaching-browser.json"
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
