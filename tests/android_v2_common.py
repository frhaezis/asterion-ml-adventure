"""Shared installed-APK checks. ADB taps exercise the actual Android surface."""
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from browser_android import ROOT, ADB, SERIAL, PACKAGE, ACTIVITY, adb, start, connect, tap, save_state

APK=ROOT/'release/asterion. elf beauties teach me all about Machine Learning. V2.apk'
ART=ROOT/'artifacts'
PRIVATE='/data/user/0/'+PACKAGE+'/files'
PROFILE=PRIVATE+'/novel-v2'

def apk_hash():
    expected=hashlib.sha256(APK.read_bytes()).hexdigest()
    installed=adb('shell','pm','path',PACKAGE).splitlines()[0].removeprefix('package:')
    assert adb('shell','sha256sum',installed).split()[0]==expected
    return expected

def screenshot(name):
    adb('shell','screencap','-p','/sdcard/'+name)
    adb('pull','/sdcard/'+name,str(ART/name))
    return str(ART/name)

def open_app():
    start();_,page=connect(None)
    page.wait_for_selector('#begin')
    return page

def begin(page):
    tap(page,'#begin')
    if page.locator('#resumeGame').is_visible():tap(page,'#resumeGame')

def open_code(page,level='l001'):
    if page.locator('#codeEditor').is_visible():return
    if page.locator('#closePanel').is_visible():tap(page,'#closePanel')
    tap(page,'#mapButton');tap(page,'[data-level="'+level+'"]');tap(page,'#selectLevel')
    tap(page,'[data-tab="python"]')
    page.wait_for_selector('#codeEditor')

def wait_saved(page):
    page.wait_for_function("document.querySelector('#saveStatus')?.textContent.includes('Сохранено')",timeout=30000)

def wait_python(page,marker=None):
    page.wait_for_function("document.querySelector('#pythonOutput')?.textContent.includes('✓ Проверка пройдена') && !document.querySelector('#codeContinue').disabled",timeout=120000)
    result=page.locator('#pythonOutput').inner_text()
    if marker:assert marker in result,result
    return result

def wait_art(page):
    page.wait_for_function("[...document.querySelectorAll('.art-image')].filter(e=>e.getClientRects().length).every(e=>e.dataset.artLoaded==='true')",timeout=60000)
    page.evaluate('async()=>{await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);}')
    page.wait_for_timeout(1500)

def ui_dump():
    # uiautomator can exit zero after an idle-state failure. Never reuse an old
    # tree (its screen coordinates may belong to the preceding native dialog).
    for attempt in range(3):
        adb('shell','rm','-f','/sdcard/asterion-v2-ui.xml')
        output=adb('shell','uiautomator','dump','/sdcard/asterion-v2-ui.xml')
        if 'dumped to:' in output:
            return ET.fromstring(adb('shell','cat','/sdcard/asterion-v2-ui.xml'))
        time.sleep(1)
    raise RuntimeError('No fresh Android UI hierarchy: '+output)

def ui_nodes():
    return [n.attrib for n in ui_dump().iter('node')]

def ui_tap(text=None,res=None,description=None,timeout=60):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        for node in ui_nodes():
            if text is not None and node.get('text')!=text:continue
            if res is not None and node.get('resource-id')!=res:continue
            if description is not None and node.get('content-desc')!=description:continue
            bounds=list(map(int,re.findall(r'\d+',node['bounds'])))
            adb('shell','input','tap',str((bounds[0]+bounds[2])//2),str((bounds[1]+bounds[3])//2))
            return node
        time.sleep(.5)
    raise TimeoutError({'text':text,'res':res,'description':description,'visible':ui_nodes()})

def dismiss_message():
    return ui_tap(res='android:id/button1')

def write_report(name,result):
    (ART/name).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
