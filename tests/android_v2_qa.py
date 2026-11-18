"""Actual Android V2 offline native Python, novel flow and persistence.

Code strings are entered through CDP; visible controls are tapped through ADB.
No completion flags are assigned by the test.
"""
import json
import os
import time
from android_v2_common import *


def run():
    report={'passed':False,'device':SERIAL,'checks':{},'solutions':[],'errors':[],
            'inputMethod':'Code through CDP; controls through Android ADB taps',
            'limitations':['Actual x86_64 Android 15 software emulator; ARM64 phone not tested.',
                           'Reference solution checks establish functionality, not human learning.']}
    old_save_hash=adb('shell','sha256sum',PRIVATE+'/save.json').split()[0]
    try:
        if os.environ.get('ASTERION_QA_RESET_PROFILE')=='1':
            adb('shell','am','force-stop',PACKAGE)
            if 'novel-v2' in adb('shell','ls','-1',PRIVATE).splitlines():
                adb('shell','mv',PROFILE,PROFILE+'.qa-retained-'+str(time.time_ns()))
        report['apkSha256']=apk_hash()
        page=open_app();page.on('pageerror',lambda e:report['errors'].append(str(e)))
        report['diagnostics']=page.evaluate('JSON.parse(Android.getDiagnostics())')
        assert report['diagnostics']['appVersion']=='2.1.0'
        wait_art(page)
        screenshot('android-v2-welcome.png')
        begin(page)
        wait_art(page)
        screenshot('android-v2-dialogue.png')
        while page.locator('#nextStory').is_visible():tap(page,'#nextStory')
        if page.locator('#nextLesson').is_visible():screenshot('android-v2-teaching.png')
        lesson_pages=0
        # Full-page coverage is checked by the 100-episode browser route.
        # On Android inspect three pages, then use the visible Code tab.
        while lesson_pages<3 and page.locator('#nextLesson').is_visible():
            tap(page,'#nextLesson');lesson_pages+=1
        tap(page,'[data-tab="python"]');page.wait_for_selector('#codeEditor')
        report['checks']['dialogueAndTeachingBeforeCode']={'pages':lesson_pages}
        draft='def decode_packets(records):\n    # V2_NATIVE_DRAFT\n    return "unexecuted"\n'
        page.locator('#codeEditor').fill(draft);wait_saved(page)
        assert save_state(page)['campaignEdition']=='elf-beauties-v2'
        assert save_state(page)['levels']['l001']['draft']==draft
        page=open_app();begin(page);page.wait_for_selector('#codeEditor')
        assert page.locator('#codeEditor').input_value()==draft
        report['checks']['forceStopRestoresDraft']=True
        assert adb('shell','sha256sum',PRIVATE+'/save.json').split()[0]==old_save_hash
        report['checks']['previousEditionSaveUnchanged']=True
        adb('shell','cmd','connectivity','airplane-mode','enable')
        adb('shell','svc','wifi','disable');adb('shell','svc','data','disable')
        report['activeDefaultNetwork']=[x.strip() for x in adb('shell','dumpsys','connectivity').splitlines() if 'Active default network' in x]
        assert report['activeDefaultNetwork'] and all('none' in x.lower() for x in report['activeDefaultNetwork'])
        bank=json.loads((ROOT/'web/python/exercises.json').read_text())['exercises']
        campaign=json.loads((ROOT/'web/data/campaign.json').read_text())['levels']
        marker='NATIVE_V2_OFFLINE_'+str(time.time_ns())
        solution=bank[0]['solution']+'\nprint('+repr(marker)+')\n'
        page.locator('#codeEditor').fill(solution)
        page.locator('#codeEditor').evaluate('(e)=>e.blur()')
        tap(page,'#runPython');report['pythonOutput']=wait_python(page,marker)
        wait_saved(page)
        assert save_state(page)['levels']['l001']['pythonPassed']
        screenshot('android-v2-python.png')
        report['checks']['actualOfflinePythonThroughUI']=True
        page.evaluate('''async()=>{const {PythonRunner}=await import('/js/python-runner.js');window.qaRunner=new PythonRunner();await qaRunner.init();window.qaBank=(await(await fetch('/python/exercises.json')).json()).exercises;}''')
        for i in range(40):
            value=page.evaluate('''async i=>{const e=qaBank[i],a=await qaRunner.run({exerciseId:e.id,code:e.solution,variant:'practice',timeoutMs:30000}),b=await qaRunner.run({exerciseId:e.id,code:e.solution,variant:'transfer',timeoutMs:30000});return {id:e.id,practice:a.status,transfer:b.status,practiceChecks:a.checks?.length,transferChecks:b.checks?.length};}''',i)
            report['solutions'].append(value)
            print('Native V2',value,flush=True)
            assert value['practice']==value['transfer']=='passed',value
        report['checks']['all40PracticeAndTransferNative']=True
        faults=page.evaluate('''async()=>{const bad=await qaRunner.run({exerciseId:'p01',code:'def broken(',timeoutMs:10000});const wrong=await qaRunner.run({exerciseId:'p01',code:qaBank[0].starter,timeoutMs:10000});return {syntax:bad.status,syntaxFeedback:bad.feedback,wrong:wrong.status};}''')
        assert faults['syntax']=='error' and 'SyntaxError' in faults['syntaxFeedback'] and faults['wrong']!='passed',faults
        report['checks']['syntaxAndWrongProgramRejected']=faults
        recovery=page.evaluate('''async()=>{const pid=()=>JSON.parse(Android.getDiagnostics()).pythonProcessPid;const before=pid();let ticks=0;const timer=setInterval(()=>ticks++,100);const timed=await qaRunner.run({exerciseId:'p01',code:'while True:\\n    pass',timeoutMs:1500});clearInterval(timer);const a=await qaRunner.run({exerciseId:'p01',code:qaBank[0].solution,timeoutMs:30000});const timeoutPid=pid();const pending=qaRunner.run({exerciseId:'p01',code:'while True:\\n    pass',timeoutMs:30000});setTimeout(()=>qaRunner.stop(),1500);const cancelled=await pending;const b=await qaRunner.run({exerciseId:'p01',code:qaBank[0].solution,timeoutMs:30000});return {before,timeoutPid,stopPid:pid(),ticks,timed:timed.status,afterTimeout:a.status,cancelled:cancelled.status,afterStop:b.status};}''')
        assert recovery['timed']=='timeout' and recovery['cancelled']=='cancelled'
        assert recovery['afterTimeout']==recovery['afterStop']=='passed'
        assert recovery['ticks']>=2 and len({recovery['before'],recovery['timeoutPid'],recovery['stopPid']})==3
        report['checks']['timeoutStopImmediateRecovery']=recovery
        page.evaluate('qaRunner.stop()')
        page=open_app();begin(page);page.wait_for_selector('#codeEditor')
        assert marker in page.locator('#codeEditor').input_value()
        assert save_state(page)['levels']['l001']['pythonPassed']
        report['checks']['pythonResultSurvivesRestart']=True
        tap(page,'#codeContinue')
        tap(page,'[data-answer="'+str(campaign[0]['check']['answer'])+'"]');tap(page,'#checkNext')
        tap(page,'#checkCode');tap(page,'#runPython');wait_python(page,marker)
        tap(page,'#codeContinue');tap(page,'[data-answer="'+str(campaign[0]['transfer']['answer'])+'"]');tap(page,'#checkNext')
        tap(page,'#completeLevel');wait_saved(page)
        state=save_state(page)
        assert state['completed'].count('l001')==1 and len(state['rewards'])==1
        assert state['currentLevel']=='l002'
        assert not state['levels']['l001'].get('battleResult')
        report['checks']['novelLessonCodeAndTransferCompletionWithoutCombat']=True
        screenshot('android-v2-garden.png')
        page=open_app();begin(page)
        assert 'l001' in save_state(page)['completed'] and save_state(page)['currentLevel']=='l002'
        report['checks']['completionSurvivesForceStop']=True
        assert adb('shell','sha256sum',PRIVATE+'/save.json').split()[0]==old_save_hash
        assert not report['errors'],report['errors']
        report['passed']=True
    except Exception as e:
        report['failure']=str(e)
        raise
    finally:
        try:adb('shell','cmd','connectivity','airplane-mode','disable')
        except Exception:pass
        write_report('android-v2-qa.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':run()
