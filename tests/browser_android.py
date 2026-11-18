"""Actual installed Android WebView smoke via ADB taps and CDP inspection.

Requires installed release APK and booted emulator. No QA mode is required.
Code text is entered through CDP; button presses use Android input tap.
Run: python tests/browser_android.py
"""
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ADB='/workspace/android-sdk/platform-tools/adb'
SERIAL='emulator-5554'
PACKAGE='org.asterion.livingprotocol'
ACTIVITY=PACKAGE+'/.MainActivity'


def adb(*args):
    completed=subprocess.run([ADB,'-s',SERIAL,*args],capture_output=True,text=True,timeout=90)
    if completed.returncode:raise RuntimeError(completed.stderr or completed.stdout)
    return completed.stdout.strip()


def start():
    adb('shell','am','force-stop',PACKAGE)
    # A document picker belongs to the app task even after an interrupted
    # fixture stops the app. Clear that test task, never the app's saved data.
    adb('shell','am','start','-W','-f','0x10008000','-n',ACTIVITY,'--ez','diagnostics','true')
    pid=''
    for _ in range(30):
        try:pid=adb('shell','pidof',PACKAGE)
        except RuntimeError:pid=''
        if pid:break
        time.sleep(1)
    assert pid,'App process absent'
    adb('forward','tcp:9222','localabstract:webview_devtools_remote_'+pid.split()[0])
    return pid


def connect(playwright):
    # Direct page CDP avoids WebView's unsupported Browser.setDownloadBehavior.
    from browser_android_cdp import RawPage
    last=None
    for _ in range(60):
        try:
            page=RawPage('http://127.0.0.1:9222')
            page.set_default_timeout(120000)
            return None,page
        except Exception as error:last=error
        time.sleep(1)
    raise RuntimeError('WebView CDP unavailable: '+str(last))


def tap(page,selector):
    element=page.locator(selector);element.wait_for(state='visible');element.scroll_into_view_if_needed()
    box=element.bounding_box();viewport=page.evaluate('({width:innerWidth,height:innerHeight,scale:devicePixelRatio})')
    size=adb('shell','wm','size')
    width,height=map(int,re.findall(r'(\d+)x(\d+)',size)[-1])
    if viewport['width']>viewport['height'] and width<height:width,height=height,width
    scale=width/viewport['width']  # Stable physical/CSS scale also while Android IME resizes the WebView.
    adb('shell','input','tap',str(round((box['x']+box['width']/2)*scale)),str(round((box['y']+box['height']/2)*scale)))
    # Input injection may return before a software-emulated WebView consumes
    # the click. Wait for the resulting frame before inspecting its next step.
    page.wait_for_timeout(300)
    if selector not in ('#exportSave','#importSave','#importRecovery'):
        page.evaluate('async()=>{if(document.hidden)return;await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);}')


def save_state(page):
    envelope=page.evaluate('JSON.parse(Android.loadSave())')
    assert 'payload' in envelope,envelope
    return json.loads(envelope['payload'])


def run():
    # Compatibility entry point now runs the illustrated V2 flow.
    from android_v2_qa import run as verify_v2
    verify_v2()


if __name__=='__main__':run()
