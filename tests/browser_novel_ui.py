"""VN regressions: draft/help, actual Python errors, cancellation, edition isolation,
mastery gates, mobile layouts and atlas portraits. Browser viewport != Android IME.
"""
import hashlib
import functools,json,threading,time
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from browser_runtime import ROOT,QuietHandler

def run():
 server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT/'web')))
 threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
 out={'errors':[],'externalRequests':[],'checks':{}};started=time.monotonic()
 out.update(campaignSha256=hashlib.sha256((ROOT/'web/data/campaign.json').read_bytes()).hexdigest(),appJsSha256=hashlib.sha256((ROOT/'web/js/app.js').read_bytes()).hexdigest())
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
   ctx=browser.new_context(viewport={'width':854,'height':480},has_touch=True)
   def gate(route):
    if urlparse(route.request.url).hostname not in {'127.0.0.1','localhost'}:out['externalRequests'].append(route.request.url);route.abort()
    else:route.continue_()
   ctx.route('**/*',gate);page=ctx.new_page();page.set_default_timeout(30000)
   page.on('pageerror',lambda e:out['errors'].append(str(e)))
   page.goto(origin+'/?qa=1');page.wait_for_function('!!window.__ASTERION_TEST__')
   page.evaluate("localStorage.setItem('asterion.save.v2','old-edition-untouched')")
   page.wait_for_function('document.querySelector(".welcome-art")?.dataset.artLoaded==="true"')
   page.screenshot(path=str(ROOT/'artifacts/v2-ui-welcome-mobile.png'))
   page.locator('#begin').click();page.wait_for_timeout(100)
   page.screenshot(path=str(ROOT/'artifacts/v2-ui-story-mobile.png'))
   assert page.evaluate("getComputedStyle(document.querySelector('.novel-portrait')).backgroundColor==='rgba(0, 0, 0, 0)'")
   page.locator('[data-tab=python]').click()
   draft='def decode_packets(records):\n    # Мой сохранённый черновик\n    return "пока разбираюсь"\n'
   page.locator('#codeEditor').fill(draft);page.locator('#toggleCodeHelp').click()
   assert page.locator('#codeHelp').is_visible()
   page.locator('#codeHelp details').evaluate_all("els=>els.forEach(e=>e.open=true)")
   assert 'split' in page.locator('#codeHelp').inner_text()
   page.locator('#closeCodeHelp').click();assert page.locator('#codeEditor').input_value()==draft
   page.locator('[data-tab=prep]').click();page.locator('#nextLesson').click();page.locator('[data-tab=python]').click()
   assert page.locator('#codeEditor').input_value()==draft
   page.evaluate('async()=>await window.__ASTERION_TEST__.save()');page.reload();page.wait_for_selector('#begin');page.locator('#begin').click()
   assert page.locator('#codeEditor').input_value()==draft
   out['checks']['draftSurvivesTheoryHelpAndReload']=True
   page.locator('#runPython').click();page.wait_for_function("window.__ASTERION_TEST__.state.levels.l001.lastResult?.status==='failed'",timeout=120000)
   assert page.locator('#codeContinue').is_disabled();out['checks']['wrongCodeRejected']=True
   page.locator('#codeEditor').fill('def broken(:');page.locator('#runPython').click()
   page.wait_for_function("window.__ASTERION_TEST__.state.levels.l001.lastResult?.status==='error'",timeout=120000)
   assert 'SyntaxError' in page.locator('#pythonOutput').inner_text();out['checks']['syntaxErrorVisible']=True
   solution=page.evaluate('window.__ASTERION_TEST__.exercises.p01.solution')
   page.locator('#codeEditor').fill(solution);page.locator('#runPython').click()
   page.wait_for_function('window.__ASTERION_TEST__.state.levels.l001.pythonPassed',timeout=120000)
   assert '✓ Проверка пройдена' in page.locator('#pythonOutput').inner_text()
   page.locator('#codeEditor').fill(solution+'\n# changed\n')
   assert not page.evaluate('window.__ASTERION_TEST__.state.levels.l001.pythonPassed')
   assert page.locator('#codeContinue').is_disabled();out['checks']['editInvalidatesVerification']=True
   page.locator('#runPython').click();page.wait_for_function('window.__ASTERION_TEST__.state.levels.l001.pythonPassed',timeout=120000)
   page.locator('#codeContinue').click();answer=page.evaluate('window.__ASTERION_TEST__.campaign.levels[0].check.answer')
   page.locator(f'[data-answer="{answer}"]').click();page.locator('#checkNext').click()
   assert page.locator('#checkNext').is_disabled();out['checks']['additionalInputsRequired']=True
   page.locator('#checkCode').click();page.locator('#runPython').click()
   page.wait_for_function('window.__ASTERION_TEST__.state.levels.l001.codeTransferPassed',timeout=120000)
   page.locator('#codeContinue').click();answer=page.evaluate('window.__ASTERION_TEST__.campaign.levels[0].transfer.answer')
   page.locator(f'[data-answer="{answer}"]').click();page.locator('#checkNext').click();page.locator('#completeLevel').click()
   page.wait_for_function('window.__ASTERION_TEST__.state.completed.length===1')
   assert page.evaluate('window.__ASTERION_TEST__.state.levels.l001.status')=='assisted'
   out['checks']['honestAssistedStatus']=True
   # New level is unlocked normally. Keep first completion untouched during cancel/pause.
   page.evaluate("(()=>{const q=window.__ASTERION_TEST__;q.openLevel(q.campaign.levels[1],'python');})()")
   page.locator('#codeEditor').fill('while True:\n    pass')
   page.locator('#runPython').click();page.wait_for_timeout(150);page.locator('#stopPython').click()
   page.wait_for_function("window.__ASTERION_TEST__.state.levels.l002.lastResult?.status==='cancelled'")
   assert page.evaluate('window.__ASTERION_TEST__.state.levels.l001.pythonPassed')
   out['checks']['stopPreservesCompletedLevel']=True
   page.locator('#runPython').click();page.wait_for_timeout(150)
   page.evaluate('window.onAppPause();window.onAppResume()');page.locator('#resumeGame').click()
   assert page.locator('#codeEditor').input_value()=='while True:\n    pass'
   assert page.evaluate("window.__ASTERION_TEST__.state.levels.l002.lastResult.status==='cancelled'")
   assert page.evaluate('window.__ASTERION_TEST__.state.levels.l001.pythonPassed')
   out['checks']['pauseCancelsOnlyCurrentRun']=True
   solution2=page.evaluate('window.__ASTERION_TEST__.exercises.p02.solution')
   page.locator('#codeEditor').fill(solution2);page.locator('#runPython').click()
   page.wait_for_function('window.__ASTERION_TEST__.state.levels.l002.pythonPassed',timeout=120000)
   out['checks']['runtimeRestartsAfterCancellation']=True
   # Import another valid checksum but wrong edition; existing state and old namespace survive.
   await_save='async()=>await window.__ASTERION_TEST__.save()';page.evaluate(await_save)
   before=page.evaluate('JSON.stringify(window.__ASTERION_TEST__.state)')
   page.evaluate("""async()=>{const {envelope}=await import('/js/storage.js');const old=structuredClone(window.__ASTERION_TEST__.state);delete old.campaignEdition;old.completed=[];await window.__ASTERION_TEST__.importEnvelope(await envelope(old));}""")
   assert page.evaluate('JSON.stringify(window.__ASTERION_TEST__.state)')==before
   assert page.evaluate("localStorage.getItem('asterion.save.v2')")=='old-edition-untouched'
   assert 'другой редакции' in page.locator('#notification').inner_text()
   out['checks']['editionImportBlockedAndLegacyPreserved']=True
   # Screens at landscape, portrait, and simulated keyboard-height viewport.
   for width,height in [(1280,720),(854,480),(390,844),(854,180)]:
    page.set_viewport_size({'width':width,'height':height})
    page.evaluate("(()=>{const q=window.__ASTERION_TEST__;q.openLevel(q.campaign.levels[1],'python');})()")
    page.locator('#codeEditor').scroll_into_view_if_needed();page.wait_for_timeout(80)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,height)
    assert page.locator('#codeEditor').input_value()==solution2
    page.locator('#toggleCodeHelp').click();assert page.locator('#codeHelp').is_visible()
    page.locator('#closeCodeHelp').click();page.locator('#runPython').scroll_into_view_if_needed()
    assert page.locator('#runPython').is_visible()
    page.screenshot(path=str(ROOT/f'artifacts/v2-ui-code-{width}x{height}.png'))
   out['checks']['fourResponsiveViewports']=True
   page.set_viewport_size({'width':854,'height':480});page.keyboard.press('Escape');page.locator('#saveExit').click()
   page.wait_for_selector('#stay');assert 'Прогресс записан' in page.locator('#panelBody').inner_text()
   page.reload();page.wait_for_selector('#begin');page.locator('#begin').click()
   assert page.locator('#codeEditor').input_value()==solution2
   out['checks']['saveExitReload']=True
   page.evaluate('async()=>await window.__ASTERION_TEST__.save()')
   page.evaluate("localStorage.setItem('asterion.novel.v2','broken-save');location.reload()")
   page.wait_for_selector('#recoverSave');page.evaluate('window.onAppPause()')
   assert page.evaluate("localStorage.getItem('asterion.novel.v2')")=='broken-save'
   page.locator('#recoverSave').click();page.wait_for_selector('#begin');page.locator('#begin').click()
   assert page.locator('#codeEditor').input_value()==solution2
   assert page.evaluate('window.__ASTERION_TEST__.state.completed.length')==1
   out['checks']['corruptSaveBlockedAndBackupRecovered']=True
   assert not out['errors'],out['errors'];assert not out['externalRequests'],out['externalRequests']
   out['passed']=True;browser.close()
 finally:
  out['seconds']=round(time.monotonic()-started,1);server.shutdown()
  (ROOT/'artifacts/v2-browser-ui.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 return out
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
