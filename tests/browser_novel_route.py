"""Known-answer QA through all 100 VN lessons. Runs real Python twice per exercise.
No completion, mastery, relationships or reward flags are injected. This verifies
software reachability, not human learning outcomes or task difficulty.
"""
import hashlib
import functools, json, threading, time, os
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from browser_runtime import ROOT, QuietHandler


def run():
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT/'web')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    draft=os.environ.get('ALLOW_DRAFT_CURRICULUM')=='1'
    result={'curriculumFinal':not draft,'errors':[],'externalRequests':[],'levels':[],'checks':{},'pythonRuns':0}
    result.update(campaignSha256=hashlib.sha256((ROOT/'web/data/campaign.json').read_bytes()).hexdigest(),appJsSha256=hashlib.sha256((ROOT/'web/js/app.js').read_bytes()).hexdigest())
    started=time.monotonic()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
            ctx=browser.new_context(viewport={'width':1280,'height':800},has_touch=True)
            def gate(route):
                if urlparse(route.request.url).hostname not in {'127.0.0.1','localhost'}:
                    result['externalRequests'].append(route.request.url);route.abort()
                else:route.continue_()
            ctx.route('**/*',gate)
            page=ctx.new_page();page.set_default_timeout(30000)
            page.on('pageerror',lambda error:result['errors'].append(str(error)))
            page.goto(origin+'/?qa=1');page.wait_for_function('window.__ASTERION_TEST__?.campaign.levels.length===100')
            page.wait_for_function('document.querySelector(".welcome-art")?.dataset.artLoaded==="true"')
            page.screenshot(path=str(ROOT/'artifacts/v2-route-welcome.png'))
            for number in range(1,101):
                ident=f'l{number:03}'
                info=page.evaluate('''id=>{const q=window.__ASTERION_TEST__,l=q.campaign.levels.find(x=>x.id===id);q.openLevel(l,'story');return {title:l.title,pythonId:l.pythonId,answer:l.check.answer,transfer:l.transfer.answer,hasTeaching:!!l.teaching,mandatoryCombat:l.mandatoryCombat};}''',ident)
                if not draft:
                    assert info['hasTeaching'],ident
                    assert info['mandatoryCombat'] is False,ident
                assert page.locator('#nextStory').count(),ident
                if number in {37,79}:page.screenshot(path=str(ROOT/f'artifacts/v2-route-story-{number:03}.png'))
                while page.locator('#nextStory').count():page.locator('#nextStory').click()
                visited=0
                while page.locator('#nextLesson').count():
                    page.locator('#nextLesson').click();visited+=1
                    assert visited<40,(ident,visited)
                if info['pythonId']:
                    solution=page.evaluate('id=>window.__ASTERION_TEST__.exercises[id].solution',info['pythonId'])
                    page.locator('#codeEditor').fill(solution);page.locator('#runPython').click()
                    page.wait_for_function('id=>window.__ASTERION_TEST__.state.levels[id].pythonPassed',arg=ident,timeout=120000)
                    result['pythonRuns']+=1
                    page.locator('#codeContinue').click()
                page.locator(f'[data-answer="{info["answer"]}"]').click();page.locator('#checkNext').click()
                if info['pythonId']:
                    assert page.locator('#checkNext').is_disabled()
                    page.locator('#checkCode').click();page.locator('#runPython').click()
                    page.wait_for_function('id=>window.__ASTERION_TEST__.state.levels[id].codeTransferPassed',arg=ident,timeout=120000)
                    result['pythonRuns']+=1;page.locator('#codeContinue').click()
                page.locator(f'[data-answer="{info["transfer"]}"]').click();page.locator('#checkNext').click()
                page.locator('#completeLevel').click()
                if number%5==0:
                    page.locator(f'[data-story-choice="{(number//5)%3}"]').click()
                    if number in {10,40}:page.screenshot(path=str(ROOT/f'artifacts/v2-route-choice-{number:03}.png'))
                    page.locator('#afterStory').click()
                page.wait_for_function('id=>window.__ASTERION_TEST__.state.completed.includes(id)',arg=ident)
                result['levels'].append({'id':ident,'title':info['title'],'python':info['pythonId'],'teachingPagesVisited':visited})
                if number==10:
                    page.evaluate('async()=>await window.__ASTERION_TEST__.save()');page.reload();page.wait_for_function('window.__ASTERION_TEST__?.state.completed.length===10')
                    assert page.evaluate('window.__ASTERION_TEST__.state.chapter')==2
                    result['checks']['chapterReload']=True
                if number%10==0:print('VN route',number,flush=True)
            page.wait_for_selector('#endingGallery');page.screenshot(path=str(ROOT/'artifacts/v2-route-ending.png'))
            summary=page.evaluate('''()=>{const s=window.__ASTERION_TEST__.state;return {completed:s.completed.length,rewards:s.rewards.length,memories:s.memories.length,meetings:Object.values(s.bonds).reduce((v,b)=>v+b.meetings,0),battles:Object.values(s.levels).filter(x=>x.battleResult).length};}''')
            assert summary=={'completed':100,'rewards':100,'memories':20,'meetings':20,'battles':0},summary
            assert result['pythonRuns']==80
            result['summary']=summary
            page.locator('#endingGallery').click()
            for char,choice in [('iris','curiosity'),('eila','care'),('mira','candor'),('selena','care')]:
                page.locator('#route_'+char).click();page.locator(f'[data-route-choice="{choice}"]').click();page.locator('#routeBack').click()
                assert page.evaluate('id=>window.__ASTERION_TEST__.state.routes[id].preference',char)==choice
            assert page.evaluate('Object.keys(window.__ASTERION_TEST__.state.routes).length')==4
            before=page.evaluate('JSON.stringify(window.__ASTERION_TEST__.state.bonds)')
            page.locator('#memory_l005').click();page.locator('#memoryBack').click()
            assert page.evaluate('JSON.stringify(window.__ASTERION_TEST__.state.bonds)')==before
            page.evaluate("(()=>{const q=window.__ASTERION_TEST__;q.openLevel(q.campaign.levels[4],'check');})()")
            wrong=page.evaluate('(window.__ASTERION_TEST__.campaign.levels[4].check.answer+1)%3')
            page.locator(f'[data-answer="{wrong}"]').click()
            assert page.evaluate('JSON.stringify(window.__ASTERION_TEST__.state.bonds)')==before
            page.evaluate('window.__ASTERION_TEST__.gallery()')
            result['checks']['learningMistakesDoNotReduceAffection']=True
            result['checks']['fourOptionalRomanticRoutes']=True;result['checks']['replayNoAffectionFarm']=True
            page.screenshot(path=str(ROOT/'artifacts/v2-route-gallery.png'))
            page.evaluate('async()=>await window.__ASTERION_TEST__.save()');page.reload();page.wait_for_function('window.__ASTERION_TEST__?.state.completed.length===100')
            assert page.evaluate('Object.keys(window.__ASTERION_TEST__.state.routes).length')==4
            result['checks']['finalReload']=True
            assert not result['errors'],result['errors'];assert not result['externalRequests'],result['externalRequests']
            result['passed']=True;browser.close()
    finally:
        result['seconds']=round(time.monotonic()-started,1);server.shutdown()
        (ROOT/'artifacts/v2-browser-route.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    data=run();print(json.dumps({k:v for k,v in data.items() if k!='levels'},ensure_ascii=False,indent=2))
