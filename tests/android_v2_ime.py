"""Two real Android keyboard show/hide cycles; no simulated viewport resize."""
from android_v2_common import *


def run():
    report={'passed':False,'apkSha256':apk_hash(),'cycles':[]}
    old=adb('shell','settings','get','secure','show_ime_with_hard_keyboard')
    try:
        p=open_app();begin(p);open_code(p)
        adb('shell','settings','put','secure','show_ime_with_hard_keyboard','1')
        def measure():return p.evaluate('({width:innerWidth,inner:innerHeight,visual:visualViewport.height,focused:document.activeElement?.id,editor:document.querySelector("#codeEditor")?.getBoundingClientRect().toJSON()})')
        baseline=measure();report['baseline']=baseline
        assert baseline['inner']>=400,baseline
        for cycle in range(2):
            tap(p,'#codeEditor')
            p.wait_for_function('innerHeight<'+str(baseline['inner']-100),timeout=60000)
            p.locator('#codeEditor').evaluate('(e)=>{e.scrollIntoView({block:"start"});e.scrollTop=0;e.setSelectionRange(0,0);}')
            shown=measure()
            assert shown['focused']=='codeEditor'
            visible=max(0,min(shown['inner'],shown['editor']['bottom'])-max(0,shown['editor']['top']))
            assert visible>80,(visible,shown)
            screenshot('android-v2-keyboard.png')
            controls={}
            for selector in ['#runPython','#stopPython','#closePanel']:
                if selector!='#closePanel':p.locator(selector).scroll_into_view_if_needed()
                bounds=p.locator(selector).bounding_box()
                hit=p.locator(selector).evaluate('(e)=>{const r=e.getBoundingClientRect();const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return !!hit&&(hit===e||e.contains(hit));}')
                assert bounds['y']>=0 and bounds['y']+bounds['height']<=shown['inner']+1 and hit,(selector,bounds,shown)
                controls[selector]={'bounds':bounds,'unobscured':hit}
            screenshot('android-v2-keyboard-controls.png')
            adb('shell','input','keyevent','KEYCODE_BACK')
            p.wait_for_function('innerHeight==='+str(baseline['inner']),timeout=60000)
            report['cycles'].append({'shown':shown,'editorVisibleCssPixels':visible,'controls':controls,'hidden':measure()})
        report['passed']=True
        report['scope']='Actual ADB taps focus textarea; actual Android Back hides keyboard. CDP inspects bounds and scrolls controls. No source was entered by this test.'
    except Exception as e:
        report['failure']=str(e);raise
    finally:
        if old=='null':adb('shell','settings','delete','secure','show_ime_with_hard_keyboard')
        else:adb('shell','settings','put','secure','show_ime_with_hard_keyboard',old)
        report['keyboardSettingRestored']=old
        write_report('android-v2-keyboard.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':run()
